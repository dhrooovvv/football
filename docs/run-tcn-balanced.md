# Run the fixed provider-balanced TCN trial

The failed expansion sampled about93%PFF. This trial assigns equal probability to IDSSE and PFF, then samples valid windows uniformly within that provider. Everything else remains fixed. It trains from scratch and compares against the previous **best eligible candidate**, not merely the failed expansion. No ratio search, fine-tuning from the leaky final53 checkpoint, target prediction or production switch.

First run the small checks. These are supplied for you; the assistant has **not executed** them.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_balanced.py --check
```

If the checks pass, run the full five-match comparison:

```sh
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_balanced.py --run
```

This checks the existing prepared files and runs five held-out folds, with two identical20k-update fits per fold and clean/corrupted evaluation. Approximately **1.5–2hours** is a planning estimate from the last run's101minutes for fold stages; actual time may differ. No dataset reconstruction is needed. CPU one thread preserves the approved comparisons and determinism; no custom RAM cap. Large arrays remain memory-mapped. Do not run the old expansion command simultaneously. Progress is saved every1000updates; same-command resumption is supported after reviewing errors. Preserve files on failure.

Results:

- `experiments/tcn-balanced-2026-11-11/evaluation/report.md`: per-match clean/corrupted metrics and full unchanged gate.
- `experiments/tcn-balanced-2026-11-11/comparison.json`: actual provider counts and descriptive deltas versus failed expansion.
- `experiments/tcn-balanced-2026-11-11/checks.txt`: supplied checks' results.
- `models/tcn-balanced/evaluation/`: private fold checkpoints.

A third data-expansion failure stops that track. Improving on the failed expansion is insufficient: the candidate must beat the retained gap-trained blend under the original gate, including median corrupted spellF1 gain>=+.01.

Stop after --run and ask for result review. Do not run final fitting just because training finished. If the complete gate passes and we review the evidence, a separately invoked command is available:

```sh
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_balanced.py --fit-final
```

That command refuses a rejected/incomplete gate, repeats an all53 fit and produces a research-only variant. It does not export the target, select a checkpoint, touch protected matches or certify release readiness. The earlier neural-export command points to the rejected uniform-expansion model and is not the release command for this trial.

All53eligible input files must remain present. Two sealed IDSSE and16PFF transfer matches remain excluded. Starts are known-label250-frame windows within halves; no evaluation labels enter fitting. Fresh folds never initialize from the final53 checkpoint. New research stops at the beginning ofNovember16.
