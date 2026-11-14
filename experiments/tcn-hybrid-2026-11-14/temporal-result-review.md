# Temporal hybrid result review — November 14, 2026

Reject this fixed candidate under the registered positive-median gate. The mean corrupted score rises slightly, but its median paired-match corrupted change is negative.

|Setting|Parent spellF1|Temporal spellF1|Parent macroF1|Temporal macroF1|
|---|---:|---:|---:|---:|
|Clean|0.650385|0.654253|0.926752|0.925926|
|Target-like corrupted|0.509836|0.510676|0.837981|0.858140|

Median corrupted delta −0.000727617842, paired spell median +0.003682057208, 3/5 paired wins and paired macro median +0.010330971276. Only the primary median condition fails. Corrupted WMX/WOY/WPY regress, WN1/WOH improve. Do not change the gate after observing this result.

At IoU0.5, clean missed spells decline953→822 while spurious spells increase451→677. Corrupted missed spells decline1278→1157, but spurious spells increase658→997. Long-gap exposed misses decline621→564. Corrupted dead/live wrong frames decline54752→35830. These changes show some recovery and better dead/live classification accompanied by over-segmentation. The counts are associations across the same reused development matches and are not additive spellF1 gains. Higher macroF1 alone does not qualify the candidate.

Saved evidence records37passing contracts,20complete repeated fits and reload/batch CSV proofs. Root verifies102registeredentries/169unique referenced hashes, ten fit proofs/twenty checkpoints and thirty predictionCSV hashes. Gate arithmetic was independently recomputed using stdlib aggregate arithmetic. No project imports, tests, model/array/CSV-row loading, inference or scoring by the reviewer.

All ten official clean/corrupted per-match results and richer diagnostic tables are retained in evaluation/temporal/results.json, report.md and paired-corruption.json. The exact reject decision is reviewed-temporal.json. Trial B remains the graph stage parent. Next execute only the graph preflight, measure feasibility, then decide whether its complete fixed comparison fits before the November16 freeze. No temporal coefficient, dilation or architecture rescue follows. Target accuracy is unknown.
