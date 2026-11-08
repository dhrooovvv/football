# Manual reduced-context quality screen — November 8, 2026

Prepared at the user's request for self-service execution; preparation does not start training or inference. This is a new candidate configuration and does not revise prior failed tests.

Use fixed30,000 training-context rows per fold, drawn uniformly without replacement using NumPy default_rng(seed20261106) from the pooled original parent stride-five, non-X rows of the other four matches. Sort selected indices; record their hash and save them under ignored data/. No class rebalancing or seed/sample search. Preprocessing is fitted only on that subset. Original frozen full-data CatBoost remains the release reference; this is a practical configuration comparison, not a controlled equal-training-volume model comparison.

Same pinned TabICL2.2.0 weights/environment and nine core features; cached CPU inference, n_jobs11/intra11, interop1, BLAS preprocessing1, one estimator, temperature1, noAMP/FA3/offload. No custom memory/runtime caps. Do not serialize model caches during screening: retain probabilities/CSV/hash/index evidence, release each fold's in-memory model after both conditions. This avoids the earlier large-cache disk failure.

Evaluate ALL five original development matches at25Hz, clean and existing fixed target-like corruption. Full timelines/half-only decoder16 and unchanged scorer remain intact. No evaluation-frame subsampling, query chunk decoder resets or changes to corruption. Fixed16,384 query chunks. Input/source/scorer/checkpoint hashes are verified. No target/public labels, sealed matches, PFF holdout or hosted inference.

Two fixed outputs: TabICL alone and normalized50/50 frozen full-data CatBoost+TabICL probabilities, decoder16. Compare standalone to parent; compare blend to standalone if standalone is quality-eligible, otherwise parent. Also report blend versus original parent. Same existing positive paired median spell improvement/majority of five/median macro drop no greater than.01, PLUS corrupted median spell gain at least.01, required tests. No weight/temperature/feature search.

QUALITY SCREEN ONLY: passing those numeric gates is provisional, not promotion. This script does NOT perform full single-thread verification, production integration, target validation or clean-environment reproduction. It must never switch production or claim development-promotable. A separate committed verification protocol is required for any eligible result. Original reference and all per-match numbers/failures are reported. If both fixed arms fail, stop this bounded screen; no automatic new samples or seeds. Stop rule and November13 freeze/14–16 delivery remain unchanged.

The CLI appends an outcome pointer to ball.md and writes a readable report. Refuse overwriting prior result JSON. A user may interrupt with Ctrl+C. No external submission or publication of arrays/CSV/cache artifacts.

Only scientific change versus the completed10,000-row screen: context cap30,000. Same seed and uniform sampling algorithm; sampling is not asserted nested. Separate runner/output directories preserve previous evidence. This is one bounded follow-up, not a context-size search. Both arms failing closes this follow-up. User will execute manually. No model execution during preparation.
