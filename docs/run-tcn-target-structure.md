# Compare actual input structure with the external training data

The winning TCN is sensitive to severe synthetic slot churn. The next qualification describes how the supplied match's tracking behaves, using geometry only. It does not run a model, read labels or change the model.

After this new protocol/source/input registration is committed, run:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/audit_tcn_target_structure.py --run
```

It first runs six supplied synthetic checks, then processes the target and the same five external matches one at a time. It reports movement within slots versus nearest same-team positions, the velocity-clipping proxy, visibility/runs, team coverage and close-position pairs. Distances use each match's recorded pitch dimensions. No identities are inferred or repaired. No tests, imports, compilation, data aggregation or model execution have been run by the assistant.

Runtime and peakRAM are unmeasured. There is no training or model inference. The original target loader allocates about225MB for raw tracking; distance aggregation uses256-frame chunks, while external geometry uses read-only memory maps. Keep the original assets in place and avoid concurrent dataset operations.

Outputs are private:

- data/competition/tcn-target-structure/report.md
- data/competition/tcn-target-structure/summaries.json
- data/competition/tcn-target-structure/provenance.json

Return completion for review. Keep partial/failure evidence; do not rerun unchanged blocked checks or overwrite results. These are descriptive proxies, not an identity-switch rate, target-accuracy measurement or promotion threshold. Final fitting/export remains behind review; sealed evaluation remains at the Nov16 freeze.
