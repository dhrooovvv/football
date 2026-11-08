"""Manual 30,000-row / 11-core TabICL quality screen; no automatic promotion.

Implementation only until uncapped and cache admissions pass and --protocol names an
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

R = Path('experiments/tabicl-medium-2026-11-08')
OUT = Path('data/tabicl-medium')
PREPARED = Path('data/external/prepared')
DIAG = Path('data/diagnostics-review')
WEIGHT = Path('data/tabicl/model.ckpt')
SEED = 20261106
QUERY_CHUNK = 16384
LABELS = ('H', 'A', 'D')
EXPECTED_IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
EXECUTION_STARTED = False
PARAMS = dict(n_estimators=1, softmax_temperature=1., random_state=SEED,
              n_jobs=11, device='cpu', use_amp=False, use_fa3=False,
              offload_mode=False, kv_cache=True, model_path=str(WEIGHT),
              allow_auto_download=False)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b''):
            digest.update(block)
    return digest.hexdigest()


def write(name, value):
    path = R / name
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False))
    temporary.replace(path)


def verify_locked_inputs():
    """Registration metadata is allowed; it must pin every permitted input."""
    manifest_path = R / 'locked-inputs.json'
    relative = manifest_path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    committed = subprocess.check_output(['git', 'show', 'HEAD:' + relative])
    raw = manifest_path.read_bytes()
    if committed != raw:
        raise RuntimeError('Locked-input manifest must be committed unchanged before execution')
    locked = json.loads(raw)
    expected = {
        'scripts/run_tabicl_medium.py',
        'reference/more-than-a-hack-2027-main/evaluation/possession_metrics.py',
        'src/possession/core.py', 'src/possession/decode.py', 'src/possession/inputs.py',
        'experiments/core-development/split.json',
    }
    for match in EXPECTED_IDS:
        expected.update({
            f'data/external/prepared/{match}.npz',
            f'data/diagnostics-review/{match}-targetlike.npz',
            f'data/diagnostics-review/{match}-clean-probs.npz',
            f'data/diagnostics-review/{match}-targetlike-probs.npz',
        })
    if not isinstance(locked, dict) or set(locked) != expected:
        raise RuntimeError('Locked-input manifest must cover exactly the registered code and five development inputs')
    for name, digest in locked.items():
        if (not isinstance(digest, str) or len(digest) != 64
                or any(c not in '0123456789abcdef' for c in digest)):
            raise RuntimeError('Invalid registered SHA256: ' + name)
        if sha(name) != digest:
            raise RuntimeError('Locked input changed before execution: ' + name)
    return {'locked_inputs_manifest': relative,
            'locked_inputs_sha256': hashlib.sha256(raw).hexdigest(),
            'locked_input_files_verified': len(locked)}


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
    locked_provenance = verify_locked_inputs()
    admission_dir = Path('experiments/tabicl-uncapped-2026-11-08')
    admission = json.loads((admission_dir / 'admission.json').read_text())
    actual = json.loads((admission_dir / 'actual.json').read_text())
    if not (admission['passed'] and actual['probabilities_equal'] and actual['csv_equal']):
        raise RuntimeError('Full-context uncapped admission has not passed')
    source = json.loads((admission_dir / 'weight-source.json').read_text())
    if sha(WEIGHT) != source['sha256']:
        raise RuntimeError('Pinned checkpoint hash changed')
    cache_dir = Path('experiments/tabicl-cache-2026-11-08')
    cache_admission = json.loads((cache_dir / 'admission.json').read_text())
    cache_actual = json.loads((cache_dir / 'actual.json').read_text())
    cache_provenance = json.loads((cache_dir / 'provenance.json').read_text())
    if not (cache_admission['passed'] and cache_actual['passed']
            and cache_admission['fixed_query_rows'] == QUERY_CHUNK):
        raise RuntimeError('Cache equivalence/repeatability admission has not passed')
    if cache_provenance['source']['sha256'] != source['sha256']:
        raise RuntimeError('Cache admission checkpoint differs')
    if QUERY_CHUNK != 16384:
        raise RuntimeError('Query chunk changed from fixed pre-score design')
    return {**locked_provenance, 'protocol': relative, 'protocol_sha256': sha(protocol),
            'protocol_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            'weight_source': source, 'query_chunk': QUERY_CHUNK,
            'cache_admission_sha256': sha(cache_dir / 'admission.json'),
            'cache_dependencies': cache_provenance['dependencies']}


def configure():
    import numpy as np
    import torch
    torch.set_num_threads(11)
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
    x, y = np.concatenate(xs), np.concatenate(ys)
    chosen = np.sort(np.random.default_rng(SEED).choice(len(y), min(30000, len(y)), replace=False))
    OUT.mkdir(parents=True, exist_ok=True)
    np.save(OUT / (heldout + '-training-indices.npy'), chosen)
    rows['_sampling'] = {'pool_rows': len(y), 'selected_rows': len(chosen), 'seed': SEED,
                         'indices_sha256': hashlib.sha256(chosen.tobytes()).hexdigest()}
    return x[chosen], y[chosen], rows


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


def gate(reference, candidate, ids, tests_pass, determinism_pass=None):
    """Quality eligibility precedes expensive full-case reproducibility proof."""
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
    quality = bool(existing and primary >= .01)
    promotable = bool(quality and determinism_pass is True)
    return {'quality_eligible': quality, 'development_promotable': promotable,
            'phase': ('DEVELOPMENT_PROMOTABLE' if promotable else 'QUALITY_ELIGIBLE'
                      if quality and determinism_pass is None else 'QUALITY_REJECTED'
                      if not quality else 'DETERMINISM_FAILED'),
            'existing_gate': existing, 'primary_median_delta': primary,
            'paired_spell_deltas': spell, 'paired_macro_deltas': macro,
            'primary_deltas': corrupted, 'matches_improved': int(sum(v > 0 for v in spell.values())),
            'tests_pass': tests_pass, 'determinism_all_cases_pass': determinism_pass,
            'prior_single_thread_cache_contract': True, 'current_repeatability_verified': False, 'production_promotion': False,
            'production_promotion_requires': 'integration, official validation, repeated CSV and clean-environment reproduction'}


def decisions(rows, ids, tests_pass, determinism_pass=None):
    by_arm = {arm: [r for r in rows if r['arm'] == arm] for arm in ('parent', 'tabicl', 'blend')}
    standalone = gate(by_arm['parent'], by_arm['tabicl'], ids, tests_pass, determinism_pass)
    # Freeze the comparison reference using QUALITY, even if a later shared
    # emission determinism failure makes both neural arms nonpromotable.
    reference = 'tabicl' if standalone['quality_eligible'] else 'parent'
    blended = gate(by_arm[reference], by_arm['blend'], ids, tests_pass, determinism_pass)
    original = gate(by_arm['parent'], by_arm['blend'], ids, tests_pass, determinism_pass)
    selected = 'blend' if blended['development_promotable'] else (
        'tabicl' if standalone['development_promotable'] else 'parent')
    return {'standalone_vs_parent': standalone, 'blend_reference': reference,
            'blend_vs_current_best': blended, 'blend_vs_original_parent': original,
            'development_selected': selected,
            'determinism_all_cases_pass': determinism_pass,
            'production_changed': False, 'sealed_opened': False, 'target_accuracy': 'unknown'}


def fit_cached(x, y, tag):
    from tabicl import TabICLClassifier
    print(f'{tag}: cached fit/warm-up start, rows={len(x)}', flush=True)
    model = TabICLClassifier(**PARAMS)
    model.fit(x, y)
    print(f'{tag}: cached fit/warm-up complete', flush=True)
    return model


def first_inference(ids):
    """Single initial fit and two fixed-condition predictions per held-out match."""
    import numpy as np
    costs, inputs, first_hashes = [], {}, {}
    for match in ids:
        start = time.monotonic()
        x_train, y_train, training = context(ids, match)
        inputs[match] = {'training': training, 'conditions': {}}
        first_hashes[match] = {}
        model = fit_cached(x_train, y_train, match + '/first')
        print(f'{match}: cache stays in memory; no model checkpoint is written', flush=True)
        # Quality screening only: do not serialize large caches.
        model_hash = None
        for condition in ('clean', 'targetlike'):
            x = case_features(match, condition)
            tab = predict(model, x, f'{match}/{condition}/first')
            saved = OUT / f'{match}-{condition}-probs.npz'
            np.savez_compressed(saved, p=tab)
            with np.load(DIAG / f'{match}-{condition}-probs.npz') as d:
                cat = d['p']
            if cat.shape != tab.shape:
                raise ValueError('Frozen parent probability shape mismatch')
            with np.load(PREPARED / (match + '.npz')) as d:
                blocks = d['blocks'].tolist()
            first_hashes[match][condition] = decoded_csvs(match, condition, 'first', cat, tab, blocks)
            feature_path = PREPARED / (match + '.npz') if condition == 'clean' else DIAG / (match + '-targetlike.npz')
            inputs[match]['conditions'][condition] = {
                'feature_sha256': sha(feature_path),
                'parent_probabilities_sha256': sha(DIAG / f'{match}-{condition}-probs.npz'),
                'candidate_probabilities_sha256': sha(saved)}
            write('input-hashes.json', inputs)
            write('first-csv-hashes.json', first_hashes)
            del x, cat, tab
            gc.collect()
        costs.append({'match': match, 'stage': 'first', 'context_rows': len(y_train),
                      'seconds': time.monotonic()-start, 'saved_model_sha256': model_hash})
        write('cost.json', costs)
        del model, x_train, y_train
        gc.collect()
        print(f'Initial inference complete: {match}', flush=True)
    return costs, inputs, first_hashes


def score_initial(ids, inputs):
    import numpy as np
    from possession.decode import decode
    print('Initial five-match inference complete; starting quality-only scoring.', flush=True)
    rows = []
    for match in ids:
        prepared_path = PREPARED / (match + '.npz')
        if sha(prepared_path) != inputs[match]['conditions']['clean']['feature_sha256']:
            raise RuntimeError('Prepared heldout input/labels changed before quality scoring')
        with np.load(prepared_path) as d:
            y, blocks = d['y'], d['blocks'].tolist()
        for condition in ('clean', 'targetlike'):
            expected = inputs[match]['conditions'][condition]
            feature_path = prepared_path if condition == 'clean' else DIAG / (match + '-targetlike.npz')
            if sha(feature_path) != expected['feature_sha256']:
                raise RuntimeError('Features changed before quality scoring')
            if sha(DIAG / f'{match}-{condition}-probs.npz') != expected['parent_probabilities_sha256']:
                raise RuntimeError('Parent emissions changed before quality scoring')
            if sha(OUT / f'{match}-{condition}-probs.npz') != expected['candidate_probabilities_sha256']:
                raise RuntimeError('Candidate emissions changed before quality scoring')
            x = case_features(match, condition)
            with np.load(DIAG / f'{match}-{condition}-probs.npz') as d:
                cat = d['p']
            with np.load(OUT / f'{match}-{condition}-probs.npz') as d:
                tab = d['p']
            for arm, probability in arm_probabilities(cat, tab).items():
                predicted = decode(probability, (1 - np.eye(3))*16, blocks)
                rows.append({'match': match, 'condition': condition, 'arm': arm,
                             **measure(y, predicted, blocks, x)})
    write('results.json', rows)
    return rows


def main():
    global EXECUTION_STARTED
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', required=True, help='Exact committed scored supplement; no default approval')
    args = parser.parse_args()
    provenance = require_execution_authority(args.protocol)
    existing_results = [p for p in R.glob('*.json') if p.name != 'locked-inputs.json']
    if existing_results:
        raise RuntimeError('Existing scored result JSON requires review; no silent overwrite/resume')
    import numpy as np
    from tabicl import TabICLClassifier  # noqa: F401; fail fast on dependency/import problems.
    # The unchanged scorer imports pandas; check it before expensive warm-up.
    scorer_path = Path('reference/more-than-a-hack-2027-main/evaluation/possession_metrics.py')
    sys.path.insert(0, str(scorer_path.parent.resolve()))
    import possession_metrics  # noqa: F401
    from importlib.metadata import distributions
    dependencies = {d.metadata['Name']: d.version for d in distributions()
        if d.metadata['Name'] in ('tabicl', 'torch', 'numpy', 'scikit-learn', 'scipy', 'einops', 'huggingface_hub')}
    if dependencies != provenance['cache_dependencies']:
        raise RuntimeError('Predictor dependencies changed since cache admission')
    provenance.update(reference_scorer_sha256=sha(scorer_path), dependencies=dependencies,
                      split_sha256=sha('experiments/core-development/split.json'))
    configure()
    R.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    EXECUTION_STARTED = True
    ids = json.loads(Path('experiments/core-development/split.json').read_text())['development']
    if tuple(ids) != EXPECTED_IDS:
        raise ValueError('Original ordered development matches required; sealed matches forbidden')
    provenance.update(params=PARAMS, class_order=LABELS, match_order=ids, training_context_limit=30000, quality_screen_only=True, model_checkpoints_written=False)
    write('provenance.json', provenance)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-q'],
                           capture_output=True, text=True)
    (R / 'production-tests.txt').write_text(tests.stdout+tests.stderr)
    if tests.returncode:
        raise RuntimeError('Required production tests failed; no model fitting or scoring')
    costs, inputs, first_hashes = first_inference(ids)
    rows = score_initial(ids, inputs)
    decision = decisions(rows, ids, tests_pass=True)
    eligible = (decision['standalone_vs_parent']['quality_eligible']
                or decision['blend_vs_current_best']['quality_eligible'])
    decision.update(status='QUALITY_ELIGIBLE' if eligible else 'QUALITY_REJECTED',
                    determinism_all_cases_performed=False, determinism_verification_started=False)
    write('quality-gate.json', decision)
    write('gate.json', decision)
    print('Quality-only decision:', json.dumps(decision), flush=True)
    if not eligible:
        decision['verification_skipped_reason'] = 'Neither fixed arm passed quality gate; no promotion possible'
        write('gate.json', decision)
        print('Both quality gates failed; no full-case refit/reload verification required.', flush=True)
        return
    print('Quality screen complete. No model promoted; any eligible result needs separate single-thread verification.', flush=True)



def finish_report():
    if not EXECUTION_STARTED:
        return
    rows = json.loads((R / 'results.json').read_text()) if (R / 'results.json').exists() else []
    gate_data = json.loads((R / 'gate.json').read_text()) if (R / 'gate.json').exists() else {}
    failure = json.loads((R / 'failure.json').read_text()) if (R / 'failure.json').exists() else None
    lines = ['# Reduced-context development results', '', 'Quality screen only. Production unchanged; single-thread verification is still required for any winner.', '',
             '| Match | Setting | Model | spellF1 | macroF1 |', '|---|---|---|---:|---:|']
    for row in rows:
        lines.append(f"| {row['match']} | {row['condition']} | {row['arm']} | {row['spellF1']:.6f} | {row['macroF1']:.6f} |")
    lines += ['', '```json', json.dumps({'gate': gate_data, 'failure': failure}, indent=2), '```']
    (R / 'report.md').write_text('\n'.join(lines)+'\n')
    from datetime import datetime
    from zoneinfo import ZoneInfo
    stamp = datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()
    with Path('ball.md').open('a') as journal:
        journal.write(f"\n\nManual reduced-context run {stamp}: status={gate_data.get('status', 'INCOMPLETE_OR_FAILED')}; report {R}/report.md. No production promotion.\n")
    print(f'Read results: {R}/report.md', flush=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Operational failures are not silently converted to metric rejections.
        if EXECUTION_STARTED and R.exists():
            write('failure.json', {'type': type(error).__name__, 'message': str(error),
                                   'production_changed': False})
        raise

    finally:
        finish_report()
