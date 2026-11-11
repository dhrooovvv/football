# Longer-context TCN result audit — November 11, 2026

Decision: **reject the registered longer-context blend**. Retain the original IDSSE gap-trained TCN/CatBoost50/50/penalty16 development candidate; production remains CatBoost16. No tests, scoring, training or model inference were newly executed by this audit.

|Arm|Clean spellF1|Corrupted spellF1|Clean macroF1|Corrupted macroF1|
|---|---:|---:|---:|---:|
|Retained short-context blend|0.592502|0.428386|0.919588|0.768685|
|Long-context blend|0.579905|0.428623|0.916689|0.773558|
|Long-context standalone (descriptive)|0.570995|0.432275|0.911537|0.816372|

The blend's mean corrupted spell change is slightly positive (+.000237), but the **median per-match** corrupted change is negative(-.014256), far below required+.01. Paired median spell change-.006220,2/5pairedwins, median macro-.000446. Thus both majority/pairedspell and primaryminimum fail; mean improvement does not override the preregistered gate. Fourcleanmatches decline; two corruptedmatches improve. Per-match clean/corrupted scores and error/missing-ball records: evaluation/report.md/results.json.

The standalone arm is .570995clean/.432275corrupted: slightly better corruptedmean than retainedblend .428386, worse cleanmean than retainedblend .592502 and historical best-clean standalone .609882. It was registered as diagnostic only. Do not choose it posthoc, retune the mixture or call its small mean advantage an established promotion. A separately preregistered standalone-versus-blend comparison can be considered using fold-safe existing checkpoints; no need to infer another hourslong retrain is necessary. No such new comparison or protocol was executed here.

Independent saved-evidence audit confirms ten unique cells agree withfivefold records. Each fold fits exactly the otherfourIDSSE matches. Recomputed pairedspell/macro/primarydeltas, medians and decision agree within1e-12. ThirtyprivateCSVhashes match for first/reload/batch4,43codehashes andfivepreparedmanifesthashes agree. Recorded user logs show55passedcontracts(35+4+2+4+10) andten repeatfit/reload/batchcases. These are recorded within-environment proofs, not new tests or clean-environment reproduction. No active runner or lastfailure was found. No finalfit/export was automatic.

Recorded foldstages sum10,817.813s(180.30minutes), about3hours of active recorded stages, not a peakmemory measurement or a universal elapsed-runtime estimate. The design changes context, depth and capacity together; this failure does not establish that every longer-context architecture fails, that more context is useless, or that TCN is at a maximum. No automatic dilation/depth/optimizer/update rescue.

Close this fixedcontexttrial (one failure in this distinct track). Preserve originalthreefaileddata-expansiontrackstop. Keep originalcurrentbest/production. Contextualstandalone/blend question remains open, with selectionoptimism fromfive repeatedlyusedmatches. Targetaccuracyunknown; releasequalification remainsoutstanding. No target observations/publiclabels, sealed/PFFprotectedinputs, newdatasets/downloads or externalpublication/submission accessed or performed. Artifact fingerprints: result-artifact-hashes.json; machine audit: result-audit.json.
