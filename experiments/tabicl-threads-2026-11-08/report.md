# Eleven-core numerical-equivalence test — November 8

**Failed its registered cross-thread probability criterion.** The first 11-core cache fit took332.785 seconds versus the historical single-thread first fit1024.517 seconds (about3.08 times faster in these uncontrolled observations). Its64-query CSV matched the single-thread CSV exactly, but maximum probability difference was0.000014782109443833846, exceeding the registered0.000001 maximum.

The procedure stopped after that first64-query check. No16,384-query test, cache reload, independent11-core refit, within-mode repeatability conclusion, quality score or production promotion occurred. This is not evidence that repeated11-core execution is nondeterministic; only cross-mode differences were observed. No alternate thread counts or numeric tolerances were searched. Original failure and locked inputs are preserved. The later generalized helper can be recovered in its original form at commita6fb691 for this test's source snapshot.

After reviewing this result, the user explicitly approved a separate CSV-based cross-core check on the full16,384-query fixture, exact within-mode repeatability, and single-thread verification before promotion. That new endpoint is registered in a separate directory; this failed numerical test remains failed. No metric gate is relaxed and no quality outcomes have been observed.
