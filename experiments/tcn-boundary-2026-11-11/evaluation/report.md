# Boundary-supervised TCN development comparison

|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.564908|0.565501|0.929536|0.928178|
|J03WMX|targetlike|0.449571|0.454501|0.866045|0.858017|
|J03WN1|clean|0.539192|0.505212|0.887772|0.874731|
|J03WN1|targetlike|0.406341|0.378999|0.796257|0.772973|
|J03WOH|clean|0.671676|0.642336|0.932105|0.928881|
|J03WOH|targetlike|0.514451|0.482899|0.842906|0.820204|
|J03WOY|clean|0.639181|0.609451|0.920628|0.912035|
|J03WOY|targetlike|0.489575|0.494668|0.825537|0.849141|
|J03WPY|clean|0.595816|0.592818|0.926808|0.923391|
|J03WPY|targetlike|0.528471|0.510709|0.862309|0.863607|

```json
{
  "quality_eligible": false,
  "existing_gate": false,
  "primary_median_delta": -0.01776192974893054,
  "primary_deltas": {
    "J03WMX": 0.004930664397772733,
    "J03WN1": -0.02734268441585508,
    "J03WOH": -0.03155231632738548,
    "J03WOY": 0.00509311094486653,
    "J03WPY": -0.01776192974893054
  },
  "paired_spell_deltas": {
    "J03WMX": 0.0027616460369793705,
    "J03WN1": -0.030661481126807555,
    "J03WOH": -0.03044642524103125,
    "J03WOY": -0.012318298343367728,
    "J03WPY": -0.010380074886254587
  },
  "paired_macro_deltas": {
    "J03WMX": -0.0046931768916936845,
    "J03WN1": -0.018162266367337532,
    "J03WOH": -0.012962497302730025,
    "J03WOY": 0.007505727168917842,
    "J03WPY": -0.0010597034385659843
  },
  "matches_improved": 1,
  "contract_checks_passed": true,
  "repeated_training_exact": true,
  "csv_repeatability_cases": 10,
  "clean_environment_verified": false,
  "production_changed": false,
  "sealed_opened": false,
  "pff_holdout_opened": false
}
```
