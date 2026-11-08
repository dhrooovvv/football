# Uncapped CPU admission — November 8, 2026

**Passed.** The M3 Pro with 18 GiB memory completed two full-context predictions, producing exactly equal probabilities and identical CSV bytes. No possession-quality score was calculated.

| Measurement | Result |
|---|---:|
| Labelled training-context rows | 113,507 |
| Held-out query frames per prediction | 64 |
| Independent fits and predictions | 2 |
| Total wall time | 2,495.184 seconds / 41.586 minutes |
| Observed peak process RSS | 9,680,912,384 bytes / 9.016 GiB |
| Minimum sampled system-available memory | 2,940,846,080 bytes / 2.739 GiB |
| Probability equality | Exact |
| CSV byte equality | Exact |

CSV SHA256: `283eba25193476a39c0e5a9a29b81eeb6093c2dfad911d24c0f601fa7eb167a2`.

Protocol `a0f5dd3` was committed before execution after the user explicitly removed the experiment's memory and runtime limits. The model, checkpoint, nine features, seed 20261106 and single-thread CPU settings were unchanged. The context used the parent model's exact stride-five sampling from the four development matches other than J03WMX. Earlier resource-guard failures remain in their original directories.

This establishes completion and repeatability for this 64-query test on the verified Mac. It does not establish full-match runtime, full-match memory requirements, operation without compression or swap, cross-machine reproducibility, higher spellF1, or target accuracy. RSS is a process measurement, not total system memory cost.

No target, public-label, sealed-match or PFF holdout data was used. No hosted inference or system-setting changes occurred. Production remains the nine-feature, unaugmented CatBoost model with penalty 16. Existing production reproduction evidence still applies; no new production reproduction was performed here.

Evidence: `actual.json`, `admission.json`, `weight-source.json`, and the independent static review in `docs/tabicl-uncapped-review-2026-11-08.md`. A read-only CPU stack sample showed active PyTorch attention; that diagnostic remains under ignored `data/`. The pandas 3.1.1 and official-scorer import preflight passed without scoring or dependency changes.

Next: cache-correctness admission under protocol `915d198`. Only if it passes may the fixed two-arm comparison under protocol `9656b93` run. That comparison covers five development matches, clean and corrupted: ten cases. The blend reuses TabICL probabilities. Production can change only after the unchanged promotion gate and all required reproducibility checks pass. The November 13 freeze remains unchanged.
