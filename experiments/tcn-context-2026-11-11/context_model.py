"""Fixed dense-support temporal extension of the archived trajectory TCN."""
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

sys.path.insert(0, str(Path("experiments/tcn-2026-11-10").resolve()))
from tcn_candidate import configure, transform, SEED, SLOTS, CHANNELS, WIDTH

DILATIONS = (1, 4, 12, 36, 108)
RADIUS = 1 + sum(DILATIONS)
RECEPTIVE_FIELD = 2 * RADIUS + 1
HALO = 163
CORE = 200
WINDOW = CORE + 2 * HALO
PARENT_WINDOW = 250
PARENT_HALO = 25
ARCHITECTURE = "object3_temporal3_d1_4_12_36_108_v1"


class TCN(nn.Module):
    def __init__(self):
        super().__init__()
        self.object = nn.Conv1d(5, 8, 3, padding=1)
        layers = []
        for index, dilation in enumerate(DILATIONS):
            layers.extend((nn.Conv1d(33 if index == 0 else 32, 32, 3,
                                     padding=dilation, dilation=dilation), nn.ReLU()))
        layers.append(nn.Conv1d(32, 3, 1))
        self.layers = nn.Sequential(*layers)

    def forward(self, x):
        batch, frames, _ = x.shape
        objects = x[:, :, :SLOTS * CHANNELS].reshape(batch, frames, SLOTS, CHANNELS)
        encoded = torch.relu(self.object(objects[:, :, :, :5].permute(0, 2, 3, 1)
                                         .reshape(batch * SLOTS, 5, frames)))
        encoded = encoded.reshape(batch, SLOTS, 8, frames).permute(0, 3, 1, 2)
        pools = []
        for role in (5, 6, 7):
            mask = objects[:, :, :, role] * objects[:, :, :, 4]
            pools.append((encoded * mask.unsqueeze(-1)).sum(2)
                         / mask.sum(2).clamp_min(1).unsqueeze(-1))
        combined = torch.cat(pools + [x[:, :, -9:]], dim=-1)
        return self.layers(combined.transpose(1, 2)).transpose(1, 2)


def predict(model, x, blocks, scaler, batch=1):
    if not isinstance(batch, int) or batch <= 0:
        raise ValueError("Batch size must be a positive integer")
    x = transform(x, scaler)
    probabilities = np.full((len(x), 3), 1 / 3, dtype=np.float64)
    seen = np.zeros(len(x), dtype=np.int8)
    items = []
    previous_stop = 0
    for start, stop in blocks:
        if not previous_stop <= start < stop <= len(x):
            raise ValueError("Half blocks must be ordered, disjoint and inside input")
        previous_stop = stop
        for core_start in range(start, stop, CORE):
            items.append((int(start), int(stop), int(core_start), int(min(CORE, stop - core_start))))
    with torch.no_grad():
        for offset in range(0, len(items), batch):
            descriptions = items[offset:offset + batch]
            values = np.stack([x[np.clip(np.arange(s - HALO, s + CORE + HALO), a, b - 1)]
                               for a, b, s, length in descriptions])
            result = torch.softmax(model(torch.from_numpy(values)), dim=-1).numpy().astype(np.float64)
            for index, (a, b, start, length) in enumerate(descriptions):
                probabilities[start:start + length] = result[index, HALO:HALO + length]
                seen[start:start + length] += 1
    for start, stop in blocks:
        if not (seen[start:stop] == 1).all():
            raise RuntimeError("Prediction coverage differs from once per half frame")
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    if not np.isfinite(probabilities).all():
        raise RuntimeError("Nonfinite context probabilities")
    return probabilities
