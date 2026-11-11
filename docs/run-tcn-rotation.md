# Evaluate the two-view TCN ensemble

This averages predictions from the retained gap-trained TCN on the original input and the same game rotated180degrees. Both views preserve team labels. No new model training, CatBoost blend or architecture change. It must beat the current .5977clean/.4631corrupted candidate under the full existing gate.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_rotation.py --run
```

One command runs the required small contracts, verifies original parent predictions, then scores five fullmatches clean/corrupted with reload/batch repeatability. Existingweights and frozeninputs are reused. Expected to take minutes rather than hours; newruntime andpeakRAM are unmeasured. CPUone thread, no customRAMcap. Do not start the old rejectedframe-set or deferredslotdiagnostic alongside it.

No tests, imports, compilation, inference or scoring were executed by the assistant. Source review is not runtimeverification. Keep partialfailure evidence and send anyerror; do notdelete outputs to force a rerun.

Outputs experiments/tcn-rotation-2026-11-11/report.md, results.json, gate.json anddeterminism.json; privateCSVs data/tcn-rotation/. Failure keeps the current standaloneTCN. A pass is provisional until serving/releasequalification; targetaccuracy remainsunknown. Send “done” for the audit.
