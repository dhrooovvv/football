"""User-run TCN preparation, five-match evaluation and full eligible-pool fitting."""
import argparse
from contextlib import contextmanager
from datetime import date, datetime
import fcntl
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from zoneinfo import ZoneInfo

import numpy as np
import torch

ROOT = Path("experiments/tcn-expanded-2026-11-10")
DATA = Path("data/tcn-expanded")
MODELS = Path("models/tcn-expanded")
sys.path.insert(0, str(ROOT.resolve()))
from expanded_data import CompactCase, FILES, pack_case, valid_windows
from expanded_training import train_fit, confirm_repeat
from prepare_tcn import encode, sha
from prepare_tcn_gap import mask_ball
from possession.core import features, promote
from possession.external import load_match
from possession.inputs import Tracking, export_labels
from possession.pff import load_pff
from possession.decode import decode
from review_frozen import score
from evaluate_pff import missing
sys.path.insert(0, str(Path("experiments/tcn-2026-11-10").resolve()))
from tcn_candidate import configure, predict, TCN, WIDTH


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False))
    os.replace(temporary, path)


def check_date():
    if datetime.now(ZoneInfo("Asia/Kolkata")).date() >= date(2026, 11, 16):
        raise RuntimeError("Research starts close at the beginning of November 16")


def registration():
    check_date()
    for name in ("protocol.md", "membership.json", "inputs.json"):
        path = ROOT / name
        if subprocess.check_output(["git", "show", "HEAD:" + str(path)]) != path.read_bytes():
            raise RuntimeError(f"Registration differs from committed version in {path}")
    locked = json.loads((ROOT / "inputs.json").read_text())
    for path, digest in locked["code"].items():
        if sha(path) != digest:
            raise RuntimeError(f"Registered code changed in {path}")
    expected_env = json.loads(Path("experiments/tcn-2026-11-10/environment.json").read_text())
    for package, expected in expected_env.items():
        if version(package) != expected:
            raise RuntimeError(f"Dependency version changed for {package}")
    members = json.loads((ROOT / "membership.json").read_text())
    development = json.loads(Path("experiments/core-development/split.json").read_text())
    pff = json.loads(Path("experiments/pff-evaluation/cohort.json").read_text())
    expected = ["idsse-" + match for match in development["development"]]
    expected += ["pff-" + match for match in pff["training"]]
    protected = {"idsse-" + match for match in development["sealed"]}
    protected.update("pff-" + match for match in pff["transfer_holdout"])
    keys = [item["key"] for item in members["training"]]
    if keys != expected or len(keys) != 53 or set(keys) & protected:
        raise RuntimeError("Training membership differs from the approved 53-match split")
    signature = sha(ROOT / "protocol.md") + sha(ROOT / "inputs.json") + sha(ROOT / "membership.json")
    return members, locked, hashlib.sha256(signature.encode()).hexdigest()


@contextmanager
def operation_lock():
    DATA.mkdir(parents=True, exist_ok=True)
    with (DATA / "operation.lock").open("a+") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("Another expanded-data command is already running") from error
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def source_check(item, locked):
    for path in item["inputs"]:
        if sha(path) != locked["data"][path]:
            raise RuntimeError(f"Registered source changed in {path}")


def verify_prepared(directory, signature):
    manifest = json.loads((directory / "manifest.json").read_text())
    if set(manifest["files"]) != set(FILES) | {"metadata.json"}:
        raise RuntimeError("Unexpected compact file manifest")
    for name, digest in manifest["files"].items():
        if sha(directory / name) != digest:
            raise RuntimeError(f"Prepared file changed in {directory / name}")
    case = CompactCase(directory)
    if case.key != directory.name:
        raise RuntimeError("Prepared case identity differs from its directory")
    if case.metadata["registration"] != signature:
        raise RuntimeError("Prepared match belongs to a different registration")
    valid_windows([case])
    return case, manifest


def prepare(members, locked, signature):
    target = json.loads(Path("data/diagnostics-review/target-shift.json").read_text())
    if sha("data/diagnostics-review/target-shift.json") != locked["data"]["data/diagnostics-review/target-shift.json"]:
        raise RuntimeError("Frozen corruption distribution changed")
    rows = []
    for index, item in enumerate(members["training"]):
        check_date()
        directory = DATA / item["key"]
        if directory.exists():
            case, manifest = verify_prepared(directory, signature)
            rows.append(case.metadata)
            print("Verified existing prepared match", item["key"], flush=True)
            continue
        source_check(item, locked)
        started = time.monotonic()
        if item["provider"] == "idsse":
            clean_path, gap_path = item["inputs"]
            with np.load(clean_path) as clean_case, np.load(gap_path) as gap_case:
                clean = clean_case["x"]
                augmented = gap_case["x"]
                labels = clean_case["y"]
                blocks = clean_case["blocks"].tolist()
                if not np.array_equal(labels, gap_case["y"]) or not np.array_equal(blocks, gap_case["blocks"]):
                    raise RuntimeError("IDSSE training-view alignment mismatch")
        else:
            track, teams, blocks, pitch, labels, counts = load_pff("data/pff/release", item["match"])
            base_core, _ = features(track, teams, blocks, pitch)
            with np.load(item["admitted_features"]) as admitted:
                if not np.array_equal(labels, admitted["y"]) or not np.array_equal(blocks, admitted["blocks"]):
                    raise RuntimeError("PFF labels or halves differ from admitted version")
                if not np.allclose(base_core, admitted["x"], equal_nan=True, atol=0, rtol=0):
                    raise RuntimeError("PFF core features differ from admitted version")
            clean = encode(track, teams, blocks, base_core)
            ball = mask_ball(track.ball, blocks, target["missing_runs"], target["observed_runs"],
                             target["missing_fraction"], 20261206 + index)
            gap_track = Tracking(track.players, ball)
            gap_core, _ = features(gap_track, teams, blocks, pitch)
            augmented = encode(gap_track, teams, blocks, gap_core)
            del track, gap_track, base_core, gap_core, ball
        valid = labels != "X"
        metadata = dict(key=item["key"], provider=item["provider"], match=item["match"],
                        registration=signature, training_gap_seed=20261206 + index,
                        graded_frames=int(valid.sum()),
                        clean_missing_fraction=float((clean[valid, -4] == 0).mean()),
                        training_gap_missing_fraction=float((augmented[valid, -4] == 0).mean()))
        staging = Path(tempfile.mkdtemp(prefix=item["key"] + ".partial-", dir=DATA))
        try:
            pack_case(staging, clean, augmented, labels, blocks, metadata)
            case = CompactCase(staging)
            valid_windows([case])
            payload = {name: sha(staging / name) for name in (*FILES, "metadata.json")}
            write_json(staging / "manifest.json", dict(files=payload))
            del case
            os.replace(staging, directory)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
        del clean, augmented, labels
        rows.append(metadata)
        print(f"Prepared {item['key']} in {time.monotonic() - started:.1f}s", flush=True)
    write_json(DATA / "preparation.json", dict(registration=signature, matches=rows))
    print("Prepared and verified all 53 eligible matches", flush=True)


def prepared_cases(members, signature):
    cases = []
    fingerprints = {}
    for item in members["training"]:
        directory = DATA / item["key"]
        case, manifest = verify_prepared(directory, signature)
        cases.append(case)
        fingerprints[case.key] = manifest["files"]
    fingerprint = hashlib.sha256(json.dumps(fingerprints, sort_keys=True).encode()).hexdigest()
    return cases, signature + fingerprint


def fit_twice(cases, directory, signature):
    check_date()
    first, losses, coverage = train_fit(cases, directory / "first", signature)
    check_date()
    second, repeated_losses, repeated_coverage = train_fit(cases, directory / "repeat", signature)
    confirm_repeat(first, second, losses, repeated_losses, coverage, repeated_coverage)
    return first, coverage


def training_coverage(cases, coverage):
    records = valid_windows(cases)
    available = {case.key: 0 for case in cases}
    for index, _, count in records:
        available[cases[index].key] += count
    return {case.key: dict(provider=case.provider, available_window_starts=available[case.key],
                           sampled_windows=coverage[case.key]) for case in cases}


def evaluate(cases, signature, locked):
    results_dir = ROOT / "evaluation"
    results_dir.mkdir(exist_ok=True)
    private = DATA / "predictions"
    private.mkdir(exist_ok=True)
    all_rows = []
    scaler = np.zeros(WIDTH), np.ones(WIDTH)
    for held in json.loads(Path("experiments/core-development/split.json").read_text())["development"]:
        held_key = "idsse-" + held
        training = [case for case in cases if case.key != held_key]
        if len(training) != 52 or held_key in {case.key for case in training}:
            raise RuntimeError("Held-out match leakage or wrong training count")
        completed = results_dir / (held + ".json")
        if completed.exists():
            prior = json.loads(completed.read_text())
            if prior["registration"] != signature:
                raise RuntimeError("Fold result registration mismatch")
            all_rows.extend(prior["rows"])
            print("Retained completed fold", held, flush=True)
            continue
        started = time.monotonic()
        model, coverage = fit_twice(training, MODELS / "evaluation" / held, signature)
        saved = torch.load(MODELS / "evaluation" / held / "first" / "progress.pt", map_location="cpu", weights_only=True)
        reloaded = TCN().eval()
        reloaded.load_state_dict(saved["state"])
        rows = []
        for setting in ("clean", "targetlike"):
            key = held + "-" + setting
            path = "data/tcn-prepared/" + key + ".npz"
            cat_path = "data/diagnostics-review/" + key + "-probs.npz"
            parent_path = "data/tcn-gap/" + key + "-first.csv"
            for source in (path, cat_path, parent_path):
                if sha(source) != locked["data"][source]:
                    raise RuntimeError("Evaluation input or reference changed")
            with np.load(path) as data:
                x, labels, blocks = data["x"], data["y"], data["blocks"].tolist()
            cat = np.load(cat_path)["p"]
            parent = np.loadtxt(parent_path, delimiter=",", skiprows=1, usecols=1, dtype=str)
            outputs = []
            standalone = None
            first_probabilities = None
            for repetition, batch in enumerate((1, 1, 4)):
                prediction_model = reloaded if repetition == 1 else model
                neural = predict(prediction_model, x, blocks, scaler, batch=batch)
                if repetition == 0:
                    first_probabilities = neural
                elif repetition == 1 and not np.array_equal(first_probabilities, neural):
                    raise RuntimeError("Reloaded probabilities differ")
                if standalone is None:
                    standalone = decode(neural, (1 - np.eye(3)) * 16, blocks)
                mixture = .5 * neural + .5 * cat
                mixture /= mixture.sum(axis=1, keepdims=True)
                outputs.append(decode(mixture, (1 - np.eye(3)) * 16, blocks))
            digests = []
            for tag, predicted in zip(("first", "repeat", "batch4"), outputs):
                export = private / (key + "-" + tag + ".csv")
                export_labels(export, predicted, len(labels))
                digests.append(sha(export))
            if len(set(digests)) != 1:
                raise RuntimeError("Inference CSV differs across repetitions or batch size")
            rows.append(dict(match=held, condition=setting, parent=score(labels, parent, blocks),
                             candidate=score(labels, outputs[0], blocks),
                             standalone_tcn=score(labels, standalone, blocks),
                             candidate_missing_ball=missing(labels, outputs[0], x[:, -4] == 0),
                             csv_sha256=digests[0], repeated_training_exact=True))
        record = dict(registration=signature, training_matches=[case.key for case in training],
                      training_coverage=training_coverage(training, coverage), rows=rows,
                      seconds=time.monotonic() - started)
        write_json(completed, record)
        all_rows.extend(rows)
        print("Evaluated held-out match", held, flush=True)
    ids = [row["match"] for row in all_rows if row["condition"] == "clean"]
    def pairs(arm):
        return {match: tuple(np.mean([[row[arm]["spellF1"], row[arm]["macroF1"]]
                                     for row in all_rows if row["match"] == match], axis=0)) for match in ids}
    baseline, candidate = pairs("parent"), pairs("candidate")
    primary = {row["match"]: row["candidate"]["spellF1"] - row["parent"]["spellF1"]
               for row in all_rows if row["condition"] == "targetlike"}
    median = float(np.median(list(primary.values())))
    gate = dict(quality_eligible=bool(promote(baseline, candidate, True) and median >= .01),
                primary_median_delta=median, primary_deltas=primary,
                paired_spell_deltas={match: float(candidate[match][0] - baseline[match][0]) for match in ids},
                paired_macro_deltas={match: float(candidate[match][1] - baseline[match][1]) for match in ids},
                matches_improved=sum(bool(candidate[match][0] > baseline[match][0]) for match in ids),
                production_changed=False, sealed_opened=False, pff_holdout_opened=False,
                contract_checks_passed=True, repeated_training_exact=True,
                csv_repeatability_cases=10, clean_environment_verified=False)
    write_json(results_dir / "results.json", all_rows)
    write_json(results_dir / "gate.json", gate)
    report = "# Expanded-data TCN comparison\n\n|Match|Setting|Parent spell|Candidate spell|Parent macro|Candidate macro|\n|---|---|---:|---:|---:|---:|\n"
    for row in all_rows:
        old, new = row["parent"], row["candidate"]
        report += (f"|{row['match']}|{row['condition']}|{old['spellF1']:.6f}|{new['spellF1']:.6f}"
                   f"|{old['macroF1']:.6f}|{new['macroF1']:.6f}|\n")
    (results_dir / "report.md").write_text(report + "\n```json\n" + json.dumps(gate, indent=2) + "\n```\n")
    print(json.dumps(gate, indent=2), flush=True)
    with Path("ball.md").open("a") as journal:
        journal.write("\nExpanded-data TCN evaluation completed. " + json.dumps(gate) + "\n")


def fit_final(cases, signature):
    model, coverage = fit_twice(cases, MODELS / "final", signature)
    path = MODELS / "final" / "tcn-53-matches.pt"
    payload = dict(state=model.state_dict(), mean=[0.] * WIDTH, scale=[1.] * WIDTH,
                   training_matches=[case.key for case in cases], registration=signature,
                   steps=20000, seed=20261106, production_promoted=False)
    write_checkpoint_path = path.with_suffix(".tmp")
    torch.save(payload, write_checkpoint_path)
    os.replace(write_checkpoint_path, path)
    loaded = torch.load(path, map_location="cpu", weights_only=True)
    restored = TCN().eval()
    restored.load_state_dict(loaded["state"])
    if not all(torch.equal(value, restored.state_dict()[key]) for key, value in model.state_dict().items()):
        raise RuntimeError("Final checkpoint reload differs")
    record = dict(model=str(path), sha256=sha(path), training_matches=payload["training_matches"],
                  coverage=training_coverage(cases, coverage), repeated_training_exact=True,
                  production_promoted=False, registration=signature)
    write_json(ROOT / "final-model.json", record)
    print("Final model trained on all 53 eligible matches:", path, flush=True)
    with Path("ball.md").open("a") as journal:
        journal.write("\nFull 53-match TCN fit completed. Model " + str(path) + ". Review development gate before use.\n")


def run_checks():
    suites = ("tests", "experiments/tcn-2026-11-10/tests", "experiments/tcn-gap-2026-11-10/tests", str(ROOT / "tests"))
    logs = []
    for suite in suites:
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", suite, "-v"], capture_output=True, text=True)
        logs.append(suite + "\n" + result.stdout + result.stderr)
        (ROOT / "checks.txt").write_text("\n".join(logs))
        if result.returncode:
            raise RuntimeError("Contract checks failed. See checks.txt")
    print("All contract checks passed", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    for action in ("run", "check", "prepare", "evaluate", "fit-final"):
        actions.add_argument("--" + action, action="store_true")
    args = parser.parse_args()
    members, locked, signature = registration()
    with operation_lock():
        run_checks()
        if args.check:
            return
        if args.run or args.prepare:
            prepare(members, locked, signature)
        if args.prepare:
            return
        configure()
        cases, training_signature = prepared_cases(members, signature)
        if args.run or args.evaluate:
            evaluate(cases, training_signature, locked)
        if args.run or args.fit_final:
            fit_final(cases, training_signature)


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        failure = dict(error_type=type(error).__name__, message=str(error), production_changed=False)
        write_json(ROOT / "last-failure.json", failure)
        with Path("ball.md").open("a") as journal:
            journal.write("\nExpanded-data TCN command stopped. See experiments/tcn-expanded-2026-11-10/last-failure.json.\n")
        raise
