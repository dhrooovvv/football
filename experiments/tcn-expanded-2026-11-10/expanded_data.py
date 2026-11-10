"""Lossless, memory-mapped storage for the existing TCN representation."""
import json
from pathlib import Path

import numpy as np

SLOTS = 64
WIDTH = 521
FILES = ("objects.npy", "roles.npy", "core.npy", "gap_ball.npy", "gap_core.npy", "labels.npy")


def write_array(path, values):
    mapped = np.lib.format.open_memmap(path, mode="w+", dtype=values.dtype, shape=values.shape)
    mapped[:] = values
    mapped.flush()
    del mapped


def pack_case(directory, clean, augmented, labels, blocks, provenance):
    directory = Path(directory)
    frames = len(labels)
    if clean.shape != (frames, WIDTH) or augmented.shape != clean.shape:
        raise ValueError("Unexpected encoded feature shape")
    if not np.isfinite(clean).all() or not np.isfinite(augmented).all():
        raise ValueError("Encoded features must be finite")
    objects = clean[:, :512].reshape(frames, SLOTS, 8)
    gap_objects = augmented[:, :512].reshape(frames, SLOTS, 8)
    roles = objects[0, :, 5:8].copy()
    for start in range(0, frames, 2048):
        stop = min(frames, start + 2048)
        expected = np.broadcast_to(roles, (stop - start, SLOTS, 3))
        if not np.array_equal(objects[start:stop, :, 5:8], expected):
            raise ValueError("Team or ball roles changed within a match")
        if not np.array_equal(gap_objects[start:stop, :, 5:8], expected):
            raise ValueError("Augmentation changed roles")
        if not np.array_equal(objects[start:stop, :-1, :5], gap_objects[start:stop, :-1, :5]):
            raise ValueError("Ball-only augmentation changed player inputs")
    codes = np.array([{"H": 0, "A": 1, "D": 2, "X": -1}[str(value)] for value in labels], dtype=np.int8)
    arrays = {
        "objects.npy": objects[:, :, :5],
        "roles.npy": roles,
        "core.npy": clean[:, -9:],
        "gap_ball.npy": gap_objects[:, -1, :5],
        "gap_core.npy": augmented[:, -9:],
        "labels.npy": codes,
    }
    for name, array in arrays.items():
        write_array(directory / name, np.asarray(array))
    metadata = dict(provenance, frames=frames, blocks=[[int(a), int(b)] for a, b in blocks])
    (directory / "metadata.json").write_text(json.dumps(metadata, indent=2))
    case = CompactCase(directory)
    for start in range(0, frames, 4096):
        stop = min(frames, start + 4096)
        indices = np.arange(start, stop)
        if not np.array_equal(case.read(indices, False), clean[start:stop]):
            raise ValueError("Compact clean representation differs from original")
        if not np.array_equal(case.read(indices, True), augmented[start:stop]):
            raise ValueError("Compact augmented representation differs from original")


class CompactCase:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.metadata = json.loads((self.directory / "metadata.json").read_text())
        self.key = self.metadata["key"]
        self.provider = self.metadata["provider"]
        self.blocks = self.metadata["blocks"]
        self.arrays = {}
        for name in FILES:
            # Small labels/roles stay in RAM, avoiding hundreds of unnecessary open mappings.
            mapping = None if name in ("roles.npy", "labels.npy") else "r"
            self.arrays[name] = np.load(self.directory / name, mmap_mode=mapping, allow_pickle=False)
        self.labels = self.arrays["labels.npy"]
        frames = self.metadata["frames"]
        expected = {
            "objects.npy": (frames, SLOTS, 5), "roles.npy": (SLOTS, 3),
            "core.npy": (frames, 9), "gap_ball.npy": (frames, 5),
            "gap_core.npy": (frames, 9), "labels.npy": (frames,),
        }
        if any(self.arrays[name].shape != shape for name, shape in expected.items()):
            raise ValueError("Malformed compact case")

    def read(self, indices, augmented):
        indices = np.asarray(indices)
        objects = np.empty((len(indices), SLOTS, 8), dtype=np.float32)
        objects[:, :, :5] = self.arrays["objects.npy"][indices]
        objects[:, :, 5:8] = self.arrays["roles.npy"]
        core_name = "gap_core.npy" if augmented else "core.npy"
        if augmented:
            objects[:, -1, :5] = self.arrays["gap_ball.npy"][indices]
        return np.column_stack((objects.reshape(len(indices), 512), self.arrays[core_name][indices]))


def valid_windows(cases, window=250):
    records = []
    for index, case in enumerate(cases):
        count = 0
        for start, stop in case.blocks:
            known = case.labels[start:stop] >= 0
            edges = np.diff(np.r_[False, known, False].astype(np.int8))
            for left, right in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)):
                starts = int(right - left - window + 1)
                if starts > 0:
                    records.append((index, int(start + left), starts))
                    count += starts
        if count == 0:
            raise ValueError(f"No complete known-label training window in {case.key}")
    return records
