# Lost-possession diagnosis and delivery qualification

Authorized November 13, 2026. Implementation preparation only; the user executes all tests, inference and scoring. No training, downloads, new quality trial, production switch or external submission is authorized by these commands.

## Two separate outputs

The diagnostic uses the five existing development matches and their original out-of-fold Trial A/B checkpoints. It must reproduce the archived CSV bytes and official scores before explaining errors. Trial B remains selected; A is a fixed reference, not an alternative selected using this analysis. The final models trained on all five matches must never be used to measure development performance.

The delivery exporter uses the completed final Trial B two-member manifest. It checks provenance, the official output format, fresh-load equality and alternate inference-batch CSV equality. Subsequent clean-environment and fresh-clone checks qualify frozen inference; they do not constitute a new training reproduction or improve measured accuracy.

## Interpretation limits

The registered development result remains B mean spellF1 0.650384708246 clean / 0.509835639664 corrupted. A retains the higher corrupted mean, 0.513496193212. Both were selected or assessed repeatedly on the same five matches. Target accuracy is unknown.

Diagnostic counts are associations, not additive causes or recoverable spellF1 points. A ground-truth spell matched by argmax but lost after decoding establishes that local evidence was present under that particular diagnostic; it does not establish that changing the decoder would improve the official overall score. Long-gap error concentration does not by itself prove that a larger receptive field fixes it. Recommendation eligibility must include consistency across matches and explicit uncertainty.

At most one next intervention may be proposed after reviewing the completed diagnostic. A future trial requires a separate approved, committed protocol; existing stopped tracks and the revised promotion rule remain unchanged. No automatic experiment follows report generation.

## Completion sequence

1. User runs the diagnostic; review archived-score reproduction, per-threshold results, missed-spell accounting, gap/length strata, clean-to-corrupted changes and probability evidence.
2. User runs the independent private export qualification; preserve all previous outputs.
3. User runs clean-environment and fresh local-clone frozen-inference qualification, retaining hashes and failures.
4. At the November 16 freeze, perform the previously planned once-only sealed evaluation of the frozen candidate and supplied baselines. Unexpectedly poor results trigger bug/transfer investigation, never sealed tuning or selecting A versus B from sealed results.

Maintain ball.md, findings.md, research-state.yaml and the technical report after each reviewed result. No research after the November 16 freeze and no action after November 17. No sealed or target-public labels enter this diagnostic; no target rows enter hosted context. No new training or sealed evaluation runner is part of this implementation step.
