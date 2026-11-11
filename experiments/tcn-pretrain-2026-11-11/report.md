# Fixed pretraining route: final development decision

Retained recipe: control40k_reset. Production unchanged; target accuracy unknown.

|Arm|Setting|Mean spellF1|Mean macroF1|
|---|---|---:|---:|
|rotation20k|clean|0.602155|0.919370|
|rotation20k|targetlike|0.477682|0.838611|
|control40k_reset|clean|0.632871|0.925900|
|control40k_reset|targetlike|0.497550|0.848143|
|pretrain20k_finetune20k|clean|0.533632|0.903483|
|pretrain20k_finetune20k|targetlike|0.443298|0.846279|

Control gate and actual-parent pretraining gate are the sequential decisions. diagnostic-contrasts.json preserves both comparisons without selecting an alternate parent after results. Full per-match metrics/errors/missing-ball quality are in each arm evaluation folder. Costs are update-matched, not exact compute-matched.
