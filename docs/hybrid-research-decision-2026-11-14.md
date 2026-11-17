# Selected hybrid for the next bounded trial

Research completed November 14, 2026 using the ECC market-research source standards and two agents, a primary-literature researcher and an independent data scientist. This decision selects one candidate for implementation preparation. Runtime, hardware qualification and development scores require the user's execution. No new experiment has run.

## Decision

Select the frozen Trial-B TCN ensemble plus a compact coarse temporal residual refiner. The parent supplies full-rate local probabilities. The learned refiner supplies a contextual correction before penalty-16 decoding. This choice targets the long-gap error association and reuses the completed parent weights.

The first candidate's input is fixed to five channels: the three parent probabilities, the existing ball-observation mask, and the existing normalized gap age. Pool these over five-frame bins anchored to the real half, giving 5Hz context. Keep full-rate parent probabilities as the local path. Do not concatenate hidden player embeddings or all nine core features in this candidate.

A concrete small architecture for the implementation protocol is an input projection to16channels, six residual temporal blocks with kernel3 and dilations1/2/4/8/16/32, and a zero-initialized three-channel correction head. With one dilated16→16 convolution and one pointwise16→16 projection per block, this has6,483trainable parameters by arithmetic. Its127coarse-bin field nominally covers25.4seconds before full-rate interpolation and the frozen parent's own support. The exact full-rate support and chunk halo must be derived and checked during implementation. No dropout, normalization, context search or coefficient grid is proposed.

The correction is interpolated to25Hz and added to log parent probabilities, followed by normalization. Zero correction must reproduce the archived parent's decoded CSV bytes. Floating-point probability comparisons need an explicitly fixed numerical tolerance because log/softmax recomputation need not preserve probability bytes. Training and inference must share the same interpolation grid, boundary padding and feature normalization. This is one project adaptation of temporal refinement, rather than a reproduction of MS-TCN++.

## Evidence and contrary findings

The denominator audit finds621/910possessions exposed to>10second gaps missed atIoU.5(68.24%), versus540/1134fullyobserved(47.62%). The higher miss rate occurs on all five matches and within each of the three coarse duration strata. These are exposure associations. Full intersecting burst duration does not imply every frame of the possession was missing. [Independent assessment](hybrid-independent-assessment-2026-11-14.md)

The prior13second deeper-TCN comparison failed. A new frozen refinement stage preserves the local predictor and changes the optimization problem. MS-TCN++ explicitly compares refinement with deeper single-stage models and separately tests passing probabilities versus hidden features. These video-action results motivate the mechanism but provide no forecast for football spellF1. Its smoothing objective will not be imported into this trial. [Primary paper](https://arxiv.org/html/2006.09220v2)

Both research agents favor temporal refinement first. The literature reviewer prefers probabilities-only inputs. The data scientist prefers including frozen player-motion embeddings because probability inputs could merely smooth mistakes. Root chooses probabilities plus the two existing missingness controls as a minimal initial interface. No local experiment establishes this input choice as optimal. The refiner cannot create new geometric evidence absent from its inputs, and it could erase short possessions or fail to recover any omitted event. These risks belong in the result interpretation.

## Why the graph alternatives follow later

A GNN–TCN would introduce explicit cross-player and player–ball messages, a capability our team mean pooling compresses. The failed attention trial was restricted to within-team attention and does not test every relational design. However, graph messages alone preserve the short temporal support. Adding both a graph encoder and a long-context branch would combine two mechanisms in the first trial. The frozen refinement candidate is the narrower next test.

BallRadar and TranSPORTmer provide social-plus-temporal modeling references. PathCRF adds structured player-pair paths. Their supervision, taxonomy or event/trajectory metrics differ from full-match H/A/D spell detection. The October2026GNN-LSTM phase model also uses possession/ball status as inputs. No reviewed source establishes a winning GNN–TCN score on our official scorer. Detailed architectures, task differences and source links are preserved in the [primary evidence review](../literature/hybrid-primary-evidence-2026-11-14.md).

PathCRF's repository uses the seven-match Sportec Open DFL source and includes pretrained models. Their overlap with our held-out and sealed matches is unresolved. Those checkpoints cannot be admitted without a match-membership audit. No weights were downloaded. [Author repository](https://github.com/hyunsungkim-ds/pathcrf)

MS-TCN2 has an explicitMITlicence. A verified public code licence was not found for BallRadar or an official TranSPORTmer implementation in this review. Implement the small refinement mechanism locally using the existing PyTorch dependency. No external implementation or dataset is required. [Official licence](https://github.com/sj-li/MS-TCN2/blob/master/LICENSE)

## Evaluation and implementation boundary

Use the five original outer folds and the selected B out-of-fold parents. Exclude each held-out match from parent/refiner fitting and preprocessing estimates. The final-five model is reserved for delivery. Frozen-parent predictions on the four fold-training matches are in-sample relative to the parent. This stacking distribution shift must be disclosed. Nested parent refits would require a separate budget amendment and are outside this bounded candidate.

Retain seeds20261106/20261107, original short-spell sampler, clean/gap view selection, CE+.1segment-soft-IoU loss,40kstaged20k/reset/20k updates, batch8 and decoder16. Two refiner initializations and two exact repeats per outer fold give20refinerfits, with zero parent fits. Generate training views from the original training corruption arrays and evaluate only the frozen clean/targetlike cases. Retain parent rotation averaging before refinement. Inputs are direction-invariant, so no second spatial rotation of probability/missingness channels is required. Average the two refined probability outputs equally.

Before execution, implementation must commit source, input/membership/environment fingerprints, exact grid/padding/support/loss-window rules and the protocol. Supply user-run checks for half/X isolation, held-out exclusion, zero-correction archived CSV reproduction, stream/cache identity, resume equality, repeated fits, reload probabilities and inference-batch CSV equality. Compare the actual retained parent on the same cells through the unchanged official scorer and positive-median gate. Include duration/gap recall, missed/spurious counts, boundary timing and missing-ball dead/live quality. No new smoothing loss or decoder change belongs in this candidate.

The new branch adds compute and capacity. A passing result establishes an advantage for the full intervention under this comparison, without uniquely attributing it to context. A matched-context control would be a separate experiment. Reused five-match selection remains optimistic and the sealed evaluation must retain its once-only interpretation rule.

Hardware feasibility is qualitative. Coarse convolution and a frozen parent should require less training activation memory than a full long-window relational model. Parent probability preparation still incurs inference work. User-run preflight must measure elapsed work, peak memory and artifact size before the full comparison. No runtime estimate or speed guarantee is established. Enforce the existing2GiBartifact cap and12GiBfreefloor, stream inputs and preserve failed outputs. All tests and training remain user-run. A complete candidate must finish before the November16freeze. Clean-environment/fresh-clone delivery qualification also remains pending.
