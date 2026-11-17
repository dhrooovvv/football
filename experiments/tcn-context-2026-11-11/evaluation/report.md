# Longer-context IDSSE TCN comparison

|Match|Setting|Parent spell|Candidate spell|Parent macro|Candidate macro|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.544862|0.524969|0.926722|0.921515|
|J03WMX|targetlike|0.358090|0.413978|0.736411|0.777670|
|J03WN1|clean|0.561681|0.533504|0.899130|0.898261|
|J03WN1|targetlike|0.390323|0.369014|0.737596|0.737573|
|J03WOH|clean|0.644248|0.646064|0.930766|0.926511|
|J03WOH|targetlike|0.476923|0.462667|0.786000|0.752199|
|J03WOY|clean|0.606986|0.590349|0.915714|0.914675|
|J03WOY|targetlike|0.468793|0.425982|0.796490|0.782647|
|J03WPY|clean|0.604734|0.604638|0.925609|0.922481|
|J03WPY|targetlike|0.447799|0.471473|0.786928|0.817701|

```json
{
  "quality_eligible": false,
  "primary_median_delta": -0.01425641025641039,
  "primary_deltas": {
    "J03WMX": 0.05588830894726332,
    "J03WN1": -0.02130849613811897,
    "J03WOH": -0.01425641025641039,
    "J03WOY": -0.04281146946796782,
    "J03WPY": 0.023674612093610103
  },
  "paired_spell_deltas": {
    "J03WMX": 0.01799739296509245,
    "J03WN1": -0.02474287379182666,
    "J03WOH": -0.006220028962669377,
    "J03WOY": -0.029724356863565116,
    "J03WPY": 0.011789282721189842
  },
  "paired_macro_deltas": {
    "J03WMX": 0.018025869907852154,
    "J03WN1": -0.0004455566088279461,
    "J03WOH": -0.019028048524044716,
    "J03WOY": -0.007441420908844365,
    "J03WPY": 0.013822147639096394
  },
  "matches_improved": 2,
  "production_changed": false,
  "sealed_opened": false,
  "pff_holdout_opened": false,
  "contract_checks_passed": true,
  "repeated_training_exact": true,
  "csv_repeatability_cases": 10,
  "clean_environment_verified": false
}
```
