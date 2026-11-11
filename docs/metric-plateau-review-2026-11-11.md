# Why improvement feels stalled, and what another run must justify

November 11, 2026. Saved external reports, journal/state/findings and protocol review only. No tests, model imports, training, inference, scoring, data-array loading or protected assets. This analysis does not register or authorize an experiment; parent owns journal/state changes and any protocol.

## Decision and hypothesis

The decision is whether another training intervention has a sufficiently distinct, testable mechanism to justify its cost before the November16 freeze. The outcome remains official per-match spellF1, primarily target-like corrupted, with the complete existing paired promotion gate. The hypothesis that the current score is an achievable upper bound is **unsupported**. The claim that nothing has improved is also contradicted by the recorded development results.

|Eligible stage|Clean mean spellF1|Target-like corrupted mean spellF1|
|---|---:|---:|
|CatBoost16 reference|.517654|.323476|
|Original unaugmented TCN + CatBoost50/50|.602554|.397037|
|Gap-trained short TCN + CatBoost50/50|.592502|.428386|
|Gap-trained standalone short TCN|.597707|.463139|
|Current retained rotation average|.602155|.477682|

These are a historical progression across interventions, not one isolated causal contrast or independent validation. From CatBoost to the present candidate, the recorded clean mean increased .084501 and target-like mean .154206. Most recent rotation change contributed .004448 clean and .014543 corrupted mean; the registered median corrupted increase was .014850, with three paired wins. The highest historical clean-only mean is .609882 from a different unaugmented standalone TCN; it is not the selected robust candidate. Calling .609882 and .602155 a regression without showing corrupted quality mixes objectives.

## Why several expensive ideas failed

1. **More data changed the domain and effective exposure.** Uniform PFF expansion allocated about93% of windows to PFF under a fixed20k update budget. The balanced trial allocated about50% but still regressed. This rejects those fixed mixtures; it does not isolate whether label conventions, tracking/noise, reduced IDSSE exposure or optimization allocation caused the loss. More frames are not equivalent to more compatible independent match information.
2. **Architecture changes changed several useful properties together.** The frame-set candidate removed stored motion and per-object temporal history while changing capacity/support; all five matches worsened. Longer context also changed depth/capacity and optimization behavior. Neither is a clean demonstration that all invariant models or all long-context models fail. Neither supports an automatic rescue sweep.
3. **The training objective is imperfectly aligned with spells.** A high frame macroF1 can coexist with missed short spells. The earlier standalone parent missed1086 clean and1373 corrupted spells at IoU.5; short recall was142/732 clean and90/732 corrupted. Those are descriptive older-parent diagnostics, not the official averaged-over-IoU score or a causal guarantee that boundary loss fixes the errors.
4. **Missing observations are a real limitation.** Gap age and player movement cannot always distinguish two plausible possession histories during a long hidden-ball interval. More optimization may reduce model error, but cannot guarantee identification when inputs do not contain the distinguishing evidence. No conditional-information bound or annotation-noise study exists here, so no numerical ceiling can be estimated.
5. **Five repeatedly reused matches constrain what the numbers mean.** Leave-one-match-out training folds overlap; frames and windows are correlated. Repeated exact fits measure computational repeatability, not sampling uncertainty. More searches on the same five can produce selection optimism. No independent-binomial sign test or frame-level confidence interval is defensible from these records. Protected matches must retain their frozen role.

The research strategy has generated too many method names relative to isolated, decision-changing evidence. Papers on known-live possession, eventF1, trajectory reconstruction or action segmentation do not supply a comparable full-match H/A/D spellF1 target. Research finds mechanisms and assumptions; it does not convert a reported .9 accuracy in another task into a credible .8 project forecast.

## Training and fine-tuning

We have already trained neural models from scratch. The next question is not whether to train at all; it is which training signal is missing. Fine-tuning means adapting particular pretrained weights to the fold's training matches. It is potentially useful only if the source task, licences, split provenance, input contract and adaptation budget are compatible. No admitted pretrained possession model has yet met all those conditions. The all53 checkpoint cannot initialize development evaluation because it saw all five development labels. Fine-tuning it while omitting one match afterward does not undo leakage.

PFF-only pretraining followed by IDSSE adaptation is a scientifically plausible, distinct schedule, but the prior mixed-provider failures do not establish its benefit. It would require an explicit bounded amendment to the stopped data line, fold-safe provenance and a total-budget control. It is not the lowest-risk additional run before this freeze and should not be quietly bundled with boundary supervision.

## Finite recommendation

**Complete the already registered boundary-objective trial once.** It is worth one run because it changes the supervision mechanism while preserving the successful motion model, data, original initialization, budget, rotation policy and decoder. Its effect direction is uncertain: it may improve transition sensitivity, overfit noisy boundaries or change calibration unfavorably. The training-only head is a limited test of boundary-supervised representations; a failure would not establish that a full boundary decoder cannot help. Its fixed coefficient and target width are hypotheses, not evidence-backed optimums.

**Allow at most one additional quality experiment after that, only if a concrete admission decision supports it and it can finish before November14 qualification.** The practical default is one fixed additional-seed ensemble of the actual retained recipe, with equal probabilities and the same rotation policy. Its expected benefit is variance reduction; bias and missing-information errors may be shared, so a large gain is not a justified expectation. Declare the extra total compute, seed and equal weights prospectively; do not select the best seed or launch a seed sweep. If the boundary result reveals no convincing remaining mechanism, use zero further quality experiments and qualify the winner.

A genuinely different larger-upside route is reliable extra ball/video evidence, but it needs an admitted aligned external evaluation path. Until that exists, a detector applied only to the target is not a valid promotion experiment. A trainable ball-imputation auxiliary objective is another hypothesis, not an observed signal; it requires uncertainty masks and a separately admitted representation change. Neither should become an automatic third fallback before this deadline.

This recommendation is a **maximum of two remaining quality experiments including boundary**, not a promise that two runs find the limit. A reasonable research budget ends because evidence and delivery time are finite, not because an upper bound has been proved. Preserve every existing stopped track and failure. At the freeze, run the already agreed sealed evaluation once, investigate bugs/transfer if weak, and do not tune to it.

The boundary command contains54 correctness tests and ten full training fits (five folds, each repeated identically). That is one quality hypothesis, not54 model searches or ten independent validation datasets. The repeated second fits consume roughly half the training work to verify deterministic training; they are not extra model diversity or metric optimization. Do not silently remove that registered requirement mid-experiment. Future protocols could explicitly separate exploratory screening from final deterministic confirmation, but any such procedure must be declared before results and cannot weaken the final gate.

## Confidence and what could change the decision

High confidence in recorded progression, provider/architecture confounding and lack of a measured ceiling. Moderate confidence that the objective-to-spell mismatch makes the boundary trial worth its bounded cost. Low confidence in the sign or size of any future gain. The interpretation could change if a source audit finds a scoring/alignment bug, if current rotation errors materially differ from the older parent's short-spell pattern, if compatible independently labelled matches become available, or if a licensed external-video path adds reliable observed information. None is established by this review.

Evidence: experiments/tcn-gap-2026-11-10/report.md; experiments/tcn-{standalone,rotation,set,context,balanced}-2026-11-11/result-review.md; experiments/tcn-expanded-2026-11-10/result-review.md; docs/fresh-methods-decision-review-2026-11-11.md; docs/tcn-training-strategy-review-2026-11-11.md; literature/structured-possession-refresh-2026-11-11.md; experiments/tcn-boundary-2026-11-11/protocol.md. Target accuracy remains unknown; production remains CatBoost16 pending neural release qualification.
