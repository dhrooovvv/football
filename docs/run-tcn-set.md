# Train the identity-robust TCN

This is the approved model experiment. It embeds each frame's player positions as team sets, then models the sequence of those summaries. It removes dependence on per-slot velocities and player histories. The temporal TCN,20,000updatebudget,gaps,folds and penalty16 stay fixed. Compare against current standalone gapTCN (.5977clean/.4631corrupted), with the full existing promotion gate.

Run this single command; required tests are included before training:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_set.py --run
```

On Mac, to prevent idle sleep during your run:

```sh
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_set.py --run
```

Use either command once, not both. The standalone slot diagnostic is not a prerequisite. No tests, imports, compilation or model execution have been performed by the assistant.

This trains five held-out folds, with two identical20kfits per fold for repeatability. Each fit sees the otherfourIDSSEmatches. Expected planning time **about1–2hours**, based on earlier shortTCNfits; actual runtime for this new code is unmeasured and could be longer. CPU one thread, no customRAMcap. Existing memory-mapped inputs are reused; no dataset download/preparation or PFFmatches. Keep the Mac powered and avoid concurrent model jobs.

Checkpoints every1000updates preserve optimizer and all RNGstates. If interrupted, preserve the folder and failure record for review; identical-source/same-config resumption is supported by the code but not yet runtime-verified. Never change settings or delete evidence to bypass an error.

Read experiments/tcn-set-2026-11-11/evaluation/report.md and gate.json when complete. It reports per-match clean/corrupted spellF1/macroF1, error categories and missing-ball quality. The run ends after comparison; it cannot replace production or generate a targetsubmission. Send “done” for an independent result audit. Keep the candidate only if the complete gate passes; otherwise keep the existing standalone TCN.
