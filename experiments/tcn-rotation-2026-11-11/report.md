# Fixed pitch-rotation ensemble comparison

Development eligibility only. No retraining or production switch.

|Match|Setting|Parent spellF1|Rotation ensemble spellF1|Parent macroF1|Rotation ensemble macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.547919|0.564908|0.921690|0.929536|
|J03WMX|targetlike|0.424853|0.449571|0.847890|0.866045|
|J03WN1|clean|0.520790|0.539192|0.888019|0.887772|
|J03WN1|targetlike|0.377544|0.406341|0.784450|0.796257|
|J03WOH|clean|0.681994|0.671676|0.931013|0.932105|
|J03WOH|targetlike|0.517194|0.514451|0.821829|0.842906|
|J03WOY|clean|0.620874|0.639181|0.917064|0.920628|
|J03WOY|targetlike|0.474725|0.489575|0.817374|0.825537|
|J03WPY|clean|0.616958|0.595816|0.927658|0.926808|
|J03WPY|targetlike|0.521379|0.528471|0.857337|0.862309|

```json
{
  "quality_eligible": true,
  "existing_gate": true,
  "primary_median_delta": 0.014850014850014803,
  "paired_spell_deltas": {
    "J03WMX": 0.020852962674421938,
    "J03WN1": 0.023600111744513874,
    "J03WOH": -0.006530619967068052,
    "J03WOY": 0.016578383107167527,
    "J03WPY": -0.007025219885383738
  },
  "paired_macro_deltas": {
    "J03WMX": 0.013000655268594619,
    "J03WN1": 0.005779590408577118,
    "J03WOH": 0.011083790162713658,
    "J03WOY": 0.00586390879040799,
    "J03WPY": 0.002061560953941166
  },
  "primary_deltas": {
    "J03WMX": 0.024717093765058817,
    "J03WN1": 0.028797603765511215,
    "J03WOH": -0.002743080678375809,
    "J03WOY": 0.014850014850014803,
    "J03WPY": 0.007091937902016787
  },
  "matches_improved": 3,
  "tests_pass": true,
  "determinism_pass": true,
  "training_executed": false,
  "production_changed": false,
  "sealed_opened": false,
  "pff_holdout_opened": false,
  "clean_environment_verified": false
}
```
