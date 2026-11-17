"""User-run boundary-supervised TCN training comparison; no automatic production promotion."""
import argparse
from contextlib import contextmanager
from datetime import date, datetime
import fcntl
import hashlib
from importlib.metadata import version
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

PROJECT = Path(__file__).resolve().parents[1]
R = Path('experiments/tcn-boundary-2026-11-11')
DATA = Path('data/tcn-boundary')
MODELS = Path('models/tcn-boundary/evaluation')
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
SETTINGS = ('clean', 'targetlike')
STEPS = 20000


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b''):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def check_date():
    require(datetime.now(ZoneInfo('Asia/Kolkata')).date() < date(2026, 11, 16),
            'Research closes at the start of November16; preserve partial evidence.')


def registration():
    check_date()
    registration_files = [R / 'protocol.md', R / 'inputs.json']
    for path in registration_files:
        saved = subprocess.run(['git', 'show', 'HEAD:' + str(path)], capture_output=True)
        require(saved.returncode == 0 and saved.stdout == path.read_bytes(),
                'Protocol and registration must be committed: ' + str(path))
    locked = json.loads((R / 'inputs.json').read_text())
    require(set(locked) == {'code', 'data', 'prepared_manifests'}, 'Unexpected lock schema')
    mandatory = ['scripts/run_tcn_boundary.py', str(R / 'protocol.md'),
                 str(R / 'boundary_model.py'), str(R / 'boundary_training.py'),
                 str(R / 'tests/test_boundary_model.py'), str(R / 'membership.json'),
                 str(R / 'requirements.txt'),
                 'experiments/tcn-rotation-2026-11-11/rotation.py',
                 'experiments/tcn-2026-11-10/environment.json',
                 'experiments/core-development/split.json']
    require(all(name in locked['code'] for name in mandatory), 'Incomplete source registration')
    for name, digest in locked['code'].items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Unsafe source path')
        require(sha(name) == digest, 'Source fingerprint changed: ' + name)
        tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', name],
                                 capture_output=True).returncode == 0
        if tracked or name in mandatory:
            committed = subprocess.run(['git', 'show', 'HEAD:' + name], capture_output=True)
            require(committed.returncode == 0 and
                    hashlib.sha256(committed.stdout).hexdigest() == digest,
                    'Source differs from git: ' + name)
    expected_manifests = {f'data/tcn-expanded/idsse-{match}/manifest.json' for match in IDS}
    require(set(locked['prepared_manifests']) == expected_manifests,
            'Exactly five development IDSSE compact manifests required')
    required_data = ['experiments/tcn-rotation-2026-11-11/results.json']
    for match in IDS:
        for setting in SETTINGS:
            required_data.extend([f'data/tcn-prepared/{match}-{setting}.npz',
                                  f'data/tcn-rotation/{match}-{setting}-first.csv'])
    require(all(path in locked['data'] for path in required_data), 'Missing frozen evaluation reference')
    for group in ('data', 'prepared_manifests'):
        for name, digest in locked[group].items():
            require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Unsafe path')
            require(sha(name) == digest, 'Frozen input changed: ' + name)
    split = json.loads(Path('experiments/core-development/split.json').read_text())
    require(tuple(split['development']) == IDS and not set(IDS).intersection(split['sealed']),
            'Five development split changed or overlaps sealed matches')
    membership = json.loads((R / 'membership.json').read_text())
    require(tuple(membership['development']) == IDS
            and membership['folds'] == {m: [n for n in IDS if n != m] for m in IDS}
            and membership['provider'] == 'idsse' and membership['pff_all_excluded']
            and not membership['final_fit_enabled']
            and set(membership['sealed_excluded']) == set(split['sealed']), 'Membership differs')
    for package, expected in json.loads(Path('experiments/tcn-2026-11-10/environment.json').read_text()).items():
        require(version(package) == expected, 'Dependency version changed: ' + package)
    signature = hashlib.sha256((sha(R / 'protocol.md') + sha(R / 'inputs.json')).encode()).hexdigest()
    return locked, signature


@contextmanager
def operation_lock():
    DATA.mkdir(parents=True, exist_ok=True)
    handles = []
    try:
        for directory in (Path('data/tcn-expanded'), DATA):
            handle = (directory / 'operation.lock').open('a+')
            handles.append(handle)
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError('Another compact-data or boundary-TCN operation is active') from error
        yield
    finally:
        for handle in reversed(handles):
            handle.close()


def run_checks():
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join([str(PROJECT / 'src'), str(PROJECT / 'scripts'),
                                      env.get('PYTHONPATH', '')])
    with (R / 'checks.txt').open('w') as log:
        for suite in ('tests', 'experiments/tcn-2026-11-10/tests',
                      'experiments/tcn-gap-2026-11-10/tests',
                      'experiments/tcn-rotation-2026-11-11/tests', str(R / 'tests')):
            log.write('\n' + suite + '\n'); log.flush()
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', suite, '-v'],
                                    stdout=log, stderr=subprocess.STDOUT, env=env)
            require(result.returncode == 0, 'User-run contracts failed; preserve checks.txt')
    print('Integrated contract checks passed.', flush=True)


def verify_compact_files(locked):
    expected_names = {'objects.npy', 'roles.npy', 'core.npy', 'gap_ball.npy',
                      'gap_core.npy', 'labels.npy', 'metadata.json'}
    for name, digest in locked['prepared_manifests'].items():
        require(sha(name) == digest, 'Prepared manifest changed: ' + name)
        directory = Path(name).parent
        manifest = json.loads(Path(name).read_text())
        require(set(manifest) == {'files'} and set(manifest['files']) == expected_names,
                'Unexpected compact manifest members')
        for filename, expected in manifest['files'].items():
            require(sha(directory / filename) == expected,
                    'Compact array/metadata changed: ' + str(directory / filename))


def verify_frozen_inputs(locked):
    for group in locked.values():
        for path, digest in group.items():
            require(sha(path) == digest, 'Registered input changed during execution: ' + path)
    verify_compact_files(locked)


def load_cases(locked, compact_case, filenames, valid_windows):
    verify_compact_files(locked)
    cases = []
    for match in IDS:
        directory = Path('data/tcn-expanded') / ('idsse-' + match)
        manifest = json.loads((directory / 'manifest.json').read_text())
        require(set(manifest) == {'files'} and set(manifest['files']) == set(filenames) | {'metadata.json'},
                'Unexpected compact manifest members')
        for name, digest in manifest['files'].items():
            require(sha(directory / name) == digest, 'Compact array/metadata changed: ' + str(directory / name))
        case = compact_case(directory)
        require(case.provider == 'idsse' and case.key == 'idsse-' + match
                and case.metadata['match'] == match, 'Compact case membership/provider changed')
        valid_windows([case])
        cases.append(case)
    return cases


def checkpoint_paths(match):
    return [MODELS / match / repeat / 'progress.pt' for repeat in ('first', 'repeat')]


def verify_fold(match, signature, architecture):
    path = R / 'evaluation' / (match + '.json')
    if not path.exists():
        return None
    value = json.loads(path.read_text())
    require(value['registration'] == signature and value['architecture'] == architecture,
            'Completed fold registration or architecture changed')
    require(value['training_matches'] == ['idsse-' + other for other in IDS if other != match],
            'Completed fold training membership changed')
    rows = value['rows']
    require(len(rows) == 2 and {(row['match'], row['condition']) for row in rows}
            == {(match, setting) for setting in SETTINGS}, 'Incomplete completed fold cells')
    require(value['repeated_training_exact'] and value['training_steps'] == STEPS
            and set(value['coverage']) == set(value['training_matches']),
            'Completed fold repeatability/budget/coverage incomplete')
    require(all(set(counts) == {'clean', 'gap'} and all(isinstance(n, int) and n >= 0
                    for n in counts.values()) for counts in value['coverage'].values())
            and all(sum(v.values()) > 0 for v in value['coverage'].values())
            and sum(sum(v.values()) for v in value['coverage'].values()) == STEPS * 8,
            'Completed fold sampling counts differ from frozen budget')
    losses = json.loads((R / 'evaluation' / (match + '-losses.json')).read_text())
    require(losses['not_validation_loss'] and len(losses['minibatch_losses']) == STEPS
            and all(math.isfinite(v) for v in losses['minibatch_losses'])
            and hashlib.sha256(json.dumps(losses['minibatch_losses']).encode()).hexdigest()
                == value['training_loss_sha256'], 'Completed training loss evidence changed')
    components = losses.get('loss_components', {})
    require(set(components) == {'class', 'boundary'}
            and all(len(v) == STEPS and all(math.isfinite(n) for n in v) for v in components.values())
            and all(abs(total - (main + .1 * auxiliary)) <= 1e-5
                    for total, main, auxiliary in zip(losses['minibatch_losses'],
                                                      components['class'], components['boundary']))
            and hashlib.sha256(json.dumps(components).encode()).hexdigest()
                == value['loss_components_sha256'], 'Completed loss components changed')
    require(set(value['checkpoint_hashes']) == {str(p) for p in checkpoint_paths(match)},
            'Completed checkpoint references changed')
    for checkpoint in checkpoint_paths(match):
        require(sha(checkpoint) == value['checkpoint_hashes'][str(checkpoint)], 'Completed checkpoint changed')
    for row in rows:
        require(row['reload_probabilities_equal'] and row['csv_bytes_equal_reload_batch4'],
                'Completed inference proof missing')
        for name in row['csv_paths']:
            require(sha(name) == row['csv_sha256'], 'Completed prediction CSV changed')
        require(len(row['csv_paths']) == 3 and len(set(row['csv_paths'])) == 3,
                'Missing or duplicated repeat CSV paths')
        source = f"data/tcn-rotation/{match}-{row['condition']}-first.csv"
        require(sha(source) == row['parent_csv_sha256'], 'Completed parent prediction changed')
        for arm in ('parent', 'candidate'):
            for metric in ('spellF1', 'macroF1'):
                metric_value = row[arm][metric]
                require(isinstance(metric_value, (int, float)) and math.isfinite(metric_value)
                        and 0 <= metric_value <= 1, 'Invalid recorded metric')
    return value


def calculate_gate(rows, np, promote):
    expected = {(match, setting) for match in IDS for setting in SETTINGS}
    require(len(rows) == 10 and {(row['match'], row['condition']) for row in rows} == expected,
            'Exactly ten unique held-out evaluation cells required')
    def paired(arm):
        return {match: tuple(float(np.mean([row[arm][metric] for row in rows if row['match'] == match]))
                            for metric in ('spellF1', 'macroF1')) for match in IDS}
    before, after = paired('parent'), paired('candidate')
    primary = {row['match']: float(row['candidate']['spellF1'] - row['parent']['spellF1'])
               for row in rows if row['condition'] == 'targetlike'}
    median = float(np.median(list(primary.values())))
    return dict(quality_eligible=bool(promote(before, after, True) and median >= .01),
                existing_gate=promote(before, after, True), primary_median_delta=median,
                primary_deltas=primary,
                paired_spell_deltas={m: after[m][0] - before[m][0] for m in IDS},
                paired_macro_deltas={m: after[m][1] - before[m][1] for m in IDS},
                matches_improved=sum(after[m][0] > before[m][0] for m in IDS),
                contract_checks_passed=True, repeated_training_exact=True,
                csv_repeatability_cases=10, clean_environment_verified=False,
                production_changed=False, sealed_opened=False, pff_holdout_opened=False)


def evaluate(cases, signature, locked, np, torch, model_module, train_fit, confirm_repeat, score, missing,
             decode, export_labels, promote, valid_windows, rotate180, average_views):
    results_dir = R / 'evaluation'; results_dir.mkdir(exist_ok=True)
    private = DATA / 'predictions'; private.mkdir(exist_ok=True)
    archive = json.loads(Path('experiments/tcn-rotation-2026-11-11/results.json').read_text())
    archived = {(row['match'], row['condition']): row for row in archive}
    require(len(archive) == 10 and set(archived) == {(m,c) for m in IDS for c in SETTINGS},
            'Incomplete parent score archive')
    scaler = np.zeros(model_module.WIDTH), np.ones(model_module.WIDTH)
    all_rows = []
    for held in IDS:
        check_date()
        completed = verify_fold(held, signature, model_module.ARCHITECTURE)
        if completed is not None:
            all_rows.extend(completed['rows'])
            print('Retained validated completed fold', held, flush=True)
            continue
        started = time.monotonic()
        training = [case for case in cases if case.key != 'idsse-' + held]
        require(len(training) == 4 and all(case.key != 'idsse-' + held for case in training),
                'Held-out training leakage')
        directory = MODELS / held
        first, losses, coverage = train_fit(training, directory / 'first', signature, steps=STEPS)
        check_date()
        second, repeated_losses, repeated_coverage = train_fit(training, directory / 'repeat', signature, steps=STEPS)
        confirm_repeat(first, second, losses, repeated_losses, coverage, repeated_coverage)
        saved = torch.load(directory / 'first/progress.pt', map_location='cpu', weights_only=True)
        repeated_saved = torch.load(directory / 'repeat/progress.pt', map_location='cpu', weights_only=True)
        components = saved['loss_components']
        require(components == repeated_saved['loss_components'], 'Repeated loss components differ')
        require(saved['step'] == STEPS and saved['identity']['matches'] == [case.key for case in training],
                'Checkpoint budget or membership differs')
        reloaded = model_module.TCN().cpu().eval()
        reloaded.load_state_dict(saved['state'], strict=True)
        rows = []
        held_case = next(case for case in cases if case.key == 'idsse-' + held)
        for setting in SETTINGS:
            with np.load(f'data/tcn-prepared/{held}-{setting}.npz', allow_pickle=False) as data:
                x, labels, blocks = data['x'], data['y'], data['blocks'].tolist()
            require(x.shape == (len(labels), model_module.WIDTH) and blocks == held_case.blocks,
                    'Evaluation dimensions/halves differ')
            encoded_labels = np.array([{'H':0,'A':1,'D':2,'X':-1}[str(v)] for v in labels], np.int8)
            require(np.array_equal(encoded_labels, held_case.labels), 'Cached evaluation labels differ')
            parent_path = f'data/tcn-rotation/{held}-{setting}-first.csv'
            parent = np.loadtxt(parent_path, delimiter=',', skiprows=1, usecols=1, dtype=str)
            require(len(parent) == len(labels) and set(np.unique(parent)) <= set('HADX'), 'Parent CSV malformed')
            parent_score = score(labels, parent, blocks)
            for metric in ('spellF1', 'macroF1'):
                require(abs(parent_score[metric] - archived[held,setting][metric]) <= 1e-12,
                        'Frozen parent metrics do not reproduce')
            rotated = rotate180(x)
            identity_prob = model_module.predict(first, x, blocks, scaler)
            rotated_prob = model_module.predict(first, rotated, blocks, scaler)
            reload_identity = model_module.predict(reloaded, x, blocks, scaler)
            reload_rotated = model_module.predict(reloaded, rotated, blocks, scaler)
            require(np.array_equal(identity_prob, reload_identity)
                    and np.array_equal(rotated_prob, reload_rotated),
                    'Reload probabilities differ in one or both views')
            first_prob = average_views(identity_prob, rotated_prob)
            reload_prob = average_views(reload_identity, reload_rotated)
            batch4_prob = average_views(model_module.predict(first, x, blocks, scaler, batch=4),
                                       model_module.predict(first, rotated, blocks, scaler, batch=4))
            predictions = [decode(first_prob, (1-np.eye(3))*16, blocks),
                           decode(reload_prob, (1-np.eye(3))*16, blocks),
                           decode(batch4_prob, (1-np.eye(3))*16, blocks)]
            paths = [private / f'{held}-{setting}-{tag}.csv' for tag in ('first','reload','batch4')]
            for path, prediction in zip(paths, predictions): export_labels(path, prediction, len(labels))
            digests = [sha(path) for path in paths]
            require(len(set(digests)) == 1, 'CSV bytes differ across reload/batch modes')
            rows.append(dict(match=held, condition=setting, parent=parent_score,
                             candidate=score(labels,predictions[0],blocks),
                             parent_missing_ball=missing(labels,parent,x[:,-4]==0),
                             candidate_missing_ball=missing(labels,predictions[0],x[:,-4]==0),
                             parent_csv_sha256=sha(parent_path), csv_sha256=digests[0],
                             csv_paths=[str(path) for path in paths], reload_probabilities_equal=True,
                             csv_bytes_equal_reload_batch4=True))
        available = {case.key: 0 for case in training}
        for index, _, count in valid_windows(training): available[training[index].key] += count
        checkpoints = {str(path):sha(path) for path in checkpoint_paths(held)}
        record = dict(registration=signature, architecture=model_module.ARCHITECTURE,
                      training_matches=[case.key for case in training], training_steps=STEPS,
                      repeated_training_exact=True, coverage=coverage, available_window_starts=available,
                      training_loss_sha256=hashlib.sha256(json.dumps(losses).encode()).hexdigest(),
                      loss_components_sha256=hashlib.sha256(json.dumps(components).encode()).hexdigest(),
                      checkpoint_hashes=checkpoints, rows=rows, seconds=time.monotonic()-started)
        write_json(results_dir / (held + '-losses.json'), {'minibatch_losses': losses, 'loss_components': components, 'not_validation_loss':True})
        write_json(results_dir / (held + '.json'), record)
        all_rows.extend(rows)
        print('Completed held-out match', held, flush=True)
    for held in IDS: require(verify_fold(held,signature,model_module.ARCHITECTURE) is not None, 'Missing completed fold')
    require(all_rows == [row for held in IDS for row in verify_fold(held,signature,model_module.ARCHITECTURE)['rows']],
            'Aggregate/fold rows differ')
    verify_frozen_inputs(locked)
    gate = calculate_gate(all_rows,np,promote)
    write_json(results_dir/'results.json',all_rows); write_json(results_dir/'gate.json',gate)
    require(calculate_gate(json.loads((results_dir/'results.json').read_text()),np,promote) == gate,
            'Saved aggregate gate differs')
    report = '# Boundary-supervised TCN development comparison\n\n|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|\n|---|---|---:|---:|---:|---:|\n'
    for row in all_rows:
        a,b=row['parent'],row['candidate']
        report += f"|{row['match']}|{row['condition']}|{a['spellF1']:.6f}|{b['spellF1']:.6f}|{a['macroF1']:.6f}|{b['macroF1']:.6f}|\n"
    (results_dir/'report.md').write_text(report+'\n```json\n'+json.dumps(gate,indent=2)+'\n```\n')
    return gate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true',required=True); parser.parse_args()
    os.chdir(PROJECT)
    locked, signature = registration()
    with operation_lock():
        run_checks()
        sys.path[:0] = [str(PROJECT/'src'), str(PROJECT/'scripts'), str(PROJECT/R),
                       str(PROJECT/'experiments/tcn-expanded-2026-11-10'),
                       str(PROJECT/'experiments/tcn-rotation-2026-11-11')]
        import numpy as np
        import torch
        import boundary_model
        from rotation import rotate180, average_views
        from boundary_training import train_fit, confirm_repeat
        from expanded_data import CompactCase, FILES, valid_windows
        from possession.core import promote
        from possession.decode import decode
        from possession.inputs import export_labels
        from review_frozen import score
        from evaluate_pff import missing
        boundary_model.configure()
        cases = load_cases(locked,CompactCase,FILES,valid_windows)
        for held in IDS: verify_fold(held,signature,boundary_model.ARCHITECTURE)
        gate = evaluate(cases,signature,locked,np,torch,boundary_model,train_fit,confirm_repeat,score,missing,
                        decode,export_labels,promote,valid_windows,rotate180,average_views)
        write_json(R/'decision.json',dict(quality_eligible=gate['quality_eligible'],
                   parent='gap_trained_short_context_tcn_rotation_50_50_penalty16',
                   architecture=boundary_model.ARCHITECTURE, production_changed=False,
                   clean_environment_verified=False, automatic_followup=False))
        print(json.dumps(gate,indent=2),flush=True)
        with Path('ball.md').open('a') as journal:
            journal.write('\nBoundary-supervised TCN development comparison recorded; production unchanged. '+json.dumps(gate)+'\n')


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        os.chdir(PROJECT)
        write_json(R/'last-failure.json',dict(error_type=type(error).__name__,message=str(error),production_changed=False))
        with Path('ball.md').open('a') as journal:
            journal.write('\nBoundary-supervised TCN stopped; preserve last-failure.json and review before resuming.\n')
        raise
