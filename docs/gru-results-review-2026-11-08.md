# Independent GRU result review — November 8, 2026

Scope: AGENTS.md and project memories; experiments/gru-2026-11-08/{results,parent,gate,determinism,cost,protocol}.json/md; legacy penalty16 aggregates in experiments/gap-augmentation/decoder-isolation.json. Only aggregate files and the preregistered protocol were read. No raw data, PFF holdout files, target/public labels, sealed matches, prediction arrays, model files, training or scorer execution were used. This arithmetic review is not a new performance experiment. I edited only this document and made no commits.

## Decision

**Reject this fixed GRU blend and retain the unaugmented nine-core CatBoost+penalty16 production candidate. No decision-changing arithmetic issue found.** Determinism passes the recorded operational checks, but predictive quality fails both required spellF1 conditions. No extra blend, epoch, window or hidden-size search is justified by this result; it tests one bounded configuration, not all sequence models.

Completeness checks:10candidate cells,10matched parent cells and10determinism cells cover exactly the same five matches × clean/target-like conditions. There are five initial-fit cost records. I independently recomputed all15 per-match deltas and checked them against gate.json within1e-12.

| Gate component | Independently recomputed result | Required | Outcome |
|---|---:|---|---|
| Median paired spellF1 change | −.008147538 | >0 | Fail |
| Positive paired spell changes | 1/5 | ≥3/5 | Fail |
| Median paired macroF1 change | +.000052442 | ≥−.01 | Pass |
| Median target-like corrupted spellF1 change | −.007520197 | ≥+.01 | Fail |
| Stored production tests | Pass | Pass | Recorded pass; not rerun here |
| Recorded deterministic checks | All10case flags pass | All pass | Recorded pass; not rerun here |

Two of five corrupted-only spell deltas are positive, but that does not satisfy the majority paired gate or the minimum median corrupted gain. Overall average macroF1 improves slightly while spellF1 worsens; it would be wrong to use that small frame-level gain to override the ranking metric or prespecified gate.

## Headline scores and fold variation

Equal weight per match; SD is the sample SD over five matches, not a confidence interval.

| Model | Condition | Mean spellF1 | Mean macroF1 | SpellF1 SD |
|---|---|---:|---:|---:|
| Parent penalty16 | clean | .517654 | .895099 | .031366 |
| Parent penalty16 | target-like | .323476 | .679401 | .012640 |
| Fixed GRU blend | clean | .504499 | .895223 | .039395 |
| Fixed GRU blend | target-like | .317274 | .680278 | .017940 |

| Match | Paired spell delta | Paired macro delta | Corrupted spell delta |
|---|---:|---:|---:|
| J03WMX | −.018115 | −.000435 | −.012831 |
| J03WN1 | −.008074 | +.000559 | +.001781 |
| J03WOH | +.001107 | +.002742 | +.002559 |
| J03WOY | −.015165 | −.000416 | −.015001 |
| J03WPY | −.008148 | +.000052 | −.007520 |

Parent half-only decoding and legacy penalty16 decoding agree **exactly** on every match/condition spellF1 and macroF1 value: maximum absolute difference0 for both metrics. Thus the inference-block policy change is not an active explanation of this run's score difference. The protocol still correctly makes inference independent of true-label reset points.

## Determinism and cost: what is and is not established

All10records report repeated_training_equal, reload_probabilities_equal and csv_bytes_equal_reload_batch4 as true. This supports the tested same-version, same-CPU software contract for external development inference, including saved/reloaded models and the extra batch4 check. It is not a fresh-environment, cross-hardware, cross-release or target-game CSV reproduction claim. No target run is needed to reject this candidate.

The five initial fits sum to24.385491 recorded seconds. Each used200updates, batch8,250input frames and200retained loss frames. That time excludes repeated-training checks, model loading, inference, validation and setup; do not label it end-to-end experiment cost. CatBoost parent budget is unchanged, while the GRU adds compute, so this is not a compute-matched architecture comparison. Falling training losses do not establish generalization or justify extending the fixed budget after seeing the rejection.

## Missing-ball behavior and uncertainty

Across286943corrupted missing-ball frames, pooling the aggregate confusion counts gives:

| Model | Predicted-D share | Live recall |
|---|---:|---:|
| Parent | 99.9655% | .0638% |
| Fixed blend | 99.9460% | .0999% |

These are explicitly frame-weighted diagnostics, not the equal-match gate inputs. The tiny movement does not fix the near-constant-dead failure mode, and no causal allocation between emissions, blend, decoder, training distribution or window length follows from it.

The protocol already identified two important limitations before results: clean IDSSE training has no ball gaps, so corrupted mask/gap inputs remain out of distribution; and the fixed10-second input window cannot see an observed endpoint in some long-gap interiors. Both fit the observed weak missing-live recovery as plausible mechanisms, not proven causes. One rejected short-budget setting does not rule out sequence modelling in general. Historical reuse of these five matches continues to limit independent generalization claims; no statistical significance or target accuracy is established.

## Immediate recommendation

Keep production unchanged, archive the candidate and preserve the fixed one-model stop. Record that deterministic execution succeeded while quality failed. Do not reopen stopped tracks or use transfer/target/public/sealed results to rescue this configuration. Remaining work should follow the frozen-candidate review and scheduled November13 evaluation/delivery rules; any future research would require explicit scope and a committed protocol, not an implicit extension of this rejected trial.
