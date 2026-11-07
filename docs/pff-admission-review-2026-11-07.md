# Independent data-science review: PFF admission — November 7, 2026

Scope: `AGENTS.md`, project memories, PFF admission protocol, `src/possession/pff.py`, its tests, committed aggregate intake evidence, and user-supplied external PFF specification text/PDF. No target assets, competition public labels, sealed IDSSE files, model training or performance evaluation. Only this review document was edited; no code or commits.

## Decision and hypothesis

**Do not admit the currently reviewed smoothed-ball adapter for the planned train-more/transfer evaluations.** The principal blocker is documented annotation-conditioned feature construction, not duplicated frame IDs.

The intended hypothesis is that adding compatible external tracking/labels improves the unchanged production configuration on the original five development matches. Outcome: matched per-match clean/corrupted spellF1 and macroF1, with the existing paired gate plus median corrupted gain >= .01. Independent PFF transfer scores are risk measurements, never selection criteria. A necessary precondition is that possession labels are not also used to manufacture the input ball trajectory in a way unavailable on target tracking.

Confidence is **high** in the smoothed-ball leakage/serving-mismatch finding and the identified code-contract gaps. Confidence is **low** in exact cross-provider possession-convention equivalence; schema agreement cannot establish it.

## 1. Blocking: smoothed ball positions are annotation-conditioned

The supplied *PFF FC Tracking Data Specification v2.2*, PDF page 2, explicitly describes player Kalman smoothing and a different ball procedure: PFF uses its events, places ball positions at the ball carrier and interpolates between events. This is external-source documentation, not an inference from model scores. Extracted evidence is in `data/pff/document-text/PFF FC Tracking Data Specification v2.2.txt`, around lines 175–232.

The reviewed adapter reads `ballsSmoothed` and `homePlayersSmoothed`/`awayPlayersSmoothed`. Several core features then directly depend on distance from players to that annotated carrier-conditioned ball position. A successful provider transfer score with these fields could partly reflect how the label helped create the features. More-data training would also see a feature-generation process absent from raw target tracking. This can make PFF look artificially easy without improving real transfer.

**Required action:** preregister a raw-ball policy before modelling. Prefer raw `balls` as independent source observations; do not fall back to `ballsSmoothed` when raw ball is absent. Keep the entire smoothed variant out of the selection comparison. If smoothed player positions are retained, state that they use a Kalman procedure and verify they are not event-derived. Using raw player observations too is the cleaner comparable measurement policy. Do not compare several such policies on model scores to choose one under the guise of preprocessing.

The specification, PDF pages 3–4, defines `visibility` as VISIBLE versus ESTIMATED. Ignoring it conflates detected and estimated positions. Require a fixed, documented observed-only policy or explicitly separate both provenance classes. An ESTIMATED finite coordinate must not silently count as an observed raw ball. Audit raw/smoothed and visible/estimated availability by state; do not use those descriptive cuts to relabel or rebalance classes.

Expected impact: credible scores may be lower than a carrier-conditioned-ball evaluation; actual generalization could improve or worsen. Neither direction is established before the raw-data comparison.

## 2. CLK: not established as a safe play/ownership event

`CLK` is absent from the supplied tracking-spec game-event enum (page 6; extracted text around lines 765–820). Its name alone is not sufficient evidence that it cannot signal a discontinuity relevant to state carry.

In the reviewed `event_state`, marking CLK NEUTRAL only prevents a play-state update; the subsequent common `home_ball` logic still updates ownership from CLK. Thus “CLK neutral” does not currently mean fully neutral.

**Required action:** either obtain a provider-supported explanation and explicit policy, or fail closed for affected segments: clear state and owner on CLK, require a fresh supported state/team assertion before recovering H/A/D, and report the exclusions. Do not alter the primary reference-video time using an undocumented game-clock correction. Absence of CLK in the fixed pilot does not validate it for all 64 matches.

## 3. Unknown carry and interval validity

VID now clears stale owner, which addresses one real risk. However, the loader can preserve live state/owner across a long gap in native observations if no VID event is present. `resample` marks the middle of a source-time gap X, but the first subsequent native record can recover an old label from carried state even with no fresh supported event.

**Required action:** preregister whether gaps exceeding native support clear state/owner; the conservative choice is to clear them until a fresh assertion. Also validate embedded `game_event.start_frame/end_frame` against the grouped source frame, or explicitly justify a provider state-transition carry contract rather than assuming an event can assert current ownership indefinitely. Track the last supporting event/frame and why each output label is known. “Annotated record present” is not the same as a valid unique-frame label.

Contradictory simultaneous assertions should remain X; do not resolve their order from input line order, latest metadata or eventual scores. The existing consensus approach is directionally appropriate, but document whether current uncertainty persists until explicit state *and* owner information is restored.

## 4. Clock and grouping guard gaps

The primary `videoTimeMs` clock is appropriate according to the supplied specification: it is time since video start, whereas `periodGameClockTime` is an estimate. `generatedTime` and `smoothedTime` are file-generation/smoothing timestamps, not a documented per-frame precedence rule.

The reviewed clock consistency check is per-step with a two-native-frame tolerance. That tolerance is large relative to an ordinary one-frame step: a systematically incorrect clock slope can pass every local step. Add a cumulative half-anchor check of video elapsed time against frame delta/native fps, with a preregistered tolerance appropriate to rounded 29.97 Hz metadata. Preserve a report of residual distribution; do not choose the tolerance from model scores.

Enforce finite positive fps, explicit metadata-match identity, two distinct home/away IDs, and one contiguous traversal of period 1 then period 2. The current singleton metadata assertion can disappear under optimized Python, and the dictionaries holding prior frame/time do not themselves prohibit returning to an earlier period. Synthetic malformed metadata/period tests should fail predictably.

## 5. Resampling and conflict diagnostics

Nearest-position sampling and past-only label sampling can use adjacent native frames at a transition. This is not automatically wrong, but it creates up to roughly one native-frame feature/label discrepancy. Record both source indices/time offsets in private provenance and test exact transition examples before claiming no alignment error. Do not interpolate across missing support, and do not concatenate equal states across halves or unknown runs.

Current `player_conflicts`/`ball_conflicts` count some pre-existing missingness and lose within-record conflict provenance after applying consensus. They are not certified coordinate-disagreement counts. The admission table should separately report:

- repeated source records and repeated known jerseys within a record;
- all-identical coordinates, all-missing values, finite/missing disagreements, genuine finite coordinate disagreements;
- play-state conflicts, ownership conflicts, VID/CLK and unsupported-event exclusions;
- timestamp/frame residuals and failures;
- native unique-frame, 25 Hz grid, known-label, observed-ball and observed-player denominators;
- label coverage and natural ball visibility conditioned on H/A/D, without performance-based replacement.

Exact duplicate grouping is appropriate because the specification documents multiple possession-event associations, but a mixed tracking/event-payload difference is not evidence of a coordinate error. Roster duplicates/unknowns should have their own failure reason rather than be silently remapped.

## Admission gate and next highest-value slice

1. Commit the measurement/unknown/clock amendments before running the full admission job.
2. Add targeted synthetic tests for raw-vs-annotated input selection, VISIBLE/ESTIMATED handling, CLK ownership, gap recovery, cumulative clock slope, malformed metadata and transition resampling.
3. Run the all-64 descriptive admission report with the locked 48/16 split. Preserve failing matches in the report; do not substitute easier matches based on performance.
4. Admit only matches with a documented usable contract and report excluded frames/matches. If exclusions leave the fixed comparison underdefined, stop for a protocol revision, not opportunistic match replacement.
5. Only then run the two already-authorized evaluations. Keep production unchanged unless the train-more comparison passes both gates. Transfer results remain descriptive.

Provider transfer mixes provider, competition, teams, camera coverage and annotation conventions. Its direction cannot be attributed solely to provider quality. The PFF holdout is match-disjoint but not necessarily team-disjoint. The original five matches remain historically reused, so a passed development gate is an engineering decision threshold, not proof of unbiased superiority or target accuracy. Do not reopen stopped decoder/settings tracks in response to these findings.

## Resolution assessment — November 7, follow-up during full admission preparation

Reviewed the updated source and full-admission protocol read-only after parent reported amendments `260e6e0` / `e37bfb6`. No new model, score or data experiment executed by this reviewer.

### Resolved in the reviewed code

- The adapter now uses raw `homePlayers`, `awayPlayers` and `balls` and retains only VISIBLE coordinates. There is no reviewed fallback to event-conditioned `ballsSmoothed`. This resolves the principal documented feature-leakage blocker, subject to the actual preparation run using this exact source version.
- CLK and VID make state unknown and clear stale owner. The code no longer treats CLK as a verified neutral play/ownership event. It does not adjust the primary video clock from CLK.
- Native gaps larger than the preregistered two-native-frame threshold clear state/owner before fresh annotations. This is a stated conservative policy rather than evidence that every possible camera cut is captured.
- Cumulative half-anchor video/frame agreement is checked in addition to local step agreement.
- Singleton metadata and explicit match identity are checked with a runtime ValueError instead of an optimizable assertion.

The earlier pilot's smoothed-input results remain engineering history; they are not valid training/transfer inputs for the corrected raw-only policy.

### Missing ball and label selection: correct separation, report the risk

The updated logic does **not** set labels X merely because raw ball coordinates are missing or ESTIMATED. That is appropriate: observation missingness is not a dead/live label and naturally missing live frames are precisely the desired teaching signal. Current first admission record for 10502 reports known labels on all 146785 output frames and 78313 naturally missing-ball graded frames; this confirms masks and labels are separate, not that their semantics are independently verified.

Required report cut before modelling: counts for each H/A/D/X crossed with raw-ball-observed/missing, plus corruption-added missingness. In particular show the number and fraction of **known live H/A frames with naturally missing ball**. Aggregate missing counts alone cannot demonstrate that the new data address the near-constant-dead failure. Also show how much VID/CLK/clock-gap exclusions remove known live/dead supervision. Unknown exclusions can be non-random and make transfer scoring easier; this must remain explicit rather than be interpreted as full-match coverage.

The current state machine preserves provider assertions through ordinary raw-coordinate absence and clears them for specified time gaps/events. Its H/A/D values remain provider-derived labels, not hand-verified target truth. No rebalancing or relabelling is warranted from these descriptive cuts.

### Remaining audit corrections before the two modelling evaluations

1. **Conflict classification is not yet the promised separated report.** The revised `player_conflicts` uses unequal-NaN-aware comparison and no longer counts all-missing identical rows as conflicts, an improvement. It still combines a finite/missing disagreement with a genuine finite-coordinate disagreement. Within-list consensus is applied before the source-record comparison, so some within-list coordinate contradictions become NaN and disappear from the coordinate-conflict count. `within_list_repeats` measures repetitions, not their agreement. `event_association_only_duplicates` can therefore overstate clean annotation-only duplication. Report these cases separately or explicitly label existing counters as broad disagreements; do not claim the refined protocol's full classification is complete.
2. **Run provenance:** record the exact adapter source hash, protocol/amendment hashes, locked split hash and source manifest hash for the preparation process that actually loaded the code. A running Python process continues using its imported source even if the file is edited later. Feature archive hashes alone do not establish which observation/label contract produced them. Do not reuse stale smoothed or differently masked caches.
3. **Tests:** the visible test file covers events, consensus and a stand-alone gap sampler, but does not visibly exercise the full raw/VISIBLE field-selection path, duplicate timestamp failure, cumulative slope check, half-order reset or metadata mismatch through `load_pff`. Add small synthetic-loader fixtures for the actual contract paths before claiming all admission gates tested. This is correctness testing, not another performance experiment.
4. **Residual strictness:** fps must be explicitly finite, home/away IDs distinct, and period traversal contiguous/ordered. Validate finite core outputs/no infinities before caching. The known metadata inventory makes these unlikely empirical failures, but the current implementation does not enforce all of them. Separate a confirmed observed failure from a missing guard.
5. **Record resampling support denominators.** Nearest observation can use a later native frame while labels are past-only. Keep source-time offsets or equivalent aggregate boundary-contract evidence; quantify unknown and missing grid points by half. This avoids claiming exact native feature/label simultaneity.

### Updated recommendation

The main raw-observation leakage blocker is resolved in the source. Full64 preparation may continue under the locked raw policy; it should be treated as **admission evidence pending report/provenance/test completion**, not automatic model admission. Do not choose different duplicate or visibility policies from downstream scores. Once the all64 matrix and these checks are complete, there is no basis in this review for withholding the two authorized evaluations merely because PFF is a different provider. Preserve failures and fixed 48/16 membership, report provider/convention/missingness caveats, and keep production unchanged unless the train-more comparison passes both gates.

## Final admission assessment — November 7, after cohort lock d4b72ac

Reviewed only the published admission aggregates, snapshot/protocol, verification/preparation code and current adapter/tests. No source rows, target or sealed files were accessed; no model, score, cleanup or new data experiment was run by this reviewer. The two evaluation protocol is `e7cb0b1`.

**Decision: the published admission evidence is sufficient to proceed with the two authorized evaluations under the locked raw/VISIBLE-only policy. I found no new demonstrated blocker requiring the in-progress train-more comparison to stop.** This is permission to test a documented measurement contract, not a statement that PFF labels equal target possession truth or that more-data training will improve performance.

### Evidence resolving the earlier admission objections

- The published matrix attempts **all 64 matches**, records 64 passes and no replacements, and admits exactly the precommitted **48 training / 16 transfer** split.
- `snapshot.json` fingerprints the adapter, core/feature functions, admission protocol, provider split and release manifest. The reporting code verifies those source fingerprints, release files, prepared feature hashes, nine-column shapes, allowed labels and no infinite clean/corrupted features before creating the modelling cohort lock. This addresses the earlier risk of unknowingly using old smoothed caches.
- The source reads raw player/ball fields and VISIBLE coordinates, never `ballsSmoothed`. The additional loader fixture explicitly presents a misleading smoothed ball and an ESTIMATED raw ball and verifies that neither becomes an observed ball. The published test log reports **29 passing tests**.
- CLK/VID uncertainty and native-gap state resets remain implemented, and cumulative half video/frame agreement is checked. No unsupported CLK play meaning has been asserted as truth.
- Coordinate and presence/missing disagreements, within-list repeats and play/team assertion disagreements have separate reported counters. These are conservative consistency diagnostics; disagreement is not automatically provider error, and raw inputs having zero such contradictions in some matches is plausible because the documented duplicates expand event associations.

### The data contain relevant naturally missing live examples

The aggregate observation-support table reports:

| Provider state | Observed raw ball | Missing/conservatively unobserved raw ball |
|---|---:|---:|
| H | 1,888,600 | 1,020,197 |
| A | 1,815,129 | 1,001,799 |
| D | 354,561 | 3,649,128 |
| X | 561 | 787 |

Thus there are **2,021,996 known H/A frames with naturally unobserved ball**, not merely dead-ball examples. Missingness does not remove their valid provider labels. This is the strongest supported reason that the new source could address the existing model's near-constant-D response during gaps; the two modelling evaluations, not this table, determine whether that potential materializes.

“Natural missing” here includes source absence, non-VISIBLE coordinates and observations conservatively discarded by the fixed consensus rule. It should not be described as a pure camera-occlusion indicator. The table concerns the 25 Hz prepared representation and provider conventions, not human-verified game truth.

### Caveats that remain, without justifying post-hoc cleanup

1. Label coverage is extremely high but not literal completeness: the aggregate X support is 1,348 frames. CLK/VID/unsupported-gap handling can make exclusions non-random. Retain per-match coverage and unknown counts in transfer interpretation.
2. PFF “clean” data already contain substantial missing observations. Additional synthetic corruption can only increase missingness; its total missing rate need not match the target's observed rate. Report natural, newly masked and total missing subsets separately as the evaluation protocol requires. Do not rank providers by comparing their different clean/corrupted conditions as if the observation regimes were matched.
3. Nearest native observations and past-only labels may straddle transitions by a native frame. This is a fixed documented resampling choice, not perfect simultaneity. It remains an alignment/noise limitation, not grounds for changing the rule after scores arrive.
4. The visible tests do not exercise every malformed metadata, half-order and cumulative-clock path. Finite-fps/distinct-team/period-order defensive checks remain worthwhile engineering follow-up, but the reviewed 64-match verified cohort provides no observed invalid input demonstrating a new stop condition. Keep those safeguards distinct from an allegation of corrupt current data.
5. The code/snapshot checks are reproducibility evidence, not independent validation of provider annotation semantics. Event-defined ownership, dead-ball transitions and unknown intervals may differ from IDSSE. Provider transfer also changes competition/teams/camera coverage. A good or poor transfer score cannot isolate one cause.

### Evaluation interpretation

Keep the original five-match outer held-out IDSSE matches out of both parent and expanded training in comparison A. Its strengthened gate is the only promotion decision. Evaluation B must remain descriptive; no tuning, source cleanup, calibration, match replacement or version choice may depend on the 16 transfer matches. Both sealed IDSSE matches remain untouched and permanently excluded from training.

A's legacy known-label-run decoder resets and B's half-only inference are explicitly different in the preregistration. Do not present their score difference as an isolated provider effect. Once results are available, report per-match heterogeneity and live-gap recovery alongside the aggregate gate; no synthetic or admission result substitutes for performance evidence. Keep production at the current candidate unless A passes the full gate and clean-environment reproduction.
