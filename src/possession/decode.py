"""Deterministic three-state decoding; no ground truth or data-loading dependency."""
import numpy as np

LABELS = np.array(['H', 'A', 'D'])


def decode(probabilities, transition_cost, blocks=None):
    """Maximise sum(log p) minus transition costs within half-open blocks.

    Class order is H,A,D; transition_cost[previous, next] is nonnegative.
    Equal scores prefer the first class. Each block starts with a uniform prior;
    uncovered frames are X. No state is carried between blocks. Input rows must
    sum to one within absolute 1e-8 (no relative tolerance). Zero probabilities
    alone are floored at 1e-12 for log evaluation. Missing observations must be
    handled upstream: this function accepts finite probabilities only.
    """
    p = np.asarray(probabilities, dtype=np.float64)
    cost = np.asarray(transition_cost, dtype=np.float64)
    if p.ndim != 2 or p.shape[1] != 3:
        raise ValueError('probabilities must have shape (frames, 3)')
    if not np.isfinite(p).all() or (p < 0).any() or (p > 1).any():
        raise ValueError('probabilities must be finite and in [0, 1]')
    if not np.allclose(p.sum(axis=1), 1., atol=1e-8, rtol=0):
        raise ValueError('probability rows must sum to one')
    if cost.shape != (3, 3) or not np.isfinite(cost).all() or (cost < 0).any():
        raise ValueError('transition costs must be a finite nonnegative 3x3 matrix')
    n = len(p)
    blocks = ([(0, n)] if n else []) if blocks is None else list(blocks)
    previous_stop = 0
    for block in blocks:
        if len(block) != 2:
            raise ValueError('blocks must be (start, stop) pairs')
        start, stop = block
        if any(isinstance(v, (bool, np.bool_)) or not isinstance(v, (int, np.integer)) for v in block):
            raise ValueError('block endpoints must be integers')
        if not previous_stop <= start < stop <= n:
            raise ValueError('blocks must be ordered, disjoint and inside the input')
        previous_stop = stop
    out = np.full(n, 'X', dtype='<U1')
    for start, stop in blocks:
        logs = np.log(np.where(p[start:stop] == 0, 1e-12, p[start:stop]))
        score = logs[0].copy()
        back = np.zeros((stop-start, 3), dtype=np.int8)
        for t in range(1, stop-start):
            candidates = score[:, None] - cost
            back[t] = np.argmax(candidates, axis=0)
            score = candidates[back[t], np.arange(3)] + logs[t]
            score -= score.max()  # common shift prevents accumulated scale growth
        state = int(np.argmax(score))
        for t in range(stop-start-1, -1, -1):
            out[start+t] = LABELS[state]
            state = int(back[t, state])
    return out
