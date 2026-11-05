"""Strict local input contracts. Errors never include raw asset contents."""
from dataclasses import dataclass
import csv
import xml.etree.ElementTree as ET
import numpy as np


@dataclass
class Tracking:
    players: np.ndarray  # frame, slot, (normalised x, y, supplied speed)
    ball: np.ndarray


def load_atd(path, n_frames, expected_slots=None):
    players = None
    ball = np.empty((n_frames, 3), dtype=np.float64)
    count = 0
    with open(path) as handle:
        for i, line in enumerate(handle):
            if i >= n_frames:
                raise ValueError('ATD has extra frames')
            parts = line.strip().split(':')
            if len(parts) != 3 or parts[0] != str(i + 1):
                raise ValueError('ATD frame IDs must be exactly sequential 1..N')
            groups = parts[1].split(';')
            if players is None:
                slots = len(groups)
                if not parts[1] or (expected_slots is not None and slots != expected_slots):
                    raise ValueError('ATD slot count mismatch')
                players = np.empty((n_frames, slots, 3), dtype=np.float64)
            if len(groups) != players.shape[1]:
                raise ValueError('ATD slot count changed')
            values = []
            for group in groups + [parts[2]]:
                fields = group.split(',')
                if len(fields) != 3:
                    raise ValueError('ATD group must have three fields')
                try:
                    row = [float(x) for x in fields]
                except ValueError:
                    raise ValueError('ATD nonnumeric field') from None
                if np.isinf(row).any():
                    raise ValueError('ATD contains infinity')
                values.append(row)
            players[i] = values[:-1]
            ball[i] = values[-1]
            count += 1
    if count != n_frames or players is None:
        raise ValueError('ATD missing frames')
    return Tracking(players, ball)


def load_teams(path, expected_slots, home_name, away_name):
    root = ET.parse(path).getroot()
    teams = list(root.iter('Team'))
    ids = [t.get('id') for t in teams]
    names = [t.findtext('Name') for t in teams]
    if len(ids) != 2 or None in ids or len(set(ids)) != 2:
        raise ValueError('Metadata requires two distinct team IDs')
    if home_name == away_name or set(names) != {home_name, away_name}:
        raise ValueError('Metadata names do not match explicit home/away mapping')
    mapping = {ids[names.index(home_name)]: 0, ids[names.index(away_name)]: 1}
    slots = [p.get('teamId') for p in root.iter('Player')]
    if len(slots) != expected_slots or any(s not in mapping for s in slots):
        raise ValueError('Metadata slot/team mismatch')
    return np.array([mapping[s] for s in slots], dtype=np.int8)


@dataclass
class Homography:
    matrices: np.ndarray
    valid: np.ndarray

    def project(self, frame, xy):
        if not self.valid[frame]:
            raise ValueError('Cannot project an invalid homography')
        points = np.asarray(xy, dtype=float)
        if points.shape[-1] != 2:
            raise ValueError('Expected xy points')
        h = np.concatenate([points, np.ones(points.shape[:-1] + (1,))], axis=-1) @ self.matrices[frame].T
        if np.any(np.abs(h[..., 2]) < 1e-12):
            raise ValueError('Projection at infinity')
        return h[..., :2] / h[..., 2:]


def load_homography(path, n_frames):
    import pandas as pd
    table = pd.read_csv(path)
    cols = [f'h{i}{j}' for i in range(3) for j in range(3)]
    required = ['frame', 'valid', 'reprojection_error'] + cols
    if any(c not in table for c in required):
        raise ValueError('Homography columns missing')
    if len(table) != n_frames or not np.array_equal(table.frame.to_numpy(), np.arange(n_frames)):
        raise ValueError('Homography frames must be sequential 0..N-1')
    if not table.valid.isin([0, 1]).all():
        raise ValueError('Homography valid flag must be 0/1')
    valid = table.valid.to_numpy(dtype=bool)
    matrices = table[cols].to_numpy(dtype=float).reshape(-1, 3, 3)
    error = table.reprojection_error.to_numpy(dtype=float)
    if not np.isfinite(matrices[valid]).all() or not np.isfinite(error[valid]).all() or (error[valid] < 0).any():
        raise ValueError('Valid homography contains invalid numbers')
    if (np.linalg.matrix_rank(matrices[valid]) < 3).any():
        raise ValueError('Valid homography is singular')
    matrices[~valid] = np.nan
    return Homography(matrices, valid)


def load_tags(path, n_frames, fps=25):
    events = []
    for node in ET.parse(path).iter('instance'):
        try:
            start, stop = [int(round(float(node.findtext(k)) * fps)) for k in ('start', 'end')]
        except (ValueError, TypeError, OverflowError):
            raise ValueError('Invalid tag timestamp') from None
        if not 0 <= start < stop <= n_frames:
            raise ValueError('Tag interval must be nonempty and inside video')
        tags = {}
        for label in node.findall('label'):
            key, value = label.findtext('group'), label.findtext('text')
            if key in tags and tags[key] != value:
                raise ValueError('Conflicting tag values')
            tags[key] = value
        events.append(dict(start=start, stop=stop, code=node.findtext('code'), tags=tags))
    return events


def tag_ownership(event, home_name, away_name):
    """Soft ownership hint only; set pieces and unknown phases stay neutral."""
    team = {home_name: 'H', away_name: 'A'}.get(event['tags'].get('Team'))
    code = (event['code'] or '').lower()
    offensive = {'build up', 'progression', 'creating chances', 'long ball',
                 'attacking transition', 'ball in final third', 'ball in the box'}
    defensive = {'defending in defensive third', 'defending in middle third',
                 'defending in attacking third', 'defensive transition'}
    if code in offensive:
        return team
    if code in defensive and team is not None:
        return {'H': 'A', 'A': 'H'}[team]
    return None


def export_labels(path, labels, n_frames):
    labels = np.asarray(labels)
    if labels.shape != (n_frames,) or not np.isin(labels, ['H', 'A', 'D', 'X']).all():
        raise ValueError('Expected exactly N labels from H/A/D/X')
    with open(path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['frame', 'label'])
        writer.writerows(enumerate(labels.tolist()))
