# Graph-only continuation to 50k cumulative updates — November 15, 2026

## User authorization and hypothesis

User explicitly chooses higher graph training over the proposed confidence-filter experiment and requests a direct full-run command. Reopen exactly one fixed graph-budget trial; previous40k graph rejection remains preserved. This is a TCN+GNN–TCN hybrid: selected Trial-B TCN ensemble is frozen, only the graph correction branch trains. Trial B is the retained-parent evaluation comparator, not an adversarial target. No additional temporal refiner, confidence filter or TCN retraining.

Hypothesis: the graph branch's declining training objective indicates possible remaining fitting capacity; additional updates might improve held-out possession recovery. This is unproven: no held-out learning curve establishes benefit. No claim that declining training loss means better spellF1. One fixed endpoint, no budget search or intermediate-score selection.

## Single changed factor

Increase graph branch training from40000to50000 cumulative updates per fit (25% increase). Resume each matching archived40k first/repeat checkpoint, preserving its exact model weights, Adam state, Torch RNG and window/view/sampler RNGs and all recorded losses/exposures. Add10000updates with no new optimizer/sampler reset at40k; original20k/reset/20k becomes20k/reset/30k. Learning rate.001, Adam, batch8, gradientclip1, short_mix sampler, CE+0.1segmentsoftIoU, corruption views and graph architecture unchanged. Graph has9835parameters. Do not warm start from the final-five model or from another fold/seed. Preserve archived files; isolated new outputs. Long trainer is a separately versioned copy of the frozen optimizer loop with only budget and warm-start/resume validation changes.

Retain five original LOMO folds and seeds20261106/20261107, two exact repeats each:20continuations,200000additional updates. All held-out matches excluded from each fit; no target assets/labels or sealed J03WQQ/J03WR9. Parent predictions on each training fold are in-sample, a pre-existing stacking distribution shift; no change to that convention. Reuse frozen graph-stage parent caches, original prepared arrays, observed masks, targetlike eval corruption and independent training/evaluation mask seeds. No new datasets, downloads, labels, features, augmentation, architecture or decoder settings.

Inference is exactly the original hybrid prediction path: frozen Trial-B parent ensemble probabilities plus graph correction, existing orientation/seed averaging, penalty16 decoder and deterministic CSV. Halves stay isolated, unknown labels excluded from supervision. No target accuracy measurement.

## Comparator, diagnostics and gate

Primary comparator is selected Trial B (mean development spellF1.650384708clean/.509835640corrupted). Show the failed40k graph's archived per-match metrics alongside50k only as budget-effect reference; do not promote relative to the failed model alone. Original official scorer unchanged; no scored intermediate endpoints.

Same promotion rule: median corrupted spellF1 delta>0; positive median paired clean/corrupted spellF1 delta; at least3/5paired-match wins; median paired macroF1 delta>=−.01; tests/repeat/reload/batchCSV correctness pass. Report means/medians and individual regressions. Per match, clean/corrupted official per-IoU scores, missed/spurious spells, short-spell recall, boundary shifts, long-gap strata and missing/observed dead/live diagnostics from unchanged diagnostic. Counts do not replace the gate. Failure closes this extension; no automatic60k/80k, learning-rate adjustment or confidence-gating rescue. Target/sealed outcomes never select anything.

## Direct user-run execution and verification

One command runs automatic source/environment/storage/deadline admission, prior37hybrid correctness tests plus six new continuation tests, then four fold/seed worker processes, each with one numerical thread. No separate manual preflight or benchmark: same architecture already has a four-job exact-output benchmark. New tests cover fixed-budget identity, warm-state/Adam/RNG preservation, repeated and interrupted/resumed synthetic graph continuation, source immutability, no extra40k reset, fold exclusion, incomplete-source refusal and forecast reserve. All tests/training/inference/scoring remain user-run; assistant does not import, compile or execute numerical project code.

Source/protocol/membership/environment/input fingerprints committed before execution. Verify original repeated-fit identities/checkpoint hashes and OOF caches before adoption. Preserve original40k source lineage in each new proof. Full continuations must repeat exactly in model/optimizer/RNG/loss/exposure, then require exact reloaded ensemble/member probabilities and identical CSV bytes for batch1/reloaded batch1/batch4. Frozen Trial-B CSV hashes and official metrics must reproduce for all ten cells before candidate scoring. Archived40k graph model/proofs and rejected review unchanged.

Resumable1000-update checkpoints; completed pair proofs and per-match evaluation hashes skip completed units. Failures preserve logs/checkpoints. At most four jobs,20continued fits. No old asset overwritten/deleted. Isolate under models/graph-long-2026-11-15 and experiments/graph-long-2026-11-15. Reserve512MiB for combined new artifacts beyond old accounting; enforce existing2GiB total and12GiB free floor. The quota is pre/post-write protection, not OS-enforced. Do not persist probability arrays. Stop if guards fail, no automatic deletion.

## Freeze admission and final artifact reservation

Freeze remains start November16 Asia/Kolkata. New research guards stop updates/diagnosis at that deadline; partial work never becomes candidate. At run/resume admission project remaining paired40k→50k tasks in four-job waves, using the larger of recorded worst full-fit update rate and four-job benchmark rate. Add one four-job wave for four possible final50k fresh fits, multiply development+final time by1.5 and add1800seconds for checks/evaluation/preparation. This is a forecast, not a runtime guarantee. Recheck date during updates and evaluation.

Observed previous task-rate maximum.161084s/update: extra development nominal2.68h; conservative full forecast including possible final fits7.88h before using the slightly slower benchmark rate.60k requires12.58h and80k21.98h by the same formula, exceeding the conservative remaining budget at registration time; choose50k by feasibility, not by quality. Actual runtime/thermal effects unknown.

The direct command stops after development comparison and writes no final fitted hybrid or target CSV. If it qualifies, review and authorize final fitting/qualification separately, only while its reserved work can finish before freeze. Final graph recipe would train from scratch on exactly five allowed matches with two seeds and two exact repeats,20k/reset/30k, while retaining frozen final-B parent; it must not reuse LOMO graph weights as final weights. A final50k release/export path still needs its own implementation/source lock and user execution. Until that qualification is complete, selected B and its existing target CSV stay unchanged. No automatic production switch, external submission or publication; no project actions after November17.
