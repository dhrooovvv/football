# TCN training-strategy review — November 11, 2026

## Decision

Prepare **one fixed provider-balanced sampling trial from scratch**, then let its unchanged gate decide. Use equal provider probability, uniform eligible window starts within the selected provider, the same 52 training matches per fold, 20,000 updates and all current architecture/augmentation/blend/decoder settings. Do not run a ratio search. Do not add fine-tuning, a larger budget or longer context to this trial.

This is the smallest useful investigation of the latest failure. It is not evidence that 50/50 is optimal or that it will beat the retained candidate. A more IDSSE-heavy ratio may prove better, but choosing it now would be an unsupported design preference, and trying several ratios would consume the reused development evidence.

Analysis scope: read project instructions, journal/state/findings, archived protocols, trainer/adapter source and saved external aggregate reports. No raw/prepared match arrays, target/public labels, sealed inputs, model checkpoint contents, tests, scoring, training or inference were accessed or executed. No code or model was run. This review edits this document only; other agents own implementation and project logging.

## What the failure establishes

The registered expanded blend declined from mean clean/corrupted spellF1 **0.592502/0.428386** to **0.520562/0.376959**. It declined in paired clean/corrupted spellF1 on every development match; median paired change -0.070287, median corrupted change -0.059098, median paired macro change -0.029278. The saved gate rejects it. Recorded contracts and deterministic training/inference checks passed, which supports repeatability rather than quality.

The five folds sampled **92.79–92.91% PFF windows**, leaving approximately 11,400 of 160,000 sampled windows from IDSSE. The prior retained fit sampled all 160,000 windows from its four IDSSE training matches. The expanded fit kept the total update budget fixed. Thus provider observations, provider label conventions and allocation of the finite training budget changed together. This run cannot distinguish negative transfer from reduced IDSSE optimization or other source differences. Dataset count alone is not the operative exposure measure.

The earlier CatBoost expansion also failed, and the descriptive transfer report documents provider risk. Those outcomes strengthen caution about pooling providers, but do not identify the TCN failure mechanism. The PFF transfer cohort remains a risk measurement, not a selection set; no new setting should be picked by its scores.

## Hypothesis, estimand and exact sampling proposal

Hypothesis: reducing PFF's dominance while retaining PFF diversity yields better held-out IDSSE possession spells than the rejected uniform expanded sampler, and may exceed the current best IDSSE-only gap-trained blend. The latter is the actual promotion question.

Let `N_s` denote the number of eligible 250-frame window starts across training matches of provider `s`. Eligible starts are exactly those already permitted by the parent: entirely known training labels and inside one half. For each sampled window:

1. Draw provider `s` with `P(IDSSE)=P(PFF)=0.5`.
2. Draw one integer uniformly from `[0,N_s)` and map it into the existing ordered valid-window records for that provider.
3. Draw the unchanged clean/gap view using its existing independent Bernoulli(0.5) RNG and use the existing raw-gap-derived features.

Thus `P(w)=0.5/N_s` for any eligible start in provider `s`. A match with `N_m` eligible starts receives `0.5*N_m/N_s` probability. **Do not also balance matches**: that would introduce another change. Expected provider counts are 80,000/80,000 per 20,000-update fit with batch eight; actual counts must be recorded. Equal expected provider mass does not require four windows of each provider per minibatch.

Use a separately fixed provider RNG so view allocation is not coupled to source allocation. Lock its seed and checkpoint RNG state before execution. Retain the existing window seed, view seed and deterministic CPU configuration; identical seeds do not imply identical windows when the sampling distribution changes. All original training and evaluation raw-gap seeds remain fixed. Source allocation is the only experimental intervention.

A frozen comparison to the failed expansion can measure recovery under this sampling policy on the same pool. **Promotion must compare to the retained best gap-trained 50/50 TCN/CatBoost blend**, whose clean/corrupted means are 0.592502/0.428386. Beating the weaker expanded model alone is insufficient. The new candidate still receives only about half the IDSSE window exposure of the retained parent; that is an important reason it could fail despite improving on the expansion.

Relative to the retained best, this is a replacement training-distribution policy that includes PFF plus explicit source allocation. Do not describe the gate comparison as a pure causal isolation of balancing: the pure balancing contrast is against the rejected expanded sampler. Both references and their purposes must be named before running.

## Fixed comparison and interpretation

Preserve five held-out IDSSE matches, full clean and fixed target-like corrupted evaluation, 20,000 updates, batch eight, final checkpoint only, all existing input features, normalization, Adam settings, augmentation, frozen CatBoost probabilities, 50/50 blend and penalty16. Preserve two exact fits per fold, exact saved/reloaded probabilities and batch CSV byte checks. Report every match, including regressions. No checkpoint selection, early stopping, class weighting, provider-conditioned output calibration or extra training is included.

Keep the gate unchanged: positive median paired clean/corrupted spellF1 change, at least three positive match changes, median paired macroF1 change at least -0.01, median corrupted spellF1 gain at least +0.01, and passing contracts/repeatability. A gate pass remains provisional until clean-environment/fresh-clone and adapter/release checks pass. No target/public score participates in any decision.

These are five repeatedly reused matches with overlapping training folds. Frame counts are not independent sample sizes; repeated fits measure computational repeatability rather than sampling uncertainty. Do not attach a frame-level confidence interval, treat five signs as an independent binomial trial, or forecast target accuracy from a gate pass. The preserved November16 sealed evaluation supplies the existing independent check after configuration freeze, with low results triggering investigation rather than tuning.

Expected impact direction: plausible recovery versus the PFF-dominated expansion; unknown versus the retained best. Confidence is high in observed regression and exposure imbalance, moderate in the relevance of testing allocation, and low in the direction or magnitude of a held-out gain. A negative result would rule out this fixed mixture/budget, not all mixed-provider learning or TCN capacity.

## Why other paths wait

**PFF pretraining then IDSSE fine-tuning:** a defensible later domain-adaptation hypothesis, but introduces a phase schedule and decisions about optimizer continuation/reset, learning rate and phase budgets. Reusing a 20,000-step expanded checkpoint and adding updates violates an equal-total-budget comparison unless explicitly registered as a budget change. At a fixed total20k budget, a split such as10k PFF/10k IDSSE is possible but unvalidated. It should not be bundled with the sampler trial or presented as a free improvement.

**Critical checkpoint leakage:** the final53-match checkpoint already trained on all five development matches. Fine-tuning it and evaluating on any of those five would contaminate the held-out comparison, even if that match is omitted during fine-tuning. Each expanded52-match fold checkpoint excludes only its own held-out IDSSE match and is eligible only for that same fold; it cannot initialize a different fold. A PFF-only48 pretraining fit would avoid these IDSSE held-out labels, but still needs fixed budgets and source-state provenance. Do not import the final53 checkpoint as an evaluation shortcut.

**IDSSE-only longer context:** a distinct and credible architecture hypothesis. Current learned support is17 encoded frames (~0.68s by sample-duration convention), while existing label-free target gap diagnostics report median10.72s. Gap age summarizes history, so the current model is not wholly devoid of longer-term information. Still, it cannot directly use both endpoints of typical long gaps through the present convolution stack. A fixed context extension is appropriate as a separate later change on the retained or newly promoted parent. Calculate support, halo, loss-frame accounting and half/chunk behavior exactly; enlarging only the input window does not enlarge the learned field. More context can also blur brief possessions and does not guarantee missing-ball recovery.

## Stop rules, execution and release

The previous CatBoost data-expansion failure and current TCN expansion failure remain in history. Under conservative broad data-expansion accounting these are two failures; a failed balanced trial is the third and stops this track. Do not create a new counter merely by renaming a sampler or switching model family. If project owners use narrower track definitions, state that interpretation and the latest explicit authorization as a bounded amendment before execution; never silently erase old failures. The earlier interaction, decoder and model-budget failures must also remain recorded. This review does not authorize a ratio sweep or automatic rescue.

The user's current instruction authorizes improvement preparation and user-run testing. Commit the new protocol and all required source/input hashes before handing over commands. Assistant must not execute even small tests or synthetic fits. New research starts remain blocked from the beginning ofNovember16; reserve time for actual winner release qualification. No automatic production replacement, external submission or publication.

The prepared export workflow currently loads the rejected expanded53 checkpoint. That workflow is not a release proof for the retained earlier gap-trained candidate. Target player-slot continuity remains an unresolved serving contract for neural velocities. Fix the appropriate release registration and verify this property independently of model-score experiments; a higher development metric does not make an invalid adapter acceptable.

Sources: `experiments/tcn-expanded-2026-11-10/{protocol.md,result-review.md,result-audit.json,expanded_training.py,expanded_data.py}`; `experiments/tcn-gap-2026-11-10/{protocol.md,gap_training.py,report.md}`; `experiments/tcn-2026-11-10/tcn_candidate.py`; `experiments/pff-evaluation/report.md`; `docs/proposed-levers-review-2026-11-10.md`; `docs/plan-2026-11-10.md`; journal/state/findings. No new numerical result is claimed.
