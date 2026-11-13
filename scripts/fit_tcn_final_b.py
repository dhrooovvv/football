"""User-run final Trial-B ensemble on the five eligible development matches."""
import argparse
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
R = Path('experiments/tcn-final-b-2026-11-13')
MISSED = Path('experiments/tcn-missed-2026-11-13')
sys.path.insert(0, str(PROJECT / R))
from release_contract import (MODELS, IDS, KEYS, SEEDS, require, sha, write_json,
                              registration, storage_guard, operation_lock, check_date)


def load(path):
    return json.loads(Path(path).read_text())


def proofs_path(seed):
    return MODELS / str(seed) / 'proof.json'


def checkpoints(seed):
    return [MODELS / str(seed) / fit / 'progress.pt' for fit in ('first', 'repeat')]


def verify_proof(seed, signature):
    path = proofs_path(seed)
    if not path.exists():
        return None
    proof = load(path)
    require(proof['registration'] == signature and proof['seed'] == seed
            and proof['training_matches'] == list(KEYS) and proof['steps'] == 40000
            and proof['repeated_training_exact'] and proof['checkpoint_state_reload_exact'],
            'Completed member proof identity differs')
    require(sha(proof['checks_path']) == proof['checks_sha256'], 'Checks log changed')
    require(set(proof['checkpoint_hashes']) == {str(p) for p in checkpoints(seed)},
            'Wrong final member checkpoint paths')
    for name, digest in proof['checkpoint_hashes'].items():
        require(sha(name) == digest, 'Final member checkpoint changed')
    return proof


def run_checks():
    path = R / 'evaluation' / ('checks-' + str(time.time_ns()) + '.txt')
    with storage_guard():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as log:
            suites = ('tests', 'experiments/tcn-2026-11-10/tests',
                      'experiments/tcn-gap-2026-11-10/tests',
                      'experiments/tcn-rotation-2026-11-11/tests',
                      'experiments/tcn-pretrain-2026-11-11/tests',
                      'experiments/tcn-parallel-2026-11-12/tests',
                      str(MISSED / 'tests'), str(R / 'tests'))
            for suite in suites:
                log.write('\n' + suite + '\n'); log.flush()
                env = os.environ.copy()
                env['PYTHONPATH'] = str(PROJECT / 'src') + os.pathsep + str(PROJECT / 'scripts')
                result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', suite, '-v'],
                                        stdout=log, stderr=subprocess.STDOUT, env=env)
                require(result.returncode == 0, 'Final contracts failed; preserve ' + str(path))
    return path


def fit_member(seed, signature, checks):
    require(seed in SEEDS, 'Unregistered seed')
    require(checks.parent == R / 'evaluation' and checks.name.startswith('checks-')
            and checks.is_file(), 'Missing final contracts log')
    log = checks.read_text()
    require(log.count('\nOK\n') == 8 and 'FAILED (' not in log, 'Incomplete final contracts log')
    with operation_lock(seed):
        if verify_proof(seed, signature):
            print('Member already complete:', seed, flush=True)
            return
        sys.path[:0] = [str(PROJECT / R), str(PROJECT / MISSED),
                       str(PROJECT / 'experiments/tcn-parallel-2026-11-12'),
                       str(PROJECT / 'experiments/tcn-expanded-2026-11-10')]
        import torch
        from parallel_model import configure
        from expanded_data import CompactCase
        from final_training import train_final, expected_identity, validate_saved, confirm_repeat
        configure()
        cases = [CompactCase(Path('data/tcn-expanded') / key) for key in KEYS]
        started = time.monotonic()
        first = train_final(cases, checkpoints(seed)[0].parent, signature, seed, storage_guard)
        train_final(cases, checkpoints(seed)[1].parent, signature, seed, storage_guard)
        paths = checkpoints(seed)
        saved = [torch.load(p, map_location='cpu', weights_only=True) for p in paths]
        identity = expected_identity(signature, seed)
        for value in saved:
            validate_saved(value, identity)
        confirm_repeat(*saved)
        loaded = type(first)().cpu().eval()
        loaded.load_state_dict(saved[0]['state'], strict=True)
        require(all(torch.equal(value, loaded.state_dict()[name]) for name, value in first.state_dict().items()),
                'Final in-memory and reloaded state differ')
        _, final_signature = registration()
        require(final_signature == signature, 'Final source/data changed during training')
        value = saved[0]
        proof = dict(registration=signature, seed=seed, identity=identity, steps=40000,
            training_matches=list(KEYS), repeated_training_exact=True, checkpoint_state_reload_exact=True,
            checks_path=str(checks), checks_sha256=sha(checks),
            checkpoint_hashes={str(p): sha(p) for p in paths},
            coverage=value['coverage'], supervised_views=value['supervised_views'],
            exposure=value['exposure'], sampler_audit=value['sampler_audit'],
            loss_sha256=hashlib.sha256(json.dumps(value['losses']).encode()).hexdigest(),
            component_loss_sha256=hashlib.sha256(json.dumps(value['component_losses']).encode()).hexdigest(),
            component_loss_summary={k: dict(mean=sum(v) / len(v), first=v[0], last=v[-1])
                                    for k, v in value['component_losses'].items()},
            stage_seconds={fit: v['stage_seconds'] for fit, v in zip(('first', 'repeat'), saved)},
            elapsed_seconds=time.monotonic() - started, quality_evaluation_performed=False,
            production_promoted=False, target_accuracy='unknown')
        write_json(proofs_path(seed), proof)
        verify_proof(seed, signature)
        print('Completed final seed', seed, flush=True)


def completed_manifest(signature):
    path = MODELS / 'manifest.json'
    if not path.exists():
        return None
    value = load(path)
    require(value['schema'] == 'final_five_trial_b_two_seed_original_motion_tcn_v1'
            and value['sampler'] == 'short_mix'
            and value['loss'] == 'cross_entropy_plus_0.1_segment_soft_iou'
            and value['class_order'] == ['H', 'A', 'D']
            and value['scaler_policy'] == 'zeros_ones_521'
            and value['source_lock_sha256'] == sha(R / 'inputs.json')
            and value['selection_review_sha256'] == sha(MISSED / 'reviewed-b.json')
            and value['environment'] == load('experiments/tcn-winner-release-2026-11-12/environment-snapshot.json')
            and value['registration'] == signature and value['training_matches'] == list(KEYS)
            and value['training_steps_per_member'] == 40000
            and value['inference'] == dict(rotation180_probability_weights=[.5, .5],
                                           seed_probability_weights=[.5, .5], switching_penalty=16)
            and value['quality_evaluation_performed'] is False
            and value['production_promoted'] is False, 'Final manifest differs')
    require(set(value['members']) == {str(s) for s in SEEDS}, 'Final ensemble needs exactly two seeds')
    for seed in SEEDS:
        proof = verify_proof(seed, signature)
        member = value['members'][str(seed)]
        require(proof and member['proof'] == str(proofs_path(seed))
                and member['repeat_model'] == str(checkpoints(seed)[1])
                and member['repeat_sha256'] == sha(checkpoints(seed)[1])
                and member['proof_sha256'] == sha(proofs_path(seed))
                and member['model'] == str(checkpoints(seed)[0])
                and member['sha256'] == sha(checkpoints(seed)[0]), 'Member manifest differs')
    return value


def run(signature, workers):
    with operation_lock():
        if completed_manifest(signature):
            print('Final ensemble already complete; preserved evidence.', flush=True)
            return
        checks = run_checks()
        pending, live = list(SEEDS), []
        try:
            while pending or live:
                check_date()
                while pending and len(live) < workers:
                    seed = pending.pop(0)
                    with storage_guard():
                        path = R / 'evaluation' / f'worker-{seed}-{time.time_ns()}.txt'
                        handle = path.open('w')
                    command = [sys.executable, str(Path(__file__).relative_to(PROJECT)),
                               '--worker', str(seed), '--checks-file', str(checks), '--run']
                    child = subprocess.Popen(command, stdout=handle, stderr=subprocess.STDOUT)
                    live.append((child, handle))
                    print('Started seed', seed, 'log:', path, flush=True)
                for item in list(live):
                    child, handle = item
                    if child.poll() is not None:
                        handle.close(); live.remove(item)
                        require(child.returncode == 0, 'Final member worker failed; preserve logs')
                if live:
                    time.sleep(1)
        finally:
            for child, handle in live:
                if child.poll() is None:
                    child.terminate()
                child.wait(); handle.close()
        _, end_signature = registration()
        require(end_signature == signature, 'Final registration changed')
        proofs = {seed: verify_proof(seed, signature) for seed in SEEDS}
        require(all(proofs.values()), 'Final ensemble members incomplete')
        environment = load('experiments/tcn-winner-release-2026-11-12/environment-snapshot.json')
        write_json(MODELS / 'manifest.json', dict(registration=signature,
            schema='final_five_trial_b_two_seed_original_motion_tcn_v1',
            training_matches=list(KEYS), training_steps_per_member=40000,
            sampler='short_mix', loss='cross_entropy_plus_0.1_segment_soft_iou',
            class_order=['H', 'A', 'D'], scaler_policy='zeros_ones_521',
            inference=dict(rotation180_probability_weights=[.5, .5], seed_probability_weights=[.5, .5],
                           switching_penalty=16),
            members={str(seed): dict(model=str(checkpoints(seed)[0]), sha256=sha(checkpoints(seed)[0]),
                                    repeat_model=str(checkpoints(seed)[1]), repeat_sha256=sha(checkpoints(seed)[1]),
                                    proof=str(proofs_path(seed)), proof_sha256=sha(proofs_path(seed))) for seed in SEEDS},
            environment=environment, source_lock_sha256=sha(R / 'inputs.json'),
            selection_review_sha256=sha(MISSED / 'reviewed-b.json'),
            code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            quality_evaluation_performed=False, production_promoted=False,
            target_accuracy='unknown', private_export_completed=False))
        completed_manifest(signature)
        print('Final ensemble fitted and repeated exactly. Stop and send done for artifact audit.', flush=True)
        print('Manifest:', MODELS / 'manifest.json', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', required=True)
    parser.add_argument('--workers', type=int, choices=(1, 2), default=2)
    parser.add_argument('--worker', type=int, choices=SEEDS, help=argparse.SUPPRESS)
    parser.add_argument('--checks-file', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    os.chdir(PROJECT)
    _, signature = registration()
    if args.worker is None:
        run(signature, args.workers)
    else:
        require(args.checks_file is not None, 'Worker requires contracts log')
        fit_member(args.worker, signature, args.checks_file)


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        os.chdir(PROJECT)
        try:
            write_json(R / 'failures' / f'{time.time_ns()}.json',
                       dict(error_type=type(error).__name__, message=str(error), production_changed=False))
        except Exception:
            print('Preserve terminal output: failure record could not be written.', file=sys.stderr)
        raise
