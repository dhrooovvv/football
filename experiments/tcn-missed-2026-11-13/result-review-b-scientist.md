# Independent saved-result review: Trial B — November 13, 2026

Verdict: Trial B qualifies under the exact registered version2 median-based gate, conditional on root provenance and byte audit. It must not be described as increasing mean corrupted spellF1: that mean regresses. Preserve Trial A and its higher corrupted mean as a distinct existing artifact; no post-hoc gate change, combined candidate, coefficient rescue or additional experiment follows.

## Arithmetic and selection meaning

The ten saved aggregate cells independently reproduce the recorded gate:

- Median corrupted spellF1 change: +0.0019622504340451874 (>0).
- Median paired clean/corrupted spellF1 change: +0.0049762962702910585 (>0).
- Paired improvements: 3/5 (WN1, WOH, WPY).
- Median paired macroF1 change: +0.00240322704069329 (>=-0.01).
- Ten fit proofs report40k steps, exact repeats, the same B trial signature and the other-four training memberships. One referenced checks log reports91tests across seven successful suites. These are saved user execution records, not independently replayed tests.

B's median corrupted gain is +0.1962percentage points, while its mean corrupted change is -0.3661points. Three corrupted match gains coexist with two regressions; WMX's -3.5910point regression is larger than the total positive changes. The gate was intentionally chosen to favour a majority/median pattern, so this outcome is not an arithmetic contradiction or permission to substitute a new mean-based acceptance rule after seeing results. However, numerical honesty requires reporting both measures. A provisional gate-selected B candidate is not proven to have better expected match performance than A.

## Mean metrics

|Setting|A spellF1|B spellF1|A macroF1|B macroF1|
|---|---:|---:|---:|---:|
|Clean|.645261041|.650384708|.924253358|.926751542|
|Target-like corrupted|.513496193|.509835640|.843502465|.837980557|

B also has sizeable individual paired macro regressions on WMX(-.012389998) and WOH(-.017099901), although its declared median macro guard passes. Corrupted macroF1 falls from .860079 to .821960 on WOH. These regressions cannot be hidden by the majority wins or clean mean improvement.

## Dominant-error diagnosis

Counts below use IoU0.5, not the full official five-threshold metric.

|Setting|Missed A→B|Spurious A→B|Recalled short spells A→B|Dead/live wrong frames A→B|
|---|---:|---:|---:|---:|
|Clean|972→953|463→451|189→198 of732|2386→2315|
|Corrupted|1268→1278|647→658|124→133 of732|50889→54752|

Short recall improves25.82%→27.05% clean and16.94%→18.17% corrupted, with integer recalled counts reconstructed from saved per-match short-spell ratios. Under corruption, this narrow short-spell improvement does not translate to fewer total missed spells: the model loses other possessions and adds more extra spells. Missing-ball D-F1 deteriorates markedly on WMX(.8449→.7839) and WOH(.8419→.7075), while improving on the other three matches. These changes are consistent with uneven robustness rather than a general correction of the remaining error mechanism. They are diagnostics, not a causal decomposition of official spellF1.

All ten fit summaries show a nonzero auxiliary loss (mean segment soft-IoU loss roughly .521–.547) and roughly9.63–9.98complete segments per minibatch. The new objective therefore received supervision; this is not evidence that its training loss predicts validation quality. Root owns hashes, checkpoint/prediction proof validation and detailed source binding checks.

## Recommendation and limits

Record B as passing the registered median gate, preserve A as the higher-mean-corrupted candidate, and clearly distinguish both from the original production pipeline. Stop the two-trial extension here. Do not silently tune the coefficient, change the sampler, blend A and B or use sealed scores to select whichever result looks best. Final independent evaluation must follow the already written frozen-candidate interpretation rule; the repeatedly reused five development matches remain selection-biased evidence and target accuracy is unknown.

Review used stdlib arithmetic and saved aggregate JSON/checks text only. No project imports, model or array deserialization, CSV rows, tests, training, inference or scorer executions; no target/public/sealed labels inspected. This document changes no sources or acceptance rule.
