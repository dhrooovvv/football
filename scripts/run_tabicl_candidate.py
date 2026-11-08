"""Conditional, preregistered TabICL-only and fixed 50/50 blend comparison.

Implementation only until uncapped admission passes and --protocol names an
unchanged, git-committed scored supplement. All model artifacts stay in data/.
This script reports development gates; it never changes production.
"""
import os
for _key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_key] = '1'

import argparse
import gc
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

R = Path('experiments/tabicl-scored-2026-11-08')
OUT = Path('data/tabicl-candidate')
PREPARED = Path('data/external/prepared')
DIAG = Path('data/diagnostics-review')
WEIGHT = Path('data/tabicl/model.ckpt')
SEED = 20261106
QUERY_CHUNK = 16384
LABELS = ('H', 'A', 'D')
EXPECTED_IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
EXECUTION_STARTED = False
PARAMS = dict(n_estimators=1, softmax_temperature=1., random_state=SEED,
              n_jobs=1, device='cpu', use_amp=False, use_fa3=False,
              offload_mode=False, kv_cache=False, model_path=str(WEIGHT),
              allow_auto_download=False)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(name, value):
    path = R / name
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False))
    temporary.replace(path)


def require_execution_authority(protocol):
    """Do not accidentally turn draft code into an unregistered experiment."""
    from datetime import datetime, date
    from zoneinfo import ZoneInfo
    if datetime.now(ZoneInfo('Asia/Kolkata')).date() > date(2026, 11, 13):
        raise RuntimeError('Research freeze has passed; scoring is not authorized')
    protocol = Path(protocol)
    relative = protocol.resolve().relative_to(Path.cwd().resolve()).as_posix()
    committed = subprocess.check_output(['git', 'show', 'HEAD:' + relative])
    if committed != protocol.read_bytes():
        raise RuntimeError('Scored protocol must be committed unchanged before execution')
    admission_dir = Path('experiments/tabicl-uncapped-2026-11-08')
    admission = json.loads((admission_dir / 'admission.json').read_text())
    actual = json.loads((admission_dir / 'actual.json').read_text())
    if not (admission['passed'] and actual['probabilities_equal'] and actual['csv_equal']):
        raise RuntimeError('Full-context uncapped admission has not passed')
    source = json.loads((admission_dir / 'weight-source.json').read_text())
    if sha(WEIGHT) != source['sha256']:
        raise RuntimeError('Pinned checkpoint hash changed')
    if QUERY_CHUNK != 16384:
        raise RuntimeError('Query chunk changed from fixed pre-score design')
    return {'protocol': relative, 'protocol_sha256': sha(protocol),
            'protocol_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            'weight_source': source, 'query_chunk': QUERY_CHUNK}


def configure():
    import numpy as np
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.mkldnn.enabled = False
    np.random.seed(SEED)
    torch.manual_seed(SEED)


def context(ids, heldout):
    import numpy as np
    xs, ys, rows = [], [], {}
    for match in ids:
        if match == heldout:
            continue
        path = PREPARED / (match + '.npz')
        with np.load(path) as data:
            indices = np.arange(0, len(data['y']), 5)
            indices = indices[data['y'][indices] != 'X']
            xs.append(data['x'][indices])
            ys.append(data['y'][indices])
            rows[match] = {'rows': len(indices), 'prepared_sha256': sha(path)}
    return np.concatenate(xs), np.concatenate(ys), rows


def case_features(match, condition):
    import numpy as np
    path = PREPARED / (match + '.npz') if condition == 'clean' else DIAG / (match + '-targetlike.npz')
    with np.load(path) as data:
        return data['x'].copy()


def normalise(probabilities):
    import numpy as np
    p = np.asarray(probabilities, dtype=np.float64)
    if p.ndim != 2 or p.shape[1] != 3 or not np.isfinite(p).all() or (p < 0).any():
        raise ValueError('Invalid H/A/D probabilities')
    sums = p.sum(axis=1, keepdims=True)
    if (sums <= 0).any() or not np.allclose(sums, 1., atol=1e-5, rtol=1e-5):
        raise ValueError('Invalid probability row sums')
    return p / sums


def predict(model, x, tag):
    import numpy as np
    order = [list(model.classes_).index(c) for c in LABELS]
    output = np.empty((len(x), 3), dtype=np.float64)
    for start in range(0, len(x), QUERY_CHUNK):
        stop = min(len(x), start + QUERY_CHUNK)
        output[start:stop] = normalise(model.predict_proba(x[start:stop])[:, order])
        print(f'{tag}: predicted {stop}/{len(x)}', flush=True)
    return output


def arm_probabilities(cat, tab):
    import numpy as np
    # Keep frozen parent emissions byte-for-byte numerically unchanged.
    parent = np.asarray(cat, dtype=np.float64)
    return {'parent': parent, 'tabicl': tab,
            'blend': normalise(.5 * parent + .5 * tab)}


def decoded_csvs(match, condition, stage, cat, tab, blocks):
    import numpy as np
    from possession.decode import decode
    from possession.inputs import export_labels
    hashes = {}
    for arm, probability in arm_probabilities(cat, tab).items():
        # Decode concatenated probabilities once per HALF, never per query chunk.
        labels = decode(probability, (1 - np.eye(3)) * 16, blocks)
        path = OUT / f'{match}-{condition}-{arm}-{stage}.csv'
        export_labels(path, labels, len(labels))
        hashes[arm] = sha(path)
    return hashes


def missing_quality(y, predicted, mask):
    import numpy as np
    valid = (y != 'X') & mask
    g, q = y[valid] == 'D', predicted[valid] == 'D'
    tp, fp = int((g & q).sum()), int((~g & q).sum())
    fn, tn = int((g & ~q).sum()), int((~g & ~q).sum())
    ratio = lambda a, b: a / b if b else None
    return {'frames': int(valid.sum()), 'true_D': int(g.sum()), 'true_live': int((~g).sum()),
            'TP_D': tp, 'FP_D': fp, 'FN_D': fn, 'TN_D': tn,
            'D_f1': ratio(2 * tp, 2 * tp + fp + fn),
            'live_f1': ratio(2 * tn, 2 * tn + fp + fn),
            'D_precision': ratio(tp, tp + fp), 'D_recall': ratio(tp, tp + fn),
            'live_recall': ratio(tn, tn + fp), 'predicted_D_share': ratio(tp + fp, len(g))}


def measure(y, predicted, blocks, x):
    import numpy as np
    sys.path.insert(0, str(Path('reference/more-than-a-hack-2027-main/evaluation').resolve()))
    import possession_metrics as metrics
    g, p = metrics.label_codes(y), metrics.label_codes(predicted)
    for _, end in sorted(blocks[:-1], reverse=True):
        g = np.insert(g, int(end), metrics.X)
        p = np.insert(p, int(end), metrics.X)
    result = metrics.evaluate(g, p, bootstrap_n=0)
    return {'spellF1': result['spell_f1_mean'], 'macroF1': result['macro_f1'],
            'missing_ball': missing_quality(y, predicted, x[:, 5] == 0)}


def gate(reference, candidate, ids, tests_pass, determinism_pass):
    import numpy as np
    from possession.core import promote
    def paired(rows):
        return {m: tuple(np.mean([[r['spellF1'], r['macroF1']]
                                for r in rows if r['match'] == m], axis=0)) for m in ids}
    before, after = paired(reference), paired(candidate)
    spell = {m: after[m][0] - before[m][0] for m in ids}
    macro = {m: after[m][1] - before[m][1] for m in ids}
    corrupted = {m: next(r['spellF1'] for r in candidate if r['match'] == m and r['condition'] == 'targetlike')
                   - next(r['spellF1'] for r in reference if r['match'] == m and r['condition'] == 'targetlike')
                 for m in ids}
    existing = promote(before, after, tests_pass)
    primary = float(np.median(list(corrupted.values())))
    return {'development_gate_pass': bool(existing and primary >= .01 and determinism_pass),
            'existing_gate': existing, 'primary_median_delta': primary,
            'paired_spell_deltas': spell, 'paired_macro_deltas': macro,
            'primary_deltas': corrupted, 'matches_improved': int(sum(v > 0 for v in spell.values())),
            'tests_pass': tests_pass, 'determinism_pass': determinism_pass,
            'production_promotion': False,
            'production_promotion_requires': 'integration, official validation, repeated CSV and clean-environment reproduction'}


def main():
    global EXECUTION_STARTED
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', required=True, help='Exact committed scored supplement; no default approval')
    args = parser.parse_args()
    provenance = require_execution_authority(args.protocol)
    if R.exists() and any(R.glob('*.json')):
        raise RuntimeError('Existing scored results require review; no silent overwrite/resume')
    EXECUTION_STARTED = True
    import numpy as np
    from tabicl import TabICLClassifier
    from possession.decode import decode
    # Fail before expensive inference if the unchanged scorer's dependencies are absent.
    scorer_path = Path('reference/more-than-a-hack-2027-main/evaluation/possession_metrics.py')
    sys.path.insert(0, str(scorer_path.parent.resolve()))
    import possession_metrics  # noqa: F401; includes the official pandas dependency.
    provenance['reference_scorer_sha256'] = sha(scorer_path)
    provenance['split_sha256'] = sha('experiments/core-development/split.json')
    configure()
    R.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    ids = json.loads(Path('experiments/core-development/split.json').read_text())['development']
    if tuple(ids) != EXPECTED_IDS:
        raise ValueError('Original ordered development matches required; sealed matches forbidden')
    provenance.update(params=PARAMS, class_order=LABELS, match_order=ids)
    write('provenance.json', provenance)
    determinism, costs, input_hashes = [], [], {}
    for match in ids:
        x_train, y_train, training = context(ids, match)
        input_hashes[match] = {'training': training, 'conditions': {}}
        model_path = OUT / (match + '.pkl')
        stage_hashes = {}
        for stage in ('first', 'reload', 'refit'):
            start = time.monotonic()
            if stage == 'reload':
                model = TabICLClassifier.load(model_path, device='cpu')  # Newly generated local file only.
            else:
                model = TabICLClassifier(**PARAMS)
                model.fit(x_train, y_train)
                if stage == 'first':
                    model.save(model_path, save_model_weights=False,
                               save_training_data=True, save_kv_cache=False)
            for condition in ('clean', 'targetlike'):
                x = case_features(match, condition)
                tab = predict(model, x, f'{match}/{condition}/{stage}')
                saved = OUT / f'{match}-{condition}-probs.npz'
                if stage == 'first':
                    np.savez_compressed(saved, p=tab)
                else:
                    with np.load(saved) as first:
                        if not np.array_equal(tab, first['p']):
                            raise AssertionError(f'{stage} probabilities differ: {match}/{condition}')
                with np.load(DIAG / f'{match}-{condition}-probs.npz') as d:
                    cat = d['p']
                if cat.shape != tab.shape:
                    raise ValueError('Frozen parent probability shape mismatch')
                with np.load(PREPARED / (match + '.npz')) as d:
                    blocks = d['blocks'].tolist()
                hashes = decoded_csvs(match, condition, stage, cat, tab, blocks)
                if stage == 'first':
                    stage_hashes[condition] = hashes
                    feature_path = PREPARED / (match + '.npz') if condition == 'clean' else DIAG / (match + '-targetlike.npz')
                    input_hashes[match]['conditions'][condition] = {'feature_sha256': sha(feature_path),
                        'parent_probabilities_sha256': sha(DIAG / f'{match}-{condition}-probs.npz'),
                        'candidate_probabilities_sha256': sha(saved)}
                elif hashes != stage_hashes[condition]:
                    raise AssertionError(f'{stage} CSV bytes differ: {match}/{condition}')
                determinism.append({'match': match, 'condition': condition, 'stage': stage,
                                    'probabilities_equal_to_first': True, 'csv_sha256': hashes})
                write('determinism.json', determinism)
                del x, cat, tab
                gc.collect()
            costs.append({'match': match, 'stage': stage, 'context_rows': len(y_train),
                          'seconds': time.monotonic() - start, 'saved_model_sha256': sha(model_path)})
            write('cost.json', costs)
            write('input-hashes.json', input_hashes)
            del model
            gc.collect()
        del x_train, y_train
        gc.collect()
        print('Verified all stages', match, flush=True)

    # No quality score is computed until every planned repeat/reload check passes.
    rows = []
    for match in ids:
        with np.load(PREPARED / (match + '.npz')) as d:
            y, blocks = d['y'], d['blocks'].tolist()
        for condition in ('clean', 'targetlike'):
            x = case_features(match, condition)
            with np.load(DIAG / f'{match}-{condition}-probs.npz') as d:
                cat = d['p']
            with np.load(OUT / f'{match}-{condition}-probs.npz') as d:
                tab = d['p']
            for arm, probability in arm_probabilities(cat, tab).items():
                predicted = decode(probability, (1 - np.eye(3)) * 16, blocks)
                rows.append({'match': match, 'condition': condition, 'arm': arm,
                             **measure(y, predicted, blocks, x)})
    write('results.json', rows)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-q'],
                           capture_output=True, text=True)
    (R / 'production-tests.txt').write_text(tests.stdout + tests.stderr)
    by_arm = {arm: [r for r in rows if r['arm'] == arm] for arm in ('parent', 'tabicl', 'blend')}
    standalone = gate(by_arm['parent'], by_arm['tabicl'], ids, tests.returncode == 0, True)
    reference = 'tabicl' if standalone['development_gate_pass'] else 'parent'
    blended = gate(by_arm[reference], by_arm['blend'], ids, tests.returncode == 0, True)
    decision = {'standalone_vs_parent': standalone, 'blend_reference': reference,
                'blend_vs_current_best': blended,
                'blend_vs_original_parent': gate(by_arm['parent'], by_arm['blend'], ids, tests.returncode == 0, True),
                'development_selected': 'blend' if blended['development_gate_pass'] else reference,
                'production_changed': False, 'sealed_opened': False, 'target_accuracy': 'unknown'}
    write('gate.json', decision)
    print(json.dumps(decision), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Operational failures are not silently converted to metric rejections.
        if EXECUTION_STARTED and R.exists():
            write('failure.json', {'type': type(error).__name__, 'message': str(error),
                                   'production_changed': False})
        raise
