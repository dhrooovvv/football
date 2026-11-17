"""Explicit all-five final artifact fit; never a substitute for LOMO evaluation."""
import os
import time
from pathlib import Path
import sys

import numpy as np
import torch
from torch import nn

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'tcn-pretrain-2026-11-11'),
                str(Path(__file__).resolve().parents[1] / 'tcn-expanded-2026-11-10')]
from pretrain_model import TCN, SEED, WINDOW, HALO, CORE, WIDTH
from expanded_data import valid_windows
from release_contract import check_membership, expected_identity, permitted_date, require

STAGE_STEPS, TOTAL_STEPS, BATCH, SAVE_EVERY = 20000, 40000, 8, 1000
VIEW_SEED = SEED + 424242


def validate_saved(saved, identity):
    require(saved['identity'] == identity, 'Final-fit checkpoint identity differs')
    step = saved['step']
    require(type(step) is int and 0 <= step <= TOTAL_STEPS and len(saved['losses']) == step
            and np.isfinite(saved['losses']).all(), 'Malformed final-fit progress/loss history')
    require(saved['stage'] == ('stage1' if step <= STAGE_STEPS else 'stage2'), 'Checkpoint stage differs')
    require(set(saved['coverage']) == {'stage1', 'stage2'}
            and set(saved['supervised_views']) == {'stage1', 'stage2'}
            and set(saved['stage_seconds']) == {'stage1', 'stage2'}, 'Checkpoint stage evidence differs')
    for stage, done in [('stage1', min(step, STAGE_STEPS)), ('stage2', max(0, step - STAGE_STEPS))]:
        counts = saved['coverage'][stage]
        views = saved['supervised_views'][stage]
        require(set(counts) == set(identity['training_matches'])
                and all(type(v) is int and v >= 0 for v in counts.values())
                and sum(counts.values()) == done * BATCH, 'Final-fit sampling coverage differs')
        require(set(views) == {'clean', 'gap'} and all(type(v) is int and v >= 0 for v in views.values())
                and sum(views.values()) == done * BATCH, 'Final-fit gap-view evidence differs')
        require(isinstance(saved['stage_seconds'][stage], (int, float))
                and np.isfinite(saved['stage_seconds'][stage]) and saved['stage_seconds'][stage] >= 0,
                'Final-fit timing evidence invalid')
    if step == TOTAL_STEPS:
        require(saved['coverage']['stage1'] == saved['coverage']['stage2']
                and saved['supervised_views']['stage1'] == saved['supervised_views']['stage2']
                and all(v > 0 for v in saved['coverage']['stage1'].values()),
                'Completed final-fit evidence disagrees with the stage sampler reset')
    if 'optimizer' in saved:
        groups = saved['optimizer']['param_groups']
        require(len(groups) == 1 and groups[0]['lr'] == .001 and groups[0]['weight_decay'] == 0,
                'Final-fit optimizer settings differ')


def train_final(cases, directory, signature, diagnostic):
    permitted_date(training=True)
    check_membership(cases)
    identity = expected_identity(signature, diagnostic)
    windows = valid_windows(cases, WINDOW)
    cumulative = np.cumsum([record[2] for record in windows])
    require(len(cumulative) > 0 and cumulative[-1] > 0, 'No eligible final-fit windows')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'progress.pt'
    torch.manual_seed(SEED)
    # Keep the registered unused head so initialization and Torch RNG match the winner.
    model = TCN().cpu()
    optimizer = torch.optim.Adam(model.parameters(), lr=.001)
    window_rng, view_rng = np.random.default_rng(SEED), np.random.default_rng(VIEW_SEED)
    coverage = {stage: {case.key: 0 for case in cases} for stage in ('stage1', 'stage2')}
    views = {stage: dict(clean=0, gap=0) for stage in ('stage1', 'stage2')}
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
        print('Resuming final fit at update', first_step, flush=True)
    model.train()
    for step in range(first_step, TOTAL_STEPS):
        started = time.monotonic()
        permitted_date(training=True)
        if step == STAGE_STEPS:
            optimizer = torch.optim.Adam(model.parameters(), lr=.001)
            window_rng, view_rng = np.random.default_rng(SEED), np.random.default_rng(VIEW_SEED)
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
                    and np.isfinite(values).all(), 'Final-fit encoded input schema differs')
            require(labels.shape == (CORE,) and (labels >= 0).all() and (labels <= 2).all(),
                    'Unknown final-fit central labels')
            batch_x.append(values)
            batch_y.append(labels)
            coverage[stage][case.key] += 1
            views[stage]['gap' if gap else 'clean'] += 1
        optimizer.zero_grad(set_to_none=True)
        logits = model(torch.from_numpy(np.stack(batch_x)))[:, HALO:HALO + CORE]
        loss = nn.functional.cross_entropy(logits.reshape(-1, 3),
                                           torch.from_numpy(np.stack(batch_y)).reshape(-1))
        require(bool(torch.isfinite(loss)), 'Nonfinite final-fit objective')
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.)
        optimizer.step()
        losses.append(float(loss.detach()))
        seconds[stage] += time.monotonic() - started
        if (step + 1) % SAVE_EVERY == 0:
            payload = dict(identity=identity, step=step + 1, stage=stage,
                           state=model.state_dict(), optimizer=optimizer.state_dict(),
                           window_rng=window_rng.bit_generator.state, view_rng=view_rng.bit_generator.state,
                           torch_rng=torch.get_rng_state(), losses=losses, coverage=coverage,
                           supervised_views=views, stage_seconds=seconds)
            temporary = path.with_suffix('.tmp')
            torch.save(payload, temporary)
            os.replace(temporary, path)
            print(f'Final fit {directory.name}: {step + 1}/{TOTAL_STEPS}', flush=True)
    require(all(v > 0 for counts in coverage.values() for v in counts.values()),
            'A final-fit stage never sampled one of the five training matches')
    model.eval()
    return model


def deep_equal(left, right):
    if isinstance(left, torch.Tensor):
        return isinstance(right, torch.Tensor) and torch.equal(left, right)
    if isinstance(left, np.ndarray):
        return isinstance(right, np.ndarray) and np.array_equal(left, right)
    if isinstance(left, dict):
        return isinstance(right, dict) and left.keys() == right.keys() and all(
            deep_equal(left[key], right[key]) for key in left)
    if isinstance(left, (list, tuple)):
        return type(left) is type(right) and len(left) == len(right) and all(
            deep_equal(a, b) for a, b in zip(left, right))
    return left == right


def confirm_final_repeat(first, repeat):
    require(first['step'] == repeat['step'] == TOTAL_STEPS, 'Incomplete repeated final fits')
    for key in ('identity', 'state', 'optimizer', 'window_rng', 'view_rng', 'torch_rng',
                'losses', 'coverage', 'supervised_views'):
        require(deep_equal(first[key], repeat[key]), 'Repeated final training differs: ' + key)
    # Measured wall-clock cost is evidence, not a deterministic training input.
