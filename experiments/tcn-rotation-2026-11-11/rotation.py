"""One fixed physical pitch rotation; no team/label relabelling."""
import numpy as np

WIDTH, SLOTS, CHANNELS = 521, 64, 8


def rotate180(x):
    """Rotate centered XY/velocity by180degrees, preserving role/mask/core fields."""
    x = np.asarray(x)
    if x.ndim != 2 or x.shape[1] != WIDTH or not np.issubdtype(x.dtype, np.floating):
        raise ValueError('Expected floating521-column input')
    if not np.isfinite(x).all():
        raise ValueError('Encoded input must be finite')
    out = x.copy()
    objects = out[:, :SLOTS * CHANNELS].reshape(len(out), SLOTS, CHANNELS)
    objects[:, :, :4] *= -1
    return out


def average_views(original, rotated):
    """Equal probability average, unchanged H/A/D column order; never average logits."""
    original, rotated = np.asarray(original), np.asarray(rotated)
    if original.ndim != 2 or original.shape[1] != 3 or rotated.shape != original.shape:
        raise ValueError('Expected two matching(frames,3) probability arrays')
    for p in (original, rotated):
        if not np.isfinite(p).all() or (p < 0).any() or (p > 1).any():
            raise ValueError('Probabilities outside finite[0,1] range')
        if not np.allclose(p.sum(1), 1, atol=1e-8, rtol=0):
            raise ValueError('Probability rows must sum to one')
    mean = .5 * original + .5 * rotated
    return mean / mean.sum(1, keepdims=True)
