"""User-run fixed two-view pitch-rotation probability ensemble; no retraining."""
import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
R = Path('experiments/tcn-rotation-2026-11-11')
OUT = Path('data/tcn-rotation')
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
CONDITIONS = ('clean', 'targetlike')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def save(name, value):
    path = R / name
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def authority():
    require(dt.datetime.now(ZoneInfo('Asia/Kolkata')).date() < dt.date(2026, 11, 16),
            'Research frozen: no execution on or after November 16.')
    locks = json.loads((R / 'inputs.json').read_text())
    require(isinstance(locks, dict) and locks, 'Missing input locks')
    must_commit = [str(Path(__file__).resolve().relative_to(ROOT)), str(R / 'protocol.md'),
                   str(R / 'rotation.py'), str(R / 'tests/test_rotation.py'),
                   str(R / 'requirements.txt')]
    mandatory = [*must_commit,
                 'experiments/tcn-standalone-2026-11-11/results.json',
                 'experiments/tcn-standalone-2026-11-11/determinism.json',
                 'experiments/core-development/split.json']
    for match in IDS:
        mandatory.append(f'models/tcn-gap/{match}.pt')
        for condition in CONDITIONS:
            mandatory.extend([f'data/tcn-prepared/{match}-{condition}.npz',
                              f'data/tcn-standalone/{match}-{condition}-first.csv'])
    require(all(p in locks for p in mandatory), 'Incomplete registration')
    for name, expected in locks.items():
        path = Path(name)
        require(not path.is_absolute() and '..' not in path.parts, 'Invalid registered path')
        require(sha(path) == expected, 'Hash mismatch: ' + name)
    for name in [str(R / 'inputs.json'), *locks]:
        tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', name],
                                 capture_output=True).returncode == 0
        if tracked or name in [str(R / 'inputs.json'), *must_commit]:
            committed = subprocess.run(['git', 'show', 'HEAD:' + name], capture_output=True)
            require(committed.returncode == 0 and
                    hashlib.sha256(committed.stdout).hexdigest() == sha(name),
                    'Registration/source must match a git commit: ' + name)
    requirements = R / 'requirements.txt'
    if requirements.exists():
        require(str(requirements) in locks, 'Unpinned requirements file')
        for line in requirements.read_text().splitlines():
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            package, version = line.strip().split('==')
            require(importlib.metadata.version(package) == version,
                    'Runtime version mismatch: ' + package)
    split = json.loads(Path('experiments/core-development/split.json').read_text())
    require(tuple(split['development']) == IDS and
            not set(IDS).intersection(split['sealed']), 'Split changed')
    return locks


def checks():
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join([str(ROOT / 'src'), str(ROOT / 'scripts'),
                                      env.get('PYTHONPATH', '')])
    with (R / 'checks.txt').open('w') as log:
        for directory in ('tests', 'experiments/tcn-2026-11-10/tests',
                          'experiments/tcn-gap-2026-11-10/tests', str(R / 'tests')):
            log.write('\n' + directory + '\n')
            log.flush()
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover',
                                     '-s', directory, '-q'], stdout=log,
                                    stderr=subprocess.STDOUT, env=env)
            require(result.returncode == 0, 'Contract tests failed; see checks.txt')
    print('Existing contract tests passed.', flush=True)


def main():
    os.chdir(ROOT)
    locks = authority()
    require(not OUT.exists() and not (R / 'started.json').exists(),
            'Prior attempt exists: preserve evidence and request review, do not overwrite.')
    checks()
    # All imports below are performed only by the user-run command, after locks/checks.
    sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts'),
                   str(ROOT / 'experiments/tcn-2026-11-10'), str(ROOT / R)]
    import numpy as np
    import torch
    from tcn_candidate import TCN, configure, predict, WIDTH
    from rotation import rotate180, average_views
    from possession.decode import decode
    from possession.core import promote
    from possession.inputs import export_labels
    from review_frozen import score
    from evaluate_pff import missing

    configure()
    archive = json.loads(Path('experiments/tcn-standalone-2026-11-11/results.json').read_text())
    previous_det = json.loads(Path('experiments/tcn-standalone-2026-11-11/determinism.json').read_text())
    expected_cells = {(m, c) for m in IDS for c in CONDITIONS}
    def cells(rows):
        require(len(rows) == 10 and {(r['match'], r['condition']) for r in rows} == expected_cells,
                'Expected exactly ten unique match/condition cells')
        return {(r['match'], r['condition']): r for r in rows}
    archived = cells(archive)
    archived_det = cells(previous_det)
    require(all(r['reload_probabilities_equal'] and
                r['csv_bytes_equal_reload_batch4'] for r in previous_det),
            'Parent inference repeatability evidence failed')
    OUT.mkdir(parents=True)
    save('started.json', {'time': dt.datetime.now(dt.timezone.utc).isoformat(),
                         'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                         'inputs_sha256': sha(R / 'inputs.json'), 'training_executed': False})
    rows, parents, determinism, costs = [], [], [], []
    transition = (1 - np.eye(3)) * 16

    def load_model(path):
        checkpoint = torch.load(path, map_location='cpu', weights_only=True)
        require(set(checkpoint) == {'state', 'mean', 'scale'}, 'Unexpected checkpoint fields')
        normalizer = (np.asarray(checkpoint['mean']), np.asarray(checkpoint['scale']))
        require(np.array_equal(normalizer[0], np.zeros(WIDTH)) and
                np.array_equal(normalizer[1], np.ones(WIDTH)), 'Normalizer changed')
        model = TCN().cpu()
        model.load_state_dict(checkpoint['state'], strict=True)
        model.eval()
        return model, normalizer

    for match in IDS:
        start = time.monotonic()
        checkpoint_path = Path('models/tcn-gap') / (match + '.pt')
        require(all(sha(checkpoint_path) == archived_det[(match, condition)]['checkpoint_sha256']
                    for condition in CONDITIONS), 'Parent checkpoint ancestry hash differs')
        model, scaler = load_model(checkpoint_path)
        reload_model, reload_scaler = load_model(checkpoint_path)
        clean_y = clean_blocks = None
        for condition in CONDITIONS:
            with np.load(f'data/tcn-prepared/{match}-{condition}.npz', allow_pickle=False) as data:
                x, y, blocks = data['x'], data['y'], data['blocks'].tolist()
            require(x.ndim == 2 and x.shape == (len(y), WIDTH) and
                    set(np.unique(y)) <= set('HADX'), 'Invalid prepared dimensions/labels')
            if condition == 'clean':
                clean_y, clean_blocks = y.copy(), blocks
            else:
                require(np.array_equal(y, clean_y) and blocks == clean_blocks,
                        'Corruption changed labels or blocks')
            seq = predict(model, x, blocks, scaler)
            parent_prediction = decode(seq, transition, blocks)
            parent_path = OUT / f'{match}-{condition}-parent.csv'
            export_labels(parent_path, parent_prediction, len(y))
            old_path = f'data/tcn-standalone/{match}-{condition}-first.csv'
            require(sha(parent_path) == sha(old_path) == archived_det[(match, condition)]['csv_sha256'],
                    'Frozen parent reconstruction differs: ' + match + '/' + condition)
            parent_score = score(y, parent_prediction, blocks)
            for metric in ('spellF1', 'macroF1'):
                require(abs(parent_score[metric] - archived[(match, condition)][metric]) <= 1e-12,
                        'Frozen parent metric mismatch: ' + metric)
            parent = {'match': match, 'condition': condition, **parent_score,
                      'missing_ball': missing(y, parent_prediction, x[:, -4] == 0)}
            rotated = rotate180(x)
            rotated_seq = predict(model, rotated, blocks, scaler)
            combined = average_views(seq, rotated_seq)
            candidate = decode(combined, transition, blocks)
            reloaded = predict(reload_model, x, blocks, reload_scaler)
            reloaded_rotated = predict(reload_model, rotated, blocks, reload_scaler)
            require(np.array_equal(seq, reloaded), 'Identity-view reload probabilities differ')
            require(np.array_equal(rotated_seq, reloaded_rotated), 'Rotated-view reload probabilities differ')
            reload_combined = average_views(reloaded, reloaded_rotated)
            require(np.array_equal(combined, reload_combined), 'Ensemble reload probabilities differ')
            batch4 = average_views(predict(model, x, blocks, scaler, batch=4),
                                   predict(model, rotated, blocks, scaler, batch=4))
            predictions = (candidate, decode(reload_combined, transition, blocks),
                           decode(batch4, transition, blocks))
            paths = [OUT / f'{match}-{condition}-{tag}.csv' for tag in ('first', 'reload', 'batch4')]
            for path, prediction in zip(paths, predictions):
                export_labels(path, prediction, len(y))
            hashes = [sha(path) for path in paths]
            require(len(set(hashes)) == 1, 'Candidate CSV differs across reload/batch modes')
            rows.append({'match': match, 'condition': condition, **score(y, candidate, blocks),
                         'missing_ball': missing(y, candidate, x[:, -4] == 0)})
            parents.append(parent)
            determinism.append({'match': match, 'condition': condition,
                                'checkpoint_sha256': sha(checkpoint_path),
                                'parent_reconstructed_exact': True,
                                'parent_csv_sha256': sha(parent_path),
                                'reload_probabilities_equal': True,
                                'both_view_reload_probabilities_equal': True,
                                'csv_bytes_equal_reload_batch4': True,
                                'csv_paths': [str(p) for p in paths], 'csv_sha256': hashes[0]})
            for name, value in [('results.json', rows), ('parent.json', parents),
                                ('determinism.json', determinism)]:
                save(name, value)
            print('Completed', match, condition, flush=True)
        costs.append({'match': match, 'seconds': time.monotonic() - start})
        save('cost.json', costs)
    cells(rows)
    cells(parents)
    cells(determinism)
    # Detect an input/source mutation during the user-run job before declaring eligibility.
    for path, expected in locks.items():
        require(sha(path) == expected, 'Registered input changed during execution: ' + path)
    paired = lambda records: {m: tuple(np.mean([[r['spellF1'], r['macroF1']]
                              for r in records if r['match'] == m], axis=0)) for m in IDS}
    a, b = paired(rows), paired(parents)
    ds = {m: float(a[m][0] - b[m][0]) for m in IDS}
    dm = {m: float(a[m][1] - b[m][1]) for m in IDS}
    index, parent_index = cells(rows), cells(parents)
    dc = {m: index[(m, 'targetlike')]['spellF1'] - parent_index[(m, 'targetlike')]['spellF1'] for m in IDS}
    primary = float(np.median(list(dc.values())))
    gate = {'quality_eligible': bool(promote(b, a, True) and primary >= .01),
            'existing_gate': promote(b, a, True), 'primary_median_delta': primary,
            'paired_spell_deltas': ds, 'paired_macro_deltas': dm, 'primary_deltas': dc,
            'matches_improved': sum(v > 0 for v in ds.values()),
            'tests_pass': True, 'determinism_pass': True,
            'training_executed': False, 'production_changed': False,
            'sealed_opened': False, 'pff_holdout_opened': False,
            'clean_environment_verified': False}
    save('gate.json', gate)
    save('decision.json', {'quality_eligible': gate['quality_eligible'],
                           'parent': 'gap_trained_standalone_short_context_tcn_penalty16',
                           'method': 'equal_identity_and_180degree_rotation_probability_average',
                           'production_changed': False, 'automatic_followup': False})
    report = ('# Fixed pitch-rotation ensemble comparison\n\nDevelopment eligibility only. '
              'No retraining or production switch.\n\n'
              '|Match|Setting|Parent spellF1|Rotation ensemble spellF1|Parent macroF1|Rotation ensemble macroF1|\n'
              '|---|---|---:|---:|---:|---:|\n')
    for p, r in zip(parents, rows):
        report += (f"|{r['match']}|{r['condition']}|{p['spellF1']:.6f}|{r['spellF1']:.6f}|"
                   f"{p['macroF1']:.6f}|{r['macroF1']:.6f}|\n")
    (R / 'report.md').write_text(report + '\n```json\n' + json.dumps(gate, indent=2) + '\n```\n')
    print(json.dumps(gate, indent=2), flush=True)
    with Path('ball.md').open('a') as journal:
        journal.write('\nFixed pitch-rotation ensemble evaluation completed; no promotion. ' + json.dumps(gate) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', required=True)
    parser.parse_args()
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        # Preserve partial evidence. Failures never produce a passing gate or auto-resume.
        if (ROOT / R).exists():
            os.chdir(ROOT)
            save('last-failure.json', {'error_type': type(error).__name__, 'message': str(error),
                                       'production_changed': False})
        raise
