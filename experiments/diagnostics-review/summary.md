# Frozen diagnostic development results

All figures are external development evidence. Target rows, distributions and public score remain local. Clean/target-like mean is the paired gate input. Frozen production remains penalty8 pending review.

| Method | Condition | Mean spellF1 | Mean macroF1 |
|---|---|---:|---:|
| baseline_0 | clean | 0.101541 | 0.355338 |
| baseline_0 | targetlike | 0.074968 | 0.420203 |
| baseline_125 | clean | 0.207060 | 0.377770 |
| baseline_125 | targetlike | 0.152251 | 0.418091 |
| baseline_25 | clean | 0.286704 | 0.376948 |
| baseline_25 | targetlike | 0.179699 | 0.435053 |
| baseline_50 | clean | 0.296145 | 0.384029 |
| baseline_50 | targetlike | 0.196645 | 0.438793 |
| catboost_penalty16 | clean | 0.517654 | 0.895099 |
| catboost_penalty16 | targetlike | 0.323476 | 0.679401 |
| catboost_penalty2 | clean | 0.317620 | 0.865113 |
| catboost_penalty2 | targetlike | 0.210958 | 0.654957 |
| catboost_penalty32 | clean | 0.478423 | 0.895019 |
| catboost_penalty32 | targetlike | 0.304005 | 0.679724 |
| catboost_penalty8 | clean | 0.508566 | 0.889775 |
| catboost_penalty8 | targetlike | 0.312864 | 0.672865 |
| nearest_decoder8 | clean | 0.115705 | 0.355828 |
| nearest_decoder8 | targetlike | 0.085645 | 0.420641 |

## Frozen penalty8 per-match taxonomy

Boundary quantiles: min/p10/median/p90/p99/max in frames; only typed boundaries matched within 2 seconds. Missed/spurious use IoU .5. Oracle gains are overlapping diagnostic repair upper bounds, not additive causal attribution or selectable predictions.

| Match | Condition | spellF1 | macroF1 | Missed | Spurious | Short recall | Dead/live wrong frames | Boundary quantiles | Oracle dead/live gain | Oracle wrong-team gain |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| J03WMX | clean | 0.499781 | 0.902245 | 281 | 173 | 0.1495 | 127 | [-50.0, -25.0, 0.0, 6.199999999999989, 45.860000000000014, 48.0] | 0.004605 | 0.492826 |
| J03WMX | targetlike | 0.304892 | 0.685807 | 380 | 237 | 0.1134 | 33243 | [-50.0, -22.0, 0.0, 8.0, 48.60000000000002, 50.0] | 0.342878 | 0.391082 |
| J03WN1 | clean | 0.496432 | 0.873339 | 267 | 192 | 0.2093 | 228 | [-50.0, -34.4, 0.0, 10.400000000000034, 46.0, 49.0] | 0.005401 | 0.494196 |
| J03WN1 | targetlike | 0.310214 | 0.675876 | 371 | 213 | 0.1453 | 27110 | [-48.0, -33.599999999999994, 0.0, 19.799999999999983, 46.0, 49.0] | 0.322646 | 0.415695 |
| J03WOH | clean | 0.527205 | 0.894625 | 189 | 190 | 0.1712 | 152 | [-50.0, -33.0, 0.0, 5.099999999999966, 40.07999999999993, 48.0] | 0.003316 | 0.464874 |
| J03WOH | targetlike | 0.325326 | 0.637961 | 292 | 179 | 0.1081 | 34159 | [-50.0, -36.099999999999994, 0.0, 6.0, 43.26000000000005, 49.0] | 0.401089 | 0.290794 |
| J03WOY | clean | 0.483060 | 0.874689 | 231 | 234 | 0.1832 | 281 | [-49.0, -31.0, 0.0, 4.100000000000023, 47.01999999999998, 50.0] | 0.005343 | 0.507561 |
| J03WOY | targetlike | 0.294293 | 0.654699 | 341 | 235 | 0.1374 | 33706 | [-49.0, -32.0, 0.0, 1.5999999999999943, 45.43999999999994, 50.0] | 0.394341 | 0.329748 |
| J03WPY | clean | 0.536352 | 0.903977 | 199 | 152 | 0.1935 | 119 | [-50.0, -32.0, 0.0, 6.0, 40.89999999999998, 49.0] | -0.002352 | 0.460804 |
| J03WPY | targetlike | 0.329596 | 0.709985 | 296 | 221 | 0.1371 | 27895 | [-50.0, -31.0, 0.0, 14.0, 41.0, 49.0] | 0.331713 | 0.349828 |
