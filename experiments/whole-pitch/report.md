# Rolling whole-pitch experiment — rejected

Parent: unaugmented nine-core CatBoost + penalty16. Five-column bundle used fixed trailing2.5s (63observations) means, independent of ball masks; no parameter/window/grid search. Same folds, seeds, budget and target-like corruption.

**Both gates fail:** existing paired gate fails (1/5 improve, median spellF1 delta-.006600); minimum median corrupted gain fails (-.005208 versus required+.01). Drop bundle and stop feature additions.25 tests passed including2 new feature contracts; rejected implementation/tests archived here for reproduction, excluded from production.

| Match | Condition | Parent spellF1 | Bundle spellF1 | Parent macroF1 | Bundle macroF1 |
|---|---|---:|---:|---:|---:|
| J03WMX | clean | 0.501360 | 0.445217 | 0.907574 | 0.899143 |
| J03WMX | targetlike | 0.323426 | 0.277677 | 0.692742 | 0.683453 |
| J03WN1 | clean | 0.484682 | 0.479126 | 0.875014 | 0.871808 |
| J03WN1 | targetlike | 0.313253 | 0.309434 | 0.680025 | 0.679476 |
| J03WOH | clean | 0.568452 | 0.531751 | 0.903698 | 0.905597 |
| J03WOH | targetlike | 0.343671 | 0.324675 | 0.646450 | 0.653453 |
| J03WOY | clean | 0.516129 | 0.508136 | 0.885072 | 0.885687 |
| J03WOY | targetlike | 0.312291 | 0.307082 | 0.663388 | 0.663725 |
| J03WPY | clean | 0.517647 | 0.507955 | 0.904135 | 0.902576 |
| J03WPY | targetlike | 0.324741 | 0.337463 | 0.714401 | 0.718625 |

## Dead/live quality where ball is missing

Subset: graded frames with ball_observed=0; binary classes dead versus live, H/A collapsed. Clean external matches have no missing-ball frames, so those subset metrics are undefined, not zero.

| Match | Missing frames | Parent binary macroF1 | Bundle binary macroF1 | Parent D precision/recall/F1 | Bundle D precision/recall/F1 | Parent errors | Bundle errors |
|---|---:|---:|---:|---|---|---:|---:|
| J03WMX | 52145 | 0.2680 | 0.2680 | 0.3649/1.0000/0.5347 | 0.3649/1.0000/0.5347 | 33105 | 33105 |
| J03WN1 | 56720 | 0.3452 | 0.3452 | 0.5260/1.0000/0.6893 | 0.5260/1.0000/0.6893 | 26881 | 26881 |
| J03WOH | 65199 | 0.3239 | 0.3242 | 0.4786/1.0000/0.6474 | 0.4787/1.0000/0.6475 | 33989 | 33979 |
| J03WOY | 60389 | 0.3096 | 0.3092 | 0.4465/1.0000/0.6174 | 0.4464/1.0000/0.6173 | 33408 | 33420 |
| J03WPY | 52490 | 0.3216 | 0.3216 | 0.4718/1.0000/0.6412 | 0.4718/1.0000/0.6412 | 27708 | 27708 |

Whole-pitch speed is slot displacement, not verified identity motion; compactness reflects visible slots, and player missingness can bias aggregates. No causal claim about why the bundle failed; no posthoc subsets or new feature attempts. Sealed matches and public labels untouched. Finalization follows the requested order: final target export twice + validator, clean-environment reproduction/hashes, technical document.

Gate details:
```json
{
  "promoted": false,
  "existing_gate_pass": false,
  "minimum_primary_gate_pass": false,
  "median_corrupted_spell_delta": -0.005208349818791869,
  "paired_spell_deltas": {
    "J03WMX": -0.050945292686740584,
    "J03WN1": -0.004687638519316584,
    "J03WOH": -0.02784816954888264,
    "J03WOY": -0.006600449568611888,
    "J03WPY": 0.001514936366966646
  },
  "paired_macro_deltas": {
    "J03WMX": -0.00886034428796989,
    "J03WN1": -0.0018775914393026616,
    "J03WOH": 0.004450776901587461,
    "J03WOY": 0.0004757059075157777,
    "J03WPY": 0.0013328647204170485
  },
  "median_paired_spell_delta": -0.006600449568611888,
  "median_paired_macro_delta": 0.0004757059075157777,
  "matches_improved": 1,
  "primary_corrupted_deltas": {
    "J03WMX": -0.045748273340375345,
    "J03WN1": -0.0038190497840417947,
    "J03WOH": -0.018995561400624694,
    "J03WOY": -0.005208349818791869,
    "J03WPY": 0.012722386102917205
  },
  "tests_passed": true
}
```
