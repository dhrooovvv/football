# Standalone gap-trained TCN comparison

Development eligibility only. No retraining or production switch.

|Match|Setting|Parent spellF1|Standalone spellF1|Parent macroF1|Standalone macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.544862|0.547919|0.926722|0.921690|
|J03WMX|targetlike|0.358090|0.424853|0.736411|0.847890|
|J03WN1|clean|0.561681|0.520790|0.899130|0.888019|
|J03WN1|targetlike|0.390323|0.377544|0.737596|0.784450|
|J03WOH|clean|0.644248|0.681994|0.930766|0.931013|
|J03WOH|targetlike|0.476923|0.517194|0.786000|0.821829|
|J03WOY|clean|0.606986|0.620874|0.915714|0.917064|
|J03WOY|targetlike|0.468793|0.474725|0.796490|0.817374|
|J03WPY|clean|0.604734|0.616958|0.925609|0.927658|
|J03WPY|targetlike|0.447799|0.521379|0.786928|0.857337|

```json
{
  "quality_eligible": true,
  "existing_gate": true,
  "primary_median_delta": 0.040270870807321946,
  "paired_spell_deltas": {
    "J03WMX": 0.03491013059682724,
    "J03WN1": -0.02683501471617178,
    "J03WOH": 0.03900877151524873,
    "J03WOY": 0.009909974412480094,
    "J03WPY": 0.042902558825093084
  },
  "paired_macro_deltas": {
    "J03WMX": 0.05322314666428407,
    "J03WN1": 0.017871598768056884,
    "J03WOH": 0.01803840413115232,
    "J03WOY": 0.011116245167598904,
    "J03WPY": 0.03622852787190145
  },
  "primary_deltas": {
    "J03WMX": 0.06676327270578797,
    "J03WN1": -0.012778720996038384,
    "J03WOH": 0.040270870807321946,
    "J03WOY": 0.005931932145524399,
    "J03WPY": 0.07358056820646275
  },
  "matches_improved": 4,
  "tests_pass": true,
  "determinism_pass": true,
  "training_executed": false,
  "production_changed": false,
  "sealed_opened": false,
  "pff_holdout_opened": false,
  "clean_environment_verified": false
}
```
