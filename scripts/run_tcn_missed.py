"""User-run short-spell exposure and segment-overlap trials; no target inputs."""
import argparse
from functools import lru_cache
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
PROJECT = Path(__file__).resolve().parents[1]
R = Path('experiments/tcn-missed-2026-11-13')
OLD = Path('experiments/tcn-parallel-2026-11-12')
DATA = Path('data/tcn-missed')
MODELS = Path('models/tcn-missed')
SEEDS = (20261106, 20261107)
sys.path[:0] = [str(PROJECT / R), str(PROJECT / 'scripts'), str(PROJECT / OLD)]
from contract import (IDS, SETTINGS, require, sha, write_json, check_date,
                      registration, binding, gate_v2, storage_guard, operation_lock)


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    with storage_guard():
        write_json(path, value)


def trial_identity(trial, signature):
    bound = binding(trial, signature)
    value = hashlib.sha256((signature + json.dumps(bound, sort_keys=True)).encode()).hexdigest()
    return bound, value


def parent_rows(bound):
    path = (OLD / 'evaluation/ensemble/results.json' if bound['parent_trial'] == 'baseline'
            else R / 'evaluation/a/results.json')
    require(sha(path) == bound['parent_results_sha256'], 'Parent result binding changed')
    return {(r['match'], r['condition']): r for r in load(path)}


def checks(trial):
    path = R / 'evaluation' / trial / ('checks-' + str(time.time_ns()) + '.txt')
    with storage_guard():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as log:
            folders = ('tests', 'experiments/tcn-2026-11-10/tests',
                       'experiments/tcn-gap-2026-11-10/tests',
                       'experiments/tcn-rotation-2026-11-11/tests',
                       'experiments/tcn-pretrain-2026-11-11/tests',
                       str(OLD / 'tests'), str(R / 'tests'))
            for folder in folders:
                log.write('\n' + folder + '\n'); log.flush()
                env = os.environ.copy()
                env['PYTHONPATH'] = str(PROJECT / 'src') + os.pathsep + str(PROJECT / 'scripts')
                result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', folder, '-v'],
                                        stdout=log, stderr=subprocess.STDOUT, env=env)
                require(result.returncode == 0, 'Checks failed; preserve ' + str(path))
    return path


@lru_cache(maxsize=1)
def dependencies():
    sys.path[:0] = [str(PROJECT / p) for p in ('src', 'scripts', str(R), str(OLD),
        'experiments/tcn-pretrain-2026-11-11', 'experiments/tcn-expanded-2026-11-10',
        'experiments/tcn-rotation-2026-11-11', 'reference/more-than-a-hack-2027-main/evaluation')]
    import numpy as np
    import torch
    import parallel_model as model_code
    model_code.configure()
    from expanded_data import CompactCase
    from training import train_fit, validate_saved, expected_identity, confirm_repeat
    from rotation import rotate180, average_views
    from possession.decode import decode
    from possession.inputs import export_labels
    from review_frozen import score
    from evaluate_pff import missing
    import possession_metrics as official
    from run_tcn_parallel import metrics
    return locals()


def fit_path(trial, match, seed, fit):
    return MODELS / trial / match / str(seed) / fit / 'progress.pt'


def proof_path(trial, match, seed):
    return R / 'evaluation' / trial / 'fits' / f'{match}-{seed}.json'


def verify_fit(trial, match, seed, signature, sampler):
    path = proof_path(trial, match, seed)
    if not path.exists():
        return None
    proof = load(path)
    require(proof['trial_signature'] == signature and proof['sampler'] == sampler
            and proof['seed'] == seed and proof['match'] == match
            and proof['exact_repeat'] and proof['training_steps'] == 40000,
            'Fit proof identity differs')
    require(sha(proof['checks_path']) == proof['checks_sha256'], 'Checks log changed')
    expected = {str(fit_path(trial, match, seed, fit)) for fit in ('first', 'repeat')}
    require(set(proof['checkpoint_hashes']) == expected, 'Wrong fit checkpoint paths')
    for name, digest in proof['checkpoint_hashes'].items():
        require(sha(name) == digest, 'Fit checkpoint changed')
    require(proof['training_matches'] == ['idsse-' + m for m in IDS if m != match],
            'Fit membership changed')
    return proof


def worker(trial, seed, signature, sampler, checks_path):
    require(seed in SEEDS, 'Unregistered seed')
    require(checks_path.is_file() and checks_path.parent == R / 'evaluation' / trial
            and checks_path.name.startswith('checks-'), 'Missing trial contracts log')
    log = checks_path.read_text()
    require(log.count('\nOK\n') == 7 and 'FAILED (' not in log, 'Incomplete trial contracts log')
    d = dependencies()
    torch = d['torch']
    for match in IDS:
        check_date()
        if verify_fit(trial, match, seed, signature, sampler):
            continue
        cases = [d['CompactCase'](Path('data/tcn-expanded') / ('idsse-' + m))
                 for m in IDS if m != match]
        started = time.monotonic()
        for fit in ('first', 'repeat'):
            d['train_fit'](cases, fit_path(trial, match, seed, fit).parent,
                           signature, trial, seed, match, sampler, storage_guard)
        paths = [fit_path(trial, match, seed, fit) for fit in ('first', 'repeat')]
        saved = [torch.load(p, map_location='cpu', weights_only=True) for p in paths]
        identity = d['expected_identity'](signature, trial, seed, match, sampler)
        for value in saved:
            d['validate_saved'](value, identity)
        d['confirm_repeat'](*saved)
        value = saved[0]
        save(proof_path(trial, match, seed), dict(trial_signature=signature,
            sampler=sampler, trial=trial, match=match, seed=seed, training_steps=40000,
            training_matches=['idsse-' + m for m in IDS if m != match], exact_repeat=True,
            checks_path=str(checks_path), checks_sha256=sha(checks_path),
            checkpoint_hashes={str(p): sha(p) for p in paths},
            sampler_audit=value['sampler_audit'], exposure=value['exposure'],
            coverage=value['coverage'], supervised_views=value['supervised_views'],
            training_loss_sha256=hashlib.sha256(json.dumps(value['losses']).encode()).hexdigest(),
            component_loss_sha256=hashlib.sha256(json.dumps(value['component_losses']).encode()).hexdigest(),
            component_loss_summary={key: dict(mean=sum(v) / len(v), first=v[0], last=v[-1])
                                    for key, v in value['component_losses'].items()},
            training_stage_seconds={fit: v['stage_seconds'] for fit, v in zip(('first', 'repeat'), saved)},
            seconds=time.monotonic() - started))
        verify_fit(trial, match, seed, signature, sampler)
        print('Completed fits', trial, match, seed, flush=True)
        del cases, saved


def model_from(path, d):
    saved = d['torch'].load(path, map_location='cpu', weights_only=True)
    model = d['model_code'].model_for_arm('ensemble').cpu().eval()
    model.load_state_dict(saved['state'], strict=True)
    return model


def parent_models(match, bound, d, signature):
    if bound['parent_trial'] == 'baseline':
        paths = [Path('models/tcn-pretrain/evaluation/control') / match / 'first/progress.pt',
                 Path('models/tcn-parallel/ensemble') / match / 'first/progress.pt']
    else:
        a_bound, a_signature = trial_identity('a', signature)
        for seed in SEEDS:
            require(verify_fit('a', match, seed, a_signature, a_bound['sampler']), 'Missing A fit proof')
        paths = [fit_path('a', match, seed, 'first') for seed in SEEDS]
    return [model_from(path, d) for path in paths]


def infer_ensemble(models, x, blocks, d, batch=1):
    model_code = d['model_code']
    np = d['np']
    members, views = [], []
    for model in models:
        pair = tuple(model_code.predict(model, values, blocks,
                     (np.zeros(model_code.WIDTH), np.ones(model_code.WIDTH)), batch=batch)
                     for values in (x, d['rotate180'](x)))
        views.extend(pair)
        members.append(d['average_views'](*pair))
    return d['average_views'](*members), views


def evaluate(trial, bound, signature, base_signature, preflight_only=False):
    d = dependencies(); np = d['np']
    old = parent_rows(bound)
    rows = []
    for match in IDS:
        models = parent_models(match, bound, d, base_signature)
        candidates = None
        if not preflight_only:
            for seed in SEEDS:
                require(verify_fit(trial, match, seed, signature, bound['sampler']), 'Missing fit proof')
            candidates = [model_from(fit_path(trial, match, seed, 'first'), d) for seed in SEEDS]
        for condition in SETTINGS:
            check_date()
            with np.load(f'data/tcn-prepared/{match}-{condition}.npz', allow_pickle=False) as data:
                x, y, blocks = data['x'], data['y'], data['blocks'].tolist()
            require(x.shape == (len(y), d['model_code'].WIDTH), 'Evaluation schema differs')
            parent_prob, _ = infer_ensemble(models, x, blocks, d)
            prediction = d['decode'](parent_prob, (1 - np.eye(3)) * 16, blocks)
            parent_path = DATA / trial / 'predictions' / f'{match}-{condition}-parent.csv'
            with storage_guard():
                parent_path.parent.mkdir(parents=True, exist_ok=True)
                d['export_labels'](parent_path, prediction, len(y))
            require(sha(parent_path) == old[match, condition]['csv_sha256'], 'Parent CSV preflight differs')
            measured = d['metrics'](y, prediction, blocks, d['score'], d['official'], np)
            require(measured == old[match, condition]['candidate'], 'Parent metrics preflight differs')
            if preflight_only:
                continue
            outputs, candidate_views = [], []
            reload_models = [model_from(fit_path(trial, match, seed, 'first'), d) for seed in SEEDS]
            for members, batch in ((candidates, 1), (reload_models, 1), (candidates, 4)):
                probabilities, views = infer_ensemble(members, x, blocks, d, batch)
                candidate_views.append(views)
                outputs.append(d['decode'](probabilities, (1 - np.eye(3)) * 16, blocks))
            require(all(np.array_equal(a, b) for a, b in zip(candidate_views[0], candidate_views[1])),
                    'Both seed/both view reload probabilities differ')
            paths = [DATA / trial / 'predictions' / f'{match}-{condition}-{tag}.csv'
                     for tag in ('first', 'reload', 'batch4')]
            for path, value in zip(paths, outputs):
                with storage_guard():
                    d['export_labels'](path, value, len(y))
            require(len({sha(path) for path in paths}) == 1, 'CSV batch/reload bytes differ')
            rows.append(dict(match=match, condition=condition, parent=measured,
                candidate=d['metrics'](y, outputs[0], blocks, d['score'], d['official'], np),
                parent_csv_sha256=sha(parent_path), parent_reconstruction_path=str(parent_path),
                parent_missing_ball=d['missing'](y, prediction, x[:, -4] == 0),
                candidate_missing_ball=d['missing'](y, outputs[0], x[:, -4] == 0),
                csv_paths=[str(p) for p in paths], csv_sha256=sha(paths[0]),
                reload_probabilities_equal_both_views=True, csv_bytes_equal_reload_batch4=True))
            save(R / 'evaluation' / trial / 'results-partial.json', rows)
            print('Evaluated', trial, match, condition, flush=True)
    if preflight_only:
        return
    require(len(rows) == 10, 'Missing evaluation cases')
    path = R / 'evaluation' / trial
    save(path / 'results.json', rows)
    before = [dict(match=r['match'], condition=r['condition'], **r['parent']) for r in rows]
    after = [dict(match=r['match'], condition=r['condition'], **r['candidate']) for r in rows]
    gate = gate_v2(before, after)
    save(path / 'gate-v2.json', gate)
    report = '# Trial ' + trial.upper() + '\n\n|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|\n|---|---|---:|---:|---:|---:|\n'
    for r in rows:
        report += f"|{r['match']}|{r['condition']}|{r['parent']['spellF1']:.6f}|{r['candidate']['spellF1']:.6f}|{r['parent']['macroF1']:.6f}|{r['candidate']['macroF1']:.6f}|\n"
    report += '\nGate v2:\n\n```json\n' + json.dumps(gate, indent=2) + '\n```\n\nReused development evidence only. Target accuracy unknown. No automatic production switch.\n'
    with storage_guard():
        (path / 'report.md').write_text(report)
    save(path / 'completion.json', dict(completed=True, trial=trial, registration=base_signature,
        trial_signature=signature, binding=bound, case_count=10, contracts_passed=True,
        repeated_training_exact=True, results_sha256=sha(path / 'results.json'),
        gate_sha256=sha(path / 'gate-v2.json'),
        fit_proofs={str(proof_path(trial, m, s)): sha(proof_path(trial, m, s)) for m in IDS for s in SEEDS},
        production_changed=False, target_accuracy='unknown'))


def verify_completed(trial, signature, bound):
    path = R / 'evaluation' / trial
    done = load(path / 'completion.json')
    require(done['completed'] and done['trial_signature'] == signature and done['binding'] == bound
            and done['contracts_passed'] and done['repeated_training_exact'] and done['case_count'] == 10,
            'Completion proof identity differs')
    require(sha(path / 'results.json') == done['results_sha256']
            and sha(path / 'gate-v2.json') == done['gate_sha256'], 'Result or gate changed')
    expected_proofs = {str(proof_path(trial, m, s)) for m in IDS for s in SEEDS}
    require(set(done['fit_proofs']) == expected_proofs, 'Missing fit proofs')
    for name, digest in done['fit_proofs'].items():
        require(sha(name) == digest, 'Fit proof changed')
    for m in IDS:
        for s in SEEDS:
            verify_fit(trial, m, s, signature, bound['sampler'])
    rows = load(path / 'results.json'); old = parent_rows(bound)
    require(len(rows) == 10 and {(r['match'], r['condition']) for r in rows}
            == {(m, c) for m in IDS for c in SETTINGS}, 'Incomplete result cells')
    for row in rows:
        require(row['parent'] == old[row['match'], row['condition']]['candidate'], 'Parent result changed')
        require(row['reload_probabilities_equal_both_views'] and row['csv_bytes_equal_reload_batch4'],
                'Inference equality proof missing')
        for name in row['csv_paths']:
            require(sha(name) == row['csv_sha256'], 'Prediction changed')
        require(sha(row['parent_reconstruction_path']) == row['parent_csv_sha256']
                == old[row['match'], row['condition']]['csv_sha256'], 'Parent CSV changed')
    gate = gate_v2([dict(match=r['match'], condition=r['condition'], **r['parent']) for r in rows],
                   [dict(match=r['match'], condition=r['condition'], **r['candidate']) for r in rows])
    require(gate == load(path / 'gate-v2.json'), 'Saved gate disagrees')
    return done, rows, gate


def run(trial, locked, membership, base_signature, workers):
    bound, signature = trial_identity(trial, base_signature)
    with operation_lock(trial):
        if (R / 'evaluation' / trial / 'completion.json').exists():
            verify_completed(trial, signature, bound)
            print('Already complete; preserved evidence. Report done for review.', flush=True)
            return
        log = checks(trial)
        # Old complete evidence is validated before any model fitting.
        from run_tcn_parallel import completion
        old_membership = load(OLD / 'membership.json')
        old_signature = hashlib.sha256((sha(OLD / 'protocol.md') + sha(OLD / 'inputs.json')).encode()).hexdigest()
        completion('ensemble', old_signature, old_membership)
        evaluate(trial, bound, signature, base_signature, preflight_only=True)
        pending, live = list(SEEDS), []
        try:
            while pending or live:
                check_date()
                while pending and len(live) < workers:
                    seed = pending.pop(0)
                    log_path = R / 'evaluation' / trial / f'worker-{seed}-{time.time_ns()}.txt'
                    with storage_guard():
                        handle = log_path.open('w')
                    command = [sys.executable, str(Path(__file__).relative_to(PROJECT)), '--trial', trial,
                               '--worker', str(seed), '--checks-file', str(log), '--run']
                    child = subprocess.Popen(command, stdout=handle, stderr=subprocess.STDOUT)
                    live.append((child, handle, seed))
                    print('Started seed', seed, 'log:', log_path, flush=True)
                for item in list(live):
                    child, handle, seed = item
                    if child.poll() is not None:
                        handle.close(); live.remove(item)
                        require(child.returncode == 0, 'Worker failed for seed ' + str(seed))
                if live:
                    time.sleep(1)
        finally:
            for child, handle, _ in live:
                if child.poll() is None:
                    child.terminate()
                child.wait(); handle.close()
        evaluate(trial, bound, signature, base_signature)
        # Recheck all source and source data fingerprints before accepting completion.
        registration()
        verify_completed(trial, signature, bound)
        print('Trial complete. Stop and report done for review; do not start another trial.', flush=True)


def pending_review(signature):
    bound, trial_signature = trial_identity('a', signature)
    done, rows, gate = verify_completed('a', trial_signature, bound)
    accepted = gate['quality_eligible']
    selected_path = (R / 'evaluation/a/results.json' if accepted
                     else OLD / 'evaluation/ensemble/results.json')
    record = dict(registration=signature, reviewed=True, accepted=accepted,
        sampler='short_mix' if accepted else 'uniform', parent_trial='a' if accepted else 'baseline',
        parent_results_sha256=sha(selected_path), a_completion_sha256=sha(R / 'evaluation/a/completion.json'))
    save(R / 'pending-review-a.json', record)
    print('Prepared pending-review-a.json. Assistant must review and commit reviewed-a.json before B.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trial', choices=('a', 'b'))
    parser.add_argument('--review-a', action='store_true')
    parser.add_argument('--worker', type=int, choices=SEEDS, help=argparse.SUPPRESS)
    parser.add_argument('--checks-file', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--workers', type=int, choices=(1, 2), default=2)
    parser.add_argument('--run', action='store_true', required=True)
    args = parser.parse_args()
    require(bool(args.trial) != args.review_a, 'Choose --trial or --review-a')
    os.chdir(PROJECT)
    locked, membership, signature = registration()
    if args.trial == 'b':
        a_bound, a_signature = trial_identity('a', signature)
        verify_completed('a', a_signature, a_bound)
    if args.review_a:
        require(args.worker is None, 'Review cannot be a training worker')
        with operation_lock('a'):
            pending_review(signature)
    elif args.worker is not None:
        bound, trial_signature = trial_identity(args.trial, signature)
        require(args.checks_file is not None, 'Worker needs contracts log')
        directory = DATA / args.trial
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / f'seed-{args.worker}.lock').open('a+') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            worker(args.trial, args.worker, trial_signature, bound['sampler'], args.checks_file)
    else:
        run(args.trial, locked, membership, signature, args.workers)


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        # Preserve failures, including storage failures, without overwriting evidence.
        os.chdir(PROJECT)
        path = R / 'failures' / f'{time.time_ns()}.json'
        try:
            save(path, dict(error_type=type(error).__name__, message=str(error), production_changed=False))
        except Exception:
            print('Failure evidence could not be written; preserve this terminal output.', file=sys.stderr)
        raise
