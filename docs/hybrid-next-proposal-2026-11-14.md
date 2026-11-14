# Hybrid feasibility and next proposal

Reviewed November 14, 2026. This document proposes one prospective intervention. It authorizes no runtime or experiment and changes no selected model. User execution remains required for every test, inference and fit.

## Completed artifact

The user supplied the successful output of scripts/export_tcn_final_b.py. First, reload and batch4 passes produce SHA256 3dca80aa3b18a8c8e880b9f26cf1dc4f17a13018df18a2e4b39cf30f7da63463. Saved completion/aggregate files and the three CSV byte hashes were checked again without reading rows. The completed evidence matches the previously audited local export. Clean-environment and fresh-clone outputs are absent. Export qualification adds no development accuracy measurement.

## Prior result that constrains the choice

The November 11 dense-context experiment already tested about 13 seconds of context. It changed depth and capacity, trained from scratch for 20k updates and selected a fixed CatBoost blend. The blend scored .579905 clean/.428623 corrupted versus its parent .592502/.428386 and failed paired/majority gates. The descriptive standalone result was .570995/.432275. Source evidence is experiments/tcn-context-2026-11-11/result-review.md. The November 14 recommendation should have explicitly included this failure. It rules out treating a repeated deeper/dilated stack as a new evidence-backed step.

## Proposed hybrid

Recommend a frozen local TCN ensemble with a separately learned coarse temporal residual refiner. Preserve the current local predictions and learn corrections using longer surrounding context. A concrete design to register is a small one-dimensional residual convolutional refiner over 5Hz pooled inputs, using the three parent probabilities and the existing nine encoded core channels. A 25-second context would span substantially longer intervals than the current approximately .68-second local receptive field. The final correction is interpolated back to 25Hz and added to log parent probabilities before the existing decoder. Zero-initialized output corrections reproduce the parent before learning.

This is a feasibility design, not an approved experiment protocol. Exact layer support, grid alignment, unknown/half handling, interpolation, central supervision and the repeated-fit budget must be fixed in the implementation protocol before execution. Coarse context may erase brief transitions if it dominates, so preserve full-rate local predictions and require short-spell diagnostics and clean performance alongside the existing promotion gate.

Use original LOMO B checkpoints. Each refiner trains only on that fold's four eligible matches, with the held-out match excluded from every fit and preprocessing estimate. Frozen TCN training remains fixed. Training-time predictions on the four training matches are in-sample relative to the parent, creating a possible stacking distribution shift that must be disclosed. The existing held-out evaluation provides the comparison, without treating it as independent confirmation after repeated selection. No final-five model may supply development evaluation predictions.

## Why this hybrid precedes a graph encoder

The latest diagnostic finds long-gap absence of an argmax spell match leading on all five matches. A GNN could improve player relationships but requires new encoder training and by itself does not enlarge temporal support. The current masked team mean aggregation already handles consistent within-team slot permutations. A GNN plus longer temporal support would change two mechanisms simultaneously. Graph-based encoding remains a conditional follow-up requiring its own evidence and authorization.

## Decision and qualification

At most this one hybrid is proposed. Historical failed trials, the positive-median promotion rule, sealed exclusions and November 16 freeze remain in force. Prepare a source-committed protocol and resumable user runner only after the user approves this particular direction. Estimate runtime from a user-run bounded preflight before scheduling the full comparison. Training cost, memory and any spellF1 gain are currently unmeasured. Complete clean-environment/fresh-clone delivery qualification separately using the existing export guide. No new dataset is needed for this proposal.


## November 14 research decision update

The completed primary/independent research is recorded in hybrid-research-decision-2026-11-14.md. It supersedes the preliminary nine-core-plus-probability interface above with three probabilities and the existing observation-mask/gap-age controls. Both agents prefer temporal refinement before graph replacement but disagree over extra hidden inputs. The decision documents that uncertainty. Implementation and preregistration remain pending.
