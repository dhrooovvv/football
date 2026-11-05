"""Label-free team aggregates; no identity continuity is assumed for ATD slots."""
import numpy as np


def build_features(tracking, teams, blocks, pitch=(105.3, 68.), fps=25):
    p, b = tracking.players, tracking.ball
    if teams is None:
        raise ValueError('Team metadata is required')
    teams = np.asarray(teams)
    if teams.shape != (p.shape[1],) or not np.isin(teams, [0, 1]).all() or set(teams) != {0, 1}:
        raise ValueError('Expected an explicit two-team slot mapping')
    if b.shape != (len(p), 3) or p.ndim != 3 or p.shape[-1] != 3:
        raise ValueError('Tracking shape mismatch')
    blocks = list(blocks)
    if fps <= 0 or not np.isfinite(fps) or len(pitch) != 2 or not np.isfinite(pitch).all() or (np.asarray(pitch) <= 0).any():
        raise ValueError('Invalid pitch or frame rate')
    previous_stop = 0
    for start, stop in blocks:
        if any(isinstance(x, bool) or not isinstance(x, (int, np.integer)) for x in (start, stop)) or not previous_stop <= start < stop <= len(p):
            raise ValueError('Invalid half blocks')
        previous_stop = stop
    xy, ball = p[..., :2] * pitch, b[:, :2] * pitch
    visible = np.isfinite(xy).all(axis=2)
    ball_visible = np.isfinite(ball).all(axis=1)
    distances = np.linalg.norm(xy - ball[:, None], axis=2)
    distances[~(visible & ball_visible[:, None])] = np.inf
    out = {'ball_visible': ball_visible.astype(float)}
    for side, label in enumerate(('home', 'away')):
        subset = teams == side
        closest = distances[:, subset].min(axis=1)
        closest[~np.isfinite(closest)] = np.nan
        out[label + '_nearest_ball_m'] = closest
        out[label + '_visible_slots'] = visible[:, subset].sum(axis=1).astype(float)
    gap = np.full(len(b), np.nan)
    velocity = np.full(len(b), np.nan)
    for start, stop in blocks:
        age = 0
        for t in range(start, stop):
            age = 0 if ball_visible[t] else age + 1
            gap[t] = age / fps
            if t > start and ball_visible[t] and ball_visible[t-1]:
                velocity[t] = np.linalg.norm(ball[t] - ball[t-1]) * fps
    out['ball_gap_seconds'] = gap
    out['ball_displacement_speed_m_s'] = velocity
    return out
