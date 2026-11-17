# Diagnose missed possessions without training

Run from the project root:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/diagnose_tcn_possessions.py --run
```

This runs synthetic correctness checks, validates frozen A/B fingerprints, reads archived predictions and reproduces their official metrics, then regenerates only the missing probability evidence from existing out-of-fold checkpoints. It performs **zero fits**. One numerical CPU thread, sequential processing, both seed members loaded; no memory cap and no downloads. There are20 trial/match/condition cells, four model-view inference passes per cell (80 total); inference/scoring duration is not yet measured for this runner. It does not load the final-five models, target match or sealed matches.

Completed trial/match pairs are resumable: use the identical command after interruption. Reports under `experiments/tcn-diagnostic-2026-11-13/evaluation/` contain aggregates only. `report.md` is the compact view, `results.json` has thresholds, gap/duration strata, corruption pairing and the conditional recommendation. If reproduction fails, preserve the error; do not retrain to make it pass. The command does not repair inputs, select a model or start a new experiment.

Research stops at the start of November16 Asia/Kolkata. Storage is bounded jointly with missed-possession trials, final B artifacts and private export to2GiB, with12GiBfreefloor; nothing is deleted automatically. All tests and inference are USER RUN and currently unexecuted. Stop after completion and report done for review.
