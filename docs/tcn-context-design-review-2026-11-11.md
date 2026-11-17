# Fixed longer-context TCN design review — November 11, 2026

Scope: independent data-science review of the proposed fixed architecture and archived source/aggregate evidence. Read AGENTS.md, ball.md, research-state.yaml and findings.md, original TCN and gap trainer. No imports, compilation, tests, model inference/training, raw/prepared arrays, restricted assets or target/sealed labels were accessed. Only this review file is edited. The review is not a test pass or a quality result.

## Recommendation and decision

Proceed to preregistration of **one fixed longer-context architecture** on the retained IDSSE-only gap-trained blend parent (.592502 clean/.428386 corrupted mean spellF1). Preserve the original 250-frame anchor distribution and central 200 labelled loss frames. Expand input context around those exact same loss positions, clip only at real half boundaries, and keep unknown contextual labels out of the loss. Do not require 526 consecutive known labels: that would change the sampling population and selectively exclude uncertain/boundary regions in addition to changing context.

Hypothesis: a longer learned temporal field can use earlier/later supported ball/player evidence to improve possession continuity and handovers around missing-ball runs. Outcome and selection are official per-match clean and fixed-corrupted spellF1/macroF1 against the retained parent under the unchanged complete gate. A passing score justifies provisional eligibility for the fixed candidate, pending release qualification. It does not establish that receptive field alone caused the difference, because depth/capacity also change.

Data expansion is stopped after its third failure. This architecture trial must retain original four-IDSSE-per-fold fitting, original five held-out IDSSE matches, gap training views and fixed evaluation masks. No PFF, new datasets, source adaptation or all53 warm-start is part of this intervention. No target-label selection or sealed access.

## Exact design arithmetic

The original shared object convolution is k3,d1, with radius1. Proposed temporal k3 dilations are (1,4,12,36,108), widths33->32 then four32->32 layers, with a32->3k1 output. Their dilation sum is161, so total learned convolutional radius is1+161=162 encoded samples, and the receptive field is325 samples. At25Hz, that is a12.96-second timestamp span, or13.00seconds by sample-duration count, with6.48seconds on either side. Precomputed velocity adds one prior raw-coordinate dependency; gap_age carries longer past missingness as a scalar. Neither qualification should be omitted when describing context.

This dilation schedule has no structural support holes: starting radius1, each next dilation is no larger than2*current_radius+1. The successive radii are2,6,18,54,162, giving potential support at every integer offset in[-162,162]. Input-dependent masks/ReLUs can still suppress particular paths; dense theoretical support is not a claim that the model actually uses every timestamp.

HALO163 is conservative for this radius, including the one-frame velocity qualification. With retained CORE200, input length is200+2*163=526frames (21.04seconds of supplied input). The learned field per output remains325samples, not526. The full crop is longer because200consecutive outputs each need their own halo.

**Parameter correction:** one32->32k3 convolution has32*32*3+32=3,104 parameters including bias. Two additional layers therefore add **6,208**, not12,416. Source arithmetic gives original9,635total and proposed15,843total: object128, firsttemporal3,200, fourhidden12,416, head99. Here12,416 is the total of all four hidden layers, not the increase over the parent. These are static arithmetic counts, not an executed model inventory. User-run source/model contracts should verify them.

## Why this is a reasonable fixed horizon

Existing label-free target diagnostics report a median ball-missing run around10.72seconds. A symmetric radius6.48seconds can potentially reach observed endpoints around the middle of a gap of that length, unlike the current0.32-second encoded radius. This is a mechanistic rationale, not a guarantee: gap placement and actual observations vary; some gaps are longer; a possession change inside an unobserved interval may remain unidentifiable. Choosing a fixed horizon from label-free input structure is distinct from tuning against target labels or public-window scores.

The denser five-layer design is a bounded choice with less depth than an eight-layer powers-of-two stack. It is not established as optimal. Do not run a dilation/width/horizon grid after failure. The result can be negative because additional depth is harder to optimize at the same20kbudget, finer handovers are obscured, or available inputs lack the missing ownership information.

## Sampling and boundary requirements

For a sampled original parent window beginning at s, retain labels and loss positions s+25 through s+224 inclusive. The larger crop begins at s+25-163 and ends before s+25+200+163; clipping/index replication uses the containing true half bounds. The original window must still satisfy the parent's complete-known250-frame requirement, so the original anchor/window RNG draws and central labels can remain exactly matched. Gap-view RNG/seeds and raw masked inputs stay unchanged. Larger-crop context may include frames whose teacher label is X; those labels are never read for loss, padding or inference resets.

Do not clip at possession or known-label-run boundaries: that would expose teacher segmentation in the input construction and prevent learning from neighbouring supported observations. Do not carry context between halves or matches. Parent window sampling records may need their containing half stored explicitly so the new crop never guesses a boundary from a label run.

Whole-half/chunk/batch validation must compare the **same boundary-extension policy**. The current predictor repeats edge frames via clipped indices. A direct model forward on an unpadded half uses internal convolution zero padding and is not an equivalent reference near half edges. A valid reference explicitly adds the same replicated input halo to the half, runs the model, then crops outputs back to real frames. Check interior and edge outputs, short halves, last partial cores and batches1/4. Require agreed exact CSV bytes and reload/repeat evidence; numerical tolerance, if any for an additional diagnostic, must be fixed before execution rather than relaxed after failure.

## Evidence strength, confounds and interpretation

Preserve20kupdates, batch8, central200lossframes/update, original optimizer/clip/seed, clean/gapview mix, input encoding, scaler, fixed CatBoost probabilities, .5/.5blend and decoder16. Total loss-frame exposure remains32million per fit, with overlaps/repeats. Compute is not equal: crops grow250->526 and depth3->5, while the architecture has6,208more parameters. Record actual cost. Do not reuse final53 or another fold's weights. Fresh initialization with the same seed is repeatable, but added layers mean it cannot make the entire parameter initialization identical to the smaller network.

Five reused development matches are the decision units; frames/windows overlap and are not independent observations. The promotion gate is an engineering screen, not a significance test. No confidence interval, power statement or .8/winning-score forecast is justified here. Require per-match results, clean trade-offs, conditional missing-ball quality and the existing error taxonomy. A pooled improvement with most matches losing must fail the existing gate. No diagnostic slice may rescue a failed global gate.

Confidence is high in support/parameter arithmetic and the sampling-confound warning, moderate in this trial's mechanistic relevance, and low in the direction or size of any actual gain. Factors that would weaken the case: no useful observations within6.48seconds of key errors, inconsistent slot identity/velocity, teacher convention errors, capacity-induced overfitting, or optimization failure. Static review cannot establish any of those conditions on private arrays.

Before user execution, lock protocol/source/input hashes, preserve stopped-track history and freeze requirements, provide synthetic tests and exact repeat/resume/reload/batch proofs, and keep production unchanged. A failure closes this fixed context trial; no automatic architecture, budget or decoder rescue. Target accuracy remains unknown.

Sources: archived experiments/tcn-2026-11-10/tcn_candidate.py; experiments/tcn-gap-2026-11-10/gap_training.py and completed reports; docs/tcn-next-change-review-2026-11-10.md; literature/tcn-transfer-context-refresh-2026-11-11.md; project journal and state. No new external source or data retrieval was needed for this design review.
