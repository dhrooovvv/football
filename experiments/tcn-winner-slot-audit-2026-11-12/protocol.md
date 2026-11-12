# Current winner identity-slot qualification — November 12, 2026

Approved qualification of the audited development winner, not a new quality candidate. All execution belongs to the user. Commit this protocol, sources and inputs.json before running; results are committed separately after review. No new research starts on/after November16. Never access target data/public labels, sealed IDSSE matches or PFF holdouts in this diagnostic. No downloads, training, tuning, automatic repair or promotion. Production remains CatBoost16; target accuracy unknown.

## Fixed winner and evidence

Use the five original development folds J03WMX/J03WN1/J03WOH/J03WOY/J03WPY. For each, load models/tcn-pretrain/evaluation/control/MATCH/first/progress.pt, not the old20k slot audit checkpoints. Verify its byte hash, exact original registration signature, control arm, held-out ID and other-four-only supervised membership, no geometry, completed40000 steps/stage2, two20000 stages, seed20261106, window/view RNG reset policy, original521 motion representation and original class architecture. The unused reconstruction head remains solely for strict checkpoint compatibility; no pretraining/reconstruction influences class inference. Compare loss/sampling/target-count evidence with the saved control fold aggregate. Checkpoints from both repeatfits and their archived hashes remain pinned, but no fit is rerun.

Preserve equal probability averaging over original and180-degree physical pitch rotation, unchanged H/A/D order, zero/one scaler, original half blocks, decoder16 and X outside blocks. Use the same ten cached clean/targetlike inputs and the unchanged scorer. Before interpreting any stress cell for a match/setting, reconstructed winner CSV bytes must equal all three archived control CSVs and archived candidate spellF1/macroF1 within1e-12. Parent reload probabilities must agree exactly in each view; first/reload/batch4 CSV bytes must match. Failure halts the attempt and retains evidence; do not bypass by overwriting.

## Four fixed arms

Preserve the prior November11 slot diagnostic's transform and seeds, now applied to the actual winner:

1. Parent: unchanged inputs.
2. Static: one fixed permutation of each team's complete8-channel player vectors per real half. Ball and core9 untouched. This is the ordering numerical control.
3. Rederived identity: original ordering, recompute player velocity only as clip(12.5*diff(encodedXY),−5,5), zero at half starts and unless adjacent observations are visible. Controls rederivation rounding relative to original normalized-coordinate velocity construction.
4. Dynamic: a separate same-team permutation at every frame, then the identical velocity rule. This deliberately extreme stress preserves each team's per-frame position/visibility multisets, roles, ball vector, core9, labels and existing gap masks. It jointly affects false adjacent-slot velocity and per-object history, rather than isolating those mechanisms.

Static/rederived seed20261111+i; dynamic20261111+100000+i, fixed original match order, same seeds across settings. Transforms run before pitch rotation. No target-calibrated churn rate, guessed identities, extra missingness, duplicate injection or identity repair. Velocities only rederived within real half blocks. Unknown label runs are excluded by the scorer; no label is used by the transforms.

## Outputs and interpretation, fixed before execution

Report40 match/setting/arm cells with official spellF1, macroF1, existing error taxonomy and missing-ball dead/live quality; deltas versus parent AND rederived identity, probability max differences and decoded-frame disagreement counts. Verify both-view reload probabilities and first/reload/batch4 CSV bytes for all40 cells. The ten parent reproductions must pass. Fingerprint all sources and original code registration, input NPZs, checkpoints, aggregate evidence and parent CSVs. Recheck hashes after execution. Keep per-frame outputs private under data/tcn-winner-slot-audit; reports expose external aggregates only.

Static allclose uses atol1e-6/rtol1e-5 and is reported, not used to tune. A failed static numerical control prevents attributing dynamic changes until investigated. Report rederivation effects separately; dynamic-vs-rederived is the relevant additional churn contrast. No numeric quality threshold, selection or improvement claim exists here. Large dynamic changes establish sensitivity to this synthetic stress, not measured target damage. Small changes do not certify target slot continuity, duplicates, coverage or target accuracy. Require human/control review before release; no automatic representation change or track reopening. Qualification commands do not alter the best development model or production config.

This protocol and all supplied synthetic checks are prepared by source inspection only. No assistant tests/imports/compile/inference/scoring/training have run. User command runs existing54 contracts plus5 inherited transform checks and4 winner metadata checks; these correctness checks do not prove competition quality. No sealed evaluation is included. Nov16 once-only frozen evaluation remains a separate authorized step.
