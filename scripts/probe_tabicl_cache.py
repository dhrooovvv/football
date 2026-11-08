"""Conditional cache-correctness admission only; no possession quality scoring.

Requires a committed protocol and completed uncapped admission. This helper
never reads query labels, competition assets, sealed matches or public scores.
Resource use is not capped. All training/model/probability artifacts stay data/.
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

R = Path('experiments/tabicl-cache-2026-11-08')
OUT = Path('data/tabicl-cache')
WEIGHT = Path('data/tabicl/model.ckpt')
PREPARED = Path('data/external/prepared')
PRIOR = Path('experiments/tabicl-uncapped-2026-11-08')
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
SEED = 20261106
QUERY_COUNT = 16384
ATOL = 1e-6
RTOL = 1e-5
MAX_ABS = 1e-6
EXECUTION_STARTED = False
PARAMS = dict(n_estimators=1, softmax_temperature=1., random_state=SEED,
              n_jobs=1, device='cpu', use_amp=False, use_fa3=False,
              offload_mode=False, model_path=str(WEIGHT), allow_auto_download=False)


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


def authority(protocol):
    from datetime import date, datetime
    from zoneinfo import ZoneInfo
    if datetime.now(ZoneInfo('Asia/Kolkata')).date() > date(2026, 11, 13):
        raise RuntimeError('Research freeze has passed')
    protocol = Path(protocol)
    relative = protocol.resolve().relative_to(Path.cwd().resolve()).as_posix()
    if subprocess.check_output(['git', 'show', 'HEAD:' + relative]) != protocol.read_bytes():
        raise RuntimeError('Exact cache admission protocol must be committed before execution')
    admission = json.loads((PRIOR / 'admission.json').read_text())
    actual = json.loads((PRIOR / 'actual.json').read_text())
    if not (admission['passed'] and actual['probabilities_equal'] and actual['csv_equal']):
        raise RuntimeError('Uncapped full-context admission has not passed')
    source = json.loads((PRIOR / 'weight-source.json').read_text())
    if sha(WEIGHT) != source['sha256']:
        raise RuntimeError('Pinned checkpoint changed')
    ids = json.loads(Path('experiments/core-development/split.json').read_text())['development']
    if tuple(ids) != IDS:
        raise RuntimeError('Original five ordered development matches required; sealed excluded')
    return {'protocol': relative, 'protocol_sha256': sha(protocol), 'source': source,
            'uncapped_actual_sha256': sha(PRIOR / 'actual.json'),
            'uncapped_dependencies': actual['dependencies'],
            'uncapped_csv_sha256': actual['csv_sha256'],
            'uncached_full_probability_comparison': False,
            'full_comparison_limit': 'Prior uncapped worker persisted CSV hashes, not raw probabilities',
            'synthetic_numeric_rule': {'max_abs': MAX_ABS, 'atol': ATOL, 'rtol': RTOL},
            'query_count': QUERY_COUNT, 'parameters_except_cache': PARAMS}


def configure():
    import numpy as np
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.mkldnn.enabled = False
    np.random.seed(SEED)
    torch.manual_seed(SEED)


def normalise(probability):
    import numpy as np
    p = np.asarray(probability, dtype=np.float64)
    if p.ndim != 2 or p.shape[1] != 3 or not np.isfinite(p).all() or (p < 0).any():
        raise ValueError('Invalid model probabilities')
    sums = p.sum(axis=1, keepdims=True)
    if not np.allclose(sums, 1., atol=1e-5, rtol=1e-5) or (sums <= 0).any():
        raise ValueError('Invalid probability row sums')
    return p / sums


def fit(x, y, cached, tag):
    from tabicl import TabICLClassifier
    print(f'{tag}: fit start; rows={len(x)}, kv_cache={cached}', flush=True)
    start = time.monotonic()
    model = TabICLClassifier(**PARAMS, kv_cache=cached)
    model.fit(x, y)
    print(f'{tag}: fit complete in {time.monotonic()-start:.3f}s', flush=True)
    return model


def predict(model, q, tag):
    order = [list(model.classes_).index(c) for c in ('H', 'A', 'D')]
    print(f'{tag}: predict start; queries={len(q)}', flush=True)
    start = time.monotonic()
    p = normalise(model.predict_proba(q)[:, order])
    print(f'{tag}: predict complete in {time.monotonic()-start:.3f}s', flush=True)
    return p


def csv_hash(p, path, blocks):
    import numpy as np
    from possession.decode import decode
    from possession.inputs import export_labels
    labels = decode(p, (1 - np.eye(3)) * 16, blocks)
    export_labels(path, labels, len(p))
    return sha(path)


def persist_model(model, path, tag):
    print(f'{tag}: saving local cache', flush=True)
    model.save(path, save_model_weights=False, save_training_data=True, save_kv_cache=True)
    return {'path': str(path), 'sha256': sha(path), 'bytes': path.stat().st_size,
            'trusted_local_file_only': True, 'training_context_saved': True,
            'kv_cache_saved': True, 'weights_saved': False}


def load_model(path, tag):
    from tabicl import TabICLClassifier
    print(f'{tag}: loading newly generated local cache', flush=True)
    return TabICLClassifier.load(path, device='cpu')


def synthetic(n):
    import numpy as np
    tag = f'synthetic-{n}'
    rng = np.random.default_rng(SEED)
    x = rng.normal(size=(n, 9))
    y = np.array(['H', 'A', 'D'])[np.arange(n) % 3]
    q = rng.normal(size=(64, 9))
    x[::13, 0] = np.nan
    q[::7, 0] = np.nan
    start = time.monotonic()
    uncached = fit(x, y, False, tag + '/uncached')
    baseline = predict(uncached, q, tag + '/uncached')
    baseline_hash = csv_hash(baseline, OUT / (tag + '-uncached.csv'), [(0, len(q))])
    del uncached
    gc.collect()
    first = fit(x, y, True, tag + '/cached-first')
    p = predict(first, q, tag + '/cached-first')
    p_hash = csv_hash(p, OUT / (tag + '-cached-first.csv'), [(0, len(q))])
    error = float(np.max(np.abs(p - baseline)))
    numeric = bool(error <= MAX_ABS and np.allclose(p, baseline, atol=ATOL, rtol=RTOL))
    equivalence = {'context_rows': n, 'query_rows': len(q), 'max_abs_probability_delta': error,
                   'numeric_tolerance_pass': numeric, 'uncached_csv_sha256': baseline_hash,
                   'cached_csv_sha256': p_hash, 'csv_bytes_equal': baseline_hash == p_hash}
    write(tag + '-equivalence.json', equivalence)
    if not numeric or baseline_hash != p_hash:
        raise AssertionError(tag + ': cached/uncached equivalence failed; no threshold rescue')
    np.savez_compressed(OUT / (tag + '-first-probs.npz'), p=p)
    model_path = OUT / (tag + '.pkl')
    saved = persist_model(first, model_path, tag)
    del first
    gc.collect()
    checks = []
    for stage in ('reload', 'refit'):
        model = load_model(model_path, tag) if stage == 'reload' else fit(x, y, True, tag + '/refit')
        repeated = predict(model, q, tag + '/' + stage)
        repeated_hash = csv_hash(repeated, OUT / (tag + '-' + stage + '.csv'), [(0, len(q))])
        equal = bool(np.array_equal(p, repeated))
        checks.append({'stage': stage, 'probabilities_exact': equal,
                       'csv_bytes_equal': repeated_hash == p_hash, 'csv_sha256': repeated_hash})
        write(tag + '-repeatability.json', checks)
        if not equal or repeated_hash != p_hash:
            raise AssertionError(tag + ': cached repeat/save-reload failed')
        del model
        gc.collect()
    result = {**equivalence, 'repeatability': checks, 'saved_cache': saved,
              'seconds': time.monotonic() - start, 'passed': True,
              'proves_possession_quality': False}
    write(tag + '.json', result)
    return result


def actual(source):
    import numpy as np
    provenance = json.loads(Path('experiments/tabicl-2026-11-08/context-provenance.json').read_text())
    xs, ys, training = [], [], {}
    for match in IDS[1:]:
        path = PREPARED / (match + '.npz')
        digest = sha(path)
        if digest != provenance['training'][match]['prepared_sha256']:
            raise RuntimeError('Prepared context changed since uncapped admission: ' + match)
        with np.load(path) as d:
            indices = np.arange(0, len(d['y']), 5)
            indices = indices[d['y'][indices] != 'X']
            xs.append(d['x'][indices])
            ys.append(d['y'][indices])
            training[match] = {'rows': len(indices), 'prepared_sha256': digest}
    x, y = np.concatenate(xs), np.concatenate(ys)
    if len(x) != 113507:
        raise RuntimeError('Matched first-fold context size changed')
    del xs, ys
    heldout_path = PREPARED / (IDS[0] + '.npz')
    with np.load(heldout_path) as d:
        q = d['x'][:QUERY_COUNT].copy()
        halves = d['blocks'].tolist()
    if len(q) != QUERY_COUNT:
        raise RuntimeError('Heldout input too short for fixed query proof')
    blocks = [(int(a), int(min(b, len(q)))) for a, b in halves if a < len(q)]
    write('actual-context-provenance.json', {'heldout': IDS[0], 'query_labels_loaded_or_used': False,
          'heldout_prepared_sha256': sha(heldout_path), 'training': training, 'context_rows': len(x)})
    print('actual: matched context loaded; query labels not loaded or used', flush=True)
    start = time.monotonic()
    first = fit(x, y, True, 'actual/cached-first')
    p64 = predict(first, q[:64], 'actual/64/cached-first')
    h64 = csv_hash(p64, OUT / 'actual64-first.csv', [(0, 64)])
    comparison = {'query_rows': 64, 'cached_csv_sha256': h64,
                  'prior_uncapped_csv_sha256': source['uncapped_csv_sha256'],
                  'csv_bytes_equal': h64 == source['uncapped_csv_sha256'],
                  'uncached_numeric_equivalence_tested': False,
                  'limitation': 'Prior uncapped worker did not save raw probabilities'}
    write('actual64-uncached-comparison.json', comparison)
    if not comparison['csv_bytes_equal']:
        raise AssertionError('Full-context cached64 CSV differs from prior uncapped64 CSV')
    pfull = predict(first, q, 'actual/16384/cached-first')
    hfull = csv_hash(pfull, OUT / 'actual16384-first.csv', blocks)
    np.savez_compressed(OUT / 'actual64-first-probs.npz', p=p64)
    np.savez_compressed(OUT / 'actual16384-first-probs.npz', p=pfull)
    model_path = OUT / 'actual.pkl'
    saved = persist_model(first, model_path, 'actual')
    del first
    gc.collect()
    checks = []
    for stage in ('reload', 'refit'):
        model = load_model(model_path, 'actual') if stage == 'reload' else fit(x, y, True, 'actual/refit')
        for count, baseline, expected_hash, bb in ((64, p64, h64, [(0, 64)]),
                                                 (QUERY_COUNT, pfull, hfull, blocks)):
            p = predict(model, q[:count], f'actual/{count}/{stage}')
            digest = csv_hash(p, OUT / f'actual{count}-{stage}.csv', bb)
            equal = bool(np.array_equal(p, baseline))
            checks.append({'stage': stage, 'query_rows': count, 'probabilities_exact': equal,
                           'csv_bytes_equal': digest == expected_hash, 'csv_sha256': digest})
            write('actual-repeatability.json', checks)
            if not equal or digest != expected_hash:
                raise AssertionError(f'actual cached {count}/{stage} exact repeatability failed')
        del model
        gc.collect()
    result = {'context_rows': len(x), 'query_sizes': [64, QUERY_COUNT],
              'full64_uncached_comparison': comparison, 'cached_repeatability': checks,
              'saved_cache': saved, 'seconds': time.monotonic() - start, 'passed': True,
              'quality_scored': False, 'full_uncached_probability_equivalence': False}
    write('actual.json', result)
    return result


def main():
    global EXECUTION_STARTED
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', required=True, help='Exact git-committed cache admission protocol')
    args = parser.parse_args()
    provenance = authority(args.protocol)
    if R.exists() and any(R.glob('*.json')):
        raise RuntimeError('Existing cache results require review; no silent overwrite/resume')
    configure()
    R.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    EXECUTION_STARTED = True
    from importlib.metadata import distributions
    provenance['dependencies'] = {d.metadata['Name']: d.version for d in distributions()
        if d.metadata['Name'] in ('tabicl', 'torch', 'numpy', 'scikit-learn', 'scipy', 'einops', 'huggingface_hub')}
    write('provenance.json', provenance)
    if provenance['dependencies'] != provenance['uncapped_dependencies']:
        raise RuntimeError('Dependency versions differ from uncapped admission; no equivalence claim allowed')
    results = []
    for n in (1000, 10000):
        results.append(synthetic(n))
    full = actual(provenance)
    write('admission.json', {'passed': True, 'synthetic_context_rows': [1000, 10000],
          'actual_context_rows': full['context_rows'], 'fixed_query_rows': QUERY_COUNT,
          'quality_scored': False, 'experiment_resource_caps': False,
          'full_uncached_comparison': 'CSV equality only; raw probabilities unavailable',
          'independent_cached_refit_and_reload': True, 'production_changed': False})
    print('Cache correctness admission passed; no quality scored or production changed.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if EXECUTION_STARTED:
            write('failure.json', {'type': type(error).__name__, 'message': str(error),
                                   'quality_scored': False, 'production_changed': False})
            write('admission.json', {'passed': False, 'failure': str(error),
                                     'quality_scored': False, 'experiment_resource_caps': False,
                                     'production_changed': False})
        raise
