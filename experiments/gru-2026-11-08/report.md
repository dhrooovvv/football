# Optional CPU GRU blend — rejected, November8

One preregistered candidate only: scratch1layerbidirectionalhidden16,200Adamsteps,batch8,250framewindows/200retainedlossframes,9fold-standardizedfeatures,cleanIDSSE4training, fixed75%CatBoost/25%GRU andViterbi16. No PFF/target/public/sealeddata used. Noaugmentation/calibration/search. CatBoost unchanged, GRUadditionalcompute explicitly bounded.

**Reject:**1/5pairedmatches improve; median corruptedspell delta-.007520 fails+.01minimum and existingpairedgate fails. No rescuedblend/window/budget. Productionunchanged.

| Match | Setting | Parent spellF1 | Blend spellF1 | Parent macroF1 | Blend macroF1 |
|---|---|---:|---:|---:|---:|
| J03WMX | clean | 0.501360 | 0.477962 | 0.907574 | 0.906915 |
| J03WMX | targetlike | 0.323426 | 0.310594 | 0.692742 | 0.692531 |
| J03WN1 | clean | 0.484682 | 0.466752 | 0.875014 | 0.874405 |
| J03WN1 | targetlike | 0.313253 | 0.315034 | 0.680025 | 0.681750 |
| J03WOH | clean | 0.568452 | 0.568107 | 0.903698 | 0.905198 |
| J03WOH | targetlike | 0.343671 | 0.346230 | 0.646450 | 0.650435 |
| J03WOY | clean | 0.516129 | 0.500800 | 0.885072 | 0.886473 |
| J03WOY | targetlike | 0.312291 | 0.297290 | 0.663388 | 0.661155 |
| J03WPY | clean | 0.517647 | 0.508872 | 0.904135 | 0.903125 |
| J03WPY | targetlike | 0.324741 | 0.317221 | 0.714401 | 0.715516 |

| Arm | Setting | Mean spellF1 | Mean macroF1 | Fold spellF1 SD |
|---|---|---:|---:|---:|
| parent | clean | 0.517654 | 0.895099 | 0.031366 |
| parent | targetlike | 0.323476 | 0.679401 | 0.012640 |
| GRUblend | clean | 0.504499 | 0.895223 | 0.039395 |
| GRUblend | targetlike | 0.317274 | 0.680278 | 0.017940 |

## Determinism and parent comparability

All5folds repeated full200step training with identical state tensors/scaler/losssequence. All10heldoutcases: exact reloadprobabilities and decodedCSVbytes equal atfixedbatch1 andbatch4. These are version/platform-specific results, not crosshardwareguarantees.1000 candidate updates plus 1000 independent repeat-verification updates = 2000 total; eachbatch8×250inputframes, losscentral200. Trainingtime cost.json records ONLYinitialtraining time, excludes repeatverification and inference. Modelserializationbyteequality notclaimed.

Maximum parent half-block versus historical label-supported score difference: spell0,macro0. No label-derived reset used for this experiment.

## Missing-ball quality

| Match | Setting | Arm | Missing frames | Live recall | D precision | D recall | Predicted D share |
|---|---|---|---:|---:|---:|---:|---:|
| J03WMX | clean | parent | 0 | undefined | undefined | undefined | undefined |
| J03WMX | targetlike | parent | 52145 | 0.000634 | 0.364880 | 1.000000 | 0.999597 |
| J03WN1 | clean | parent | 0 | undefined | undefined | undefined | undefined |
| J03WN1 | targetlike | parent | 56720 | 0.000521 | 0.525958 | 1.000000 | 0.999753 |
| J03WOH | clean | parent | 0 | undefined | undefined | undefined | undefined |
| J03WOH | targetlike | parent | 65199 | 0.000147 | 0.478648 | 1.000000 | 0.999923 |
| J03WOY | clean | parent | 0 | undefined | undefined | undefined | undefined |
| J03WOY | targetlike | parent | 60389 | 0.000927 | 0.446503 | 1.000000 | 0.999487 |
| J03WPY | clean | parent | 0 | undefined | undefined | undefined | undefined |
| J03WPY | targetlike | parent | 52490 | 0.001010 | 0.471846 | 1.000000 | 0.999467 |
| J03WMX | clean | GRUblend | 0 | undefined | undefined | undefined | undefined |
| J03WMX | targetlike | GRUblend | 52145 | 0.001298 | 0.365034 | 1.000000 | 0.999175 |
| J03WN1 | clean | GRUblend | 0 | undefined | undefined | undefined | undefined |
| J03WN1 | targetlike | GRUblend | 56720 | 0.000521 | 0.525958 | 1.000000 | 0.999753 |
| J03WOH | clean | GRUblend | 0 | undefined | undefined | undefined | undefined |
| J03WOH | targetlike | GRUblend | 65199 | 0.000794 | 0.478810 | 1.000000 | 0.999586 |
| J03WOY | clean | GRUblend | 0 | undefined | undefined | undefined | undefined |
| J03WOY | targetlike | GRUblend | 60389 | 0.000927 | 0.446503 | 1.000000 | 0.999487 |
| J03WPY | clean | GRUblend | 0 | undefined | undefined | undefined | undefined |
| J03WPY | targetlike | GRUblend | 52490 | 0.001442 | 0.471954 | 1.000000 | 0.999238 |

## Limits

10swindow is shorter than median10.72sgaps and much shorter than p90~33.8s; some interiorscannotseeobservedendpoints. Bidirectionalwindows use localfutureobservations offline. Clean-onlytraining leaves missing masks/gapageOOD. This failure is evidence against this fixedsmallbudgetcandidate, not allGRUs or sequence modelling. No new temporal feature,augmentation or largercontexttriedafterresults. Five developmentmatches have historicalreuse; no unbiased generalization claim. Torchisolatedresearchdependency, notproductionrequirement.

Gate:
```json
{
  "promoted": false,
  "existing_gate": false,
  "primary_median_delta": -0.007520196934094114,
  "paired_spell_deltas": {
    "J03WMX": -0.018114648673849654,
    "J03WN1": -0.008074361833281696,
    "J03WOH": 0.0011072025587004486,
    "J03WOY": -0.015164974373041207,
    "J03WPY": -0.008147537653247827
  },
  "paired_macro_deltas": {
    "J03WMX": -0.00043528721528940384,
    "J03WN1": 0.000558576875230421,
    "J03WOH": 0.0027422604129928585,
    "J03WOY": -0.00041600870724656236,
    "J03WPY": 5.244173730278856e-05
  },
  "primary_deltas": {
    "J03WMX": -0.012831377449736003,
    "J03WN1": 0.001781470710427946,
    "J03WOH": 0.0025586221207719584,
    "J03WOY": -0.015000916488017935,
    "J03WPY": -0.007520196934094114
  },
  "matches_improved": 1,
  "tests_pass": true,
  "determinism_pass": true
}
```
