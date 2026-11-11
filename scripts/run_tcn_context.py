"""User-run fixed longer-context TCN trial; retained IDSSE distribution and budget."""
import argparse
from contextlib import contextmanager
from datetime import date, datetime
import fcntl
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

import numpy as np
import torch
import time

import run_tcn_expanded as engine
from run_tcn_expanded import write_json, training_coverage
from possession.core import promote
from possession.decode import decode
from possession.inputs import export_labels
from review_frozen import score
from evaluate_pff import missing
from prepare_tcn import sha

ROOT = Path("experiments/tcn-context-2026-11-11")
DATA = Path("data/tcn-context")
MODELS = Path("models/tcn-context")
ORIGINAL_ROOT = Path("experiments/tcn-expanded-2026-11-10")
ORIGINAL_DATA = Path("data/tcn-expanded")
sys.path.insert(0, str(ROOT.resolve()))
from context_training import train_fit
from context_model import TCN, predict


def check_date():
    if datetime.now(ZoneInfo("Asia/Kolkata")).date() >= date(2026, 11, 16):
        raise RuntimeError("New research closes at the beginning of November 16")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def registration():
    check_date()
    for name in ("protocol.md", "inputs.json"):
        path = ROOT / name
        require(subprocess.check_output(["git", "show", "HEAD:" + str(path)]) == path.read_bytes(),
                "Registration differs from the committed version")
    locked = json.loads((ROOT / "inputs.json").read_text())
    for path, digest in locked["code"].items():
        require(sha(path) == digest, "Registered code changed in " + path)
    for package, expected in json.loads(Path("experiments/tcn-2026-11-10/environment.json").read_text()).items():
        require(version(package) == expected, "Dependency version differs for " + package)
    development = json.loads(Path("experiments/core-development/split.json").read_text())
    original = json.loads((ORIGINAL_ROOT / "membership.json").read_text())
    members = {"training": [item for item in original["training"] if item["provider"] == "idsse"]}
    expected = ["idsse-" + match for match in development["development"]]
    protected = {"idsse-" + match for match in development["sealed"]}
    require([item["key"] for item in members["training"]] == expected and len(expected) == 5
            and not set(expected) & protected, "Training membership differs from the five IDSSE split")
    for item in members["training"]:
        require(item["provider"] == item["key"].split("-", 1)[0], "Provider identity differs")
        path = str(ORIGINAL_DATA / item["key"] / "manifest.json")
        require(sha(path) == locked["prepared_manifests"][path], "Prepared manifest changed in " + path)
    digest = hashlib.sha256((sha(ROOT / "protocol.md") + sha(ROOT / "inputs.json")).encode()).hexdigest()
    return members, locked, digest


@contextmanager
def operation_lock():
    DATA.mkdir(parents=True, exist_ok=True)
    handles = []
    try:
        # Also exclude simultaneous writes/preparation by the old expanded runner.
        for directory in (ORIGINAL_DATA, DATA):
            handle = (directory / "operation.lock").open("a+")
            handles.append(handle)
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError("Another context or compact-input operation is running") from error
        yield
    finally:
        for handle in reversed(handles):
            handle.close()


def run_checks():
    suites = ("tests", "experiments/tcn-2026-11-10/tests", "experiments/tcn-gap-2026-11-10/tests",
              str(ORIGINAL_ROOT / "tests"), str(ROOT / "tests"))
    logs = []
    for suite in suites:
        completed = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", suite, "-v"],
                                   capture_output=True, text=True)
        logs.append(suite + "\n" + completed.stdout + completed.stderr)
        (ROOT / "checks.txt").write_text("\n".join(logs))
        require(completed.returncode == 0, "Contract checks failed; preserve checks.txt and report the failure")
    print("All user-run contract checks passed", flush=True)


def configure_engine():
    # Reuse pinned checkpoint and scoring helpers in this isolated process.
    # Candidate evaluation below changes the fold size to four IDSSE matches.
    engine.ROOT = ROOT
    engine.DATA = DATA
    engine.MODELS = MODELS
    engine.train_fit = train_fit
    engine.TCN = TCN
    engine.predict = predict
    engine.check_date = check_date


def load_cases(members, locked):
    cases = []
    for item in members["training"]:
        path = ORIGINAL_DATA / item["key"]
        # Full array hashes are checked locally by the user, not during preparation.
        case, manifest = engine.verify_prepared(path, locked["prepared_registration"])
        require(case.provider == item["provider"], "Prepared provider differs from membership")
        cases.append(case)
    return cases


def verify_completed_folds(members, signature):
    expected = [item["key"] for item in members["training"]]
    development = [item["match"] for item in members["training"] if item["provider"] == "idsse"]
    for match in development:
        path = ROOT / "evaluation" / (match + ".json")
        if not path.exists():
            continue
        fold = json.loads(path.read_text())
        require(fold["registration"] == signature, "Completed fold registration differs")
        require(fold["training_matches"] == [key for key in expected if key != "idsse-" + match],
                "Completed fold membership differs")
        rows = fold["rows"]
        require(len(rows) == 2 and {(r["match"], r["condition"]) for r in rows}
                == {(match, "clean"), (match, "targetlike")}, "Completed fold conditions differ")
        require(set(fold["training_coverage"]) == set(fold["training_matches"]), "Fold coverage differs")
        for row in rows:
            require(row["repeated_training_exact"], "Completed fold repeat-fit proof missing")
            for tag in ("first", "repeat", "batch4"):
                csv = DATA / "predictions" / (match + "-" + row["condition"] + "-" + tag + ".csv")
                require(sha(csv) == row["csv_sha256"], "Completed fold CSV hash differs")



def verified_gate(members, signature):
    """Accept only the exact complete, independently checked result set."""
    verify_completed_folds(members, signature)
    ids = [item["match"] for item in members["training"] if item["provider"] == "idsse"]
    expected_files = {match + ".json" for match in ids}
    actual_files = {path.name for path in (ROOT / "evaluation").glob("J*.json")}
    require(len(ids) == 5 and actual_files == expected_files, "All five exact registered fold files are required")
    rows = []
    for match in ids:
        rows.extend(json.loads((ROOT / "evaluation" / (match + ".json")).read_text())["rows"])
    require(rows == json.loads((ROOT / "evaluation/results.json").read_text()), "Aggregate/fold result rows differ")
    baseline = {}
    candidate = {}
    primary = {}
    for match in ids:
        pair = [row for row in rows if row["match"] == match]
        for row in pair:
            for arm in ("parent", "candidate"):
                for metric in ("spellF1", "macroF1"):
                    value = row[arm][metric]
                    require(isinstance(value, (int, float)) and np.isfinite(value) and 0 <= value <= 1,
                            "Invalid recorded metric")
        for arm, output in (("parent", baseline), ("candidate", candidate)):
            output[match] = tuple(float(np.mean([row[arm][metric] for row in pair]))
                                  for metric in ("spellF1", "macroF1"))
        primary[match] = next(row["candidate"]["spellF1"] - row["parent"]["spellF1"]
                              for row in pair if row["condition"] == "targetlike")
    primary_median = float(np.median(list(primary.values())))
    eligible = bool(engine.promote(baseline, candidate, True) and primary_median >= .01)
    saved = json.loads((ROOT / "evaluation/gate.json").read_text())
    require(saved["quality_eligible"] == eligible, "Saved gate disagrees with complete fold metrics")
    deltas = {"primary_deltas": primary,
              "paired_spell_deltas": {match: candidate[match][0] - baseline[match][0] for match in ids},
              "paired_macro_deltas": {match: candidate[match][1] - baseline[match][1] for match in ids}}
    for name, values in deltas.items():
        require(set(saved[name]) == set(ids) and all(abs(saved[name][match] - value) < 1e-12
                                                    for match, value in values.items()), "Saved gate deltas differ")
    require(abs(saved["primary_median_delta"] - primary_median) < 1e-12
            and saved["matches_improved"] == sum(candidate[match][0] > baseline[match][0] for match in ids),
            "Saved gate summary differs")
    require(saved["contract_checks_passed"] and saved["repeated_training_exact"]
            and saved["csv_repeatability_cases"] == 10, "Required correctness evidence is incomplete")
    return eligible


def evaluate(cases, signature, locked):
    results_dir = ROOT / "evaluation"
    results_dir.mkdir(exist_ok=True)
    private = DATA / "predictions"
    private.mkdir(exist_ok=True)
    all_rows = []
    scaler = np.zeros(521), np.ones(521)
    for held in json.loads(Path("experiments/core-development/split.json").read_text())["development"]:
        held_key = "idsse-" + held
        training = [case for case in cases if case.key != held_key]
        if len(training) != 4 or held_key in {case.key for case in training}:
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
        model, coverage = engine.fit_twice(training, MODELS / "evaluation" / held, signature)
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
    report = "# Longer-context IDSSE TCN comparison\n\n|Match|Setting|Parent spell|Candidate spell|Parent macro|Candidate macro|\n|---|---|---:|---:|---:|---:|\n"
    for row in all_rows:
        old, new = row["parent"], row["candidate"]
        report += (f"|{row['match']}|{row['condition']}|{old['spellF1']:.6f}|{new['spellF1']:.6f}"
                   f"|{old['macroF1']:.6f}|{new['macroF1']:.6f}|\n")
    (results_dir / "report.md").write_text(report + "\n```json\n" + json.dumps(gate, indent=2) + "\n```\n")
    print(json.dumps(gate, indent=2), flush=True)
    with Path("ball.md").open("a") as journal:
        journal.write("\nLonger-context TCN evaluation recorded. " + json.dumps(gate) + "\n")


def record_decision():
    gate = json.loads((ROOT / "evaluation/gate.json").read_text())
    write_json(ROOT / "decision.json", dict(quality_eligible=gate["quality_eligible"],
               parent="retained_IDSSE_gap_blend_penalty16", architecture="dense_context_325",
               data_expansion_track_remains_stopped=True, production_changed=False,
               clean_environment_verified=False, automatic_followup=False))
    print("Development gate " + ("provisionally passed" if gate["quality_eligible"] else "FAILED; reject this context trial"), flush=True)
    with Path("ball.md").open("a") as journal:
        journal.write("\nLonger-context TCN development trial completed. " + json.dumps(gate) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check", action="store_true")
    actions.add_argument("--run", action="store_true")
    args = parser.parse_args()
    members, locked, signature = registration()
    with operation_lock():
        run_checks()
        if args.check:
            return
        for path, digest in locked["data"].items():
            require(sha(path) == digest, "Evaluation reference/input changed in " + path)
        configure_engine()
        engine.configure()
        cases = load_cases(members, locked)
        verify_completed_folds(members, signature)
        evaluate(cases, signature, locked)
        verified_gate(members, signature)
        record_decision()


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        write_json(ROOT / "last-failure.json", dict(error_type=type(error).__name__,
                                                         message=str(error), production_changed=False))
        with Path("ball.md").open("a") as journal:
            journal.write("\nLonger-context TCN stopped; preserve last-failure.json and review before retry.\n")
        raise
