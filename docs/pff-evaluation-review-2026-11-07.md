# Independent PFF evaluation-design review — November 7, 2026

Scope: AGENTS.md, project memories, committed split, source configuration/features/decoder and prior aggregate reports. No competition assets, public-label rows, sealed matches, private predictions or new performance experiments were accessed. This is a design review, not evidence that PFF will improve the model. I own only this document; no production code or commits changed.

## Decision

Proceed to the two authorized evaluations only after all-64 admission contracts pass or a fixed, non-performance failure policy is recorded. Keep nine-core unaugmented CatBoost and penalty16 unchanged. Freeze remains November13. Confidence is high in this no-leak design; confidence in actual provider transfer is currently low because it has not been measured.

## A. Train-more comparison: exact paired design

For each of the original five IDSSE development matches j:

- Parent fit: the other four IDSSE development matches.
- Expanded fit: those SAME four IDSSE matches plus admitted matches from the locked PFF48 additional-training group. Never include j or PFF16 transfer-holdout matches in either training/calibration path.
- Training is clean/unaugmented: every-fifth-frame sampling after excluding unknown labels, same nine columns, seed20261106, CPUthread1,300iterations,depth6,rate.05,l2=3, no early stopping, calibration, weights or new preprocessing. Do not cap/rebalance PFF after seeing results. Increased source rows and provider dominance are consequences of the authorized one data-volume change; report actual sampled rows and wall time.
- Evaluate BOTH fits on identical clean j and the identical existing fixed target-like corrupted j features/masks. Prefer fresh one-thread parents or explicitly verify cached-parent predictive equality. Distinct cache keys must include training IDs, split hash, features, parameters and corruption fingerprint.

Gate is per match, not pooled frames: let S be official spellF1 and F be macroF1. Paired spell delta is mean(clean S delta, corrupted S delta); paired macro delta is analogous. Require median paired spell delta>0, at least3/5 positive paired spell deltas, median paired macro delta>=-.01, AND median corrupted S delta>=+.01; tests pass and clean deterministic reproduction before use. Report all ten cells, all five deltas, failures, missing-ball quality and variability. A positive overall mean or one large match gain does not substitute for the gate. This gate is an engineering rule, not a statistical-significance guarantee.

A rejection leaves original model untouched. No more-data weighting, provider-specific thresholds or feature changes may be folded into a rescue attempt without a separate authorized protocol.

## B. Cross-provider risk: do not select versions from it

- IDSSE→PFF: train on all original five IDSSE development matches, evaluate all admitted matches in the locked PFF16 transfer holdout. The current final model can be reused only with verified identical config/training provenance and one-thread inference.
- Reverse: train on admitted PFF48 ONLY, evaluate the original five IDSSE development matches. Do not include any IDSSE samples in that fit. This is the requested reverse transfer measurement, not another promotion gate.
- Never include either sealed IDSSE match. Preserve PFF48/16 membership even if admission fails; report missing/failed matches and reasons rather than replacing difficult matches.
- Fix all adapter choices, class mappings, feature definitions, execution seeds, corruption seeds and decoder choices BEFORE reading transfer scores. No fitting temperature/class balance/thresholds, choosing a variant, or choosing a cleanup rule by PFF16 performance. Transfer is descriptive risk measurement even when surprising.

Report each match clean and corrupted, provider-specific equal-match means/medians/ranges/SD and source label/observation coverage. A pooled frame-weighted number would overrepresent longer or less-excluded matches. Do not pool two providers into one quality claim; their supervision conventions may differ. With16 PFF matches and5 historically reused IDSSE matches, report the population difference; do not call reverse results independent confirmation of prior IDSSE development results.

## Critical inference-block caveat

Existing scripts use blocks_valid(y, half_blocks) to reset decoding at true-label X gaps. That is annotation-informed segmentation, whereas production target inference uses only supplied half blocks. It can affect continuity and spell boundaries. This is a methodological caveat, not proof a promotion decision was wrong.

For A, preserve the legacy parent's segmentation on both sides for a controlled one-change comparison and explicitly disclose it. For the new transfer-risk protocol, preregister observation/metadata-only inference blocks (prefer half boundaries only), then let the unchanged scorer mask X labels. Do not select decoder reset points from actual H/A/D transitions. If legacy X-reset evaluation is retained for transfer, label it as annotation-supported evaluation and do not claim full production-equivalent inference. Never compare A and B aggregate numbers as though their segmentation protocols/populations were identical without documenting that difference.

## Missing-ball dead/live metric contract

Define E as frames inside included half/time blocks with known ground truth y∈{H,A,D}. Define M0 from the adapter's clean ball XY visibility BEFORE synthetic corruption, and M1 from visibility AFTER corruption, recomputing masks/gap age from raw masked positions. Frame denominators must use unique resampled25Hz frames, never expanded duplicate native records.

For each match/condition report:

1. |E|, excluded-X frames, known-label time coverage and H/A/D support.
2. Natural missing subset E∩M0, additional newly missing subset E∩M1∩not M0, and all currently missing subset E∩M1. PFF clean already has natural missingness; do not call clean “fully observed.” Do not impute naturally missing balls to force its total missing rate to equal a target rate.
3. For each nonempty subset, TP_D,FP_D,FN_D,TN_D, then D precision/recall/F1, live recall=TN_D/(TN_D+FP_D), binary macroF1 and predicted-D fraction=(TP_D+FP_D)/N. Here D is positive, live is H/A collapsed. Include class support; when no live or no dead support exists, mark the affected metric undefined with the denominator, not a convenient zero or silently dropped class.
4. Explicitly show missingness fractions over E for each condition and the fixed seeds/hash of each raw-position mask. Existing IDSSE evaluation masks/seeds remain unchanged. New PFF masks require a preregistered deterministic ID/seed rule; do not choose seeds by resulting scores.

The prior development failure is near-constant D during missing-ball frames. D recall alone can look perfect while live recall is almost zero. The proposed table tests whether naturally missing PFF examples improve that behavior without hiding class-support changes. It cannot by itself isolate the causal source between emissions, decoder and label convention.

## Admission and interpretation risks, ranked

**High confidence / high impact:** native duplicates and unknown/X exclusions change the evaluation population. Publish per-field duplicate, coordinate-missingness, state/owner-conflict and unique25Hz known-label counts per half before models. Provisional100% delivered-record annotation presence is not an admission statistic. Report censored fragments and short-spell support; excluded intervals can artificially shorten observed spells.

**High confidence / high impact:** PFF48 vastly outnumbers four IDSSE training matches. Class/source mixture and naturally missing broadcast tracking may drive any gain or regression. Treat that as part of the one data-source change; do not infer that label count alone caused the outcome or silently rebalance to fix it.

**High confidence / medium impact:** nine-column output must retain the same order, units,25Hz speed/gap semantics and half resets. Normalize each source using its own metric pitch; verify player-team slot membership and classes_ probability reordering. No provider ID feature or target-label-derived mapping.

**Unresolved / potentially high impact:** PFF and IDSSE possession continuation through loose balls/flight and interruptions may differ. Even valid schema and passing tests establish an executable contract, not cross-provider possession truth. Poor transfer should trigger a documented bug/convention investigation, not tuning to its labels.

**Persistent limitation:** the original five matches were reused historically. Nested previous searches and a new source do not erase this. PFF16 risk measurements and later sealed evaluation improve evidence only if they remain outside selection/tuning decisions.

## Highest-value next slice

Before any fit, publish one admission matrix for all64 matches: source records→unique native keys→duplicate observations→coordinate/missingness disagreements→state/team conflicts→half/time checks→unique25Hz frames→known/unknown labels, with natural missing-ball × H/A/D support. Keep rows private, aggregates/hashes committed. Then preregister A/B exact training populations, mask seeds, inference-block policy and gate; execute once, report failures without replacement or retrospective threshold changes.

Sources: experiments/pff-intake/split.json; src/possession/config.py/core.py/decode.py; scripts/run_core.py/review_frozen.py; docs/review-data-analyst-2026-11-07.md; project memories. No newly measured performance is asserted here.
