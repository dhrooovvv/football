# Run the gap-trained TCN without CatBoost

This uses the five existing short-context gap-trained checkpoints. No retraining. It compares standalone TCN against the retained 50/50 blend on the same five full development matches, clean and corrupted. The long-context model is excluded.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_standalone.py --run
```

The command checks committed fingerprints, runs the existing small correctness tests, reconstructs the parent predictions, then evaluates standalone predictions and reload/batch repeatability. No tests or inference were run by the assistant. Source inspection is not runtime validation.

There are ten match/condition cases, with three inference passes each for repeatability. Training is skipped, so this should be considerably shorter than the prior training jobs; no reliable measured duration exists for this runner. CPU one thread, no custom RAM cap. Keep the computer awake and powered. Do not launch other experiments concurrently.

Read experiments/tcn-standalone-2026-11-11/report.md and gate.json when complete. A passing result must satisfy the full existing gate including median corrupted spellF1 gain of +0.01. It does not automatically replace production. A failure keeps the retained blend. Do not delete partial/failed outputs to force a rerun; send the error for review.

The existing small contract suite includes synthetic training checks. No real-match model is retrained. Independent static review found no blocking issue; runtime has not been verified.
