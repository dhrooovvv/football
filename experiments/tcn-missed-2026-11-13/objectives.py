"""Fold-training-only spell indexing, exposure sampling and soft segment overlap."""
from pathlib import Path
import sys

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tcn-expanded-2026-11-10'))
from expanded_data import valid_windows

WINDOW, HALO, CORE, SHORT, FLANK = 250, 25, 200, 50, 25
EPSILON = 1e-6


class SegmentIndex:
    """Maximal labelled segments within each original half and known-label run."""
    def __init__(self, case):
        self.rows = []
        for block_start, block_stop in case.blocks:
            y = np.asarray(case.labels[block_start:block_stop])
            known = (y >= 0) & (y <= 2)
            edges = np.diff(np.r_[False, known, False].astype(np.int8))
            for a, b in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)):
                first, stop = int(block_start + a), int(block_start + b)
                changes = np.flatnonzero(y[a + 1:b] != y[a:b - 1]) + first + 1
                bounds = [first, *map(int, changes), stop]
                local = [(left, right, int(case.labels[left]))
                         for left, right in zip(bounds[:-1], bounds[1:])]
                for i, (left, right, team) in enumerate(local):
                    # A context cannot run through another segment or an unknown/half edge.
                    previous = local[i - 1][0] if i else left
                    following = local[i + 1][1] if i + 1 < len(local) else right
                    self.rows.append((left, right, team, previous, following))
        self.starts = np.asarray([r[0] for r in self.rows], dtype=np.int64)

    def contained(self, left, right):
        first = int(np.searchsorted(self.starts, left, side='left'))
        stop = int(np.searchsorted(self.starts, right, side='left'))
        return [r for r in self.rows[first:stop] if r[1] <= right and r[2] in (0, 1)]

    def supports(self, start):
        """Return (team, spell-left/right, support-left/right), relative to central core."""
        left, right = start + HALO, start + HALO + CORE
        result = []
        for a, b, team, previous, following in self.contained(left, right):
            support_left = max(left, a - FLANK, previous)
            support_right = min(right, b + FLANK, following)
            result.append((team, a - left, b - left,
                           support_left - left, support_right - left))
        return result


class WindowSampler:
    """Original uniform starts, or an explicitly equal short-spell/uniform mixture."""
    def __init__(self, cases, mode):
        if mode not in ('uniform', 'short_mix'):
            raise ValueError('Unknown fixed sampler')
        self.mode, self.records = mode, valid_windows(cases, WINDOW)
        self.cumulative = np.cumsum([r[2] for r in self.records], dtype=np.int64)
        if len(self.cumulative) == 0 or self.cumulative[-1] <= 0:
            raise ValueError('No valid complete known-label windows')
        self.indices = [SegmentIndex(case) for case in cases]
        self.eligible, self.audit = [], {}
        for ci, (case, index) in enumerate(zip(cases, self.indices)):
            eligible, excluded = 0, 0
            for a, b, team, _, _ in index.rows:
                if team not in (0, 1) or b - a > SHORT:
                    continue
                ranges = []
                for record_case, first, count in self.records:
                    if record_case != ci:
                        continue
                    lo = max(first, b - HALO - CORE)
                    hi = min(first + count - 1, a - HALO)
                    if lo <= hi:
                        ranges.append((lo, hi))
                if len(ranges) > 1:
                    raise ValueError('A spell belongs to multiple known half runs')
                if ranges:
                    self.eligible.append((ci, a, b, team, *ranges[0]))
                    eligible += 1
                else:
                    excluded += 1
            self.audit[case.key] = dict(eligible_short_spells=eligible,
                                       excluded_short_spells=excluded)
        if mode == 'short_mix' and not self.eligible:
            raise ValueError('No eligible short spells; fixed mixture cannot be implemented')

    def uniform(self, draw):
        if not 0 <= draw < int(self.cumulative[-1]):
            raise ValueError('Uniform draw outside valid support')
        row = int(np.searchsorted(self.cumulative, draw, side='right'))
        ci, first, _ = self.records[row]
        return ci, first + int(draw - (self.cumulative[row - 1] if row else 0))

    def batch(self, window_rng, sampler_rng, size=8):
        if self.mode == 'uniform':
            return [(*self.uniform(int(draw)), 'uniform')
                    for draw in window_rng.integers(0, int(self.cumulative[-1]), size=size)]
        choices = sampler_rng.random(size) < .5
        result = []
        for short in choices:
            if short:
                ci, _, _, _, lo, hi = self.eligible[int(sampler_rng.integers(len(self.eligible)))]
                result.append((ci, int(window_rng.integers(lo, hi + 1)), 'short'))
            else:
                ci, start = self.uniform(int(window_rng.integers(int(self.cumulative[-1]))))
                result.append((ci, start, 'uniform'))
        return result

    def short_exposure(self, case_index, start):
        return sum(b - a <= SHORT for a, b, _, _, _ in
                   self.indices[case_index].contained(start + HALO, start + HALO + CORE))


def segment_soft_iou(logits, batch_supports):
    """Mean over complete H/A spells, not over frames, classes or windows.

    logits: B x 200 x 3; supports retain original match-segment identity.
    No-support result retains a differentiable connection to logits.
    """
    if logits.ndim != 3 or logits.shape[1:] != (CORE, 3) or len(batch_supports) != logits.shape[0]:
        raise ValueError('Expected B x 200 x 3 logits and one support list per window')
    if not any(batch_supports):
        return logits.sum() * 0., 0
    probabilities = torch.softmax(logits, dim=-1)
    losses = []
    for batch, supports in enumerate(batch_supports):
        for team, a, b, lo, hi in supports:
            if team not in (0, 1) or not 0 <= lo <= a < b <= hi <= CORE:
                raise ValueError('Invalid complete-spell context')
            p = probabilities[batch, lo:hi, team]
            intersection = p[a - lo:b - lo].sum()
            union = p.sum() - intersection + (b - a)
            losses.append(1. - (intersection + EPSILON) / (union + EPSILON))
    return torch.stack(losses).mean(), len(losses)
