"""Original motion/class TCN plus a discarded geometric-pretraining head."""
import sys
from pathlib import Path

import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tcn-2026-11-10'))
from tcn_candidate import (TCN as OriginalTCN, configure, predict, transform, fit_scaler,
                           WIDTH, SLOTS, CHANNELS, SEED, WINDOW, HALO, CORE)

ARCHITECTURE = 'original_motion_tcn_geometric_pretraining_head_v1'
SCHEMA = 'original_encoded521_core9_observed_masked_ballXY_v1'
PARAMETERS = 9701
RECEPTIVE_FIELD = 17


class TCN(OriginalTCN):
    def __init__(self):
        # Preserve every original parameter's initialization and ordering first.
        super().__init__()
        self.reconstruction = nn.Conv1d(32, 2, 1)

    def forward_reconstruction(self, x):
        batch, frames, width = x.shape
        if width != WIDTH:
            raise ValueError('Expected unchanged 521-column representation')
        objects = x[:, :, :SLOTS * CHANNELS].reshape(batch, frames, SLOTS, CHANNELS)
        hidden = torch.relu(self.object(objects[:, :, :, :5].permute(0, 2, 3, 1)
                            .reshape(batch * SLOTS, 5, frames)))
        hidden = hidden.reshape(batch, SLOTS, 8, frames).permute(0, 3, 1, 2)
        pools = []
        for role in (5, 6, 7):
            mask = objects[:, :, :, role] * objects[:, :, :, 4]
            pools.append((hidden * mask.unsqueeze(-1)).sum(2)
                         / mask.sum(2).clamp_min(1).unsqueeze(-1))
        hidden = torch.cat(pools + [x[:, :, -9:]], dim=-1).transpose(1, 2)
        for layer in list(self.layers.children())[:-1]:
            hidden = layer(hidden)
        return self.reconstruction(hidden).transpose(1, 2)

    # Class inference remains OriginalTCN.forward; reconstruction is never fused.


def reconstruction_loss(prediction, target, valid):
    """Mean XY squared error on genuinely observed, synthetically hidden frames."""
    if prediction.shape != target.shape or prediction.ndim != 3 or prediction.shape[-1] != 2:
        raise ValueError('Expected aligned batch/time/XY prediction and target')
    if valid.shape != prediction.shape[:-1] or valid.dtype != torch.bool:
        raise ValueError('Expected a boolean batch/time target mask')
    if not bool(valid.any()):
        raise ValueError('No genuinely observed synthetic-mask targets in this batch')
    selected = target[valid]
    if not bool(torch.isfinite(selected).all()):
        raise ValueError('Nonfinite observed target')
    return ((prediction[valid] - selected) ** 2).mean()
