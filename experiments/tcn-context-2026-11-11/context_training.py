"""Same parent loss anchors and budget, with longer half-clipped input context."""
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

sys.path.insert(0, str(Path("experiments/tcn-expanded-2026-11-10").resolve()))
from expanded_data import valid_windows
from expanded_training import write_checkpoint, confirm_repeat
from context_model import (TCN, SEED, HALO, CORE, WINDOW, PARENT_HALO,
                           PARENT_WINDOW, ARCHITECTURE)


def training_windows(cases):
    """Preserve archived 250-frame valid-start support and order exactly."""
    windows = []
    for index, first, count in valid_windows(cases, PARENT_WINDOW):
        halves = [(int(a), int(b)) for a, b in cases[index].blocks
                  if a <= first and first + count - 1 + PARENT_WINDOW <= b]
        if len(halves) != 1:
            raise ValueError("Parent anchor support must belong to exactly one real half")
        start, stop = halves[0]
        windows.append((index, first, count, start, stop))
    return windows


def locate_draw(windows, cumulative, draw):
    if not 0 <= draw < cumulative[-1]:
        raise ValueError("Anchor draw outside valid support")
    index = int(np.searchsorted(cumulative, draw, side="right"))
    match, first, _, half_start, half_stop = windows[index]
    anchor = first + int(draw - (cumulative[index - 1] if index else 0))
    return match, anchor, half_start, half_stop


def context_indices(anchor, half_start, half_stop):
    if not half_start <= anchor or anchor + PARENT_WINDOW > half_stop:
        raise ValueError("Parent anchor crosses a real half")
    core_start = anchor + PARENT_HALO
    return np.clip(np.arange(core_start - HALO, core_start + CORE + HALO), half_start, half_stop - 1)


def train_fit(cases, directory, signature, steps=20000, save_every=1000):
    if not cases or any(case.provider != "idsse" for case in cases):
        raise ValueError("Context trial accepts IDSSE training cases only")
    if len({case.key for case in cases}) != len(cases):
        raise ValueError("Duplicate training case keys")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "progress.pt"
    identity = dict(signature=signature, matches=[case.key for case in cases], steps=steps,
                    seed=SEED, architecture=ARCHITECTURE, halo=HALO, window=WINDOW,
                    parent_anchor_window=PARENT_WINDOW, parent_anchor_halo=PARENT_HALO)
    windows = training_windows(cases)
    cumulative = np.cumsum([record[2] for record in windows])
    torch.manual_seed(SEED)
    rng = np.random.default_rng(SEED)
    view_rng = np.random.default_rng(SEED + 424242)
    model = TCN().cpu()
    optimizer = torch.optim.Adam(model.parameters(), lr=.001)
    losses = []
    coverage = {case.key: {"clean": 0, "gap": 0} for case in cases}
    first_step = 0
    if path.exists():
        saved = torch.load(path, map_location="cpu", weights_only=True)
        if saved["identity"] != identity:
            raise RuntimeError("Checkpoint training identity differs from this run")
        model.load_state_dict(saved["state"])
        optimizer.load_state_dict(saved["optimizer"])
        rng.bit_generator.state = saved["window_rng"]
        view_rng.bit_generator.state = saved["view_rng"]
        torch.set_rng_state(saved["torch_rng"])
        losses, coverage, first_step = saved["losses"], saved["coverage"], saved["step"]
        if len(losses) != first_step or not 0 <= first_step <= steps:
            raise RuntimeError("Checkpoint step/loss mismatch")
        print(f"Resuming {directory} at update {first_step}", flush=True)
    model.train()
    for step in range(first_step, steps):
        batch_x, batch_y = [], []
        for draw in rng.integers(0, int(cumulative[-1]), size=8):
            index, anchor, half_start, half_stop = locate_draw(windows, cumulative, draw)
            case = cases[index]
            use_gap = bool(view_rng.random() < .5)
            labels = np.asarray(case.labels[anchor + PARENT_HALO:anchor + PARENT_HALO + CORE], dtype=np.int64)
            if labels.shape != (CORE,) or (labels < 0).any() or (labels > 2).any():
                raise RuntimeError("Central parent loss labels are not completely known")
            batch_x.append(case.read(context_indices(anchor, half_start, half_stop), use_gap))
            batch_y.append(labels)
            coverage[case.key]["gap" if use_gap else "clean"] += 1
        optimizer.zero_grad(set_to_none=True)
        logits = model(torch.from_numpy(np.stack(batch_x)))[:, HALO:HALO + CORE]
        loss = nn.functional.cross_entropy(logits.reshape(-1, 3), torch.from_numpy(np.stack(batch_y)).reshape(-1))
        if not torch.isfinite(loss):
            raise RuntimeError("Nonfinite training loss")
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.)
        optimizer.step()
        losses.append(float(loss.detach()))
        if (step + 1) % save_every == 0 or step + 1 == steps:
            payload = dict(identity=identity, step=step + 1, state=model.state_dict(),
                           optimizer=optimizer.state_dict(), window_rng=rng.bit_generator.state,
                           view_rng=view_rng.bit_generator.state, torch_rng=torch.get_rng_state(),
                           losses=losses, coverage=coverage)
            write_checkpoint(path, payload)
            print(f"{directory.name}: update {step + 1}/{steps}, minibatch loss {losses[-1]:.5f}", flush=True)
    if steps >= 20000 and any(sum(counts.values()) == 0 for counts in coverage.values()):
        raise RuntimeError("A training match was never sampled")
    model.eval()
    return model, losses, coverage
