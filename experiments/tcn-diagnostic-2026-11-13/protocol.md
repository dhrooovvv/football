# Frozen A/B lost-possession diagnostic — November 13, 2026

This is a diagnostic, not a quality experiment or model-selection trial. Selected B and reference A stay unchanged. No training, downloads, new corruption, parameter search, target data/labels, final-five-model evaluation or sealed inputs. The user runs every test/inference/scoring command. Stop research at the start of November 16 Asia/Kolkata. No automatic new experiment.

## Registered inputs and execution

Exactly J03WMX, J03WN1, J03WOH, J03WOY, J03WPY, each clean and frozen targetlike. Use A/B out-of-fold first checkpoints for seeds20261106/20261107, validated against completed fit proofs and inherited source/data/environment registration. Both seeds' identity/180-degree probabilities average equally, then seeds average equally, decoder penalty16 unchanged. Existing CSVs are read and scored first; require exact full archived metric equality. Archives contain no probabilities, so re-infer each case at batch1 and require decoded labels AND CSV bytes to reproduce the saved prediction before attribution. No probabilities or frame rows retained in diagnostic outputs. Final-five weights are never loaded.

Ten resumable units (trial × match), each runs both conditions and saves aggregate-only results with content digest, registration signature, checks-log hash. Restart verifies all source/data/model/CSV evidence and unit signatures. One numerical thread, sequential cases, two models in memory. No numerical execution by assistant. Synthetic tests execute first in user subprocess. Combined oldmissed/finalB/export/diagnostic artifact roots plus regular files in data/tcn-final-b-clean-env and data/tcn-final-b-clean-clone (excluding their shared symlink targets already counted in original roots) share data/tcn-missed/storage.lock, 2GiBcap/12GiBfreefloor and64MiBwrite reserve. No automatic deletion. The full artifact check is repeated around writes; other programs can still consume disk.

## Spell accounting and fixed definitions

Use unchanged official H/A maximal spells, exact same-team IoU greedy matcher and thresholds .3,.4,.5,.6,.7. Original frame identities `(start,stop,team)` stay unchanged; valid runs split at both half boundaries and GT X. Official archive score adapter inserts separators; independent original-coordinate accounting must reproduce its per-threshold scores. Clean/corrupted labels, blocks and complete spell identities must match exactly.

Duration: ≤50frames,51–250frames,>250frames (25fps). Gap: fully observed, max intersecting burst≤50frames,51–250frames,>250frames. Burst length is the FULL missing run intersecting a spell, clipped only at valid-run/half/X boundaries, not clipped to the spell and not the sum of missing frames. Use existing encoder ball-observation mask at x[:,-4]; no mask regeneration or imputation.

Report all official precision/recall/F1 and missed/spurious counts per threshold, recall/counts crossed by duration and gap, matched-spell start/end boundary shift quantiles (0,.1,.5,.9,1), observed/missing/all wrong-team and dead/live frame errors and alive/dead F1. GT-spell strata do not have a valid standalone predicted-spell precision denominator, so report stratified recall only.

At headline IoU.5 missed spells receive overlapping descriptive flags:
- decoder_removed_support: raw probability argmax is officially matched but decoded spell is not. Association only, NOT causal proof or a recoverable score.
- long_gap_without_argmax_match: intersects >250frame missing run and raw argmax does not match.
- observed_wrong_team: whole spell observed and strictly more than half its frames predicted opposite team.
- dead_live_confusion: at least one GT possession frame predicted D. Separately report all frame dead/live errors.
- merged: overlapping same-team predicted spell overlaps at least two same-team GT spells.
- fragmented: at least two same-team predicted spells overlap one GT spell.
- boundary_misalignment: same-team overlap exists but no official match; may overlap merged/fragmented.
- other: none above.

Report pairwise flag overlap counts. For ranking only, assign each missed spell the FIRST flag in the above fixed order. This arbitrary documented priority avoids double counting but is NOT a causal partition. Report raw-argmax matched/decoded missed, reverse and both-missed at EVERY IoU. Pair each GT spell clean-to-corrupted at every threshold: retained/lost/gained/missed-both and lost counts by corrupted duration/gap strata.

## Recommendation policy and acceptance

Rank B corrupted exclusive categories and show per-match counts; A is reference only. A conditional proposal is emitted only if a unique aggregate-leading category is one of the first three and it has positive joint-highest count in at least3/5matches. Decoder support → narrowly scoped decoding; long-gap missing evidence → longer temporal context; fully observed wrong team → local player–ball relationships. Otherwise output no proposal and request human review. A reproduction/schema failure stops the diagnostic for bug investigation, rather than recommending a model. Any recommendation is only a hypothesis; counts are not spellF1 improvement estimates. No stopped track reopened, no gate changed, no model promoted.

Do not infer label convention bugs merely from score or this taxonomy. If trusted evidence reveals such a defect, fix and preregister a correction separately. Append actual results only after user run. Existing median gate, all historical failed trials, production model and final qualification plan remain unchanged. Target accuracy unknown.
