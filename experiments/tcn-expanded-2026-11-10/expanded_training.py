"""The frozen gap-trained TCN budget with compact inputs and resumable fits."""
import os
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

sys.path.insert(0, str(Path("experiments/tcn-2026-11-10").resolve()))
from tcn_candidate import TCN, SEED, WINDOW, HALO, CORE
from expanded_data import valid_windows


def write_checkpoint(path, payload):
    temporary = path.with_suffix(".tmp")
    torch.save(payload, temporary)
    os.replace(temporary, path)


def train_fit(cases, directory, signature, steps=20000, save_every=1000):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "progress.pt"
    identity = dict(signature=signature, matches=[case.key for case in cases], steps=steps, seed=SEED)
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
        losses = saved["losses"]
        coverage = saved["coverage"]
        first_step = saved["step"]
        if len(losses) != first_step or not 0 <= first_step <= steps:
            raise RuntimeError("Checkpoint step/loss mismatch")
        print(f"Resuming {directory} at update {first_step}", flush=True)
    windows = valid_windows(cases, WINDOW)
    cumulative = np.cumsum([record[2] for record in windows])
    model.train()
    for step in range(first_step, steps):
        batch_x, batch_y = [], []
        for draw in rng.integers(0, int(cumulative[-1]), size=8):
            record_index = int(np.searchsorted(cumulative, draw, side="right"))
            match_index, first, _ = windows[record_index]
            offset = int(draw - (cumulative[record_index - 1] if record_index else 0))
            start = first + offset
            case = cases[match_index]
            use_gap = bool(view_rng.random() < .5)
            batch_x.append(case.read(np.arange(start, start + WINDOW), use_gap))
            batch_y.append(np.asarray(case.labels[start + HALO:start + HALO + CORE], dtype=np.int64))
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
    if any(sum(counts.values()) == 0 for counts in coverage.values()):
        raise RuntimeError("A training match was never sampled")
    model.eval()
    return model, losses, coverage


def confirm_repeat(first, second, first_losses, second_losses, first_coverage, second_coverage):
    equal = all(torch.equal(value, second.state_dict()[name]) for name, value in first.state_dict().items())
    if not equal or first_losses != second_losses or first_coverage != second_coverage:
        raise RuntimeError("Repeated training differs")
