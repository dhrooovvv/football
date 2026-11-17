"""User-run fixed provider-balanced TCN trial; archived experiments stay unchanged."""
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

import run_tcn_expanded as engine
from prepare_tcn import sha

ROOT = Path("experiments/tcn-balanced-2026-11-11")
DATA = Path("data/tcn-balanced")
MODELS = Path("models/tcn-balanced")
ORIGINAL_ROOT = Path("experiments/tcn-expanded-2026-11-10")
ORIGINAL_DATA = Path("data/tcn-expanded")
sys.path.insert(0, str(ROOT.resolve()))
from balanced_training import train_fit


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
    cohort = json.loads(Path("experiments/pff-evaluation/cohort.json").read_text())
    members = json.loads((ORIGINAL_ROOT / "membership.json").read_text())
    expected = ["idsse-" + match for match in development["development"]]
    expected += ["pff-" + match for match in cohort["training"]]
    protected = {"idsse-" + match for match in development["sealed"]}
    protected.update("pff-" + match for match in cohort["transfer_holdout"])
    require([item["key"] for item in members["training"]] == expected and len(expected) == 53
            and not set(expected) & protected, "Training membership differs from the protected split")
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
                raise RuntimeError("Another balanced or expanded operation is running") from error
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
    # Reuse the pinned scorer/evaluator verbatim in this isolated process. Only
    # output paths and the provider-balanced training function are substituted.
    engine.ROOT = ROOT
    engine.DATA = DATA
    engine.MODELS = MODELS
    engine.train_fit = train_fit
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
    """Final fitting accepts only the exact complete, independently checked result set."""
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


def supplement():
    rows = json.loads((ROOT / "evaluation/results.json").read_text())
    reference = json.loads((ORIGINAL_ROOT / "evaluation/results.json").read_text())
    old = {(row["match"], row["condition"]): row for row in reference}
    comparisons = []
    for row in rows:
        previous = old[(row["match"], row["condition"])]
        comparisons.append(dict(match=row["match"], condition=row["condition"],
                                spell_delta_vs_uniform=row["candidate"]["spellF1"] - previous["candidate"]["spellF1"],
                                macro_delta_vs_uniform=row["candidate"]["macroF1"] - previous["candidate"]["macroF1"]))
    gate = json.loads((ROOT / "evaluation/gate.json").read_text())
    coverage = {}
    for path in sorted((ROOT / "evaluation").glob("J*.json")):
        fold = json.loads(path.read_text())
        counts = {provider: sum(sum(item["sampled_windows"].values()) for item in fold["training_coverage"].values()
                                if item["provider"] == provider) for provider in ("idsse", "pff")}
        require(sum(counts.values()) == 160000, "Sample count differs from 20k by batch8")
        coverage[path.stem] = dict(sampled_windows=counts, pff_fraction=counts["pff"] / 160000)
    summary = dict(descriptive_only_vs_uniform=comparisons, coverage=coverage,
                   quality_eligible=gate["quality_eligible"],
                   promotion_reference="retained_gap_augmented_50_50_blend_penalty16",
                   consecutive_data_expansion_failures=0 if gate["quality_eligible"] else 3,
                   data_expansion_track_stopped=not gate["quality_eligible"],
                   automatic_ratio_search=False, production_changed=False)
    engine.write_json(ROOT / "comparison.json", summary)
    if not gate["quality_eligible"]:
        print("REJECT: third data-expansion failure; track stops. No automatic ratio or budget retry.", flush=True)
    else:
        print("Development gate passed provisionally; production and release status unchanged.", flush=True)
    with Path("ball.md").open("a") as journal:
        journal.write("\nBalanced-provider TCN fixed trial complete. " + json.dumps(summary) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check", action="store_true")
    actions.add_argument("--run", action="store_true")
    actions.add_argument("--fit-final", action="store_true")
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
        if args.run:
            engine.evaluate(cases, signature, locked)
            verified_gate(members, signature)
            supplement()
        else:
            require(verified_gate(members, signature),
                    "Final fit requires a complete passing development gate; rejected trials stop")
            engine.fit_final(cases, signature)
            # This remains a separately reviewed research artifact, never auto-exported.
            print("Final model saved. No production switch or target export.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        engine.write_json(ROOT / "last-failure.json", dict(error_type=type(error).__name__,
                                                         message=str(error), production_changed=False))
        with Path("ball.md").open("a") as journal:
            journal.write("\nBalanced-provider TCN stopped; preserve last-failure.json and review before retry.\n")
        raise
