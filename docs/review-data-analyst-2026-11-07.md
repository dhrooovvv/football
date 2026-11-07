# Independent data-analyst review — November 7, 2026

Scope: committed experiment aggregates and implementation only. No competition assets, public-label rows, sealed data, new training or performance experiments were accessed. This review does not change production, gates, splits or the November 13 freeze. Existing results were recomputed arithmetically from stored per-match numbers.

## Decision

Keep the current nine-core, unaugmented CatBoost + penalty16 candidate. The recorded promotions/rejections checked below agree with their applicable gates. Prioritize PFF adapter correctness, then the already-authorized train-more comparison and descriptive transfer evaluation. More optimization against the original five matches has weak independent evidential value.

## Findings

### 1. Missing-ball behavior is almost constant dead, not merely a modest quality decline — high confidence

The committed `experiments/whole-pitch/parent-results.json` reports the penalty16 parent's dead/live confusion metrics on **graded frames with ball_observed=0**. D recall is exactly 1.0 for all five target-like-corrupted development matches. Combining the reported D precision/recall, error count and subset size gives:

| Match | Missing-ball frames | Implied fraction predicted D | Implied live recall |
|---|---:|---:|---:|
| J03WMX | 52,145 | 99.9597% | 0.0634% |
| J03WN1 | 56,720 | 99.9753% | 0.0521% |
| J03WOH | 65,199 | 99.9923% | 0.0147% |
| J03WOY | 60,389 | 99.9487% | 0.0927% |
| J03WPY | 52,490 | 99.9467% | 0.1010% |

These figures are algebraic reconstructions, not a new score: TP = errors / (1/precision + 1/recall − 2), predicted-D = TP/precision; live recall uses the resulting TN/live support. Small numerical rounding is possible. The source metrics have full floating precision. Binary macroF1 is only about .268–.345. D recall alone would give a misleadingly positive account.

**Interpretation:** the current model/decoder almost always defaults to dead during artificially missing-ball intervals. This strongly explains a large part of missing-frame error, but does not isolate emissions from decoder or prove why the model learned that response. Clean external data have no missing-ball frames, so their missing-ball metrics are undefined, not zero and not evidence of robust live-gap handling.

**Action:** in future already-authorized reports, include missing-frame confusion counts, live recall, D precision/recall and predicted-D share alongside macroF1. Do not rebalance to target/public summaries or alter the current candidate on this observation. PFF can test whether naturally missing broadcast observations provide compatible live examples, once the adapter is valid.

### 2. Promotion arithmetic supports the recorded decisions — high confidence

Per-match gate inputs are arithmetic means of clean and corrupted spellF1/macroF1. Across matches, the gate takes the median paired delta and counts positive spell deltas. This is not the same as a difference in overall means.

| Comparison | Median paired spell delta | Improved matches | Median paired macro delta | Median corrupted spell delta | Recorded decision |
|---|---:|---:|---:|---:|---|
| Augmentation8 vs unaugmented8 | +.003268 | 4/5 | −.001228 | +.001957 | Historically passed original gate; later dropped |
| Penalty16 vs penalty8 | +.010056 | 3/5 | +.006132 | +.017998 | Keep16 |
| Augmentation16 vs unaugmented16 | −.001331 | 2/5 | −.000708 | +.000119 | Reject |
| Rolling whole-pitch bundle vs16 | −.006600 | 1/5 | +.000476 | −.005208 | Reject both required gates |
| Nested CatBoost setting policy vs16 | −.000306 | 1/5 | −.000703 | −.000035 | Reject |

Sources: `gap-augmentation/gates.json`, `combined16/gate.json`, `whole-pitch/gate.json`, `extension-2026-11-07/settings/gate.json`. Historical augmentation8 was evaluated before the global +.01 minimum was applied; its passing historical record should not be relabelled a protocol violation. It is not an active retained branch now. Penalty16 would also meet today's +.01 corrupted minimum against penalty8.

One useful example: the nested setting policy's mean corrupted spellF1 rises from .323476 to .324172, yet its paired corrupted median is negative and the clean/corrupted paired gate improves only one match. Rejecting it correctly avoids being fooled by the top-line mean. The nested outer corrupted fold SD (.012502) describes five-match dispersion; it is not an independent confidence interval.

### 3. Original versus target-like corruption is a changed population, not a fair version comparison — high confidence

`gap-augmentation/fidelity.json` shows original graded missing-ball rates of 25.98–28.08% and target-like rates of 35.72–47.52%, against a target observed aggregate of 40.69%. Mean values alone would hide the fold-to-fold difference. Longer gap durations, a different missing fraction and changed realized overlap with play all vary simultaneously.

The reported higher spellF1 but lower macroF1 under target-like corruption is consistent with removing many short predicted fragments while erasing more live frames. It is not a proved causal explanation because these factors were not isolated. The recorded spurious-spell reduction supports the mechanism, but does not identify its unique cause. Do not compare an old-corruption candidate to a new-corruption parent for promotion. Current comparisons correctly use identical fixed masks within each pair.

The empirical model matches unconditional observed/missing runs, not conditional camera coverage or play state. It is a stress test, not proof of realistic target noise. Preserve those fixed masks for current gates rather than searching new seeds; characterize natural PFF missingness separately.

### 4. Current selection is clear, but the state mirrors can mislead future work — high confidence

`experiments/core-development/selection.json` correctly selects penalty16, disables augmentation, and sets execution_thread_count1. However:

- `research-state.yaml` still says total_runs6 and external_performance_runs4 despite subsequent augmentation, combined, whole-pitch, decoder and nested-settings comparisons.
- `baseline_value` remains null; `best_value` is an undocumented scalar mixing clean/corrupted means. The selected mean .420565 is interpretable only with its exact corruption model and aggregation definition.
- Global consecutive_rejections2 coexists with decoder failures3 and settings failures1. Per-track values are present, but consumers must not interpret the global field as the active decoder counter.
- Selection stop_reason still refers to the older feature-stop, superseded by the authorized extension; extension_rejections and later journal entries supply the correction.
- Extension track remains data_access_pending even though PFF files arrived and the actual blocker is adapter validity.
- Hypothesis flags still say pending despite later temporal-decoding and corruption results. Some hypotheses were never directly tested, so they should be marked scoped/deferred rather than casually declared confirmed.

**Action:** rebuild a compact current-status index from experiment manifests and date the gate version, parent, corruption fingerprint and metric definition for each comparison. Preserve historical journal entries; update only current mirrors. A future process should not have to infer the latest state from multiple append-only narratives.

### 5. PFF annotation presence is not validated unique-frame label coverage — high confidence

`pff-intake/coverage-summary.json` counts 11,707,598 delivered standard-time records with provisional H/A/D state presence. Every file has non-increasing frame IDs; the deeper first-match probe reports 849 duplicate keys and 401 conflicting selected payloads. CLK semantics remain unresolved. Consequently 100% provisional annotation presence is not 100% usable unique 25 Hz supervision.

Do not admit matches or choose a duplicate precedence rule from downstream spellF1. Before modelling, separate coordinate conflicts from ownership/state conflicts, identify authoritative update timestamps if documented, and report unique-frame/time coverage after deduplication and resampling. For unresolved labels preserve X/unknown or fail the contract; do not turn absence/conflict into D. The prospective 48/16 split must remain fixed, with exclusions explained without performance-driven replacement.

## Ranked likely drivers and uncertainty

1. **Near-constant D output in missing-ball frames:** directly supported by confusion metrics; high impact and high confidence as a measured failure mode. Causal allocation between learned emissions and temporal decoding remains uncertain.
2. **Provider/label convention and observation differences:** plausible major transfer risk; external class shares/durations and continuous clean observations differ. Not yet a proved convention mismatch, and no cross-provider performance exists.
3. **Five-match historical reuse:** certain evidence limitation. Nested inner/outer selection avoids direct outer-label tuning within the settings experiment but cannot erase prior reuse or provider correlation.
4. **PFF duplicate/clock semantics:** directly demonstrated ingestion risk; its eventual performance impact is not measured. Fixing it is a prerequisite, not a promotion result.

## Immediate next slice

Complete an all-64, non-performance adapter-admission table: native records → unique frame keys → identical duplicates → coordinate-only conflicts → state/owner conflicts → documented timestamp precedence → valid 25 Hz observations → known/unknown labels, separately by half and missing-ball status. Compare native event-label provenance at boundaries, including CLK/VID and duplicate conflicts. Keep row contents local; publish aggregate counts, hashes and tests only.

After that contract passes, run the already-authorized train-more gate and cross-provider transfer diagnostics. Do not reopen failed feature/decoder searches or use the transfer holdout as a tuning leaderboard. Target accuracy and sealed generalization remain unknown.
