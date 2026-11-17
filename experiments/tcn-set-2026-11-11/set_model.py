"""Frame-wise masked set encoding before the frozen short temporal network."""
import sys
from pathlib import Path

import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tcn-2026-11-10'))
from tcn_candidate import (configure, predict, transform, fit_scaler,
                           WIDTH, SLOTS, CHANNELS, SEED, WINDOW, HALO, CORE)

ARCHITECTURE = 'pointwise_xy_visibility8_team_mean_temporal_d1_2_4_v1'
SCHEMA = 'encoded521_ignore_object_velocity_use_0_1_4_core9_v1'
OBJECT_CHANNELS = (0, 1, 4)
DILATIONS = (1, 2, 4)
RADIUS = sum(DILATIONS)
RECEPTIVE_FIELD = 2 * RADIUS + 1
PARAMETERS = 9539


class TCN(nn.Module):
    """No per-object history or adjacent-slot velocity reaches the set encoder.

    A different same-team slot permutation at each frame preserves the
    mathematical output. Floating reduction order need not preserve every bit.
    Core ball speed remains available through the unchanged nine core columns.
    """
    def __init__(self):
        super().__init__()
        self.object = nn.Linear(3, 8)
        self.layers = nn.Sequential(
            nn.Conv1d(33, 32, 3, padding=1), nn.ReLU(),
            nn.Conv1d(32, 32, 3, padding=2, dilation=2), nn.ReLU(),
            nn.Conv1d(32, 32, 3, padding=4, dilation=4), nn.ReLU(),
            nn.Conv1d(32, 3, 1))

    def forward(self, x):
        batch, frames, width = x.shape
        if width != WIDTH:
            raise ValueError('Expected the unchanged521-column representation')
        objects = x[:, :, :SLOTS * CHANNELS].reshape(batch, frames, SLOTS, CHANNELS)
        encoded = torch.relu(self.object(objects[:, :, :, list(OBJECT_CHANNELS)]))
        pools = []
        for role in (5, 6, 7):
            mask = objects[:, :, :, role] * objects[:, :, :, 4]
            pools.append((encoded * mask.unsqueeze(-1)).sum(2)
                         / mask.sum(2).clamp_min(1).unsqueeze(-1))
        combined = torch.cat(pools + [x[:, :, -9:]], dim=-1)
        return self.layers(combined.transpose(1, 2)).transpose(1, 2)
