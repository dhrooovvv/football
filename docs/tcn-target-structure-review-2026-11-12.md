# Independent review: label-free input structure qualification

November 12, 2026. Source-only review of `scripts/audit_tcn_target_structure.py`, `experiments/tcn-target-structure-2026-11-12/structure.py`, the fixed protocol, user instructions and six supplied synthetic contracts. Lock completion and committed fingerprints remain registration prerequisites. No tests, imports of project modules, compilation, model/scorer execution, training, arrays, CSV rows or restricted target contents were executed or loaded by this reviewer.

## Hypothesis and decision

The completed controlled stress diagnostic establishes severe sensitivity of the frozen TCN to per-frame identity churn, jointly through false adjacent-slot velocity and disrupted temporal object history. The next uncertainty is whether actual target input structure differs materially from the stable external inputs. This audit describes that structure without estimating identity-switch rates or target accuracy. Its result informs a human serving-risk review before final fitting/export; it does not select a model or reopen a stopped quality track.

## Source findings

The runner uses the original strict local ATD/teams parser and explicit target frame/team/pitch/block contract. External access is restricted to five development matches' object, role and metadata files plus physical pitch metadata. It does not load possession labels, cached core/gap features, checkpoints, models, protected matches or public labels. Outputs are private aggregates with source/config/input hashes; no coordinate or per-frame sequence is written.

The aggregation code carries adjacent-frame pairs across computational chunks, resets at real half boundaries, excludes missing coordinates from motion and geometry, and reports explicit observation denominators. Run lengths are pooled per slot, include half-edge censored fragments and do not treat half starts as observed reappearances. Same-team close-position counts use unordered visible pairs once each. Physical displacement uses each provider's pitch scale. Four histogram quantile intervals and fixed descriptive bins avoid retaining geometry samples. Six synthetic contracts cover stable/chunk behavior, permutation sensitivity, gaps/halves, close-pair counts, aggregate-only output and strict input shapes; all remain unexecuted.

No blocking computation or protected-data defect was found in the reviewed source. Review recommendations concerning report denominators and wording are incorporated: the table uses the same-slot-observed-pair nearest-set metric for direct comparison to same-slot displacement, and visibility counts are explicitly slot counts rather than unique player counts. Both target and external geometry now traverse the same centered-float32 round trip for the diagnostic. Target parser failures are reduced to a generic local error rather than exposing raw exception contents; fixed runtime contract messages identify failed prerequisites without asset values.

## Interpretation requirements

- The nearest previous same-team set statistic is directed and many-to-one. Nearby different teammates, crowded positions and duplicate tracks can all make it small; it is neither an assignment nor verified identity. The same-slot versus nearest-set contrast is a warning proxy, not an identity-switch estimate.
- Same-slot displacement includes only slot pairs observed in both adjacent frames. The all-current nearest-set summary also includes current observations whose same slot was missing previously. Quantitative contrasts should use `nearest_previous_set_for_same_slot_observed_pairs`, which shares the same current observation support as same-slot displacement. Retain the all-current summary as a separate description.
- Visible slots are not verified unique players. More than eleven visible team slots is a coverage/duplication warning, not an established player count. Pooled missing-run distributions include inactive, replacement and unused slots; different allocated slot capacities make naive provider comparisons misleading.
- Exact and near-coincident same-team positions can reflect legitimate close teammates or quantization. The fixed close-pair summaries are not duplicate-track rates. Conversely, noncoincident duplicate detections may evade these summaries.
- The velocity clipping proxy is the rederived normalized-coordinate component exceeding magnitude five at 25Hz. A zero clipping rate does not establish identity continuity: jumps below approximately .2 pitch units per frame can still be grossly implausible player motion. Interpret the physical displacement bins and tail intervals alongside clipping.
- Both providers are examined in float32 through centered encoding and inversion before rederivation. This introduces rounding relative to original normalized coordinates. The proxy is not an exact reconstruction of the encoder's original pre-rounding velocities. Histogram quantiles are .01m intervals, with an open upper tail at 200m.
- These summaries do not measure identity correctness, target accuracy or causally identify the stress failure mechanism. Even target distributions similar to external distributions cannot certify correct target identities or model quality. No cutoff is an automatic release pass.

## Recommendation

Run the preregistered aggregate audit once locally under user control after protocol/source/input fingerprints are committed. Review target versus per-match external ranges, preserving denominators, slot capacities, censoring and proxy ambiguity. Do not tune thresholds from target outcomes, repair identities, zero velocity, change representation, retune decoder or begin new training as an implicit response. Record a material mismatch as a serving limitation requiring an explicit decision. If the evidence supports proceeding, retain the residual uncertainty and continue the already-approved final-fit/export qualification. Production remains unchanged and target accuracy unknown.

This review is not a runtime pass or a certificate that the winner can be served safely on the target. Final registration consistency and user-run contracts remain pending.
