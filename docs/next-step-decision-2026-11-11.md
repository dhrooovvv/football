# Next decision after the standalone TCN pass

November11. The user asks for the strongest permitted next step with agents and previous research. Current quality leader is gap-trained standalone short-context TCN + penalty16: mean held-out spellF1 .597707clean/.463139corrupted, not a target score. Its last registered comparison passed4/5pairedwins and medianprimary+.040271. Production remains CatBoost16 pending qualification.

Three independent reviews revisited the evidence: a data scientist analyzed saved current-leader errors/losses, a literature researcher checked primary symmetry/ensemble/segmentation sources, and an ML engineer audited release assumptions. No new tests/model/scorer runs or protected data access. Their reports are docs/tcn-next-quality-review-2026-11-11.md, literature/tcn-next-step-evidence-2026-11-11.md and docs/tcn-release-readiness-review-2026-11-11.md.

## Priority decision

Prepare one external-only temporal-slot compatibility diagnostic before any further candidate selection. Official challenge DATA.md99–101 and OVERVIEW.md90–93 explicitly describe slots changing identity. In contrast, external training uses persistent PersonId, adjacent-slot velocity and per-slot temporal convolution before collective pooling. Fixed player-order invariance cannot establish robustness to changing identities over time. This is a concrete representation mismatch mechanism; its metric cost is unknown and cannot be inferred from documentation alone.

The four fixed arms separate original behavior, pure fixed-order invariance, velocity rederivation rounding and severe temporal identity churn. Same five checkpoints/ten frozen cases, unchanged scorer/decoder, no retraining. Commit protocol before user execution. The stress is deliberately extreme and uncalibrated to target: it tests dependence, not expected target accuracy. If controls fail, investigate them first. No numerical threshold in this diagnostic promotes or rejects a candidate. Results determine whether ONE identity-robust representation experiment should be proposed under the full unchanged promotion gate.

## Quality opportunities held in reserve

The data scientist proposes identity+180degree pitch rotation output averaging; the literature researcher proposes team-role swap output averaging. Both are valid hypotheses with different transforms and failure modes. Neither has measured improvement here, so there is no defensible claim which is better. Do not bundle them or select between their scores after an unregistered search. Defer symmetry until the serving assumption is assessed, then preregister at most one if still appropriate.

Current leader recalls142/732shortspells clean and90/732corrupted atIoU.5; wrong-team oracle repairs have larger diagnostic effects than clean dead/live repairs. These are not achievable headroom estimates. Learning losses decline late in allfivefolds, but no corresponding validation curve proves20kundertraining.40kupdates, seed ensembles and loss modifications remain untested alternatives; none is automatically authorized as a simultaneous change, and no source forecasts spellF1=.8 or a winning threshold.

PFF expansion stopped afterthree failures, larger context/relativeXY fixed trials rejected, decoder track stopped. Generic literature does not override these local results. No new dataset is admitted/downloaded. Preserve sealed2IDSSE and16PFF exclusions and target-label restrictions. Avoid revisiting the rejected53model exporter; the current winner needs its own registered finalfit and release path.

## Sequence

1. User runs the registered slot diagnostic; assistant audits only saved aggregates/hashes.
2. Depending on controls and stress, prepare ONE justified quality change against standalone parent, or proceed directly to retained-recipe finalfit/release qualification. Every actual candidate must pass the existing medianprimary+.01/pairedmajority/macro/tests gate. No automatic repair or new run.
3. Resolve serving schema, prepare candidate-specific finalfit/export and require official validation, repeated CSVbytes, clean-environment/fresh-clone reproduction. A finalfit is not a new held-out quality result.
4. Reserve November14–15 for qualification. Freeze November16, then the existing single sealed evaluation and interpretation rule; no tuning from sealed/public scores or external submission.

Command and exact interpretation: docs/run-tcn-slot-audit.md and experiments/tcn-slot-audit-2026-11-11/protocol.md. All running remains with the user. Target accuracy unknown.
