# Frozen 50/50 Probability Ensemble: Trial B TCN + Graph50k

## Summary Metrics (Spell F1)

| Condition | Metric | Trial B TCN | Graph50k | 50/50 Ensemble |
| :--- | :--- | :--- | :--- | :--- |
| Clean | Mean | 0.650385 | 0.648875 | 0.659432 |
| Clean | Median | 0.647843 | 0.651401 | 0.660465 |
| Targetlike | Mean | 0.509836 | 0.518200 | 0.522431 |
| Targetlike | Median | 0.516391 | 0.519042 | 0.517526 |

## Summary Metrics (Macro F1)

| Condition | Metric | Trial B TCN | Graph50k | 50/50 Ensemble |
| :--- | :--- | :--- | :--- | :--- |
| Clean | Mean | 0.926752 | 0.925788 | 0.929070 |
| Clean | Median | 0.932253 | 0.927787 | 0.934239 |
| Targetlike | Mean | 0.837981 | 0.845472 | 0.848072 |
| Targetlike | Median | 0.845931 | 0.853001 | 0.849162 |

## Per-Match Spell F1 and Paired Deltas

| Match | Cond | TCN | Graph50k | Ensemble | Δ vs TCN | Δ vs G50k |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| J03WMX | clean | 0.624036 | 0.600000 | 0.627721 | +0.003684 | +0.027721 |
| J03WMX | targetlike | 0.483486 | 0.482286 | 0.497583 | +0.014097 | +0.015298 |
| J03WN1 | clean | 0.614756 | 0.643537 | 0.624771 | +0.010015 | -0.018767 |
| J03WN1 | targetlike | 0.452398 | 0.491917 | 0.475177 | +0.022780 | -0.016740 |
| J03WOH | clean | 0.714674 | 0.696721 | 0.710440 | -0.004234 | +0.013718 |
| J03WOH | targetlike | 0.543099 | 0.565498 | 0.560455 | +0.017357 | -0.005043 |
| J03WOY | clean | 0.650614 | 0.651401 | 0.660465 | +0.009851 | +0.009064 |
| J03WOY | targetlike | 0.516391 | 0.519042 | 0.517526 | +0.001134 | -0.001516 |
| J03WPY | clean | 0.647843 | 0.652713 | 0.673766 | +0.025923 | +0.021053 |
| J03WPY | targetlike | 0.553804 | 0.532258 | 0.561413 | +0.007609 | +0.029155 |

## Gate v2 Outcome

### Against Retained Trial B TCN:
- Primary Corrupted Median Delta: +0.014097 (required > 0): PASS
- Paired Median Spell Delta: +0.008891 (required > 0): PASS
- Paired Matches Improved: 5/5 (required >= 3): PASS
- Paired Median Macro Delta: +0.004555 (required >= -0.01): PASS
- Repeatability: PASS (byte-identical across all 10 CSVs)
- **Overall Gate vs TCN: PASS (Eligible)**

### Against Graph50k:
- Primary Corrupted Median Delta: -0.001516 (required > 0): FAIL
- Paired Median Spell Delta: +0.004338 (required > 0): PASS
- Paired Matches Improved: 4/5 (required >= 3): PASS
- Paired Median Macro Delta: +0.002211 (required >= -0.01): PASS
- **Overall Gate vs Graph50k: FAIL (Ineligible)**
