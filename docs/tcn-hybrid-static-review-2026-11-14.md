# Sequential hybrid implementation static review

Review date November 14, 2026. Model/training review was performed by an independent agent. Root completed the integration source review after the agent service reached its usage limit. All tests, project imports, compilation, model loading, array/CSV processing, inference and scoring remain user-run. The reviewer has inspected source and existing aggregate metadata only.

## Scope

The new temporal-refinement and graph-correction models, half-anchored context adapter, training checkpoint/resume contract, sequential development runner and final qualification path under experiments/tcn-hybrid-2026-11-14. Historical registered source remains outside the modification boundary.

## Confirmed correction

The initial graph parameter-count constant was 10,555 while the declared modules contain 9,835 parameters by static arithmetic. The author corrected the constant before execution. The temporal model's declared 6,483 parameters agrees with the specified convolutions. Runtime parameter-count contracts still need execution.

## Model and training boundary reviewed

- Temporal context uses the full real-half five-frame grid, actual centres for partial terminal bins and clamped interpolation. The fixed 169-bin input includes the interpolation brackets for 200 full-rate targets plus 63 bins of convolutional support on either side. Context does not reset at a sampled central crop.
- Graph construction masks absent nodes, excludes player self-edges, includes all cutoff-distance ties and connects the observed ball to all visible players in both directions. Fewer than four available neighbours are handled by the candidate mask and infinite cutoff. Per-team readout is masked, including empty groups.
- The training correction remains differentiable at zero initialization. Exact-parent inference fast paths do not replace the training gradient path. Graph correction uses both rotation views and preserves parent values outside real half blocks.
- The new trainer preserves the original short-spell sampler, clean/gap draw sequence, central 200-frame labels, complete-spell auxiliary objective and 20k optimizer/sampler reset. Checkpoints include model/optimizer, all RNG states, component losses, match/view exposure and sampler accounting. Exact repeat comparison intentionally excludes timing.

## Integration review

Root reviewed the completed runner/contract, final-fit/export/sealed entrypoint, protocols and runbooks. The graph edge MLP was changed to evaluate actual edges while preserving defined adjacency, avoiding dense masked message work. Final-work projection includes serial final fits. Registration separates pre-freeze research and delivery date guards. Reviewed temporal results bind graph parent weights. Delivery checks final identities and repeated checkpoints, all-three export equality, and once-only sealed candidate identity. Sealed raw sources are first accessed at freeze, with prospective corruption seeds20261206/20261207 and fixed baseline widths. All37 supplied tests remain UNEXECUTED. Independent integration review did not complete because the agent service reached its usage limit. Static review cannot certify execution or numerical repeatability.

## Residual verification

The user must execute synthetic contracts, archived-parent CSV/score reproduction, actual preflight timing and RSS checks, full repeated fits, reload/batch CSV equality and clean-environment/fresh-clone qualification. The current five matches have been reused for selection. Target accuracy and independent sealed performance remain unknown.
