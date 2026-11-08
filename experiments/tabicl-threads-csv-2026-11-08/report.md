# Findings from completed checks — November 8, 2026

No experiment restarted for this review. No spellF1 or macroF1 comparison was executed, so there is no demonstrated accuracy improvement over production.

The M3 Pro with18GiB completed the full113507-row context with64queries twice on one CPU thread; probabilities and CSV bytes were exact. Cached single-thread inference also passed independent refit and reload checks at64 and16384queries. The completed single-thread cache is5592640506bytes.

The later11-core CSV-based test completed its first fit and BOTH64/16384-query predictions before disk exhaustion. Both CSVs exactly matched their single-thread references. Probability vectors were not bit-identical: max differences1.478210944e-5 and6.521959831e-5 respectively. This establishes output equality only for these fixtures, not arbitrary inputs or completed11-core repeatability.

| Operation | Earlier one-thread run | Eleven-thread run |
|---|---:|---:|
| Context/cache fit |1024.517s|357.594s|
|16384-query prediction|144.788s|49.183s|

These observations suggest about3x speed for these operations, not a controlled benchmark or a measured end-to-end evaluation speedup. The first strict probability-threshold experiment remains failed and is not retroactively passed.

The CSV-based procedure then failed saving its cache with OSError28, before reload/refit proofs. Therefore threading admission is incomplete/failed; no quality scoring or promotion followed. The incomplete4496723968-byte cache was removed at stop, freeing space; completed evidence and original inputs remain. Production remains nine masked core features, unaugmented CatBoost and Viterbi penalty16. Target accuracy remains unknown. User stop remains in force.

Evidence: checks.json/cost.json/admission.json in this directory; prior uncapped/cache reports. Full five-match clean/corrupted comparison, blend performance and full11-core repeatability remain untested.
