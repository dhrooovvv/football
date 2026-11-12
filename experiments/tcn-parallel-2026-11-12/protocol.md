# Two independent bounded experiments: attention and initialization ensemble

Registered November12,2026 after the user explicitly approved the attention experiment and asked to run the seed ensemble concurrently. This extends the previously closed quality budget for exactly these two fixed candidates and permits ONE additional representation trial despite the earlier stopped representation track. Historical failures and stop counters are preserved; this is not a reset or an open search. Other stopped tracks remain closed. All tests, imports, compilation, fitting, inference and scoring are USER-RUN. Commit source, protocol, membership and fingerprints before execution; results are committed separately. No downloads, external publication or submission.

## Frozen parent and independence

Parent is the audited original motion TCN, staged40k supervised/reset, equal original/180-degree probability average and Viterbi16: mean spellF1 .6328708454621595 clean / .49754997776865695 target-like corrupted. Use the five archived CONTROL fold checkpoints and CSVs under experiments/tcn-pretrain-2026-11-11/evaluation/control and models/tcn-pretrain/evaluation/control. Never evaluate or initialize from the all-five final artifact: it has seen every development label. Production remains unchanged, target accuracy unknown.

Both candidates train from scratch and are independently screened against this same frozen parent. Their completion order must not affect selection. Each branch makes one controlled change from the frozen best; the final cross-branch comparison selects between alternatives and is not a causal one-change ablation from attention to ensemble. Do not combine attention and seed ensembling, change inference weights or pick a favorable seed. No target trajectory inputs, public-window labels/scores, predictions, sealed matches or PFF trajectories are accessed in this experiment, even unlabelled. Historical source/configuration and membership metadata may be fingerprinted for provenance.

Development IDs/order: J03WMX,J03WN1,J03WOH,J03WOY,J03WPY. Each fold trains exactly the other four ordered IDSSE cases. Reuse unchanged compact clean/independent training-gap inputs and frozen ten clean/targetlike evaluation NPZs. Hold out the evaluation match completely. The two sealed IDSSE matches and16PFF holdouts remain untouched. No new labels, source mixture, corruption fitting, normalization or coordinate changes.

## A: one masked relational pooling replacement

Keep the original object temporal Conv3/motion channels, original temporal classifier, input521/core9, loss, windows, gap policy and decoder. Replace ONLY the H/A mean-pooling module with a shared single-head self-attention module over observed same-team object embeddings. Q,K,V are Linear8-to8 with bias, shared between teams; scaled dot products use sqrt(8), valid keys and queries are masked, then attended embeddings are averaged over observed queries. Ball pooling stays unchanged. A fully missing team produces exact finite zero. No residual/output projection, dropout, positional identity embedding, cross-team attention, new features or extra temporal context.

Construct the original pretrain-compatible TCN, including its unused reconstruction head, BEFORE constructing Q/K/V. Shared original parameters therefore receive the same initialized values/order as the winning control. The reconstruction head never enters inference or training loss. Added QKV parameters216; total9917 versus9701 compatible parent, whose class network has9635 parameters. Parameter/capacity change is part of the module replacement; this does not isolate weighting from added capacity. It is a project hypothesis inspired by Borghesi2023, not an exact paper reproduction or published spellF1 result.

Attention uses initialization seed20261106, window seed20261106 and view seed20685348. Same40k staged schedule below. No alternative attention sizes, seeds, mask policy or architecture rescue if this candidate fails. Retain the current encoder's temporal-slot dependency; attention is not an identity repair or a guarantee of target robustness.

## B: one initialization-diversity ensemble

New member is the ORIGINAL compatible motion TCN without attention. Fix model initialization seed20261107 prospectively. Window seed20261106 and view seed20685348 remain unchanged, isolating initialization diversity rather than changing every source of randomness. Same40k budget/schedule and fold memberships. There is no seed sweep or checkpoint selection.

For each held-out input, first compute the new seed member's equal original/180-degree probability average. Independently reproduce the frozen first-seed fold probabilities and archived parent CSV/metrics. Average the two normalized probability arrays at fixed weights .5/.5, then use decoder16. Do not average labels, decoded spells or logits. The existing same-seed exact-repeat fits are not diverse ensemble members. Do not ensemble the all-five final model into held-out evaluation. Standalone new-seed predictions may be used for repeatability internally, but no standalone candidate is selected post hoc.

## Shared optimization and finite compute

For each arm/fold, two independently initialized full fits must agree exactly in tensors, optimizer, Torch/window/view RNGs, losses, coverage and clean/gap view counts. Timing evidence is excluded from equality. Each fit40000 updates =20000 supervised + fresh Adam and freshly restarted window/view RNGs +20000 supervised. Do not reset learned weights or Torch RNG at the stage boundary. Adam lr.001, gradient clip1, batch8, window250, halo25, central200 crossentropy, uniform valid-window sampling, .5 independent cached-gap view probability. No early stopping, learned scaler, extra data or selected epoch. Checkpoint every1000 updates with full state; only identical registration/config may resume.

Maximum five folds x two fits x two arms =20fit pipelines /800000 total updates. The ensemble reuses the first-seed fold models; it does not retrain them. CPU intra-op1 and inter-op1, deterministic algorithms, MKLDNN disabled, fixed numerical library thread environments. No custom RAM cap. Two separate processes can overlap, nominally consuming two numerical compute threads; they are not bound to particular physical cores. Tests run in separate children with inherited thread settings.

Read-only geometry may be shared; arm outputs, checkpoints, test logs and operation locks are isolated. Do not rebuild prepared inputs or launch an additional dataset/model job concurrently. Record each arm's observed timings; concurrency, memory pressure, efficiency/performance-core scheduling and thermal throttling prevent a twofold-speed guarantee. The Mac reports18GiB RAM and11cores (5performance/6efficiency). This is hardware inventory, not an execution capacity guarantee.

Keep shared source and inputs immutable while either arm runs. Any source correction after a failure requires explicit registration/provenance handling for both arms; never re-sign old results or mutate a running branch's sources silently. Preserve completed/partial/failure records for review.

The old repeated40k pair took about33minutes; five such pairs suggests roughly3hours for the ensemble training as an unmeasured planning estimate. Attention is NOT covered by this estimate: full64x64 attention per team increases intermediate memory and computation substantially despite few added weights. Its duration and peakRAM are unmeasured and may be much greater. No models/tests have been run to benchmark it by the assistant.

## Evaluation evidence and unchanged gate

Reconstruct ten archived parent CSV bytes and metrics with the actual CONTROL checkpoints, exact training identity and membership guard, before any new full fit in each arm. Repeat parent checks during candidate evaluation. All ten cases per arm require original/rotation reload probability equality and identical first/reload/batch4 CSV bytes. The original reference scorer remains unchanged. Organizer reference files are hash-verified separately; they are not required to be committed or published. Project source, protocol, membership and input lock must match committed bytes.

Report every match and condition: official mean spellF1, macroF1, precision/recall/F1 at IoU .3/.4/.5/.6/.7, short-spell recall, missed/spurious spells, boundary-shift diagnostics and missing-ball dead/live quality. Record input/model/CSV hashes, sample coverage, loss and elapsed time. Training loss is not validation quality; synthetic checks are not competition evidence. Five repeatedly reused matches/overlapping folds do not justify independent population p-values or a target score forecast.

Each independent screen applies the complete existing gate versus the frozen parent: median per-match mean(clean,corrupted) spellF1 delta >0; at least3/5 paired wins; median paired macroF1 delta >=-.01; median target-like corrupted spellF1 delta >=+.01; required tests and determinism pass. A clean or corrupted mean alone cannot override the gate.

## Predeclared final decision after both complete

User-run finalize performs no new fits and requires complete, hash-consistent records for both arms. Apply the gate to ATTENTION against the frozen parent first. If it passes, attention is the provisional retained best; otherwise retain parent. Then apply the ENSEMBLE gate against that actual retained best, including the +.01 median corrupted improvement. Retain ensemble only if it passes that comparison. This ordering is fixed before results, so parallel runtime order cannot select the winner. Report ensemble-versus-parent screening even if it fails against retained attention. No post-hoc mixture of both candidates or choosing an alternative based on favorable means.

Stop after these two candidates and finalize/report. If either fails, close that fixed route without seed/weight/capacity/loss/decoder rescue. Existing stop histories remain recorded. A passing development gate is eligibility, not a production switch. Any new winning recipe still requires its own final-fit/export integration, official validation and clean-environment/fresh-clone byte reproduction; do not overwrite the already qualified private candidate.

## Schedule and outputs

Starts, resumption and fold progression require date before November16 localAsia/Kolkata; trainer rechecks every1000updates. Preserve partial evidence at freeze. No research starts on/after November16, no action afterNovember17. User's willingness to spend runtime does not change those dates. Sealed evaluation remains once at freeze, under the prewritten bug/transfer-investigation-not-tuning rule. No public-label selection or external submission.

User commands and output paths are specified in docs/run-tcn-parallel.md. Both arms may start in separate terminals; leave execution to the user. Finalize only after both finish. Append important outcomes and failures to ball.md and update state/findings without rewriting history. Source review and all supplied contracts are unexecuted runtime evidence until the user runs them.
