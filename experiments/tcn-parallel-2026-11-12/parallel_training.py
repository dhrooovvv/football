"""Fixed fold-safe supervised40k/reset fitting; no final-all-match entrypoint."""
from datetime import date, datetime
import os
from pathlib import Path
import sys
import time
from zoneinfo import ZoneInfo

import numpy as np
import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tcn-expanded-2026-11-10'))
from expanded_data import valid_windows
from parallel_model import (model_for_arm, INITIALIZATION_SEEDS, ARCHITECTURES,
                            PARAMETERS, SCHEMA, WINDOW, HALO, CORE, WIDTH)

IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
STAGE_STEPS, TOTAL_STEPS, SAVE_EVERY, BATCH = 20000, 40000, 1000, 8
WINDOW_SEED, VIEW_SEED = 20261106, 20685348


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def research_open():
    require(datetime.now(ZoneInfo('Asia/Kolkata')).date() < date(2026, 11, 16),
            'Research frozen; preserve partial progress')


def expected_identity(signature, arm, held_out):
    require(isinstance(signature, str) and bool(signature), 'Registration signature required')
    require(arm in INITIALIZATION_SEEDS and held_out in IDS, 'Unregistered arm or held-out match')
    return dict(registration=signature, arm=arm, held_out=held_out,
                training_matches=['idsse-' + match for match in IDS if match != held_out],
                geometry_matches=[], total_steps=40000, stage_steps=20000,
                initialization_seed=INITIALIZATION_SEEDS[arm], window_seed=WINDOW_SEED,
                view_seed=VIEW_SEED, architecture=ARCHITECTURES[arm], schema=SCHEMA,
                parameters=PARAMETERS[arm], window=250, halo=25, core=200, batch=8,
                optimizer='Adam', learning_rate=.001, gradient_clip=1.,
                supervised_gap_probability=.5,
                stage_boundary='reset_Adam_and_supervised_RNG_in_both_arms')


def validate_saved(saved, identity):
    require(saved['identity'] == identity, 'Fold checkpoint identity differs')
    step = saved['step']
    require(type(step) is int and 0 <= step <= TOTAL_STEPS and len(saved['losses']) == step
            and np.isfinite(saved['losses']).all(), 'Invalid progress/loss history')
    require(saved['stage'] == ('stage1' if step <= STAGE_STEPS else 'stage2'), 'Wrong checkpoint stage')
    for name in ('coverage', 'supervised_views', 'stage_seconds'):
        require(set(saved[name]) == {'stage1', 'stage2'}, 'Incomplete stage evidence')
    for stage, done in [('stage1', min(step, STAGE_STEPS)),
                        ('stage2', max(0, step - STAGE_STEPS))]:
        coverage, views = saved['coverage'][stage], saved['supervised_views'][stage]
        require(set(coverage) == set(identity['training_matches'])
                and all(type(v) is int and v >= 0 for v in coverage.values())
                and sum(coverage.values()) == done * BATCH, 'Invalid fold sampling evidence')
        require(set(views) == {'clean', 'gap'}
                and all(type(v) is int and v >= 0 for v in views.values())
                and sum(views.values()) == done * BATCH, 'Invalid gap-view evidence')
        require(isinstance(saved['stage_seconds'][stage], (int, float))
                and np.isfinite(saved['stage_seconds'][stage]) and saved['stage_seconds'][stage] >= 0,
                'Invalid stage timing evidence')
    if step == TOTAL_STEPS:
        require(saved['coverage']['stage1'] == saved['coverage']['stage2']
                and saved['supervised_views']['stage1'] == saved['supervised_views']['stage2']
                and all(v > 0 for v in saved['coverage']['stage1'].values()),
                'Completed fit disagrees with sampler reset')


def train_fit(cases, directory, signature, arm, held_out):
    research_open()
    identity = expected_identity(signature, arm, held_out)
    require([case.key for case in cases] == identity['training_matches']
            and all(case.provider == 'idsse' for case in cases),
            'Exactly the ordered other-four IDSSE cases required')
    windows = valid_windows(cases, WINDOW)
    cumulative = np.cumsum([row[2] for row in windows])
    require(len(cumulative) > 0 and cumulative[-1] > 0, 'No eligible supervised windows')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'progress.pt'
    torch.manual_seed(INITIALIZATION_SEEDS[arm])
    model = model_for_arm(arm).cpu()
    optimizer = torch.optim.Adam(model.parameters(), lr=.001)
    window_rng, view_rng = np.random.default_rng(WINDOW_SEED), np.random.default_rng(VIEW_SEED)
    coverage = {s: dict.fromkeys(identity['training_matches'], 0) for s in ('stage1', 'stage2')}
    views = {s: dict(clean=0, gap=0) for s in ('stage1', 'stage2')}
    seconds = dict(stage1=0., stage2=0.)
    losses, first_step = [], 0
    if path.exists():
        saved = torch.load(path, map_location='cpu', weights_only=True)
        validate_saved(saved, identity)
        first_step, losses, coverage = saved['step'], saved['losses'], saved['coverage']
        views, seconds = saved['supervised_views'], saved['stage_seconds']
        model.load_state_dict(saved['state'], strict=True)
        optimizer.load_state_dict(saved['optimizer'])
        window_rng.bit_generator.state = saved['window_rng']
        view_rng.bit_generator.state = saved['view_rng']
        torch.set_rng_state(saved['torch_rng'])
        print(f'Resuming {arm}/{held_out}/{directory.name}: {first_step}', flush=True)
    model.train()
    for step in range(first_step, TOTAL_STEPS):
        started = time.monotonic()
        if step % SAVE_EVERY == 0:
            research_open()
        if step == STAGE_STEPS:
            optimizer = torch.optim.Adam(model.parameters(), lr=.001)
            window_rng, view_rng = np.random.default_rng(WINDOW_SEED), np.random.default_rng(VIEW_SEED)
        stage = 'stage1' if step < STAGE_STEPS else 'stage2'
        batch_x, batch_y = [], []
        for draw in window_rng.integers(0, int(cumulative[-1]), size=BATCH):
            index = int(np.searchsorted(cumulative, draw, side='right'))
            case_index, first, _ = windows[index]
            start = first + int(draw - (cumulative[index - 1] if index else 0))
            case = cases[case_index]
            gap = bool(view_rng.random() < .5)
            values = case.read(np.arange(start, start + WINDOW), gap)
            labels = np.asarray(case.labels[start + HALO:start + HALO + CORE], dtype=np.int64)
            require(values.shape == (WINDOW, WIDTH) and values.dtype == np.float32
                    and np.isfinite(values).all(), 'Encoded training schema differs')
            require(labels.shape == (CORE,) and (labels >= 0).all() and (labels <= 2).all(),
                    'Unknown central supervised labels')
            batch_x.append(values)
            batch_y.append(labels)
            coverage[stage][case.key] += 1
            views[stage]['gap' if gap else 'clean'] += 1
        optimizer.zero_grad(set_to_none=True)
        logits = model(torch.from_numpy(np.stack(batch_x)))[:, HALO:HALO + CORE]
        loss = nn.functional.cross_entropy(logits.reshape(-1, 3),
                                           torch.from_numpy(np.stack(batch_y)).reshape(-1))
        require(bool(torch.isfinite(loss)), 'Nonfinite supervised loss')
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.)
        optimizer.step()
        losses.append(float(loss.detach()))
        seconds[stage] += time.monotonic() - started
        if (step + 1) % SAVE_EVERY == 0 or step + 1 in (STAGE_STEPS, TOTAL_STEPS):
            saved = dict(identity=identity, step=step + 1, stage=stage, state=model.state_dict(),
                         optimizer=optimizer.state_dict(), window_rng=window_rng.bit_generator.state,
                         view_rng=view_rng.bit_generator.state, torch_rng=torch.get_rng_state(),
                         losses=losses, coverage=coverage, supervised_views=views, stage_seconds=seconds)
            temporary = path.with_suffix('.tmp')
            torch.save(saved, temporary)
            os.replace(temporary, path)
            print(f'{arm}/{held_out}/{directory.name}: {step + 1}/{TOTAL_STEPS}', flush=True)
    validate_saved(saved, identity)
    model.eval()
    return model


def deep_equal(left, right):
    if isinstance(left, torch.Tensor):
        return isinstance(right, torch.Tensor) and torch.equal(left, right)
    if isinstance(left, np.ndarray):
        return isinstance(right, np.ndarray) and np.array_equal(left, right)
    if isinstance(left, dict):
        return isinstance(right, dict) and left.keys() == right.keys() and all(
            deep_equal(left[k], right[k]) for k in left)
    if isinstance(left, (list, tuple)):
        return type(left) is type(right) and len(left) == len(right) and all(
            deep_equal(a, b) for a, b in zip(left, right))
    return left == right


def confirm_repeat(first, repeat):
    require(first['step'] == repeat['step'] == TOTAL_STEPS, 'Incomplete repeated fold fits')
    for name in ('identity', 'state', 'optimizer', 'window_rng', 'view_rng', 'torch_rng',
                 'losses', 'coverage', 'supervised_views'):
        require(deep_equal(first[name], repeat[name]), 'Exact repeated training differs: ' + name)
