# Error and training-strategy reassessment

November 11, 2026. Source and saved aggregate results only. No tests, model/data-module imports, compilation, inference, scoring, training, raw arrays or protected assets were read or executed. This report does not register an experiment or reopen a stopped track. Other agents own the statistical and new-literature reviews.

The best retained development candidate remains the original gap-trained motion TCN with equal identity/180-degree probability averaging and decoder16. Its mean spellF1 is 0.602155 clean / 0.477682 target-like corrupted; macroF1 is 0.919370 / 0.838611. These are two different evaluation conditions. The clean score has not steadily increased: the earlier unaugmented TCN's historical clean mean was 0.609882. The retained selection prioritizes robustness and the full match-level gate.

## Current errors, rather than an architecture shopping list

Arithmetic over the ten rows of experiments/tcn-rotation-2026-11-11/results.json gives:

|Saved diagnostic|Clean|Target-like corrupted|
|---|---:|---:|
|Missed spells at IoU0.5|1,119|1,379|
|Spurious spells at IoU0.5|386|616|
|Short spells recalled at IoU0.5|125 / 732 (17.1%)|92 / 732 (12.6%)|
|Dead/live wrong frames|2,362|51,589|
|Late / early boundary counts|474 / 557|421 / 449|

These diagnostics differ from the official mean-over-IoU spellF1. Frames and spells within a match are dependent. Compared with the previous standalone parent (1,086 missed / 497 spurious, short142/732 clean), rotation reduced spurious spells while clean missed spells increased and clean short recall fell. The successful score change therefore did not solve the missing-short-possession problem. It is wrong to describe rotation as a universal improvement in boundaries or recall.

The saved oracle-repair diagnostic averages approximately +0.381 clean / +0.395 corrupted when true team labels repair wrong-team predictions, versus -0.0085 / +0.0996 for the dead/live repair. These are counterfactual label-informed transformations with non-additive effects on spells. They are not achievable gain estimates, independent error contributions or evidence that a deployable model can reach the repaired score. They indicate that a dead/live-only improvement is unlikely to resolve all important failures.

Boundary supervision is a justified remaining hypothesis: frame crossentropy and complete-spell overlap reward different behavior, and current short recall is low. Its training-only shared gradient does not add missing ball observations or directly identify the controlling player. A large improvement cannot be inferred from the error counts or from an action-segmentation paper. The registered boundary trial should answer this one question; it should not trigger a grid of coefficients or boundary widths if rejected.

## What the current system actually learns

Boundary reviewed: external stable-ID positions -> normalized64-object521-column representation with motion and9core features -> independent per-object3-frame convolution -> masked mean for home/away/ball -> short temporal convolutions -> class probabilities -> rotation average -> decoder16 -> CSV. The class network has9,635 parameters and encoded receptive field17frames (about0.68s at25Hz). The ten-second input crop does not give every prediction ten seconds of usable network context.

The source offers rich positions but collapses player embeddings to three group means before the final temporal reasoning. This may discard useful player-ball and opponent relationships; it is a mechanism hypothesis, not a demonstrated capacity lower bound. The failed frame-set redesign removed useful motion/history together with other changes, so its failure does not establish that relational or invariant models cannot help. It also provides no justification for repeating an architecture sweep before the deadline. Relative-XY, longer-context and frame-set failures remain counted; decoder/source-expansion stops remain binding.

There is also a concrete serving mismatch: official challenge documentation permits slots to appear, vanish and swap identities, whereas external per-slot velocities and the pre-pooling temporal convolution use stable PersonId histories. Rotation leaves this unchanged. It may damage target transfer; no target-quality effect has been measured. A higher score on the same stable-ID external matches would not resolve it. The existing deferred slot-stress protocol is a diagnostic, not another promotion candidate or a source of target labels.

## One substantive direction beyond the pending objective

If the boundary trial is completed and one more scientifically justified training comparison fits before November14, the strongest distinct direction to admit for feasibility is **masked-trajectory pretraining on eligible external training geometry, followed by IDSSE possession fine-tuning**. Preserve training/test membership throughout each fold. Use only the48 eligible PFF training matches plus that fold's four IDSSE training matches, never the held-out IDSSE match, sealed matches,16PFF holdouts or target. Labels from incompatible providers need not be mixed into the final possession objective: an observed-position reconstruction task uses its own observation truth, then final H/A/D fine-tuning uses compatible IDSSE labels.

This differs from the failed uniform/50-50 supervised PFF expansion: it separates representation learning from potentially incompatible team/dead label conventions and gives the final possession stage its own allocation of updates. It is not established to work locally. Different coordinate, motion, identity and observation conventions still need an explicit input contract. Estimated masked-ball positions must retain original missingness and never become observed truth. Fine-tuning cannot repair a loss of information or mismatched input semantics by itself.

The parent's literature agent should establish the concrete masked-model source and licensing before an implementation decision. A new method must be compared with a matched-total-compute control; otherwise a gain could be extra optimization rather than pretraining. Predeclare all pretraining/fine-tuning budgets, mask distribution, fold-local normalization, seeds and fixed final checkpoint. Additional compute cannot be called the same parent budget. This is a proposal requiring an explicit bounded protocol amendment, not permission to bypass stopped source/representation tracks or start an overnight run immediately.

With the deadline, it is less ready than the registered boundary trial. Ball imputation/visual recovery offer different information mechanisms but lack established deployment/evaluation prerequisites; fixed seed averaging is easier but mostly reduces variance and is not a credible promise of a large jump. None should be bundled with pretraining or the boundary loss in the same comparison.

## Finite decision budget

Recommend finishing the one registered boundary trial and allowing at most ONE additional distinct comparison before November14 only if its data/provenance, matched-compute control and implementation fit the deadline. If those prerequisites fail, spend the remaining time qualifying the retained winner. Keep the full promotion gate, log regressions and preserve stopped-track history. November14–15 should qualify the final model and November16 freezes it. No further serial model-name experiments should be presented as a likely path to0.8.

We have not measured a ceiling. We also have not measured that more models or more training will cross0.6clean or0.48corrupted. Five repeatedly reused development matches and overlapping folds cannot establish independent generalization. Frozen sealed evaluation supplies an independent check only at its authorized stage; its result must trigger investigation rather than tuning. Target accuracy remains unknown.

Evidence: experiments/tcn-rotation-2026-11-11/{results.json,result-review.md}; experiments/tcn-standalone-2026-11-11/result-review.md; experiments/tcn-set-2026-11-11/result-review.md; experiments/tcn-2026-11-10/tcn_candidate.py; docs/tcn-release-readiness-review-2026-11-11.md; literature/structured-possession-refresh-2026-11-11.md; literature/high-upside-methods-synthesis-2026-11-11.md. This document adds no model-quality measurement beyond saved results and no new runtime validation.
