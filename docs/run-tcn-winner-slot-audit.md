# Check the actual winning TCN's identity-slot sensitivity

The development winner is the staged40k supervised TCN, with rotation averaging and decoder16. This command uses its existing five fold checkpoints; it does not train a model or read competition/sealed matches. Do not run the older audit_tcn_slots.py against the new winner.

After the new registration is committed, run:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/audit_tcn_winner_slots.py --run
```

It first runs the supplied correctness checks and verifies registered sources, inputs and completed40k checkpoint identities. It must reproduce the saved winner's ten CSVs and scores. It then reports unchanged, fixed-order permutation, velocity-rederivation control and per-frame identity-churn stress for every clean/corrupted development match. Each arm keeps both rotation views and checks reload probabilities plus repeat/batch4 CSV bytes.

CPU one thread, no custom RAM cap. No training. Runtime and peak RAM for this complete diagnostic remain unmeasured; it performs240 full-match prediction-view passes plus scoring, so allow more time than the earlier standalone inference. Tests and inference have not been run by the assistant. Do not launch concurrent dataset jobs or delete partial/failure evidence to bypass a mismatch.

Send experiments/tcn-winner-slot-audit-2026-11-12/report.md and decision.json for review after it finishes. results.json contains all40 aggregate cells; controls.json separates ordering and velocity-rounding effects, determinism.json contains40 repeatability records. Private CSVs remain in data/tcn-winner-slot-audit/.

This extreme synthetic stress measures sensitivity, not target accuracy or a promotion score. It cannot improve/promote a model. Static numerical-control failure requires investigation before interpreting dynamic changes; release requires explicit review of the resulting transfer limitation. Production stays unchanged. Sealed evaluation remains at the Nov16 freeze, separately.
