"""Same parent window/view draws and20k budget; new frame-wise set encoder."""
import os
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tcn-expanded-2026-11-10'))
from expanded_data import valid_windows
from set_model import (TCN, SEED, WINDOW, HALO, CORE, WIDTH, ARCHITECTURE, SCHEMA)

BATCH = 8
VIEW_SEED = SEED + 424242


def write_checkpoint(path, payload):
    path = Path(path)
    temporary = path.with_suffix('.tmp')
    torch.save(payload, temporary)
    os.replace(temporary, path)


def train_fit(cases, directory, signature, steps=20000, save_every=1000):
    if not cases or any(case.provider != 'idsse' for case in cases):
        raise ValueError('Set-TCN accepts IDSSE training cases only')
    if len({case.key for case in cases}) != len(cases):
        raise ValueError('Duplicate training case keys')
    if any(case.key.rsplit('-', 1)[-1] in {'J03WQQ', 'J03WR9'} for case in cases):
        raise ValueError('Sealed match forbidden in training')
    if not isinstance(steps, int) or steps <= 0 or not isinstance(save_every, int) or save_every <= 0:
        raise ValueError('Positive integer update/checkpoint budgets required')
    if not isinstance(signature, str) or not signature:
        raise ValueError('Source/input registration signature required')
    windows = valid_windows(cases, WINDOW)
    cumulative = np.cumsum([record[2] for record in windows])
    if not len(cumulative) or cumulative[-1] <= 0:
        raise ValueError('No eligible parent250-frame training windows')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'progress.pt'
    identity = dict(signature=signature, matches=[case.key for case in cases], steps=steps,
                    seed=SEED, view_seed=VIEW_SEED, architecture=ARCHITECTURE, schema=SCHEMA,
                    window=WINDOW, halo=HALO, core=CORE, batch=BATCH,
                    optimizer='Adam', learning_rate=.001, gradient_clip=1., gap_probability=.5)
    torch.manual_seed(SEED)
    rng = np.random.default_rng(SEED)
    view_rng = np.random.default_rng(VIEW_SEED)
    model = TCN().cpu()
    optimizer = torch.optim.Adam(model.parameters(), lr=.001)
    losses = []
    coverage = {case.key: {'clean': 0, 'gap': 0} for case in cases}
    first_step = 0
    if path.exists():
        saved = torch.load(path, map_location='cpu', weights_only=True)
        if saved['identity'] != identity:
            raise RuntimeError('Checkpoint training identity differs from this run')
        losses, coverage, first_step = saved['losses'], saved['coverage'], saved['step']
        if len(losses) != first_step or not 0 <= first_step <= steps:
            raise RuntimeError('Checkpoint step/loss mismatch')
        if set(coverage) != {case.key for case in cases}:
            raise RuntimeError('Checkpoint coverage membership mismatch')
        if any(set(v) != {'clean', 'gap'} or any(not isinstance(n, int) or n < 0 for n in v.values())
               for v in coverage.values()):
            raise RuntimeError('Malformed checkpoint coverage')
        if sum(sum(v.values()) for v in coverage.values()) != first_step * BATCH:
            raise RuntimeError('Checkpoint coverage/update mismatch')
        if not np.isfinite(losses).all():
            raise RuntimeError('Nonfinite saved training losses')
        model.load_state_dict(saved['state'], strict=True)
        optimizer.load_state_dict(saved['optimizer'])
        rng.bit_generator.state = saved['window_rng']
        view_rng.bit_generator.state = saved['view_rng']
        torch.set_rng_state(saved['torch_rng'])
        print(f'Resuming {directory} at update {first_step}', flush=True)
    model.train()
    for step in range(first_step, steps):
        batch_x, batch_y = [], []
        for draw in rng.integers(0, int(cumulative[-1]), size=BATCH):
            index = int(np.searchsorted(cumulative, draw, side='right'))
            case_index, first, _ = windows[index]
            start = first + int(draw - (cumulative[index - 1] if index else 0))
            case = cases[case_index]
            use_gap = bool(view_rng.random() < .5)
            values = case.read(np.arange(start, start + WINDOW), use_gap)
            labels = np.asarray(case.labels[start + HALO:start + HALO + CORE], dtype=np.int64)
            if values.shape != (WINDOW, WIDTH) or values.dtype != np.float32:
                raise RuntimeError('Training input shape/dtype differs from parent')
            if labels.shape != (CORE,) or (labels < 0).any() or (labels > 2).any():
                raise RuntimeError('Central parent loss labels must be completely known')
            batch_x.append(values)
            batch_y.append(labels)
            coverage[case.key]['gap' if use_gap else 'clean'] += 1
        optimizer.zero_grad(set_to_none=True)
        logits = model(torch.from_numpy(np.stack(batch_x)))[:, HALO:HALO + CORE]
        loss = nn.functional.cross_entropy(logits.reshape(-1, 3),
                                           torch.from_numpy(np.stack(batch_y)).reshape(-1))
        if not torch.isfinite(loss):
            raise RuntimeError('Nonfinite training loss')
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
            print(f'{directory.name}: update {step + 1}/{steps}, minibatch loss {losses[-1]:.5f}', flush=True)
    if steps >= 20000 and any(sum(counts.values()) == 0 for counts in coverage.values()):
        raise RuntimeError('A training match was never sampled')
    model.eval()
    return model, losses, coverage


def confirm_repeat(first, second, first_losses, second_losses, first_coverage, second_coverage):
    left, right = first.state_dict(), second.state_dict()
    equal = left.keys() == right.keys() and all(torch.equal(value, right[name]) for name, value in left.items())
    if not equal or first_losses != second_losses or first_coverage != second_coverage:
        raise RuntimeError('Repeated training differs')
