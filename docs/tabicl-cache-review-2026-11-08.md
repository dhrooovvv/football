# Independent cache-admission review — November 8

Scope: read-only inspection of `scripts/probe_tabicl_cache.py`, committed cache protocol915d198 and aggregate JSON. No model runs, arrays, query labels, target/sealed/PFFholdout assets or process interruption. This reviewer edits only this document. This is computational correctness/admission review, not possession-quality review.

## Protocol and implementation
No blocking mismatch identified. Execution requires completed uncapped exact-repeatability admission, exact committed protocol bytes, pinned local weight SHA and original ordered five development IDs. Dependency versions must match uncapped admission. CPUthread1, deterministic algorithms, seed, oneestimator, temperature1 and noAMP/FA3/offload settings are preserved. The explicit prospective change is `kv_cache=False` to `True`, with fixed query count16384, not an unlogged quality-driven model choice. No resource-kill caps, metric evaluation, hidden class rebalancing, context reduction or extra-match training appears.

Synthetic1000/10000 checks use the same fixedseed/data construction with missing values; they compare reordered float64normalized H/A/D probabilities under the preregistered maxabs<=1e-6 AND allclose tolerance, plus exact decoder16CSV equality. Cached reload and independent refit require exact probabilities and CSV equality. No tolerance adaptation is coded.

Actual context source hashes and113507rows are checked against prior provenance. Heldout features/halfblocks are read without query labels. Full64cacheCSV is compared to prioruncapped64CSV; this is explicitly a CSV-only cross-mode check because the earlier uncached worker did not save raw probabilities. Fixed16384cached serving then requires exact reload/refit probabilities and decodedCSV bytes. Pickles contain training context/cache, so their files remain in ignoreddata and loading is confined to newly generated local files. Dependency/provenance records and streamed pickle hashes support traceability without publishing caches.

## Current aggregate evidence (partial)
- Uncapped admission completed: exit0,2495.184swall; two fits/probabilities and decodedCSVexact. This establishes tested113507context/64query completion/repeatability, not full-match speed or accuracy.
- Synthetic1000 and10000 cached-vsuncached maxabsprobabilitydelta0.0 and identicalCSV hashes. Protocol numeric/CSV equivalence gates pass in these cases.
- Full113507context cached64CSV hash matches uncapped64 (`283eba25193476a39c0e5a9a29b81eeb6093c2dfad911d24c0f601fa7eb167a2`). Full numeric cross-mode identity is NOT established.
- At inspection, actual-repeatability.json records only reload64 exact probabilities/CSV. Reload16384 and independent cached refit64/16384 remain pending; there is no final cache admission conclusion in this partial review.

No spellF1 or target quality evidence exists. The64vs16384prefix probability identity is not explicitly asserted; do not claim arbitrary query-chunk invariance. The serving protocol can still be a valid fixed16384numerical candidate if its own repeatability gate passes. Cache equivalence on syntheticcases and64CSV is not proof of full-match uncached/cached numerical equivalence or unchanged accuracy.

Recommendation: keep waiting for mandatory actual reload/refit checks; do not start scoring while the admission is incomplete. If all pass, use only the separately committed scored supplement and unchanged promotion rules. If any fails, report a numerical/operational failure without treating it as a metric rejection. Production remains unchanged.

## Final aggregate gate audit (supersedes pending-status observations above)
Final `actual.json`, `actual-repeatability.json` and `admission.json` now exist. All four required actualcached checks pass: reload64, reload16384, independentrefit64 and independentrefit16384 each report exact probabilities and identical CSV bytes to their initial cached reference. Both syntheticcontexts also pass independentrefit/reload exactness and cached/uncached numeric/CSV gates. AdmissionJSON correctly reports passed=true, fixed16384queryrows,113507contextrows, no quality scored and no production change. Actualadmissiontotal2540.665s (~42.344min) includes multiple fit/predict/save/reload operations; do not report it as one fit or one query cost. Savedcontext/cachemetadata reports5,592,640,506bytes; artifact remains underignoreddata.

Final recommendation: computational admission passes its preregistered requirements. A separately committed fixed scored supplement may proceed under the existing authorization and gates. This is not full-match repeatability proof, full uncached/cached numeric equivalence, arbitrarychunkinvariance or any possession-accuracy result. No model or source change made by this reviewer; only aggregate files read.
