"""User-run final hybrid fitting, private export and once-only sealed evaluation."""
import argparse
from contextlib import contextmanager
from datetime import date, datetime
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from zoneinfo import ZoneInfo

for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
PROJECT = Path(__file__).resolve().parents[1]
R = Path('experiments/tcn-hybrid-2026-11-14')
MODELS = Path('models/tcn-hybrid/final')
DATA = Path('data/tcn-hybrid/final')
OUT = Path('data/competition/tcn-hybrid-exports')
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
SEEDS = (20261106, 20261107)
sys.path[:0] = [str(PROJECT / R), str(PROJECT / 'src'), str(PROJECT / 'scripts')]
from hybrid_contract import (registration, validated_review, storage_guard, require, sha, stage_signature)


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value, training=True):
    with storage_guard(training=training):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
        temporary.replace(path)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, 'Missing module: ' + str(path))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def selected_stages(through, signature):
    stages, reviews = [], {}
    for stage in ('temporal', 'graph'):
        review = validated_review(stage, signature)
        reviews[stage] = sha(R / ('reviewed-' + stage + '.json'))
        if review['accepted']:
            stages.append(stage)
        if stage == through:
            break
    return stages, reviews


def release_identity(through, base_signature):
    stages, reviews = selected_stages(through, base_signature)
    value = dict(schema='frozen_b_hybrid_final_v1', registration=base_signature,
                 through=through, stages=stages, review_hashes=reviews,
                 base_manifest_sha256=sha('models/tcn-final-b/manifest.json'),
                 training_matches=['idsse-' + m for m in IDS], seeds=list(SEEDS),
                 steps=40000, class_order=['H', 'A', 'D'], switching_penalty=16)
    signature = hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
    return value, signature


@contextmanager
def operation():
    DATA.mkdir(parents=True, exist_ok=True)
    with (DATA / 'operation.lock').open('a+') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError('Another final hybrid operation is active') from error
        with Path('data/tcn-expanded/operation.lock').open('a+') as compact:
            fcntl.flock(compact, fcntl.LOCK_SH | fcntl.LOCK_NB)
            yield


def checks():
    path = R / 'release' / ('checks-' + str(time.time_ns()) + '.txt')
    with storage_guard(training=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as stream:
            env = os.environ.copy()
            env['PYTHONPATH'] = 'src:scripts:' + str(R)
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover',
                                     '-s', str(R / 'tests'), '-v'],
                                    stdout=stream, stderr=subprocess.STDOUT, env=env)
    require(result.returncode == 0, 'Hybrid release checks failed; preserve ' + str(path))
    return path


def dependencies():
    sys.path[:0] = [str(PROJECT / R), str(PROJECT / 'scripts'), str(PROJECT / 'src'),
                   str(PROJECT / 'experiments/tcn-pretrain-2026-11-11'),
                   str(PROJECT / 'experiments/tcn-rotation-2026-11-11'),
                   str(PROJECT / 'reference/more-than-a-hack-2027-main/evaluation')]
    import numpy as np
    import torch
    import pretrain_model as base_model
    import hybrid_model
    import hybrid_data
    import hybrid_training
    from expanded_data import CompactCase
    from rotation import rotate180, average_views
    from possession.decode import decode
    from possession.inputs import export_labels
    from run_tcn_parallel import metrics
    import possession_metrics as official
    base_model.configure()
    old_root = PROJECT / 'experiments/tcn-final-b-export-2026-11-13'
    sys.path.insert(0, str(old_root))
    old_export = module('frozen_final_b_export', PROJECT / 'scripts/export_tcn_final_b.py')
    manifest, _, environment = old_export.registration()
    return locals()


def base_probabilities(x, blocks, d, batch=1):
    members = d['old_export'].load_members(d['manifest'], d['torch'], d['base_model'])
    value, _ = d['old_export'].ensemble_probabilities(
        members, x, d['rotate180'](x), blocks, d['base_model'], d['average_views'], d['np'], batch)
    return value


def checkpoint_paths(stage, seed):
    return [MODELS / stage / str(seed) / fit / 'progress.pt' for fit in ('first', 'repeat')]


def final_model(stage, seed, signature, d):
    paths = checkpoint_paths(stage, seed)
    proof = load(MODELS / stage / str(seed) / 'proof.json')
    require(proof['signature'] == signature and proof['seed'] == seed and proof['stage'] == stage,
            'Final branch proof identity differs')
    require(proof['exact_repeat'] and proof['steps'] == 40000, 'Final branch is incomplete')
    require(proof['checkpoint_hashes'] == {str(p): sha(p) for p in paths}, 'Final branch bytes changed')
    require(sha(proof['checks_path']) == proof['checks_sha256'], 'Final branch checks changed')
    saved = [d['torch'].load(p, map_location='cpu', weights_only=True) for p in paths]
    identity = d['hybrid_training'].expected_identity(signature, stage, seed, None, purpose='final')
    for value in saved:
        d['hybrid_training'].validate_saved(value, identity)
    d['hybrid_training'].confirm_repeat(*saved)
    model = (d['hybrid_model'].TemporalRefiner() if stage == 'temporal'
             else d['hybrid_model'].GraphRefiner()).cpu().eval()
    model.load_state_dict(saved[0]['state'], strict=True)
    return model


def apply_stage(stage, x, parent, blocks, signature, d, batch=1):
    values = []
    for seed in SEEDS:
        model = final_model(stage, seed, signature, d)
        prediction = d['hybrid_model'].predict(model, x, parent, blocks, batch=batch)
        values.append(prediction)
    if all(d['np'].array_equal(value, parent) for value in values):
        return parent.copy()
    return d['average_views'](*values)


def infer(x, blocks, stages, signatures, d, batch=1):
    probabilities = base_probabilities(x, blocks, d, batch)
    for stage in stages:
        probabilities = apply_stage(stage, x, probabilities, blocks, signatures[stage], d, batch)
    return probabilities


def cached_final_parent(base, stage, preceding, signatures, d, identity):
    """Cache only frozen probabilities; original prepared arrays remain shared."""
    paths = {}
    for gap in (False, True):
        tag = 'gap' if gap else 'clean'
        path = DATA / 'cache' / stage / (base.key + '-' + tag + '.npy')
        proof_path = path.with_suffix('.json')
        binding = dict(release=identity, stage=stage, case=base.key, view=tag,
                       preceding=preceding, signatures=signatures)
        if proof_path.exists():
            proof = load(proof_path)
            require(proof['binding'] == binding and sha(path) == proof['sha256'], 'Final cache differs')
        else:
            require(not path.exists(), 'Orphan final cache; preserve and review')
            x = base.read(d['np'].arange(len(base.labels)), gap)
            probabilities = infer(x, base.blocks, preceding, signatures, d)
            with storage_guard():
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary = path.with_suffix('.tmp')
                with temporary.open('wb') as stream:
                    d['np'].save(stream, probabilities, allow_pickle=False)
                temporary.replace(path)
            save(proof_path, dict(binding=binding, sha256=sha(path)))
        paths[tag] = path
    return d['hybrid_data'].HybridCase(base, paths['clean'], paths['gap'])


def fit_final(through, registration_signature, check_path, d):
    identity, signature = release_identity(through, registration_signature)
    final_fit_projection(identity['stages'], registration_signature)
    signatures = {}
    for stage in identity['stages']:
        # Temporal final artifacts have one identity whether graph is retained later.
        _, stage_signature = release_identity(stage, registration_signature)
        preceding = [s for s in identity['stages'] if s == 'temporal' and stage == 'graph']
        cases = [cached_final_parent(d['CompactCase'](Path('data/tcn-expanded') / ('idsse-' + m)),
                                     stage, preceding, signatures, d, stage_signature) for m in IDS]
        for seed in SEEDS:
            proof_path = MODELS / stage / str(seed) / 'proof.json'
            if proof_path.exists():
                final_model(stage, seed, stage_signature, d)
                continue
            paths = checkpoint_paths(stage, seed)
            first = None
            for index, path in enumerate(paths):
                model = d['hybrid_training'].train_fit(cases, path.parent, stage_signature, stage,
                    seed, None, storage_guard, purpose='final')
                if index == 0:
                    first = model
            saved = [d['torch'].load(p, map_location='cpu', weights_only=True) for p in paths]
            expected = d['hybrid_training'].expected_identity(stage_signature, stage, seed, None, purpose='final')
            for value in saved:
                d['hybrid_training'].validate_saved(value, expected)
            d['hybrid_training'].confirm_repeat(*saved)
            require(all(d['torch'].equal(v, saved[0]['state'][k]) for k, v in first.state_dict().items()),
                    'In-memory final branch differs from checkpoint')
            save(proof_path, dict(signature=stage_signature, stage=stage, seed=seed, steps=40000,
                training_matches=identity['training_matches'], exact_repeat=True,
                checks_path=str(check_path), checks_sha256=sha(check_path),
                checkpoint_hashes={str(p): sha(p) for p in paths}))
            print('Final hybrid branch complete:', stage, seed, flush=True)
        signatures[stage] = stage_signature
    members = {stage: {str(seed): dict(proof=str(MODELS / stage / str(seed) / 'proof.json'),
                proof_sha256=sha(MODELS / stage / str(seed) / 'proof.json')) for seed in SEEDS}
               for stage in identity['stages']}
    save(MODELS / ('manifest-' + through + '.json'), dict(identity=identity, signature=signature,
         stage_signatures=signatures, members=members, source_inputs_sha256=sha(R / 'inputs.json'),
         base_manifest_sha256=sha('models/tcn-final-b/manifest.json'),
         quality_evaluation_performed=False, production_promoted=False, target_accuracy='unknown'))
    print('Final hybrid fit complete. Stop for saved-artifact review.', flush=True)


def final_fit_projection(stages, registration_signature):
    """Recompute remaining serial final work using the user's measured preflights."""
    seconds = 0.
    for stage in stages:
        pending = sum(not (MODELS / stage / str(seed) / 'proof.json').exists() for seed in SEEDS)
        if not pending:
            continue
        report = load(R / 'preflight' / stage / 'report.json')
        bound, signature = stage_signature(stage, registration_signature)
        require(report['completed'] and report['signature'] == signature and report['binding'] == bound,
                'Final fitting needs the measured preflight for this exact parent')
        require(sha(report['checks_path']) == report['checks_sha256'], 'Preflight checks changed')
        for path, digest in report['caches'].items():
            require(sha(path) == digest, 'Preflight cache changed before final fitting')
        speed = report['maximum_seconds_per_update']
        require(isinstance(speed, (int, float)) and 0 < speed < float('inf'), 'Invalid measured fit speed')
        seconds += speed * 40000 * 2 * pending + report['preparation_and_probe_seconds']
    remaining = (datetime(2026, 11, 16, tzinfo=ZoneInfo('Asia/Kolkata'))
                 - datetime.now(ZoneInfo('Asia/Kolkata'))).total_seconds()
    require(1.5 * seconds < remaining, 'Projected serial final fitting exceeds time before freeze')
    return dict(projected_seconds=1.5 * seconds, remaining_seconds=remaining, estimate_not_guarantee=True)


def validate_manifest(path, base_signature, d):
    value = load(path)
    identity, signature = release_identity(value['identity']['through'], base_signature)
    require(value['identity'] == identity and value['signature'] == signature
            and value['source_inputs_sha256'] == sha(R / 'inputs.json')
            and value['base_manifest_sha256'] == sha('models/tcn-final-b/manifest.json'),
            'Hybrid final manifest differs')
    require(value['quality_evaluation_performed'] is False and value['production_promoted'] is False,
            'Unexpected final manifest status')
    for stage in identity['stages']:
        _, expected = release_identity(stage, base_signature)
        require(value['stage_signatures'][stage] == expected, 'Final branch signature differs')
        for seed in SEEDS:
            proof = value['members'][stage][str(seed)]
            require(sha(proof['proof']) == proof['proof_sha256'], 'Final branch proof changed')
            final_model(stage, seed, expected, d)
    return value


def export_final(manifest_path, base_signature, d, check_path, tag):
    value = validate_manifest(manifest_path, base_signature, d)
    output = OUT / tag
    require(tag in ('local', 'clean', 'clone') and not output.exists(), 'Preserve existing private export')
    config = load('configs/competition.json')
    source, blocks = d['old_export'].validate_target_config(config)
    from possession.core import features
    from possession.inputs import load_atd, load_teams
    from prepare_tcn import encode
    paths = [Path(p) for p in d['old_export'].TARGET_ASSETS]
    track = load_atd(paths[0], source['frames'], source['slots'])
    teams = load_teams(paths[1], source['slots'], config['home_team'], config['away_team'])
    core, _ = features(track, teams, blocks, config['pitch_metres'], config['fps'])
    x = encode(track, teams, blocks, core)
    with storage_guard(training=False):
        OUT.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix='pending-' + tag + '-', dir=OUT))
    hashes, first = {}, None
    for name, batch in (('first', 1), ('reload', 1), ('batch4', 4)):
        probabilities = infer(x, blocks, value['identity']['stages'], value['stage_signatures'], d, batch)
        if name == 'first':
            first = probabilities.copy()
        elif name == 'reload':
            require(d['np'].array_equal(first, probabilities), 'Hybrid probabilities changed after reload')
        prediction = d['decode'](probabilities, (1 - d['np'].eye(3)) * 16, blocks)
        filename = 'candidate.csv' if name == 'first' else 'candidate-' + name + '.csv'
        with storage_guard(training=False):
            d['export_labels'](staging / filename, prediction, source['frames'])
        require(d['official'].validate_submission(d['official'].read_label_csv(staging / filename),
                source['frames']) is None, 'Official hybrid CSV validation failed')
        hashes[name] = sha(staging / filename)
    require(len(set(hashes.values())) == 1, 'Hybrid CSV bytes differ across inference passes')
    registration(training=False)
    d['old_export'].registration()
    validate_manifest(manifest_path, base_signature, d)
    save(staging / 'provenance.json', dict(completed=True, manifest=str(manifest_path),
         manifest_sha256=sha(manifest_path), csv_sha256=hashes['first'], pass_hashes=hashes,
         official_validation=True, exact_reload_probabilities=True, environment=d['environment'],
         checks_path=str(check_path), checks_sha256=sha(check_path),
         code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
         production_promoted=False, target_accuracy='unknown'), training=False)
    with storage_guard(training=False):
        require(not output.exists(), 'Export appeared concurrently')
        staging.replace(output)
    print('Private hybrid export qualified:', hashes['first'], flush=True)


def sealed_corruption(track, blocks, seed, d):
    from possession.core import corrupt
    from possession.inputs import Tracking
    summary = load('data/diagnostics-review/target-shift.json')
    gaps = d['np'].asarray(summary['missing_runs'], dtype=int)
    seen = d['np'].asarray(summary['observed_runs'], dtype=int)
    require(len(gaps) > 0 and len(seen) > 0 and (gaps > 0).all() and (seen > 0).all(),
            'Frozen target-like burst model is invalid')
    rng = d['np'].random.default_rng(seed)
    ball = track.ball.copy()
    for start, stop in blocks:
        position = start
        missing = bool(rng.random() < summary['missing_fraction'])
        while position < stop:
            length = int(rng.choice(gaps if missing else seen))
            end = min(stop, position + length)
            if missing:
                ball[position:end] = d['np'].nan
            position, missing = end, not missing
    return Tracking(corrupt(track, blocks, seed).players, ball)


def sealed(manifest_path, base_signature, d):
    today = datetime.now(ZoneInfo('Asia/Kolkata')).date()
    require(date(2026, 11, 16) <= today <= date(2026, 11, 17), 'Sealed evaluation starts at freeze')
    value = validate_manifest(manifest_path, base_signature, d)
    qualified_exports(manifest_path)
    directory = R / 'sealed'
    match_paths = {}
    for match in ('J03WQQ', 'J03WR9'):
        paths = list(Path('data/external').rglob('*' + match + '*.xml'))
        metadata = [p for p in paths if 'matchinformation' in p.name.lower()]
        positions = [p for p in paths if 'positions' in p.name.lower()]
        require(len(metadata) == len(positions) == 1, 'Sealed raw input path is ambiguous')
        match_paths[match] = [str(metadata[0]), str(positions[0])]
    identity = dict(manifest_sha256=sha(manifest_path), signature=value['signature'],
                    matches=['J03WQQ', 'J03WR9'], corruption_seeds=[20261206, 20261207],
                    input_hashes={p: sha(p) for pair in match_paths.values() for p in pair},
                    corruption_statistics_sha256=sha('data/diagnostics-review/target-shift.json'))
    marker = directory / 'started.json'
    if marker.exists():
        require(load(marker) == identity, 'Once-only sealed candidate already locked differently')
    else:
        save(marker, identity, training=False)
    if (directory / 'completion.json').exists():
        completed = load(directory / 'completion.json')
        require(completed['identity'] == identity, 'Sealed completion differs')
        for path, digest in completed['results_hashes'].items():
            require(sha(path) == digest, 'Sealed results changed')
        print('Sealed evaluation already completed; preserved results.', flush=True)
        return
    from possession.external import load_match
    from possession.core import features
    from prepare_tcn import encode
    from review_frozen import score
    starter = PROJECT / 'reference/more-than-a-hack-2027-main/starter'
    sys.path.insert(0, str(starter))
    import baseline
    results = {}
    for index, match in enumerate(identity['matches']):
        report_path = directory / (match + '.json')
        if report_path.exists():
            old = load(report_path)
            require(old['identity'] == identity and old['match'] == match, 'Sealed resume differs')
            checksum = old.pop('content_sha256', None)
            require(hashlib.sha256(json.dumps(old, sort_keys=True).encode()).hexdigest() == checksum,
                    'Sealed cached report content differs')
            for path, digest in old['input_hashes'].items():
                require(sha(path) == digest, 'Sealed source changed')
            results[str(report_path)] = sha(report_path)
            continue
        input_hashes = {p: identity['input_hashes'][p] for p in match_paths[match]}
        track, teams, blocks, pitch, y = load_match(*match_paths[match])
        rows = []
        for condition, observed in (('clean', track),
                ('targetlike', sealed_corruption(track, blocks, identity['corruption_seeds'][index], d))):
            core, _ = features(observed, teams, blocks, pitch)
            x = encode(observed, teams, blocks, core)
            probabilities = infer(x, blocks, value['identity']['stages'], value['stage_signatures'], d)
            prediction = d['decode'](probabilities, (1 - d['np'].eye(3)) * 16, blocks)
            candidate = d['metrics'](y, prediction, blocks, score, d['official'], d['np'])
            home = d['np'].where(d['np'].isfinite(core[:, 0]), core[:, 0], d['np'].inf)
            away = d['np'].where(d['np'].isfinite(core[:, 1]), core[:, 1], d['np'].inf)
            codes = d['np'].where(d['np'].minimum(home, away) < d['np'].inf,
                                 d['np'].where(home <= away, 0, 1), -1)
            baselines = {}
            for width in (0, 25, 50, 125):
                labels = d['np'].full(len(y), 'X')
                for start, stop in blocks:
                    labels[start:stop] = baseline.smooth(codes[start:stop], width)
                baselines[str(width)] = d['metrics'](y, labels, blocks, score, d['official'], d['np'])
            rows.append(dict(condition=condition, candidate=candidate, baselines=baselines))
        require(input_hashes == {p: sha(p) for p in input_hashes}, 'Sealed source changed during evaluation')
        report = dict(identity=identity, match=match, input_hashes=input_hashes, rows=rows)
        report['content_sha256'] = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
        save(report_path, report, training=False)
        results[str(report_path)] = sha(report_path)
        print('Completed once-only sealed evaluation:', match, flush=True)
    save(directory / 'completion.json', dict(identity=identity, completed=True, results_hashes=results,
         interpretation='Poor development transfer or loss to smoothing baseline triggers bug/transfer investigation. '
                        'No tuning or model selection from sealed results.', target_accuracy='unknown'), training=False)


def qualified_exports(manifest_path):
    """Require the planned local/clean/clone qualification for this selected artifact."""
    hashes = []
    for tag in ('local', 'clean', 'clone'):
        directory = OUT / tag
        provenance = load(directory / 'provenance.json')
        require(provenance['completed'] and provenance['manifest_sha256'] == sha(manifest_path)
                and provenance['official_validation'] and provenance['exact_reload_probabilities'],
                'Selected hybrid export qualification is incomplete: ' + tag)
        require(set(provenance['pass_hashes']) == {'first', 'reload', 'batch4'}
                and set(provenance['pass_hashes'].values()) == {provenance['csv_sha256']},
                'Qualified export pass hashes differ')
        for name in ('candidate.csv', 'candidate-reload.csv', 'candidate-batch4.csv'):
            require(sha(directory / name) == provenance['csv_sha256'], 'Qualified CSV bytes changed')
        hashes.append(provenance['csv_sha256'])
    require(len(set(hashes)) == 1, 'Local, clean and clone hybrid exports differ')
    return hashes[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--fit', action='store_true')
    mode.add_argument('--export', action='store_true')
    mode.add_argument('--sealed', action='store_true')
    parser.add_argument('--through', choices=('temporal', 'graph'), default='graph')
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--output-tag', choices=('local', 'clean', 'clone'), default='local')
    args = parser.parse_args()
    os.chdir(PROJECT)
    registered = registration(training=args.fit)
    base_signature = registered[-1]
    with operation():
        check_path = checks()
        d = dependencies()
        if args.fit:
            fit_final(args.through, base_signature, check_path, d)
        else:
            manifest = args.manifest or MODELS / ('manifest-' + args.through + '.json')
            if args.export:
                export_final(manifest, base_signature, d, check_path, args.output_tag)
            else:
                sealed(manifest, base_signature, d)


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        os.chdir(PROJECT)
        try:
            save(R / 'release' / 'failures' / (str(time.time_ns()) + '.json'),
                 dict(error_type=type(error).__name__, message=str(error)), training=False)
        except Exception:
            print('Preserve terminal output; failure evidence could not be saved.', file=sys.stderr)
        raise
