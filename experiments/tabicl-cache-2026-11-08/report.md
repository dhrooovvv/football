# Cache-correctness admission — November 8, 2026

**Passed the preregistered checks. No quality score or production promotion.**

Synthetic contexts of 1,000 and 10,000 rows produced zero maximum probability difference between cached and uncached predictions, with identical decoded CSVs. Cached reload and independent refit predictions also matched exactly.

For the actual 113,507-row context, the cached 64-frame CSV matched the uncapped reference. Full uncached/cached probability equality was not tested because the earlier worker did not persist its probability arrays. For both 64 and 16,384 queries, cached reload and independent cached refit produced EXACT probabilities and CSV bytes. No arbitrary query-chunk invariance is claimed.

The actual-case procedure took 2,540.665 seconds, including two cache fits, prediction checks, save/load and hashing. This is not a single-fit latency. The saved cache is 5,592,640,506 bytes; it includes external training context and stays under ignored data/.

| Observed operation | Seconds |
|---|---:|
| First full-context cache fit | 1024.517 |
| First cached 64-query prediction | 2.509 |
| First cached 16,384-query prediction | 144.788 |
| Reloaded cached 16,384-query prediction | 216.330 |
| Independent cache refit | 986.575 |
| Refitted cached 16,384-query prediction | 139.952 |

These are descriptive timings from these runs, not a controlled speed benchmark. The resource observer started after the first synthetic pass and may omit earlier peaks: observed process peak 9,674,309,632 bytes and minimum system-available memory 2,803,515,392 bytes. There were no resource termination thresholds. RSS excludes total system, compression and swap costs.

Evidence: admission.json, actual.json, synthetic/repeatability JSONs, provenance.json, resources.json and execution.log. The independent review is docs/tabicl-cache-review-2026-11-08.md. Weights, inputs, seeds, classes and CPU settings stayed fixed. No query labels, competition assets, public labels, sealed matches, PFF holdout, hosted inference or submission were used. Production remains unchanged; target accuracy is unknown.

The user next approved testing all 11 CPU cores for development scoring, retaining single-thread winner verification. That separate preregistered computational test must pass before changing scored execution. The two fixed candidate arms, ten cases and metric gate remain unchanged. The November 13 freeze remains unchanged.
