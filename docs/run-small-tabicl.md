# Run the reduced-context screen on this Mac

This uses the existing local prepared development inputs, frozen CatBoost probabilities, pinned weights and isolated dependencies. A fresh clone alone lacks those assets.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=data/tabicl-deps:src data/gru-env/bin/python scripts/run_tabicl_small.py --protocol experiments/tabicl-small-2026-11-08/protocol.md
```

The command starts the experiment: fixed10,000 training rows,11CPU threads, five full development matches clean/corrupted, standalone TabICL and50/50blend. Evaluation frames are not sampled. No custom memory/time caps. No large model cache files are saved; the in-memory model is released after each fold. Arrays and CSVs remain in ignored data/.

Progress appears in Terminal. Results: experiments/tabicl-small-2026-11-08/report.md, results.json and gate.json. Outcomes append a pointer to ball.md. QUALITY_ELIGIBLE means only provisional numeric gates passed; single-thread verification and production reproduction remain required. Production is never changed.

The15–30minute initial estimate is not yet measured for this configuration. Ctrl+C interrupts. The runner refuses overwriting existing result JSON. A new experiment needs a separate protocol/result directory; do not delete evidence to search samples or seeds. Sealed matches and target labels are not used. Research starts are blocked after November13.
