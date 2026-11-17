# Completed frozen possession diagnostic and local export review

Reviewed November 14, 2026 from saved aggregate JSON, checks logs and byte hashes. The assistant did not execute tests, model inference or scoring, and did not deserialize models, arrays or prediction rows.

The user-run diagnostic records 14 passing checks and reconstructs all 20 archived A/B cells and CSV bytes. Local ensemble export records 11 passing checks, official format validation, exact four-view reload probabilities and three byte-identical CSVs. Root independently verified 76 registered entries, committed source bytes and 194 unique referenced file hashes. Detailed audit is result-audit-2026-11-14.json.

## What costs recall

At IoU 0.5 selected B misses 1,278 corrupted spells. Under the documented exclusive priority, 535 fall in long gaps without an argmax match, 265 have an argmax match lost after decoding, and 250 are fully observed wrong-team errors after higher-priority flags. Long-gap evidence leads on all five matches. This is a descriptive partition with arbitrary priority. Counts cannot be summed into predicted spellF1 gains.

|Match|Corrupted missed|Long-gap absent argmax match|Argmax matched, decoder missed|
|---|---:|---:|
|J03WMX|301|106|74|
|J03WN1|303|125|67|
|J03WOH|211|113|45|
|J03WOY|250|101|45|
|J03WPY|213|90|34|

Tracking the same GT spells across conditions, corruption loses 359 matches and gains 34 at IoU 0.5. Of the 359 lost matches, 289 (80.5%) intersect a missing-ball burst longer than ten seconds. Burst length is the whole valid-run-clipped burst intersecting the spell, so this does not assert that the entire possession was unobserved. This paired result strengthens the long-gap recommendation beyond aggregate count alone.

Decoding loses 265 matches that argmax obtained but also obtains 172 that argmax missed. These are matched-GT recall counts only. They do not capture spurious predictions or all official IoU thresholds and cannot establish that argmax or a lower penalty improves overall spellF1.

## One next research direction

Recommend one prospective longer-context temporal intervention. The current 17-frame receptive field is about 0.68 seconds at 25fps, while the leading failures intersect bursts over ten seconds. A future protocol should change temporal context alone against selected B, retain both seeds, sampler, loss, rotation, decoder, corruption and comparison budget, and measure recovery of the specific long-gap strata alongside the full existing promotion gate. A longer context may provide pre/post-gap evidence but cannot guarantee ownership when observations are absent.

No architecture or training budget is chosen by these counts alone. A bounded implementation proposal and separate user approval are required before a new trial. Previously stopped tracks, freeze and sealed exclusions remain in force. No automatic decoder, attention or loss variation follows.

## Quality and qualification

Reproduced B means remain 0.650384708246 clean and 0.509835639664 corrupted. A remains higher corrupted mean at 0.513496193212. This diagnostic adds explanations and reproductions, without a new candidate score or independent accuracy measurement.

Private final ensemble CSV SHA256 is 3dca80aa3b18a8c8e880b9f26cf1dc4f17a13018df18a2e4b39cf30f7da63463. Its local official validator and repeated-load/batch checks pass in the saved user execution. Private provenance and target outputs remain under data/competition/tcn-final-b-exports/local. Clean-environment and fresh-clone exports are still pending. The once-only sealed evaluation remains at the November 16 freeze. Target accuracy is unknown.

All original diagnostic per-match/per-IoU scores, strata, boundary shifts, overlapping flags and paired corruption tables are preserved under evaluation/results.json. No scorer or frozen source was changed during review.
