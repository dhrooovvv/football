# Check whether changing player identities affects the TCN

The official input documentation says tracker slots can change identity. Our TCN learned on stable person slots and uses adjacent-slot motion and short per-slot histories. This diagnostic checks that assumption on the five external development matches, without reading the competition match.

Run:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/audit_tcn_slots.py --run
```

It uses existing checkpoints, with no real-match retraining. It evaluates the unchanged model, a fixed same-team slot permutation, a velocity-rounding control, and changing same-team permutations. The latter deliberately exaggerates identity churn; its score is not a target-performance forecast. All clean/corrupted cases are reported. It checks the saved parent predictions first and records repeatability.

No tests, imports, compilation or model inference have been run by the assistant. New synthetic transform checks and existing small contracts run as part of your command. Source review alone does not establish runtime success.

CPU one thread, no custom RAM cap. Previous standalone inference recorded roughly66seconds of fold stages; this job has extra views/scoring and should be a short diagnostic rather than an hours-long training job, but its runtime and peakRAM remain unmeasured. Keep the Mac powered and avoid concurrent dataset jobs.

Outputs: experiments/tcn-slot-audit-2026-11-11/report.md, results.json, controls.json and determinism.json; private CSVs under data/tcn-slot-audit/. Send the result for review. Do not delete failed/partial evidence or rerun to bypass a mismatch. This diagnostic cannot promote a model. A supported repair requires a new registered training comparison against the standalone leader, using the existing gate.
