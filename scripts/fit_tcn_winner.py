"""User-run final five-match fit of the qualified staged40k TCN recipe."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
ROOT = Path('experiments/tcn-winner-release-2026-11-12')
sys.path.insert(0, str(PROJECT / ROOT))
from release_contract import (IDS, KEYS, MODELS, SCHEMA, check_membership, registration,
                              reviewed_diagnostic, require, sha, write_json)


@contextmanager
def operation_lock():
    MODELS.mkdir(parents=True, exist_ok=True)
    handles = []
    try:
        for path in (Path('data/tcn-expanded/operation.lock'), MODELS / 'operation.lock'):
            handle = path.open('a+')
            handles.append(handle)
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError('Another final-fit or compact-data operation is active') from error
        yield
    finally:
        for handle in reversed(handles):
            handle.close()


def run_checks():
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join((str(PROJECT / 'src'), str(PROJECT / 'scripts'),
                                       env.get('PYTHONPATH', '')))
    with (ROOT / 'checks.txt').open('w') as log:
        for suite in ('tests', 'experiments/tcn-2026-11-10/tests',
                      'experiments/tcn-gap-2026-11-10/tests',
                      'experiments/tcn-rotation-2026-11-11/tests',
                      'experiments/tcn-pretrain-2026-11-11/tests', str(ROOT / 'tests')):
            log.write('\n' + suite + '\n')
            log.flush()
            completed = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', suite, '-v'],
                                       env=env, stdout=log, stderr=subprocess.STDOUT)
            require(completed.returncode == 0, 'User-run release contracts failed; inspect checks.txt')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', required=True)
    parser.add_argument('--slot-diagnostic', type=Path,
                        default=Path('experiments/tcn-winner-slot-audit-2026-11-12/decision.json'))
    parser.add_argument('--acknowledge-slot-risk', action='store_true', required=True,
                        help='Only after human review of the completed current-winner diagnostic')
    args = parser.parse_args()
    os.chdir(PROJECT)
    locked, signature, environment = registration(training=True)
    diagnostic = reviewed_diagnostic(args.slot_diagnostic, args.acknowledge_slot_risk)
    require(not (MODELS / 'manifest.json').exists(), 'Final manifest already exists; preserve earlier evidence')
    with operation_lock():
        require(not (MODELS / 'manifest.json').exists(), 'Final manifest was completed by another process')
        run_checks()
        # Runtime numerical imports occur only in this explicitly user-invoked command.
        sys.path[:0] = [str(PROJECT / 'experiments/tcn-pretrain-2026-11-11'),
                       str(PROJECT / 'experiments/tcn-expanded-2026-11-10')]
        import torch
        from pretrain_model import configure
        from expanded_data import CompactCase
        from winner_training import train_final, validate_saved, confirm_final_repeat
        from release_contract import expected_identity
        configure()
        cases = [CompactCase(Path('data/tcn-expanded') / key) for key in KEYS]
        check_membership(cases)
        started = time.monotonic()
        first = train_final(cases, MODELS / 'first', signature, diagnostic)
        repeat = train_final(cases, MODELS / 'repeat', signature, diagnostic)
        paths = [MODELS / name / 'progress.pt' for name in ('first', 'repeat')]
        saved = [torch.load(path, map_location='cpu', weights_only=True) for path in paths]
        identity = expected_identity(signature, diagnostic)
        for checkpoint in saved:
            validate_saved(checkpoint, identity)
        confirm_final_repeat(*saved)
        loaded = type(first)().cpu().eval()
        loaded.load_state_dict(saved[0]['state'], strict=True)
        require(all(torch.equal(value, loaded.state_dict()[name]) for name, value in first.state_dict().items()),
                'Reloaded final model differs')
        # Re-hash full source/inputs and reviewed diagnostic after both repeated fits.
        _, final_signature, _ = registration(training=True)
        require(final_signature == signature and reviewed_diagnostic(args.slot_diagnostic, True) == diagnostic,
                'Release inputs changed during final fitting')
        losses_sha = hashlib.sha256(json.dumps(saved[0]['losses']).encode()).hexdigest()
        manifest = dict(schema=SCHEMA, model=str(paths[0]), repeat_model=str(paths[1]),
                        sha256=sha(paths[0]), repeat_sha256=sha(paths[1]), registration=signature,
                        identity=identity, training_matches=list(KEYS), repeated_training_exact=True,
                        scaler_policy='zeros_ones_521', class_order=['H', 'A', 'D'],
                        inference=dict(rotation180_probability_weights=[.5, .5], switching_penalty=16),
                        slot_diagnostic=diagnostic, environment=environment,
                        coverage=saved[0]['coverage'], supervised_views=saved[0]['supervised_views'],
                        training_loss_sha256=losses_sha, training_steps=40000,
                        checkpoint_state_reload_exact=True,
                        stage_seconds={name: value['stage_seconds'] for name, value in zip(('first', 'repeat'), saved)},
                        elapsed_seconds=time.monotonic() - started,
                        code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                        release_inputs_sha256=sha(ROOT / 'inputs.json'),
                        prepared_manifest_hashes=locked['prepared_manifests'],
                        quality_evaluation_performed=False, production_promoted=False, target_accuracy='unknown')
        write_json(MODELS / 'losses.json', dict(minibatch_losses=saved[0]['losses'], not_validation_loss=True))
        write_json(MODELS / 'manifest.json', manifest)
        with Path('ball.md').open('a') as journal:
            journal.write('\nFinal five-IDSSE staged40k TCN fit and exact repeated fit completed. '
                          'Manifest SHA256 ' + sha(MODELS / 'manifest.json') + '. '
                          'This fit is not new quality evidence; production unchanged, target accuracy unknown.\n')
        print('Final fit repeated exactly. Manifest:', MODELS / 'manifest.json', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        os.chdir(PROJECT)
        write_json(MODELS / 'last-failure.json', dict(error_type=type(error).__name__,
                   message=str(error), production_changed=False))
        raise
