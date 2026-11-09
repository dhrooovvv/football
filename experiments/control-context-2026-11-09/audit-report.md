# Penalty16 frozen audit — November9

No fitting or target/sealed access. Gap bins are elapsed missing age, not full run length. Frame counts do not attribute spellF1 loss.

|Match|Setting|spellF1|macroF1|Missed|Spurious|Short recall|Wrong-team frames|Dead/live frames|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|J03WMX|clean|0.501360|0.907574|309|96|0.0928|11706|106|
|J03WMX|targetlike|0.323426|0.692742|386|158|0.0722|7735|33218|
|J03WN1|clean|0.484682|0.875014|302|105|0.1221|12624|169|
|J03WN1|targetlike|0.313253|0.680025|382|129|0.0872|8518|27111|
|J03WOH|clean|0.568452|0.903698|201|88|0.1171|10132|158|
|J03WOH|targetlike|0.343671|0.646450|294|122|0.0901|5951|34159|
|J03WOY|clean|0.516129|0.885072|252|115|0.0916|12983|215|
|J03WOY|targetlike|0.312291|0.663388|347|151|0.0687|7220|33639|
|J03WPY|clean|0.517647|0.904135|238|76|0.0806|10727|119|
|J03WPY|targetlike|0.324741|0.714401|312|145|0.0645|7760|27889|

Clean wrong-team frames58172 versus767dead/live. Target-like wrong-team37184 versus156016dead/live. Missing-age>1second has0live recovery in this cohort. These are diagnostic counts, not causal or achievable spell gains. A short-context feature cannot resolve unsupported long gaps. One fixed temporal proximity/support bundle is chosen to test handovers and gap endpoints, retaining CatBoost16; long-gap limitations remain. Full boundary quantiles and age slices: audit.json.
