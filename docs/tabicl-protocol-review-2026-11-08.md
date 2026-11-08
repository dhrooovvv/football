# TabICLv2 protocol review — November 8, 2026

Scope: independent static review of `experiments/tabicl-2026-11-08/protocol.md` at initial protocol commit `b0b2e70`, frozen training/inference source, and installed TabICL 2.2.0 source. No model execution, private target inspection, sealed access or outcome inspection. This report does not certify code not yet written.

## Decision

The hypothesis is useful and falsifiable: a fixed pretrained tabular predictor, alone or in an equal-probability blend, improves the unchanged development spell metric enough to pass the existing practical gate. Resource admission before scoring is appropriate. Generic benchmark results and successful synthetic probes cannot establish possession quality.

**One clarification is required before actual-context admission or scoring:** the parent uses every fifth frame starting at zero per match, then removes X labels (`scripts/run_core.py`, `scripts/predict_core.py`). The initial protocol's “full other-four-match known-label context” would instead give TabICL approximately five times as many labelled rows. Amend and commit the protocol to use exactly the parent's stride-five context indices and no further subsampling. This is preservation of parent sampling, not a context-size search. If all frames are deliberately retained instead, disclose a changed sampling budget and do not describe the experiment as the otherwise-identical model replacement requested by the user.

## Locks before inference

- Record the public checkpoint revision/hash and environment; disable network downloads during subsequent probes after obtaining that checkpoint. Public model download is distinct from hosted inference.
- Explicitly fix CPU, random_state 20261106, n_jobs 1, Torch intra/inter-op threads 1, AMP/FA3 off, BLAS/OpenMP thread limits, offload/cache settings and query chunk size. Existing automatic memory/offload choices should not silently define a different candidate on each run. The protocol allows fixed defaults recorded before inference, so recording these choices before execution is not tuning.
- TabICL `classes_` is supplied by LabelEncoder and will normally be A,D,H for these labels. Reorder probabilities to H,A,D before the fixed decoder and blend. Reject missing/extra classes or nonfinite outputs; normalize float64 rows consistently before decoding.
- Installed preprocessing fits its numerical encoder, unique-feature filter, normalizers and outlier transforms on training context, then transforms query features. Keep that separation; never fit on the heldout match or use heldout labels to pick/reset context, chunks or decoding intervals.
- Require both independent fit/predict equality and saved/reloaded candidate equality before promotion. A 64-query probe does not demonstrate full-match runtime; the scored supplement must lock query batching and a full-workload cap before scores are calculated. Runtime failure is feasibility rejection, not a negative spellF1 result.

## Selection and interpretation

The sequential gate is defensible if fixed before outcomes: B versus frozen CatBoost; C versus B only if B passes, otherwise versus frozen CatBoost. Report both arms against original CatBoost as well. Do not promote a failed B merely because its blend passes. An equal blend is an experiment, not an assumption that two models improve quality. No weight search, class rebalance, temperature rescue or context reduction after failure.

The five development matches have been reused across prior decisions. Passing the majority/median/+0.01 gate is practical selection evidence, not an unbiased estimate of future-match improvement or a statistical significance claim. Frames and spells within a match are dependent; avoid frame-level confidence intervals masquerading as independent sample precision. Report the five paired effects and heterogeneous clean/corrupted outcomes directly. Preserve the sealed boundary for the preregistered freeze evaluation; do not use transfer scores to choose versions.

The replacement tests a model package including synthetic pretraining and its fixed preprocessing, not a causal effect of transformer architecture alone. New pretraining compute is not equal to the CatBoost budget; the protocol appropriately discloses additional bounded inference compute. Existing nine features lose player-configuration information during ball gaps, so a probability-model upgrade may improve calibration or class decisions without solving the dominant missing-ball information deficit.

Recommendation: commit the sampling clarification and effective inference configuration, then execute only Stage A. Continue to separately preregistered scored comparison only if resource and determinism admission pass. Preserve production and do not infer target accuracy from either outcome. Confidence is high in the identified sampling and class-order risks, moderate in feasibility until measured, and currently absent for any metric improvement.

## Implementation follow-up, before scored evaluation

Reviewed protocol clarification `2309457` and admission runner `62967b4` without executing it or reading probe outcomes. Parent sampling is now correctly matched: stride five followed by X removal per other training match. The runner selects only the first heldout development match's query features, maps model classes explicitly to H/A/D, pins the public checkpoint revision, disables auto-download in workers, fixes CPU precision/thread settings and applies a monitored wall/RSS cap. Installed TabICL loading uses `weights_only=True`. No quality scorer or target/sealed loader is invoked.

**Numerical adapter correction needed:** TabICL emits float32 probabilities (`_batch_forward` returns `out.float().cpu().numpy()`, and NumPy softmax preserves that dtype). The runner's default `np.allclose` row-sum test is looser than `decode`'s float64 absolute 1e-8 row-sum contract. Valid float32 probabilities can therefore fail the decoder admission for representation rounding rather than nondeterminism or resource infeasibility. Convert reordered probabilities to float64 and normalize each row before passing to the unchanged decoder, consistent with prior experiment adapters. Commit and log this implementation correction; it changes no model setting or promotion threshold. Do not describe this predictable numerical adapter failure as evidence against TabICL quality.

The resource watcher samples worker RSS every 0.25 seconds, so report observed peak RSS rather than claiming a kernel-enforced hard memory limit. Its time cap includes the two fits/predictions together as clarified. A 64-query test still does not demonstrate full-match runtime or a clean-environment serving artifact; those remain separate requirements before any promotion.

## Admission outcome review

Reviewed public-safe result artifacts after normalization correction `f5a28f9`: `admission.json`, `1000.json`, `10000.json`, and the preserved initial adapter-failure trace. The actual probe log is empty; there is no completed actual-probe JSON or quality result. No additional execution or asset inspection was performed.

| Probe | Wall seconds | Observed peak RSS bytes | Outcome |
|---|---:|---:|---|
| Synthetic 1,000 context / 64 query | 3.385 | 807,518,208 | Repeated probabilities and CSV bytes equal |
| Synthetic 10,000 context / 64 query | 26.490 | 2,306,818,048 | Repeated probabilities and CSV bytes equal |
| Parent-matched actual four-match context / 64 query | 15.787 | 6,847,381,504 | Monitor terminated worker with SIGTERM, return code -15, after crossing 6 GiB threshold |

The first attempt's failure was exactly the identified float32 row-sum adapter issue, not a quality, resource or nondeterminism finding. It was separately preserved, corrected without changing the model settings or scorer, committed, and the admission sequence restarted. The two completed synthetic cases support same-environment, same-process repeated-fit reproducibility only. Identical synthetic CSV hashes across context sizes are not a quality comparison, nor evidence that the two predictors produce identical probabilities across sizes.

**Stopping is required and appropriate under the preregistered contract.** The actual-context worker exceeded the fixed observed-RSS threshold before completing admission. Classify this as a resource admission failure under the fixed CPU/no-offload configuration. Neither standalone arm B nor blend arm C is admitted for scoring. No spellF1, macroF1, target accuracy, actual-context determinism or clean-environment model reproduction conclusion can be drawn. Do not count this as two measured metric rejections: neither scored arm ran.

Keep CatBoost production unchanged and close this bounded track. Do not silently shrink context, increase memory, switch devices, enable offloading or change blend weights as a rescue. This result does not prove TabICLv2 is inherently unsuitable under every resource policy; it establishes infeasibility within this specific locked policy. Any future alternative resource strategy would be a new explicitly authorized, preregistered experiment and must still respect the freeze and existing data boundaries.
