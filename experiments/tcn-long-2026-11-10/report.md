# Scratch trajectory TCN development screen

Quality eligibility only; production unchanged.

|Match|Setting|Parent spellF1|TCN spellF1|Parent macroF1|TCN macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.501360|0.582791|0.907574|0.920598|
|J03WMX|targetlike|0.323426|0.348694|0.692742|0.691098|
|J03WN1|clean|0.484682|0.576852|0.875014|0.897624|
|J03WN1|targetlike|0.313253|0.363504|0.680025|0.680137|
|J03WOH|clean|0.568452|0.659085|0.903698|0.932628|
|J03WOH|targetlike|0.343671|0.407104|0.646450|0.681695|
|J03WOY|clean|0.516129|0.635323|0.885072|0.917399|
|J03WOY|targetlike|0.312291|0.370927|0.663388|0.654484|
|J03WPY|clean|0.517647|0.595362|0.904135|0.920015|
|J03WPY|targetlike|0.324741|0.443028|0.714401|0.728697|

```json
{
  "quality_eligible": true,
  "existing_gate": true,
  "primary_median_delta": 0.05863681550244326,
  "paired_spell_deltas": {
    "J03WMX": 0.053349444170044114,
    "J03WN1": 0.0712100242959357,
    "J03WOH": 0.07703301211971614,
    "J03WOY": 0.08891528017273753,
    "J03WPY": 0.09800080842460152
  },
  "paired_macro_deltas": {
    "J03WMX": 0.005689628062934049,
    "J03WN1": 0.011361073474585481,
    "J03WOH": 0.03208734114869449,
    "J03WOY": 0.011711277092699035,
    "J03WPY": 0.015088045831543995
  },
  "primary_deltas": {
    "J03WMX": 0.025267894003123292,
    "J03WN1": 0.05025063758684378,
    "J03WOH": 0.06343293906066266,
    "J03WOY": 0.05863681550244326,
    "J03WPY": 0.11828714770547455
  },
  "matches_improved": 5,
  "tests_pass": true,
  "determinism_pass": true,
  "production_changed": false,
  "sealed_opened": false,
  "clean_environment_verified": false
}
```
