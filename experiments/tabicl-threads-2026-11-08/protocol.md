# All-core equivalence test — November 8, 2026

The user explicitly approved testing all CPU cores for development scoring, while retaining single-thread verification for any winner. The M3 Pro reports 11 physical and logical cores. This protocol is committed before execution. It is conditional on the single-thread cache admission passing; its current independent refit must finish unchanged first.

Only the execution thread count changes: TabICL n_jobs and Torch intra-op threads become 11. Torch inter-op threads and NumPy/BLAS preprocessing remain one. The same pinned model, checkpoint, seed 20261106, nine features, exact 113,507-row context, 64-query and 16,384-query samples, class order, float64 row normalization and decoder 16 remain fixed. There are no memory or runtime termination thresholds. No GPU or system-setting changes.

The reference is the completed single-thread cache admission: its stored normalized probability arrays, CSV hashes, training-input hashes and dependency versions. Verify those sources and the checkpoint before running. No query labels, competition assets, public labels, sealed matches, PFF holdout or quality scores are used.

Fit a cached model with 11 threads and predict both fixed samples. Require EXACT probability equality and identical decoded CSV bytes against the single-thread references. Save and reload the locally generated cache and independently refit with 11 threads; require the same exact results for both samples. Also serve the all-core-fitted cache with one thread and require exact results. Record actual thread counts, timings, model hashes and all failures. Cached arrays and pickles stay under ignored data/.

If any exact check fails, reject the threading optimization, retain the admitted single-thread model configuration, and do not search other thread counts or relax tolerances. This is a computational check, not an accuracy rejection. If it passes, separately commit the amended scored protocol, runner and input/code hashes BEFORE any quality scoring. The amended runner may use 11 threads for initial development inference but must use one thread for required winner verification, with exact probabilities and CSVs against the scored outputs. No production switch follows from this test.

The fixed standalone and 50/50 blend candidates, original five match splits, seeds, CatBoost budget, corruption, scorer, promotion gate and metric stop rule remain unchanged. November 13 freeze and November 14–16 delivery remain unchanged. No publication of data, external submission or hosted inference.
