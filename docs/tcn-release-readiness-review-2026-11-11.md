# TCN release readiness: source-only review

November 11. Boundary reviewed: IDSSE identity-based positions → normalized 521-column representation → gap-trained short-context TCN checkpoint → H/A/D probabilities → penalty16 full-half decoder → deterministic CSV. Compared this with target ATD slot adapter and the existing candidate exporter. No code changed outside this report; no private asset, array, checkpoint contents or target prediction read. No imports, compilation, tests, training, inference or scoring executed.

## Primary transfer risk: identity-dependent computation before pooling

Official challenge documentation explicitly says that the 46 slots for22 players appear, vanish and **swap identity** (`reference/more-than-a-hack-2027-main/DATA.md:99–101`, `OVERVIEW.md:90–93`; the starter baseline repeats this at `starter/baseline.py:87–89`). These are supplied input semantics, not an inference from private target observations. A persistent-person guarantee is absent by design; requiring the target data to prove that guarantee cannot resolve the documented mismatch.

The external adapter uses `(team, PersonId)` slots (`src/possession/external.py`). `scripts/prepare_tcn.py:31–35` computes velocity by differencing the same slot whenever adjacent frames are both observed. Identity switches between adjacent observed frames are not masked. Supplied ATD speed is not used by this encoder; normalized-coordinate displacement times25 is used instead. Per-source normalization is consistent at the code level, but no runtime parity check was executed here.

`experiments/tcn-2026-11-10/tcn_candidate.py:18–25` applies a three-frame object convolution to each slot before team pooling. A single same-team permutation held fixed through a window is a symmetry of the mathematical architecture (floating accumulation order may still perturb bytes). A permutation changing between frames is not: it changes both velocity and each object's temporal neighborhood. Team mean pooling afterwards cannot undo that change. The temporal network can therefore receive different emissions for identical team position sets represented by different cross-frame track identities.

This is a plausible train/serve transfer mechanism, not evidence that it currently dominates spellF1 or that the existing candidate fails on the competition match. No target accuracy claim follows. Fragmented/reacquired tracks and potential simultaneous duplicates also change observation support and averaging weights; current metadata checks do not certify coverage or absence of duplicates.

## Smallest useful next preparation

Prepare one registered user-local **label-free adapter diagnostic** before release. Output aggregates only, with source hashes:

1. For each half/team: observed-slot count distribution, zero-player fraction, contiguous observed-run length distribution, reappearance-after-gap distribution, and adjacent-observed displacement/speed quantiles. Use each source's pitch for metric diagnostics; distinguish these metrics from normalized encoder velocity.
2. Report jumps and very close same-team observations across a few fixed, documented diagnostic thresholds. These flag suspect representation segments, never certify person identity or authorize target relabelling/repair.
3. Compare those statistics against the five external training matches without target labels or any selection based on target accuracy. A quiet report of no jumps cannot establish identity correctness.
4. Add synthetic user-run contracts showing fixed same-team permutation behavior and time-varying slot-swap sensitivity. A meaningful external stress evaluation can then preregister one fixed slot-fragmentation policy using local label-free evidence; it must not silently alter production or become an unbounded robustness search.

Do not zero velocity or replace object Conv1d as an unregistered “bug fix”: either changes the model representation and needs a fresh external-only comparison against the new retained standalone parent under the existing gate. Likewise, nearest-neighbor identity reassignment can introduce wrong correspondences and must not be added without evidence. This report does not select a model change or claim that augmentation will solve the mismatch.

## Current exporter is for a different model

`scripts/export_neural_candidate.py:53–60` requires the rejected final53 checkpoint, original membership,20k steps and seed. At its probability stage it always mixes CatBoost50/50; its provenance also records blend weights[.5,.5]. It is deliberately registered for that older artifact. It cannot qualify or export the retained **IDSSE gap-trained standalone TCN** merely by changing a command argument. Preserve the old evidence and create a separately registered retained-candidate final-fit/export workflow.

That workflow should embed exact development-only training membership, architecture/feature schema, augmentation and optimizer configuration, seed/budget, preparation/source hashes and environment in the final artifact. Never fit the sealed IDSSE2 or PFF16. A five-development-match final fit is not itself held-out quality evidence. Full-training clean-environment reproducibility and frozen-inference byte equality are distinct checks.

The exporter does have useful code-level protections to preserve: private staging/output paths, untouched production CSV, explicit H/A/D class order, X outside configured half blocks, unchanged official format validator, reload/batch CSV hash equality and recorded provenance. These are static observations, not runtime passes for the retained winner. The current standalone evaluation records within-environment checks only; its final training artifact and serving path do not yet exist.

## Release decision and validation still required

Keep the newly eligible standalone candidate for development selection and retain current production until qualification. First resolve how much the documented identity mismatch affects serving assumptions using local aggregates and a bounded external diagnostic. Then register the correct final fit/export path. User runs all contracts, fit and export; provide fail-closed behavior for wrong model/config/source hash or changed shape, official validation, initial/reload/batch byte checks, clean environment and fresh-clone reproduction. PeakRAM/full export latency remain unmeasured.

Residual risks: source annotation differences, tactical tracking gaps/identity switches, reused-five-match selection optimism, target accuracy unknown, and no frozen sealed evaluation yet. A low sealed score triggers the prewritten bug/transfer investigation rather than tuning. No fallback, hosted processing, public-score selection or external publication is recommended here.
