# Audited current-winner slot diagnostic

November 12, 2026. User-run results independently checked through saved aggregate arithmetic, logged checks, execution-commit ancestry and file-byte hashes. No model, scorer, tests, compilation or inference executed by the reviewer.

**Finding:** extreme frame-by-frame player-identity churn severely damages this frozen TCN. Controls and parent reconstruction pass. This diagnostic does not estimate target accuracy, reject the development winner or reopen a stopped quality track.

| Match | Clean parent | Clean churn | Corrupted parent | Corrupted churn |
|---|---:|---:|---:|---:|
|J03WMX|0.589806|0.049187|0.475829|0.040098|
|J03WN1|0.570609|0.045856|0.438186|0.049073|
|J03WOH|0.686197|0.035480|0.519716|0.040912|
|J03WOY|0.649812|0.052467|0.499497|0.026099|
|J03WPY|0.667930|0.081301|0.554521|0.077155|

| Setting | Parent mean spellF1 | Churn mean spellF1 | Parent macroF1 | Churn macroF1 | Median spell delta |
|---|---:|---:|---:|---:|---:|
|clean|0.632871|0.052858|0.925900|0.369464|-0.586629|
|targetlike|0.497550|0.046667|0.848143|0.319705|-0.473399|

Static same-team reordering and identity-preserving velocity recomputation changed zero decoded labels in all ten settings. Their maximum probability differences were 6.65e-07 and 8.18e-06 respectively. The rederivation control therefore rules out numerical rederivation alone as the explanation here.

Dynamic churn changes both false adjacent-slot velocity and the temporal object encoder before pooling. It preserves each frame's team geometry, core features and ball inputs. It is intentionally much more severe than an unknown real swap pattern; it does not distinguish the two disrupted mechanisms or quantify actual target identity changes.

Verified 211 registered fingerprints; 120 new private CSV hashes, 30 parent reference CSV hashes and ten checkpoint byte hashes; all forty repeatability records and ten parent reconstructions agree. User logs record 63 passing contracts. No failure artifact found. Recorded fold time 381.293s (about6m21), excluding initial checks/other overhead; no RAM measurement.

**Next step:** preregister a geometry-only local target/external structure audit with fixed descriptive summaries. Inspect continuity, coverage, encoder clipping and duplicate burden without labels or model inference. Nearest-set correspondence is a proxy, not identity truth. Review before final fitting/export; do not blindly acknowledge away the limitation. No identity repair, new training budget, target-label tuning, automatic rejection/promotion or sealed access.

Original .632870845 clean/.497549978 corrupted development scores, production configuration, promotion gate, stop counts and November16 freeze remain unchanged. Target accuracy is unknown. Separate scientist review: result-review-scientist.md.
