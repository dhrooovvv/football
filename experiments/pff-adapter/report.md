# PFF adapter first-step implementation — November7

Production unchanged; no training, scorer run, target/public labels or sealed assets.

Implemented: annotation-aware grouping by period/frame, per-observation consensus or missing, provider state/team assertions with unknown conflicts, CLKstate-neutral, VIDclears stale ownership, native frame/video-clock checks, per-half25Hz nearest observation without interpolation, past-only supported label lookup, normalized metric coordinates and roster/team mapping.

Firstpilot failedclosed on repeatedjerseys within one list. Protocol amendment1742703 committed before rerun; repeated knownjersey observations use the same consensus rule. Unknownjerseys stillfail. Stale-owner regression fixed and tested; fullpilot rerun matches observation arrays and labels exactly. Pilot10502outputs14678525Hzframes; canonical array hash in pilot.json.28tests pass. SerializedNPZcontainer-byte equality is not claimed; equality concerns arrays/labels and canonical bytes, not archive timestamps.

Important corrected diagnosis: spec2.2 documents duplicateframes for multiple associated possessionevents. Prior401mixed-payload conflicts did not mean401coordinateconflicts. Current counters are provisional consensus-missing counters (include missingness), not final separated coordinate/label classification. Full64admission and precise per-field conflict reporting remain pending. CLKneutral is a conservative non-play-state assumption, not proof of its full clock semantics; provider documentation review remains necessary before admission. No first/last/newest quality rule or average labels.

Independent reviews: docs/review-data-scientist-2026-11-07.md and docs/review-data-analyst-2026-11-07.md. Recent rejection arithmetic verified. Main weakness: nearconstantD on missing-ballframes. Repair counterfactuals are not upperbounds; rejected duration implementation mishandled censoring, not evidence against all durationpriors. Stoppedtrack staysclosed.

Next: refine per-field/conflict/time/label counters and CLKpolicy; all64strictadmission report and independent parser/schema cross-check before Track1modelling. Preserve locked48/16split and both sealedIDSSEexclusions. This pilot does not establish providercompatibility, generalization or competitionquality. FreezeNovember13 unchanged.
