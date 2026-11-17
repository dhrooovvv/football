"""Geometry-only compact input reader; possession labels are never opened."""
import json
from pathlib import Path

import numpy as np

SLOTS = 64
WIDTH = 521
WINDOW = 250
HALO = 25
CORE = 200
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
PROTECTED = {'idsse-J03WQQ', 'idsse-J03WR9'} | {
    'pff-' + value for value in ('3846', '3831', '3841', '10512', '3847', '10506',
    '3833', '3819', '10505', '3849', '3858', '3834', '3812', '3820', '3851', '3845')}
GEOMETRY_FILES = ('objects.npy', 'roles.npy', 'core.npy', 'gap_ball.npy', 'gap_core.npy')


class GeometryCase:
    def __init__(self, directory):
        self.directory = Path(directory)
        if self.directory.name in PROTECTED:
            raise ValueError('Protected match forbidden before reading geometry')
        self.metadata = json.loads((self.directory / 'metadata.json').read_text())
        self.key = self.metadata['key']
        self.provider = self.metadata['provider']
        self.blocks = self.metadata['blocks']
        if self.key in PROTECTED or self.key != self.directory.name:
            raise ValueError('Protected or inconsistent geometry identity')
        if self.provider not in ('idsse', 'pff') or not self.key.startswith(self.provider + '-'):
            raise ValueError('Invalid geometry provider/key')
        frames = self.metadata['frames']
        if not isinstance(frames, int) or frames <= 0:
            raise ValueError('Invalid geometry frame count')
        self.arrays = {name: np.load(self.directory / name,
                       mmap_mode=None if name == 'roles.npy' else 'r', allow_pickle=False)
                       for name in GEOMETRY_FILES}
        expected = {'objects.npy': (frames, SLOTS, 5), 'roles.npy': (SLOTS, 3),
                    'core.npy': (frames, 9), 'gap_ball.npy': (frames, 5),
                    'gap_core.npy': (frames, 9)}
        if any(self.arrays[name].shape != shape or self.arrays[name].dtype != np.float32
               for name, shape in expected.items()):
            raise ValueError('Malformed geometry shape/dtype')
        roles = self.arrays['roles.npy']
        if not np.isfinite(roles).all() or not np.isin(roles, (0, 1)).all() \
                or (roles.sum(1) > 1).any() or roles[:, 2].sum() != 1 \
                or not np.array_equal(roles[-1], [0, 0, 1]):
            raise ValueError('Roles must identify a unique final-slot ball')
        previous_stop = 0
        for start, stop in self.blocks:
            if not isinstance(start, int) or not isinstance(stop, int) \
                    or not 0 <= previous_stop <= start < stop <= frames:
                raise ValueError('Malformed/overlapping half blocks')
            previous_stop = stop
        if not self.blocks:
            raise ValueError('No half blocks')

    def read(self, indices, augmented=True):
        indices = np.asarray(indices)
        objects = np.empty((len(indices), SLOTS, 8), dtype=np.float32)
        objects[:, :, :5] = self.arrays['objects.npy'][indices]
        objects[:, :, 5:8] = self.arrays['roles.npy']
        core = self.arrays['gap_core.npy' if augmented else 'core.npy'][indices]
        if augmented:
            objects[:, -1, :5] = self.arrays['gap_ball.npy'][indices]
        result = np.column_stack((objects.reshape(len(indices), 512), core))
        if not np.isfinite(result).all():
            raise ValueError('Nonfinite encoded geometry input')
        return result

    def targets(self, indices):
        ball = self.arrays['objects.npy'][indices, -1]
        gap = self.arrays['gap_ball.npy'][indices]
        if not np.isin(ball[:, 4], (0, 1)).all() or not np.isin(gap[:, 4], (0, 1)).all():
            raise ValueError('Observation flags must be binary')
        if ((gap[:, 4] == 1) & (ball[:, 4] == 0)).any():
            raise ValueError('Corruption cannot invent observations')
        valid = (ball[:, 4] == 1) & (gap[:, 4] == 0)
        target = np.asarray(ball[:, :2], dtype=np.float32).copy()
        target[~valid] = 0
        if not np.isfinite(target[valid]).all():
            raise ValueError('Nonfinite observed ball target')
        return target, valid


def eligible_starts(case, window=WINDOW, halo=HALO, core=CORE):
    """Full-half anchors with at least one central synthetic target; no labels."""
    if window != WINDOW or halo != HALO or core != CORE:
        raise ValueError('Frozen250/25/200 pretraining window required')
    starts = []
    for first, stop in case.blocks:
        if stop - first < window:
            continue
        _, valid = case.targets(np.arange(first, stop))
        cumulative = np.r_[0, np.cumsum(valid, dtype=np.int64)]
        offsets = np.arange(stop - first - window + 1)
        counts = cumulative[offsets + halo + core] - cumulative[offsets + halo]
        starts.append((offsets[counts > 0] + first).astype(np.int64))
    result = np.concatenate(starts) if starts else np.empty(0, np.int64)
    if not len(result):
        raise ValueError('No observed synthetic-mask geometry windows: ' + case.key)
    return result


def validate_membership(supervised_cases, geometry_cases, held_out, allowed_pff):
    if held_out not in IDS or allowed_pff is None:
        raise ValueError('Explicit held-out match and allowed PFF membership required')
    supervised_keys = [case.key for case in supervised_cases]
    expected = {'idsse-' + match for match in IDS if match != held_out}
    if len(supervised_keys) != 4 or set(supervised_keys) != expected \
            or any(case.provider != 'idsse' for case in supervised_cases):
        raise ValueError('Supervised cases must be exactly the four training IDSSE matches')
    pff = ['pff-' + str(match).removeprefix('pff-') for match in allowed_pff]
    if len(set(pff)) != len(pff) or set(pff) & PROTECTED:
        raise ValueError('Protected/duplicate allowed PFF membership')
    geometry_keys = [case.key for case in geometry_cases]
    if geometry_cases and (len(geometry_keys) != len(expected) + len(pff)
            or set(geometry_keys) != expected | set(pff)):
        raise ValueError('Geometry cases differ from exact fold-local training pool')
    for case in geometry_cases:
        if case.key in PROTECTED or case.key == 'idsse-' + held_out \
                or not case.key.startswith(case.provider + '-'):
            raise ValueError('Protected or held-out geometry forbidden')
