# Trial A

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

Gate v2:

```json
{
  "gate_version": "positive_median_v2",
  "quality_eligible": true,
  "existing_gate": true,
  "primary_median_delta": 0.011695374371911371,
  "paired_median_spell_delta": 0.00530387320148118,
  "paired_median_macro_delta": -0.009168188781474185,
  "matches_improved": 3,
  "primary_deltas": {
    "J03WMX": 0.035836100547125826,
    "J03WN1": 0.015542873247375466,
    "J03WOH": 0.011695374371911371,
    "J03WOY": -0.002194931761368646,
    "J03WPY": -0.024353942984080112
  },
  "paired_spell_deltas": {
    "J03WMX": 0.035955744286866764,
    "J03WN1": 0.015575944334245362,
    "J03WOH": -0.00044875096034835416,
    "J03WOY": 0.00530387320148118,
    "J03WPY": -0.009651486990173042
  },
  "paired_macro_deltas": {
    "J03WMX": 0.002814146272896667,
    "J03WN1": -0.009168188781474185,
    "J03WOH": 0.0003879577332799311,
    "J03WOY": -0.010082052408995956,
    "J03WPY": -0.012516024038501716
  },
  "contracts_passed": true,
  "repeated_training_exact": true,
  "production_changed": false,
  "sealed_opened": false,
  "target_accuracy": "unknown"
}
```

Reused development evidence only. Target accuracy unknown. No automatic production switch.
