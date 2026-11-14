# Frozen final Trial-B ensemble private qualification

Started November13; prepared November14,2026. Commit protocol, source, fingerprints and final-artifact evidence before user execution. No new experiment or model selection. The user runs every test, inference pass and qualification command. No downloads or runtime execution by the assistant.

## Fixed artifact and scope

Export only `models/tcn-final-b/manifest.json`, schema `final_five_trial_b_two_seed_original_motion_tcn_v1`. Exactly the five permitted IDSSE development matches trained both initialization seeds20261106/20261107. Each member has an exact40k repeat fit. Retain short_mix sampling, CE+.1segment soft-IoU, original9701-parameter network, zeros/ones521 scaler, unchanged encoder, H/A/D order and penalty16. Validate saved checkpoints and exact first/repeat equality again on each fresh load; bind both weights, member proofs, checks log, final source-lock and audited manifest.

Within each member average original and180-degree-rotated probabilities using the existing normalized average; then average the two members' probabilities using the same function, in seed order. This is precisely the archived out-of-fold combination. No logits averaging, class rebalance, calibration, refit, decoder changes, public scoring or target-label read. TrialB was selected by the agreed median rule; A still has the higher corrupted mean. Neither is selected here.

## Qualification sequence

1. Verify committed delivery source/input lock and exact target asset/scorer hashes inherited from the previous release. Validate frozen artifact metadata and runtime package/Python/platform versions without calling any historical training-date guard. Date allows delivery through November17; action stops thereafter.
2. Run the new synthetic export contracts in a separate process before loading real arrays or models. Record the checks log privately. Synthetic checks establish implementation properties only.
3. Read only the frozen tactical tracking/team metadata and configuration. Use unchanged strict adapter,9core features and521 encoder,25fps, original half-open graded blocks. X outside blocks; H/A/D inside. Never inspect public labels or sealed assets.
4. Make three fresh model-loading passes: batch1, another batch1, then batch4. Each pass loads both final models and validates each against its repeat fit. Require all four seed/view probability arrays to match exactly between the two batch1 passes. Require byte-identical CSVs for all three passes. The unchanged official validator must return None for each output.
5. Rehash all registered source/assets/manifest/proofs/checkpoints after inference. Save private provenance including source, manifest, inputs, model and CSV hashes, environment metadata and checks log hash. Output H/A/D shares, H/A possession-spell count/mean duration and H/A/D segment count/mean duration as distinctly named label-free aggregates. Target accuracy remains unknown.
6. Independently invoke the same command in a newly installed pinned environment and a fresh local clone, then compare candidate CSV bytes and all immutable provenance hashes. This verifies frozen inference, not fresh training reproduction. No external publication or submission.

## Storage and failure behavior

Outputs are only new `local`, `clean` or `clone` directories beneath `data/competition/tcn-final-b-exports`. Existing outputs are refused. A staging directory is renamed only after every gate passes; incomplete staging and checks logs are preserved on failure, never automatically removed. Production and older exports are untouched. An exclusive export lock prevents concurrent copies of this exporter.

Use the same shared storage mutex as the completed missed-possession fits. Count both old missed/final artifacts, this export, diagnostic roots, new clean environment and new local clone toward2GiB; maintain12GiBfree with64MiBwrite reserve. Count local linked inputs once. Check before each bounded file write and after it. Third-party environment installation/clone commands require user preflight and postflight and do not have a hard filesystem quota; transient installer usage is explicitly not certified. Stop and retain evidence if insufficient storage; do not delete assets or substitute dependencies.

A wrong format/hash/runtime/repeatability result is a qualification failure. Diagnose implementation or environment, never tune model quality in response. The once-only sealed evaluation remains a distinct freeze step and is not implemented or invoked here. Unexpected sealed quality triggers bug/transfer investigation, not tuning. Research stops November16; this frozen-artifact delivery may run November16–17.

## Supplied checks and current status

Eleven synthetic tests cover two-member manifest identity, recipe and membership rejection, decoder/seed weights, repeat proofs, private output paths, post-freeze delivery deadline, official validator success semantics, half/X spell accounting, all-D output, exact probability averaging order and storage limits. They are supplied, not executed by the assistant. Clean-environment and fresh-clone reproduction are pending user execution. Version pins do not certify wheel bytes or OS/BLAS identity; output equality is required.
