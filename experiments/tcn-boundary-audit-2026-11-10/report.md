# Frozen temporal-model error audit — November10

40cachedexternalcases, no modeltraining/inference. Short<=2s recall measured atIoU.5; boundaryshift quantiles conditionalonmatcheswithin2s. Counts pooled across5matches, not independent significance or additive spell-cost attribution. Label-derivedboundarymasks diagnostic-only.

|Model|Setting|Short recall|Long recall|Missed|Spurious|Observed wrong-team frames|Observed dead/live frames|
|---|---|---:|---:|---:|---:|---:|---:|
|catboost|clean|0.1011|0.5866|1302|480|58172|767|
|catboost|targetlike|0.0765|0.3293|1721|705|37162|925|
|tcn|clean|0.2008|0.6951|1060|479|44031|2611|
|tcn|targetlike|0.1311|0.4249|1532|899|28259|1952|
|blend|clean|0.1434|0.6650|1149|318|43471|1316|
|blend|targetlike|0.0956|0.4050|1589|523|27281|1201|
|gap_blend|clean|0.1380|0.6585|1163|317|44143|1233|
|gap_blend|targetlike|0.0997|0.4339|1541|440|28147|960|

Decision: observedownership andpoorbriefpossessionrecall justify testing explicit ball-conditionedrelations. Not a proof of causalspellloss; no claim boundaryhead/attention/longcontext willwin. Gapblend reducescorruptedspuriousspells versusunaugblend; therefore addingunqualifiedsmoothing isnotprioritized. One relativeXY+pairmask intervention, no velocity/context/loss/decoderbundle. Fullpermatchboundaryquantiles/slices/shortcounts areinresults.json.
