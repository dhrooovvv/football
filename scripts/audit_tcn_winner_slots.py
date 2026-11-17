"""User-run slot diagnostic for the actual40k-reset rotation TCN; no training."""
import argparse
from datetime import date, datetime
import fcntl
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
R = Path('experiments/tcn-winner-slot-audit-2026-11-12')
OUT = Path('data/tcn-winner-slot-audit')
PARENT = Path('experiments/tcn-pretrain-2026-11-11')
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')


def require(ok, reason):
    if not ok: raise RuntimeError(reason)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def save(name, value):
    path = R / name
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def authority():
    require(datetime.now(ZoneInfo('Asia/Kolkata')).date() < date(2026, 11, 16), 'Research frozen')
    lock = json.loads((R / 'inputs.json').read_text())
    must_commit = ['scripts/audit_tcn_winner_slots.py', str(R / 'protocol.md'),
                   str(R / 'slot_transforms.py'), str(R / 'tests/test_slots.py'),
                   str(R / 'winner_contract.py'), str(R / 'tests/test_winner_contract.py'),
                   str(R / 'requirements.txt'), 'docs/run-tcn-winner-slot-audit.md']
    inherited = json.loads((PARENT/'inputs.json').read_text())
    require(set(inherited) == {'code','data','prepared_manifests'}, 'Wrong parent registration')
    require(all(name in lock and lock[name] == digest for name,digest in inherited['code'].items()),
            'Original source fingerprints not preserved')
    for required in [*must_commit,
                     'experiments/tcn-2026-11-10/environment.json',
                     str(PARENT/'inputs.json'), str(PARENT/'membership.json'),
                     str(PARENT/'evaluation/control/results.json'),
                     'experiments/core-development/split.json']:
        require(required in lock, 'Incomplete registration: ' + required)
    for m in IDS:
        require(str(PARENT/'evaluation/control'/(m+'.json')) in lock, 'Unpinned fold evidence')
        for repeat in ('first','repeat'):
            require(f'models/tcn-pretrain/evaluation/control/{m}/{repeat}/progress.pt' in lock,
                    'Unpinned40k control checkpoint')
        for c in ('clean', 'targetlike'):
            require(f'data/tcn-prepared/{m}-{c}.npz' in lock, 'Unpinned evaluation input')
            for tag in ('first','reload','batch4'):
                require(f'data/tcn-pretrain/predictions/control/{m}-{c}-{tag}.csv' in lock,
                        'Unpinned parent CSV')
    for name, digest in lock.items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Unsafe registered path')
        require(sha(name) == digest, 'Hash changed: ' + name)
    for name in [str(R / 'inputs.json'), *lock]:
        tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', name], capture_output=True).returncode == 0
        if tracked or name == str(R / 'inputs.json') or name in must_commit:
            result = subprocess.run(['git', 'show', 'HEAD:' + name], capture_output=True)
            require(result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == sha(name),
                    'Registration/source must be committed: ' + name)
    for name, expected in json.loads(Path('experiments/tcn-2026-11-10/environment.json').read_text()).items():
        require(version(name) == expected, 'Runtime version changed: ' + name)
    split = json.loads(Path('experiments/core-development/split.json').read_text())
    require(tuple(split['development']) == IDS and not set(IDS) & set(split['sealed']), 'Invalid split')
    membership = json.loads((PARENT/'membership.json').read_text())
    require(membership['development'] == list(IDS) and membership['sealed_excluded'] == split['sealed']
            and membership['supervised_folds'] == {m:['idsse-'+n for n in IDS if n!=m] for m in IDS}
            and membership['target_excluded'] and membership['held_out_even_unlabelled_excluded']
            and not membership['final_fit_enabled'], 'Original protected membership changed')
    return lock, membership


def checks():
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join([str(ROOT / 'src'), str(ROOT / 'scripts'),
                                      env.get('PYTHONPATH', '')])
    with (R / 'checks.txt').open('w') as log:
        for folder in ['tests', 'experiments/tcn-2026-11-10/tests',
                       'experiments/tcn-gap-2026-11-10/tests',
                       'experiments/tcn-rotation-2026-11-11/tests',
                       str(PARENT/'tests'), str(R / 'tests')]:
            log.write('\n' + folder + '\n'); log.flush()
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', folder, '-q'],
                                    stdout=log, stderr=subprocess.STDOUT, env=env)
            require(result.returncode == 0, 'Contracts failed; see checks.txt')


def main():
    os.chdir(ROOT)
    sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts'),
                   str(ROOT / PARENT), str(ROOT / R),
                   str(ROOT / 'experiments/tcn-rotation-2026-11-11')]
    lock, membership = authority()
    handle=(OUT.parent/'tcn-winner-slot-audit.operation.lock').open('a+')
    try: fcntl.flock(handle,fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        raise RuntimeError('Another current-winner slot diagnostic is active') from error
    require(not OUT.exists() and not (R / 'started.json').exists(), 'Existing attempt: preserve and request review')
    checks()
    import numpy as np
    import torch
    from pretrain_model import TCN, WIDTH, configure, predict
    from slot_transforms import permute_slots
    from winner_contract import validate_control
    from rotation import rotate180, average_views
    from possession.decode import decode
    from possession.inputs import export_labels
    from review_frozen import score
    from evaluate_pff import missing
    configure()
    archive = json.loads((PARENT/'evaluation/control/results.json').read_text())
    archived = {(v['match'], v['condition']): v for v in archive}
    expected = {(m,c) for m in IDS for c in ('clean','targetlike')}
    require(len(archive) == 10 and set(archived) == expected, 'Incomplete parent archive')
    OUT.mkdir(parents=True)
    save('started.json', {'git_commit': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                         'time': datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(), 'inputs_sha256': sha(R / 'inputs.json'),
                         'diagnostic_only': True, 'training_executed': False})
    original_signature = hashlib.sha256((sha(PARENT/'protocol.md')+sha(PARENT/'inputs.json')).encode()).hexdigest()
    def load(path, match, record):
        d = torch.load(path, map_location='cpu', weights_only=True)
        validate_control(d, match, original_signature, membership, record)
        m = TCN().cpu().eval(); m.load_state_dict(d['state'], strict=True)
        return m, (np.zeros(WIDTH), np.ones(WIDTH))
    def infer(model, values, blocks, scaler, batch=1):
        p = predict(model,values,blocks,scaler,batch=batch)
        q = predict(model,rotate180(values),blocks,scaler,batch=batch)
        return average_views(p,q), (p,q)
    def verified_inference(model, reloaded, values, blocks, scaler, reload_scaler, stem):
        prob, views = infer(model,values,blocks,scaler)
        repeat_prob, repeat_views = infer(reloaded,values,blocks,reload_scaler)
        require(all(np.array_equal(a,b) for a,b in zip(views,repeat_views))
                and np.array_equal(prob,repeat_prob), 'Both-view reload probabilities differ')
        batch_prob, _ = infer(model,values,blocks,scaler,batch=4)
        predictions = [decode(p,(1-np.eye(3))*16,blocks) for p in (prob,repeat_prob,batch_prob)]
        paths = [OUT/f'{stem}-{tag}.csv' for tag in ('first','reload','batch4')]
        for path,prediction in zip(paths,predictions): export_labels(path,prediction,len(values))
        require(len({sha(p) for p in paths}) == 1, 'Repeat CSV differs')
        return prob,predictions[0],paths
    rows, deterministic, timings = [], [], []
    for i, match in enumerate(IDS):
        started = time.monotonic()
        require(datetime.now(ZoneInfo('Asia/Kolkata')).date() < date(2026,11,16), 'Research frozen')
        record = json.loads((PARENT/'evaluation/control'/(match+'.json')).read_text())
        checkpoint = f'models/tcn-pretrain/evaluation/control/{match}/first/progress.pt'
        require(record['checkpoint_hashes'][checkpoint] == sha(checkpoint), 'Parent checkpoint hash differs')
        for name,digest in record['checkpoint_hashes'].items():
            require(name in lock and lock[name] == digest and sha(name)==digest, 'Archived checkpoint changed')
        require(record['rows'] == [v for v in archive if v['match']==match], 'Fold and aggregate archive differ')
        model, scaler = load(checkpoint,match,record)
        reload, rs = load(checkpoint,match,record)
        clean_y, clean_blocks = None, None
        for condition in ('clean', 'targetlike'):
            with np.load(f'data/tcn-prepared/{match}-{condition}.npz', allow_pickle=False) as d:
                x, y, blocks = d['x'], d['y'], d['blocks'].tolist()
            require(x.shape == (len(y),WIDTH), 'Invalid input shape')
            if condition == 'clean': clean_y, clean_blocks = y.copy(), blocks
            else: require(np.array_equal(y,clean_y) and blocks == clean_blocks, 'Corruption changed labels')
            base_prob,base,base_paths = verified_inference(model,reload,x,blocks,scaler,rs,f'{match}-{condition}-parent')
            reference=archived[match,condition]
            expected_paths=[f'data/tcn-pretrain/predictions/control/{match}-{condition}-{tag}.csv'
                            for tag in ('first','reload','batch4')]
            require(reference['csv_paths']==expected_paths and reference['reload_probabilities_equal']
                    and reference['csv_bytes_equal_reload_batch4'], 'Archived current-parent reference differs')
            require(all(sha(p)==reference['csv_sha256'] for p in expected_paths+base_paths),
                    'Current40k parent CSV reconstruction differs')
            measured = score(y,base,blocks)
            for metric in ('spellF1','macroF1'):
                require(abs(measured[metric]-reference['candidate'][metric]) <= 1e-12, 'Parent score differs')
            rows.append({'match':match,'condition':condition,'variant':'parent',**measured,
                         'missing_ball':missing(y,base,x[:,-4]==0)})
            deterministic.append({'match':match,'condition':condition,'variant':'parent',
                                  'reload_probabilities_equal':True,'csv_bytes_equal_reload_batch4':True,
                                  'csv_sha256':sha(base_paths[0]),'csv_paths':[str(p) for p in base_paths]})
            for variant,seed in [('static',20261111+i),('rederived_identity',20261111+i),('dynamic',20261111+i+100000)]:
                changed = permute_slots(x,blocks,seed,variant)
                prob,pred,paths = verified_inference(model,reload,changed,blocks,scaler,rs,f'{match}-{condition}-{variant}')
                rows.append({'match':match,'condition':condition,'variant':variant,'seed':seed,
                             **score(y,pred,blocks),'missing_ball':missing(y,pred,changed[:,-4]==0),
                             'max_probability_difference_vs_parent':float(np.max(np.abs(prob-base_prob))),
                             'probabilities_close_atol1e_6_rtol1e_5':bool(np.allclose(prob,base_prob,atol=1e-6,rtol=1e-5)),
                             'label_differences_vs_parent':int((pred!=base).sum())})
                if variant == 'rederived_identity':
                    identity_prob, identity_pred = prob.copy(), pred.copy()
                elif variant == 'dynamic':
                    rows[-1]['max_probability_difference_vs_rederived_identity'] = float(np.max(np.abs(prob-identity_prob)))
                    rows[-1]['label_differences_vs_rederived_identity'] = int((pred!=identity_pred).sum())
                deterministic.append({'match':match,'condition':condition,'variant':variant,
                                      'reload_probabilities_equal':True,'csv_bytes_equal_reload_batch4':True,
                                      'csv_sha256':sha(paths[0]),'csv_paths':[str(p) for p in paths]})
            save('results.json',rows);save('determinism.json',deterministic)
            print('Completed',match,condition,flush=True)
        timings.append({'match':match,'seconds':time.monotonic()-started});save('cost.json',timings)
    require(len(rows)==40 and {(v['match'],v['condition'],v['variant']) for v in rows} ==
            {(m,c,v) for m,c in expected for v in ('parent','static','rederived_identity','dynamic')}, 'Incomplete diagnostic')
    require(len(deterministic) == 40 and {(v['match'], v['condition'], v['variant']) for v in deterministic} ==
            {(m, c, v) for m, c in expected for v in ('parent','static', 'rederived_identity', 'dynamic')},
            'Incomplete repeatability records')
    index = {(v['match'], v['condition'], v['variant']): v for v in rows}
    controls = []
    for match, condition in sorted(expected):
        reference = index[match, condition, 'parent']
        rounding = index[match, condition, 'rederived_identity']
        for variant in ('parent', 'static', 'rederived_identity', 'dynamic'):
            value = index[match, condition, variant]
            for metric in ('spellF1', 'macroF1'):
                value[metric + '_delta_vs_parent'] = value[metric] - reference[metric]
                value[metric + '_delta_vs_rederived_identity'] = value[metric] - rounding[metric]
        static = index[match, condition, 'static']
        controls.append({'match': match, 'condition': condition,
                         'static_probabilities_within_tolerance': static['probabilities_close_atol1e_6_rtol1e_5'],
                         'static_max_probability_difference': static['max_probability_difference_vs_parent'],
                         'static_label_differences': static['label_differences_vs_parent'],
                         'rederivation_max_probability_difference': rounding['max_probability_difference_vs_parent'],
                         'rederivation_label_differences': rounding['label_differences_vs_parent'],
                         'diagnostic_only': True})
    save('results.json', rows)
    save('controls.json', controls)
    for p,h in lock.items(): require(sha(p)==h, 'Input changed during execution: '+p)
    report = '# Current40k winner: external identity-churn diagnostic\n\nWorst-case synthetic stress, not target accuracy or a model-selection gate. Frozen recipe: original521 motion TCN, staged40k control, equal original/180degree probability average, decoder16.\n\n|Match|Setting|Variant|spellF1|macroF1|Changed labels|\n|---|---|---|---:|---:|---:|\n'
    for v in rows:
        report += f"|{v['match']}|{v['condition']}|{v['variant']}|{v['spellF1']:.6f}|{v['macroF1']:.6f}|{v.get('label_differences_vs_parent',0)}|\n"
    report += ('\nFull metric deltas versus both parent and rederived-identity are in results.json; '
               'numerical control status is in controls.json. Static tolerance failure requires '
               'investigation before interpreting churn. No target-calibrated corruption or promotion threshold.\n')
    (R/'report.md').write_text(report)
    save('decision.json',{'completed':True,'diagnostic_only':True,'quality_selection_performed':False,'model_promoted':False,
                          'winner':'control40k_reset_rotation_penalty16','parent_reproduced':True,
                          'repeatability_passed':True,
                          'training_executed':False,'production_changed':False,'target_accuracy':'unknown',
                          'tests_pass':True,'repeatability_cases':len(deterministic),
                          'parent_reconstruction_cases':10,'inputs_sha256':sha(R/'inputs.json'),
                          'registration':hashlib.sha256((sha(R/'protocol.md')+sha(R/'inputs.json')).encode()).hexdigest(),
                          'results_sha256':sha(R/'results.json'),'controls_sha256':sha(R/'controls.json'),
                          'determinism_sha256':sha(R/'determinism.json'),
                          'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                          'static_controls_within_tolerance':all(c['static_probabilities_within_tolerance'] for c in controls),
                          'interpretation_requires_control_review':True})
    print('Diagnostic complete; no model-selection or production decision made.',flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true',required=True);p.parse_args()
    try: main()
    except Exception as error:
        os.chdir(ROOT)
        if R.exists(): save('last-failure.json',{'type':type(error).__name__,'message':str(error),'production_changed':False})
        raise
