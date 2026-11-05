# Phase 1 input, feature and export contracts

Preregistered 2026-11-06 before implementation and execution. User has supplied Archive.zip and explicitly removed the fallback implementation track.

Scope: one main learned-model pipeline's foundation. No fitting, model selection, target labels, or manual correction. Real restricted inputs are processed locally; only integrity/contract pass-fail and missing-file names may reach chat. Detailed reports and feature arrays remain under ignored data/.

Confirmatory contracts:
- Safely unpack only documented asset types from nested zips; reject traversal, symlinks and duplicate destinations; preserve source provenance and SHA256 privately.
- Raw ATD: exactly the configured number of sequential IDs 1..N, consistent nonempty slot count, three numeric fields per slot/ball; NaN permitted as explicit missingness, Inf rejected; no silent skipping, no wraparound indexing.
- Metadata: exactly two distinct teams, explicit home/away mapping checked against metadata, each slot assigned to a known team; missing metadata blocks team features.
- Homography: exact columns needed, integer frames 0..N-1 in order; valid is 0/1; valid matrices finite and nonsingular; invalid matrices cannot be projected.
- Tag intervals: public seconds-to-frame rule and half-open intervals, no empty/inverted/out-of-range intervals; unknown team is neutral; defense and offense map to different possession evidence.
- Features: distances use metres, missing xy does not become zero distance, team aggregation independent of slot ordering, gap age resets between halves, no derivatives across missing points or half boundaries. No labels used as features.
- Export: exact frame,label header, full ordered frame range, labels H/A/D/X only; identical inputs create identical bytes; reject blank or wrong-length predictions.
- Integration: synthetic metadata/tracking/tags/homography produces validated feature arrays and a valid CSV with synthetic probabilities through the existing decoder. Synthetic probabilities do not constitute a trained model or fallback.

Real asset check: extract supplied assets locally, inspect video header with ffprobe without decoding/displaying images, run schema/alignment validation and write a private report. Missing files are a dependency result, not a reason to fabricate metadata or label predictions. Do not infer teams from track slot indices or the video by hand.

Gate: all synthetic confirmatory contracts pass; real status is reported separately and may be partial. Extra tests discovered during implementation are exploratory and labelled as such. No competition-quality conclusion from correctness tests.
