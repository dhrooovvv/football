# Frozen temporal recovery audit

Exploratory development evidence only. All parent/temporal CSV hashes and official scores reproduced before interpretation. No candidate tested or training performed.

|Match|Setting|Parent spellF1|Temporal spellF1|Recovered|Introduced spurious|Parent-margin AUC|Temporal-margin AUC|Agreement AUC|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|J03WMX|clean|0.624036|0.640748|55|64|0.6403|0.5835|0.6081|
|J03WMX|targetlike|0.483486|0.482759|55|126|0.6297|0.6807|0.6654|
|J03WN1|clean|0.614756|0.641158|55|65|0.5891|0.6327|0.6413|
|J03WN1|targetlike|0.452398|0.476171|48|127|0.6649|0.7054|0.6703|
|J03WOH|clean|0.714674|0.705646|36|54|0.6476|0.6836|0.6618|
|J03WOH|targetlike|0.543099|0.559490|46|94|0.7229|0.6989|0.6326|
|J03WOY|clean|0.650614|0.631368|42|85|0.5566|0.6314|0.5909|
|J03WOY|targetlike|0.516391|0.498643|40|123|0.6813|0.7404|0.6957|
|J03WPY|clean|0.647843|0.652346|31|53|0.6713|0.5886|0.5350|
|J03WPY|targetlike|0.553804|0.536318|23|100|0.6200|0.6665|0.6226|

## Graph training-only trend

|Fold|Seed|Stage|First1000 loss|Last1000 loss|Last5000 minus preceding5000|
|---|---:|---:|---:|---:|---:|
|J03WMX|20261106|1|0.310253|0.272219|-0.014071|
|J03WMX|20261106|2|0.267877|0.227564|-0.011175|
|J03WMX|20261107|1|0.310186|0.269295|-0.014305|
|J03WMX|20261107|2|0.263421|0.226561|-0.008784|
|J03WN1|20261106|1|0.315485|0.279397|-0.012884|
|J03WN1|20261106|2|0.281250|0.231001|-0.013265|
|J03WN1|20261107|1|0.315613|0.283186|-0.012520|
|J03WN1|20261107|2|0.283799|0.235781|-0.012765|
|J03WOH|20261106|1|0.332615|0.293597|-0.014314|
|J03WOH|20261106|2|0.289952|0.236954|-0.010352|
|J03WOH|20261107|1|0.332656|0.297867|-0.011038|
|J03WOH|20261107|2|0.293960|0.247679|-0.009852|
|J03WOY|20261106|1|0.305697|0.272145|-0.011525|
|J03WOY|20261106|2|0.269900|0.232150|-0.008241|
|J03WOY|20261107|1|0.305851|0.269676|-0.011575|
|J03WOY|20261107|2|0.266557|0.228863|-0.008404|
|J03WPY|20261106|1|0.319356|0.293502|-0.012944|
|J03WPY|20261106|2|0.288002|0.246656|-0.010442|
|J03WPY|20261107|1|0.319238|0.285429|-0.015411|
|J03WPY|20261107|2|0.280144|0.239583|-0.012113|

AUC and spell counts are not recoverable spellF1 gains. Inspect all match denominators, contrary cases and clean/corrupted consistency before proposing a rule. Training loss is not a held-out learning curve and cannot establish a benefit from longer graph training. No automatic thresholds, model change or third trial. Stop for review before one separate prospectively registered correction rule. Selected Trial B and production unchanged. Sealed matches untouched; target accuracy unknown.
