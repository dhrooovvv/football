# Track3 nested CatBoost search — rejected

No final setting selected by outer performance. Each outer fold chose one configuration using only its4training matches in inner LOMO. All9features, folds, corruption masks, seed and penalty16 unchanged. No preprocessing or calibration fit outside a fold.

Budget:80logical inner fits,40unique models by exact training-set/config reuse,5outer fits;10000inner+1100outer=11100actual trees versus21500logical maximum. CPUthread1. Parent remains unaugmented300iterations/depth6/rate.05/l2=3,penalty16.

| Match | Chosen depth/rate/iterations/l2 | Setting | Parent spellF1 | Search spellF1 | Parent macroF1 | Search macroF1 |
|---|---|---|---:|---:|---:|---:|
| J03WMX | [8, 0.05, 200, 6] | clean | 0.501360 | 0.496059 | 0.907574 | 0.906283 |
| J03WMX | [8, 0.05, 200, 6] | targetlike | 0.323426 | 0.319095 | 0.692742 | 0.691753 |
| J03WN1 | [8, 0.05, 200, 6] | clean | 0.484682 | 0.477000 | 0.875014 | 0.873891 |
| J03WN1 | [8, 0.05, 200, 6] | targetlike | 0.313253 | 0.320323 | 0.680025 | 0.680721 |
| J03WOH | [6, 0.08, 200, 3] | clean | 0.568452 | 0.559885 | 0.903698 | 0.902056 |
| J03WOH | [6, 0.08, 200, 3] | targetlike | 0.343671 | 0.344937 | 0.646450 | 0.646687 |
| J03WOY | [8, 0.05, 200, 6] | clean | 0.516129 | 0.516495 | 0.885072 | 0.885071 |
| J03WOY | [8, 0.05, 200, 6] | targetlike | 0.312291 | 0.311798 | 0.663388 | 0.662798 |
| J03WPY | [6, 0.03, 300, 6] | clean | 0.517647 | 0.518887 | 0.904135 | 0.902657 |
| J03WPY | [6, 0.03, 300, 6] | targetlike | 0.324741 | 0.324706 | 0.714401 | 0.712247 |

| Source | Setting | Mean spellF1 | Fold spellF1 SD | Mean macroF1 | Fold macroF1 SD |
|---|---|---:|---:|---:|---:|
| parent | clean | 0.517654 | 0.031366 | 0.895099 | 0.014275 |
| parent | targetlike | 0.323476 | 0.012640 | 0.679401 | 0.026199 |
| nested search | clean | 0.513665 | 0.030927 | 0.893992 | 0.013918 |
| nested search | targetlike | 0.324172 | 0.012502 | 0.678841 | 0.025384 |

Gate REJECT:1/5 paired improvements and median corrupted delta-.000035 fails+.01minimum. Track3 failure1; fixed search budget exhausted, no retrospective grid expansion. Complete gate:
```json
{
  "promoted": false,
  "existing_gate": false,
  "median_primary_delta": -3.485838779948569e-05,
  "paired_spell_deltas": {
    "J03WMX": -0.004815402672620206,
    "J03WN1": -0.00030621904508598696,
    "J03WOH": -0.0036505684337665434,
    "J03WOY": -6.346844077348424e-05,
    "J03WPY": 0.0006026724338670797
  },
  "paired_macro_deltas": {
    "J03WMX": -0.0011401847484576733,
    "J03WN1": -0.00021321315776900995,
    "J03WOH": -0.0007026256318585222,
    "J03WOY": -0.00029594456274684156,
    "J03WPY": -0.0018155611162297136
  },
  "primary_deltas": {
    "J03WMX": -0.004330215308279373,
    "J03WN1": 0.007070002756652483,
    "J03WOH": 0.0012658227848101888,
    "J03WOY": -0.0004927499843073169,
    "J03WPY": -3.485838779948569e-05
  },
  "matches_improved": 1,
  "tests_passed": true,
  "logical_inner_fits": 80,
  "unique_inner_fits": 40,
  "outer_fits": 5,
  "outer_corrupted_spell_std": 0.012501659155745509
}
```

Nested search prevents direct outer-label setting choice within this experiment, but the same five matches have historical reuse. Fold SD is descriptive variation, not an independent confidence interval. No other-provider transfer claim. Optional GRU deferred because Track1 required evaluations are unavailable; no scratch sequence model trained.
