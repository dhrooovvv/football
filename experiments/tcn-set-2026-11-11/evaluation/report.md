# Pointwise set-TCN development comparison

|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.547919|0.492647|0.921690|0.914969|
|J03WMX|targetlike|0.424853|0.358467|0.847890|0.799271|
|J03WN1|clean|0.520790|0.389668|0.888019|0.837917|
|J03WN1|targetlike|0.377544|0.266841|0.784450|0.695024|
|J03WOH|clean|0.681994|0.573353|0.931013|0.911421|
|J03WOH|targetlike|0.517194|0.408235|0.821829|0.752389|
|J03WOY|clean|0.620874|0.504528|0.917064|0.880720|
|J03WOY|targetlike|0.474725|0.366033|0.817374|0.722835|
|J03WPY|clean|0.616958|0.551085|0.927658|0.913782|
|J03WPY|targetlike|0.521379|0.406847|0.857337|0.793951|

```json
{
  "quality_eligible": false,
  "existing_gate": false,
  "primary_median_delta": -0.10895865361275181,
  "primary_deltas": {
    "J03WMX": -0.06638621487167368,
    "J03WN1": -0.11070312857862674,
    "J03WOH": -0.10895865361275181,
    "J03WOY": -0.10869232162007825,
    "J03WPY": -0.11453194943184603
  },
  "paired_spell_deltas": {
    "J03WMX": -0.06082914996224098,
    "J03WN1": -0.12091250561301237,
    "J03WOH": -0.10880012919765114,
    "J03WOY": -0.11251914715751904,
    "J03WPY": -0.09020242159202474
  },
  "paired_macro_deltas": {
    "J03WMX": -0.027670121213057675,
    "J03WN1": -0.06976413750478394,
    "J03WOH": -0.04451667166579765,
    "J03WOY": -0.06544087796463072,
    "J03WPY": -0.03863113306441002
  },
  "matches_improved": 0,
  "contract_checks_passed": true,
  "repeated_training_exact": true,
  "csv_repeatability_cases": 10,
  "clean_environment_verified": false,
  "production_changed": false,
  "sealed_opened": false,
  "pff_holdout_opened": false
}
```
