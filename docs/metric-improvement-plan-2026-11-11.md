# Metric improvement plan after the boundary result

November 11, 2026. Planning decision, not an executable experiment protocol. This plan uses the supplied papers, prior primary-source research and saved development evidence. No training, inference, scoring, test or model import was executed to prepare it. User owns all execution. New protocol/source/input hashes must be committed before any run.

## Starting point and objective

Retained development candidate: original gap-trained motion TCN, equal identity/180degree probability averaging, uniform decoder16. Mean spellF1 .602154622 clean / .477681884 target-like corrupted; macroF1 .919369777 / .838610693. Highest historical clean spellF1 .609882 is a different unaugmented model. Production remains CatBoost16 until neural qualification; target accuracy is unknown.

Latest saved quality run is the already audited boundary trial, rejected at .583063/.464355 spellF1. Its17 saved audit-artifact hashes were rechecked unchanged; no newer quality result was identified. The failure is closed, not awaiting another coefficient. Current corrupted short-spell recall is92/732 atIoU.5; rotation improved spurious-spell behavior without solving missed short spells. The intended outcome is a reliable increase in official spellF1, not a particular number borrowed from another metric.

## What each research source contributes

|Evidence|Decision for this plan|
|---|---|
|Borghesi2023 TCN: separate dead/live and possessing-team accuracy; best configuration includes self-attention|Relevant trajectory/interaction evidence. Our model is not an exact reproduction. Report comparable accuracy diagnostics when available; keep spellF1 as selection metric. Do not transplant an86.2% accuracy target into spellF1.|
|Rudolph/Brefeld2025 trajectory masked autoencoder|Strongest distinct remaining learning hypothesis: geometric pretraining followed by compatible possession fine-tuning. Its eventmAP gains do not predict our gain.|
|2019 Fernández/Bornn/Cervone EPV PDF|Pressure, pitch control and formation-relative space are plausible representations. EPV evaluates possessions rather than discovering them. Defer added features and avoid possession-conditioned attacker/defender label leakage.|
|Guo etal2026 YOLO/DBSCAN paper|Conditional visible-ball recovery lead. Aggregate possession-percentage RMSE is not spellF1. Defer detection changes until synchronized external video and downstream labels are admitted.|
|Boundary-supervision literature and our completed trial|The fixed local objective failed, including short-spell recall. No coefficient/width/refinement rescue.|
|PathCRF, TranSPORTmer, BallRadar, CropDrop|Research mechanisms with task/supervision/identity/provenance limitations. Do not bundle a replacement model, oracle live-play or imputed-as-observed positions into the remaining comparison.|

Sources: https://doi.org/10.1016/j.eswa.2023.119780 ; https://link.springer.com/article/10.1007/s10994-024-06647-3 ; local supplied EPV PDF and literature/epv-paper-reading-2026-11-11.md ; https://www.mdpi.com/1424-8220/26/4/1252 ; literature/training-methods-reassessment-2026-11-11.md ; literature/structured-possession-refresh-2026-11-11.md ; experiments/tcn-boundary-2026-11-11/result-review.md.

## Phase 1 — Prepare one distinct learning comparison (November11–12)

Choose masked-geometry pretraining followed by IDSSE-only possession fine-tuning. Use a reconstruction head during pretraining on the existing successful encoder, then discard it for possession inference. This is a project adaptation of the learning principle, not a T-MAE reproduction. Preserve original motion inputs, downstream architecture, rotation policy and decoder. Do not combine self-attention, longer context, boundary loss or new features with pretraining.

For each fold, eligible pretraining pool is48PFF training matches plus the otherfourIDSSE development matches. Fine-tuning uses only those four IDSSE H/A/D label sequences. Exclude the held-out IDSSE match even as unlabelled data, two sealed IDSSE matches,16PFF holdouts and all target data. Start each fold independently; all-five/all53 checkpoints are ineligible initializations.

Define ONE masked reconstruction task, with targets restricted to genuinely observed training geometry. The first implementation decision is whether the retained encoder can support useful masked-ball reconstruction without target leakage or trivial copying. Synthetic masking must happen before feature computation so ball masks, derived speeds and gap ages agree. Loss must not use naturally missing/interpolated positions as truth. Pretraining window eligibility uses observation/half information, not possession labels. Any learned preprocessing is fold-local. Reconstructed coordinates are not inserted into the possession inputs as observations.

Admission requires consistent coordinate/role/observation conventions, source hashes and an implementable reconstruction objective. Original17frame effective context remains a limitation; a successful reconstruction loss alone is not admission evidence for better long-gap spells. If the adaptation requires another architecture redesign or cannot fit the schedule, close this route and qualify the winner. Do not substitute a different research track automatically.

Before the command, fix mask schedule, reconstruction target/normalization, pretraining and fine-tuning steps, seeds, optimizer transition, head initialization and total runtime budget in a committed protocol. No compatible public checkpoint has been admitted; implement locally from the stated method rather than importing unverified weights/code.

## Phase 2 — User runs the fixed control and candidate (November12–13)

Budget proposal for review at protocol preparation:20k geometric pretraining updates then20k IDSSE possession updates. Keep the full original20k supervised exposure instead of diluting it through provider mixing. The necessary control trains the same downstream model from scratch for40k supervised updates on each fold's fourIDSSE matches. Both use fixed final checkpoints; no best-epoch or seed selection. The40k control is also a candidate and is assessed first against the current winner. This is a proposed explicit total-budget amendment, not a claim that40k equals the original20k parent.

Run the pretraining candidate against the actual retained best after control review. Preserve the complete existing gate; the matched-update control diagnoses whether a gain is attributable to pretraining rather than only more optimization. Report actual time as well as steps/frame presentations: pretext updates and supervised updates need not have equal cost. Do not claim exact compute matching from equal update counts alone. Source-level cost estimates and a prospectively locked compute accounting rule are required before calling the control compute-matched.

Each arm has five held-out folds. Preserve the current exact repeated-training requirement: two fits per fold. Maximum20fit pipelines across control and pretraining arms, each40k total updates; this is one further learning route plus its necessary control, not a seed/architecture sweep. Based on the previous82.83minute200k-update boundary run,800k updates give a rough5.5hour arithmetic anchor. Budget roughly6–8hours for planning only; PFF IO and reconstruction costs are unmeasured. Do not give a runtime guarantee or launch a job during plan preparation.

Report ten clean/corrupted cells per arm: spellF1, macroF1, missed/spurious spells, short-spell recall, boundary shifts and missing-ball dead/live quality. Capture sample exposure, objective losses, input/model/output hashes and timings. Loss is training evidence, not model selection. If the fixed pretraining task fails the quality gate, close it with no mask/learning-rate/pretext rescue.

A brief optional diagnostic can report paper-compatible dead/live and live-only team accuracy from existing external cached predictions, with exact denominators and D-prediction handling defined first. It requires no retraining, remains user-run, and cannot replace official spellF1 or rank against another dataset. Do not make this report a new prerequisite for training.

## Unchanged promotion and protection rules

Keep a change only when median per-match paired mean(clean,corrupted) spellF1 delta is positive, at least3/5 paired matches improve, median paired macroF1 delta >=-.01, median target-like corrupted spellF1 delta >=+.01, and required tests/reproducibility pass. Apply to the actual current best. Report clean regressions explicitly; do not add a new undisclosed clean-score gate or select by mean alone.

Architecture/data/decoder stop histories remain intact. The proposed pretraining route and increased total budget need an explicit bounded protocol amendment before execution; this plan does not quietly reopen any stopped sweep. No target public labels/scores, hand labels or protected match data for training, selection or tuning. No external submission or publication. User runs all tests, training, inference and scoring. Assistant handles preparation, static review, saved-result audits and documentation.

## Phase 3 — Qualification and freeze

|Date|Deliverable|
|---|---|
|November11–12|Finalize feasibility, exact protocol, source review and locked run command.|
|November12–13|User runs control/candidate; audit results and retain only gate-passing changes. Close improvement work before November14.|
|November14–15|Prepare the actual winning recipe's final fit/export, serving-contract checks, official validator, byte-identical repeats, clean environment and fresh clone. Fix the old exporter mismatch; it loads a rejected model.|
|November16|Freeze configuration; once-only candidate and supplied-baseline evaluation on the two sealed matches, clean/corrupted, per match. Weak results trigger bug/transfer investigation, never tuning. Prepare the all-compatible-labelled-match variant without switching to it; wait for the user's choice.|
|November17|Delivery buffer only; no submission without instruction.|

Preserve a reproducible retained candidate until all qualification succeeds. The known target temporal-slot identity mismatch is not fixed by a higher stable-ID development score and requires the existing serving diagnostic before neural release. No architecture change may be silently labelled a bugfix. Complete history leak scan, technical report, licences/citations, rejected-experiment record, regeneration command and output/model hashes alongside qualification. Final target public-window correctness check stays narrowly allowed only under the existing documented usage limits, never for selection.

There is no evidence-backed forecast of0.8 or a competition-winning threshold. The plan spends remaining improvement time on a different learning mechanism with an informative control, while retaining the existing evaluation safeguards.
