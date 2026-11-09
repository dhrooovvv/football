# Improvement evidence review — November 9, 2026

Scope: local aggregate reports, research journal/state and source inspection only. No training, inference, evaluation, private arrays, competition observations, public-label rows or sealed assets were accessed. This document is evidence analysis, not a model protocol or authority to reopen stopped tracks.

## Decision

Keep nine-core unaugmented CatBoost + penalty16 selected. There is no defensible numerical forecast that a new model will raise official spellF1 to .8. The strongest next work is a current-parent, gap-stratified error audit followed, only if warranted and explicitly authorized, by one temporal team-control feature experiment. Do not spend another bounded trial merely scaling TabICL context or sweeping blend weights.

Confidence is high in the rejection of the tested configurations and in the feature information bottleneck described below. Confidence is low in the size of any future gain or in target generalization.

## What the headline score means

The selected .517654 is the equal-match mean clean spellF1 over five IDSSE development matches, evaluated leave-one-match-out. Target-like corrupted mean is .323476. Neither measures the target match or two sealed matches. The official scorer matches H/A possession intervals one-to-one at temporal IoUs .3,.4,.5,.6,.7, then averages F1; D is not a possession spell. Frame accuracy, possession-team accuracy on known-live clips, ball reconstruction accuracy and F1 at a single IoU cannot be treated as this metric.

A .8 target would require a clean absolute gain of .282346, about55% relative to the current score. This arithmetic is a distance to a goal, not an expected effect. On the corrupted task, reaching .8 would require .476524 absolute gain. Published scores cannot determine that feasibility without matched task, input visibility, labels, split and scorer.

The promotion rule is an engineering decision rule, not a significance test: five matches, positive median paired clean/corrupted spell delta, a majority positive, median macro delta at least−.01, plus median corrupted spell gain at least+.01 and correctness/reproducibility checks. Reusing these five matches across many hypotheses creates selection optimism. Frames are temporally dependent; millions of frames do not create millions of independent tests. No new confidence interval or power estimate was computed here.

Source: reference/more-than-a-hack-2027-main/evaluation/possession_metrics.py; experiments/gru-2026-11-08/report.md; research-state.yaml.

## Strongest supported mechanism: lack of control information during gaps

Source inspection of src/possession/core.py and features.py shows the nine columns contain nearest H/A distances, their margin, instantaneous consecutive-observation ball speed, edge distance, three observation indicators and elapsed missing-ball time. When ball XY is missing, distances, margin, speed and edge are unavailable; home/away distance-observed masks also become zero. Thus many missing frames differ principally in gap age. Player motion/geometry and prior owner are not encoded in the CatBoost row. Viterbi can propagate surrounding emissions, but cannot manufacture unobserved team-control evidence.

Aggregate missing-ball results are consistent with this limitation: the parent predicted D on99.9655% of corrupted missing-ball frames, with live recall .0638%. Adding PFF training improved live recall to8.9503% but worsened global scores. This is evidence of poor recovery, not proof that missingness alone causes every error, nor evidence that a specific new feature will fix it. Rates are pooled frame-weighted diagnostics and cannot replace equal-match spell results.

Source: docs/pff-evaluation-review-2026-11-07.md, completed-results addendum.

## What the rejected experiments do and do not imply

| Intervention | Recorded primary/paired evidence | Interpretation |
|---|---|---|
| Rolling whole-pitch feature bundle | Median corrupted spell−.005208; paired−.006600;1/5 improve | The tested2.5s broad aggregates failed; does not test explicit player–ball control history. Feature track was stopped. |
| Gap augmentation + penalty16 | Paired median−.001331;2/5 improve | Corruption exposure alone did not repair this representation at the fixed budget. |
| IDSSE + PFF48 | Median corrupted−.034930; paired−.056268;0/5 improve | This unweighted provider expansion failed. Row volume, visibility, convention and capacity are confounded; “PFF cannot help” is unsupported. |
| Scratch BiGRU hidden16 fixed25% blend | Corrupted median−.007520; paired−.008148;1/5 improve | A small fixed model over the same nine features did not help. It did not test richer player geometry. |
| TabICL10k /30k, one estimator, fixed50/50 blend | Blend primary medians+.001995 /+.001606; both1/5 paired improve | Small corrupted gains fail the full gate and do not justify further blind context-size search. No general conclusion about all TabICL settings. |
| Duration prior | Rejected; estimator includes censored fragments as complete endpoints | The implementation is not evidence against every duration prior, but decoder track has3failures and is closed. |

Sources: experiments/whole-pitch/report.md; experiments/combined16/report.md; docs/pff-evaluation-review-2026-11-07.md; experiments/gru-2026-11-08/report.md; experiments/tabicl-small-2026-11-08/gate.json; experiments/tabicl-medium-2026-11-08/gate.json; docs/review-data-scientist-2026-11-07.md.

## Decoder-reset concern: already narrowed, not a promising score rescue

Legacy scripts call blocks_valid(y, half_blocks), resetting at annotation X gaps; production uses metadata half blocks. That is a real general training/evaluation-serving concern for cohorts with unknown-label gaps. However, the completed evaluation review records known-label fraction1.0 for all scored arrays in the relevant cohort, so these resets do not create a demonstrated difference here. The GRU report explicitly verifies identical parent half-only versus legacy scores. Recent TabICL runners use half blocks for inference. No H/A/D label-transition reset was found in the inspected code paths. Do not present this already-known caveat as a likely explanation for the missing .28 or silently alter legacy scores.

Sources: scripts/review_frozen.py:blocks_valid; scripts/run_core.py; scripts/run_tabicl_medium.py:first_inference/score_initial; docs/pff-evaluation-review-2026-11-07.md:completed-results addendum; experiments/gru-2026-11-08/report.md.

## Next highest-value slice and conditional experiment

First refresh the error taxonomy for current penalty16 emissions/decoder, with no model selection or parameter changes: separate observed versus missing ball, fixed gap-duration bins, wrong-team versus dead/live errors, short-spell recall, and missed/spurious spells and boundaries. Prior detailed diagnostics use penalty8 and oracle repairs overlap; those repairs are counterfactual diagnostics, not additive headroom or achievable upper bounds. Use external development examples only; do not hand-label target video.

If that confirms ownership errors around handovers and gap endpoints dominate, propose one fixed temporal team-control feature bundle, preserving CatBoost/penalty16. A minimal candidate can summarize nearest-team evidence over a preregistered short past/future window with explicit observed-support masks, using no player-slot identity continuity. Relative player–ball motion is another candidate, but must not be bundled with look-ahead/history in the same trial: choose one from the failure slice. Never fill long missing gaps with fabricated confident ownership; unsupported context remains missing. Same folds/seeds/budget/corruption/gate; freezeNovember13. A feature-track amendment and committed protocol must precede execution.

A more-data alternative should first audit actual sampled training row counts by provider × H/A/D × ball visibility and per-match exposure. If confirmed provider dominance is addressed, source balancing would be a distinct one-change training experiment, not a retrospective rewrite of the failed unweighted PFF run. PFF16 stays descriptive transfer data, not a selection leaderboard.

Expected impact direction: temporal control evidence could improve short/hand-over spell correctness and robustness near observed gap endpoints. Magnitude is unknown, and gain may be zero or negative; long gaps without identifiable endpoints may remain ambiguous. The case for it would weaken if current-parent errors are primarily incompatible labels, observation noise or dead/live episodes that no proposed feature distinguishes.

Keep the sealed evaluation untouched untilNovember13. If a future development gain fails there, investigate bugs/transfer rather than tune on the sealed matches. This is the strongest protection against a visually attractive .8 that does not generalize.

## Ranking representation options before the freeze

1. **Light temporal ball-control evidence + existing CatBoost:** first choice after the diagnostic slice. It changes the missing information while retaining the tested classifier/decoder and has a smaller implementation/verification burden. No promised gain or runtime number.
2. **Raw player/ball trajectory temporal convolution with permutation-invariant team set pooling:** a scientifically plausible later architecture if richer geometric evidence is needed. It could learn motion/control rather than being confined to the nine-column bottleneck. However, it introduces player-presence masks, team pooling, temporal context, standardization, training objective and a new model implementation; provider/slot discontinuities and deterministic inference require explicit contracts. It is a substantially larger research intervention beforeNovember13 and should not be treated as an inexpensive follow-on to the failed small GRU. Scratch training on only four matches per fold also leaves generalization uncertain. Rank behind the minimal evidence test, not an immediate parallel architecture search.

The prior GRU result cannot distinguish a weak representation from an inadequate temporal architecture/training budget because both were fixed together. Neither a TCN nor a larger transformer has an identifiable attainable spellF1 from current evidence. In particular, no defensible .6–.8 range or probability of reaching .8 can be supplied.
