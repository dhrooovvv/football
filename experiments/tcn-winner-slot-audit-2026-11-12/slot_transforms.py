"""External-only diagnostic representation stress; no model or label dependency."""
import numpy as np

SLOTS, CHANNELS, WIDTH = 64, 8, 521


def permute_slots(x, blocks, seed, mode="static"):
    """Permute players within team; preserve ball, core and observation-mask multiset.

    Static: one independent permutation per team/half. Dynamic: independent
    permutation each frame. Dynamic/rederived-identity: recompute player velocities using
    encoded XY / 2 and 25Hz; neighboring observations must both exist. This
    deliberately destroys slot identity for a worst-case stress diagnostic.
    """
    if mode not in ("static", "dynamic", "rederived_identity"):
        raise ValueError("Unknown diagnostic mode")
    dynamic = mode == "dynamic"
    x = np.asarray(x)
    if x.ndim != 2 or x.shape[1] != WIDTH or not np.isfinite(x).all():
        raise ValueError('Expected finite521-column encoded input')
    out = x.copy()
    source = x[:, :SLOTS * CHANNELS].reshape(len(x), SLOTS, CHANNELS)
    target = out[:, :SLOTS * CHANNELS].reshape(len(x), SLOTS, CHANNELS)
    rng = np.random.default_rng(seed)
    previous = 0
    for start, stop in blocks:
        if not previous <= start < stop <= len(x):
            raise ValueError('Invalid half blocks')
        previous = stop
        roles = source[start, :, 5:8]
        if not np.array_equal(source[start:stop, :, 5:8],
                              np.broadcast_to(roles, (stop - start, SLOTS, 3))):
            raise ValueError('Team role changed inside a half')
        if not np.isin(roles, [0, 1]).all() or (roles.sum(1) > 1).any():
            raise ValueError('Invalid role flags')
        if not np.array_equal(roles[-1], [0, 0, 1]) or roles[:-1, 2].any():
            raise ValueError('Expected unique last-slot ball')
        for team in (() if mode == "rederived_identity" else (5, 6)):
            slots = np.flatnonzero(source[start, :SLOTS - 1, team] == 1)
            if dynamic:
                for frame in range(start, stop):
                    target[frame, slots] = source[frame, rng.permutation(slots)]
            else:
                order = rng.permutation(slots)
                target[start:stop, slots] = source[start:stop, order]
        if mode == "static":
            continue
        players = target[start:stop, :SLOTS - 1]
        players[:, :, 2:4] = 0
        supported = (players[1:, :, 4] == 1) & (players[:-1, :, 4] == 1)
        velocity = np.diff(players[:, :, :2], axis=0) * 12.5
        players[1:, :, 2:4] = np.where(supported[:, :, None],
                                      np.clip(velocity, -5, 5), 0)
    if not np.array_equal(out[:, -9:], x[:, -9:]):
        raise RuntimeError('Core features changed')
    if not np.array_equal(target[:, -1], source[:, -1]):
        raise RuntimeError('Ball changed')
    return out
