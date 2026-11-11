# Run the boundary-supervision experiment

This trains the original successful TCN with one additional training signal: whether possession changes at each frame. It preserves motion features, the existing gap augmentation, two-view rotation averaging and decoder16. It compares against the current winner: **0.6022 clean / 0.4777 target-like corrupted spellF1**.

Run once; the required tests run first, then training and scoring:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_boundary.py --run
```

The command trains five held-out folds with two identical20,000-update fits each to verify repeatability. Each fit sees only the other four IDSSE development matches. One CPU thread; no custom RAM cap. Allow roughly **1.5–2 hours as a planning estimate**, not a measured promise for this runner. No PFF, sealed matches, target labels, downloads or target export. Keep the Mac powered and avoid simultaneous model jobs.

Checkpoints every1000updates retain the optimizer and random states. If interrupted, preserve the evidence and report the error; rerunning unchanged code supports resumption, but the new runner has not been executed by the assistant. Do not alter settings or delete files to bypass errors.

Results appear in experiments/tcn-boundary-2026-11-11/evaluation/report.md and gate.json. Keep the new objective only if the full gate passes, including at least +0.01 median corrupted spellF1 improvement. A development pass does not automatically replace production. Send “done” for a saved-result audit.

All tests, imports, compilation, model inference, training and scoring remain for you to run. The assistant has performed source inspection only. This is one fixed objective trial; failure does not trigger an automatic coefficient or model search.
