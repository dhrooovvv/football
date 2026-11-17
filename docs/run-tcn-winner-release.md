# Run the winning TCN delivery qualification

Prepared November12. Nothing here has been executed by the assistant. Current eligible development spellF1 is **.632871 clean / .497550 target-like corrupted**. Production remains CatBoost16 and target accuracy is unknown.

First run the current-winner slot diagnostic using `docs/run-tcn-winner-slot-audit.md`, then stop and have its results reviewed. Do not chain the training command behind the diagnostic. Static-control failures require investigation; a dynamic-stress score is not a promotion gate. The commands below are for after that review and explicit acknowledgement of the unresolved target-identity risk.

## Final five-match artifact: user runs

Source/protocol/inputs must already be committed. Use the existing pinned environment and run beforeNov16:

```bash
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/fit_tcn_winner.py --run --acknowledge-slot-risk
```

This runs the contracts, then two exact40k fits on the five approved IDSSE development matches. Same winning20k+reset+20k recipe, independent cached gap views, CPU1/interop1, no RAM cap, no PFF/protected/target data and no quality selection. Rough30–60minute estimate for training only; not measured. Checkpoints every1000 updates allow the same command to resume; do not delete earlier evidence. After manifest completion, the command refuses to overwrite it.

Private manifest: `models/tcn-winner-release/manifest.json`. This fit trains on the five development matches and cannot yield an independent development score. A repeated fit tests determinism, not generalisation.

## Private candidate export: user runs separately

After final-fit results are reviewed, choose a new output directory:

```bash
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/export_tcn_winner.py --manifest models/tcn-winner-release/manifest.json --output data/competition/tcn-winner-local --acknowledge-slot-risk
```

The exporter performs equal original/180-degree probability averaging and penalty16, checks unchanged official format validation plus reload/batch4 identical CSV bytes, then writes private candidate CSVs/provenance. It does not read competition labels or score target accuracy. Only aggregate prediction diagnostics and hashes are recorded. No existing production predictions are replaced, and nothing is submitted or pushed.

Then follow `docs/run-tcn-winner-reproduction.md` for a fresh pinned environment and fresh local clone. Frozen-model inference reproduction reuses the exact checkpoint; it is not full training reproduction. Nov16 sealed evaluation and final correctness score remain separate planned steps, not started by these commands.
