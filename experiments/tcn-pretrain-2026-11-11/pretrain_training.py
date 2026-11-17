"""Two fixed stages: geometric pretraining or supervised control, then supervision."""
import os
import sys
import time
from pathlib import Path
from datetime import date, datetime
from zoneinfo import ZoneInfo

import numpy as np
import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tcn-expanded-2026-11-10'))
from expanded_data import valid_windows
from pretrain_data import eligible_starts, validate_membership
from pretrain_model import (TCN, SEED, WINDOW, HALO, CORE, WIDTH, ARCHITECTURE,
                            SCHEMA, reconstruction_loss)

BATCH = 8
VIEW_SEED = SEED + 424242
PRETEXT_SEED = SEED + 707070


def write_checkpoint(path, payload):
    temporary = Path(path).with_suffix('.tmp')
    torch.save(payload, temporary)
    os.replace(temporary, path)


def research_open():
    if datetime.now(ZoneInfo('Asia/Kolkata')).date() >= date(2026, 11, 16):
        raise RuntimeError('Research is frozen; preserve partial checkpoint evidence')


def train_fit(supervised_cases, geometry_cases, directory, signature, arm, held_out,
              stage_steps=20000, save_every=1000, allowed_pff=None):
    research_open()
    if arm not in ('control', 'pretrain'):
        raise ValueError('Expected fixed control or pretrain arm')
    if not isinstance(stage_steps, int) or stage_steps <= 0 \
            or not isinstance(save_every, int) or save_every <= 0:
        raise ValueError('Positive integer stage/checkpoint budgets required')
    if not isinstance(signature, str) or not signature:
        raise ValueError('Committed registration signature required')
    validate_membership(supervised_cases, geometry_cases, held_out, allowed_pff)
    if arm == 'pretrain' and not geometry_cases:
        raise ValueError('Pretraining requires exact fold-local geometry cases')
    if arm == 'control' and geometry_cases:
        raise ValueError('Control must not load/use additional geometry cases')
    windows = valid_windows(supervised_cases, WINDOW)
    cumulative = np.cumsum([record[2] for record in windows])
    if not len(cumulative) or cumulative[-1] <= 0:
        raise ValueError('No eligible supervised windows')
    starts = [eligible_starts(case) for case in geometry_cases]
    first_cases = geometry_cases if arm == 'pretrain' else supervised_cases
    total_steps = stage_steps * 2
    identity = dict(signature=signature, arm=arm, held_out=held_out,
                    supervised_matches=[case.key for case in supervised_cases],
                    geometry_matches=[case.key for case in geometry_cases],
                    allowed_pff=[str(v) for v in allowed_pff],
                    total_steps=total_steps, stage_steps=stage_steps,
                    architecture=ARCHITECTURE, schema=SCHEMA, seed=SEED,
                    pretext_seed=PRETEXT_SEED, view_seed=VIEW_SEED, window=WINDOW,
                    halo=HALO, core=CORE, batch=BATCH, optimizer='Adam', learning_rate=.001,
                    gradient_clip=1., supervised_gap_probability=.5,
                    stage_boundary='reset_Adam_and_supervised_RNG_in_both_arms',
                    pretext_target='clean_observed_cached_synthetic_hidden_ballXY',
                    pretext_loss='mean_squared_XY_error_over_valid_batch_frames',
                    pretext_sampler='uniform_match_then_uniform_eligible_start')
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'progress.pt'
    torch.manual_seed(SEED)
    model = TCN().cpu()
    optimizer = torch.optim.Adam(model.parameters(), lr=.001)
    window_rng = np.random.default_rng(SEED)
    view_rng = np.random.default_rng(VIEW_SEED)
    pretext_rng = np.random.default_rng(PRETEXT_SEED)
    losses = []
    coverage = {'stage1': {case.key: 0 for case in first_cases},
                'stage2': {case.key: 0 for case in supervised_cases}}
    target_counts = {'stage1': 0, 'stage2': 0}
    # Wall-clock measurements are evidence only, excluded from exact repeat checks.
    stage_seconds = {'stage1': 0.0, 'stage2': 0.0}
    supervised_views = {stage: {'clean': 0, 'gap': 0} for stage in ('stage1', 'stage2')}
    first_step = 0
    if path.exists():
        saved = torch.load(path, map_location='cpu', weights_only=True)
        if saved['identity'] != identity:
            raise RuntimeError('Checkpoint training identity differs')
        first_step = saved['step']; losses = saved['losses']
        if not isinstance(first_step, int) or not 0 <= first_step <= total_steps \
                or len(losses) != first_step or not np.isfinite(losses).all():
            raise RuntimeError('Malformed checkpoint step/loss history')
        expected_coverage = coverage
        coverage = saved['coverage']; target_counts = saved['target_counts']
        supervised_views = saved['supervised_views']
        stage_seconds = saved['stage_seconds']
        if set(stage_seconds) != {'stage1', 'stage2'} or any(
                not isinstance(v, (int, float)) or not np.isfinite(v) or v < 0
                for v in stage_seconds.values()):
            raise RuntimeError('Checkpoint stage timing evidence differs')
        if set(coverage) != {'stage1', 'stage2'} or set(target_counts) != {'stage1', 'stage2'}:
            raise RuntimeError('Checkpoint stage evidence differs')
        for stage, done in [('stage1', min(first_step, stage_steps)),
                            ('stage2', max(0, first_step - stage_steps))]:
            if set(coverage[stage]) != set(expected_coverage[stage]) \
                    or any(not isinstance(v, int) or v < 0 for v in coverage[stage].values()) \
                    or sum(coverage[stage].values()) != done * BATCH:
                raise RuntimeError('Checkpoint stage coverage differs')
        if set(supervised_views) != {'stage1', 'stage2'}:
            raise RuntimeError('Checkpoint supervised view stages differ')
        for stage, done in [('stage1', min(first_step, stage_steps)),
                            ('stage2', max(0, first_step - stage_steps))]:
            expected_draws = 0 if arm == 'pretrain' and stage == 'stage1' else done * BATCH
            if set(supervised_views[stage]) != {'clean', 'gap'} \
                    or any(not isinstance(v, int) or v < 0 for v in supervised_views[stage].values()) \
                    or sum(supervised_views[stage].values()) != expected_draws:
                raise RuntimeError('Checkpoint supervised view counts differ')
        if any(not isinstance(v, int) or v < 0 for v in target_counts.values()) \
                or target_counts['stage2'] != 0 \
                or (arm == 'control' and target_counts['stage1'] != 0):
            raise RuntimeError('Checkpoint target counts differ')
        if saved['stage'] != ('stage1' if first_step <= stage_steps else 'stage2'):
            raise RuntimeError('Checkpoint phase differs from step')
        model.load_state_dict(saved['state'], strict=True)
        optimizer.load_state_dict(saved['optimizer'])
        window_rng.bit_generator.state = saved['window_rng']
        view_rng.bit_generator.state = saved['view_rng']
        pretext_rng.bit_generator.state = saved['pretext_rng']
        torch.set_rng_state(saved['torch_rng'])
        print(f'Resuming {arm} {directory} at update {first_step}', flush=True)
    model.train()
    for step in range(first_step, total_steps):
        iteration_started = time.monotonic()
        if step % save_every == 0:
            research_open()
        if step == stage_steps:
            # Same stage transition in both arms; no optimizer-state advantage.
            optimizer = torch.optim.Adam(model.parameters(), lr=.001)
            window_rng = np.random.default_rng(SEED)
            view_rng = np.random.default_rng(VIEW_SEED)
        stage = 'stage1' if step < stage_steps else 'stage2'
        pretext = arm == 'pretrain' and stage == 'stage1'
        batch_x, batch_y, batch_valid = [], [], []
        if pretext:
            for _ in range(BATCH):
                index = int(pretext_rng.integers(len(geometry_cases)))
                case = geometry_cases[index]
                start = int(starts[index][int(pretext_rng.integers(len(starts[index])))])
                values = case.read(np.arange(start, start + WINDOW), augmented=True)
                target, valid = case.targets(np.arange(start + HALO, start + HALO + CORE))
                if target.shape != (CORE, 2) or valid.shape != (CORE,) or not valid.any():
                    raise RuntimeError('Invalid reconstruction target window')
                batch_x.append(values); batch_y.append(target); batch_valid.append(valid)
                coverage[stage][case.key] += 1
                target_counts[stage] += int(valid.sum())
        else:
            for draw in window_rng.integers(0, int(cumulative[-1]), size=BATCH):
                index = int(np.searchsorted(cumulative, draw, side='right'))
                case_index, first, _ = windows[index]
                start = first + int(draw - (cumulative[index - 1] if index else 0))
                case = supervised_cases[case_index]
                use_gap = bool(view_rng.random() < .5)
                values = case.read(np.arange(start, start + WINDOW), use_gap)
                supervised_views[stage]['gap' if use_gap else 'clean'] += 1
                labels = np.asarray(case.labels[start + HALO:start + HALO + CORE], dtype=np.int64)
                if labels.shape != (CORE,) or (labels < 0).any() or (labels > 2).any():
                    raise RuntimeError('Unknown central supervised labels')
                batch_x.append(values); batch_y.append(labels)
                coverage[stage][case.key] += 1
        if any(x.shape != (WINDOW, WIDTH) or x.dtype != np.float32
               or not np.isfinite(x).all() for x in batch_x):
            raise RuntimeError('Training input violates unchanged encoded schema')
        optimizer.zero_grad(set_to_none=True)
        tensor = torch.from_numpy(np.stack(batch_x))
        if pretext:
            prediction = model.forward_reconstruction(tensor)[:, HALO:HALO + CORE]
            loss = reconstruction_loss(prediction, torch.from_numpy(np.stack(batch_y)),
                                       torch.from_numpy(np.stack(batch_valid)))
        else:
            logits = model(tensor)[:, HALO:HALO + CORE]
            loss = nn.functional.cross_entropy(logits.reshape(-1, 3),
                                               torch.from_numpy(np.stack(batch_y)).reshape(-1))
        if not bool(torch.isfinite(loss)):
            raise RuntimeError('Nonfinite training objective')
        loss.backward(); nn.utils.clip_grad_norm_(model.parameters(), 1.); optimizer.step()
        losses.append(float(loss.detach()))
        stage_seconds[stage] += time.monotonic() - iteration_started
        if (step + 1) % save_every == 0 or step + 1 in (stage_steps, total_steps):
            write_checkpoint(path, dict(identity=identity, step=step + 1, stage=stage,
                state=model.state_dict(), optimizer=optimizer.state_dict(),
                window_rng=window_rng.bit_generator.state, view_rng=view_rng.bit_generator.state,
                pretext_rng=pretext_rng.bit_generator.state, torch_rng=torch.get_rng_state(),
                losses=losses, coverage=coverage, target_counts=target_counts,
                supervised_views=supervised_views, stage_seconds=stage_seconds))
            print(f'{arm} {directory.name}: update {step + 1}/{total_steps} {stage} loss {losses[-1]:.6f}', flush=True)
    if stage_steps >= 20000:
        if any(value == 0 for counts in coverage.values() for value in counts.values()):
            raise RuntimeError('A stage training match was never sampled')
        if arm == 'pretrain' and target_counts['stage1'] == 0:
            raise RuntimeError('No reconstruction targets sampled')
    model.eval()
    return model, losses, coverage


def confirm_repeat(first, second, first_losses, second_losses, first_coverage, second_coverage):
    left, right = first.state_dict(), second.state_dict()
    if left.keys() != right.keys() or not all(torch.equal(value, right[name]) for name, value in left.items()) \
            or first_losses != second_losses or first_coverage != second_coverage:
        raise RuntimeError('Repeated training differs')
