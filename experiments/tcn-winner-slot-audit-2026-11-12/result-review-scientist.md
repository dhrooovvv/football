# Independent scientist review: current-winner slot stress

Reviewed November 12, 2026. Scope: saved external aggregate JSON, report, controls, determinism, cost and user-run check log only. Recomputed arithmetic and aggregate-output hashes with the standard library. No tests, imports of project/model modules, compilation, training, inference, scoring, arrays, checkpoints, CSV rows or target assets were executed or loaded by this reviewer.

## Decision-relevant result

The winning TCN is strongly sensitive to the preregistered extreme dynamic identity-churn transformation. This is a valid warning about its dependence on continuous slot history. It is not evidence that target spellF1 is approximately .05, and it does not reject the model under the development promotion gate. The appropriate next step is label-free measurement of the actual target input's continuity, duplication and coverage, followed by human review before final fitting/export. Keep the development winner and existing production pipeline unchanged in the meantime.

## Evidence and effect size

All forty match/condition/variant cells are present and unique. The saved decision records ten parent reconstructions and forty exact reload/batch CSV cases; determinism records contain all forty passing cases. The user-run log records 63 passing contracts: 35 + 4 + 2 + 5 + 8 + 9. These are correctness checks, not 63 quality comparisons.

Both controls support interpretation. Static whole-vector same-team permutation and identity-preserving velocity rederivation change zero decoded labels in all ten settings. The largest static probability difference is 6.6548e-7, within the preregistered tolerance. The largest rederivation difference is 8.1837e-6 and leaves CSV labels unchanged. Dynamic-versus-rederived metric deltas therefore equal dynamic-versus-parent deltas here; numerical rederivation alone does not explain the collapse.

| Setting | Parent mean spellF1 | Dynamic mean spellF1 | Median paired spellF1 change | Parent mean macroF1 | Dynamic mean macroF1 | Matches declining |
|---|---:|---:|---:|---:|---:|---:|
| Clean | .632871 | .052858 | −.586629 | .925900 | .369464 | 5/5 |
| Target-like corrupted | .497550 | .046667 | −.473399 | .848143 | .319705 | 5/5 |

The loss in mean spellF1 is about 91.65% clean and 90.62% corrupted, relative to each unchanged parent mean. This describes the severe synthetic intervention, not a forecast of target degradation. Across the five matches, decoded labels differ on 372,006 clean and 402,305 corrupted frames; no percentage is inferred without the corresponding valid-frame denominator.

The error type also changes materially. Clean dead/live wrong frames rise from 1,866 to 222,958; corrupted from 46,568 to 268,982. Missed spells rise from 1,044 to 2,143 clean and 1,312 to 2,166 corrupted. Spurious spells rise from 373 to 3,469 clean and 645 to 3,138 corrupted. This is a broad failure under churn, rather than an isolated small boundary displacement. A decoder-penalty adjustment is not supported by this diagnostic.

Recorded per-match diagnostic times sum to 381.293 seconds, about 6 minutes 21 seconds. This excludes the initial test phase and other unrecorded overhead; it is not peak RAM evidence.

## Strength and limits of the conclusion

Confidence is high in the descriptive statement that this particular frozen model fails under this particular joint synthetic transformation, assuming the pinned runner executed as recorded. No confidence interval or population-generalization p-value is warranted from these five reused matches with overlapping training folds. The effects are large and consistent, but the five outcomes are not independent prospective replications.

Dynamic permutation redraws each team's slot assignment every frame, recomputes velocity from the resulting false adjacent-slot history and also disrupts the temporal object convolution before pooling. It tests both mechanisms jointly. It does not identify whether velocity, pre-pooling temporal history, their interaction or another sensitivity dominates. The test preserves instantaneous team position/visibility multisets, core features and ball inputs, which rules out changed ball coordinates or changed per-frame team geometry as the direct intervention.

The target contract permits identity changes but does not specify their empirical rate. Sparse changes, disappearance/reappearance and every-frame random permutation are different distributions. Stable controls do not certify target slot continuity; extreme stress failure does not establish how close the real target is to that stress. Static permutation success also does not guarantee behavior under duplicate tracks, changed player coverage or other target noise. These uncertainties could materially change the release interpretation.

## Highest-value next qualification evidence

Prepare a separately preregistered, user-run, label-free local input audit. Report only aggregates on the authorized target and corresponding stable external inputs: adjacent jointly visible slot displacement/speed distributions in physical units, extreme-jump and encoded-velocity-clipping frequency, observation/run-length coverage and duplicate/near-duplicate track burden. A same-team frame-to-frame assignment-cost comparison can provide a continuity warning, but inferred assignments are not verified identities. Fix any thresholds and summaries in the protocol before running, preferably using documented physical scales or the external controls rather than adapting thresholds to target outcomes.

Use no target labels, public scores, manual identity annotation or target quality selection. Do not remap identities, zero velocity, change the model, reopen stopped tracks or launch another training budget as an implicit response. If actual target observations show material continuity mismatch, record a serving limitation and decide how to address the input contract explicitly; any model or representation change would require its own authorized external comparison. If mismatch appears limited, retain that uncertainty rather than claiming identity correctness and continue reviewed qualification.

Final-five fitting is artifact generation, not a remedy for the diagnosed transfer mechanism and not independent quality evidence. It can wait for this narrow input audit. The sealed matches remain sealed until the November 16 freeze, under the existing no-tuning interpretation rule. Target accuracy remains unknown.

## Provenance checked

The current `results.json`, `controls.json`, `determinism.json` and `inputs.json` byte hashes agree with their recorded decision hashes. Recomputed protocol/input registration signature agrees with the decision. Results SHA256: `90759e750d5b9638eb8c9e62ad1c75bd07b4b3cb3c3c50ba9fc6c4b8c6003081`. This review did not independently load model state or score CSV predictions; those broader artifact checks remain the root audit's responsibility.
