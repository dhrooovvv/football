# control comparison against rotation20k

|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.564908|0.589806|0.929536|0.932604|
|J03WMX|targetlike|0.449571|0.475829|0.866045|0.873619|
|J03WN1|clean|0.539192|0.570609|0.887772|0.898676|
|J03WN1|targetlike|0.406341|0.438186|0.796257|0.811443|
|J03WOH|clean|0.671676|0.686197|0.932105|0.937640|
|J03WOH|targetlike|0.514451|0.519716|0.842906|0.854898|
|J03WOY|clean|0.639181|0.649812|0.920628|0.923844|
|J03WOY|targetlike|0.489575|0.499497|0.825537|0.825637|
|J03WPY|clean|0.595816|0.667930|0.926808|0.936735|
|J03WPY|targetlike|0.528471|0.554521|0.862309|0.875117|

```json
{
  "quality_eligible": true,
  "existing_gate": true,
  "primary_median_delta": 0.026049299698361117,
  "primary_deltas": {
    "J03WMX": 0.026258831739016553,
    "J03WN1": 0.03184469410326568,
    "J03WOH": 0.005265445004714486,
    "J03WOY": 0.009922197861896409,
    "J03WPY": 0.026049299698361117
  },
  "paired_spell_deltas": {
    "J03WMX": 0.025578340760806118,
    "J03WN1": 0.031630807024900176,
    "J03WOH": 0.009893163762635715,
    "J03WOY": 0.010276962710736859,
    "J03WPY": 0.04908151737908928
  },
  "paired_macro_deltas": {
    "J03WMX": 0.0053209420446492794,
    "J03WN1": 0.013045373676700667,
    "J03WOH": 0.008763574194285306,
    "J03WOY": 0.0016579119241857398,
    "J03WPY": 0.011366945124469785
  },
  "matches_improved": 5,
  "contract_checks_passed": true,
  "repeated_training_exact": true,
  "csv_repeatability_cases": 10,
  "clean_environment_verified": false,
  "production_changed": false,
  "sealed_opened": false,
  "pff_holdout_opened": false
}
```
