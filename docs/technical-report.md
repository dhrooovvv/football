# Ball possession technical report — draft, November 7, 2026

## Selected method and status

Selected pipeline: strict local adapter → nine masked core features → direct three-class CatBoost H/A/D probabilities → deterministic Viterbi, uniform switching penalty16 → frame,label CSV. No minimum spell length, augmentation, whole-pitch bundle, Smart Tagging, video model, reconstructed ball, fallback branch or class rebalancing enters production. Architecture freeze remains November12. This draft documents the executed candidate, not a competition submission or hidden-score claim.

The final target CSV has199319 rows and SHA-256 `ab253e43f46fc9a7885b689498a220595e78d67ad2a6099a07316e081ca3f815`. Official validation passes. Two independent full training/inference runs and a third run in a clean environment generated identical CSV bytes. Model serialization hashes differ across fits because metadata differs; actual artifact hashes are recorded without claiming identical model-file bytes.

## Sources and external training data

- Organizer starter, DATA.md, EVALUATION.md, RULES.md, unchanged evaluation/possession_metrics.py and evaluation/validate_submission.py: local reference/more-than-a-hack-2027-main. Scorer is the specification; no changes made to reference evaluation code. Organizer competition assets remain local and ignored by Git.
- IDSSE/DFL dataset: [official repository](https://github.com/spoho-datascience/idsse-data), [Bassek et al., Scientific Data12,195 (2025)](https://doi.org/10.1038/s41597-025-04505-y), [file manifest](https://api.figshare.com/v2/articles/28196177). Attribution: Deutsche Fußball Liga; Bassek, Rein, Weber and Memmert. Dataset CC-BY4.0; downloaded development file sizes/MD5 verified in private data/external/manifest.json.
- [Floodlight DFL parser](https://raw.githubusercontent.com/floodlight-sports/floodlight/master/floodlight/io/dfl.py) supplies documented label mapping: BallStatus0=Dead,1=Alive; BallPossession1=Home,2=Away. Metadata explicit HomeTeamId/GuestTeamId and pitch dimensions determine teams and coordinate transformation.
- [CatBoost](https://catboost.ai/docs/), version1.2.10. No pretrained neural checkpoint or hosted model receives competition assets.

Five external development matches: J03WMX,J03WN1,J03WOH,J03WOY,J03WPY. Leave-one-match-out evaluation trains on four and scores the fifth. Two sealed matches J03WQQ/J03WR9 remain unopened and undownloaded. Final model trains on all five development matches. Use every fifth clean training frame after excluding unknown labels; unknowns break evaluation/decoding runs. Final CatBoost budget:300iterations, depth6, learning_rate.05, l2_leaf_reg3, random_seed20261106, thread_count4, MultiClass, no early stopping. No target labels are training samples.

## Input and feature rules

Target ATD IDs must be exactly1..199319; output indices0..199318. Require46 slots with explicit home/away names from metadata, fixed slot count, finite-or-NaN numeric values and no infinities. Slots are tracklets, not stable player identities. Target normalized coordinates are scaled by105.3×68m; external centered metric positions become normalized coordinates using their own pitch dimensions. Do not infer team identity from position or attacking direction.

Nine columns: home nearest-ball distance, away nearest-ball distance, away-minus-home distance margin, instantaneous ball displacement speed, signed pitch-edge distance, ball-observed mask, finite-home-distance mask, finite-away-distance mask, ball gap age. Missing values remain NaN. Speed requires consecutive ball observations and resets across half boundaries; missing ball does not itself mean dead play. All core columns are invariant under a180-degree pitch reflection.

Viterbi maximizes summed log probabilities minus uniform penalty16 for state changes. Decode halves independently; uncovered target frames are X. Configured half-open target blocks:[11185,90652),[110808,190198). Export deterministic newline-delimited frame,label with exactly one row per video frame. Validator checks schema, not predictive correctness.

## Evaluation, corruption and selection

Report official spellF1 (mean across prescribed IoU thresholds) and frame macroF1 per external match, clean and corrupted. Original synthetic burst corruption underestimated target gaps. Current target-like evaluation masks bootstrap alternating empirical target observed/missing ball-run lengths using only target tracking, fixed seed20261106+sorted-match index. Mask raw ball positions before feature computation; retain the original independent player corruption. Actual graded missing fractions35.7–47.5% versus target40.7%; finite-match samples are approximate, not exact rate matching. Missingness conditional on play/occlusion is not modelled.

Original promotion gate: positive median paired development-match spellF1 change, majority of five improve, median macroF1 change>=-.01, tests pass. Per-match gate input is arithmetic mean(clean,corrupted). No sealed or target public score drives selection. Penalty16 separately passed this gate. Augmentation at16 failed and was dropped. Latest rolling whole-pitch bundle also failed, including the additional minimum median corrupted spellF1 gain+.01 required for that experiment. No feature additions follow that failure. Full protocols/results and dated decisions are in experiments/ and ball.md.

Selected penalty16 external means: clean spellF1 .517654 / macroF1 .895099; target-like corrupted .323476 / .679401. These are development-selected results with repeated use of the same five matches, not unbiased generalization estimates.

## Reproduction and artifact provenance

Pinned top-level dependencies: requirements-pipeline.txt. Full resolved environment: experiments/whole-pitch/clean-environment-lock.txt. Exact Python/platform, hashes and clean reproduction evidence: experiments/whole-pitch/reproduction.json. Two-run export evidence: finalization.json. Model/CSV files remain ignored under models/ and data/; the hash manifest is committed.

From repository root with the approved private input layout and Python3.13:

```
python3.13 -m venv data/reproduction/venv
 data/reproduction/venv/bin/python -m pip install -r experiments/whole-pitch/clean-environment-lock.txt
PYTHONPATH=src data/reproduction/venv/bin/python scripts/rebuild_clean_inputs.py
PYTHONPATH=src data/reproduction/venv/bin/python scripts/predict_core.py --cache data/reproduction/prepared --outdir data/reproduction/predictions --model-path models/finalization/clean-environment.cbm
 data/reproduction/venv/bin/python reference/more-than-a-hack-2027-main/evaluation/validate_submission.py data/reproduction/predictions/candidate.csv
```

The rebuild command loads only the five development XML matches and asserts exact feature/label equality with original clean caches. The prediction command performs fresh full-development training, loads target tracking locally, exports CSV, reloads its model and requires identical regenerated CSV bytes. Compare output CSV SHA-256 against this report. Installation logs, target validation details and private provenance remain under ignored data/. This is an environment reproduction on the same machine, not a separate-hardware portability claim.

## Rules implemented and limitations

No target public-label tuning/training, sealed-match access, external submission or restricted-row publication. Earlier one-off public-window evaluation was authorized solely for alignment checks; this finalization did not reload public labels or rescore target predictions. Synthetic tests establish contracts, not competition quality. Existing paused automation remains paused. No research after November12 architecture freeze; no further action after November17 under the standing schedule.

External label conventions are only nominally matched to H/A/D. Dead share41–52% and mean possessions5.5–7.7s differ from the short public-window documentation; loose-ball/flight ownership continuation and unknown-label exclusions may differ. Ball absence interacts differently with nearest-player heuristics across sources. No remapping or class rebalance was fitted to target summaries. Domain shift, corrupted tracking robustness, visible-subset bias and short-spell recall remain limitations. Sealed generalization and full target accuracy remain unknown.

This draft still needs team review, the later authorized frozen sealed evaluation, and any organizer-specific final packaging requirements. No submission receipt exists because no submission has been made.
