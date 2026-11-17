# Recovery audit review — November 15, 2026

Diagnostic complete, not a new model result. Selected Trial B stays unchanged. Ten user-run contracts pass, all ten parent/temporal archived CSV hashes and official scores reproduced, and inference-batch CSV identity passed in the saved runner. Root independently checks206source/165evidence fingerprints, committed source bytes, five completed-unit content hashes, exact unit-to-aggregate equality, current registration/check-log binding and report digest. No tests, inference, model/array deserialization or scoring by root. Result audit: result-audit.json. Initial failed check evidence is retained.

## Per-match evidence

|Match|Setting|Recovered|Introduced spurious|Parent-margin AUC|Temporal-margin AUC|Member-agreement AUC|
|---|---|---:|---:|---:|---:|---:|
|J03WMX|clean|55|64|.6403|.5835|.6081|
|J03WMX|targetlike|55|126|.6297|.6807|.6654|
|J03WN1|clean|55|65|.5891|.6327|.6413|
|J03WN1|targetlike|48|127|.6649|.7054|.6703|
|J03WOH|clean|36|54|.6476|.6836|.6618|
|J03WOH|targetlike|46|94|.7229|.6989|.6326|
|J03WOY|clean|42|85|.5566|.6314|.5909|
|J03WOY|targetlike|40|123|.6813|.7404|.6957|
|J03WPY|clean|31|53|.6713|.5886|.5350|
|J03WPY|targetlike|23|100|.6200|.6665|.6226|

Clean219recovered/321introduced-spurious; corrupted212/570. These are operational greedy IoU.5 spell categories, not net gains: the refiner also loses some previously matched possessions. They are not the same counts as the earlier net missed-spell changes. Existing total spurious counts also include persistent errors.

Every signal's AUC exceeds0.5in all five matches in both settings. Mean corrupted temporal-margin AUC.698381, parent-margin.663766, agreement.657323. Clean means .623964/.620996/.607406 respectively. Temporal confidence has the strongest corrupted rank separation here, but all distributions overlap: corrupted recovered median margins .6999–.7385 versus spurious .5186–.5935. There is no perfect confidence cutoff. These are reused-development diagnostic associations, not accuracy, significance or a promised spellF1 improvement.

## One next intervention, proposed only

The evidence supports one fixed temporal-confidence filter rather than more training first: after frozen temporal penalty16 decoding, restore Trial-B labels over an entire temporal H/A spell when its mean temporal probability margin over the strongest alternative is below0.5; otherwise keep it. Keep temporal D regions unchanged. Treat complete original half-bounded decoded spells consistently, including unknown-supervision regions at inference: labels must never define deployed filter boundaries. This is one post-decoder rule, not a confidence grid or trained gating model. It can create new boundaries or lose real recovered spells; only the full unchanged paired gate can decide retention.

Threshold0.5would be a single conservative, prospectively fixed margin requirement, not a fitted optimum. The rule and signal were motivated by reused development errors, so selection bias remains. Do not evaluate it from saved diagnostic labels now or claim a gain. A separate committed protocol/source lock and explicit authorization precede execution; no rule is implemented/tested/promoted in this audit. If it fails, close this bounded temporal rescue without another cutoff. No additional seed, graph alteration or new architecture is proposed.

## Graph continuation evidence

All20recorded stage-wise late5000-minus-preceding5000 total-training-loss differences are negative, range−.015411to−.008241. This supports continued fitting of the training objective, not a held-out spellF1 learning trend. There are no intermediate held-out predictions establishing undertraining instead of overfitting. Longer graph training might help, but the audit does not justify promising it or spending another full comparison before the cheaper temporal rule. Graph remains rejected and no longer training run is registered.

## Decision

No change to selected B (mean development spellF1.650384708clean/.509835640corrupted), production, private submission CSV, gate, freeze or sealed plan. Next optional comparison is the one confidence filter above, requiring its own prospective protocol and approval. No training performed. Target accuracy unknown. No external publication or submission.
