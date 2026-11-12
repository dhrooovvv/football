"""Two fixed candidates; class encoder/history and input schema remain unchanged."""
import math
from pathlib import Path
import sys

import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tcn-pretrain-2026-11-11'))
from pretrain_model import (TCN as OriginalTCN, configure, predict, WIDTH, SLOTS,
                           CHANNELS, WINDOW, HALO, CORE)

INITIALIZATION_SEEDS = {'attention': 20261106, 'ensemble': 20261107}
ARCHITECTURES = {'attention': 'original_motion_tcn_masked_team_self_attention_v1',
                 'ensemble': 'original_motion_tcn_geometric_pretraining_head_v1'}
PARAMETERS = {'attention': 9917, 'ensemble': 9701}
SCHEMA = 'original_encoded521_core9_observed_masked_ballXY_v1'


class AttentionTCN(OriginalTCN):
    def __init__(self):
        # Construct every original parameter, including the unused reconstruction
        # head, first. The retained weights therefore start identically to parent.
        super().__init__()
        self.query = nn.Linear(8, 8)
        self.key = nn.Linear(8, 8)
        self.value = nn.Linear(8, 8)

    def attend(self, hidden, visible):
        """One shared head within one team; never attend to an unobserved key.

        The mean over observed queries produces the same8-channel interface as
        the old pool. Finite masked logits, explicit renormalization and query
        masking make an entirely missing team return exact zeros.
        """
        q, k, v = self.query(hidden), self.key(hidden), self.value(hidden)
        scores = torch.matmul(q, k.transpose(-1, -2)) / math.sqrt(8.)
        key_mask = visible.unsqueeze(-2)
        scores = scores.masked_fill(~key_mask, -1.e9)
        weights = torch.softmax(scores, dim=-1) * key_mask.to(scores.dtype)
        weights = weights / weights.sum(-1, keepdim=True).clamp_min(1.e-12)
        context = torch.matmul(weights, v)
        query_mask = visible.to(context.dtype).unsqueeze(-1)
        return (context * query_mask).sum(-2) / query_mask.sum(-2).clamp_min(1.)

    def forward(self, x):
        batch, frames, width = x.shape
        if width != WIDTH:
            raise ValueError('Expected unchanged521-column representation')
        objects = x[:, :, :SLOTS * CHANNELS].reshape(batch, frames, SLOTS, CHANNELS)
        hidden = torch.relu(self.object(objects[:, :, :, :5].permute(0, 2, 3, 1)
                            .reshape(batch * SLOTS, 5, frames)))
        hidden = hidden.reshape(batch, SLOTS, 8, frames).permute(0, 3, 1, 2)
        pools = []
        for role in (5, 6):
            visible = (objects[:, :, :, role] * objects[:, :, :, 4]) > 0
            pools.append(self.attend(hidden, visible))
        ball_mask = objects[:, :, :, 7] * objects[:, :, :, 4]
        pools.append((hidden * ball_mask.unsqueeze(-1)).sum(2)
                     / ball_mask.sum(2).clamp_min(1).unsqueeze(-1))
        pooled = torch.cat(pools + [x[:, :, -9:]], dim=-1)
        return self.layers(pooled.transpose(1, 2)).transpose(1, 2)


def model_for_arm(arm):
    if arm not in INITIALIZATION_SEEDS:
        raise ValueError('Only registered attention or ensemble arm allowed')
    return AttentionTCN() if arm == 'attention' else OriginalTCN()
