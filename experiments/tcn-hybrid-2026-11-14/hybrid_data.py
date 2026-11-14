"""Half-anchored coarse context and source cases for frozen-parent correction."""
from pathlib import Path

import numpy as np

CORE, TEMPORAL_RADIUS, TEMPORAL_WINDOW = 200, 63, 169


def validate_blocks(blocks, frames):
    previous = 0
    for start, stop in blocks:
        if type(start) not in (int, np.int64) or type(stop) not in (int, np.int64):
            raise ValueError('Half bounds must be integer frame indices')
        if not previous <= start < stop <= frames:
            raise ValueError('Half bounds must be ordered, disjoint and inside the case')
        previous = stop


class TemporalContext:
    """The full half grid is fixed before any training or inference chunking.

    Each coarse prediction depends on63 bins in each direction. A full-rate
    prediction interpolates at most two neighboring coarse predictions. Inputs
    contain up to43 required coarse bracket bins plus63 left/right bins=169.
    The parent itself contributes its original8-frame radius. Partial final
    bins use their actual arithmetic frame centre.
    """
    def __init__(self, parent, observed, gap_age, blocks):
        parent = np.asarray(parent)
        observed, gap_age = np.asarray(observed), np.asarray(gap_age)
        if parent.ndim != 2 or parent.shape[1] != 3 or observed.shape != (len(parent),) or gap_age.shape != observed.shape:
            raise ValueError('Malformed parent or missingness channels')
        if not np.isfinite(parent).all() or not np.isfinite(observed).all() or not np.isfinite(gap_age).all():
            raise ValueError('Nonfinite temporal input')
        validate_blocks(blocks, len(parent))
        self.rows = []
        for start, stop in blocks:
            starts = np.arange(start, stop, 5, dtype=np.int64)
            ends = np.minimum(starts+5, stop)
            centres = (starts+ends-1)/2.
            features = np.empty((len(starts), 5), dtype=np.float32)
            for i, (a, b) in enumerate(zip(starts, ends)):
                features[i, :3] = parent[a:b].mean(0)
                features[i, 3] = observed[a:b].mean()
                features[i, 4] = gap_age[a:b].mean()
            self.rows.append((int(start), int(stop), centres, features))

    def window(self, left, right):
        if not 0 < right-left <= CORE:
            raise ValueError('Temporal target must contain between1and200frames')
        containing = [r for r in self.rows if r[0] <= left < right <= r[1]]
        if len(containing) != 1:
            raise ValueError('Temporal target crosses half or lies outside registered blocks')
        _, _, centres, features = containing[0]
        targets = np.arange(left, right, dtype=np.float64)
        upper = np.searchsorted(centres, targets, side='right')
        lower = np.clip(upper-1, 0, len(centres)-1)
        upper = np.clip(upper, 0, len(centres)-1)
        denominator = centres[upper]-centres[lower]
        weights = np.divide(targets-centres[lower], denominator,
                            out=np.zeros(len(targets), dtype=np.float64), where=denominator > 0)
        weights = np.clip(weights, 0, 1)
        first = int(lower.min())-TEMPORAL_RADIUS
        last_needed = int(upper.max())+TEMPORAL_RADIUS
        if last_needed >= first+TEMPORAL_WINDOW:
            raise ValueError('Registered temporal halo is insufficient')
        indices = np.clip(np.arange(first, first+TEMPORAL_WINDOW), 0, len(features)-1)
        return features[indices], lower-first, upper-first, weights


class HybridCase:
    """Training view of an existing compact case and exact cached parent arrays."""
    def __init__(self, source, parent_clean, parent_gap):
        self.source = source
        self.key, self.provider = source.key, source.provider
        self.labels, self.blocks = source.labels, source.blocks
        self.parent = {}
        self.contexts = {}
        for gap, value in ((False, parent_clean), (True, parent_gap)):
            probability = np.load(value, mmap_mode='r', allow_pickle=False) if isinstance(value, (str, Path)) else np.asarray(value)
            if probability.shape != (len(self.labels), 3) or probability.dtype != np.float64:
                raise ValueError('Parent cache must preserve float64(frame,3) probabilities')
            for start in range(0, len(probability), 4096):
                part = probability[start:start+4096]
                if not np.isfinite(part).all() or np.any(part < 0) or not np.allclose(part.sum(1), 1, atol=1e-8, rtol=0):
                    raise ValueError('Parent cache contains invalid probabilities')
            self.parent[gap] = probability
        validate_blocks(self.blocks, len(self.labels))

    def read(self, indices, augmented):
        return self.source.read(indices, augmented)

    def context(self, gap):
        if gap not in self.contexts:
            if hasattr(self.source, 'arrays') and 'core.npy' in self.source.arrays:
                core = self.source.arrays['gap_core.npy' if gap else 'core.npy']
                observed, age = core[:, 5], core[:, 8]
            else:
                observed, age = np.empty(len(self.labels)), np.empty(len(self.labels))
                for start in range(0, len(self.labels), 4096):
                    stop = min(len(self.labels), start+4096)
                    values = self.read(np.arange(start, stop), gap)
                    observed[start:stop], age[start:stop] = values[:, -4], values[:, -1]
            self.contexts[gap] = TemporalContext(self.parent[gap], observed, age, self.blocks)
        return self.contexts[gap]

    def temporal_window(self, start, gap):
        left = start+25
        return self.context(gap).window(left, left+CORE)

    def parent_window(self, start, gap):
        return np.asarray(self.parent[gap][start+25:start+25+CORE])
