# Graph continuation: frozen TCN + 50k graph

|Match|Setting|TCN spellF1|Graph40k|Graph50k|TCN macroF1|Graph50k macroF1|
|---|---|---:|---:|---:|---:|---:|
|J03WMX|clean|0.624036|0.615314|0.600000|0.932480|0.927787|
|J03WMX|targetlike|0.483486|0.485517|0.482286|0.861490|0.853684|
|J03WN1|clean|0.614756|0.617117|0.643537|0.905193|0.915930|
|J03WN1|targetlike|0.452398|0.463326|0.491917|0.796590|0.814290|
|J03WOH|clean|0.714674|0.695082|0.696721|0.941679|0.937827|
|J03WOH|targetlike|0.543099|0.557762|0.565498|0.821960|0.853001|
|J03WOY|clean|0.650614|0.650481|0.651401|0.922153|0.918541|
|J03WOY|targetlike|0.516391|0.501781|0.519042|0.845931|0.847441|
|J03WPY|clean|0.647843|0.658824|0.652713|0.932253|0.928854|
|J03WPY|targetlike|0.553804|0.533687|0.532258|0.863932|0.858944|

Gate against retained Trial B:

{
  "gate_version": "positive_median_v2",
  "quality_eligible": true,
  "existing_gate": true,
  "primary_median_delta": 0.0026502545301886338,
  "paired_median_spell_delta": 0.0017183673660080556,
  "paired_median_macro_delta": -0.001050865410236801,
  "matches_improved": 3,
  "primary_deltas": {
    "J03WMX": -0.0012005242463957178,
    "J03WN1": 0.03951919830368833,
    "J03WOH": 0.022399304663887953,
    "J03WOY": 0.0026502545301886338,
    "J03WPY": -0.021546283309958003
  },
  "paired_spell_deltas": {
    "J03WMX": -0.01261840271276704,
    "J03WN1": 0.03415032706616539,
    "J03WOH": 0.0022233515479098687,
    "J03WOY": 0.0017183673660080556,
    "J03WPY": -0.008338121135143206
  },
  "paired_macro_deltas": {
    "J03WMX": -0.006249632347814615,
    "J03WN1": 0.014218382105753213,
    "J03WOH": 0.01359504044000226,
    "J03WOY": -0.001050865410236801,
    "J03WPY": -0.004193377771479767
  },
  "contracts_passed": true,
  "repeated_training_exact": true,
  "production_changed": false,
  "sealed_opened": false,
  "target_accuracy": "unknown"
}

No automatic promotion. Target accuracy unknown.
