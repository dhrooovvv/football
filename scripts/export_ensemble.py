"""Production target export script for the promoted frozen 50/50 TCN-Graph50k ensemble."""
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
sys.path[:0] = [
    str(PROJECT / 'src'),
    str(PROJECT / 'scripts'),
    str(PROJECT / 'experiments/tcn-hybrid-2026-11-14'),
    str(PROJECT / 'experiments/graph-long-2026-11-15'),
    str(PROJECT / 'experiments/tcn-pretrain-2026-11-11'),
    str(PROJECT / 'experiments/tcn-rotation-2026-11-11'),
    str(PROJECT / 'reference/more-than-a-hack-2027-main/evaluation')
]

import numpy as np
import torch
import pretrain_model as tcn_code
import hybrid_model
from hybrid_contract import IDS, SEEDS
from rotation import rotate180, average_views
from possession.decode import decode
from possession.inputs import load_atd, load_teams, export_labels
from possession.core import features
from prepare_tcn import encode
import possession_metrics as official

TARGET_ASSETS = (
    PROJECT / 'data/competition/tactical/BAR-ATH_tactical_atd.txt',
    PROJECT / 'data/competition/tactical/BAR-ATH_tactical_atd.xml'
)
OUTPUT_DIR = PROJECT / 'data/competition/tcn-graph-ensemble-exports/local'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_tcn_members(manifest):
    tcn_code.configure()
    members = []
    for seed in (20261106, 20261107):
        entry = manifest['tcn_parent']['members'][str(seed)]
        path = PROJECT / entry['path']
        assert sha(path) == entry['sha256'], f"TCN checkpoint hash mismatch: {path}"
        saved = torch.load(path, map_location='cpu', weights_only=True)
        m = tcn_code.TCN().cpu().eval()
        m.load_state_dict(saved['state'], strict=True)
        members.append(m)
    return members


def load_graph_models(manifest):
    models_by_fold = {}
    for m in IDS:
        models_by_fold[m] = []
        for s in (20261106, 20261107):
            entry = manifest['graph50k_refiner']['folds'][m][str(s)]
            path = PROJECT / entry['path']
            assert sha(path) == entry['sha256'], f"Graph checkpoint hash mismatch: {path}"
            saved = torch.load(path, map_location='cpu', weights_only=True)
            gm = hybrid_model.GraphRefiner().cpu().eval()
            gm.load_state_dict(saved['state'], strict=True)
            models_by_fold[m].append(gm)
    return models_by_fold


def tcn_probabilities(members, encoded, rotated, blocks, batch=1):
    scaler = np.zeros(tcn_code.WIDTH), np.ones(tcn_code.WIDTH)
    views = []
    probabilities = []
    for model in members:
        pair = tuple(tcn_code.predict(model, x, blocks, scaler, batch=batch) for x in (encoded, rotated))
        views.extend(pair)
        probabilities.append(average_views(*pair))
    return average_views(*probabilities), views


def graph_probabilities(models_by_fold, encoded, p_tcn, blocks, batch=4):
    fold_probs = []
    for m in IDS:
        fold_members = models_by_fold[m]
        # Evaluate each member on the encoded features with parent probabilities
        outputs = [hybrid_model.predict(gm, encoded, p_tcn, blocks, batch=batch) for gm in fold_members]
        if all(np.array_equal(output, p_tcn) for output in outputs):
            fold_probs.append(p_tcn.copy())
        else:
            fold_probs.append(average_views(outputs[0], outputs[1]))
    # Average across all 5 cross-validation folds
    mean = np.mean(fold_probs, axis=0)
    return mean / mean.sum(axis=1, keepdims=True)


def output_aggregates(predicted, blocks, fps=25):
    counts = dict.fromkeys(('H', 'A', 'D'), 0)
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
    return {
        'shares': {key: value / total for key, value in counts.items()},
        'spell_count': len(durations),
        'mean_spell_seconds': sum(durations) / len(durations) if durations else 0,
        'valid_frames': total,
        'label_free': True
    }


def main():
    print("=== Generating Final Target Predictions for Promoted 50/50 Ensemble ===", flush=True)
    manifest_path = PROJECT / 'experiments/tcn-graph-ensemble/manifest.json'
    assert manifest_path.exists(), "Manifest missing!"
    with open(manifest_path) as f:
        manifest = json.load(f)

    config_path = PROJECT / 'configs/competition.json'
    with open(config_path) as f:
        config = json.load(f)

    source = config['sources']['tactical']
    blocks = config['tactical_half_open_blocks']
    n_frames = source['frames']
    slots = source['slots']
    assert n_frames == 199319, f"Unexpected frame count: {n_frames}"

    track_path, teams_path = TARGET_ASSETS
    print(f"Loading tracking: {track_path} ...", flush=True)
    track = load_atd(track_path, n_frames, slots)
    print(f"Loading teams: {teams_path} ...", flush=True)
    teams = load_teams(teams_path, slots, config['home_team'], config['away_team'])

    print("Computing features ...", flush=True)
    core, names = features(track, teams, blocks, config['pitch_metres'], config['fps'])
    encoded = encode(track, teams, blocks, core)
    del track, core
    rotated = rotate180(encoded)

    valid = np.zeros(n_frames, dtype=bool)
    for start, stop in blocks:
        valid[start:stop] = True

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pass_hashes = {}
    label_free_aggregates = None

    for tag, batch in (('first', 4), ('reload', 4)):
        t0 = time.time()
        print(f"\n--- Running pass: {tag} (batch={batch}) ---", flush=True)

        # 1. Load fresh models
        tcn_members = load_tcn_members(manifest)
        graph_models = load_graph_models(manifest)

        # 2. Compute TCN base probabilities
        print("Computing TCN probabilities ...", flush=True)
        p_tcn, _ = tcn_probabilities(tcn_members, encoded, rotated, blocks, batch=batch)
        assert p_tcn.shape == (n_frames, 3)
        assert np.all(np.isfinite(p_tcn))

        # 3. Compute Graph50k probabilities
        print("Computing Graph50k probabilities ...", flush=True)
        p_graph = graph_probabilities(graph_models, encoded, p_tcn, blocks, batch=batch)
        assert p_graph.shape == (n_frames, 3)
        assert np.all(np.isfinite(p_graph))

        # 4. Form 50/50 ensemble
        p_ens = 0.5 * p_tcn + 0.5 * p_graph
        assert np.all(np.isfinite(p_ens))
        # Normalize
        row_sums = p_ens.sum(axis=1, keepdims=True)
        p_ens = p_ens / row_sums

        # 5. Decode with frozen Viterbi decoder (penalty = 16)
        print("Decoding with frozen Viterbi decoder (penalty=16) ...", flush=True)
        pred = decode(p_ens, (1 - np.eye(3)) * 16, blocks)
        pred[~valid] = 'X'

        # 6. Export and validate
        filename = 'candidate.csv' if tag == 'first' else f'candidate-{tag}.csv'
        out_path = OUTPUT_DIR / filename
        export_labels(out_path, pred, n_frames)

        # Validate with official submission validator
        val_error = official.validate_submission(official.read_label_csv(out_path), n_frames)
        assert val_error is None, f"Official format validator failed: {val_error}"

        csv_hash = sha(out_path)
        pass_hashes[tag] = csv_hash
        print(f"Pass {tag} complete in {time.time()-t0:.1f}s. CSV SHA256: {csv_hash}", flush=True)

        if tag == 'first':
            label_free_aggregates = output_aggregates(pred, blocks, config['fps'])

    # Verify identical bytes across all three passes
    assert len(set(pass_hashes.values())) == 1, f"CSV bytes differ across passes: {pass_hashes}"
    final_sha = pass_hashes['first']
    print(f"\nAll passes verified byte-identical! SHA256: {final_sha}", flush=True)

    # Save provenance metadata
    provenance = {
        'schema': 'tcn_graph50k_ensemble_private_export_v1',
        'export_date': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'completed': True,
        'manifest': str(manifest_path.relative_to(PROJECT)),
        'manifest_sha256': sha(manifest_path),
        'csv_sha256': final_sha,
        'pass_hashes': pass_hashes,
        'official_validation_passed': True,
        'frame_count': n_frames,
        'label_free_aggregates': label_free_aggregates,
        'production_promoted': True,
        'target_accuracy': 'unknown'
    }

    with open(OUTPUT_DIR / 'provenance.json', 'w') as f:
        json.dump(provenance, f, indent=2)

    print("Provenance saved to:", OUTPUT_DIR / 'provenance.json', flush=True)


if __name__ == '__main__':
    main()
