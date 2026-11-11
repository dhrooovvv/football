# Temporal-slot diagnostic design review — November 11

Decision: determine whether retained gapTCN depends on persistent per-slot player identity, and whether a claimed stress effect could instead be an input-transformation bug. This is external-only robustness diagnosis; it does not select a new model or reconstruct actual target churn. Official format documentation allowing swaps is a concrete precondition for investigating training/serving mismatch. Documentation citations come from the release review; no restricted rows or assets were read for this review.

## Arms and the confound to remove

Use the five original fold-safe checkpoints and ten existing clean/target-like encoded inputs, with frozen penalty16 and existing official scorer. Fix RNG seed20261111+i per development match, without post-result resampling. All existing labels remain unchanged. Require exact identity-parent CSV reconstruction before interpreting any modified arm.

1. **Parent:** original encoded inputs.
2. **Static permutation control:** sample one same-team player-slot permutation per real half. Apply it identically at every frame to each whole eight-channel player vector, INCLUDING its stored velocity and visibility/role flags. Ball slot and nine core channels stay untouched. No velocity rederivation. This probes intended object-order invariance, without a precision confound.
3. **Velocity-reconstruction control:** identity player ordering, but recompute player velocity from encoded XY and visibility, with the same procedure as the dynamic arm. This distinguishes rounding/reconstruction effects from churn. It introduces no identity change.
4. **Dynamic same-team shuffle stress:** independently permute player eight-channel vectors within each team at each frame. Then recompute player velocity in the shuffled slot sequence. Ball vector and nine core channels remain original. Compare the stress result against BOTH parent and velocity-reconstruction control.

If only three arms can be implemented, omit the reconstruction control only with an explicit limitation: the dynamic-parent difference combines slot churn and velocity reconstruction. Do not call that an isolated churn effect. Four fixed arms cost only inference and better reduce uncertainty. A second dynamically shuffled arm preserving stored velocities could further isolate object-convolution identity dependence, but is outside this bounded diagnostic and should not be added automatically.

## Reconstruct velocity carefully

The encoder uses centered XY=2*(normalized_position-.5), so normalized velocity is12.5*first_difference(encodedXY). Recompute only for player slots and only when current AND previous shuffled-slot visibility are both1. Otherwise set velocity to0. Clip each axis to[-5,5], preserving float32 convention. Set first-frame velocity to0 independently at every real half; do not cross half, chunk, unknown-label or corruption boundaries incorrectly. Unknown labels must not define new temporal blocks. A disappearing object invalidates its slot velocity; arbitrary transitions between visible different players produce the intended extreme fake-velocity stress.

Original encoder casts raw positions to float32 before computing velocity, whereas reversing centered XY can lose precision. Therefore the rederived-identity control need not be bit-identical to the original. Report max input velocity difference and parent/rederived probability and CSV differences, rather than dismissing them as negligible without measurement. The static arm does not have this rederivation issue and should preserve the mathematical model up to reduction-order roundoff.

Same-team permutations include missing player slots carrying that team's fixed role; preserve the frame's multiset of role/visibility/position values. Never permute ball or cross teams. The slot permutation must not be selected using true labels, predictions, distance to ball or target statistics. Ball/core stay fixed because the spatial multiset and its per-frame distances are unchanged. This does not preserve physically meaningful velocity under dynamic churn; that distortion is precisely the stress being tested.

## Preregister interpretation without a result-based threshold

Report every match/condition's spellF1, macroF1, short-spell recall, missed/spurious counts and dead/live errors, as well as per-arm probability-difference summaries, CSV equality and reconstruction diagnostics. Fix the static control numerical tolerance in the protocol before running (for example max absolute probability difference1e-6 under CPU1, accompanied by exact CSV equality results). This is a mathematical-invariance check, not a performance-promotion threshold. Floating-point permutation of pooling summations can alter probabilities slightly; if a CSV differs, investigate numerical/boundary sensitivity rather than automatically declaring a semantic failure.

If the static control exceeds its preregistered probability tolerance, stop interpretation and investigate input mapping/model invariance first. If the reconstruction control changes quality materially, dynamic-parent changes cannot be attributed solely to churn; report dynamic-versus-rederived differences explicitly. Do not invent a post-result materiality cutoff. A drop in dynamic-versus-rederived quality supports dependence on temporal slot consistency under this extreme synthetic reassignment, not a numerical estimate of target failure. A small drop does not certify target support because real tracklets, substitutions and missingness may interact differently from independent shuffles.

No arm is a new candidate. There is no promotion gate application, no tuning, no changed production recipe and no validation-label-driven choice. Regardless of stress score, resolve target slot semantics at adapter/model level before release. A potential repair would need its own preregistered one-change trial and the existing quality gate against retained standalone TCN.

## Execution and uncertainty

User runs all tests, inference and scoring. CPU1/interop1, deterministicTorch/MKLDNNoff; reload/batch CSV checks remain required where applicable. Commit protocol/input/source hashes first. Never access target labels/rows, sealed matches or PFF holdouts. Preserve November16freeze and stopped tracks. Target accuracy unknown. Five reused matches and overlapping folds make this descriptive robustness evidence, not independent statistical confirmation. No new tests, model imports, compilation, raw-array loading, inference or scorer execution occurred in this review.

## Implementation static addendum

Inspected scripts/audit_tcn_slots.py, slot_transforms.py, tests/test_slots.py and protocol.md without executing code. No additional blocking transformation defect identified. Static permutation copies all eight channels consistently within real halves; dynamic and identity controls use the same12.5scaling, adjacent-visibility support, axis clipping and half-first-frame zeroing. Ball slot and core9 are checked unchanged. Permutation streams are independent of labels and observation counts, so the same clean/corrupted role groups receive the same fixed random reassignments. Unknown labels are not temporal boundaries.

Root review is addressing controls.json, quality deltas against parent/rederived_identity, explicit git commitment of required source/protocol and test subprocess PYTHONPATH. These must be resolved before locking; this addendum does not claim they are already fixed. Role constancy is checked, while full one-hot/ball-slot validity is not yet enforced inside the transform; with fingerprinted known encoder outputs this is defensive hardening rather than a new confound. The numerical static control must be recorded as a prerequisite to interpreting churn, not silently treated as a model-quality pass. Runtime, test success and score behavior remain unverified.
