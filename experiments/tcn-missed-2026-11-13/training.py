"""Two bounded fold-safe trials; no target or final-all-match training API."""
from datetime import date, datetime
import math
import os
from pathlib import Path
import sys
import time
from zoneinfo import ZoneInfo

import numpy as np
import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tcn-parallel-2026-11-12'))
from parallel_model import model_for_arm, SCHEMA, WIDTH
from parallel_training import deep_equal
from objectives import WindowSampler, segment_soft_iou, WINDOW, HALO, CORE

IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
SEEDS = (20261106, 20261107)
STAGE_STEPS, TOTAL_STEPS, SAVE_EVERY, BATCH = 20000, 40000, 1000, 8
WINDOW_SEED, VIEW_SEED, SAMPLER_SEED = 20261106, 20685348, 20261106 + 515151
STAGES = ('stage1', 'stage2')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def research_open():
    require(datetime.now(ZoneInfo('Asia/Kolkata')).date() < date(2026, 11, 16),
            'Research frozen; preserve partial progress')


def expected_identity(signature, trial, seed, held_out, sampler):
    require(isinstance(signature, str) and bool(signature), 'Registration signature required')
    require(trial in ('a', 'b') and seed in SEEDS and held_out in IDS, 'Unregistered trial/seed/fold')
    require(sampler in ('uniform', 'short_mix') and (trial != 'a' or sampler == 'short_mix'),
            'Unregistered sampler for trial')
    return dict(registration=signature, trial=trial, held_out=held_out,
                training_matches=['idsse-' + m for m in IDS if m != held_out],
                total_steps=40000, stage_steps=20000, initialization_seed=seed,
                window_seed=WINDOW_SEED, view_seed=VIEW_SEED, sampler_seed=SAMPLER_SEED,
                sampler=sampler, architecture='original_motion_tcn_geometric_pretraining_head_v1',
                schema=SCHEMA, parameters=9701, window=250, halo=25, core=200, batch=8,
                optimizer='Adam', learning_rate=.001, gradient_clip=1.,
                supervised_gap_probability=.5, auxiliary_loss='segment_soft_iou' if trial == 'b' else 'none',
                auxiliary_coefficient=.1 if trial == 'b' else 0.,
                segment_flank=25, segment_epsilon=1e-6, short_spell_max_frames=50,
                stage_boundary='reset_Adam_and_all_supervised_RNGs')


def validate_saved(saved, identity):
    require(saved['identity'] == identity, 'Fold checkpoint identity differs')
    step = saved['step']
    require(type(step) is int and 0 <= step <= TOTAL_STEPS and len(saved['losses']) == step
            and all(math.isfinite(v) for v in saved['losses']), 'Invalid progress/loss history')
    require(saved['stage'] == ('stage1' if step <= STAGE_STEPS else 'stage2'), 'Wrong stage')
    require(set(saved['component_losses']) == {'cross_entropy', 'segment_soft_iou', 'segment_count'},
            'Incomplete component loss evidence')
    for key, values in saved['component_losses'].items():
        require(len(values) == step and all(math.isfinite(v) and v >= 0 for v in values),
                'Invalid component loss evidence: ' + key)
    require(all(type(v) is int for v in saved['component_losses']['segment_count']), 'Noninteger segment counts')
    if identity['trial'] == 'a':
        require(not any(saved['component_losses']['segment_count'])
                and not any(saved['component_losses']['segment_soft_iou']), 'Trial A has an auxiliary loss')
    require(set(saved['sampler_audit']) == set(identity['training_matches']), 'Sampler audit membership')
    for row in saved['sampler_audit'].values():
        require(set(row) == {'eligible_short_spells', 'excluded_short_spells'}
                and all(type(v) is int and v >= 0 for v in row.values()), 'Invalid sampler audit')
    for name in ('coverage', 'supervised_views', 'stage_seconds', 'exposure'):
        require(set(saved[name]) == set(STAGES), 'Incomplete stage evidence: ' + name)
    for stage, done in [('stage1', min(step, STAGE_STEPS)),
                        ('stage2', max(0, step - STAGE_STEPS))]:
        counts, views, exposure = saved['coverage'][stage], saved['supervised_views'][stage], saved['exposure'][stage]
        require(set(counts) == set(identity['training_matches'])
                and all(type(v) is int and v >= 0 for v in counts.values())
                and sum(counts.values()) == done * BATCH, 'Invalid match exposure')
        require(set(views) == {'clean', 'gap'} and all(type(v) is int and v >= 0 for v in views.values())
                and sum(views.values()) == done * BATCH, 'Invalid gap exposure')
        require(set(exposure) == {'uniform_windows', 'short_windows', 'complete_short_presentations', 'loss_segments'}
                and all(type(v) is int and v >= 0 for v in exposure.values())
                and exposure['uniform_windows'] + exposure['short_windows'] == done * BATCH,
                'Invalid short-spell exposure')
        require(exposure['complete_short_presentations'] >= exposure['short_windows'],
                'Targeted window does not contain a complete short spell')
        stage_slice = slice(0, min(step, STAGE_STEPS)) if stage == 'stage1' else slice(STAGE_STEPS, step)
        require(sum(saved['component_losses']['segment_count'][stage_slice]) == exposure['loss_segments'],
                'Segment loss coverage differs')
        if identity['sampler'] == 'uniform':
            require(exposure['short_windows'] == 0, 'Uniform sampler recorded targeted windows')
        require(math.isfinite(saved['stage_seconds'][stage]) and saved['stage_seconds'][stage] >= 0,
                'Invalid timing evidence')
    for key in ('window_rng', 'view_rng', 'sampler_rng', 'torch_rng', 'state', 'optimizer'):
        require(key in saved, 'Incomplete resume state: ' + key)
    if step == TOTAL_STEPS:
        for key in ('coverage', 'supervised_views', 'exposure'):
            require(saved[key]['stage1'] == saved[key]['stage2'], 'Reset sampling evidence differs: ' + key)
        require(all(v > 0 for v in saved['coverage']['stage1'].values()), 'Unvisited training match')


def confirm_repeat(first, repeat):
    require(first['step'] == repeat['step'] == TOTAL_STEPS, 'Incomplete repeat fits')
    for key in ('identity', 'step', 'stage', 'state', 'optimizer', 'window_rng', 'view_rng',
                'sampler_rng', 'torch_rng', 'losses', 'component_losses', 'coverage',
                'supervised_views', 'exposure', 'sampler_audit'):
        require(deep_equal(first[key], repeat[key]), 'Exact repeated training differs: ' + key)


def train_fit(cases, directory, signature, trial, seed, held_out, sampler, write_guard):
    research_open()
    identity = expected_identity(signature, trial, seed, held_out, sampler)
    require([case.key for case in cases] == identity['training_matches']
            and all(case.provider == 'idsse' for case in cases),
            'Exactly the ordered other-four IDSSE training cases required')
    sampling = WindowSampler(cases, sampler)
    directory = Path(directory)
    with write_guard():
        directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'progress.pt'
    torch.manual_seed(seed)
    model = model_for_arm('ensemble').cpu()
    optimizer = torch.optim.Adam(model.parameters(), lr=.001)
    window_rng, view_rng, sampler_rng = (np.random.default_rng(s) for s in (WINDOW_SEED, VIEW_SEED, SAMPLER_SEED))
    coverage = {s: dict.fromkeys(identity['training_matches'], 0) for s in STAGES}
    views = {s: dict(clean=0, gap=0) for s in STAGES}
    exposure = {s: dict(uniform_windows=0, short_windows=0, complete_short_presentations=0, loss_segments=0)
                for s in STAGES}
    seconds = dict.fromkeys(STAGES, 0.)
    losses, components, first_step = [], dict(cross_entropy=[], segment_soft_iou=[], segment_count=[]), 0
    if path.exists():
        saved = torch.load(path, map_location='cpu', weights_only=True)
        validate_saved(saved, identity)
        require(saved['sampler_audit'] == sampling.audit, 'Sampler support changed')
        first_step, losses, components = saved['step'], saved['losses'], saved['component_losses']
        coverage, views, exposure, seconds = (saved[k] for k in ('coverage', 'supervised_views', 'exposure', 'stage_seconds'))
        model.load_state_dict(saved['state'], strict=True)
        optimizer.load_state_dict(saved['optimizer'])
        window_rng.bit_generator.state = saved['window_rng']
        view_rng.bit_generator.state = saved['view_rng']
        sampler_rng.bit_generator.state = saved['sampler_rng']
        torch.set_rng_state(saved['torch_rng'])
        print(f'Resuming {trial}/{seed}/{held_out}/{directory.name}: {first_step}', flush=True)
    model.train()
    for step in range(first_step, TOTAL_STEPS):
        started = time.monotonic()
        research_open()
        if step == STAGE_STEPS:
            optimizer = torch.optim.Adam(model.parameters(), lr=.001)
            window_rng, view_rng, sampler_rng = (np.random.default_rng(s) for s in (WINDOW_SEED, VIEW_SEED, SAMPLER_SEED))
        stage = 'stage1' if step < STAGE_STEPS else 'stage2'
        batch_x, batch_y, supports = [], [], []
        for ci, start, branch in sampling.batch(window_rng, sampler_rng, BATCH):
            case = cases[ci]
            gap = bool(view_rng.random() < .5)
            values = case.read(np.arange(start, start + WINDOW), gap)
            y = np.asarray(case.labels[start + HALO:start + HALO + CORE], dtype=np.int64)
            require(values.shape == (WINDOW, WIDTH) and values.dtype == np.float32 and np.isfinite(values).all(),
                    'Encoded training schema differs')
            require(y.shape == (CORE,) and (y >= 0).all() and (y <= 2).all(), 'Unknown central label')
            batch_x.append(values); batch_y.append(y)
            supports.append(sampling.indices[ci].supports(start))
            coverage[stage][case.key] += 1
            views[stage]['gap' if gap else 'clean'] += 1
            exposure[stage][branch + '_windows'] += 1
            exposure[stage]['complete_short_presentations'] += sampling.short_exposure(ci, start)
        optimizer.zero_grad(set_to_none=True)
        logits = model(torch.from_numpy(np.stack(batch_x)))[:, HALO:HALO + CORE]
        ce = nn.functional.cross_entropy(logits.reshape(-1, 3), torch.from_numpy(np.stack(batch_y)).reshape(-1))
        auxiliary, count = segment_soft_iou(logits, supports) if trial == 'b' else (logits.sum() * 0., 0)
        loss = ce + .1 * auxiliary if trial == 'b' else ce
        require(bool(torch.isfinite(loss)), 'Nonfinite training loss')
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.)
        optimizer.step()
        losses.append(float(loss.detach()))
        components['cross_entropy'].append(float(ce.detach()))
        components['segment_soft_iou'].append(float(auxiliary.detach()))
        components['segment_count'].append(count)
        exposure[stage]['loss_segments'] += count
        seconds[stage] += time.monotonic() - started
        if (step + 1) % SAVE_EVERY == 0 or step + 1 in (STAGE_STEPS, TOTAL_STEPS):
            saved = dict(identity=identity, step=step + 1, stage=stage, state=model.state_dict(),
                         optimizer=optimizer.state_dict(), window_rng=window_rng.bit_generator.state,
                         view_rng=view_rng.bit_generator.state, sampler_rng=sampler_rng.bit_generator.state,
                         torch_rng=torch.get_rng_state(), losses=losses, component_losses=components,
                         coverage=coverage, supervised_views=views, exposure=exposure,
                         sampler_audit=sampling.audit, stage_seconds=seconds)
            validate_saved(saved, identity)
            with write_guard():
                temporary = path.with_suffix('.tmp')
                torch.save(saved, temporary)
                os.replace(temporary, path)
            print(f'{trial}/{seed}/{held_out}/{directory.name}: {step + 1}/{TOTAL_STEPS}', flush=True)
    validate_saved(saved, identity)
    model.eval()
    return model
