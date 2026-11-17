# Staged supervised training wins; masked-ball pretraining rejected

Audited November12,2026. Retain the40k supervised TCN with the registered halfway optimizer/sampler reset, equal identity/180degree probability averaging and decoder16 as the new best eligible development candidate. Production remains CatBoost16 until qualification. Target accuracy is unknown.

|Mean metric|Prior20k rotation|40k supervised/reset|20k pretrain+20k fine-tune|
|---|---:|---:|---:|
|Clean spellF1|.602154622|**.632870845**|.533631828|
|Target-like spellF1|.477681884|**.497549978**|.443298439|
|Clean macroF1|.919369777|**.925899545**|.903482932|
|Target-like macroF1|.838610693|**.848142823**|.846279086|

## Independent gate decisions

Control versus oldrotation: PASS. Median corrupted spell gain+.026049300(required+.01); median paired clean/corrupted spell gain+.025578341;5/5paired match wins; median paired macro gain+.008763574. All five matches improve spellF1 in both conditions and macroF1 in both conditions. This also exceeds the historical clean-only .609882 result, though selection still follows the full robust gate.

Pretraining versus the newly retainedcontrol: FAIL. Median corrupted spell delta−.064596722; median paired spell−.079157145;0/5wins. Median macro−.007931129 meets the macro tolerance alone. Pretraining spellF1 declines on all five matches in both conditions. Reject this fixed reconstruction route and retain the supervised/reset control. Do not select pretraining by a favorable auxiliary diagnostic or start another mask/ratio/learning-rate rescue.

The registered control combines additional supervised updates and a halfway reset. This experiment does not isolate how much gain comes from more updates versus the reset schedule. The pretraining comparison matches update counts and schedule, not exact computation. It rejects this compact masked-ball pretext/data schedule; it does not prove that all self-supervised pretraining or additional data is useless.

## Errors and remaining weakness

Compared with oldrotation, the retained control recalls150/732shortspells clean(20.49%) versus125/732(17.08%), and104/732corrupted(14.21%) versus92/732(12.57%), atIoU.5. Missed spells fall1119→1044 clean and1379→1312 corrupted. Spurious spells fall386→373 clean but rise616→645 corrupted. The gain is not universal across every diagnostic. Dead/live wrong frames fall2362→1866 clean and51589→46568 corrupted. These diagnostics differ from official averaged-over-IoU spellF1 and are dependent within matches.

Pretraining short recall is81/732clean and63/732corrupted; its corrupted dead/live errors fall to38112 while spellF1 worsens. Better one-frame/error-category diagnostics cannot substitute for the whole-spell gate. See per-arm per-match reports and JSON for all ten cells, boundary shifts and missing-ball quality.

## Integrity and execution evidence

Root independently recomputed all20match/condition cells, fold/aggregate agreement, exact fold membership, stage budgets/coverage, parent metrics and gate deltas from saved aggregate JSON. Verified249registeredfingerprints(145code,51reference/input,53compactmanifests),371compactmember hashes,20checkpoints,60candidate CSV hashes and20parent CSV references. Original committed protocol/source match registration. Held-out IDSSE matches remain excluded even from geometry pretraining, PFF16/sealed/target excluded. Geometry loader reads no possession labels.

User logs record54contracts passing; saved20cases report exact repeated state/loss/coverage plus both-view reload probabilities and initial/reload/batch4 CSV equality. Checkpoint bytes can differ because timings are stored; exact repeat checks concern model tensors/loss/sampling evidence, not elapsed times. No last-failure record. This review did not run tests, model/data imports, compilation, inference, scorer or training, and did not load dataset arrays or model states. Byte hashing and saved aggregate arithmetic only.

Recorded fold-stage sums: control10039.032310seconds, pretrain10683.076111seconds, combined20722.108421seconds(5h45m22s). These are summed recorded stages, not independently measured total command walltime or peakRAM. Stage timings exclude checkpoint serialization/eligibility preparation. Actual per-arm cost differs despite matched updates.

## Next decision

Close the finite improvement comparison as preregistered; no automatic extra architecture/80k/pretraining rescue. Prepare the actual winning40k-reset recipe's finalfit/export and serving validation. The old expanded53CatBoost-blend exporter is incompatible. Preserve Nov14–15qualification and Nov16freeze/once-only sealed evaluation. Weak sealed results trigger bug/transfer investigation, never tuning. Target slot-identity transfer risk remains unresolved and must be addressed in qualification; no development gain proves target accuracy.

Working targets discussed November12: .55target-like development spellF1 next milestone, .60stretch. They are engineering goals without a performance forecast, not a new gate or justification for further unregistered searches. Current .49755 has not met .55. No published winning cutoff is known. Production/sealed/public-label rules unchanged. No external push or submission.
