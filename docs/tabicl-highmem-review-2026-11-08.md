# Higher-memory TabICLv2 admission review — November 8

Scope: read-only static inspection of committed protocol b916aca, scripts/probe_tabicl_highmem.py, imported scripts/probe_tabicl.py, and public-safe admission output. No training, inference, dataset/weight contents or restricted assets inspected by reviewer. Only this review file edited; other workers own journal/state/results.

## Hypothesis and decision
The admission hypothesis is that the unchanged matched-context CPU workload can finish two independent fits/predictions within300seconds,10GiB observed processRSS, and a3GiB system-available-memory floor, with exact probability/CSV equality. The outcome is operational completion, not spellF1. Only a passing admission could justify a separately committed scored-comparison supplement; passing would not establish football improvement or unbiased generalization.

## Static contract review
The wrapper calls the same normalized worker, selecting the other four development matches, parent stride5 indices then excludingX, with firstheldoutJ03WMX and64feature queries. It does not call a scorer or read target/sealed/PFFholdout data. The113507row count is the prior context-provenance count, conditional on unchanged split/prepared cache; this reviewer did not reopen dataset arrays or independently rehash them. Model parameters, seed, CPUthread1, one estimator, temperature1, AMP/FA3/offload/cacheOFF, H/A/D column mapping and float64 normalization remain unchanged. The checkpoint SHA256 is asserted before launching the child. Imported worker result directory is redirected correctly, preserving the old6GiB admission evidence. Previously passed synthetic probes are not rerun.

Two independent fits/predictions and exact probability/CSV assertions remain in the worker. The wrapper samples childRSS and whole-system available memory every.25seconds and terminates on any cap. It does not promise an OS-enforced hard limit or fixed memory remaining for macOS: other processes, compression and sampling overshoot can change available memory. RSS monitoring does not aggregate descendant processes, but this configuration fixes n_jobs1 and does not intentionally launch parallel child jobs. No blocking contract mismatch found in the inspected code.

## Observed outcome
Admission JSON records:

- exitcode−15 (SIGTERM), passedfalse;
- reason:3GiB system available-memory floor;
- elapsed8.738204958s;
- observed workerRSSpeak5,240,406,016bytes, approximately4.88GiB;
- minimum observed systemavailable3,103,588,352bytes, approximately2.89GiB;
- actual.log empty and no completed actual-result JSON.

This is a system-headroom admission failure. It is NOT a10GiB processRSS failure, a spellF1 rejection, or evidence that the workload completed within5GiB. The earlier6GiB probe and this attempt encountered different whole-system memory conditions; their interrupted peaks cannot be treated as model-memory measurements at completion. Actual-context repeatability and full prediction/runtime remain unmeasured. No scored standalone or blend evaluation is admissible under this failed protocol.

## Recommendation and uncertainty
Stop this attempt as preregistered; preserve production and all historical resource failures. Confidence is high in the stop decision and its operational interpretation, but low in any statement about eventual full-context memory or accuracy. Do not infer that all M3Pro18GiB machines cannot run the workload. A later retry would require changed available-memory conditions and a preregistered amendment; raising only the processRSS cap cannot solve the observed whole-system floor. The highest-value next diagnostic is label-free baseline memory availability and competing-process resource use, without model execution or closing user apps. No metric-dependent action is warranted.
