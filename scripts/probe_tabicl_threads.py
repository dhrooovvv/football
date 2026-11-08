"""Preregistered CPU-11 cache speed/equality admission; no quality scoring.

Model and context stay fixed. Default probability mode retains the old numeric
plus exact-CSV criterion. Explicit csv mode gates cross-core equivalence only on
exact decoded CSV bytes, recording numeric differences as diagnostics. Within
CPU-11 refit/reload probabilities and CSV remain exact in both modes.
No thread-count search, tolerance search, resource caps or production changes.
"""
import os
BLAS_KEYS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS')
for _key in BLAS_KEYS:
    os.environ[_key] = '1'

import argparse
import gc
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_R = Path('experiments/tabicl-threads-2026-11-08')
DEFAULT_OUT = Path('data/tabicl-threads')
R, OUT = DEFAULT_R, DEFAULT_OUT
CRITERION = 'probability'
CACHE = Path('experiments/tabicl-cache-2026-11-08')
BASE_DATA = Path('data/tabicl-cache')
PREPARED = Path('data/external/prepared')
WEIGHT = Path('data/tabicl/model.ckpt')
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
THREADS = 11
SEED = 20261106
QUERY_COUNT = 16384
ATOL = 1e-6
RTOL = 1e-5
MAX_ABS = 1e-6
EXECUTION_STARTED = False


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


def expected_locked_paths(output_dir=None):
    registration = Path(output_dir) if output_dir is not None else R
    expected = {
        'scripts/probe_tabicl_threads.py', 'scripts/probe_tabicl_cache.py',
        (registration / 'baseline-timings.json').as_posix(),
        'src/possession/decode.py', 'src/possession/inputs.py',
        'experiments/core-development/split.json',
        'experiments/tabicl-2026-11-08/context-provenance.json',
        'experiments/tabicl-uncapped-2026-11-08/weight-source.json',
        'experiments/tabicl-cache-2026-11-08/admission.json',
        'experiments/tabicl-cache-2026-11-08/actual.json',
        'experiments/tabicl-cache-2026-11-08/provenance.json',
        'data/tabicl-cache/actual64-first-probs.npz',
        'data/tabicl-cache/actual16384-first-probs.npz',
    }
    expected.update(f'data/external/prepared/{match}.npz' for match in IDS)
    return expected


def require_committed(path):
    path = Path(path)
    relative = path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    if subprocess.check_output(['git', 'show', 'HEAD:' + relative]) != path.read_bytes():
        raise RuntimeError('Registration file is not committed unchanged: ' + relative)
    return relative


def authority(protocol):
    from datetime import date, datetime
    from zoneinfo import ZoneInfo
    if datetime.now(ZoneInfo('Asia/Kolkata')).date() > date(2026, 11, 13):
        raise RuntimeError('Research freeze has passed')
    relative = require_committed(protocol)
    manifest_path = R / 'locked-inputs.json'
    manifest_relative = require_committed(manifest_path)
    locked = json.loads(manifest_path.read_text())
    if not isinstance(locked, dict) or set(locked) != expected_locked_paths():
        raise RuntimeError('Thread manifest must cover exactly the registered code and baseline/context inputs')
    for name, digest in locked.items():
        if (not isinstance(digest, str) or len(digest) != 64
                or any(c not in '0123456789abcdef' for c in digest)):
            raise RuntimeError('Invalid registered SHA256: ' + name)
        if sha(name) != digest:
            raise RuntimeError('Locked thread input changed: ' + name)
    admission = json.loads((CACHE / 'admission.json').read_text())
    actual = json.loads((CACHE / 'actual.json').read_text())
    baseline_path = R / 'baseline-timings.json'
    require_committed(baseline_path)
    timings = json.loads(baseline_path.read_text())
    import math
    timing_keys = ('first_cache_fit_seconds', 'first_predict64_seconds', 'first_predict16384_seconds',
                   'reload_predict64_seconds', 'reload_predict16384_seconds')
    for name in timing_keys:
        value = timings.get(name)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0:
            raise RuntimeError('Missing/invalid registered CPU1 baseline timing: ' + name)
    if 'source_log_sha256' in timings:
        if timings.get('source_log', 'data/tabicl-cache-run.log') != 'data/tabicl-cache-run.log':
            raise RuntimeError('Unexpected CPU1 timing source')
        if sha('data/tabicl-cache-run.log') != timings['source_log_sha256']:
            raise RuntimeError('Registered CPU1 timing log changed')
    source = json.loads((CACHE / 'provenance.json').read_text())
    if not (admission['passed'] and actual['passed']
            and admission['fixed_query_rows'] == QUERY_COUNT):
        raise RuntimeError('Single-thread cache admission has not passed')
    if sha(WEIGHT) != source['source']['sha256']:
        raise RuntimeError('Pinned weights changed')
    ids = json.loads(Path('experiments/core-development/split.json').read_text())['development']
    if tuple(ids) != IDS:
        raise RuntimeError('Original ordered development matches required; sealed excluded')
    return {'protocol': relative, 'protocol_sha256': sha(protocol),
            'locked_manifest': manifest_relative, 'locked_manifest_sha256': sha(manifest_path),
            'locked_file_count': len(locked), 'expected_dependencies': source['dependencies'],
            'cache_actual_sha256': sha(CACHE / 'actual.json'),
            'cached_cpu1_total_admission_seconds': actual['seconds'],
            'baseline_timings': timings, 'baseline_timings_sha256': sha(baseline_path),
            'timing_limit': 'Historical CPU1 phase times; run order/system load are uncontrolled',
            'checkpoint_source': source['source'],
            'cpu1_parameters_except_cache': source['parameters_except_cache'], 'threads_tested': THREADS,
            'verification_threads': 1, 'resource_caps': False, 'quality_scored': False,
            'criterion': CRITERION,
            'output_directory': R.as_posix(), 'artifact_directory': OUT.as_posix(),
            'numeric_reference_rule_not_enforced': CRITERION == 'csv',
            'cross_thread_rule': ({'max_abs': MAX_ABS, 'atol': ATOL, 'rtol': RTOL, 'csv_exact': True}
                                  if CRITERION == 'probability' else {'csv_exact': True, 'numeric_differences': 'diagnostic_only'}),
            'within_cpu11_rule': 'exact normalized probabilities and CSV bytes'}


def configure():
    import numpy as np
    import psutil
    import torch
    hardware = {'logical_cores': psutil.cpu_count(logical=True),
                'physical_cores': psutil.cpu_count(logical=False),
                'machine': platform.machine(), 'platform': platform.platform()}
    if hardware['logical_cores'] != THREADS or hardware['physical_cores'] != THREADS:
        raise RuntimeError('Preregistered CPU-11 test requires the verified 11-core hardware')
    torch.set_num_threads(THREADS)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.mkldnn.enabled = False
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    hardware.update(torch_intra_threads=torch.get_num_threads(),
                    torch_interop_threads=torch.get_num_interop_threads(),
                    blas_preprocessing_env={k: os.environ[k] for k in BLAS_KEYS})
    return hardware


def matched_inputs():
    import numpy as np
    registered = json.loads(Path('experiments/tabicl-2026-11-08/context-provenance.json').read_text())
    xs, ys, training = [], [], {}
    for match in IDS[1:]:
        path = PREPARED / (match + '.npz')
        if sha(path) != registered['training'][match]['prepared_sha256']:
            raise RuntimeError('Training input differs from CPU1 admission: ' + match)
        with np.load(path) as d:
            indices = np.arange(0, len(d['y']), 5)
            indices = indices[d['y'][indices] != 'X']
            xs.append(d['x'][indices])
            ys.append(d['y'][indices])
            training[match] = {'rows': len(indices), 'prepared_sha256': sha(path)}
    x, y = np.concatenate(xs), np.concatenate(ys)
    if len(x) != 113507:
        raise RuntimeError('Matched CPU1 context row count changed')
    with np.load(PREPARED / (IDS[0] + '.npz')) as d:
        q = d['x'][:QUERY_COUNT].copy()
        halves = d['blocks'].tolist()
    if len(q) != QUERY_COUNT:
        raise RuntimeError('Fixed 16384-query input is unavailable')
    blocks = [(int(a), int(min(b, len(q)))) for a, b in halves if a < len(q)]
    write('context-provenance.json', {'heldout': IDS[0], 'context_rows': len(x),
          'training': training, 'query_labels_loaded_or_used': False})
    return x, y, q, blocks


def baseline_probabilities(base, blocks):
    import numpy as np
    actual = json.loads((CACHE / 'actual.json').read_text())
    hashes = {64: actual['full64_uncached_comparison']['cached_csv_sha256']}
    full_hashes = {r['csv_sha256'] for r in actual['cached_repeatability']
                   if r['query_rows'] == QUERY_COUNT and r['probabilities_exact'] and r['csv_bytes_equal']}
    if len(full_hashes) != 1:
        raise RuntimeError('CPU1 full-query cache references are inconsistent')
    hashes[QUERY_COUNT] = full_hashes.pop()
    arrays = {}
    for count, bb in ((64, [(0, 64)]), (QUERY_COUNT, blocks)):
        with np.load(BASE_DATA / f'actual{count}-first-probs.npz') as d:
            arrays[count] = d['p'].copy()
        if arrays[count].shape != (count, 3):
            raise RuntimeError('CPU1 baseline probability shape changed')
        # References already contain normalized float64 probabilities. Do not
        # renormalize them a second time; cross-mode rules are applied below.
        digest = base.csv_hash(arrays[count], OUT / f'cpu1-reference-{count}.csv', bb)
        if digest != hashes[count]:
            raise RuntimeError('CPU1 baseline probabilities/CSV provenance mismatch')
    return arrays, hashes


def run_predictions(base, model, q, blocks, stage, serving_threads, references, hashes, checks, costs):
    import numpy as np
    import torch
    model.n_jobs = serving_threads
    torch.set_num_threads(serving_threads)
    if torch.get_num_interop_threads() != 1:
        raise RuntimeError('Interop threads changed')
    for count, bb in ((64, [(0, 64)]), (QUERY_COUNT, blocks)):
        tag = f'{stage}/serve{serving_threads}/{count}'
        before = torch.get_num_threads()
        if before != serving_threads or model.n_jobs != serving_threads:
            raise RuntimeError('Actual serving thread count differs from protocol')
        start = time.monotonic()
        p = base.predict(model, q[:count], tag)
        seconds = time.monotonic() - start
        after = torch.get_num_threads()
        if after != serving_threads:
            raise RuntimeError('Serving did not restore the configured thread count')
        digest = base.csv_hash(p, OUT / f'{stage}-serve{serving_threads}-{count}.csv', bb)
        exact = bool(np.array_equal(p, references[count]))
        delta = float(np.max(np.abs(p - references[count])))
        cross_numeric = (bool(delta <= MAX_ABS and np.allclose(p, references[count], atol=ATOL, rtol=RTOL))
                         if CRITERION == 'probability' else None)
        within_exact = None
        if serving_threads == THREADS and stage != 'first':
            anchor_path = OUT / f'first-serve{THREADS}-{count}-probs.npz'
            anchor_record = next(r for r in checks if r['stage'] == 'first'
                                 and r['serving_threads'] == THREADS and r['query_rows'] == count)
            if sha(anchor_path) != anchor_record['saved_probabilities_sha256']:
                raise RuntimeError('Initial CPU11 probability anchor changed')
            with np.load(anchor_path) as anchor:
                within_exact = bool(np.array_equal(p, anchor['p']))
        row = {'stage': stage, 'serving_threads': serving_threads, 'query_rows': count,
               'torch_threads_before': before, 'torch_threads_after': after,
               'normalized_probabilities_exact_to_cpu1': exact,
               'criterion': CRITERION, 'max_abs_difference_to_cpu1': delta,
               'numeric_reference_rule_not_enforced': CRITERION == 'csv',
               'within_cpu11_probabilities_exact_to_first': within_exact,
               'csv_bytes_equal_to_cpu1': digest == hashes[count], 'csv_sha256': digest}
        if CRITERION == 'probability':
            row['cross_thread_numeric_tolerance_pass'] = cross_numeric
        checks.append(row)
        costs.append({'stage': stage, 'operation': 'predict', 'serving_threads': serving_threads,
                      'query_rows': count, 'seconds': seconds})
        write('checks.json', checks)
        write('cost.json', costs)
        if digest != hashes[count]:
            raise AssertionError('Thread optimization rejected: exact cross-core CSV equality failed: ' + tag)
        if CRITERION == 'probability' and not cross_numeric:
            raise AssertionError('Thread optimization rejected: fixed cross-thread probability rule failed: ' + tag)
        if within_exact is False:
            raise AssertionError('Thread optimization rejected: within-CPU11 exact repeatability failed: ' + tag)
        probabilities_path = OUT / f'{stage}-serve{serving_threads}-{count}-probs.npz'
        np.savez_compressed(probabilities_path, p=p)
        row['saved_probabilities_sha256'] = sha(probabilities_path)
        write('checks.json', checks)


def main():
    global EXECUTION_STARTED, R, OUT, CRITERION
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--criterion', choices=('probability', 'csv'), default='probability')
    parser.add_argument('--output', type=Path, default=DEFAULT_R)
    parser.add_argument('--data-output', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--protocol', required=True, help='Exact committed CPU-11 protocol')
    args = parser.parse_args()
    R, OUT, CRITERION = args.output, args.data_output, args.criterion
    root = Path.cwd().resolve()
    relative_r = R.resolve().relative_to(root)
    relative_out = OUT.resolve().relative_to(root)
    if not relative_r.parts or relative_r.parts[0] != 'experiments':
        raise RuntimeError('Research output must stay under experiments/')
    if not relative_out.parts or relative_out.parts[0] != 'data':
        raise RuntimeError('Model/probability artifacts must stay under ignored data/')
    if CRITERION == 'csv' and (R.resolve() == DEFAULT_R.resolve() or OUT.resolve() == DEFAULT_OUT.resolve()):
        raise RuntimeError('CSV criterion requires separate new output/artifact directories; preserve original results')
    if OUT.exists() and any(OUT.iterdir()):
        raise RuntimeError('Existing artifact directory is nonempty; preserve prior evidence')
    provenance = authority(args.protocol)
    registration_names = {'locked-inputs.json', 'baseline-timings.json'}
    if any(p.name not in registration_names for p in R.glob('*.json')):
        raise RuntimeError('Existing thread results require review; no silent overwrite/resume')
    import probe_tabicl_cache as base
    from importlib.metadata import distributions
    dependencies = {d.metadata['Name']: d.version for d in distributions()
        if d.metadata['Name'] in ('tabicl', 'torch', 'numpy', 'scikit-learn', 'scipy', 'einops', 'huggingface_hub')}
    if dependencies != provenance['expected_dependencies']:
        raise RuntimeError('Predictor environment differs from CPU1 cache admission')
    provenance.update(dependencies=dependencies, hardware=configure())
    base.R, base.OUT = R, OUT
    if base.PARAMS != provenance['cpu1_parameters_except_cache']:
        raise RuntimeError('Parameters differ from CPU1 cache baseline before thread override')
    base.PARAMS = dict(base.PARAMS, n_jobs=THREADS)
    if base.PARAMS['device'] != 'cpu' or base.PARAMS['offload_mode'] is not False:
        raise RuntimeError('CPU/offload configuration changed')
    provenance['parameters_except_cache'] = base.PARAMS
    R.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    EXECUTION_STARTED = True
    write('provenance.json', provenance)
    x, y, q, blocks = matched_inputs()
    references, hashes = baseline_probabilities(base, blocks)
    model_path = OUT / 'actual-cpu11.pkl'
    checks, costs, saved = [], [], None
    from tabicl import TabICLClassifier
    import torch
    start_all = time.monotonic()
    for stage in ('first', 'reload', 'refit'):
        torch.set_num_threads(THREADS)
        start = time.monotonic()
        print(f'{stage}: CPU11 cache fit/load starts', flush=True)
        if stage == 'reload':
            if sha(model_path) != saved['sha256']:
                raise RuntimeError('Newly generated local cache changed before reload')
            model = TabICLClassifier.load(model_path, device='cpu')
            if model.n_jobs != THREADS or model.kv_cache is not True:
                raise RuntimeError('Saved CPU11/cache settings changed')
        else:
            model = base.fit(x, y, True, 'threads/' + stage)
        costs.append({'stage': stage, 'operation': 'load' if stage == 'reload' else 'cached_fit',
                      'fitting_threads': THREADS, 'torch_intra_threads': torch.get_num_threads(),
                      'torch_interop_threads': torch.get_num_interop_threads(),
                      'context_rows': len(x), 'seconds': time.monotonic() - start})
        write('cost.json', costs)
        if torch.get_num_threads() != THREADS or torch.get_num_interop_threads() != 1:
            raise RuntimeError('Actual cache fit/load threads differ from protocol')
        run_predictions(base, model, q, blocks, stage, THREADS, references, hashes, checks, costs)
        if stage == 'first':
            # Save while the estimator still declares the CPU11 serving setting.
            saved = base.persist_model(model, model_path, 'threads/first')
            write('saved-cache.json', saved)
        if stage == 'refit':
            run_predictions(base, model, q, blocks, stage, 1, references, hashes, checks, costs)
        del model
        gc.collect()
    # Six CPU11 predictions plus two CPU1 serving checks on the final refit.
    # All ratios are descriptive observations, not controlled benchmark claims.
    timings = provenance['baseline_timings']
    fit_ratios, prediction_ratios, paired_ratios = [], [], []
    for row in costs:
        if row['operation'] == 'cached_fit':
            one = timings['first_cache_fit_seconds']
            fit_ratios.append({'stage': row['stage'], 'baseline_cpu1_phase': 'first_cached_fit',
                'baseline_cpu1_seconds': one, 'cpu11_seconds': row['seconds'],
                'cpu1_over_cpu11_wall_ratio': one/row['seconds'] if row['seconds'] else None})
        elif row['operation'] == 'predict' and row['serving_threads'] == THREADS:
            baseline_phase = 'reload' if row['stage'] == 'reload' else 'first'
            one = timings[f"{baseline_phase}_predict{row['query_rows']}_seconds"]
            prediction_ratios.append({'stage': row['stage'], 'query_rows': row['query_rows'],
                'baseline_cpu1_phase': baseline_phase, 'baseline_cpu1_seconds': one,
                'cpu11_seconds': row['seconds'],
                'cpu1_over_cpu11_wall_ratio': one/row['seconds'] if row['seconds'] else None})
    for count in (64, QUERY_COUNT):
        one = next(r['seconds'] for r in costs if r['stage'] == 'refit' and r['operation'] == 'predict'
                   and r['serving_threads'] == 1 and r['query_rows'] == count)
        eleven = next(r['seconds'] for r in costs if r['stage'] == 'refit' and r['operation'] == 'predict'
                      and r['serving_threads'] == THREADS and r['query_rows'] == count)
        paired_ratios.append({'stage': 'refit', 'query_rows': count, 'paired_cpu1_seconds': one,
            'paired_cpu11_seconds': eleven, 'cpu1_over_cpu11_wall_ratio': one/eleven if eleven else None,
            'ordering_caveat': 'Same fitted cache; CPU11 measured before CPU1; shared system load uncontrolled'})
    write('admission.json', {'passed': True, 'thread_optimization_admitted': True,
          'criterion': CRITERION, 'numeric_reference_rule_not_enforced': CRITERION == 'csv',
          'admission_scope': ('Cross-core exact CSV equivalence only; numeric differences diagnostic; exact within-CPU11 proof'
                              if CRITERION == 'csv' else 'Numeric and CSV computational equivalence only; speed ratios descriptive'),
          'cores_selected_for_scoring': False,
          'threads': THREADS, 'cpu1_verification': True, 'checks': len(checks),
          'seconds': time.monotonic()-start_all, 'observed_fit_wall_ratios': fit_ratios,
          'observed_prediction_wall_ratios': prediction_ratios,
          'final_refit_same_cache_serving_wall_ratios': paired_ratios,
          'controlled_speed_benchmark': False, 'quality_scored': False,
          'production_changed': False, 'experiment_resource_caps': False})
    print(f'CPU11 {CRITERION} criterion and exact within-mode admission passed; no quality or production change.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if EXECUTION_STARTED:
            write('failure.json', {'type': type(error).__name__, 'message': str(error),
                                   'criterion': CRITERION, 'numeric_reference_rule_not_enforced': CRITERION == 'csv',
                                   'quality_scored': False, 'production_changed': False})
            write('admission.json', {'passed': False, 'thread_optimization_admitted': False,
                  'criterion': CRITERION, 'numeric_reference_rule_not_enforced': CRITERION == 'csv',
                  'fallback_threads': 1, 'failure': str(error), 'quality_scored': False,
                  'production_changed': False, 'experiment_resource_caps': False,
                  'no_retry_thread_search': True})
        raise
