"""Original motion TCN with one training-only boundary-supervision head."""
import sys
from pathlib import Path

import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tcn-2026-11-10'))
from tcn_candidate import (TCN as OriginalTCN, configure, predict, transform, fit_scaler,
                           WIDTH, SLOTS, CHANNELS, SEED, WINDOW, HALO, CORE)

ARCHITECTURE = 'original_motion_tcn_training_boundary_head_v1'
SCHEMA = 'original_encoded521_motion_core9_boundary_aux_v1'
BOUNDARY_WEIGHT = 0.1
PARAMETERS = 9668
RECEPTIVE_FIELD = 17


class TCN(OriginalTCN):
    def __init__(self):
        # Main weights have exactly the original initialization/RNG order.
        super().__init__()
        self.boundary = nn.Conv1d(32, 1, 1)

    def forward_with_boundary(self, x):
        batch, frames, width = x.shape
        if width != WIDTH:
            raise ValueError('Expected unchanged 521-column representation')
        objects = x[:, :, :SLOTS * CHANNELS].reshape(batch, frames, SLOTS, CHANNELS)
        encoded = torch.relu(self.object(objects[:, :, :, :5].permute(0, 2, 3, 1)
                             .reshape(batch * SLOTS, 5, frames)))
        encoded = encoded.reshape(batch, SLOTS, 8, frames).permute(0, 3, 1, 2)
        pools = []
        for role in (5, 6, 7):
            mask = objects[:, :, :, role] * objects[:, :, :, 4]
            pools.append((encoded * mask.unsqueeze(-1)).sum(2)
                         / mask.sum(2).clamp_min(1).unsqueeze(-1))
        hidden = torch.cat(pools + [x[:, :, -9:]], dim=-1).transpose(1, 2)
        for layer in list(self.layers.children())[:-1]:
            hidden = layer(hidden)
        return self.layers[-1](hidden).transpose(1, 2), self.boundary(hidden).squeeze(1)

    # Inherited forward uses only original object/layers; boundary head cannot
    # affect inference directly. It affects shared weights only during training.


def boundary_targets(labels, block_starts=None):
    """Binary transitions at t, masked unless both adjacent H/A/D labels exist.

    labels: (batch,time) integer codes; block_starts optionally marks new halves.
    The left crop edge is always masked: an unavailable predecessor is not a
    boundary. Training supplies the full250 window before selecting central200.
    """
    if labels.ndim != 2 or labels.shape[1] == 0:
        raise ValueError('Expected nonempty batch/time labels')
    valid_label = (labels >= 0) & (labels <= 2)
    valid = torch.zeros_like(labels, dtype=torch.bool)
    valid[:, 1:] = valid_label[:, 1:] & valid_label[:, :-1]
    if block_starts is not None:
        if block_starts.shape != labels.shape or block_starts.dtype != torch.bool:
            raise ValueError('Block-start mask must match labels and be boolean')
        valid &= ~block_starts
    target = torch.zeros_like(labels, dtype=torch.float32)
    target[:, 1:] = (labels[:, 1:] != labels[:, :-1]).to(torch.float32)
    target = torch.where(valid, target, torch.zeros_like(target))
    return target, valid


def balanced_boundary_loss(logits, target, valid):
    """Equal positive/negative class means, over the batch's valid frames.

    If only one class exists use that class mean; no valid frames yields a
    differentiable zero. No global/evaluation-label prevalence is consulted.
    """
    if logits.shape != target.shape or logits.shape != valid.shape or valid.dtype != torch.bool:
        raise ValueError('Boundary logits, targets and validity must align')
    if not bool(valid.any()):
        return logits.sum() * 0.0
    selected_targets = target[valid]
    if not bool(((selected_targets == 0) | (selected_targets == 1)).all()):
        raise ValueError('Boundary targets must be binary')
    losses = nn.functional.binary_cross_entropy_with_logits(logits[valid], selected_targets, reduction='none')
    positive = selected_targets == 1
    means = []
    if bool(positive.any()):
        means.append(losses[positive].mean())
    if bool((~positive).any()):
        means.append(losses[~positive].mean())
    return torch.stack(means).mean()
