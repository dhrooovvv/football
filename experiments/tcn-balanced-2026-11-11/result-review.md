# Balanced-provider TCN result audit — November 11, 2026

**Reject. Stop the data-expansion track after its third consecutive failure.** Retain the previous IDSSE gap-trained50/50TCN/CatBoost development candidate. Production remains nine-core CatBoost16. No tests, training or inference were launched during this audit.

|Arm|Clean spellF1|Corrupted spellF1|Clean macroF1|Corrupted macroF1|
|---|---:|---:|---:|---:|
|Retained best blend|0.592502|0.428386|0.919588|0.768685|
|Balanced-provider blend|0.512005|0.370875|0.897192|0.740760|
|Balanced standalone TCN (descriptive)|0.486628|0.397102|0.883794|0.811118|

The paired gate has0/5wins, medianpairedspell−.065493, medianpairedmacro−.023643 (below−.01), and primarymediancorruptedspell−.065475 (required+.01). All clean spell scores decline, four of five corrupted spell scores decline. Per-match scores, taxonomy and missing-ball quality remain in evaluation/report.md/results.json. The inherited evaluator report heading says Expanded-data; this directory is specifically the fixed balanced-provider trial.

Independently recalculated all paired/primary deltas, medians and decision within1e-12. Five fold memberships exclude exactly their heldoutIDSSEmatch and retain48PFF. Ten aggregate cells equal fold rows. Thirty private CSV hashes verify initial/reload/batch4 equality;42registeredcode and53preparedmanifesthashes agree. The saved user log records53passedtests (35+4+2+4+8), and ten cases record exact repeated fitting. These are recorded user-run successes, not rerun tests or clean-environment reproduction. No active runner or saved lastfailure was found. Final fitting was not automatically run after rejection.

Every fold sampled79,546IDSSE and80,454PFFwindows,50.28375%PFF. Identical shares acrossfolds are expected from the shared provider seed/draw budget; window selection and heldoutmembership differ. Balancing was actually applied. Compared descriptively to uniformexpansion (.520562/.376959), meanblendspell is again lower (.512005/.370875). Thus the fixed50/50allocation did not rescue the failure. This weakens the explanation that93%PFFdominance alone explains the loss; provider labels/noise, lower IDSSEexposure and fixedbudget remain confounded. It does not establish a TCNceiling or rule out every transfer approach. Do not select the standalone diagnostic arm or fit another mixture after seeing scores.

Recorded fold stages sum5,466.209s (91.10min); this is not measured complete elapsedwalltime or peakRAM. Source arrays were not loaded by the audit; prepared manifests and prediction-file bytes were hashed, without exposing rows. No target labels/observations or protected matches accessed. Targetaccuracyunknown, releaseverificationpending. Retain failed artifacts. No externalpublication/submission.

Preserve all three failures: unweightedCatBoostexpansion, unweightedTCNexpansion, fixedbalancedTCNexpansion. Stop data expansion, ratio searches and automatic transfer/adaptation rescue. The separate planned next hypothesis is temporalcontext on the retained candidate with its original IDSSEtraining policy; it requires its own protocol/sourcecommit before userexecution and does not reopen data expansion. No new experiment started here. Full researchplan docs/improvement-plan-2026-11-11.md.
