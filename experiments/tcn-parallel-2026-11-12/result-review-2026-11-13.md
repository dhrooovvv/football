# Completed attention and seed-ensemble review — November 13, 2026

Both authorized user-run arms completed ten cases across five held-out matches, with two exact 40k fits per fold. Each checks log records 68 passing contracts. Saved repeated-training, both-view reload and reload/batch4 CSV equality proofs pass. Reviewer uses stdlib arithmetic/metadata and byte hashing only: 228 registration fingerprints, 151 committed code entries, 35 training-compact members and all checkpoint/prediction/result/log fingerprints checked, 378 unique files total. Different completion Git HEADs include the intervening documentation commit; the locked sources and common registration signature are unchanged. This audit does not independently replay training or scoring.

## Ordered decision

Attention is compared first with the frozen parent and rejected. Ensemble is therefore compared with that same parent and rejected. Retain staged40k original-motion TCN + original/180 probability averaging + penalty16 as the eligible development winner. Production CatBoost and the existing private TCN artifact remain unchanged. No attention-plus-ensemble mixture was tested. The official --finalize command has NOT been executed; the ordered conclusion here is independently computed from saved aggregates, not a claim that ordered-decision.json exists.

| Measure | Parent | Attention | Ensemble |
|---|---:|---:|---:|
| Mean clean spellF1 | .632870845 | .631785195 | .633872006 |
| Mean corrupted spellF1 | .497549978 | .493400419 | .506191099 |
| Mean clean macroF1 | .925899545 | .924987520 | .925171920 |
| Mean corrupted macroF1 | .848142823 | .828407615 | .854009568 |
| Median corrupted spellF1 change | — | -.000205388 | +.007730567 |
| Median paired spellF1 change | — | +.004189586 | +.007742859 |
| Paired spellF1 match wins | — | 3/5 | 3/5 |
| Median paired macroF1 change | — | -.010357389 | +.002279352 |

Attention fails the +.01 corrupted median improvement and the no-worse-than-.01 paired macro guardrail. Ensemble passes the earlier gate but fails the additional +.01 corrupted median threshold. Do not lower the threshold after seeing this near miss or promote by favorable means. Ensemble has the highest observed mean of these three but is not an eligible promoted best.

## Per-match results

| Match | Setting | Parent spell / macro | Attention spell / macro | Ensemble spell / macro |
|---|---|---:|---:|---:|
| J03WMX | clean | 0.589806 / 0.932604 | 0.594921 / 0.929533 | 0.597561 / 0.934497 |
| J03WMX | targetlike | 0.475829 / 0.873619 | 0.465049 / 0.848780 | 0.483560 / 0.878624 |
| J03WN1 | clean | 0.570609 / 0.898676 | 0.584690 / 0.904283 | 0.573191 / 0.898726 |
| J03WN1 | targetlike | 0.438186 / 0.811443 | 0.437981 / 0.785121 | 0.428434 / 0.808180 |
| J03WOH | clean | 0.686197 / 0.937640 | 0.686364 / 0.935591 | 0.708571 / 0.937801 |
| J03WOH | targetlike | 0.519716 / 0.854898 | 0.530191 / 0.848184 | 0.540146 / 0.859262 |
| J03WOY | clean | 0.649812 / 0.923844 | 0.650310 / 0.926618 | 0.648811 / 0.922626 |
| J03WOY | targetlike | 0.499497 / 0.825637 | 0.507379 / 0.816442 | 0.516624 / 0.839782 |
| J03WPY | clean | 0.667930 / 0.936735 | 0.642641 / 0.928914 | 0.641226 / 0.932210 |
| J03WPY | targetlike | 0.554521 / 0.875117 | 0.526402 / 0.843511 | 0.562192 / 0.884201 |

## Error interpretation

Counts below are aggregate diagnostics at IoU .5; they are not the complete five-threshold official metric. On corrupted data, parent/attention/ensemble missed spells are 1312/1333/1308, spurious spells 645/605/564, and recalled short spells approximately 104/103/100 out of 732 (counts recovered from recorded per-match recall ratios). Dead/live wrong frames are 46568/63730/42828. Attention did not fix missing-ball robustness. Ensemble's improvement is consistent with suppressing extra spells, while missed and short-spell recall remain largely unresolved; this is diagnostic association, not a causal proof. On clean data missed spells are 1044/1043/1046, spurious 373/351/346 and recalled short spells 150/159/151. No claim that short-spell improvement alone guarantees spellF1.

Sum of recorded fold durations: attention 52967.832 seconds (~14h42m48s); ensemble 11241.303 (~3h07m21s). These exclude some setup and do not establish total concurrent wall time, exclusive CPU time or peak RAM. Attention was about 4.71 times the ensemble arm by this timing measure despite a small parameter increment.

## Next steps and limits

This finishes the two-candidate exception. Record both failures and stop these fixed alternatives; no unregistered seed/weight/attention sweep. Preserve prior stop histories, full gate, sealed matches and November16 freeze. Neither failure proves a TCN ceiling. Any next quality experiment needs a distinct error-targeted mechanism and separate authorization/preregistration; do not automatically begin another long run. Existing candidate clean-environment/fresh-clone qualification and once-only protected evaluation remain delivery work. Five repeatedly reused development matches are not independent generalization evidence; target accuracy remains unknown. No target/public-label selection, sealed access, model fitting, tests, inference, scorer execution, source change, download, publication, submission or push occurred in this review.
