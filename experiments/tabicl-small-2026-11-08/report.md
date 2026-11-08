# Reduced-context development results

Quality screen only. Production unchanged; single-thread verification is still required for any winner.

| Match | Setting | Model | spellF1 | macroF1 |
|---|---|---|---:|---:|
| J03WMX | clean | parent | 0.501360 | 0.907574 |
| J03WMX | clean | tabicl | 0.473177 | 0.888859 |
| J03WMX | clean | blend | 0.490452 | 0.906677 |
| J03WMX | targetlike | parent | 0.323426 | 0.692742 |
| J03WMX | targetlike | tabicl | 0.283654 | 0.669451 |
| J03WMX | targetlike | blend | 0.323196 | 0.694999 |
| J03WN1 | clean | parent | 0.484682 | 0.875014 |
| J03WN1 | clean | tabicl | 0.458344 | 0.865858 |
| J03WN1 | clean | blend | 0.474314 | 0.872311 |
| J03WN1 | targetlike | parent | 0.313253 | 0.680025 |
| J03WN1 | targetlike | tabicl | 0.268804 | 0.613169 |
| J03WN1 | targetlike | blend | 0.319041 | 0.681582 |
| J03WOH | clean | parent | 0.568452 | 0.903698 |
| J03WOH | clean | tabicl | 0.551645 | 0.896695 |
| J03WOH | clean | blend | 0.556874 | 0.902283 |
| J03WOH | targetlike | parent | 0.343671 | 0.646450 |
| J03WOH | targetlike | tabicl | 0.312409 | 0.589202 |
| J03WOH | targetlike | blend | 0.343131 | 0.645874 |
| J03WOY | clean | parent | 0.516129 | 0.885072 |
| J03WOY | clean | tabicl | 0.493506 | 0.878976 |
| J03WOY | clean | blend | 0.503493 | 0.880492 |
| J03WOY | targetlike | parent | 0.312291 | 0.663388 |
| J03WOY | targetlike | tabicl | 0.289855 | 0.631945 |
| J03WOY | targetlike | blend | 0.315461 | 0.668073 |
| J03WPY | clean | parent | 0.517647 | 0.904135 |
| J03WPY | clean | tabicl | 0.509357 | 0.897633 |
| J03WPY | clean | blend | 0.525110 | 0.903075 |
| J03WPY | targetlike | parent | 0.324741 | 0.714401 |
| J03WPY | targetlike | tabicl | 0.303977 | 0.674969 |
| J03WPY | targetlike | blend | 0.326736 | 0.712210 |

```json
{
  "gate": {
    "standalone_vs_parent": {
      "quality_eligible": false,
      "development_promotable": false,
      "phase": "QUALITY_REJECTED",
      "existing_gate": false,
      "primary_median_delta": -0.03126212695186176,
      "paired_spell_deltas": {
        "J03WMX": -0.033977394222476365,
        "J03WN1": -0.03539393651641576,
        "J03WOH": -0.024034219524783018,
        "J03WOY": -0.022528984540549524,
        "J03WPY": -0.014526900845399204
      },
      "paired_macro_deltas": {
        "J03WMX": -0.021002898697783823,
        "J03WN1": -0.03800572421935433,
        "J03WOH": -0.032125515308402575,
        "J03WOY": -0.018769657726047884,
        "J03WPY": -0.022966513747105677
      },
      "primary_deltas": {
        "J03WMX": -0.039771846541367895,
        "J03WN1": -0.04444906630220008,
        "J03WOH": -0.03126212695186176,
        "J03WOY": -0.022435430329527994,
        "J03WPY": -0.020763468013467956
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
      "primary_median_delta": 0.0019948574867335034,
      "paired_spell_deltas": {
        "J03WMX": -0.005568629218737686,
        "J03WN1": -0.002289980067785413,
        "J03WOH": -0.006058659841884362,
        "J03WOY": -0.004732828639696707,
        "J03WPY": 0.0047289654108972345
      },
      "paired_macro_deltas": {
        "J03WMX": 0.0006802173109686782,
        "J03WN1": -0.000573275110827387,
        "J03WOH": -0.0009957783638470108,
        "J03WOY": 5.210220931317622e-05,
        "J03WPY": -0.0016252077948277766
      },
      "primary_deltas": {
        "J03WMX": -0.00022981640655428404,
        "J03WN1": 0.005788266247413132,
        "J03WOH": -0.0005398956606139094,
        "J03WOY": 0.00317049011450532,
        "J03WPY": 0.0019948574867335034
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
      "primary_median_delta": 0.0019948574867335034,
      "paired_spell_deltas": {
        "J03WMX": -0.005568629218737686,
        "J03WN1": -0.002289980067785413,
        "J03WOH": -0.006058659841884362,
        "J03WOY": -0.004732828639696707,
        "J03WPY": 0.0047289654108972345
      },
      "paired_macro_deltas": {
        "J03WMX": 0.0006802173109686782,
        "J03WN1": -0.000573275110827387,
        "J03WOH": -0.0009957783638470108,
        "J03WOY": 5.210220931317622e-05,
        "J03WPY": -0.0016252077948277766
      },
      "primary_deltas": {
        "J03WMX": -0.00022981640655428404,
        "J03WN1": 0.005788266247413132,
        "J03WOH": -0.0005398956606139094,
        "J03WOY": 0.00317049011450532,
        "J03WPY": 0.0019948574867335034
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
