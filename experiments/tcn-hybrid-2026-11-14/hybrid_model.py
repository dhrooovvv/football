"""Two fixed correction models, preserving frozen parent probability inputs."""
from functools import lru_cache

import numpy as np
import torch
from torch import nn

SLOTS, CHANNELS, WIDTH = 64, 8, 521
CORE, GRAPH_RADIUS = 200, 7
TEMPORAL_DILATIONS = (1, 2, 4, 8, 16, 32)
TEMPORAL_RADIUS = sum(TEMPORAL_DILATIONS)
TEMPORAL_WINDOW = 169
PARAMETERS = {'temporal': 6483, 'graph': 9835}
ARCHITECTURES = {'temporal': 'coarse5_residual16_d1_2_4_8_16_32_v1',
                 'graph': 'visible_knn4_ball_all_message8_temporal32_v1'}


@lru_cache(maxsize=1)
def configure():
    torch.set_num_threads(1)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.mkldnn.enabled = False


class ResidualBlock(nn.Module):
    def __init__(self, dilation):
        super().__init__()
        self.dilated = nn.Conv1d(16, 16, 3, padding=dilation, dilation=dilation)
        self.project = nn.Conv1d(16, 16, 1)

    def forward(self, values):
        return values + self.project(torch.relu(self.dilated(values)))


class TemporalRefiner(nn.Module):
    stage = 'temporal'

    def __init__(self):
        super().__init__()
        self.input = nn.Conv1d(5, 16, 1)
        self.blocks = nn.Sequential(*(ResidualBlock(d) for d in TEMPORAL_DILATIONS))
        self.head = nn.Conv1d(16, 3, 1)
        nn.init.zeros_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def forward(self, values):
        if values.ndim != 3 or values.shape[-1] != 5:
            raise ValueError('Temporal inputs must have shape batch,time,5')
        hidden = torch.relu(self.input(values.transpose(1, 2)))
        return self.head(self.blocks(hidden)).transpose(1, 2)


def adjacency(objects):
    """receiver,sender edges, including all ties at the fourth player distance."""
    if objects.ndim != 3 or objects.shape[-2:] != (SLOTS, CHANNELS):
        raise ValueError('Expected frame,64,8 encoded objects')
    visible = objects[..., 4] > 0
    player = visible & ((objects[..., 5] > 0) | (objects[..., 6] > 0))
    ball = visible & (objects[..., 7] > 0)
    xy = objects[..., :2]
    difference = xy[:, :, None, :] - xy[:, None, :, :]
    squared = difference.square().sum(-1)
    distinct = ~torch.eye(SLOTS, dtype=torch.bool, device=objects.device)[None]
    candidates = player[:, :, None] & player[:, None, :] & distinct
    distances = squared.masked_fill(~candidates, float('inf'))
    threshold = torch.sort(distances, dim=-1).values[..., 3:4]
    near = candidates & (distances <= threshold)
    player_ball = (player[:, :, None] & ball[:, None, :]) | (ball[:, :, None] & player[:, None, :])
    return near | player_ball


class GraphRefiner(nn.Module):
    stage = 'graph'

    def __init__(self):
        super().__init__()
        self.node = nn.Linear(8, 8)
        self.message = nn.Sequential(nn.Linear(22, 8), nn.ReLU(), nn.Linear(8, 8))
        self.layers = nn.Sequential(nn.Conv1d(33, 32, 3, padding=1), nn.ReLU(),
                                    nn.Conv1d(32, 32, 3, padding=2, dilation=2), nn.ReLU(),
                                    nn.Conv1d(32, 32, 3, padding=4, dilation=4), nn.ReLU())
        self.head = nn.Conv1d(32, 3, 1)
        nn.init.zeros_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def graph_features(self, objects):
        """Evaluate the shared message MLP only for actual visible graph edges."""
        edges = adjacency(objects)
        visible = objects[..., 4] > 0
        hidden = torch.relu(self.node(objects))
        frame, receiver, sender = torch.nonzero(edges, as_tuple=True)
        relative = objects[frame, sender, :4] - objects[frame, receiver, :4]
        distance = torch.sqrt(relative[..., :2].square().sum(-1, keepdim=True).clamp_min(0))
        same_team = ((objects[frame, sender, 5:7] * objects[frame, receiver, 5:7]).sum(-1, keepdim=True) > 0).to(objects.dtype)
        inputs = torch.cat((hidden[frame, receiver], hidden[frame, sender], relative,
                            distance, same_team), dim=-1)
        messages = self.message(inputs)
        flat_receiver = frame*SLOTS+receiver
        # CPU index_add uses the fixed lexicographic nonzero edge order. The
        # repeated-fit contracts still certify the actual numerical runtime.
        totals = torch.zeros_like(hidden).reshape(-1, 8).index_add(0, flat_receiver, messages)
        counts = torch.zeros((len(objects)*SLOTS, 1), dtype=objects.dtype, device=objects.device)
        counts = counts.index_add(0, flat_receiver, torch.ones((len(frame), 1), dtype=objects.dtype, device=objects.device))
        aggregated = (totals/counts.clamp_min(1)).reshape_as(hidden)
        nodes = torch.relu(hidden+aggregated)*visible.unsqueeze(-1)
        pools = []
        for role in (5, 6, 7):
            mask = (visible & (objects[..., role] > 0)).to(objects.dtype).unsqueeze(-1)
            pools.append((nodes * mask).sum(1) / mask.sum(1).clamp_min(1))
        return torch.cat(pools, dim=-1)

    def forward(self, values):
        if values.ndim != 3 or values.shape[-1] != WIDTH:
            raise ValueError('Graph inputs must have shape batch,time,521')
        batch, frames, _ = values.shape
        objects = values[..., :512].reshape(batch * frames, SLOTS, CHANNELS)
        pooled = self.graph_features(objects).reshape(batch, frames, 24)
        temporal = torch.cat((pooled, values[..., -9:]), dim=-1).transpose(1, 2)
        return self.head(self.layers(temporal)).transpose(1, 2)


def model_for_stage(stage):
    if stage == 'temporal':
        return TemporalRefiner()
    if stage == 'graph':
        return GraphRefiner()
    raise ValueError('Only temporal and graph stages are registered')


def corrected_logits(parent, correction):
    """Differentiable even when the zero-initialized correction is identically zero."""
    if parent.shape != correction.shape or parent.shape[-1] != 3:
        raise ValueError('Parent/correction shapes differ')
    return parent.detach().to(torch.float64).clamp_min(1e-12).log() + correction.to(torch.float64)


def corrected_probabilities(parent, correction):
    parent, correction = np.asarray(parent), np.asarray(correction)
    if parent.shape != correction.shape or parent.ndim != 2 or parent.shape[1] != 3:
        raise ValueError('Parent/correction shapes differ')
    if not np.isfinite(parent).all() or not np.isfinite(correction).all():
        raise ValueError('Nonfinite correction or parent')
    if np.any(parent < 0) or not np.allclose(parent.sum(1), 1, atol=1e-8, rtol=0):
        raise ValueError('Parent probabilities are invalid')
    # Inference-only identity preserves the frozen parent's exact CSV boundary cases.
    # The training path above always retains the correction gradient.
    if np.count_nonzero(correction) == 0:
        return parent.copy()
    logits = np.log(np.maximum(parent, 1e-12)) + correction.astype(np.float64)
    logits -= logits.max(1, keepdims=True)
    values = np.exp(logits)
    return values / values.sum(1, keepdims=True)


def predict(model, x, parent_probs, blocks, batch=1):
    """Full-rate probabilities, with real-half padding and optional graph rotation."""
    from hybrid_data import TemporalContext
    if type(batch) is not int or batch <= 0:
        raise ValueError('Inference batch must be a positive integer')
    x, parent = np.asarray(x), np.asarray(parent_probs)
    if x.shape != (len(parent), WIDTH) or parent.shape[1:] != (3,) or not np.isfinite(x).all():
        raise ValueError('Malformed inference representation')
    output = parent.copy()
    model.eval()
    if model.stage == 'temporal':
        context = TemporalContext(parent, x[:, -4], x[:, -1], blocks)
        descriptions = [(a, min(a + CORE, stop)) for start, stop in blocks for a in range(start, stop, CORE)]
        with torch.no_grad():
            for offset in range(0, len(descriptions), batch):
                group = descriptions[offset:offset+batch]
                windows = [context.window(a, b) for a, b in group]
                values = model(torch.from_numpy(np.stack([w[0] for w in windows])))
                for i, ((a, b), (_, lo, hi, weights)) in enumerate(zip(group, windows)):
                    correction = interpolate(values[i], lo, hi, weights).numpy()
                    output[a:b] = corrected_probabilities(parent[a:b], correction)
        return output
    if model.stage != 'graph':
        raise ValueError('Unregistered correction model')
    descriptions = [(start, stop, a, min(CORE, stop-a)) for start, stop in blocks
                    for a in range(start, stop, CORE)]
    corrections = []
    with torch.no_grad():
        for rotate in (False, True):
            delta = np.zeros_like(parent, dtype=np.float64)
            for offset in range(0, len(descriptions), batch):
                group = descriptions[offset:offset+batch]
                values = []
                group_core = max(item[3] for item in group)
                for start, stop, a, length in group:
                    indices = np.clip(np.arange(a-GRAPH_RADIUS, a+group_core+GRAPH_RADIUS), start, stop-1)
                    chunk = np.asarray(x[indices], dtype=np.float32).copy()
                    if rotate:
                        chunk[:, :512].reshape(-1, SLOTS, CHANNELS)[..., :4] *= -1
                    values.append(chunk)
                result = model(torch.from_numpy(np.stack(values))).numpy().astype(np.float64)
                for i, (_, _, a, length) in enumerate(group):
                    delta[a:a+length] = result[i, GRAPH_RADIUS:GRAPH_RADIUS+length]
            corrections.append(corrected_probabilities(parent, delta))
    if all(np.array_equal(value, parent) for value in corrections):
        return parent.copy()
    mean = .5 * corrections[0] + .5 * corrections[1]
    for start, stop in blocks:
        output[start:stop] = mean[start:stop] / mean[start:stop].sum(1, keepdims=True)
    return output


def interpolate(values, lo, hi, weights):
    device = values.device
    lo = torch.as_tensor(lo, dtype=torch.long, device=device)
    hi = torch.as_tensor(hi, dtype=torch.long, device=device)
    weight = torch.as_tensor(weights, dtype=values.dtype, device=device).unsqueeze(-1)
    return values[lo] * (1-weight) + values[hi] * weight
