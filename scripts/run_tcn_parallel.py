"""User-run isolated attention and second-seed ensemble comparisons; external only."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

# Separate processes may run concurrently, each with one numerical compute thread.
for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'

PROJECT = Path(__file__).resolve().parents[1]
R = Path('experiments/tcn-parallel-2026-11-12')
DATA = Path('data/tcn-parallel')
MODELS = Path('models/tcn-parallel')
PARENT = Path('experiments/tcn-pretrain-2026-11-11')
sys.path.insert(0, str(PROJECT / R))
from parallel_contract import (IDS, SETTINGS, ARMS, require, sha, write_json,
                               check_date, registration, verify_hashes, gate, ordered_decision)


@contextmanager
def operation_lock(arm):
    directory = DATA / arm
    directory.mkdir(parents=True, exist_ok=True)
    handles = []
    try:
        # Multiple readers coexist; existing preprocessing writers request EX locks.
        for path, mode in ((Path('data/tcn-expanded/operation.lock'), fcntl.LOCK_SH),
                           (directory / 'operation.lock', fcntl.LOCK_EX)):
            handle = path.open('a+'); handles.append(handle)
            try: fcntl.flock(handle, mode | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError('A conflicting compact-data or same-arm operation is active') from error
        yield
    finally:
        for handle in reversed(handles): handle.close()


def checks(arm):
    directory = R / 'evaluation' / arm
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'checks.txt'
    if path.exists():
        path = directory / ('checks-resume-' + str(time.time_ns()) + '.txt')
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join((str(PROJECT / 'src'), str(PROJECT / 'scripts'),
                                       env.get('PYTHONPATH', '')))
    with path.open('w') as log:
        for folder in ('tests', 'experiments/tcn-2026-11-10/tests',
                       'experiments/tcn-gap-2026-11-10/tests',
                       'experiments/tcn-rotation-2026-11-11/tests',
                       'experiments/tcn-pretrain-2026-11-11/tests', str(R / 'tests')):
            log.write('\n' + folder + '\n'); log.flush()
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', folder, '-v'],
                                    stdout=log, stderr=subprocess.STDOUT, env=env)
            require(result.returncode == 0, 'Contracts failed; preserve ' + str(path))
    return str(path), sha(path)


def frozen_parent():
    archive = json.loads((PARENT / 'evaluation/control/results.json').read_text())
    index = {(v['match'], v['condition']): v for v in archive}
    require(len(archive) == 10 and set(index) == {(m, c) for m in IDS for c in SETTINGS},
            'Incomplete frozen parent archive')
    return index


def metrics(y, predicted, blocks, score, official, np):
    result = score(y, predicted, blocks)
    # Exactly the same valid-run/half separation as review_frozen.score.
    truth, guess = official.label_codes(y), official.label_codes(predicted)
    for _, stop in sorted(blocks[:-1], reverse=True):
        truth = np.insert(truth, int(stop), official.X)
        guess = np.insert(guess, int(stop), official.X)
    spells = official.spell_scores(truth, guess, official.valid_runs(truth))
    result['spell_per_iou'] = {str(k): v for k, v in spells['per_iou'].items()}
    result['true_spell_count'] = spells['n_gt']
    result['predicted_spell_count'] = spells['n_pred']
    require(abs(result['spellF1'] - spells['mean_f1']) <= 1e-12, 'Official metric adapters disagree')
    return result


def verify_fold(arm, match, signature, membership):
    path = R / 'evaluation' / arm / (match + '.json')
    if not path.exists(): return None
    value = json.loads(path.read_text())
    require(value['registration'] == signature and value['arm'] == arm
            and value['match'] == match and value['training_matches'] == membership['supervised_folds'][match]
            and value['training_steps'] == 40000 and value['repeated_training_exact'] is True,
            'Cached fold identity/budget differs')
    require(value['parent_reconstructed'] is True and value['contracts_passed'] is True,
            'Cached fold lacks correctness evidence')
    require(value['architecture'] == {
        'attention': 'original_motion_tcn_masked_team_self_attention_v1',
        'ensemble': 'original_motion_tcn_geometric_pretraining_head_v1'}[arm]
        and value['parameters'] == {'attention': 9917, 'ensemble': 9701}[arm],
        'Cached architecture/parameter identity differs')
    require(sha(value['checks_path']) == value['checks_sha256'], 'Recorded contracts log changed')
    expected_paths = {str(MODELS / arm / match / fit / 'progress.pt') for fit in ('first', 'repeat')}
    require(set(value['checkpoint_hashes']) == expected_paths, 'Wrong fold checkpoint paths')
    for name, digest in value['checkpoint_hashes'].items():
        require(sha(name) == digest, 'Cached fold checkpoint changed')
    loss = json.loads((R / 'evaluation' / arm / (match + '-losses.json')).read_text())
    require(loss['not_validation_loss'] and len(loss['minibatch_losses']) == 40000
            and all(math.isfinite(v) for v in loss['minibatch_losses'])
            and hashlib.sha256(json.dumps(loss['minibatch_losses']).encode()).hexdigest()
            == value['training_loss_sha256'], 'Cached loss evidence differs')
    for stage in ('stage1', 'stage2'):
        counts = value['coverage'][stage]; views = value['supervised_views'][stage]
        require(set(counts) == set(membership['supervised_folds'][match])
                and all(type(n) is int and n > 0 for n in counts.values())
                and sum(counts.values()) == 160000, 'Cached exposure differs')
        require(set(views) == {'clean', 'gap'} and all(type(n) is int and n > 0 for n in views.values())
                and sum(views.values()) == 160000, 'Cached gap exposure differs')
    require(value['coverage']['stage1'] == value['coverage']['stage2']
            and value['supervised_views']['stage1'] == value['supervised_views']['stage2'],
            'Stage-reset evidence differs')
    require(len(value['rows']) == 2 and {(v['match'], v['condition']) for v in value['rows']}
            == {(match, c) for c in SETTINGS}, 'Incomplete cached cells')
    parents = frozen_parent()
    for row in value['rows']:
        require(row['reload_probabilities_equal_both_views'] and row['csv_bytes_equal_reload_batch4'],
                'Cached inference proof failed')
        expected = [str(DATA / arm / 'predictions' / f'{match}-{row["condition"]}-{tag}.csv')
                    for tag in ('first', 'reload', 'batch4')]
        require(row['csv_paths'] == expected, 'Unexpected candidate CSV paths')
        for name in expected: require(sha(name) == row['csv_sha256'], 'Candidate CSV changed')
        parent = parents[match, row['condition']]
        require(row['parent_csv_sha256'] == parent['csv_sha256'], 'Frozen parent reference differs')
        require(sha(row['parent_reconstruction_path']) == parent['csv_sha256'],
                'Saved parent reconstruction CSV changed')
        for key, metric in parent['candidate'].items():
            require(row['parent'][key] == metric, 'Cached parent metric differs')
        for side in ('parent', 'candidate'):
            for key in ('spellF1', 'macroF1'):
                require(math.isfinite(row[side][key]) and 0 <= row[side][key] <= 1, 'Invalid metric')
            thresholds = row[side]['spell_per_iou']
            require(set(thresholds) == {'0.3', '0.4', '0.5', '0.6', '0.7'},
                    'Per-threshold spell metrics incomplete')
            for detail in thresholds.values():
                require(all(math.isfinite(detail[key]) and 0 <= detail[key] <= 1
                            for key in ('precision', 'recall', 'f1')),
                        'Invalid threshold metric')
                require(all(type(detail[key]) is int and detail[key] >= 0
                            for key in ('n_matched', 'n_spurious', 'n_missed')),
                        'Invalid spell-count evidence')
            require(abs(sum(v['f1'] for v in thresholds.values()) / 5 - row[side]['spellF1']) <= 1e-12,
                    'Per-threshold mean differs from official spellF1')
    return value


def completion(arm, signature, membership):
    path = R / 'evaluation' / arm / 'completion.json'
    require(path.exists(), 'Arm has not completed: ' + arm)
    record = json.loads(path.read_text())
    require(record['registration'] == signature and record['arm'] == arm
            and record['completed'] and record['contracts_passed'] and record['repeated_training_exact'],
            'Arm completion proof differs')
    folds = [verify_fold(arm, match, signature, membership) for match in IDS]
    require(all(folds), 'Missing completed fold')
    rows = [row for fold in folds for row in fold['rows']]
    results_path = R / 'evaluation' / arm / 'results.json'
    require(json.loads(results_path.read_text()) == rows and sha(results_path) == record['results_sha256'],
            'Arm results differ from completed fold evidence')
    require(record['fold_hashes'] == {m: sha(R / 'evaluation' / arm / (m + '.json')) for m in IDS},
            'Fold completion fingerprints changed')
    return rows


def run_arm(arm, locked, membership, signature):
    with operation_lock(arm):
        if (R / 'evaluation' / arm / 'completion.json').exists():
            completion(arm, signature, membership)
            print('Arm already complete; preserved evidence:', arm, flush=True)
            return
        checks_path, checks_sha = checks(arm)
        sys.path[:0] = [str(PROJECT / 'src'), str(PROJECT / 'scripts'), str(PROJECT / R),
                       str(PROJECT / 'experiments/tcn-pretrain-2026-11-11'),
                       str(PROJECT / 'experiments/tcn-expanded-2026-11-10'),
                       str(PROJECT / 'experiments/tcn-rotation-2026-11-11'),
                       str(PROJECT / 'experiments/tcn-winner-slot-audit-2026-11-12'),
                       str(PROJECT / 'reference/more-than-a-hack-2027-main/evaluation')]
        import numpy as np
        import torch
        import possession_metrics as official
        import parallel_model as model_code
        from parallel_training import train_fit, validate_saved, expected_identity, confirm_repeat
        from expanded_data import CompactCase
        from pretrain_model import TCN as ParentTCN
        from winner_contract import validate_control
        from rotation import rotate180, average_views
        from possession.decode import decode
        from possession.inputs import export_labels
        from review_frozen import score
        from evaluate_pff import missing
        model_code.configure()
        parents = frozen_parent()
        old_membership = json.loads((PARENT / 'membership.json').read_text())
        parent_signature = hashlib.sha256((sha(PARENT / 'protocol.md') + sha(PARENT / 'inputs.json')).encode()).hexdigest()
        cases = {m: CompactCase(Path('data/tcn-expanded') / ('idsse-' + m)) for m in IDS}
        directory = R / 'evaluation' / arm
        predictions = DATA / arm / 'predictions'; predictions.mkdir(parents=True, exist_ok=True)

        def infer(model, x, blocks, batch=1):
            scaler = np.zeros(model_code.WIDTH), np.ones(model_code.WIDTH)
            views = tuple(model_code.predict(model, values, blocks, scaler, batch=batch)
                          for values in (x, rotate180(x)))
            return average_views(*views), views

        def load_candidate(path, match):
            saved = torch.load(path, map_location='cpu', weights_only=True)
            validate_saved(saved, expected_identity(signature, arm, match))
            model = model_code.model_for_arm(arm).cpu().eval()
            model.load_state_dict(saved['state'], strict=True)
            return model

        def parent_model(match):
            path = f'models/tcn-pretrain/evaluation/control/{match}/first/progress.pt'
            record = json.loads((PARENT / 'evaluation/control' / (match + '.json')).read_text())
            saved = torch.load(path, map_location='cpu', weights_only=True)
            validate_control(saved, match, parent_signature, old_membership, record)
            require(record['checkpoint_hashes'][path] == sha(path), 'Wrong current-parent checkpoint')
            model = ParentTCN().cpu().eval(); model.load_state_dict(saved['state'], strict=True)
            return model

        # Reconstruct all ten references before the first expensive new fit.
        # Only tiny parent models survive this phase; feature arrays are released.
        parent_models = {}
        for match in IDS:
            check_date()
            parent = parent_model(match)
            for condition in SETTINGS:
                with np.load(f'data/tcn-prepared/{match}-{condition}.npz', allow_pickle=False) as data:
                    px, py, pb = data['x'], data['y'], data['blocks'].tolist()
                pp, _ = infer(parent, px, pb)
                predicted = decode(pp, (1 - np.eye(3)) * 16, pb)
                preflight = predictions / f'{match}-{condition}-parent-preflight.csv'
                export_labels(preflight, predicted, len(py))
                old = parents[match, condition]
                require(sha(preflight) == old['csv_sha256'], 'Parent preflight CSV reconstruction differs')
                measured = metrics(py, predicted, pb, score, official, np)
                require(all(measured[k] == v for k, v in old['candidate'].items()),
                        'Parent preflight aggregate metrics differ')
                del px, py, pb, pp, predicted
            parent_models[match] = parent
        all_rows = []
        for match in IDS:
            check_date()
            cached = verify_fold(arm, match, signature, membership)
            if cached:
                all_rows.extend(cached['rows']); continue
            started = time.monotonic()
            parent = parent_models[match]
            training = [cases[m] for m in IDS if m != match]
            require([v.key for v in training] == membership['supervised_folds'][match], 'Training membership differs')
            fits = MODELS / arm / match
            first = train_fit(training, fits / 'first', signature, arm, match)
            train_fit(training, fits / 'repeat', signature, arm, match)
            paths = [fits / fit / 'progress.pt' for fit in ('first', 'repeat')]
            saved = [torch.load(path, map_location='cpu', weights_only=True) for path in paths]
            for value in saved: validate_saved(value, expected_identity(signature, arm, match))
            confirm_repeat(*saved)
            reloaded = load_candidate(paths[0], match)
            fold_rows = []
            clean_labels, clean_blocks = None, None
            for condition in SETTINGS:
                check_date()
                with np.load(f'data/tcn-prepared/{match}-{condition}.npz', allow_pickle=False) as data:
                    x, y, blocks = data['x'], data['y'], data['blocks'].tolist()
                require(x.shape == (len(y), model_code.WIDTH), 'Evaluation schema differs')
                if condition == 'clean': clean_labels, clean_blocks = y.copy(), blocks
                else: require(np.array_equal(y, clean_labels) and blocks == clean_blocks,
                              'Corruption changed labels or half boundaries')
                parent_prob, _ = infer(parent, x, blocks)
                parent_pred = decode(parent_prob, (1 - np.eye(3)) * 16, blocks)
                parent_path = predictions / f'{match}-{condition}-parent-reconstruction.csv'
                export_labels(parent_path, parent_pred, len(y))
                old = parents[match, condition]
                require(sha(parent_path) == old['csv_sha256'], 'Current40k parent CSV reconstruction differs')
                parent_metrics = metrics(y, parent_pred, blocks, score, official, np)
                for key, value in old['candidate'].items():
                    require(parent_metrics[key] == value, 'Parent aggregate metrics differ')
                outputs, probability_views = [], []
                for model, batch in ((first, 1), (reloaded, 1), (first, 4)):
                    candidate_prob, views = infer(model, x, blocks, batch)
                    probability_views.append(views)
                    probabilities = average_views(parent_prob, candidate_prob) if arm == 'ensemble' else candidate_prob
                    outputs.append(decode(probabilities, (1 - np.eye(3)) * 16, blocks))
                require(all(np.array_equal(a, b) for a, b in zip(probability_views[0], probability_views[1])),
                        'Both-view reload probabilities differ')
                csv_paths = [predictions / f'{match}-{condition}-{tag}.csv'
                             for tag in ('first', 'reload', 'batch4')]
                for path, predicted in zip(csv_paths, outputs): export_labels(path, predicted, len(y))
                require(len({sha(path) for path in csv_paths}) == 1, 'Candidate reload/batch CSV bytes differ')
                candidate_metrics = metrics(y, outputs[0], blocks, score, official, np)
                fold_rows.append(dict(match=match, condition=condition, parent=parent_metrics,
                    candidate=candidate_metrics, parent_csv_sha256=old['csv_sha256'],
                    parent_reconstruction_path=str(parent_path),
                    parent_missing_ball=missing(y, parent_pred, x[:, -4] == 0),
                    candidate_missing_ball=missing(y, outputs[0], x[:, -4] == 0),
                    csv_paths=[str(path) for path in csv_paths], csv_sha256=sha(csv_paths[0]),
                    reload_probabilities_equal_both_views=True, csv_bytes_equal_reload_batch4=True))
                print('Completed', arm, match, condition, flush=True)
                del x, y, blocks, parent_prob, parent_pred, outputs, probability_views
            loss_hash = hashlib.sha256(json.dumps(saved[0]['losses']).encode()).hexdigest()
            write_json(directory / (match + '-losses.json'),
                       dict(minibatch_losses=saved[0]['losses'], not_validation_loss=True))
            record = dict(registration=signature, arm=arm, match=match,
                architecture=model_code.ARCHITECTURES[arm], parameters=model_code.PARAMETERS[arm],
                training_matches=membership['supervised_folds'][match], training_steps=40000,
                repeated_training_exact=True, parent_reconstructed=True, contracts_passed=True,
                checks_path=checks_path, checks_sha256=checks_sha,
                checkpoint_hashes={str(path): sha(path) for path in paths},
                coverage=saved[0]['coverage'], supervised_views=saved[0]['supervised_views'],
                training_loss_sha256=loss_hash, rows=fold_rows,
                training_stage_seconds={fit: value['stage_seconds'] for fit, value in zip(('first', 'repeat'), saved)},
                seconds=time.monotonic() - started)
            write_json(directory / (match + '.json'), record)
            verify_fold(arm, match, signature, membership)
            all_rows.extend(fold_rows)
            write_json(directory / 'results-partial.json', all_rows)
        require(len(all_rows) == 10, 'Incomplete arm results')
        all_rows = [row for match in IDS for row in verify_fold(arm, match, signature, membership)['rows']]
        verify_hashes(locked)
        write_json(directory / 'results.json', all_rows)
        before = [dict(match=v['match'], condition=v['condition'], **v['parent']) for v in all_rows]
        after = [dict(match=v['match'], condition=v['condition'], **v['candidate']) for v in all_rows]
        write_json(directory / 'screening-gate.json', gate(before, after))
        report = '# ' + arm + ': frozen-parent comparison\n\nIndependent screen only; final ordered decision requires both arms. No automatic production promotion.\n\n|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|\n|---|---|---:|---:|---:|---:|\n'
        for row in all_rows:
            report += f"|{row['match']}|{row['condition']}|{row['parent']['spellF1']:.6f}|{row['candidate']['spellF1']:.6f}|{row['parent']['macroF1']:.6f}|{row['candidate']['macroF1']:.6f}|\n"
        report += '\nPer-threshold precision/recall/F1, errors and missing-ball quality are in results.json. Loss histories are training evidence, never validation scores. Reused-five-match evidence is not target accuracy; protected matches remain untouched.\n'
        (directory / 'report.md').write_text(report)
        write_json(directory / 'completion.json', dict(completed=True, arm=arm, registration=signature,
            contracts_passed=True, repeated_training_exact=True, case_count=10,
            results_sha256=sha(directory / 'results.json'),
            fold_hashes={m: sha(directory / (m + '.json')) for m in IDS},
            code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            production_changed=False, target_accuracy='unknown'))
        completion(arm, signature, membership)
        print('Arm complete:', arm, '; run finalization only after both arms finish.', flush=True)


def finalize(locked, membership, signature):
    with operation_lock('finalize'), operation_lock('attention'), operation_lock('ensemble'):
        destination = R / 'ordered-decision.json'
        require(not destination.exists(), 'Ordered decision already exists; preserve evidence')
        completed = {arm: completion(arm, signature, membership) for arm in ARMS}
        parent = [dict(match=row['match'], condition=row['condition'], **row['parent'])
                  for row in completed['attention']]
        other = [dict(match=row['match'], condition=row['condition'], **row['parent'])
                 for row in completed['ensemble']]
        require(parent == other, 'The independently run arms used different parent evidence')
        candidates = {arm: [dict(match=row['match'], condition=row['condition'], **row['candidate'])
                            for row in completed[arm]] for arm in ARMS}
        decision = ordered_decision(parent, candidates['attention'], candidates['ensemble'])
        decision.update(registration=signature, both_arms_completed=True,
                        selection_requires_human_review=True, clean_environment_verified=False,
                        source_result_hashes={arm: sha(R / 'evaluation' / arm / 'results.json') for arm in ARMS})
        verify_hashes(locked)
        write_json(destination, decision)
        print(json.dumps(decision, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--arm', choices=ARMS)
    choice.add_argument('--finalize', action='store_true')
    parser.add_argument('--run', action='store_true', required=True)
    args = parser.parse_args()
    os.chdir(PROJECT)
    locked, membership, signature = registration()
    if args.finalize:
        finalize(locked, membership, signature)
    else:
        run_arm(args.arm, locked, membership, signature)


if __name__ == '__main__':
    try: main()
    except (Exception, KeyboardInterrupt) as error:
        os.chdir(PROJECT)
        # The requested arm determines the isolated failure path; never overwrite another arm.
        arm = sys.argv[sys.argv.index('--arm') + 1] if '--arm' in sys.argv else 'finalize'
        if arm not in (*ARMS, 'finalize'): arm = 'invalid'
        write_json(R / 'evaluation' / arm / ('failure-' + str(time.time_ns()) + '.json'),
                   dict(error_type=type(error).__name__, message=str(error), production_changed=False))
        raise
