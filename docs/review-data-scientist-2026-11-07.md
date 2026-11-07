# Independent data-scientist review — November 7, 2026

Scope: committed experiment protocols, aggregate JSON results, research state and implementation code only. No restricted target assets, public labels, sealed matches, private prediction arrays or raw PFF records were read. No training, scoring, experiment rerun or production change. This review recomputed decision arithmetic from existing aggregate results; it is not a new performance experiment.

## Decision summary

Keep the current nine-core, unaugmented CatBoost + penalty16 candidate. The strongest supported result is that temporal decoding materially improves these five development matches; the current evidence does not establish target-match accuracy or unbiased provider generalization. Prioritize PFF adapter validation over another model search. Confidence is high in the recent rejection decisions' arithmetic, moderate in same-condition relative development performance, and low in external generalization until provider transfer and the later sealed evaluation exist.

I independently checked all ten match/condition cells in each recent decoder/settings comparison and recomputed paired medians and improvement counts. Rejections agree with stored gates:

| Candidate vs penalty16 | Median paired spellF1 delta | Median corrupted spellF1 delta | Paired matches improving |
|---|---:|---:|---:|
| Gap-age switching | 0.000000 | 0.000000 | 0/5 |
| Separate H/A and D costs | −0.006705 | −0.014535 | 2/5 |
| Learned duration prior | −0.007980 | −0.005646 | 0/5 |
| Nested CatBoost setting policy | −0.000306 | −0.000035 | 1/5 |

Sources: `experiments/extension-2026-11-07/decoder/*-results.json`, `settings/outer-results.json`, and penalty16 rows of `experiments/gap-augmentation/decoder-isolation.json`. Each has exactly one clean and one target-like corrupted cell per match. All 80 nested-search records exclude both outer held-out match and inner validation match from training; inner validation never equals the outer match. No split-membership leakage was found in these records.

## Concrete issues, distinguished from uncertainty

1. **Error-repair gains are not mathematical upper bounds or causal attribution.** `scripts/review_frozen.py:32` calls deterministic class-error repairs “upper bounds.” SpellF1 is non-monotone in frame corrections: the committed clean J03WPY dead/live repair gain is negative (about −0.00235). That is possible for a specific counterfactual repair, but not a supremum over permissible repairs that includes doing nothing. Rename the interpretation to “specific label-informed counterfactual repair”; keep gains non-additive and do not infer the uniquely largest causal error source from them. This changes interpretation, not measured candidate scores or promotion decisions.

2. **The rejected duration estimator treats censored spell fragments as complete durations.** `experiments/extension-2026-11-07/decoder/methods.py:19–27` records each maximal known-label run up to a half edge or X boundary as an observed endpoint. Half-terminal runs can be right-censored, and runs starting/ending beside unknown labels can be left/right censored. Treating these as ordinary exits biases hazard estimates; resetting at X also changes the measured duration population. Exact decoder optimization tests do not validate that statistical estimator. The result supports rejection of this implementation, not rejection of all duration priors. Do not reopen the stopped decoder track; document this limitation and require censor-aware estimation if such work is authorized later.

3. **Research-state mirrors lag the executed experiment history.** `research-state.yaml` still reports `total_runs: 6` and `external_performance_runs: 4`, and hypotheses remain broadly pending, despite subsequent augmentation, feature, decoder and settings experiments. This is an auditability defect rather than evidence that model scores are wrong. Reconcile a machine-readable experiment register with the dated journal; preserve historical entries.

## Statistical and evaluation caveats

- Five outer matches are five clustered observations, not hundreds of thousands of independent frame samples. Their training folds overlap. The majority/median gate is a practical engineering decision rule, not a significance test or a confidence guarantee. Do not derive frame-level confidence intervals or treat fold SD as uncertainty on target accuracy.
- Penalty16's historical promotion improved only 3/5 paired matches. Its corrupted median gain over8 was +0.017998; leave-one-match-out sensitivity medians range about +0.01052 to +0.01817. That supports the recorded gate passage but shows how little independent information exists near the new +0.01 threshold. This is descriptive sensitivity, not a new selection criterion and not grounds to change production.
- Nested setting selection correctly excludes each outer match *within this search*. Earlier feature/decoder/model choices already used all five matches, so nesting cannot retroactively make the final architecture an unbiased estimate. The current negative search result is useful restraint, not proof that the current settings are globally optimal.
- One fixed evaluation corruption realization per match makes paired comparisons fair for that realization but leaves corruption-seed sensitivity unknown. Alternating run bootstrap reproduces unconditional gaps approximately; it does not reproduce the association between visibility, stoppages, location or possession transitions. Missing fractions vary materially between matches. Existing masks should stay fixed for the authorized comparisons. Any extra corruption-seed analysis would need separate preregistration and must not become an unannounced new selection set.
- Original-versus-target-like corruption comparisons changed both missingness amount and run structure. Fewer spurious spells together with lower frame macroF1 is consistent with reduced fragmentation and longer wrong intervals; it is not an isolated causal estimate of gap duration.

## PFF admission: highest-value next work

The current block is legitimate: `experiments/pff-intake/coverage-summary.json` certifies annotation presence over delivered records, not correct labels on unique frames. All64 files have non-increasing IDs; only the first-match probe establishes that its anomalies are duplicates rather than backward steps. The probe's401 conflicting payloads are not yet split into coordinate, time and label conflicts. Do not generalize that decomposition to all64.

Before modelling, the adapter should produce an admission manifest for every match with:

- unique `(period, frame)` count and separate identical, coordinate-conflicting, timestamp-conflicting and label-conflicting groups;
- documented resolution precedence, if provider timestamps genuinely establish one; otherwise retain per-field missing/unknown status or fail the contract instead of choosing by eventual score;
- explicit CLK policy and event interval/clock consistency, without silently mixing updated standalone events and embedded tracking annotations;
- 25Hz mapping with source-time provenance, preserved missing observations, half isolation and no invented ownership through unknown intervals;
- retained and excluded frames/spells, coverage near boundaries, and missing-ball rates separately for the locked48/16 groups. Excluding ambiguous boundaries can make evaluated spells easier, so denominators must be visible.

Coordinate ambiguity need not automatically destroy a consistent teacher label: labels and observations should remain separate channels. Conversely, plausible coordinates do not resolve conflicting labels. Keep the hash split unchanged and do not replace failing matches according to performance.

After admission, the highest-value *already authorized* experiment is the fixed train-more comparison on IDSSE5, followed by descriptive frozen IDSSE→PFF16 and PFF48→IDSSE5 transfer. Never tune or select using PFF16 transfer outcomes. Report cross-provider results as provider-label agreement, not automatically equivalent possession truth. If conventions are not equivalent, that may invalidate a transfer interpretation even when the adapter is numerically correct.

## Recommendation and invalidation conditions

Expected benefit direction: trustworthy additional labels could improve robustness and reduce dependence on five-match reuse; gains are unproven and can reverse under label-convention shift. Keep the strengthened gate and production unchanged until contracts and a preregistered comparison pass. Preserve November13 freeze and November14–16 delivery-only window.

What could invalidate the favorable interpretation of the current method: undiscovered train/test overlap, a scorer/data alignment error, provider label semantics that do not match the intended possession rules, or large frozen-transfer/sealed degradation. These should trigger investigation under the existing rules, not tuning against sealed or public scores. No new architecture experiment is the immediate priority.
