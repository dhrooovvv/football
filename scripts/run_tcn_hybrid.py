"""User-run sequential temporal and graph corrections over frozen Trial-B parents."""
import argparse
import hashlib
import io
import csv
from functools import lru_cache
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
            'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
PROJECT = Path(__file__).resolve().parents[1]
R = Path('experiments/tcn-hybrid-2026-11-14')
sys.path[:0] = [str(PROJECT / R), str(PROJECT / 'scripts')]
from hybrid_contract import (DATA, MODELS, MISSED, IDS, SEEDS, SETTINGS, STAGES,
    require, sha, load, save, registration, stage_binding, stage_signature,
    storage_guard, operation_lock, check_date, check_storage, gate_v2,
    committed_bytes, missed_signature, deadline_projection, artifact_projection)
import run_tcn_missed as frozen


@lru_cache(maxsize=1)
def dependencies():
    d = frozen.dependencies()
    sys.path.insert(0, str(PROJECT / R))
    import hybrid_model
    import hybrid_data
    import hybrid_training
    sys.path.insert(0, str(PROJECT / 'experiments/tcn-diagnostic-2026-11-13'))
    from diagnostics import analyze, paired_changes
    d.update(hybrid_model=hybrid_model, hybrid_data=hybrid_data,
             hybrid_training=hybrid_training, analyze=analyze, paired_changes=paired_changes)
    return d


def csv_digest(labels):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['frame', 'label'])
    writer.writerows(enumerate(labels.tolist()))
    return hashlib.sha256(stream.getvalue().encode()).hexdigest()


def fit_path(stage, held_out, seed, fit='first'):
    return MODELS / stage / held_out / str(seed) / fit / 'progress.pt'


def proof_path(stage, held_out, seed):
    return R / 'evaluation' / stage / 'fits' / f'{held_out}-{seed}.json'


def parent_rows(bound):
    directory = R / 'evaluation/temporal' if bound['temporal_selected'] else MISSED / 'evaluation/b'
    path = directory / 'results.json'
    require(sha(path) == bound['parent_results_sha256'], 'Retained parent results changed')
    return {(r['match'], r['condition']): r for r in load(path)}


def verify_fit(stage, held_out, seed, signature):
    path = proof_path(stage, held_out, seed)
    if not path.exists():
        return None
    proof = load(path)
    require(proof['stage'] == stage and proof['held_out'] == held_out and proof['seed'] == seed
            and proof['signature'] == signature and proof['exact_repeat'] is True
            and proof['steps'] == 40000 and proof['training_matches'] == ['idsse-' + m for m in IDS if m != held_out],
            'Hybrid fit evidence identity differs')
    expected = {str(fit_path(stage, held_out, seed, fit)) for fit in ('first', 'repeat')}
    require(set(proof['checkpoint_hashes']) == expected, 'Wrong hybrid checkpoint paths')
    for name, digest in proof['checkpoint_hashes'].items():
        require(sha(name) == digest, 'Hybrid checkpoint bytes changed')
    require(sha(proof['checks_path']) == proof['checks_sha256'], 'Hybrid checks log changed')
    return proof


def load_checkpoint(stage, held_out, seed, signature, d, fit='first'):
    require(verify_fit(stage, held_out, seed, signature), 'Missing repeated-fit proof')
    saved = d['torch'].load(fit_path(stage, held_out, seed, fit), map_location='cpu', weights_only=True)
    training = d['hybrid_training']
    training.validate_saved(saved, training.expected_identity(signature, stage, seed, held_out))
    model = d['hybrid_model'].model_for_stage(stage).cpu().eval()
    model.load_state_dict(saved['state'], strict=True)
    return model


def b_models(held_out, d):
    signature = missed_signature()
    bound, trial_signature = frozen.trial_identity('b', signature)
    for seed in SEEDS:
        require(frozen.verify_fit('b', held_out, seed, trial_signature, bound['sampler']), 'Missing original B fit')
    return [frozen.model_from(frozen.fit_path('b', held_out, seed, 'first'), d) for seed in SEEDS]


def ensemble_prediction(models, x, parent, blocks, d, batch=1, return_members=False):
    outputs = [d['hybrid_model'].predict(model, x, parent, blocks, batch=batch) for model in models]
    result = (parent.copy() if all(d['np'].array_equal(output, parent) for output in outputs)
              else d['average_views'](*outputs))
    return (result, outputs) if return_members else result


def parent_probabilities(stage, held_out, x, blocks, d, bound, b_members=None, temporal_members=None):
    members = b_members if b_members is not None else b_models(held_out, d)
    parent, _ = frozen.infer_ensemble(members, x, blocks, d, batch=1)
    if stage == 'graph' and bound['temporal_selected']:
        if temporal_members is None:
            _, temporal_signature = stage_signature('temporal', bound['registration'])
            temporal_members = [load_checkpoint('temporal', held_out, seed, temporal_signature, d) for seed in SEEDS]
        parent = ensemble_prediction(temporal_members, x, parent, blocks, d)
    return parent


def cache_paths(stage, held_out, key, view, role):
    require(stage in STAGES and held_out in IDS and role in ('training', 'evaluation'), 'Invalid cache role')
    require(key in IDS and view in ('clean', 'gap', 'targetlike'), 'Invalid cache membership/view')
    require(role != 'training' or key != held_out, 'Held-out match cannot enter a training cache')
    require(view in (('clean', 'gap') if role == 'training' else SETTINGS), 'Corruption view belongs to the wrong cache role')
    directory = DATA / stage / 'parents' / held_out / role
    return directory / f'{key}-{view}.npy', directory / f'{key}-{view}.json'


def probability_cache(stage, held_out, key, view, role, signature, bound, d,
                      x=None, blocks=None, b_members=None, temporal_members=None):
    path, metadata = cache_paths(stage, held_out, key, view, role)
    source = (Path('data/tcn-expanded') / ('idsse-' + key) / 'metadata.json' if role == 'training'
              else Path('data/tcn-prepared') / f'{key}-{view}.npz')
    identity = dict(signature=signature, binding=bound, stage=stage, held_out=held_out,
                    case=key, role=role, view=view, source_sha256=sha(source),
                    training_matches=['idsse-' + m for m in IDS if m != held_out])
    if metadata.exists():
        value = load(metadata)
        require(value['identity'] == identity and sha(path) == value['sha256'], 'Parent cache binding/bytes changed')
        return path, value
    require(not path.exists(), 'Unbound parent array exists; preserve and review incomplete evidence')
    np = d['np']
    if x is None:
        require(role == 'training', 'Evaluation cache requires explicit frozen case')
        case = d['CompactCase'](Path('data/tcn-expanded') / ('idsse-' + key))
        blocks = case.blocks
        x = case.read(np.arange(len(case.labels)), view == 'gap')
    started = time.monotonic()
    p = parent_probabilities(stage, held_out, x, blocks, d, bound, b_members, temporal_members)
    require(p.dtype == np.float64 and p.shape == (len(x), 3) and np.isfinite(p).all(), 'Parent probability schema')
    with storage_guard(reserve=max(64 * 1024 ** 2, int(p.nbytes) + 1024 ** 2)):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix('.npy.tmp')
        with temporary.open('wb') as handle:
            np.save(handle, p, allow_pickle=False)
        temporary.replace(path)
    value = dict(identity=identity, sha256=sha(path), shape=list(p.shape), dtype=str(p.dtype),
                 preparation_seconds=time.monotonic() - started, bytes=path.stat().st_size)
    save(metadata, value)
    return path, value


def prepare_cases(stage, held_out, signature, bound, d=None):
    d = d or dependencies()
    cases = []
    for key in IDS:
        if key == held_out:
            continue
        base = d['CompactCase'](Path('data/tcn-expanded') / ('idsse-' + key))
        paths = [probability_cache(stage, held_out, key, view, 'training', signature, bound, d)[0]
                 for view in ('clean', 'gap')]
        cases.append(d['hybrid_data'].HybridCase(base, *paths))
    return cases


def checks(stage):
    path = R / 'evaluation' / stage / f'checks-{time.time_ns()}.txt'
    with storage_guard():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as stream:
            env = os.environ.copy(); env['PYTHONPATH'] = 'src:scripts:' + str(R)
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(R / 'tests'), '-v'],
                                    stdout=stream, stderr=subprocess.STDOUT, env=env)
    require(result.returncode == 0, 'Hybrid checks failed; preserve ' + str(path))
    return path


def verify_original_b():
    bound, signature = frozen.trial_identity('b', missed_signature())
    return frozen.verify_completed('b', signature, bound)


def zero_model(stage, d):
    return d['hybrid_model'].model_for_stage(stage).cpu().eval()


def preflight(stage, signature, bound, workers):
    check_date()
    checks_path = checks(stage)
    verify_original_b()
    d = dependencies(); np = d['np']
    started = time.monotonic(); rows = parent_rows(bound)
    timings, caches, zero_proofs = [], {}, []
    evaluation_frames = 0
    for held_out in IDS:
        b_members = b_models(held_out, d)
        temporal_members = None
        if bound['temporal_selected']:
            _, ts = stage_signature('temporal', bound['registration'])
            temporal_members = [load_checkpoint('temporal', held_out, s, ts, d) for s in SEEDS]
        for key in IDS:
            if key == held_out:
                continue
            for view in ('clean', 'gap'):
                path, value = probability_cache(stage, held_out, key, view, 'training', signature, bound, d,
                    b_members=b_members, temporal_members=temporal_members)
                caches[str(path)] = value['sha256']
        for condition in SETTINGS:
            with np.load(f'data/tcn-prepared/{held_out}-{condition}.npz', allow_pickle=False) as data:
                x, y, blocks = data['x'], data['y'], data['blocks'].tolist()
            path, value = probability_cache(stage, held_out, held_out, condition, 'evaluation', signature, bound, d,
                x=x, blocks=blocks, b_members=b_members, temporal_members=temporal_members)
            caches[str(path)] = value['sha256']
            parent = np.load(path, mmap_mode='r', allow_pickle=False)
            pred = d['decode'](parent, (1 - np.eye(3)) * 16, blocks)
            expected = rows[held_out, condition]
            require(csv_digest(pred) == expected['csv_sha256'] and d['metrics'](y, pred, blocks, d['score'], d['official'], np)
                    == expected['candidate'], 'Archived retained parent CSV/metric reproduction failed')
            output = d['hybrid_model'].predict(zero_model(stage, d), x, parent, blocks, batch=1)
            require(np.allclose(output, parent, atol=1e-12, rtol=0)
                    and csv_digest(d['decode'](output, (1 - np.eye(3)) * 16, blocks)) == expected['csv_sha256'],
                    'Zero correction fails original parent reproduction')
            pair = ensemble_prediction([zero_model(stage, d), zero_model(stage, d)], x, parent, blocks, d)
            require(np.array_equal(pair, parent) and csv_digest(d['decode'](pair, (1 - np.eye(3)) * 16, blocks))
                    == expected['csv_sha256'], 'Zero-correction ensemble fails parent reproduction')
            zero_proofs.append(dict(match=held_out, condition=condition, csv_sha256=expected['csv_sha256']))
            evaluation_frames += len(y)
            del x, parent
        cases = prepare_cases(stage, held_out, signature, bound, d)
        probe_dir = MODELS / stage / 'preflight' / held_out / str(time.time_ns())
        before = time.monotonic()
        d['hybrid_training'].train_fit(cases, probe_dir, signature, stage, SEEDS[0], held_out,
                                       storage_guard, steps=64, probe=True)
        timings.append((time.monotonic() - before) / 64)
        del cases, b_members, temporal_members
        print('Preflight measured', stage, held_out, flush=True)
    elapsed = time.monotonic() - started
    # Full evaluation repeats three passes versus one zero pass, with reload/scoring overhead.
    projection = deadline_projection(max(timings), elapsed * 3, workers,
                                      included_branches=2 if bound['temporal_selected'] else 1)
    disk_projection = artifact_projection(evaluation_frames, 2 if bound['temporal_selected'] else 1)
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = int(rss if sys.platform == 'darwin' else rss * 1024)
    value = dict(completed=True, stage=stage, signature=signature, binding=bound,
        checks_path=str(checks_path), checks_sha256=sha(checks_path), probe_steps_per_fold=64,
        seconds_per_update_by_fold=dict(zip(IDS, timings)), maximum_seconds_per_update=max(timings),
        preparation_and_probe_seconds=elapsed, peak_process_rss_bytes=rss_bytes,
        projected_parallel_peak_rss_bytes=rss_bytes * workers,
        projection=projection, caches=caches, zero_correction_proofs=zero_proofs,
        storage=check_storage(), artifact_projection=disk_projection,
        evaluation_frames=evaluation_frames, preparation_work_is_measured=True,
        complete_comparison_work_is_estimated=True, no_probe_quality_scores=True,
        production_changed=False, target_accuracy='unknown')
    save(R / 'preflight' / stage / 'report.json', value)
    print('Preflight complete. Projected finish before freeze:', projection['projected_to_finish'], flush=True)


def verify_preflight(stage, signature, bound, workers):
    path = R / 'preflight' / stage / 'report.json'
    require(path.is_file(), 'Run and review this stage preflight first')
    value = load(path)
    require(value['completed'] and value['signature'] == signature and value['binding'] == bound,
            'Preflight source/parent differs')
    require(sha(value['checks_path']) == value['checks_sha256'], 'Preflight checks changed')
    for p, digest in value['caches'].items():
        require(sha(p) == digest, 'Prepared parent cache changed')
    projection = deadline_projection(value['maximum_seconds_per_update'],
        value['preparation_and_probe_seconds'] * 3, workers, 2 if bound['temporal_selected'] else 1)
    require(projection['projected_to_finish'], 'Measured projection no longer fits before November16 freeze')
    disk_projection = artifact_projection(value['evaluation_frames'], 2 if bound['temporal_selected'] else 1)
    require(disk_projection['within_budget'], 'Projected fit/evaluation artifacts exceed the storage constraints')
    return value


def worker(stage, seed, signature, bound, checks_path):
    d = dependencies(); training = d['hybrid_training']; torch = d['torch']
    require(checks_path.is_file() and checks_path.parent == R / 'evaluation' / stage
            and checks_path.name.startswith('checks-'), 'Missing registered hybrid checks path')
    checks_text = checks_path.read_text()
    require('\nOK\n' in checks_text and 'FAILED (' not in checks_text, 'Missing passing hybrid checks')
    for held_out in IDS:
        check_date()
        if verify_fit(stage, held_out, seed, signature):
            continue
        cases = prepare_cases(stage, held_out, signature, bound, d)
        started = time.monotonic()
        for fit in ('first', 'repeat'):
            training.train_fit(cases, fit_path(stage, held_out, seed, fit).parent,
                               signature, stage, seed, held_out, storage_guard)
        saved = [torch.load(fit_path(stage, held_out, seed, fit), map_location='cpu', weights_only=True)
                 for fit in ('first', 'repeat')]
        identity = training.expected_identity(signature, stage, seed, held_out)
        for value in saved:
            training.validate_saved(value, identity)
        training.confirm_repeat(*saved)
        value = saved[0]
        proof = dict(stage=stage, seed=seed, held_out=held_out, signature=signature,
            binding=bound, training_matches=identity['training_matches'], steps=40000,
            exact_repeat=True, checks_path=str(checks_path), checks_sha256=sha(checks_path),
            checkpoint_hashes={str(fit_path(stage, held_out, seed, fit)): sha(fit_path(stage, held_out, seed, fit))
                               for fit in ('first', 'repeat')}, seconds=time.monotonic() - started,
            training_loss_sha256=hashlib.sha256(json.dumps(value['losses']).encode()).hexdigest(),
            component_loss_sha256=hashlib.sha256(json.dumps(value['component_losses']).encode()).hexdigest(),
            coverage=value['coverage'], supervised_views=value['supervised_views'], exposure=value['exposure'])
        save(proof_path(stage, held_out, seed), proof)
        verify_fit(stage, held_out, seed, signature)
        print('Completed repeated fit', stage, held_out, seed, flush=True)
        del cases, saved


def evaluate(stage, signature, bound, d=None):
    d = d or dependencies(); np = d['np']; rows = []; paired = []
    archive = parent_rows(bound)
    for held_out in IDS:
        check_date()
        members = [load_checkpoint(stage, held_out, seed, signature, d) for seed in SEEDS]
        records = {}; previous_y = None; previous_blocks = None
        for condition in SETTINGS:
            with np.load(f'data/tcn-prepared/{held_out}-{condition}.npz', allow_pickle=False) as data:
                x, y, blocks = data['x'], data['y'], data['blocks'].tolist()
            if previous_y is not None:
                require(np.array_equal(y, previous_y) and blocks == previous_blocks, 'Corruption altered labels/halves')
            previous_y, previous_blocks = y.copy(), blocks
            path, _ = probability_cache(stage, held_out, held_out, condition, 'evaluation', signature, bound, d,
                                          x=x, blocks=blocks)
            parent = np.load(path, mmap_mode='r', allow_pickle=False)
            parent_pred = d['decode'](parent, (1 - np.eye(3)) * 16, blocks)
            old = archive[held_out, condition]
            require(csv_digest(parent_pred) == old['csv_sha256']
                    and d['metrics'](y, parent_pred, blocks, d['score'], d['official'], np) == old['candidate'],
                    'Retained parent no longer reproduces archive')
            fresh = [load_checkpoint(stage, held_out, seed, signature, d) for seed in SEEDS]
            probabilities, member_probs = ensemble_prediction(members, x, parent, blocks, d, return_members=True)
            repeat_prob, repeat_members = ensemble_prediction(fresh, x, parent, blocks, d, return_members=True)
            batch_prob = ensemble_prediction(members, x, parent, blocks, d, batch=4)
            require(np.array_equal(probabilities, repeat_prob)
                    and all(np.array_equal(a, b) for a, b in zip(member_probs, repeat_members)),
                    'Reloaded hybrid probabilities differ')
            predictions = [d['decode'](p, (1 - np.eye(3)) * 16, blocks)
                           for p in (probabilities, repeat_prob, batch_prob)]
            paths = [DATA / stage / 'predictions' / f'{held_out}-{condition}-{tag}.csv'
                     for tag in ('first', 'reload', 'batch4')]
            for csv_path, labels in zip(paths, predictions):
                with storage_guard():
                    csv_path.parent.mkdir(parents=True, exist_ok=True)
                    d['export_labels'](csv_path, labels, len(y))
            require(len({sha(p) for p in paths}) == 1, 'Hybrid batch/reload CSV bytes differ')
            analysis, records[condition] = d['analyze'](y, predictions[0], x[:, -4] == 0, probabilities, blocks, d['official'])
            measured = d['metrics'](y, predictions[0], blocks, d['score'], d['official'], np)
            require(analysis['per_iou'] == measured['spell_per_iou'], 'Official and diagnostic spell scores differ')
            rows.append(dict(match=held_out, condition=condition, parent=old['candidate'], candidate=measured,
                analysis=analysis, parent_missing_ball=d['missing'](y, parent_pred, x[:, -4] == 0),
                candidate_missing_ball=d['missing'](y, predictions[0], x[:, -4] == 0),
                csv_paths=[str(p) for p in paths], csv_sha256=sha(paths[0]), parent_csv_sha256=old['csv_sha256'],
                reload_probabilities_equal=True, csv_bytes_equal_reload_batch4=True))
            save(R / 'evaluation' / stage / 'results-partial.json', rows)
            print('Evaluated hybrid', stage, held_out, condition, flush=True)
        paired.append(dict(match=held_out, per_iou=d['paired_changes'](records['clean'], records['targetlike'])))
    before = [dict(match=r['match'], condition=r['condition'], **r['parent']) for r in rows]
    after = [dict(match=r['match'], condition=r['condition'], **r['candidate']) for r in rows]
    gate = gate_v2(before, after)
    directory = R / 'evaluation' / stage
    save(directory / 'results.json', rows); save(directory / 'gate-v2.json', gate)
    save(directory / 'paired-corruption.json', paired)
    report = '# Hybrid ' + stage + '\n\n|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|\n|---|---|---:|---:|---:|---:|\n'
    for row in rows:
        report += f"|{row['match']}|{row['condition']}|{row['parent']['spellF1']:.6f}|{row['candidate']['spellF1']:.6f}|{row['parent']['macroF1']:.6f}|{row['candidate']['macroF1']:.6f}|\n"
    report += '\nGate\n\n'+json.dumps(gate, indent=2)+'\n\nReused development evidence. Target accuracy unknown. Review before the next stage.\n'
    with storage_guard():
        (directory / 'report.md').write_text(report)
    save(directory / 'completion.json', dict(completed=True, stage=stage, signature=signature,
        binding=bound, results_sha256=sha(directory / 'results.json'), gate_sha256=sha(directory / 'gate-v2.json'),
        paired_sha256=sha(directory / 'paired-corruption.json'), report_sha256=sha(directory / 'report.md'),
        fit_proofs={str(proof_path(stage, m, s)): sha(proof_path(stage, m, s)) for m in IDS for s in SEEDS},
        case_count=10, contracts_passed=True, repeated_training_exact=True,
        production_changed=False, sealed_opened=False, target_accuracy='unknown'))


def verify_completed(stage, signature, bound):
    directory = R / 'evaluation' / stage
    done = load(directory / 'completion.json')
    require(done['completed'] and done['stage'] == stage and done['signature'] == signature and done['binding'] == bound
            and done['case_count'] == 10 and done['contracts_passed'] and done['repeated_training_exact'],
            'Hybrid completion identity differs')
    for key, filename in (('results_sha256', 'results.json'), ('gate_sha256', 'gate-v2.json'),
                          ('paired_sha256', 'paired-corruption.json'), ('report_sha256', 'report.md')):
        require(sha(directory / filename) == done[key], 'Hybrid completion bytes differ')
    expected_proofs = {str(proof_path(stage, m, s)) for m in IDS for s in SEEDS}
    require(set(done['fit_proofs']) == expected_proofs, 'Incomplete hybrid fit proofs')
    for path, digest in done['fit_proofs'].items():
        require(sha(path) == digest, 'Hybrid fit proof changed')
    for match in IDS:
        for seed in SEEDS:
            require(verify_fit(stage, match, seed, signature), 'Missing hybrid fit')
    rows = load(directory / 'results.json'); parent = parent_rows(bound)
    require(len(rows) == 10 and {(r['match'], r['condition']) for r in rows} == set(parent), 'Incomplete hybrid cells')
    for row in rows:
        old = parent[row['match'], row['condition']]
        require(row['parent'] == old['candidate'] and row['parent_csv_sha256'] == old['csv_sha256']
                and row['reload_probabilities_equal'] and row['csv_bytes_equal_reload_batch4'], 'Hybrid parent/equality evidence differs')
        for path in row['csv_paths']:
            require(sha(path) == row['csv_sha256'], 'Hybrid prediction changed')
    gate = gate_v2([dict(match=r['match'], condition=r['condition'], **r['parent']) for r in rows],
                   [dict(match=r['match'], condition=r['condition'], **r['candidate']) for r in rows])
    require(gate == load(directory / 'gate-v2.json'), 'Hybrid gate disagrees with saved scores')
    return done, rows, gate


def review(stage, base_signature):
    bound, signature = stage_signature(stage, base_signature)
    done, _, gate = verify_completed(stage, signature, bound)
    directory = R / 'evaluation' / stage
    paths = {name: digest for proof in done['fit_proofs'] for name, digest in load(proof)['checkpoint_hashes'].items()}
    value = dict(stage=stage, registration=base_signature, review_completed=True,
        accepted=gate['quality_eligible'], parent_binding=bound,
        completion_sha256=sha(directory / 'completion.json'), results_sha256=done['results_sha256'],
        gate_sha256=done['gate_sha256'], checkpoint_hashes=paths,
        instruction='Review saved evidence and commit this record before a dependent stage or release.')
    path = R / ('reviewed-' + stage + '.json')
    if path.exists():
        require(load(path) == value, 'Existing reviewed decision differs; preserve it')
    else:
        save(path, value)
    print('Review record prepared for human review and git commit:', path, flush=True)
    return value


def validated_review(stage, base_signature, require_committed=True):
    path = R / ('reviewed-' + stage + '.json')
    require(path.is_file(), 'Missing explicit reviewed hybrid decision')
    if require_committed:
        committed_bytes(path)
    value = load(path)
    bound, signature = stage_signature(stage, base_signature)
    done, _, gate = verify_completed(stage, signature, bound)
    require(value['stage'] == stage and value['registration'] == base_signature and value['review_completed']
            and value['accepted'] is gate['quality_eligible'] and value['parent_binding'] == bound
            and value['completion_sha256'] == sha(R / 'evaluation' / stage / 'completion.json')
            and value['results_sha256'] == done['results_sha256'] and value['gate_sha256'] == done['gate_sha256'],
            'Reviewed hybrid decision changed')
    expected = {p: h for proof in done['fit_proofs'] for p, h in load(proof)['checkpoint_hashes'].items()}
    require(value['checkpoint_hashes'] == expected, 'Reviewed checkpoint set differs')
    return value


def run(stage, base_signature, workers):
    bound, signature = stage_signature(stage, base_signature)
    if stage == 'graph':
        validated_review('temporal', base_signature)
    if (R / 'evaluation' / stage / 'completion.json').exists():
        verify_completed(stage, signature, bound)
        print('Stage already completed. Preserve and report for review.', flush=True)
        return
    pre = verify_preflight(stage, signature, bound, workers)
    check = checks(stage)
    pending, active = list(SEEDS), []
    try:
        while pending or active:
            check_date()
            while pending and len(active) < workers:
                seed = pending.pop(0)
                path = R / 'evaluation' / stage / f'worker-{seed}-{time.time_ns()}.txt'
                with storage_guard():
                    handle = path.open('w')
                command = [sys.executable, 'scripts/run_tcn_hybrid.py', '--stage', stage,
                           '--worker', str(seed), '--checks-file', str(check), '--run']
                child = subprocess.Popen(command, stdout=handle, stderr=subprocess.STDOUT)
                active.append((child, handle, seed))
                print('Started hybrid seed', seed, 'log:', path, flush=True)
            for item in list(active):
                child, handle, seed = item
                if child.poll() is not None:
                    handle.close(); active.remove(item)
                    require(child.returncode == 0, 'Hybrid worker failed; preserve seed ' + str(seed))
            if active:
                time.sleep(1)
    finally:
        for child, handle, _ in active:
            if child.poll() is None:
                child.terminate()
            child.wait(); handle.close()
    evaluate(stage, signature, bound)
    registration(); verify_completed(stage, signature, bound)
    print('Hybrid stage complete. Stop and report done for review.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=STAGES, required=True)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--preflight', action='store_true')
    actions.add_argument('--run', action='store_true')
    actions.add_argument('--review', action='store_true')
    parser.add_argument('--workers', type=int, choices=(1, 2), default=2)
    parser.add_argument('--worker', type=int, choices=SEEDS, help=argparse.SUPPRESS)
    parser.add_argument('--checks-file', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    os.chdir(PROJECT)
    _, _, base_signature = registration()
    bound, signature = stage_signature(args.stage, base_signature)
    with operation_lock(args.stage, args.worker):
        if args.worker is not None:
            require(args.run and args.checks_file is not None, 'Internal worker requires explicit checks')
            worker(args.stage, args.worker, signature, bound, args.checks_file)
        elif args.preflight:
            if args.stage == 'graph':
                validated_review('temporal', base_signature)
            preflight(args.stage, signature, bound, args.workers)
        elif args.review:
            review(args.stage, base_signature)
        else:
            run(args.stage, base_signature, args.workers)


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        os.chdir(PROJECT)
        try:
            save(R / 'failures' / f'{time.time_ns()}.json', dict(error_type=type(error).__name__,
                 message=str(error), production_changed=False, target_accuracy='unknown'))
        except Exception:
            print('Could not save failure evidence; preserve terminal output.', file=sys.stderr)
        raise
