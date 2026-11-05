# Phase 1 foundation result

Protocol commit: 736dc98, before implementation/execution. Date: 2026-11-06.

Seven new confirmatory test methods passed, with multiple invalid-input cases each; two new exploratory edge-case tests and nine existing decoder tests passed. Final complete run: 18/18, 0.228 seconds. Synthetic tests demonstrate input/export/feature correctness only. No fitted model or competition performance claim.

Implemented strict ATD, explicit team metadata, homography, tag interval and label-export adapters; label-free metre-scaled team aggregates and half-reset missingness/speed features; safe whitelisted nested extraction with local provenance; preparation commands and separate tactical/broadcast configuration. Automatic tag polarity is a soft hint, not a target label. Feature command intentionally requires tactical team metadata.

## Real local checks

Archive extracted to ignored data/competition with private hashes; no video images, raw tracking values, XML contents or feature arrays exposed to hosted context. Tactical ATD, homography and video-header alignment pass. Newly supplied Smart Tagging XML intervals pass. Broadcast ATD passes. Broadcast homography fails the declared valid-row numeric contract and remains excluded; no repair/imputation attempted. Header validation does not prove full video decodability.

Tactical metadata was subsequently found under Downloads/More Than A Hack 2027 - Initial Challenge - Dataset/tactical and passed explicit team/slot validation. Full tactical feature arrays were materialised locally; shape, no-infinity and half-reset checks passed. Only optional BAR-ATH_broadcast_atd.xml remains missing. Smart Tagging does not substitute for ATD metadata.

## Failures and corrections retained

Initial preparation script mistakenly applied tactical frame count to both cameras, causing broadcast frame-count failures. Corrected against unchanged public games.py: tactical 199319, broadcast 164488, separate unaligned timelines. Reran only broadcast validation after this configuration change. Broadcast raw then passed; its homography still failed valid-row numeric checks. Initial and corrected reports remain under ignored data/competition. This was an implementation configuration defect, not evidence that the broadcast raw file was corrupt.

Tag ownership helper was corrected during implementation to use the actual published phase names rather than illustrative generic names; final tests use BUILD UP and DEFENDING IN MIDDLE THIRD. Public scorer untouched.

## Limits and next steps

Phase 1 is partial. No external dataset adapter or split established, no training, no predictions or submission. Audit external labels and instantiate match splits; then preregister the first learned-model experiment. Recent-method review does not justify replacing the main candidate with PathCRF without a substantial adapter and live/dead component.
