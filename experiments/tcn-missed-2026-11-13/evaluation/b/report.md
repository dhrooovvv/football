# Trial B

|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.633636|0.624036|0.933942|0.932480|
|J03WMX|targetlike|0.519396|0.483486|0.884808|0.861490|
|J03WN1|clean|0.588800|0.614756|0.899015|0.905193|
|J03WN1|targetlike|0.443977|0.452398|0.789555|0.796590|
|J03WOH|clean|0.695979|0.714674|0.937759|0.941679|
|J03WOH|targetlike|0.551841|0.543099|0.860079|0.821960|
|J03WOY|clean|0.661614|0.650614|0.918457|0.922153|
|J03WOY|targetlike|0.514429|0.516391|0.823786|0.845931|
|J03WPY|clean|0.646277|0.647843|0.932094|0.932253|
|J03WPY|targetlike|0.537838|0.553804|0.859285|0.863932|

Gate v2:

```json
{
  "gate_version": "positive_median_v2",
  "quality_eligible": true,
  "existing_gate": true,
  "primary_median_delta": 0.0019622504340451874,
  "paired_median_spell_delta": 0.0049762962702910585,
  "paired_median_macro_delta": 0.00240322704069329,
  "matches_improved": 3,
  "primary_deltas": {
    "J03WMX": -0.03590981257125814,
    "J03WN1": 0.008421052631578996,
    "J03WOH": -0.008742768224075492,
    "J03WOY": 0.0019622504340451874,
    "J03WPY": 0.015966509988249222
  },
  "paired_spell_deltas": {
    "J03WMX": -0.022754947514241786,
    "J03WN1": 0.017188505884461414,
    "J03WOH": 0.0049762962702910585,
    "J03WOY": -0.004518595441622253,
    "J03WPY": 0.008766525749235199
  },
  "paired_macro_deltas": {
    "J03WMX": -0.012389998218909515,
    "J03WN1": 0.006606659910034618,
    "J03WOH": -0.01709990091302216,
    "J03WOY": 0.012920703544773371,
    "J03WPY": 0.00240322704069329
  },
  "contracts_passed": true,
  "repeated_training_exact": true,
  "production_changed": false,
  "sealed_opened": false,
  "target_accuracy": "unknown"
}
```

Reused development evidence only. Target accuracy unknown. No automatic production switch.
