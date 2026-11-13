# Trial A saved-result review — November 13, 2026

Decision: accept short_mix provisionally under the registered positive-median v2 gate; production unchanged. Trial B retains this sampler and compares against A, changing only the preregistered segment-soft-IoU objective. reviewed-a.json binds A completion and result hashes; it must be committed before B.

Root verifies295registered entries,166committed source/input files,369unique byte hashes including20checkpoints and all saved prediction CSVs without reading rows or loading model state. Saved logs report91passingcontracts; fit proofs record exact repeats and inference reload/batch CSV equality. Ten fits-by-seed/fold proofs represent20full40kfits. No new test/import/compile/inference/scorer/training executed by reviewer. Independent aggregate arithmetic review: result-review-a-scientist.md.

Means: clean spell .633872006→.645261041, corrupted .506191099→.513496193. Clean macro .925171920→.924253358; corrupted .854009568→.843502465. Primary corrupted median gain+.011695374; paired spell median+.005303873;3/5pairedwins; paired macro median-.009168189 passes >=-.01 by only.000831811. The corrupted mean macro decline-.010507103 is a separate measure and does not override the prespecified paired-median guard. Corrupted spell regresses on WOY and WPY; paired clean/corrupt spell regresses on WOH and WPY. No unanimity/independent-generalization claim.

|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.597561|0.633636|0.934497|0.933942|
|J03WMX|targetlike|0.483560|0.519396|0.878624|0.884808|
|J03WN1|clean|0.573191|0.588800|0.898726|0.899015|
|J03WN1|targetlike|0.428434|0.443977|0.808180|0.789555|
|J03WOH|clean|0.708571|0.695979|0.937801|0.937759|
|J03WOH|targetlike|0.540146|0.551841|0.859262|0.860079|
|J03WOY|clean|0.648811|0.661614|0.922626|0.918457|
|J03WOY|targetlike|0.516624|0.514429|0.839782|0.823786|
|J03WPY|clean|0.641226|0.646277|0.932210|0.932094|
|J03WPY|targetlike|0.562192|0.537838|0.884201|0.859285|

Error counts at IoU.5, not complete official five-threshold spellF1: clean missed1046→972, spurious346→463, short recalled151→189 of732, dead/livewrong1719→2386. Corrupted missed1308→1268, spurious564→647, short recalled100→124 of732, dead/livewrong42828→50889. Short recalled counts are recovered from saved per-match recall ratios. This supports targeted short-possession recovery, with overprediction/dead-live costs; not a universal fix or causal attribution beyond this sampler comparison.

Every seed's fold proofs record about half targeted windows and stage-reset equality; eligible/excluded short-spell audits and realized complete-short exposure are saved per fit. No auxiliary loss was used in A. Sum recorded seed/fold durations20184.336seconds (~5h36m24s), not total concurrent wall time or peak RAM. Historical failed experiments/stopped tracks and freezeNov16 unchanged. Target accuracy unknown. No sealed/target/publiclabel access, download, publication or push. Trial B is the final already-authorized fixed trial; no extra variants.
