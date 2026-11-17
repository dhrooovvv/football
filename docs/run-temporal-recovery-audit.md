# User-run temporal recovery audit

Prepared November15,2026. Diagnostic only: no training, downloads, target labels, sealed matches or candidate promotion. Tests and numerical execution have not been run by the assistant.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/audit_temporal_recovery.py --run
```

This runs ten supplied synthetic contracts, verifies archived repeated-fit evidence, reuses frozen parent caches, regenerates only temporal fold probabilities for ten clean/corrupted cases and requires exact archived CSV/official-score reproduction. It reports whether parent support, temporal confidence or seed agreement separates recovered from introduced spurious spells, per match. It also extracts graph training-loss trends from saved checkpoints; it does not train or run graph inference. One numerical thread, one process. No measured runtime yet: this is inference/scoring plus checkpoint reading, not another40k-update training run.

Outputs are under experiments/temporal-recovery-audit-2026-11-15/evaluation/. Progress is saved after each complete match. Resume with the same command if interrupted after successful checks. A failed/interrupted unit-test log requires review; no automatic deletion. Complete results.json is never overwritten. Return success/error for review. No automatic correction rule is tested: first determine whether the frozen temporal errors are distinguishable. The runner refuses research from November16 onward under the unchanged freeze.

Parent Trial B, production, submission-package CSV and rejected hybrid reviews stay unchanged. A possible correction rule requires its own prospective source/protocol lock before comparison; the agreed promotion gate is unchanged. Graph training loss is not a validation learning curve. Target-match accuracy remains unknown.

November15 fix01: the initial user run failed five numeric-label adapter checks before inference. The adapter is corrected; original checks.txt is retained, and fresh attempts write unique logs bound to the current registration. Rerun the same command; delete no logs. Ten current tests remain unexecuted by the assistant.
