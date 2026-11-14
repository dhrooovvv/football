"""User-run frozen two-member Trial-B private export; no labels, score or training."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
PROJECT = Path(__file__).resolve().parents[1]
ROOT = Path('experiments/tcn-final-b-export-2026-11-13')
sys.path.insert(0, str(PROJECT / ROOT))
from export_contract import (FINAL, MANIFEST, OUTPUT_ROOT, SEEDS, TARGET_ASSETS,
    load, require, sha, registration, final_signature, permitted_date,
    write_guard, write_json, validate_output, operation_lock, check_storage)


def run_checks():
    """A fresh subprocess keeps tests from configuring the inference process."""
    path = OUTPUT_ROOT / ('checks-' + str(time.time_ns()) + '.txt')
    with write_guard():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as stream:
            env = os.environ.copy()
            env['PYTHONPATH'] = str(PROJECT / 'src') + os.pathsep + str(PROJECT / 'scripts')
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s',
                str(ROOT / 'tests'), '-v'], stdout=stream, stderr=subprocess.STDOUT, env=env)
    require(result.returncode == 0, 'Export contracts failed; preserve ' + str(path))
    return path


def load_members(manifest, torch, model_code):
    from final_training import expected_identity, validate_saved, confirm_repeat
    members = []
    for seed in SEEDS:
        record = manifest['members'][str(seed)]
        require(sha(record['model']) == record['sha256']
                and sha(record['repeat_model']) == record['repeat_sha256']
                and sha(record['proof']) == record['proof_sha256'], 'Member bytes changed before reload')
        values = [torch.load(record[key], map_location='cpu', weights_only=True)
                  for key in ('model', 'repeat_model')]
        identity = expected_identity(final_signature(), seed)
        for value in values:
            validate_saved(value, identity)
        confirm_repeat(*values)
        proof = load(record['proof'])
        require(proof['identity'] == identity, 'Proof identity differs')
        for name in ('coverage', 'supervised_views', 'exposure', 'sampler_audit'):
            require(values[0][name] == proof[name], 'Proof/checkpoint mismatch: ' + name)
        for name, hash_key in (('losses', 'loss_sha256'), ('component_losses', 'component_loss_sha256')):
            digest = hashlib.sha256(json.dumps(values[0][name]).encode()).hexdigest()
            require(digest == proof[hash_key], 'Loss evidence differs')
        model = model_code.TCN().cpu().eval()
        model.load_state_dict(values[0]['state'], strict=True)
        require(sum(p.numel() for p in model.parameters()) == 9701, 'Class network differs')
        members.append(model)
        del values
    return members


def ensemble_probabilities(members, encoded, rotated, blocks, model_code, average_views, np, batch):
    require(len(members) == 2, 'Two ensemble members required')
    scaler = np.zeros(model_code.WIDTH), np.ones(model_code.WIDTH)
    probabilities, views = [], []
    for model in members:
        pair = tuple(model_code.predict(model, x, blocks, scaler, batch=batch) for x in (encoded, rotated))
        views.extend(pair)
        probabilities.append(average_views(*pair))
    # Identical ordering and normalization to the archived fold evaluation.
    return average_views(*probabilities), views


def output_aggregates(predicted, blocks, fps):
    counts = dict.fromkeys(('H', 'A', 'D'), 0)
    live_durations, all_durations = [], []
    for start, stop in blocks:
        last, length = None, 0
        for value in predicted[start:stop]:
            label = str(value)
            require(label in counts, 'Unexpected label inside a graded block')
            counts[label] += 1
            if label == last:
                length += 1
            else:
                if length:
                    all_durations.append(length / fps)
                    if last in ('H', 'A'):
                        live_durations.append(length / fps)
                last, length = label, 1
        if length:
            all_durations.append(length / fps)
            if last in ('H', 'A'):
                live_durations.append(length / fps)
    total = sum(counts.values())
    require(total > 0 and fps > 0, 'Empty graded output')
    return dict(shares={key: value / total for key, value in counts.items()},
        ha_spell_count=len(live_durations),
        mean_ha_spell_seconds=sum(live_durations) / len(live_durations) if live_durations else None,
        had_segment_count=len(all_durations), mean_had_segment_seconds=sum(all_durations) / len(all_durations),
        valid_frames=total, label_free=True, target_accuracy='unknown')


def validate_csv(path, official):
    reason = official.validate_submission(official.read_label_csv(path), 199319)
    require(reason is None, 'Official format validator failed; inspect private evidence')


def validate_target_config(config):
    source, blocks = config['sources']['tactical'], config['tactical_half_open_blocks']
    require(config['game'] == 'BAR-ATH' and config['fps'] == 25
            and config['home_team'] == 'Barcelona' and config['away_team'] == 'Atletic Club'
            and config['pitch_metres'] == [105.3, 68.0]
            and source == dict(frames=199319, slots=46)
            and blocks == [[11185, 90652], [110808, 190198]], 'Frozen target contract differs')
    return source, blocks


def export(output, manifest, signature, environment, checks):
    sys.path[:0] = [str(PROJECT / 'src'), str(PROJECT / 'scripts'), str(PROJECT / FINAL),
        str(PROJECT / 'experiments/tcn-pretrain-2026-11-11'),
        str(PROJECT / 'experiments/tcn-rotation-2026-11-11'),
        str(PROJECT / 'reference/more-than-a-hack-2027-main/evaluation')]
    import numpy as np
    import torch
    import pretrain_model as model_code
    import possession_metrics as official
    from possession.core import features
    from possession.decode import decode
    from possession.inputs import load_atd, load_teams, export_labels
    from prepare_tcn import encode
    from rotation import rotate180, average_views
    model_code.configure()
    manifest_hash = sha(MANIFEST)
    config = load('configs/competition.json')
    source, blocks = validate_target_config(config)
    track_path, teams_path = map(Path, TARGET_ASSETS)
    track = load_atd(track_path, source['frames'], source['slots'])
    teams = load_teams(teams_path, source['slots'], config['home_team'], config['away_team'])
    core, names = features(track, teams, blocks, config['pitch_metres'], config['fps'])
    require(names == ['home_distance', 'away_distance', 'distance_margin', 'ball_speed', 'edge_distance',
                     'ball_observed', 'home_observed', 'away_observed', 'gap_age'], 'Core order differs')
    encoded = encode(track, teams, blocks, core)
    del track, core
    rotated = rotate180(encoded)
    valid = np.zeros(source['frames'], dtype=bool)
    for start, stop in blocks:
        valid[start:stop] = True
    with write_guard():
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix='pending-' + output.name + '-', dir=OUTPUT_ROOT))
    # Preserve incomplete evidence on error; do not delete any user artifacts.
    digests, reference_views = [], None
    for tag, batch in (('first', 1), ('reload', 1), ('batch4', 4)):
        permitted_date()
        members = load_members(manifest, torch, model_code)
        probabilities, views = ensemble_probabilities(members, encoded, rotated, blocks,
                                                      model_code, average_views, np, batch)
        if tag == 'first':
            reference_views = views
        elif tag == 'reload':
            require(len(views) == len(reference_views) == 4
                    and all(np.array_equal(a, b) for a, b in zip(reference_views, views)),
                    'Member/view probabilities changed after fresh loading')
        predicted = decode(probabilities, (1 - np.eye(3)) * 16, blocks)
        require((predicted[~valid] == 'X').all() and np.isin(predicted[valid], ['H', 'A', 'D']).all(),
                'X/graded-block handling differs')
        path = staging / ('candidate.csv' if tag == 'first' else f'candidate-{tag}.csv')
        with write_guard():
            export_labels(path, predicted, source['frames'])
        validate_csv(path, official)
        digests.append(sha(path))
        if tag == 'first':
            aggregates = output_aggregates(predicted, blocks, config['fps'])
        del members, probabilities, views, predicted
        print('Validated private export pass:', tag, flush=True)
    require(len(set(digests)) == 1, 'CSV bytes differ across fresh loads or inference batches')
    _, after_signature, _ = registration()
    require(after_signature == signature and sha(MANIFEST) == manifest_hash,
            'Source/input/model/evidence changed during export')
    provenance = dict(schema='final_b_private_export_v1', completed=True,
        model_manifest=str(MANIFEST), model_manifest_sha256=manifest_hash,
        members=manifest['members'], export_registration=signature,
        export_inputs_sha256=sha(ROOT / 'inputs.json'),
        code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        input_hashes={str(p): sha(p) for p in (*map(Path, TARGET_ASSETS), Path('configs/competition.json'))},
        class_order=['H', 'A', 'D'], inference=manifest['inference'],
        csv_sha256=digests[0], pass_csv_sha256=dict(zip(('first', 'reload', 'batch4'), digests)),
        official_format_validation_passed=True, fresh_load_passes=3,
        reload_probabilities_equal_all_four_views=True, repeated_csv_bytes_equal=True,
        label_free_prediction_aggregates=aggregates, environment=environment,
        checks_path=str(checks), checks_sha256=sha(checks), temporal_slot_continuity_verified=False,
        target_accuracy='unknown', production_promoted=False, quality_evaluation_performed=False,
        full_training_reproduced_in_this_environment=False)
    write_json(staging / 'provenance.json', provenance)
    with write_guard():
        require(not output.exists(), 'Output appeared during export; preserve all evidence')
        os.replace(staging, output)
    print('Private final-B export qualified. CSV SHA256:', digests[0], flush=True)
    print('No target accuracy measured; production unchanged.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', required=True)
    parser.add_argument('--output', type=Path, default=OUTPUT_ROOT / 'local')
    args = parser.parse_args()
    os.chdir(PROJECT)
    manifest, signature, environment = registration()
    output = validate_output(args.output)
    with operation_lock():
        check_storage()
        checks = run_checks()
        export(output, manifest, signature, environment, checks)


if __name__ == '__main__':
    main()
