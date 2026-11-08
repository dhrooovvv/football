# Reduced-context development results

Quality screen only. Production unchanged; single-thread verification is still required for any winner.

| Match | Setting | Model | spellF1 | macroF1 |
|---|---|---|---:|---:|
| J03WMX | clean | parent | 0.501360 | 0.907574 |
| J03WMX | clean | tabicl | 0.474129 | 0.884897 |
| J03WMX | clean | blend | 0.490500 | 0.904441 |
| J03WMX | targetlike | parent | 0.323426 | 0.692742 |
| J03WMX | targetlike | tabicl | 0.287711 | 0.666599 |
| J03WMX | targetlike | blend | 0.325032 | 0.694477 |
| J03WN1 | clean | parent | 0.484682 | 0.875014 |
| J03WN1 | clean | tabicl | 0.467545 | 0.847989 |
| J03WN1 | clean | blend | 0.479506 | 0.872101 |
| J03WN1 | targetlike | parent | 0.313253 | 0.680025 |
| J03WN1 | targetlike | tabicl | 0.283014 | 0.635357 |
| J03WN1 | targetlike | blend | 0.318194 | 0.678705 |
| J03WOH | clean | parent | 0.568452 | 0.903698 |
| J03WOH | clean | tabicl | 0.536351 | 0.895296 |
| J03WOH | clean | blend | 0.548997 | 0.901189 |
| J03WOH | targetlike | parent | 0.343671 | 0.646450 |
| J03WOH | targetlike | tabicl | 0.298698 | 0.586960 |
| J03WOH | targetlike | blend | 0.333652 | 0.644567 |
| J03WOY | clean | parent | 0.516129 | 0.885072 |
| J03WOY | clean | tabicl | 0.471557 | 0.869039 |
| J03WOY | clean | blend | 0.504994 | 0.880899 |
| J03WOY | targetlike | parent | 0.312291 | 0.663388 |
| J03WOY | targetlike | tabicl | 0.280739 | 0.625197 |
| J03WOY | targetlike | blend | 0.311921 | 0.662082 |
| J03WPY | clean | parent | 0.517647 | 0.904135 |
| J03WPY | clean | tabicl | 0.517474 | 0.898619 |
| J03WPY | clean | blend | 0.520944 | 0.902475 |
| J03WPY | targetlike | parent | 0.324741 | 0.714401 |
| J03WPY | targetlike | tabicl | 0.309585 | 0.674716 |
| J03WPY | targetlike | blend | 0.347669 | 0.721250 |

```json
{
  "gate": {
    "standalone_vs_parent": {
      "quality_eligible": false,
      "development_promotable": false,
      "phase": "QUALITY_REJECTED",
      "existing_gate": false,
      "primary_median_delta": -0.03155171651361277,
      "paired_spell_deltas": {
        "J03WMX": -0.03147259971267141,
        "J03WN1": -0.023688247092043258,
        "J03WOH": -0.03853704394026053,
        "J03WOY": -0.038061738607202855,
        "J03WPY": -0.007664187732826067
      },
      "paired_macro_deltas": {
        "J03WMX": -0.024410317580552676,
        "J03WN1": -0.035846396113054624,
        "J03WOH": -0.03394626356954855,
        "J03WOY": -0.027111985120254256,
        "J03WPY": -0.022600829993181915
      },
      "primary_deltas": {
        "J03WMX": -0.03571484932172009,
        "J03WN1": -0.03023896351690286,
        "J03WOH": -0.04497334627855426,
        "J03WOY": -0.03155171651361277,
        "J03WPY": -0.015155619138451648
      },
      "matches_improved": 0,
      "tests_pass": true,
      "determinism_all_cases_pass": null,
      "prior_single_thread_cache_contract": true,
      "current_repeatability_verified": false,
      "production_promotion": false,
      "production_promotion_requires": "integration, official validation, repeated CSV and clean-environment reproduction"
    },
    "blend_reference": "parent",
    "blend_vs_current_best": {
      "quality_eligible": false,
      "development_promotable": false,
      "phase": "QUALITY_REJECTED",
      "existing_gate": false,
      "primary_median_delta": 0.0016063997309733735,
      "paired_spell_deltas": {
        "J03WMX": -0.004626651803240123,
        "J03WN1": -0.00011769447662668409,
        "J03WOH": -0.014736479171342187,
        "J03WOY": -0.005752239237245105,
        "J03WPY": 0.013112663085210363
      },
      "paired_macro_deltas": {
        "J03WMX": -0.0006994817102977668,
        "J03WN1": -0.002116164959989897,
        "J03WOH": -0.0021963396551213377,
        "J03WOY": -0.002739792508325789,
        "J03WPY": 0.002594723278289357
      },
      "primary_deltas": {
        "J03WMX": 0.0016063997309733735,
        "J03WN1": 0.004940879054064928,
        "J03WOH": -0.010018573476268389,
        "J03WOY": -0.0003690441677701717,
        "J03WPY": 0.022928432191590187
      },
      "matches_improved": 1,
      "tests_pass": true,
      "determinism_all_cases_pass": null,
      "prior_single_thread_cache_contract": true,
      "current_repeatability_verified": false,
      "production_promotion": false,
      "production_promotion_requires": "integration, official validation, repeated CSV and clean-environment reproduction"
    },
    "blend_vs_original_parent": {
      "quality_eligible": false,
      "development_promotable": false,
      "phase": "QUALITY_REJECTED",
      "existing_gate": false,
      "primary_median_delta": 0.0016063997309733735,
      "paired_spell_deltas": {
        "J03WMX": -0.004626651803240123,
        "J03WN1": -0.00011769447662668409,
        "J03WOH": -0.014736479171342187,
        "J03WOY": -0.005752239237245105,
        "J03WPY": 0.013112663085210363
      },
      "paired_macro_deltas": {
        "J03WMX": -0.0006994817102977668,
        "J03WN1": -0.002116164959989897,
        "J03WOH": -0.0021963396551213377,
        "J03WOY": -0.002739792508325789,
        "J03WPY": 0.002594723278289357
      },
      "primary_deltas": {
        "J03WMX": 0.0016063997309733735,
        "J03WN1": 0.004940879054064928,
        "J03WOH": -0.010018573476268389,
        "J03WOY": -0.0003690441677701717,
        "J03WPY": 0.022928432191590187
      },
      "matches_improved": 1,
      "tests_pass": true,
      "determinism_all_cases_pass": null,
      "prior_single_thread_cache_contract": true,
      "current_repeatability_verified": false,
      "production_promotion": false,
      "production_promotion_requires": "integration, official validation, repeated CSV and clean-environment reproduction"
    },
    "development_selected": "parent",
    "determinism_all_cases_pass": null,
    "production_changed": false,
    "sealed_opened": false,
    "target_accuracy": "unknown",
    "status": "QUALITY_REJECTED",
    "determinism_all_cases_performed": false,
    "determinism_verification_started": false,
    "verification_skipped_reason": "Neither fixed arm passed quality gate; no promotion possible"
  },
  "failure": null
}
```
