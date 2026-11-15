"""Registered 50k graph budget; frozen 40k checkpoints continue without reset."""
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'tcn-missed-2026-11-13'))
sys.path.insert(0, str(HERE.parent / 'tcn-parallel-2026-11-12'))
from objectives import WindowSampler, segment_soft_iou, WINDOW, HALO, CORE
from parallel_training import deep_equal
from hybrid_model import model_for_stage, corrected_logits, interpolate, ARCHITECTURES, PARAMETERS

IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
SEEDS = (20261106, 20261107)
STAGE_STEPS, TOTAL_STEPS, BATCH, SAVE_EVERY = 20000, 50000, 8, 1000
WINDOW_SEED, VIEW_SEED, SAMPLER_SEED = 20261106, 20685348, 20776257
STAGES = ('stage1', 'stage2')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def research_open():
    require(datetime.now(ZoneInfo('Asia/Kolkata')).date() < date(2026, 11, 16),
            'Research frozen at the beginning of November16; preserve partial evidence')


def expected_identity(signature, stage, seed, held_out, purpose='fold', steps=TOTAL_STEPS, probe=False):
    require(isinstance(signature, str) and bool(signature), 'Registration signature is required')
    require(stage in ARCHITECTURES and seed in SEEDS, 'Unregistered model or seed')
    require(type(steps) is int and (1 <= steps <= 1000 if probe else steps == TOTAL_STEPS),
            'Only a marked bounded probe may change the training budget')
    require(purpose in ('fold', 'final') and (held_out in IDS if purpose == 'fold' else held_out is None),
            'Fold/final membership identity is invalid')
    members = ['idsse-'+m for m in IDS if purpose == 'final' or m != held_out]
    return dict(registration=signature, stage=stage, held_out=held_out, purpose=purpose,
        probe=bool(probe), training_matches=members, total_steps=steps,
        initialization_seed=seed, stage_steps=STAGE_STEPS, batch=BATCH,
        architecture=ARCHITECTURES[stage], parameters=PARAMETERS[stage],
        input_schema='original_encoded521_core9_frozen_parent_float64_v1',
        window_seed=WINDOW_SEED, view_seed=VIEW_SEED, sampler_seed=SAMPLER_SEED,
        sampler='short_mix', parent_frozen=True, supervised_gap_probability=.5,
        central_frames=CORE, original_sampler_window=WINDOW, original_sampler_halo=HALO,
        optimizer='Adam', learning_rate=.001, gradient_clip=1.,
        auxiliary_loss='segment_soft_iou', auxiliary_coefficient=.1,
        segment_flank=25, segment_epsilon=1e-6,
        stage_boundary='reset_Adam_and_supervised_RNGs_at_20k')


def validate_saved(saved, identity):
    require(saved['identity'] == identity, 'Hybrid checkpoint identity changed')
    step = saved['step']
    require(type(step) is int and 0 < step <= identity['total_steps'], 'Invalid saved progress')
    require(saved['stage'] == ('stage1' if step <= STAGE_STEPS else 'stage2'), 'Wrong reset stage')
    require(len(saved['losses']) == step and all(math.isfinite(v) and v >= 0 for v in saved['losses']),
            'Invalid saved loss history')
    require(set(saved['component_losses']) == {'cross_entropy', 'segment_soft_iou', 'segment_count'},
            'Incomplete component losses')
    for name, values in saved['component_losses'].items():
        require(len(values) == step and all(math.isfinite(v) and v >= 0 for v in values),
                'Invalid component loss: '+name)
    require(all(type(v) is int for v in saved['component_losses']['segment_count']), 'Segment counts must be integers')
    require(set(saved['sampler_audit']) == set(identity['training_matches']), 'Sampler membership changed')
    for row in saved['sampler_audit'].values():
        require(set(row) == {'eligible_short_spells', 'excluded_short_spells'}
                and all(type(v) is int and v >= 0 for v in row.values()), 'Invalid sampler audit')
    for name in ('coverage', 'supervised_views', 'stage_seconds', 'exposure'):
        require(set(saved[name]) == set(STAGES), 'Missing reset-stage evidence')
    for stage, done in (('stage1', min(step, STAGE_STEPS)), ('stage2', max(0, step-STAGE_STEPS))):
        count, views, exposure = (saved[name][stage] for name in ('coverage', 'supervised_views', 'exposure'))
        require(set(count) == set(identity['training_matches'])
                and all(type(v) is int and v >= 0 for v in count.values())
                and sum(count.values()) == done*BATCH, 'Invalid match exposure')
        require(set(views) == {'clean', 'gap'} and all(type(v) is int and v >= 0 for v in views.values())
                and sum(views.values()) == done*BATCH, 'Invalid view exposure')
        require(set(exposure) == {'uniform_windows', 'short_windows', 'complete_short_presentations', 'loss_segments'}
                and all(type(v) is int and v >= 0 for v in exposure.values())
                and exposure['uniform_windows']+exposure['short_windows'] == done*BATCH,
                'Invalid short-spell exposure')
        require(exposure['complete_short_presentations'] >= exposure['short_windows'], 'Targeted spell is not contained')
        section = slice(0, min(step, STAGE_STEPS)) if stage == 'stage1' else slice(STAGE_STEPS, step)
        require(sum(saved['component_losses']['segment_count'][section]) == exposure['loss_segments'],
                'Segment exposure disagrees with component loss')
        require(math.isfinite(saved['stage_seconds'][stage]) and saved['stage_seconds'][stage] >= 0,
                'Invalid stage timing')
    for key in ('state', 'optimizer', 'window_rng', 'view_rng', 'sampler_rng', 'torch_rng'):
        require(key in saved, 'Missing resumable state: '+key)
    if step == 2*STAGE_STEPS and not identity['probe']:
        for name in ('coverage', 'supervised_views', 'exposure'):
            require(saved[name]['stage1'] == saved[name]['stage2'], 'Reset draw accounting differs')
        require(all(v > 0 for v in saved['coverage']['stage1'].values()), 'A training match was never sampled')


def confirm_repeat(first, repeat):
    require(first['identity'] == repeat['identity']
            and first['step'] == repeat['step'] == first['identity']['total_steps'], 'Incomplete exact repeat')
    for key in ('identity', 'step', 'stage', 'state', 'optimizer', 'window_rng', 'view_rng', 'sampler_rng',
                'torch_rng', 'losses', 'component_losses', 'coverage', 'supervised_views', 'exposure', 'sampler_audit'):
        require(deep_equal(first[key], repeat[key]), 'Repeated hybrid fitting differs: '+key)


def training_logits(model, cases, draws, gaps):
    parents, targets = [], []
    for (ci, start, _), gap in zip(draws, gaps):
        case = cases[ci]
        y = np.asarray(case.labels[start+HALO:start+HALO+CORE], dtype=np.int64)
        require(y.shape == (CORE,) and np.all((y >= 0) & (y <= 2)), 'Unknown central loss label')
        parents.append(case.parent_window(start, gap))
        targets.append(y)
    if model.stage == 'temporal':
        windows = [cases[ci].temporal_window(start, gap) for (ci, start, _), gap in zip(draws, gaps)]
        output = model(torch.from_numpy(np.stack([w[0] for w in windows])))
        correction = torch.stack([interpolate(output[i], w[1], w[2], w[3]) for i, w in enumerate(windows)])
    else:
        values = [cases[ci].read(np.arange(start, start+WINDOW), gap)
                  for (ci, start, _), gap in zip(draws, gaps)]
        require(all(v.shape == (WINDOW, 521) and v.dtype == np.float32 and np.isfinite(v).all() for v in values),
                'Malformed graph training window')
        correction = model(torch.from_numpy(np.stack(values)))[:, HALO:HALO+CORE]
    return corrected_logits(torch.from_numpy(np.stack(parents)), correction), torch.from_numpy(np.stack(targets))


def train_fit(cases, directory, signature, stage, seed, held_out, write_guard,
              steps=TOTAL_STEPS, probe=False, purpose='fold', stop_after=None,
              warm_start=None, source_identity=None):
    research_open()
    identity = expected_identity(signature, stage, seed, held_out, purpose, steps, probe)
    require([case.key for case in cases] == identity['training_matches']
            and all(case.provider == 'idsse' for case in cases), 'Hybrid fit membership differs')
    if stop_after is not None:
        require(type(stop_after) is int and 0 < stop_after <= steps and probe,
                'Only synthetic marked probes may stop at an explicit small step')
    limit = stop_after if stop_after is not None else steps
    sampling = WindowSampler(cases, 'short_mix')
    directory = Path(directory)
    with write_guard():
        directory.mkdir(parents=True, exist_ok=True)
    path = directory/'progress.pt'
    if not path.exists() and warm_start is not None:
        original = torch.load(warm_start, map_location='cpu', weights_only=True)
        adopted = adopt_warm_start(original, source_identity, identity)
        with write_guard():
            temporary = path.with_suffix('.tmp')
            torch.save(adopted, temporary)
            os.replace(temporary, path)
    torch.manual_seed(seed)
    model = model_for_stage(stage).cpu()
    optimizer = torch.optim.Adam(model.parameters(), lr=.001)
    window_rng, view_rng, sampler_rng = (np.random.default_rng(s) for s in (WINDOW_SEED, VIEW_SEED, SAMPLER_SEED))
    coverage = {s: dict.fromkeys(identity['training_matches'], 0) for s in STAGES}
    views = {s: dict(clean=0, gap=0) for s in STAGES}
    exposure = {s: dict(uniform_windows=0, short_windows=0, complete_short_presentations=0, loss_segments=0) for s in STAGES}
    seconds = dict.fromkeys(STAGES, 0.)
    losses, components = [], dict(cross_entropy=[], segment_soft_iou=[], segment_count=[])
    first_step = 0
    if path.exists():
        saved = torch.load(path, map_location='cpu', weights_only=True)
        validate_saved(saved, identity)
        require(saved['sampler_audit'] == sampling.audit, 'Sampler support changed')
        first_step, losses, components = saved['step'], saved['losses'], saved['component_losses']
        coverage, views, exposure, seconds = (saved[k] for k in ('coverage', 'supervised_views', 'exposure', 'stage_seconds'))
        model.load_state_dict(saved['state'], strict=True)
        optimizer.load_state_dict(saved['optimizer'])
        window_rng.bit_generator.state, view_rng.bit_generator.state = saved['window_rng'], saved['view_rng']
        sampler_rng.bit_generator.state = saved['sampler_rng']
        torch.set_rng_state(saved['torch_rng'])
        print('Resuming', stage, seed, held_out, first_step, flush=True)
    model.train()
    for step in range(first_step, limit):
        research_open()
        started = time.monotonic()
        if step == STAGE_STEPS:
            optimizer = torch.optim.Adam(model.parameters(), lr=.001)
            window_rng, view_rng, sampler_rng = (np.random.default_rng(s) for s in (WINDOW_SEED, VIEW_SEED, SAMPLER_SEED))
        reset_stage = 'stage1' if step < STAGE_STEPS else 'stage2'
        draws = sampling.batch(window_rng, sampler_rng, BATCH)
        gaps, supports = [], []
        for ci, start, branch in draws:
            case = cases[ci]
            gap = bool(view_rng.random() < .5)
            gaps.append(gap)
            supports.append(sampling.indices[ci].supports(start))
            coverage[reset_stage][case.key] += 1
            views[reset_stage]['gap' if gap else 'clean'] += 1
            exposure[reset_stage][branch+'_windows'] += 1
            exposure[reset_stage]['complete_short_presentations'] += sampling.short_exposure(ci, start)
        optimizer.zero_grad(set_to_none=True)
        logits, labels = training_logits(model, cases, draws, gaps)
        ce = nn.functional.cross_entropy(logits.reshape(-1, 3), labels.reshape(-1))
        auxiliary, count = segment_soft_iou(logits, supports)
        loss = ce+.1*auxiliary
        require(bool(torch.isfinite(loss)), 'Nonfinite hybrid loss')
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.)
        optimizer.step()
        losses.append(float(loss.detach()))
        components['cross_entropy'].append(float(ce.detach()))
        components['segment_soft_iou'].append(float(auxiliary.detach()))
        components['segment_count'].append(count)
        exposure[reset_stage]['loss_segments'] += count
        seconds[reset_stage] += time.monotonic()-started
        if (step+1) % SAVE_EVERY == 0 or step+1 in (STAGE_STEPS, steps, limit):
            saved = dict(identity=identity, step=step+1, stage=reset_stage,
                state=model.state_dict(), optimizer=optimizer.state_dict(),
                window_rng=window_rng.bit_generator.state, view_rng=view_rng.bit_generator.state,
                sampler_rng=sampler_rng.bit_generator.state, torch_rng=torch.get_rng_state(),
                losses=losses, component_losses=components, coverage=coverage, supervised_views=views,
                exposure=exposure, sampler_audit=sampling.audit, stage_seconds=seconds)
            validate_saved(saved, identity)
            with write_guard():
                temporary = path.with_suffix('.tmp')
                torch.save(saved, temporary)
                os.replace(temporary, path)
            print(stage, seed, held_out, directory.name, step+1, '/', steps, flush=True)
    if first_step >= limit:
        saved = torch.load(path, map_location='cpu', weights_only=True)
    validate_saved(saved, identity)
    model.eval()
    return model


def adopt_warm_start(saved, source_identity, identity):
    """Rebind only registered lineage/budget; preserve weights/Adam/RNG exactly."""
    from hybrid_training import validate_saved as validate_original
    require(source_identity is not None, 'Original source identity required')
    validate_original(saved, source_identity)
    require(saved['step'] == source_identity['total_steps'], 'Warm start must be complete')
    allowed = {'registration', 'total_steps'}
    require({k:v for k,v in source_identity.items() if k not in allowed}
            == {k:v for k,v in identity.items() if k not in allowed}, 'Warm start recipe differs')
    require(source_identity['total_steps'] < identity['total_steps'], 'Budget must increase')
    require(identity['stage'] == 'graph', 'Graph extension only')
    if not identity['probe']:
        require(source_identity['total_steps'] == 40000 and identity['total_steps'] == 50000,
                'Unregistered continuation budget')
    value = dict(saved, identity=identity)
    validate_saved(value, identity)
    return value
