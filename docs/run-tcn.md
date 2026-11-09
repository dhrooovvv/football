# User-run trajectory TCN — November10

One registered local scratch model, not a replication of the published TCN. Uses only the five permitted IDSSE development matches. Existing isolated research environment is required; no new dependencies/weights. Runtime and peak memory on full matches are unmeasured. CPU1 is deliberate for reproducibility. Keep original files; do not clear partial outputs to rerun without review.

First, prepare and validate the raw trajectory inputs:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/prepare_tcn.py --prepare
```

Only after it prints `Preparation complete; no fitting`, run:

```sh
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_candidate.py --run
```

Preparation verifies exact original core feature/label/half alignment and exact target-like corruption reconstruction before producing private raw trajectory arrays. Failure means STOP and share the error; do not bypass assertions. No target match observations/public labels or sealed matches are read. The target-like missing mask is the previously frozen mask on the external development data.

Scoring runs five held-out matches clean/corrupted, with two identical200-step fits per fold to verify training determinism, saved-model reload and batch1/batch4CSV-byte equivalence. Single-threadCPU, no offloading or custom memory/time cap, no blend. This workload has not run and has no measured duration. Terminal prints each completed match. If interrupted, retain partial evidence and ask for review.

Results: experiments/tcn-2026-11-10/report.md, results.json, parent.json, gate.json, determinism.json, cost.json and test logs. Arrays/models/CSVs remain ignored under data/ and models/. Gate quality_eligible is provisional; production is NEVER switched automatically. A passing candidate still needs clean-environment/fresh-clone reproduction and official validation before production promotion. Failure closes this fixed trial; no architecture/seed/blend sweep. New research starts stop at beginning ofNovember16localtime, reserving freeze day for sealed evaluation/delivery. This is the new active cutoff, not the historicalNovember13guard in completed runners.

Small checks (already passed during preparation):

```sh
PYTHONPATH=src:scripts data/gru-env/bin/python -m unittest discover -s tests -q
PYTHONPATH=src:scripts data/gru-env/bin/python -m unittest discover -s experiments/tcn-2026-11-10/tests -q
```

Scientific limitations: clean-only training has little missing-ball exposure; short receptive field cannot reconstruct arbitrary long gaps; a fixed200-step budget may underfit richer geometry. These are deliberate declared limitations, not permission to rescue a failed run. Sequence updates and CatBoost trees are not equal compute units; the fixedsequencebudget matches the earlierGRU trial. Actual adapter compatibility, full-fit repeatability, complete-data memory/runtime and predictive benefit remain unverified until user execution.
