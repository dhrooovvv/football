"""User-run frozen A/B OOF diagnostic. No training, tuning or target input access."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time

for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
            'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
PROJECT = Path(__file__).resolve().parents[1]
R = Path('experiments/tcn-diagnostic-2026-11-13')
sys.path[:0] = [str(PROJECT/'scripts'), str(PROJECT/R)]
import run_tcn_missed as frozen
from diagnostic_contract import registration, require, sha, save, storage_guard, operation_lock


def csv_digest(labels):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['frame', 'label'])
    writer.writerows(enumerate(labels.tolist()))
    return hashlib.sha256(stream.getvalue().encode('utf-8')).hexdigest()


def read_archive(row, n, official):
    path = Path(row['csv_paths'][0])
    require(sha(path) == row['csv_sha256'], 'Archived prediction hash differs')
    frame = official.read_label_csv(path)
    require(official.validate_submission(frame, n) is None, 'Archived CSV invalid')
    return frame['label'].to_numpy()


def run_checks():
    path = R/'evaluation'/('checks-'+str(time.time_ns())+'.txt')
    with storage_guard():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as stream:
            env = os.environ.copy()
            env['PYTHONPATH'] = 'src:scripts:'+str(R)
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s',
                                     str(R/'tests'), '-v'], stdout=stream, stderr=subprocess.STDOUT, env=env)
    require(result.returncode == 0, 'Diagnostic checks failed; preserve '+str(path))
    return path


def cached_unit(path, signature):
    if not path.exists():
        return None
    value = json.loads(path.read_text())
    digest = value.pop('content_sha256', None)
    expected = hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()
    require(digest == expected and value['signature'] == signature and value['complete'] is True,
            'Cached unit changed or is incomplete')
    require(sha(value['checks_path']) == value['checks_sha256'], 'Cached checks evidence changed')
    value['content_sha256'] = digest
    return value


def complete_unit(path, value):
    value['content_sha256'] = hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()
    save(path, value)


def run():
    from diagnostics import analyze, paired_changes, recommendation
    signature, parent_signature = registration()
    archives = {}
    for trial in ('a', 'b'):
        bound, trial_signature = frozen.trial_identity(trial, parent_signature)
        _, rows, _ = frozen.verify_completed(trial, trial_signature, bound)
        archives[trial] = {(r['match'], r['condition']): r for r in rows}
    checks_path = run_checks()
    d = None
    all_cells, paired = [], []
    for trial in ('b', 'a'):
        for match in frozen.IDS:
            frozen.check_date()
            unit_path = R/'evaluation'/'cases'/f'{trial}-{match}.json'
            cached = cached_unit(unit_path, signature)
            if cached is not None:
                require(cached['trial'] == trial and cached['match'] == match, 'Cached unit membership differs')
                all_cells.extend(cached['cells']); paired.append(cached['paired'])
                print('Verified completed diagnostic', trial, match, flush=True)
                continue
            if d is None:
                d = frozen.dependencies()
            np = d['np']; official = d['official']
            models = [frozen.model_from(frozen.fit_path(trial, match, seed, 'first'), d) for seed in frozen.SEEDS]
            cells, records, previous_y, previous_blocks = [], {}, None, None
            for condition in frozen.SETTINGS:
                frozen.check_date()
                with np.load(f'data/tcn-prepared/{match}-{condition}.npz', allow_pickle=False) as data:
                    x, y, blocks = data['x'], data['y'], data['blocks'].tolist()
                require(x.shape == (len(y), d['model_code'].WIDTH), 'Prepared schema differs')
                if previous_y is not None:
                    require(np.array_equal(previous_y, y) and previous_blocks == blocks,
                            'Clean/corrupted labels or blocks differ')
                previous_y, previous_blocks = y.copy(), blocks
                archived = archives[trial][match, condition]
                pred = read_archive(archived, len(y), official)
                measured = d['metrics'](y, pred, blocks, d['score'], official, np)
                require(measured == archived['candidate'], 'Archived official scores do not reproduce')
                # A/B retained decoded CSVs, not probabilities. Stream one case, then discard.
                probabilities, views = frozen.infer_ensemble(models, x, blocks, d, batch=1)
                decoded = d['decode'](probabilities, (1-np.eye(3))*16, blocks)
                require(np.array_equal(decoded, pred) and csv_digest(decoded) == archived['csv_sha256'],
                        'Frozen model does not reproduce archived CSV bytes')
                analysis, records[condition] = analyze(y, pred, x[:, -4] == 0, probabilities, blocks, official)
                require(analysis['per_iou'] == measured['spell_per_iou']
                        and abs(analysis['spellF1']-measured['spellF1']) <= 1e-12,
                        'Diagnostic spell accounting differs from official scorer')
                cells.append(dict(trial=trial, match=match, condition=condition,
                    official=measured, analysis=analysis, archived_csv_sha256=archived['csv_sha256'],
                    archived_metrics_reproduced=True, inference_csv_bytes_reproduced=True))
                del probabilities, views, x, decoded
                print('Diagnosed', trial, match, condition, flush=True)
            changes = dict(trial=trial, match=match, per_iou=paired_changes(records['clean'], records['targetlike']))
            value = dict(signature=signature, complete=True, trial=trial, match=match,
                checks_path=str(checks_path), checks_sha256=sha(checks_path), cells=cells, paired=changes)
            complete_unit(unit_path, value)
            all_cells.extend(cells); paired.append(changes)
            del models, records
    registration()
    for trial in ('a', 'b'):
        bound, trial_signature = frozen.trial_identity(trial, parent_signature)
        frozen.verify_completed(trial, trial_signature, bound)
    require(len(all_cells) == 20 and len(paired) == 10, 'Incomplete diagnostic')
    result = dict(signature=signature, completed=True, cells=all_cells, clean_corrupted_pairing=paired,
        recommendation=recommendation(all_cells), selected_candidate='b', reference='a',
        training_performed=False, production_changed=False, target_accuracy='unknown', sealed_opened=False)
    save(R/'evaluation/results.json', result)
    report = '# Frozen A/B possession diagnostic\n\nAll scores reproduce the archive. No training or model selection.\n\n'
    report += '|Trial|Match|Setting|spellF1|macroF1|Missed at IoU .5|\n|---|---|---|---:|---:|---:|\n'
    for row in all_cells:
        report += f"|{row['trial']}|{row['match']}|{row['condition']}|{row['official']['spellF1']:.6f}|{row['official']['macroF1']:.6f}|{row['analysis']['missed_iou_05']}|\n"
    report += '\nConditional proposal and ranked associations:\n\n```json\n'+json.dumps(result['recommendation'], indent=2)+'\n```\n'
    report += '\nDetailed per-IoU precision/recall, duration/gap strata, overlapping associations, boundary shifts, dead/live quality and paired corruption losses are in results.json. Counts are not recoverable spellF1 gains. Argmax support is an association, not a causal decoder verdict. Target accuracy unknown. Stop for review; no intervention is authorized.\n'
    with storage_guard():
        (R/'evaluation/report.md').write_text(report)
    save(R/'evaluation/completion.json', dict(signature=signature, completed=True,
        results_sha256=sha(R/'evaluation/results.json'), report_sha256=sha(R/'evaluation/report.md'),
        units={str(p): sha(p) for p in sorted((R/'evaluation/cases').glob('*.json'))},
        production_changed=False, training_performed=False))
    print('Diagnostic complete. Stop and report done for review.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', required=True)
    parser.parse_args()
    os.chdir(PROJECT)
    with operation_lock():
        run()


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        os.chdir(PROJECT)
        try:
            save(R/'failures'/f'{time.time_ns()}.json', dict(error_type=type(error).__name__,
                message=str(error), production_changed=False, training_performed=False))
        except Exception:
            print('Could not save failure evidence; preserve terminal output.', file=sys.stderr)
        raise
