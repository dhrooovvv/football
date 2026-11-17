# Fixed pretraining comparison — independent source review

November11,2026. Scope: scripts/run_tcn_pretrain.py; experiments/tcn-pretrain-2026-11-11/{pretrain_data.py,pretrain_model.py,pretrain_training.py,tests/test_pretrain_model.py,protocol.md,membership.json}; docs/run-tcn-pretrain.md. Source inspection only. No tests, model/data imports, compilation, arrays/checkpoints, inference, scorer or training were executed/read. New input locks remain the parent's responsibility before registration. Static review does not certify runtime correctness or possession quality.

## Correctness boundaries reviewed

GeometryCase opens only objects/roles/core/gap_ball/gap_core arrays and metadata, never possession labels. Targets require clean visibility AND synthetic-gap missingness; naturally missing or still-visible ball locations are not reconstruction targets. Geometry eligible starts are observation-based and remain in real half blocks with at least one central target. Existing full-half raw-before-feature gap views provide consistent derived inputs; provenance must remain hash-pinned. Synthetic targets are not supplied to the class inference path or fused as new observations.

Model constructs OriginalTCN first, then the66parameter32-to-2 reconstruction head. Class inference remains the inherited path; pretext bypasses the class head while updating shared weights. This preserves class initialization and motion/history, not original learned weights after pretraining. Loss is maskedXY MSE, not another segmentation objective. No use of held-out possession labels for inference.

Membership guards compare committed fold definitions to existing splits. Supervised cases are exactly the otherfourIDSSE matches; candidate geometry is thosefour plus48eligiblePFF matches. The held-out match is absent from its geometry list, including unlabelled use. Protected IDs and PFFholdouts are excluded. Control receives no geometry-case list. Hashing registered label files as byte integrity evidence does not mean GeometryCase consumes their labels.

Control20k+20k supervised and candidate20kpretext+20ksupervised both resetAdam and supervised sampler/view RNGs at the stage boundary. Protocol explicitly identifies this as a reset control, not continuous40ktraining or exactcompute matching. Checkpoints include identity, optimizer, allRNGs, step/stage, losses, coverage, target and supervised-view counts. The step-at-boundary resume resets once before stage2; midstage2 resume restores the current optimizer without another reset. Repeated states/losses/coverage/target and view counts are checked.

Runner completes control first and uses it as promotion parent only on fullgate pass; otherwise rotation remains parent. Candidate is judged against the actual retainedbest, while both references stay in diagnostic rows. Fullgate includes+.01 median corrupted spell gain; means alone cannot promote. Both original/rotation views require exact reload probabilities, and initial/reload/batch4 decodedCSV bytes must agree. No automatic production promotion, finalfit, target export or protected evaluation occurs.

## Concrete issues caught and corrected before registration

1. Synthetic perturbation fixture originally used a250-elementboolean mask on600-frameobjects. Corrected to objects[indices[valid],-1,:2], with a new-file replacement while prior arrays may be memory-mapped. This avoids a guaranteed preflight indexing failure. Source inspected; test remains unexecuted.
2. Runner originally retained a52case geometry mapping list while constructing the nextfold's list, temporarily doubling open mappings. It now explicitly deletes geometry and model/checkpoint objects after each completed fold (scripts/run_tcn_pretrain.py, end of evaluate_arm fold). This reduces file-descriptor and memory pressure on the Mac. Actual descriptor limits/peakRAM remain unmeasured.

## Supplied verification and residual risks

Eight new synthetic contracts cover original initialization/class path, no label reads, target masking and input independence, half-local observation-only windows, masked gradients, membership rejection, shared stage reset/RNG behavior, and exact interrupted resumption at/midstage2. Existing46contracts are integrated as well. These54checks are supplied, not executed by this reviewer. User must run the registered command; normal dataset/runtime and new-arm inference proof remain pending.

No remaining blocking defect was found by this source pass after the fixes above. Residual risks include real prepared-manifest/schema compatibility, runtime/resource limits, exact resumption across the registered environment, and statistical generalization after repeated reuse of five development matches. The original17frame receptive field still limits missing-ball context; reconstruction loss may not improve short possessions. Geometry pretraining can still carry provider/identity shift. Current .602155clean/.477682corrupted is an eligible development baseline, not evidence of target accuracy or winning rank. Historical stopped tracks and freeze/release safeguards remain intact.
