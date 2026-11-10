"""User-run local CSV format and repeatability checks for a final 53-match TCN."""
import argparse
from datetime import date, datetime
from importlib.metadata import version
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

import numpy as np
import torch
from catboost import CatBoostClassifier

from possession.core import features
from possession.decode import decode
from possession.inputs import load_atd, load_teams, export_labels
from prepare_tcn import encode, sha

sys.path.insert(0, str(Path("experiments/tcn-2026-11-10").resolve()))
from tcn_candidate import TCN, WIDTH, configure, predict
sys.path.insert(0, str(Path("reference/more-than-a-hack-2027-main/evaluation").resolve()))
import possession_metrics as official

ROOT = Path("experiments/neural-export-2026-11-11")


def registration():
    if datetime.now(ZoneInfo("Asia/Kolkata")).date() > date(2026, 11, 17):
        raise RuntimeError("The project end date has passed")
    for name in ("protocol.md", "inputs.json"):
        path = ROOT / name
        if subprocess.check_output(["git", "show", "HEAD:" + str(path)]) != path.read_bytes():
            raise RuntimeError("Export registration differs from the committed version")
    for path, digest in json.loads((ROOT / "inputs.json").read_text()).items():
        if sha(path) != digest:
            raise RuntimeError(f"Registered export input changed in {path}")
    expected_env = json.loads(Path("experiments/tcn-2026-11-10/environment.json").read_text())
    for name, expected in expected_env.items():
        if version(name) != expected:
            raise RuntimeError(f"Dependency version differs for {name}")


def load_final_tcn(manifest_path):
    manifest = json.loads(manifest_path.read_text())
    path = Path(manifest["model"])
    if sha(path) != manifest["sha256"]:
        raise RuntimeError("Final checkpoint differs from its training manifest")
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    members = json.loads(Path("experiments/tcn-expanded-2026-11-10/membership.json").read_text())
    expected = [item["key"] for item in members["training"]]
    if checkpoint.get("training_matches") != expected or manifest.get("training_matches") != expected:
        raise RuntimeError("Checkpoint is not the registered final 53-match fit")
    if not manifest.get("repeated_training_exact") or checkpoint.get("registration") != manifest.get("registration"):
        raise RuntimeError("Training registration or repeated-fit proof differs")
    if checkpoint.get("steps") != 20000 or checkpoint.get("seed") != 20261106:
        raise RuntimeError("Training budget or seed differs from the registered fit")
    mean = np.asarray(checkpoint["mean"], dtype=np.float64)
    scale = np.asarray(checkpoint["scale"], dtype=np.float64)
    if mean.shape != (WIDTH,) or scale.shape != (WIDTH,) or not np.array_equal(mean, np.zeros(WIDTH)) or not np.array_equal(scale, np.ones(WIDTH)):
        raise RuntimeError("Checkpoint normalization differs from the frozen representation")
    model = TCN().cpu().eval()
    model.load_state_dict(checkpoint["state"])
    return model, (mean, scale), path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registration()
    private_root = Path("data/competition").resolve()
    if not args.output.resolve().is_relative_to(private_root):
        raise RuntimeError("Keep candidate outputs inside the ignored data/competition directory")
    if args.output.exists():
        raise RuntimeError("Choose a new output directory to preserve earlier evidence")
    if args.output.resolve() == Path("data/competition/predictions").resolve():
        raise RuntimeError("Use a separate candidate directory for this export check")
    configure()
    model, scaler, model_path = load_final_tcn(args.manifest)
    cfg = json.loads(Path("configs/competition.json").read_text())
    source = cfg["sources"]["tactical"]
    base = Path("data/competition/tactical/BAR-ATH_tactical")
    track_path = Path(str(base) + "_atd.txt")
    teams_path = Path(str(base) + "_atd.xml")
    track = load_atd(track_path, source["frames"], source["slots"])
    teams = load_teams(teams_path, source["slots"], cfg["home_team"], cfg["away_team"])
    blocks = cfg["tactical_half_open_blocks"]
    core, names = features(track, teams, blocks, cfg["pitch_metres"], cfg["fps"])
    encoded = encode(track, teams, blocks, core)
    cat_path = Path("models/core-final.cbm")
    cat = CatBoostClassifier()
    cat.load_model(str(cat_path))
    classes = list(cat.classes_)
    if len(classes) != 3 or set(classes) != {"H", "A", "D"}:
        raise RuntimeError("CatBoost class mapping differs")
    cat_probabilities = cat.predict_proba(core, thread_count=1)[:, [classes.index(c) for c in ("H", "A", "D")]]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="neural-export-", dir=args.output.parent))
    try:
        digests = []
        for tag, batch in (("first", 1), ("reload", 1), ("batch4", 4)):
            if tag == "reload":
                model, scaler, _ = load_final_tcn(args.manifest)
            neural = predict(model, encoded, blocks, scaler, batch=batch)
            probabilities = .5 * neural + .5 * cat_probabilities
            probabilities /= probabilities.sum(axis=1, keepdims=True)
            predicted = decode(probabilities, (1 - np.eye(3)) * 16, blocks)
            valid = np.zeros(len(predicted), dtype=bool)
            for start, stop in blocks:
                valid[start:stop] = True
            if not (predicted[~valid] == "X").all():
                raise RuntimeError("Output outside the configured half blocks differs from X")
            path = staging / ("candidate.csv" if tag == "first" else "candidate-" + tag + ".csv")
            export_labels(path, predicted, source["frames"])
            official.validate_submission(official.read_label_csv(path), source["frames"])
            digests.append(sha(path))
        if len(set(digests)) != 1:
            raise RuntimeError("CSV bytes differ across reload or batch size")
        provenance = dict(model=str(model_path), model_sha256=sha(model_path),
                          training_manifest_sha256=sha(args.manifest), catboost_sha256=sha(cat_path),
                          export_registration_sha256=sha(ROOT / "inputs.json"),
                          code_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                          tracking_sha256=sha(track_path), teams_sha256=sha(teams_path),
                          config_sha256=sha("configs/competition.json"), core_features=names,
                          blend_weights=[.5, .5], penalty=16, csv_sha256=digests[0],
                          official_format_validation_passed=True, repeated_csv_bytes_equal=True,
                          target_accuracy="unknown", temporal_slot_continuity_verified=False,
                          production_promoted=False,
                          dependencies={name: version(name) for name in ("torch", "numpy", "pandas", "catboost", "scipy")})
        (staging / "provenance.json").write_text(json.dumps(provenance, indent=2))
        os.replace(staging, args.output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    print("Candidate CSV format and repeated bytes verified. SHA256", digests[0], flush=True)
    with Path("ball.md").open("a") as journal:
        journal.write("\nNeural candidate local format/repeatability export completed in " + str(args.output) + ". CSV SHA256 " + digests[0] + ". Target accuracy unknown.\n")


if __name__ == "__main__":
    main()
