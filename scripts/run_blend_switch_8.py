"""User-run, locked comparison of two decoder penalties on held-out predictions."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch

from prepare_tcn import IDS, sha
from prepare_tcn_gap import authority
from possession.core import promote
from possession.decode import decode
from possession.inputs import export_labels
from review_frozen import score

sys.path.insert(0, str(Path("experiments/tcn-gap-2026-11-10").resolve()))
from gap_training import TCN, configure, predict

ROOT = Path("experiments/blend-switch-8")


def check_registration():
    authority()
    for name in ("protocol.md", "inputs.json"):
        path = ROOT / name
        if path.read_bytes() != subprocess.check_output(["git", "show", "HEAD:" + str(path)]):
            raise RuntimeError(f"Uncommitted registration change in {path}")
    for path, digest in json.loads((ROOT / "inputs.json").read_text()).items():
        if sha(path) != digest:
            raise RuntimeError(f"Input hash mismatch in {path}")


def main():
    check_registration()
    run_dir = ROOT / "run"
    run_dir.mkdir(exist_ok=False)
    configure()
    for suite in ("tests", "experiments/tcn-2026-11-10/tests", "experiments/tcn-gap-2026-11-10/tests"):
        subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", suite, "-q"], check=True)

    private = Path("data/blend-switch-8")
    private.mkdir(exist_ok=True)
    results = []
    cost = 1 - np.eye(3)
    for match in IDS:
        checkpoint = torch.load(f"models/tcn-gap/{match}.pt", map_location="cpu", weights_only=True)
        model = TCN().eval()
        model.load_state_dict(checkpoint["state"])
        scaler = np.array(checkpoint["mean"]), np.array(checkpoint["scale"])
        for setting in ("clean", "targetlike"):
            key = f"{match}-{setting}"
            with np.load(f"data/tcn-prepared/{key}.npz") as case:
                x, truth, blocks = case["x"], case["y"], case["blocks"].tolist()
            with np.load(f"data/diagnostics-review/{key}-probs.npz") as cache:
                cat = cache["p"]
            def emissions():
                prob = 0.5 * cat + 0.5 * predict(model, x, blocks, scaler)
                return prob / prob.sum(axis=1, keepdims=True)
            prob = emissions()
            parent = decode(prob, 16 * cost, blocks)
            candidate = decode(prob, 8 * cost, blocks)
            for tag, labels in (("parent", parent), ("first", candidate),
                                ("repeat", decode(emissions(), 8 * cost, blocks))):
                export_labels(private / f"{key}-{tag}.csv", labels, len(truth))
            if sha(private / f"{key}-parent.csv") != sha(f"data/tcn-gap/{key}-first.csv"):
                raise RuntimeError("Parent export differs from the registered reference")
            if sha(private / f"{key}-first.csv") != sha(private / f"{key}-repeat.csv"):
                raise RuntimeError("Candidate export is not repeatable")
            results.append(dict(match=match, setting=setting, parent=score(truth, parent, blocks),
                                candidate=score(truth, candidate, blocks)))
        print("Completed", match, flush=True)

    def paired(arm):
        return {m: tuple(np.mean([[r[arm]["spellF1"], r[arm]["macroF1"]]
                                 for r in results if r["match"] == m], axis=0)) for m in IDS}
    primary = {r["match"]: r["candidate"]["spellF1"] - r["parent"]["spellF1"]
               for r in results if r["setting"] == "targetlike"}
    delta = float(np.median(list(primary.values())))
    gate = dict(quality_eligible=bool(promote(paired("parent"), paired("candidate"), True) and delta >= .01),
                primary_median_delta=delta, primary_deltas=primary, production_changed=False)
    (run_dir / "results.json").write_text(json.dumps(results, indent=2))
    (run_dir / "gate.json").write_text(json.dumps(gate, indent=2))
    print(json.dumps(gate, indent=2))
    with Path("ball.md").open("a") as journal:
        journal.write("\nUser-run decoder comparison completed. " + json.dumps(gate) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", required=True)
    parser.parse_args()
    main()
