# Independent hybrid assessment

Reviewed November 14, 2026 using source, saved aggregate JSON and stdlib arithmetic. No project import, numerical model execution, test, array/checkpoint loading, target row access or new experiment was performed.

## Decision and hypothesis

Recommend one bounded frozen-local-TCN plus coarse temporal residual-refiner trial before replacing the spatial encoder with a GNN. The hypothesis is that surrounding player-motion context can recover possessions the local model loses during missing-ball bursts while the full-rate local path preserves short transitions. The outcome is official per-match clean/target-like corrupted spellF1 against selected Trial B, under the existing positive-median gate. Any gain, cost and runtime remain unmeasured.

A GNN may supply useful pairwise geometry. The measured evidence currently gives stronger support to temporal robustness. A spatial GNN alone leaves the current temporal receptive field unchanged. Combining new graph reasoning and longer context in one initial trial would make the mechanism of any improvement ambiguous. The failed within-team attention trial does not test all cross-team/ball graph relationships, but it is relevant contrary evidence against assuming a relational replacement will win.

## Denominator audit

The diagnostic's headline exclusive category count of 535 is priority-dependent. For actual exposure rates, group all ground-truth spells by the full missing burst intersecting each spell. At IoU 0.5, Trial B on the corrupted cases gives the following aggregate counts.

|Exposure|Ground-truth spells|Missed spells|Miss rate|
|---|---:|---:|---:|
|Fully observed|1,134|540|47.62%|
|Missing burst at most 2s|28|2|7.14%|
|Missing burst over 2s through 10s|218|115|52.75%|
|Missing burst over 10s|910|621|68.24%|

The very small short-gap stratum has a different duration composition and cannot establish that short gaps help. Long-gap miss rates exceed fully observed rates in all five matches. The comparison also persists within the diagnostic's three coarse duration groups.

|GT spell duration|Fully observed misses / spells|Over-10s-gap misses / spells|
|---|---:|---:|
|At most 2s|328 / 453 (72.41%)|222 / 226 (98.23%)|
|Over 2s through 10s|203 / 561 (36.19%)|336 / 455 (73.85%)|
|Over 10s|9 / 120 (7.50%)|63 / 229 (27.51%)|

Source is experiments/tcn-diagnostic-2026-11-13/evaluation/results.json, Trial B, targetlike, bins/per_iou/0.5. Existing paired evidence also loses 359 clean matches after corruption, of which 289 intersect bursts over ten seconds. This supports a descriptive robustness concern. It does not establish how many possessions a refiner can recover, nor demonstrate temporal context is the sole cause. The corruption perturbs observations and may affect surrounding spells. Burst exposure is defined by the full intersecting burst, so an exposed spell can still contain observed frames.

There are five repeatedly reused development matches, not thousands of independent experiments. Spell-level or frame-level confidence intervals would understate match clustering and selection optimism. Report per-match changes, their spread and all five official IoU thresholds. Avoid significance language or forecasts of 0.8 from these counts.

## Contrary evidence and design requirements

The November 11 13-second dense-context trial failed its registered blend comparison. Its changed depth/capacity, 20k training and previous parent differ from the proposed frozen residual stage. This failure reduces confidence in a generic "more context wins" argument. The current recommendation has moderate confidence as the next uncertainty-reducing experiment and low confidence in a positive quality result.

The refiner should preserve informative player context. Using only three probabilities plus nine core features risks reducing it to smoothing because most ball-distance features are masked during gaps. Consider frozen pre-temporal pooled features as inputs alongside probabilities, with the exact interface locked in the protocol. Separate initialization seeds have unaligned latent channels. Never average their hidden representations. Either concatenate them in a fixed order or pair one refiner with each corresponding frozen member and average only the resulting probabilities. No graph encoder or extra spatial features belong in this same intervention.

Training features must use the outer fold's parent checkpoint, which excludes the held-out match. The parent was fitted on the other four matches, so its predictions on those four are in-sample. This is a stacking training/serving mismatch, not held-out label leakage. It can make the refiner learn corrections for a cleaner parent than it sees at test time. Generating nested cross-fitted parent predictions would reduce that risk but requires extra parent fits and changes the agreed budget. The bounded first trial can disclose the mismatch, keep all outer-held-out predictions honest, and reject the candidate if the promotion gate fails. It must not present the design as fully cross-fitted stacking.

Keep the five outer folds, both initialization seeds, 40k staged updates, original sampler/loss semantics and exact repeats. Twenty refiner fits (5 folds × 2 seeds × 2 exact repeats) are the maximum comparison work if that paired-member design is selected. Cache only fold-safe frozen features needed for those fits. Preregister whether temporal sampling is fixed to real-half coordinates, the 25Hz↔5Hz pooling/interpolation grid, receptive field, edge replication, unknown-label treatment and complete-spell auxiliary loss semantics. Never cross halves or unknown-label regions in supervised loss. Offline bidirectional context is available, but must be consistent between fitting, chunked inference and release.

Treat the refiner as one extra learned stage. It adds compute over the frozen parent. Compare its completed official scores with the unchanged archived parent and describe the additional compute openly. Zero correction initialization must reproduce parent probabilities before training. No gain should be attributed uniquely to context rather than extra capacity without a separate matched-context control, which would be outside this one-candidate scope.

CPU feasibility is plausible for a small convolutional refiner without new dependencies, because parent backpropagation is absent. Actual parent feature extraction, wall time, peak memory and artifact footprint still need the user-run preflight. Prepared arrays must be streamed or mapped, with the 2GiB artifact ceiling and 12GiB free-space floor retained. No runtime guarantee follows from parameter count. Require exact repeated fits, reload probabilities and decoded CSV bytes. Preserve original folds, stopped tracks, target/public-label restrictions and sealed exclusions. Any new trial must finish before the November 16 freeze to qualify.

## Interpretation after execution

Promotion requires the unchanged existing gate. Long-gap recall, short-spell recall, boundary shifts, dead/live errors and missed/spurious spells explain the result. They do not replace that gate. A passing development result remains provisional until the planned independent sealed evaluation. Failure closes this fixed candidate without automatic dilation, scale, graph or coefficient variants.
