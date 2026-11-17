# Next quality decision after standalone gap-TCN — November 11

## Decision and strongest signal

The registered standalone comparison supports retaining gap-trained short-context TCN + penalty16 over the former50/50 CatBoost blend: clean/corrupted mean spellF1 .597707/.463139 versus .592502/.428386; median corrupted paired gain +.040271;4/5 paired wins. These are genuine protocol-matched development effects, not target accuracy. J03WN1 regresses on both settings, so improvement is heterogeneous. Repeated fits and CSV tests establish computational repeatability, not independent sampling evidence.

Recommendation: ONE fixed two-view test-time pitch-rotation average, using existing fold checkpoints. Compare identity-only probabilities against the equal average of identity and180-degree full-pitch-rotated probabilities, then apply unchanged penalty16. This is cheaper and cleaner than another training-budget extension. No new model architecture, decoder, training data, calibration, team swap or blend-weight search.

## Saved errors of the new leader

Calculated from experiments/tcn-standalone-2026-11-11/results.json, without loading arrays or executing a scorer:

|Setting|Missed spells at IoU.5|Spurious spells at IoU.5|Recalled short spells|Dead/live wrong frames|
|---|---:|---:|---:|---:|
|Clean|1,086|497|142/732 (19.4%)|2,814|
|Target-like corrupted|1,373|772|90/732 (12.3%)|58,039|

These are five-match sums, not independent trial counts or the official mean-over-IoU spell metric. Median diagnostic oracle repair gain is .360612clean/.378167corrupted for wrong-team errors versus -.005197/.105028 for dead/live. These oracle repairs use true labels, overlap other errors, and can change spell segmentation non-monotonically. They neither quantify achievable headroom nor identify the best intervention causally. Still, team-control mistakes and missed short spells remain larger unresolved problems than clean dead/live mistakes.

The proposed symmetry test addresses avoidable spatial-orientation sensitivity in the H/A emissions, not the entire long-gap or short-spell problem. Reduced spatial nuisance could improve team-control predictions; smoothing probabilities across views could instead erase useful brief boundaries. Direction and magnitude of held-out gain are unknown.

## Why this is a legitimate single intervention

Source inspection: prepare_tcn.encode stores centered XY, normalized velocities, visibility and fixed H/A/ball role flags for64slots, followed by nine invariant core features. The current object convolutions consume signed XY/velocity and therefore do not enforce pitch-rotation invariance. gap_training.py samples clean/gap windows only; no pitch or team-swap augmentation is present. A180-degree rotation of all positions/velocities preserves physical possession-team labels, distances, speed magnitudes, pitch-edge distance, observation masks and gap ages.

For an encoded input copy, reshape the first512channels into64x8 and negate channels0:4 (XY and velocity). Leave visibility, role flags and finalninecore values unchanged. No H/A label or probability-column permutation applies. Preserve exact zero values for absent objects. This transformation is an involution; intended football state is unchanged. Use a transformation-specific synthetic contract and compare against locally generated raw synthetic rotated-track encoding, with floating-point tolerance justified, before scoring. Never use target rows for a semantic test.

Do not introduce team swap at the same time: that requires swapping H/A flags and core distances/masks, negating distance margin and permuting output columns, a distinct intervention. Do not search among four reflections after inspecting results. Freeze just identity plus180rotation at50/50.

## Registered evaluation proposal

Parent: current retained standalone gap-TCN, not historical blend. Existing five LOMO checkpoints and frozen ten clean/target-like inputs. Verify fingerprinted checkpoint/input ancestry and reconstruct identity parent CSV bytes/metrics from the completed standalone trial. Average probabilities, normalize once, decode full halves with16. No tuning or training. Report every match/condition spellF1/macroF1, short-spell metrics, missed/spurious counts and missing-ball dead/live quality. Verify initial/reload/batch CSV identity for the averaged prediction; restrict CPU/interop to1, deterministic Torch/MKLDNNoff. Preserve X outside blocks and unknown-label scoring semantics.

Promotion: median target-like corrupted spell gain >=+.01 versus current parent, positive median paired clean/corrupted spell gain, >=3/5pairedwins, median paired macro gain >=-.01, contracts/repeatability pass. Failure closes the fixed symmetry comparison without automatic reflection/weight/temperature rescue. Historic stopped decoder/data-expansion tracks remain stopped. Precommit source/protocol/inputs before user-run execution; all tests/model/scoring remain user-run. No target labels, sealed matches or PFF holdout access. No production promotion without release checks.

## Why not40k first

All five archived gap-training minibatch loss sequences continue falling: mean16k–18k to18k–20k changes are respectively .237720→.228550, .226903→.217001, .245808→.232567, .228568→.221891 and .260777→.248796. This establishes ongoing optimization on sampled training batches, not held-out underfitting. There is no corresponding late-stage held-out validation curve. Increasing updates could help or overfit and doubles training cost. No40k protocol should be justified as a proven convergence need. It would require an explicitly isolated budget change with fold-safe scratch training or correctly checkpointed optimizer/RNG continuation; current saved short checkpoints lack optimizer state, so naive continuation cannot claim the same training trajectory.

Seed averaging is also plausible but requires additional full fits and introduces an inference ensemble after source expansion/context already consumed development selection. It is not a free independent-data validation. Prior relativeXY/long-context/PFF failures remain recorded; do not rerun them under new names. The fixed symmetry test has the best information-per-compute ratio among these untested choices, not a proven largest expected score gain.

## Confidence and release risk

High confidence in the saved gate arithmetic and observed current-model error counts. Moderate confidence that signed XY/velocity create an untested symmetry sensitivity. Low confidence in a positive held-out gain or competition ranking. Five repeatedly reused matches and overlapping training folds invalidate frame-level confidence intervals or an independent-binomial interpretation of4/5wins. No defensible probability of winning or reaching.8 follows from these data.

A numerical improvement would be invalidated as a release argument by target adapter temporal-identity errors. Target slots must be stable for adjacent-frame velocity; metadata shape checks alone are insufficient. Prepare retained-recipe release qualification in parallel and preserve one sealed evaluation after November16freeze, with low scores triggering bug/transfer investigation rather than tuning. Reserve November14–15 for delivery. Target accuracy remains unknown.

Sources: AGENTS.md; research-state.yaml; ball.md J087–J089; experiments/tcn-standalone-2026-11-11/{results.json,result-audit.json,protocol.md}; experiments/tcn-gap-2026-11-10/{gap_training.py,*training-loss.json}; scripts/prepare_tcn.py; experiments/tcn-2026-11-10/tcn_candidate.py; docs/tcn-training-strategy-review-2026-11-11.md; literature/tcn-transfer-context-refresh-2026-11-11.md. Analysis read aggregate metrics and losses only. No tests, imports, compilation, training, inference, scorer execution or raw input loading.

## Priority amendment: temporal-slot stress diagnostic before symmetry scoring

A subsequent release review identifies official DATA.md99–101 / OVERVIEW90–93 as explicitly allowing slot swaps. The earlier recommendation treated target temporal identity as a release caveat; this evidence elevates it to the immediate next action. A cheap symmetry gain would not resolve a model whose temporal object encoder or velocity construction misinterprets changing slot identities. Defer the proposed symmetry comparison until an external-only slot diagnostic is reviewed. This changes priority, not model selection or the promotion gate.

Register one diagnostic on the existing five held-out checkpoints and ten clean/corrupted encoded inputs, without training or target raw/label access. The parent remains the retained standalone gapTCN. Distinguish a pure static permutation control from velocity reconstruction and hypothetical dynamic churn. Do not promote any candidate from this stress test or infer target accuracy from its magnitude. Detailed scientific controls: docs/tcn-slot-audit-design-review-2026-11-11.md.
