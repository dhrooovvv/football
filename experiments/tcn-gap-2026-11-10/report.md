# Gap-augmented TCN blend development screen

Quality eligibility only; production unchanged.

|Match|Setting|Parent spellF1|Augmented blend spellF1|Parent macroF1|Augmented blend macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.549938|0.544862|0.924640|0.926722|
|J03WMX|targetlike|0.355670|0.358090|0.736189|0.736411|
|J03WN1|clean|0.576847|0.561681|0.903673|0.899130|
|J03WN1|targetlike|0.381308|0.390323|0.697085|0.737596|
|J03WOH|clean|0.663358|0.644248|0.931594|0.930766|
|J03WOH|targetlike|0.422821|0.476923|0.691628|0.786000|
|J03WOY|clean|0.613856|0.606986|0.916779|0.915714|
|J03WOY|targetlike|0.397737|0.468793|0.691725|0.796490|
|J03WPY|clean|0.608772|0.604734|0.926382|0.925609|
|J03WPY|targetlike|0.427650|0.447799|0.753733|0.786928|

```json
{
  "quality_eligible": true,
  "existing_gate": true,
  "primary_median_delta": 0.020148972553111322,
  "paired_spell_deltas": {
    "J03WMX": -0.001327747763648579,
    "J03WN1": -0.0030760167237581237,
    "J03WOH": 0.017496140562104245,
    "J03WOY": 0.03209299330447857,
    "J03WPY": 0.008055385269600368
  },
  "paired_macro_deltas": {
    "J03WMX": 0.00115229675492734,
    "J03WN1": 0.017984100178029205,
    "J03WOH": 0.046772392078148206,
    "J03WOY": 0.05185030486542408,
    "J03WPY": 0.016211340897053228
  },
  "primary_deltas": {
    "J03WMX": 0.0024200825836090956,
    "J03WN1": 0.009014169430207941,
    "J03WOH": 0.05410215774716576,
    "J03WOY": 0.07105642603095258,
    "J03WPY": 0.020148972553111322
  },
  "matches_improved": 3,
  "tests_pass": true,
  "determinism_pass": true,
  "production_changed": false,
  "sealed_opened": false,
  "clean_environment_verified": false
}
```
