# Optional GRU design review — November 8, 2026

Scope: project instructions, current state, committed experiment aggregates and code. No target tracking, public-label rows, sealed matches or PFF holdout observations were read. No experiment, training or scoring was run. This review does not change production or reopen the stopped decoder/settings tracks.

## Decision and hypothesis

The next eligible candidate is one fixed small bidirectional GRU over the existing nine features, blended with the frozen CatBoost probabilities and decoded at penalty16. The hypothesis is that learned temporal context can improve possession-spell continuity beyond the current emissions, particularly under the fixed target-like missingness. The decision is whether this one candidate replaces the current model, not whether sequence models are generally superior.

Keep production unchanged unless the candidate passes BOTH the original paired gate and median corrupted spellF1 gain>=+.01, plus tests and byte-identical inference/regeneration. Those are engineering promotion criteria, not statistical significance or independent generalization guarantees. Historical reuse of the five IDSSE matches remains.

## Preconditions to lock before execution

1. **Fold isolation.** Exclude the outer match from scaler statistics, training-window generation, optimization, calibration and every setting choice. Windows must not cross match, half or unsupported-label boundaries. Unknown labels may filter training losses; they must not define inference windows. No PFF source or holdout is added to this candidate after the rejected expanded-data experiment.
2. **Window population and loss.** Define uniformity precisely: uniform eligible starts across training matches versus uniform matches then starts yield different exposure. Lock the choice. If inference retains200central frames from250inputs with25halos, prefer matching central-only training loss; otherwise disclose the boundary-context mismatch. Handle short valid runs explicitly without introducing a possession-duration minimum.
3. **Long-gap limitation.** The proposed250frame input is10seconds total, while the observed target missing-run median is268frames/10.72seconds and p90~33.8seconds. Independent window hidden states cannot carry evidence beyond that support. Either select one longer fixed context BEFORE performance or preregister that the candidate does not directly test long-gap recovery throughout those gaps. No window search or longer-window rescue after results.
4. **Clean-only missingness shift.** Clean IDSSE training has no missing ball frames in the recorded subsets: ball masks are constant and gap age is zero. Corrupted evaluation therefore exposes feature patterns the GRU never observed during training. Fold-only NaN imputation is necessary but is not missing-data robustness training. Preserve the no-augmentation rule; do not add masking augmentation after a weak result. A failure would concern this clean-trained candidate and budget, not all GRUs.
5. **Fixed budget and blend.** Proposed200optimizer steps, batch8, one layer/hidden16, Adam.001, no scheduler/early stopping and .75CatBoost/.25GRU are one candidate policy. This adds neural computation while keeping the parent CatBoost budget unchanged; do not describe it as equal total compute. Report steps, sampled frames, unique-window coverage where available, runtime and parameter count. The400000full-window frame exposures under the250frame proposal are limited training exposure; underfitting remains a plausible alternative explanation.
6. **Parent consistency.** Use exactly the same frozen CatBoost models/probabilities for parent and blend. Decode both with the same observation/half-defined block policy. Report the parent difference from the historical label-supported reset policy separately rather than attributing that difference to the GRU.

## Implementation and reproducibility contracts

- Fit imputation/scaling from the four training matches only. Lock finite-value statistics, zero-variance handling, clipping and feature order. Do not fit separately on clean and corrupted held-out observations.
- Output class order must be H,A,D in both models. Softmax outputs and blended probabilities should be finite, nonnegative and explicitly normalized in float64 before the decoder's1e-8sum contract. Casting float32probabilities to float64 alone does not correct their row sums.
- Every half/frame must receive exactly one retained-window output with no shifts, duplicate coverage or omissions. Edge padding or variable-length behavior and short halves must be specified and tested. Never carry hidden state across halves or matches.
- Bidirectional future context is permitted for offline inference, but the latency/context should be stated. It is not evidence of online performance.
- CPU, one numerical thread, fixed seeds, fixed versions, no dropout at inference, deterministic kernels where supported. Serialize/reload then reproduce on fixed inputs. Test independent training repeat if required before promotion and require final CSV equality in clean environment.
- Distinguish byte-identical CSV at the FIXED deployment batching policy from exact floating-probability equality across arbitrary batch sizes. CPU kernel arithmetic may depend on batch shapes. If stronger batch invariance is required, specify whether the gate concerns probabilities or decoded CSV. Do not change the deployment batching policy after results.
- Synthetic tests establish isolation, alignment, probability and repeatability contracts only. They do not prove spellF1 quality. A checkpoint hash can differ due serialization metadata even when tensors/predictions match; report what was actually compared.

## Outcome interpretation

Report per match clean/corrupted spellF1 and macroF1, paired and corrupted deltas, short-spell recall and missing-ball confusion/live recall/predictedDshare. The current parent predictsD on approximately99.95–99.99% of missing-ball development frames; Drecall alone would obscure poor live recovery. A submetric gain cannot override the whole-match gate.

A positive result would support this fixed neural blend on these reused development matches. It would not establish target accuracy, causal gap reconstruction, provider-label equivalence or broad superiority. A negative result should retain the simpler parent and be logged once, with no posthoc blend/window/settings search. Stop rules and November13freeze remain unchanged.

## Recommendation and confidence

Proceed with one bounded preregistered candidate after the above ambiguities are resolved. Confidence is high in the isolation/reproducibility requirements, moderate that temporal context is a reasonable remaining hypothesis, and low in any predicted gain. The highest-value evidence is the fixed clean/corrupted paired comparison with honest missing-frame diagnostics; sealed matches must remain closed until the freeze evaluation.

Sources: AGENTS.md; research-state.yaml; src/possession/core.py/config.py/decode.py; experiments/diagnostics-review/input-shift.md; experiments/whole-pitch/parent-results.json; docs/review-data-analyst-2026-11-07.md; experiments/pff-evaluation/report.md. PyTorch runtime/version-specific determinism settings require verification in the implementation environment; this review does not certify them.

## Pre-fit code review follow-up

Reviewed the committed-protocol implementation in experiments/gru-2026-11-08/gru_candidate.py and scripts/run_gru_candidate.py after the parent's clarification. No training, scoring, raw observations or private assets were read during this review.

The main design questions are now locked: valid starts are sampled uniformly; loss uses the same central200positions; the10second support and clean-training missingness shift are disclosed; class order is H,A,D; blended probabilities are normalized in float64; inference blocks use halves only; fixed batch1 is the deployed contract with an additional batch4decoded-CSV check. No new performance result was used to choose these rules.

**No substantive fold leak or sequence alignment bug was found in the reviewed implementation.** The outer match is excluded from scaler/training inputs. The cumulative valid-start sampler handles interval offsets correctly and never samples a window crossing a half or unknown-label run. The retained inference slices cover each half/frame exactly once, with same-half endpoint padding and zero hidden state per window. Serialized scaler values are reloaded with the model, repeated training resets the RNG, and repeated state tensors/losses, reload probabilities and decoded CSV bytes are checked explicitly.

This is a code review, not runtime certification. The independent repeated-fit checks still have to execute on all five actual folds. If a strict batch4CSV gate fails, the preregistered rule is to drop the candidate, not search batching/kernel settings after scores.

One reporting requirement remains: save the new half-block parent metrics versus the historical label-supported parent metrics, as promised in the protocol. That comparison can use the new parent aggregates and existing historical aggregate files after completion; no new model or performance trial is needed. Prior aggregate results report full known-label support for the IDSSE matches, but equality should be shown rather than assumed.

Recommendation: proceed with the single fixed fit/evaluation budget, keep production unchanged until the strengthened gate and actual determinism/reproduction checks pass, and interpret either outcome only as evidence about this bounded candidate.
