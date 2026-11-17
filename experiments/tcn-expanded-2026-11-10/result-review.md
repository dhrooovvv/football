# Expanded-data TCN result audit — November 11, 2026

Decision: **reject the registered expanded-data blend**. Retain the previous gap-trained 50/50 TCN/CatBoost development candidate. Production remains nine-core CatBoost with penalty 16. This is a review of completed user-run evidence, not a new experiment. No training, inference, synthetic checks or target export was launched by the assistant.

|Arm|Clean spellF1|Corrupted spellF1|Clean macroF1|Corrupted macroF1|
|---|---:|---:|---:|---:|
|Previous eligible blend|0.592502|0.428386|0.919588|0.768685|
|Expanded-data blend|0.520562|0.376959|0.897874|0.733919|
|Expanded standalone TCN (diagnostic)|0.490922|0.371692|0.881966|0.737247|

Full per-match clean/corrupted spellF1 and macroF1: evaluation/report.md and results.json. The candidate loses clean spellF1 on all five matches and corrupted spellF1 on four. Paired clean/corrupted spell change is negative on all five. Independently recomputed median paired spell delta -0.070287, median paired macro delta -0.029278 (below -0.01), median primary corrupted spell delta -0.059098 (required +0.01), and 0/5 paired wins. Saved gate arithmetic agrees within 1e-12.

Confirmed five complete held-out folds, each with exactly the approved other four IDSSE matches plus 48 PFF matches. Aggregate result rows agree with their fold records. Recorded user-run logs show 45 passed contracts (35 production, 4 TCN, 2 gap, 4 expanded), and all ten cases completed repeated-training, reload and batch-CSV checks. These are within-environment proofs recorded by the completed runner, not new tests executed during this audit. All 32 registered code hashes still match.

The final all-53 artifact exists and its SHA256 matches the manifest: `9e0a1e41e5c0994249fa5c833089aa8f3cad5a2139696f32b40e641a196d110d`. Manifest membership equals the registered 53, and records exact repeated fitting and no production promotion. The final training artifact is research-only; it has no independent held-out score of its own. Do not deploy or select it because training completed.

Actual sampling confirms the disclosed provider imbalance: PFF supplied 92.79–92.91% of sampled windows in each development fit. Final fitting sampled 145,908 PFF windows and 14,092 IDSSE windows (91.19% PFF), totaling 160,000 windows. A small fixed update budget over this larger pool and differences between provider observations/labels are plausible explanations for regression; these results do not isolate their causal contributions. More data under this sampler/budget demonstrably failed. They do not establish that every mixed-provider training strategy fails. Source balancing or provider pretraining followed by IDSSE adaptation would be a different experiment requiring a separate protocol and authorization; no automatic rescue is started.

Five recorded fold stages total 6,076.154 seconds (101.27 minutes), including their repeated fits and evaluation. This excludes preparation and final fitting; no complete wall-clock or peak RAM measurement is inferred.

No active expanded/export process was found at audit. No neural-check output directory exists: target export, official validation and clean/fresh-clone neural reproduction have not been performed. The prepared exporter specifically loads this rejected expanded checkpoint, so it must not be treated as a release path for the retained earlier candidate without a separate checkpoint/export registration. Target temporal slot continuity remains unresolved. Target accuracy is unknown. The two sealed IDSSE and sixteen PFF transfer matches were excluded; no protected raw inputs or target labels were accessed by this audit.

Close this fixed expansion trial. Keep the prior candidate, preserve the failed final artifact and logs, and prioritize release qualification of the retained candidate. No model selection on target labels, no new run, no external publication/submission. Machine-readable audit: result-audit.json; input/output fingerprints: result-artifact-hashes.json.
