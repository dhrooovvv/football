"""User-run frozen temporal recovery diagnostic; no new candidate or training."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from importlib.metadata import version

for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
            'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
PROJECT = Path(__file__).resolve().parents[1]
ROOT = Path('experiments/temporal-recovery-audit-2026-11-15')
sys.path[:0] = [str(PROJECT/'scripts'), str(PROJECT/ROOT)]
import run_tcn_hybrid as hybrid
from hybrid_contract import (require, sha, load, committed_bytes, registration,
    stage_signature, check_date, storage_guard, check_storage)


def verify():
    check_date()  # Improvement diagnosis stops at the November16 freeze.
    locked = load(ROOT/'inputs.json')
    require(set(locked) == {'code', 'evidence'}, 'Incomplete diagnostic lock schema')
    require({str(ROOT/name) for name in ('protocol.md', 'membership.json', 'recovery.py',
                'tests/test_recovery.py')} | {'scripts/audit_temporal_recovery.py',
                'docs/run-temporal-recovery-audit.md'} <= set(locked['code']),
            'Incomplete diagnostic source lock')
    for group, entries in locked.items():
        require(group in ('code', 'evidence'), 'Unexpected lock group')
        for name, digest in entries.items():
            p = Path(name)
            require(not p.is_absolute() and '..' not in p.parts, 'Unsafe lock path')
            require(sha(p) == digest, 'Changed registered bytes: '+name)
            if group == 'code':
                committed_bytes(p)
    committed_bytes(ROOT/'inputs.json')
    membership = load(ROOT/'membership.json')
    require(membership == dict(development=list(hybrid.IDS),
        folds={m: ['idsse-'+n for n in hybrid.IDS if n != m] for m in hybrid.IDS},
        sealed_excluded=['J03WQQ', 'J03WR9'], target_excluded=True), 'Diagnostic membership differs')
    environment = load('experiments/tcn-winner-release-2026-11-12/environment-snapshot.json')
    require(platform.python_version() == environment['python'] and platform.system() == environment['system']
            and platform.machine() == environment['machine'], 'Locked Python/platform differs')
    for package, expected in environment['packages'].items():
        require(version(package) == expected, 'Locked package differs: '+package)
    _, _, base = registration(training=False)
    return hashlib.sha256((sha(ROOT/'protocol.md')+sha(ROOT/'inputs.json')).encode()).hexdigest(), base


def write(path, value):
    # The new root is outside historical artifact enumerations: reserve its entire
    # allowance in addition to historical artifacts, and cap the root separately.
    content = value if isinstance(value, str) else json.dumps(value, indent=2, allow_nan=False)+'\n'
    used = sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
    require(used+len(content.encode()) < 32*1024**2, 'Diagnostic exceeds32MiB; preserve evidence')
    with storage_guard(reserve=32*1024**2):
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix('.tmp')
        temp.write_text(content); temp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, action='store_true')
    parser.parse_args()
    os.chdir(PROJECT)
    signature, base = verify()
    directory = ROOT/'evaluation'
    directory.mkdir(exist_ok=True)
    # One process owns this diagnostic; no conflict with the original fit workers.
    import fcntl
    with (directory/'operation.lock').open('a+') as guard:
        fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(not (directory/'results.json').exists(), 'Completed diagnostic exists; review it')
        check_storage(reserve=32*1024**2)
        if not (directory/'checks-status.json').exists():
            log = directory/f'checks-{time.time_ns()}.txt'
            with log.open('w') as stream:
                outcome = subprocess.run([sys.executable, '-m', 'unittest', 'discover',
                    '-s', str(ROOT/'tests'), '-v'], stdout=stream, stderr=subprocess.STDOUT)
            require(outcome.returncode == 0, 'Diagnostic checks failed; preserve log')
            write(directory/'checks-status.json',
                  dict(passed=True, signature=signature, path=str(log), sha256=sha(log)))
        checks = load(directory/'checks-status.json')
        log = Path(checks['path'])
        require(log.parent == directory and log.name.startswith('checks-') and log.suffix == '.txt',
                'Unsafe checks log path')
        require(checks == dict(passed=True, signature=signature, path=str(log), sha256=sha(log)),
                'Checks log changed')
        d = hybrid.dependencies()
        import recovery
        import diagnostics
        np = d['np']; official = d['official']
        # Frozen original results and all repeated-fit proofs must still verify.
        stage_info = {}
        for stage in ('temporal', 'graph'):
            bound, stage_sig = stage_signature(stage, base)
            done, rows, _ = hybrid.verify_completed(stage, stage_sig, bound)
            stage_info[stage] = (bound, stage_sig, {(r['match'], r['condition']): r for r in rows})
        bound, stage_sig, archives = stage_info['temporal']
        cells = []
        for match in hybrid.IDS:
            check_date()
            unit = directory/(match+'.json')
            if unit.exists():
                cached = load(unit)
                content = {k:v for k,v in cached.items() if k != 'content_sha256'}
                require(cached['signature'] == signature and cached['match'] == match
                        and hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
                        == cached['content_sha256'], 'Cached cell changed')
                cells.extend(cached['cells']); continue
            members = [hybrid.load_checkpoint('temporal', match, seed, stage_sig, d) for seed in hybrid.SEEDS]
            rows = []; previous = None
            for condition in hybrid.SETTINGS:
                check_date()
                with np.load(f'data/tcn-prepared/{match}-{condition}.npz', allow_pickle=False) as data:
                    x, y, blocks = data['x'], data['y'], data['blocks'].tolist()
                if previous is not None:
                    require(np.array_equal(y, previous[0]) and blocks == previous[1], 'Views changed labels/halves')
                previous = (y.copy(), blocks)
                path, meta_path = hybrid.cache_paths('temporal', match, match, condition, 'evaluation')
                meta = load(meta_path)
                expected = dict(signature=stage_sig, binding=bound, stage='temporal', held_out=match,
                    case=match, role='evaluation', view=condition,
                    source_sha256=sha(f'data/tcn-prepared/{match}-{condition}.npz'),
                    training_matches=['idsse-'+m for m in hybrid.IDS if m != match])
                require(meta['identity'] == expected and sha(path) == meta['sha256'], 'Parent OOF cache changed')
                parent = np.load(path, mmap_mode='r', allow_pickle=False)
                temporal, member_probs = hybrid.ensemble_prediction(members, x, parent, blocks, d, return_members=True)
                again = hybrid.ensemble_prediction(members, x, parent, blocks, d, batch=4)
                predictions = [d['decode'](p, (1-np.eye(3))*16, blocks) for p in (parent, temporal)]
                batch_pred = d['decode'](again, (1-np.eye(3))*16, blocks)
                require(hybrid.csv_digest(batch_pred) == hybrid.csv_digest(predictions[1]),
                        'Batch CSV differs')
                old = archives[match, condition]
                for tag, pred, metric, digest in (
                    ('parent', predictions[0], old['parent'], old['parent_csv_sha256']),
                    ('temporal', predictions[1], old['candidate'], old['csv_sha256'])):
                    require(hybrid.csv_digest(pred) == digest and
                        d['metrics'](y, pred, blocks, d['score'], official, np) == metric,
                        'Archived '+tag+' CSV/scores do not reproduce')
                records = recovery.spell_records(y, *predictions, parent, temporal, member_probs,
                    x[:, -4] == 0, blocks, official, diagnostics)
                rows.append(dict(match=match, condition=condition, archive_reproduced=True,
                    parent=old['parent'], temporal=old['candidate'], summary=recovery.summarize(records),
                    external_spell_records=records))
                print('Diagnosed frozen temporal', match, condition, flush=True)
                del x, parent, temporal, member_probs, again, batch_pred
            value = dict(signature=signature, match=match, cells=rows)
            value['content_sha256'] = hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
            write(unit, value); cells.extend(rows)
            del members
        graph = []
        _, graph_sig, _ = stage_info['graph']
        for match in hybrid.IDS:
            for seed in hybrid.SEEDS:
                check_date()
                saved = d['torch'].load(hybrid.fit_path('graph', match, seed), map_location='cpu', weights_only=True)
                identity = d['hybrid_training'].expected_identity(graph_sig, 'graph', seed, match)
                d['hybrid_training'].validate_saved(saved, identity)
                proof = load(hybrid.proof_path('graph', match, seed))
                require(hashlib.sha256(json.dumps(saved['losses']).encode()).hexdigest() == proof['training_loss_sha256']
                    and hashlib.sha256(json.dumps(saved['component_losses']).encode()).hexdigest()
                    == proof['component_loss_sha256'], 'Graph loss evidence changed')
                graph.append(dict(match=match, seed=seed, training_only=True,
                    losses=recovery.loss_summary(saved['losses']),
                    components={k: recovery.loss_summary(v) for k,v in saved['component_losses'].items()
                                if k in ('cross_entropy', 'segment_soft_iou')}))
                del saved
        verify()
        consistency = {condition: {s: dict(
            auc_above_half=sum(r['summary']['signals'][s]['recovered_vs_introduced_spurious_auc'] is not None
                and r['summary']['signals'][s]['recovered_vs_introduced_spurious_auc'] > .5
                for r in cells if r['condition'] == condition),
            auc_below_half=sum(r['summary']['signals'][s]['recovered_vs_introduced_spurious_auc'] is not None
                and r['summary']['signals'][s]['recovered_vs_introduced_spurious_auc'] < .5
                for r in cells if r['condition'] == condition)) for s in recovery.SIGNALS}
            for condition in hybrid.SETTINGS}
        report = '# Frozen temporal recovery audit\n\nExploratory development evidence only. '
        report += 'All parent/temporal CSV hashes and official scores reproduced before interpretation. '
        report += 'No candidate tested or training performed.\n\n'
        report += '|Match|Setting|Parent spellF1|Temporal spellF1|Recovered|Introduced spurious|Parent-margin AUC|Temporal-margin AUC|Agreement AUC|\n'
        report += '|---|---|---:|---:|---:|---:|---:|---:|---:|\n'
        for row in cells:
            summary = row['summary']; counts = summary['counts']
            values = [summary['signals'][s]['recovered_vs_introduced_spurious_auc'] for s in recovery.SIGNALS]
            formatted = ['NA' if v is None else f'{v:.4f}' for v in values]
            report += (f"|{row['match']}|{row['condition']}|{row['parent']['spellF1']:.6f}|"
                f"{row['temporal']['spellF1']:.6f}|{counts.get('recovered',0)}|"
                f"{counts.get('introduced_spurious',0)}|"+'|'.join(formatted)+'|\n')
        report += '\n## Graph training-only trend\n\n'
        report += '|Fold|Seed|Stage|First1000 loss|Last1000 loss|Last5000 minus preceding5000|\n|---|---:|---:|---:|---:|---:|\n'
        for row in graph:
            for stage, trend in enumerate(row['losses'], 1):
                report += (f"|{row['match']}|{row['seed']}|{stage}|{trend['first_1000_mean']:.6f}|"
                    f"{trend['last_1000_mean']:.6f}|{trend['late_5000_change']:.6f}|\n")
        report += ('\nAUC and spell counts are not recoverable spellF1 gains. Inspect all match denominators, '
            'contrary cases and clean/corrupted consistency before proposing a rule. Training loss is not '
            'a held-out learning curve and cannot establish a benefit from longer graph training. '
            'No automatic thresholds, model change or third trial. Stop for review before one separate '
            'prospectively registered correction rule. Selected Trial B and production unchanged. '
            'Sealed matches untouched; target accuracy unknown.\n')
        write(directory/'report.md', report)
        write(directory/'results.json', dict(signature=signature, complete=True, cells=cells,
            report_sha256=sha(directory/'report.md'),
            signal_consistency=consistency, graph_training_loss=graph,
            interpretation='Exploratory, reused development labels; AUC is not a recoverable spellF1 gain. '
                'Training loss cannot establish held-out benefit from longer graph training.',
            candidate_tested=False, training_performed=False, production_changed=False,
            target_accuracy='unknown', sealed_opened=False, next_step='Review before registering one fixed correction rule'))
        print('Diagnostic complete. No model promoted or new training started. Report done for review.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        os.chdir(PROJECT)
        try:
            write(ROOT/'failures'/f'{time.time_ns()}.json',
                  dict(error_type=type(error).__name__, message=str(error),
                       training_performed=False, production_changed=False))
        except Exception:
            print('Could not save failure evidence; preserve terminal output.', file=sys.stderr)
        raise
