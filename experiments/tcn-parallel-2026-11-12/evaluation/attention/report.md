# attention: frozen-parent comparison

Independent screen only; final ordered decision requires both arms. No automatic production promotion.

|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.589806|0.594921|0.932604|0.929533|
|J03WMX|targetlike|0.475829|0.465049|0.873619|0.848780|
|J03WN1|clean|0.570609|0.584690|0.898676|0.904283|
|J03WN1|targetlike|0.438186|0.437981|0.811443|0.785121|
|J03WOH|clean|0.686197|0.686364|0.937640|0.935591|
|J03WOH|targetlike|0.519716|0.530191|0.854898|0.848184|
|J03WOY|clean|0.649812|0.650310|0.923844|0.926618|
|J03WOY|targetlike|0.499497|0.507379|0.825637|0.816442|
|J03WPY|clean|0.667930|0.642641|0.936735|0.928914|
|J03WPY|targetlike|0.554521|0.526402|0.875117|0.843511|

Per-threshold precision/recall/F1, errors and missing-ball quality are in results.json. Loss histories are training evidence, never validation scores. Reused-five-match evidence is not target accuracy; protected matches remain untouched.
