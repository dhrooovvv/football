# pretrain comparison against control40k_reset

|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.589806|0.546890|0.932604|0.919208|
|J03WMX|targetlike|0.475829|0.457888|0.873619|0.877045|
|J03WN1|clean|0.570609|0.473529|0.898676|0.871152|
|J03WN1|targetlike|0.438186|0.373589|0.811443|0.799228|
|J03WOH|clean|0.686197|0.575610|0.937640|0.921026|
|J03WOH|targetlike|0.519716|0.489474|0.854898|0.858623|
|J03WOY|clean|0.649812|0.497668|0.923844|0.885235|
|J03WOY|targetlike|0.499497|0.405867|0.825637|0.821303|
|J03WPY|clean|0.667930|0.574462|0.936735|0.920794|
|J03WPY|targetlike|0.554521|0.489674|0.875117|0.875195|

```json
{
  "quality_eligible": false,
  "existing_gate": false,
  "primary_median_delta": -0.06459672174359005,
  "primary_deltas": {
    "J03WMX": -0.01794089041057384,
    "J03WN1": -0.06459672174359005,
    "J03WOH": -0.030242627846211345,
    "J03WOY": -0.09363082077051926,
    "J03WPY": -0.06484663490172721
  },
  "paired_spell_deltas": {
    "J03WMX": -0.030428381750091105,
    "J03WN1": -0.08083831448765005,
    "J03WOH": -0.07041502742362094,
    "J03WOY": -0.12288752384670237,
    "J03WPY": -0.07915714481460889
  },
  "paired_macro_deltas": {
    "J03WMX": -0.004984958299497189,
    "J03WN1": -0.01986951609638532,
    "J03WOH": -0.0064440458738562745,
    "J03WOY": -0.021471229311907702,
    "J03WPY": -0.007931129107907497
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
