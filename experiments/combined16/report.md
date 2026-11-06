# Combined augmentation16 decision and label-free diagnostic

**Reject augmentation; keep unaugmented penalty16.** Gate:2/5 matches improve, median paired spellF1 delta-.001331, macroF1-.000708. Primary corrupted median delta+.000119 does not override the unchanged gate.23 tests pass.

| Match | Condition | Parent spellF1 | Combined spellF1 | Parent macroF1 | Combined macroF1 |
|---|---|---:|---:|---:|---:|
| J03WMX | clean | 0.501360 | 0.488557 | 0.907574 | 0.905297 |
| J03WMX | targetlike | 0.323426 | 0.323544 | 0.692742 | 0.697768 |
| J03WN1 | clean | 0.484682 | 0.478500 | 0.875014 | 0.872922 |
| J03WN1 | targetlike | 0.313253 | 0.320537 | 0.680025 | 0.690129 |
| J03WOH | clean | 0.568452 | 0.568915 | 0.903698 | 0.905187 |
| J03WOH | targetlike | 0.343671 | 0.352305 | 0.646450 | 0.643546 |
| J03WOY | clean | 0.516129 | 0.511568 | 0.885072 | 0.883676 |
| J03WOY | targetlike | 0.312291 | 0.310799 | 0.663388 | 0.658861 |
| J03WPY | clean | 0.517647 | 0.517088 | 0.904135 | 0.903661 |
| J03WPY | targetlike | 0.324741 | 0.322639 | 0.714401 | 0.708315 |

## Label-free target output vs external ground truth

Target diagnostic uses frozen unaugmented model with penalty16, configured graded halves only; no public labels loaded. H/A spells are maximal runs, reset at half boundaries. External unknown-label gaps also split spells. Durations/coverage differ, so counts are descriptive, not matched quality comparisons.

| Aggregate | Target prediction | External ground-truth min–max |
|---|---:|---:|
| H share (%) | 36.564 | 25.728–35.012 |
| A share (%) | 21.481 | 20.702–31.691 |
| D share (%) | 41.955 | 41.515–51.698 |
| H/A possession spells | 467.000 | 402.000–511.000 |
| Mean possession duration (s) | 7.898 | 5.470–7.740 |

Target graded frames:158857; all H/A/D segments:625, mean duration:10.167s. These are not possession-spell counts.

No public-window comparison, label scoring, rebalancing or calibration. Target share/duration differences do not establish correctness or error. Existing candidate.csv remains the earlier penalty8 export; this round calculated aggregates only.

## Next experiment — not run

Whole-pitch bundle preregistered in proposed-whole-pitch.md against unaugmented penalty16. Longitudinal centroid separation uses absolute attack-axis projection, giving one nonredundant direction-invariant scalar. New bundle awaits approval. Consecutive failures1; existing stop rule and November12 freeze unchanged. Stop after this report.
