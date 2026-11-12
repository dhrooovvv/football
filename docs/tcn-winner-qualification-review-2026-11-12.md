# Independent review: winning TCN qualification

Prepared November 12, 2026. Scope: static source and experiment-design review only. No tests, imports, compilation, training, inference, scoring, arrays, checkpoints or restricted target contents were executed or loaded by this reviewer. Reviewed the new diagnostic, checkpoint contract, final-fit trainer, fit/export entrypoints, release contract, supplied synthetic tests, protocols and reproduction instructions against their original control/representation sources.

## Decision and strongest supported evidence

The registered 40,000-update supervised/reset control improved clean and target-like corrupted spellF1 on all five reused development matches. Its mean scores are .632870845 and .497549978; the median paired corrupted gain is +.026049300 over the preceding 20,000-update rotation model. That supports retaining the recipe as the current eligible development candidate. It does not estimate target accuracy, establish competition rank or prove that still longer training helps. The overlapping training folds and repeated use of these five matches prevent treating the five improvements as five independent prospective confirmations.

The next decision is whether this candidate can be served faithfully under the target input contract. Source documentation allows target slots to change identities, whereas the external representation uses stable person identities, adjacent-slot velocity and an object temporal convolution before pooling. This is a plausible transfer mechanism, not measured target damage. Qualification must preserve the model recipe and expose this uncertainty.

## Diagnostic interpretation contract

- Reconstruct the actual 40k control parent from each current fold checkpoint, equal original/180-degree probability averaging and penalty 16. Match archived parent CSV bytes and metrics before interpreting stress results.
- Preserve static within-team/half permutation as a numerical control. Keep a separate identity-preserving velocity-rederivation control. Dynamic churn versus that rederivation control is the relevant diagnostic contrast; parent versus dynamic also includes rederivation differences.
- Per-frame random permutation is a deliberately severe synthetic stress, not an empirical estimate of target identity-switch frequency. Neither a large nor small effect directly estimates target accuracy.
- Report every match and setting. A failed numerical control blocks interpretation. No target-calibrated quality threshold, model selection, representation repair or automatic production promotion follows from this diagnostic.
- A human review point belongs between the completed diagnostic and final-fit/export execution. Material unresolved transfer risk must remain visible in the release decision.

## Final-fit and export contract

Use a distinct final-fit entrypoint with exactly the five allowed IDSSE development IDs. Do not weaken the existing four-training-match LOMO guard or invent a held-out identity. Exclude both sealed IDSSE matches, PFF holdouts, PFF training matches and target data from this winning supervised fit.

Preserve original class initialization, the unused reconstruction head for compatibility, 20k + 20k updates, Adam reset and window/view RNG reset at the boundary. Torch RNG is not reset at the boundary. Preserve the original gap inputs, seeds, window sampler, loss and decoder. Increasing training membership from four to five with a fixed update budget changes exposure per match; the final fit is an artifact-generation step, not a new generalization comparison.

Require exact repeated fit states, losses and sampling evidence; checkpoint/manifest source and membership integrity; original plus rotated probability averaging; unchanged official CSV validator; X outside configured blocks; exact first/reload/batch CSV bytes; and private outputs. Frozen-model inference reproduction in a fresh pinned environment is distinct from full training reproduction and must be reported separately. The legacy 53-match/CatBoost-blend exporter is unsuitable.

Sealed evaluation remains once at the November 16 freeze. Poor sealed results trigger alignment, implementation or transfer investigation, not tuning. Target accuracy remains unknown. Production remains the existing CatBoost pipeline until a separately documented release decision.

## Implementation findings and dispositions

The current slot runner uses the actual control40k checkpoints, validates the complete original training identity and archived sampling/loss evidence, retains rotation/16 and reconstructs all ten archived parent CSVs before interpreting stress. Both-view reload probabilities and first/reload/batch CSV bytes are required for all forty cells. Static and rederived-identity controls are preserved. No source blocker was found in this implementation.

The explicit final trainer preserves the original supervised draw mapping, crossentropy, initialization and stage transition, with a separate exact-five membership contract. The original four-member fold trainer remains unchanged. Repeated final fits compare weights, optimizer, RNG, losses and sample/view evidence while excluding elapsed time. The exporter checks class order, feature order, frozen input configuration, X handling, original/rotation probabilities and unchanged official validator's `None` success return. No CatBoost probabilities or target labels are used.

The review identified three integrity hardening items, now implemented in source:

1. Bind diagnostic completion to its current committed protocol/input signature and exact forty repeatability/ten parent cases, rather than trusting a plausible signature string alone.
2. Recheck absence of the final manifest after acquiring the operation lock to prevent a completed concurrent fit being overwritten.
3. Rehash both checkpoints and reviewed diagnostic after export inference, in addition to source/target/manifest rechecks.

Documentation paths now agree on `data/gru-env/bin/python` and `data/competition/tcn-winner-local`. Seven release contracts are supplied, including a synthetic interrupted-versus-uninterrupted training check immediately at and after the optimizer reset. Its test-local smaller budget and model do not expose runtime budget overrides; exact optimizer step count, weights, RNG, losses and sampling evidence distinguish the intended reset/resume semantics from continuous optimization. All seven checks remain unexecuted.

Final lock generation and committed byte-fingerprint agreement remain root-owned prerequisites. Supplied synthetic contracts are not a substitute for the user-run runtime steps.

No blocking defect remains in the reviewed source, subject to final registration consistency checks. This is not a runtime pass, slot robustness certificate, target-accuracy estimate or release approval. The highest-value next evidence is the current-winner parent reconstruction and controlled external slot diagnostic; report its outcomes before launching final fitting. The production pipeline remains unchanged.
