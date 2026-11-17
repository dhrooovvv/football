"""User-run private export of the five-match staged40k TCN; no scoring or tuning."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PROJECT = Path(__file__).resolve().parents[1]
ROOT = Path('experiments/tcn-winner-release-2026-11-12')
sys.path.insert(0, str(PROJECT / ROOT))
from release_contract import (KEYS, SCHEMA, TARGET_ASSETS, expected_identity, registration,
                              reviewed_diagnostic, require, sha, write_json)


def validate_manifest(manifest, signature, environment):
    require(manifest.get('schema') == SCHEMA and manifest.get('registration') == signature,
            'Manifest belongs to a different release registration')
    require(manifest.get('training_matches') == list(KEYS) and manifest.get('training_steps') == 40000,
            'Final fit membership or budget differs')
    require(manifest.get('repeated_training_exact') is True
            and manifest.get('checkpoint_state_reload_exact') is True, 'Final fit/reload evidence is missing')
    require(manifest.get('scaler_policy') == 'zeros_ones_521'
            and manifest.get('class_order') == ['H', 'A', 'D'], 'Representation/class convention differs')
    require(manifest.get('inference') == dict(rotation180_probability_weights=[.5, .5], switching_penalty=16),
            'Winner probability/decoder recipe differs')
    require(manifest.get('environment') == environment and manifest.get('production_promoted') is False
            and manifest.get('quality_evaluation_performed') is False, 'Final-fit provenance differs')
    diagnostic = manifest.get('slot_diagnostic')
    require(isinstance(diagnostic, dict) and diagnostic.get('human_review_acknowledged') is True,
            'Human review of slot diagnostic is missing')
    require(manifest.get('identity') == expected_identity(signature, diagnostic), 'Final-fit identity differs')
    require(manifest.get('release_inputs_sha256') == sha(ROOT / 'inputs.json'), 'Release input lock differs')


def load_winner(manifest, signature, environment, torch, model_code):
    from winner_training import validate_saved, confirm_final_repeat
    validate_manifest(manifest, signature, environment)
    paths = [Path(manifest['model']), Path(manifest['repeat_model'])]
    for path in paths:
        require(path.resolve().is_relative_to((PROJECT / 'models').resolve()), 'Model must stay in private models')
    require(paths[0] != paths[1] and sha(paths[0]) == manifest['sha256']
            and sha(paths[1]) == manifest['repeat_sha256'], 'Final/repeated checkpoint hashes differ')
    checkpoints = [torch.load(path, map_location='cpu', weights_only=True) for path in paths]
    for checkpoint in checkpoints:
        validate_saved(checkpoint, manifest['identity'])
    confirm_final_repeat(*checkpoints)
    require(checkpoints[0]['coverage'] == manifest['coverage']
            and checkpoints[0]['supervised_views'] == manifest['supervised_views'],
            'Manifest sampling evidence differs from checkpoint')
    import hashlib
    require(hashlib.sha256(json.dumps(checkpoints[0]['losses']).encode()).hexdigest()
            == manifest['training_loss_sha256'], 'Final training loss evidence differs')
    model = model_code.TCN().cpu().eval()
    model.load_state_dict(checkpoints[0]['state'], strict=True)
    require(sum(p.numel() for p in model.parameters()) == 9701, 'Final class network/head differs')
    return model


def output_aggregates(predicted, blocks, fps):
    # No labels are read; this describes predictions rather than target accuracy.
    counts = {label: 0 for label in ('H', 'A', 'D')}
    durations = []
    for start, stop in blocks:
        last, length = None, 0
        for value in predicted[start:stop]:
            label = str(value)
            counts[label] += 1
            if label == last:
                length += 1
            else:
                if length:
                    durations.append(length / fps)
                last, length = label, 1
        if length:
            durations.append(length / fps)
    total = sum(counts.values())
    return dict(shares={key: value / total for key, value in counts.items()},
                spell_count=len(durations), mean_spell_seconds=sum(durations) / len(durations),
                valid_frames=total, label_free=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--acknowledge-slot-risk', action='store_true', required=True,
                        help='After human review; acknowledges unresolved slot-identity transfer risk')
    args = parser.parse_args()
    os.chdir(PROJECT)
    _, signature, environment = registration(training=False)
    require(args.manifest.resolve().is_relative_to((PROJECT / 'models').resolve()),
            'Use a private winner training manifest')
    manifest_hash = sha(args.manifest)
    manifest = json.loads(args.manifest.read_text())
    validate_manifest(manifest, signature, environment)
    diagnostic = reviewed_diagnostic(Path(manifest['slot_diagnostic']['path']), args.acknowledge_slot_risk)
    require(diagnostic == manifest['slot_diagnostic'], 'Reviewed slot evidence changed after final fit')
    private_root = (PROJECT / 'data/competition').resolve()
    require(args.output.resolve().is_relative_to(private_root)
            and args.output.resolve() not in (private_root, private_root / 'predictions'),
            'Keep this candidate in a separate private data/competition directory')
    require(not args.output.exists(), 'Output directory exists; preserve earlier evidence')
    sys.path[:0] = [str(PROJECT / 'src'), str(PROJECT / 'scripts'),
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
    model = load_winner(manifest, signature, environment, torch, model_code)
    config = json.loads(Path('configs/competition.json').read_text())
    source, blocks = config['sources']['tactical'], config['tactical_half_open_blocks']
    require(config['game'] == 'BAR-ATH' and config['fps'] == 25
            and config['home_team'] == 'Barcelona' and config['away_team'] == 'Atletic Club'
            and config['pitch_metres'] == [105.3, 68.0]
            and source == dict(frames=199319, slots=46)
            and blocks == [[11185, 90652], [110808, 190198]], 'Frozen target contract differs')
    track_path, teams_path = map(Path, TARGET_ASSETS)
    track = load_atd(track_path, source['frames'], source['slots'])
    teams = load_teams(teams_path, source['slots'], config['home_team'], config['away_team'])
    core, names = features(track, teams, blocks, config['pitch_metres'], config['fps'])
    require(names == ['home_distance', 'away_distance', 'distance_margin', 'ball_speed',
                      'edge_distance', 'ball_observed', 'home_observed', 'away_observed', 'gap_age'],
            'Nine core features/order differs')
    encoded = encode(track, teams, blocks, core)
    rotated = rotate180(encoded)
    scaler = np.zeros(model_code.WIDTH), np.ones(model_code.WIDTH)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='tcn-winner-export-', dir=args.output.parent))
    try:
        digests, originals = [], None
        valid = np.zeros(source['frames'], dtype=bool)
        for start, stop in blocks:
            valid[start:stop] = True
        aggregates = None
        for tag, batch in (('first', 1), ('reload', 1), ('batch4', 4)):
            if tag == 'reload':
                model = load_winner(manifest, signature, environment, torch, model_code)
            original = model_code.predict(model, encoded, blocks, scaler, batch=batch)
            rotation = model_code.predict(model, rotated, blocks, scaler, batch=batch)
            if tag == 'first':
                originals = (original.copy(), rotation.copy())
            if tag == 'reload':
                require(np.array_equal(originals[0], original) and np.array_equal(originals[1], rotation),
                        'Original/rotation probabilities changed after reload')
            predicted = decode(average_views(original, rotation), (1 - np.eye(3)) * 16, blocks)
            require((predicted[~valid] == 'X').all() and np.isin(predicted[valid], ['H', 'A', 'D']).all(),
                    'X/graded-block label handling differs')
            path = staging / ('candidate.csv' if tag == 'first' else 'candidate-' + tag + '.csv')
            export_labels(path, predicted, source['frames'])
            reason = official.validate_submission(official.read_label_csv(path), source['frames'])
            require(reason is None, 'Official CSV format validator failed')
            digests.append(sha(path))
            if tag == 'first':
                aggregates = output_aggregates(predicted, blocks, config['fps'])
        require(len(set(digests)) == 1, 'CSV bytes differ across reload/batch4')
        _, after_signature, _ = registration(training=False)
        require(signature == after_signature and sha(args.manifest) == manifest_hash,
                'Export source/assets/manifest changed during inference')
        require(sha(manifest['model']) == manifest['sha256']
                and sha(manifest['repeat_model']) == manifest['repeat_sha256']
                and reviewed_diagnostic(Path(diagnostic['path']), True) == diagnostic,
                'Checkpoint or reviewed diagnostic evidence changed during inference')
        provenance = dict(winner=SCHEMA, model=str(manifest['model']), model_sha256=manifest['sha256'],
                          repeat_model_sha256=manifest['repeat_sha256'], training_manifest_sha256=manifest_hash,
                          export_registration=signature, export_registration_sha256=sha(ROOT / 'inputs.json'),
                          code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                          tracking_sha256=sha(track_path), teams_sha256=sha(teams_path),
                          config_sha256=sha('configs/competition.json'), core_features=names,
                          class_order=['H', 'A', 'D'], rotation_probability_weights=[.5, .5], penalty=16,
                          csv_sha256=digests[0], official_format_validation_passed=True,
                          reload_probabilities_equal_both_views=True, repeated_csv_bytes_equal=True,
                          slot_diagnostic=diagnostic, temporal_slot_continuity_verified=False,
                          label_free_prediction_aggregates=aggregates, dependencies=environment,
                          target_accuracy='unknown', production_promoted=False,
                          full_training_reproduced_in_this_environment=False)
        write_json(staging / 'provenance.json', provenance)
        os.replace(staging, args.output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    with Path('ball.md').open('a') as journal:
        journal.write('\nPrivate staged40k TCN export validated/reloaded/batch4 byte-identically. '
                      'CSV SHA256 ' + digests[0] + '. Production unchanged; target accuracy unknown.\n')
    print('Private candidate format/repeated bytes verified. SHA256', digests[0], flush=True)


if __name__ == '__main__':
    main()
