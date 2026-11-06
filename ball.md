# Ball possession — project plan and running record

Created 2026-11-06, India time. This is the primary human-readable project memory. Read it before work and append important actions after each meaningful step. Detailed prior evidence: [audit](audit/DEEP_AUDIT_AND_IMPLEMENTATION_PLAN.md).

## Objective and current truth

Produce a reproducible algorithmic `frame,label` CSV for 199,319 tactical-video frames, source code and a technical document. Rank objective: spellF1; macroF1 is the first tie-break. Three contributors are confirmed. Publication/submission requires user instruction. Existing reference files are starter material, not our implemented model.

- Inputs: tactical video, tracking, homography, ATD metadata and Smart Tagging now available and locally validated. Optional broadcast has a homography numeric failure and missing team metadata. Real tactical feature arrays materialised; no fitted candidate.

The November 5/6 checkpoints in the earlier plan were planned, not completed. Reset the remaining work from November 6. Target submission November 16; published deadline November 17, exact cutoff/timezone unconfirmed. Registration status must be checked before the published November 10 close.

## Best current approach — a testable candidate

Use a local CPU-first pipeline:

`strict tactical adapter → masked geometric/context features → learned probabilities → soft Smart Tagging evidence → H/A/D Viterbi decoder → deterministic CSV → official validator`

User instruction November 6: do not build a separate fallback. Build the main learned-model pipeline directly; use supplied baselines only as evaluation comparators. Compare direct three-class CatBoost against a two-stage alternative (dead/live, then home/away while live). The previous recommendation of two classifiers was an engineering hypothesis, not established superiority. Missing-value support helps implementation but does not establish that CatBoost beats another model. Neither learned candidate has been trained here.

Make these decisions explicit:

- Model features: per-team nearest distances and margin, ball speed when observed, team movement/density, pitch-edge distance, observation masks and gap age, temporal summaries. No persistent player identity assumptions.
- Missing ball does not imply dead play. Infer stoppages using multiple signals; preserve last controlled ownership through uncertainty where warranted.
- Decoder: deterministic Viterbi with soft switching penalties, separate halves, no long hard minimum spell length. Add duration priors only after evidence supports them.
- Tags: offensive/defensive polarity, unknown/N/A neutral, restart intervals are soft evidence rather than exact restart instants. Do not blindly copy phase tags to possession labels.
- Local execution and pinned environment. Keep competition assets and reconstructive derivatives out of public source and hosted-model calls.
- TCN, broadcast synchronisation, ball reconstruction and a dashboard are deferred. Reopen only if the core is complete and validated before freeze.

## Three phases

### Phase 1 — validate inputs and build the main pipeline foundation (November 6–8)

Goal: prove the data/evaluation contracts and obtain one complete inference path.

1. Contributor A: resolve enrolment/data access; create strict frame, slot/team, coordinate and missingness contracts. Keep private assets outside public source.
2. Contributor B: build features, learned-emission interface, three-state decoder and exact CSV exporter using synthetic sequences while assets are pending.
3. Contributor C: verify IDSSE label semantics and load external matches; fix whole-match development/test splits before modelling; create the experiment harness using the unchanged scorer.
4. Test malformed IDs, partial NaNs, unknown teams, team-swap symmetry, short turnovers, live-ball gaps, moving dead balls, restarts and half boundaries.
5. When assets arrive, validate ATD frame_id−1, tag round(seconds×25), homography frame indexing and full-match output length. Regenerate a reference baseline for the first time; existing audit only rescored supplied CSVs.

Exit gate: synthetic contracts pass; full inference command and exporter exist; real full-match CSV passes the official validator when data is available. If assets remain missing, explicitly record partial completion rather than claiming this gate passed.

### Phase 2 — find which changes improve possessions (November 9–12)

Goal: select a defensible candidate on other matches, using a small set of hypothesis-driven comparisons.

1. Establish supplied raw/smoothed baselines on the same external matches.
2. Test sequence decoding independently of model changes (H1).
3. Train direct H/A/D CatBoost, then compare the dead/live + team factorisation (H2). Use identical features, splits and constrained search budgets.
4. Test burst-gap augmentation and missingness/context features (H3); report clean and corrupted settings separately.
5. Add Smart Tagging adapters and synthetic semantic tests (H4). External data may lack equivalent tags; do not invent measured target gains.
6. Inspect missed/spurious spells, dead/live errors, short-spell recall and boundary shifts. Log refutations as well as successes.
7. Freeze architecture/config/model choices November 12. Drop unfinished optional work.

Exit gate: selected candidate beats or offers a documented robustness advantage over supplied baselines in development evidence; all contracts pass; model/config/input provenance recorded. If evidence is mixed or external labels unusable, retain the best validated main candidate, or report that selection remains blocked. No promised hidden score.

### Phase 3 — verify, reproduce and deliver (November 13–16; November 17 buffer)

Goal: turn the frozen candidate into a verifiable submission.

1. Evaluate frozen candidate and supplied baselines once on sealed external matches; do not reopen tuning based on those results.
2. Run full target inference locally when assets are available; validate the exact final CSV.
3. Reproduce in a clean supported environment, twice, requiring byte-identical CSV hashes.
4. Prepare source, dependency lock, model/config hashes, one regeneration command, licence attribution, and a short technical document with training sources and limitations.
5. Check public-source exclusions and the three deliverables. Team lead reviews and submits November 16; preserve receipt and final hashes. External publication/submission requires an explicit user instruction.

Exit gate: exact CSV validates and reproduces, technical document is complete, repository is reviewable, submission receipt exists after the team submits. November 17 is contingency only.

```mermaid
gantt
    title Three phases — November 2026
    dateFormat YYYY-MM-DD
    axisFormat %d %b
    Phase 1 - main pipeline foundation :crit, 2026-11-06, 3d
    Phase 2 - experiments and selection :2026-11-09, 4d
    Architecture freeze :milestone, 2026-11-12, 0d
    Phase 3 - verification and delivery :crit, 2026-11-13, 4d
    Target submission :milestone, 2026-11-16, 0d
    Deadline buffer :2026-11-17, 1d
```

## Evaluation contract

- Never train, calibrate, choose thresholds/models or tune durations against competition public labels. They support pipeline correctness and label semantics only.
- External labels: verify ballstatus and possession code meanings; exclude unsupported frames; avoid leaking target ownership/status or unavailable event-derived labels into inputs.
- With seven usable external matches: seal two matches; use the other five for grouped development. Record actual match IDs before fitting. Do not pretend these splits are already instantiated.
- Fit preprocessing/calibration inside training folds. Never randomly split neighbouring frames. Compare per-match spellF1 (mean over IoUs 0.3/0.4/0.5/0.6/0.7), macroF1, dead/live quality, boundary latency and runtime.
- Fixed corruption seeds and burst masks; no claiming a random 41% dropout simulates all target noise. Keep synthetic correctness scores separate from external performance and hidden target outcomes.
- Promotion: positive median paired development-match spellF1 change, improvement on a majority of development matches, no median macroF1 drop greater than 0.01, and all correctness tests passing. These are proposed engineering gates, not statistical significance claims. Lock the exact gate in each protocol before running.
- Retain failed/negative experiments and budget/runtime. Reassess after three comparisons or immediately when a core assumption fails.

## Hypothesis queue

| ID | Change and mechanism | Prediction | Comparator | Status |
|---|---|---|---|---|
| H1 | Temporal decoder suppresses unsupported flicker | Higher external spellF1 without eliminating short supported spells | Same emissions, argmax or fixed smoothing | Pending |
| H2 | Separate dead/live and ownership decisions isolate distinct errors | Factorised CatBoost improves spellF1/dead-live tradeoff | Direct three-class CatBoost, matched budget | Pending |
| H3 | Burst augmentation and gap-age/context reflect structured occlusions | Better corrupted-match spellF1 with limited clean-score loss | Same model without augmentation | Pending |
| H4 | Event semantics provide controlled restart/team priors | Correct synthetic polarity/restart handling; field benefit unknown | No tag evidence | Pending |

## Immediate next actions

- [ ] A: establish data access and registration status.
- [ ] C: download and decode one external match, then audit target-label availability.
- [x] B: preregister and implement synthetic decoder contract experiment (J006).
- [ ] A/B: strict loader and exporter tests.
- [ ] C: instantiate match splits and save hashes before learned experiments.

If external labels are unusable by the end of November 8, report the main-model training dependency and investigate compatible external labels; do not silently build a fallback. If competition assets remain absent November 9, report the delivery risk and prioritise the main pipeline input contracts. New research stops November 12; there is no value in an unverified late model.

## Append-only journal rules

Append an entry after every meaningful decision, implementation step, experiment, blocker change or user correction. Never rewrite past results to match a newer interpretation; append a correction referencing the earlier entry. Use India dates/times when known; never invent historical timestamps.

Each entry records: ID/date, provenance (user / AI proposal / executed evidence), phase, action, evidence paths or URLs, result, limitations, decision and next step. Clearly distinguish proposed, running, completed and blocked. Model score claims require a saved result and reproducible command. Log protocol commit before experiment execution; save results in a separate later commit. Keep brief state mirrors in research-state.yaml and findings.md; ball.md remains the main entry point.

## Journal

### J001 — 2026-11-04 — prior audit, executed evidence

Reviewed the supplied PDF and starter archive. Four supplied baseline CSVs validated; public scores reproduced. Evidence: audit/evaluation/scoreboard.csv, audit/validation.txt, audit/source-integrity.json, audit/probe-results.json. Found silent acceptance of duplicate IDs, partial-NaN player errors, unsafe raw ID indexing, and unordered homography loading. These are synthetic demonstrations, not proof the real bundle is corrupt. No baseline regenerated from tracking; no trained model.

### J002 — 2026-11-05 — user constraints

User confirmed three contributors and no separate match bundle. Updated the earlier audit plan. Actual availability/hours and registration status are still unknown.

### J003 — 2026-11-06 — AI proposal, untested

Recommended CatBoost with H/A/D sequence decoding, supported by implementation fit rather than measured superiority. Corrected the earlier implication that two classifiers are established best: compare factorised and direct targets. Main delivery dependency remains real assets. Primary sources retained in literature/survey.md.

### J004 — 2026-11-06 — user request and executed planning

User invoked autoresearch, requested exactly three project phases and an ongoing ball.md record. Created this plan and companion research memory. Configured a 20-minute Codex chat heartbeat under the skill's continuity instruction. It must avoid repeated blocked checks and report meaningful changes only. No external model experiment or implementation result is claimed by this setup. Next: Phase 1 external-data adapter and preregistered synthetic decoder tests.

### J005 — 2026-11-06 — executed setup and preregistration

Initialised local git history (initial plan commit e35f1bf). Wrote the H1 synthetic decoder contract protocol before implementation/execution, including isolated noise, short supported possession, stoppage, half isolation and deterministic symmetry fixtures. Status: not run. Protocol: experiments/h1-decoder-contracts/protocol.md. Created to_human/three-phase-plan.html as a planning report. No improvement trajectory or competitive score exists yet. Next: implement and run this locked contract experiment, or verify external-label loading; record actual results in a later commit.

### J006 — 2026-11-06 — executed evidence, Phase 1

Implemented deterministic H/A/D Viterbi decoding with independent half-open blocks, strict input validation and X outside blocks. Ran the preregistered H1 contract experiment after protocol commit 14385bb: 6/6 confirmatory and 3/3 exploratory tests passed (9 total, 0.228 s unittest runtime). Exploratory tests include an exhaustive small-sequence optimum oracle. Evidence: experiments/h1-decoder-contracts/results/run.json, results/test-output.txt and analysis.md; code: src/possession/decode.py; fixtures: tests/test_decode.py. No training or target data used. H1 external-performance claim remains pending; this is one tested component, not a full inference pipeline. Next: strict adapters/exporter or external label loading.

### J007 — 2026-11-06 — user scope change and input inventory

User removed the separate fallback track, requested Phase 1 work and a last30days search for better available methods, and supplied Archive.zip. Inventory: five nested dataset zips and one tactical video (excluding macOS metadata); nested zips hold tactical/broadcast raw ATD and homographies plus a README. No ATD metadata XML or Smart Tagging XML is present. Do not infer missing teams or read restricted contents into hosted context. Updated current plan; earlier journal entries remain historical. New Phase 1 contract protocol committed before execution.

### J008 — 2026-11-06 — executed Phase 1 foundation

After protocol commit 736dc98, implemented strict adapters, safe nested extraction/provenance, missingness-aware metre-scaled team features, deterministic CSV export and local preparation commands. Final run: 7 new confirmatory methods, 2 new exploratory methods, 9 existing decoder tests, all 18 passed in 0.228 s. Evidence: experiments/phase1-ingestion-contracts/results/run.json and test-output.txt. Real tactical ATD/homography/video-header checks pass; full video decode not tested. Initial validation incorrectly used tactical length for broadcast; corrected to published 164488-frame broadcast timeline and reran only changed broadcast checks. Raw broadcast then passed, but its valid-row homography numeric contract still fails. Keep optional broadcast excluded; do not infer corruption of passing raw data. No scorer modifications, training, predictions or target-label tuning.

### J009 — 2026-11-06 — executed recent-method research and decision

Ran last30days v3.31.0 for October 7-November 6 plus primary paper/code inspection. Most returned social/code matches concerned other tasks; do not treat counts as supporting evidence. PathCRF has pretrained variants but assumes known in-play episodes, rejects incomplete selected-player features, and requires player-trajectory adaptation; pretrained Sportec evaluation risks overlap unless exact split provenance is audited. New October 8 GNN-LSTM paper takes possession/ball-status inputs, so it does not solve our missing-label problem. Decision: retain CatBoost plus decoding as first main candidate, not a proven best model and not a fallback; PathCRF deferred behind an explicit compatibility experiment. Evidence/URLs: literature/recent-methods-2026-11-06.md, last30days-engine-output.txt. No external checkpoint executed.

### J010 — 2026-11-06 — new user input and completed tactical preparation

User supplied BAR-ATH_tactical_smart_tagging.xml; local interval validation passed. A filename-only search located tactical ATD metadata in Downloads/More Than A Hack 2027 - Initial Challenge - Dataset/tactical. Copied both into ignored data/competition with private source hashes. Metadata team/slot checks passed; generated data/competition/derived/tactical_features.npz locally. Shape, no-infinity and half-reset checks passed; no raw/derived rows exposed to hosted context. All required tactical assets are now available. Optional broadcast metadata is still absent. Updated three-phase report and current memory; no separate fallback. Phase 1 remains partial until external-label loading/splits and learned inference are established. Next: external label adapter and split provenance, preregister before model experiments. Automation remains paused as found; not re-enabled.

### J011 — 2026-11-06 — user-requested expanded method search

Executed another last30days run plus primary-paper/code searches. Additional serious leads: TranSPORTmer (ACCV 2024) supports masked trajectory inputs and global state classification; WACV 2026 multimodal CropDrop model reports higher possessor/state accuracy than BallRadar/TranSPORTmer on its own proprietary data. Critical limitation: its evaluation excludes out-of-play sequences, so its state accuracy is not a live/dead result. Public usable checkpoints/code for these two were not verified. BallRadar has public training code and Metrica reproduction path; pretrained availability unverified. No relevant last-30-day result established superiority over the current project candidate. Correct framing: CatBoost is a practical candidate, not the research state of the art. Expanded neural shortlist, no architecture switch or experiment executed. Evidence: literature/expanded-model-review-2026-11-06.md and expanded-model-search-output.txt. Next: verify external labels/splits before comparisons.

### J012 — 2026-11-06 — separately supplied tracking and homography confirmed

User supplied Downloads/BAR-ATH_tactical_atd.txt and Downloads/BAR-ATH_tactical_homography.csv. Local SHA256 comparison confirms both are byte-identical to the archive inputs already validated and used for feature preparation. Private comparison record: data/competition/additional-file-comparison.json. No replacement or redundant schema run needed; no asset contents exposed. Tactical readiness and next action (external labels/splits) unchanged.

### J013 — 2026-11-06 — user-directed core implementation and preregistration

User fixed the architecture to strict adapters, masked core features, CatBoost, Viterbi and deterministic CSV. No optional change before error evidence; same splits/seeds/budget; promotion gate mandatory; stop after three consecutive rejections. Protocol commit 6b71d10 fixes five leave-one-match-out development folds (J03WMX, J03WN1, J03WOH, J03WOY, J03WPY); sealed J03WQQ/J03WR9 will not be downloaded or opened. Development acquisition running. Implemented core/DFL adapter, training and export commands; 21 synthetic tests passed after correcting floating-point comparison at the exact -0.01 gate boundary with 1e-12 tolerance. No measured model score yet. Capsule advisor failed twice; ordinary local tools used. Next: complete acquisition, validate external adapter and run baseline.
| Match | Condition | spellF1 | macroF1 | Missed@.5 | Spurious@.5 | Short recall@.5 | Dead/live errors |
|---|---|---:|---:|---:|---:|---:|---:|
| J03WMX | clean | 0.322746 | 0.875081 | 277 | 741 | 0.28865979381443296 | 181 |
| J03WMX | corrupted | 0.192753 | 0.729203 | 373 | 924 | 0.211340206185567 | 23363 |
| J03WN1 | clean | 0.352838 | 0.854724 | 254 | 628 | 0.36627906976744184 | 294 |
| J03WN1 | corrupted | 0.218022 | 0.719923 | 369 | 734 | 0.2441860465116279 | 19520 |
| J03WOH | clean | 0.298719 | 0.865841 | 211 | 734 | 0.3063063063063063 | 264 |
| J03WOH | corrupted | 0.190335 | 0.736050 | 278 | 819 | 0.25225225225225223 | 19175 |
| J03WOY | clean | 0.272973 | 0.845957 | 263 | 831 | 0.2748091603053435 | 364 |
| J03WOY | corrupted | 0.161771 | 0.715872 | 348 | 927 | 0.22900763358778625 | 20642 |
| J03WPY | clean | 0.340826 | 0.883962 | 211 | 579 | 0.24193548387096775 | 240 |
| J03WPY | corrupted | 0.189080 | 0.754324 | 312 | 752 | 0.18548387096774194 | 20570 |


### J014 — 2026-11-06 — baseline and first promotion

Core baseline completed five leave-one-match-out folds, clean/corrupted. Per-match table above; exact errors/config in experiments/core-development/core. Change 1 (protocol b457d96): switching penalty 2 to 8 passed the gate on all five matches. Median paired spellF1 gain +0.136625; median macroF1 gain +0.024777. Keep penalty 8; no minimum duration. Same trained emissions reused. Table follows. Remaining frequent error: corrupted dead/live classification. Next targeted proposal: one ball-independent mean-player-speed feature, computed only from consecutive observed xy within each half.
| Match | Condition | spellF1 | macroF1 | Missed@.5 | Spurious@.5 | Short recall@.5 | Dead/live errors |
|---|---|---:|---:|---:|---:|---:|---:|
| J03WMX | clean | 0.499781 | 0.902245 | 281 | 173 | 0.14948453608247422 | 127 |
| J03WMX | corrupted | 0.266783 | 0.751594 | 368 | 493 | 0.14948453608247422 | 23320 |
| J03WN1 | clean | 0.496432 | 0.873339 | 267 | 192 | 0.20930232558139536 | 228 |
| J03WN1 | corrupted | 0.281809 | 0.731619 | 362 | 401 | 0.13953488372093023 | 19487 |
| J03WOH | clean | 0.527205 | 0.894625 | 189 | 190 | 0.17117117117117117 | 152 |
| J03WOH | corrupted | 0.296951 | 0.760070 | 264 | 411 | 0.15315315315315314 | 19131 |
| J03WOY | clean | 0.483060 | 0.874689 | 231 | 234 | 0.183206106870229 | 281 |
| J03WOY | corrupted | 0.255513 | 0.738953 | 330 | 470 | 0.16030534351145037 | 20580 |
| J03WPY | clean | 0.536352 | 0.903977 | 199 | 152 | 0.1935483870967742 | 119 |
| J03WPY | corrupted | 0.266804 | 0.772056 | 297 | 428 | 0.13709677419354838 | 20477 |

Gate (tests must separately pass): {"promoted": true, "paired_spell_deltas": {"J03WMX": 0.12553288293933146, "J03WN1": 0.10369072930457524, "J03WOH": 0.16755102997323384, "J03WOY": 0.15191491027949028, "J03WPY": 0.13662494584578377}, "paired_macro_deltas": {"J03WMX": 0.02477731425591223, "J03WN1": 0.015155335353252974, "J03WOH": 0.026401588704415002, "J03WOY": 0.025906507197535178, "J03WPY": 0.018873754075304228}}


### J015 — 2026-11-06 — rejected mean-player-speed feature

Change 2, protocol 967acb0: mean observed player speed failed promotion. Only 2/5 paired match spellF1 improvements, median delta -0.001331; macroF1 median +0.000564. Reject from production, retain experiment code/results for reproducibility. Consecutive rejection count: 1. Per-match table follows. Current best remains core features + penalty8. Error review also shows short-spell recall fell in all clean matches after penalty8 (e.g. J03WMX .289 to .149), supporting one targeted over-merging test.
| Match | Condition | spellF1 | macroF1 | Missed@.5 | Spurious@.5 | Short recall@.5 | Dead/live errors |
|---|---|---:|---:|---:|---:|---:|---:|
| J03WMX | clean | 0.504044 | 0.905028 | 279 | 172 | 0.17010309278350516 | 125 |
| J03WMX | corrupted | 0.259859 | 0.752777 | 374 | 488 | 0.12886597938144329 | 23241 |
| J03WN1 | clean | 0.503784 | 0.872646 | 263 | 188 | 0.19767441860465115 | 248 |
| J03WN1 | corrupted | 0.296799 | 0.741701 | 352 | 383 | 0.13372093023255813 | 18360 |
| J03WOH | clean | 0.529514 | 0.895636 | 187 | 186 | 0.1981981981981982 | 233 |
| J03WOH | corrupted | 0.296109 | 0.759357 | 264 | 411 | 0.15315315315315314 | 18985 |
| J03WOY | clean | 0.479023 | 0.874517 | 236 | 225 | 0.16030534351145037 | 329 |
| J03WOY | corrupted | 0.247328 | 0.740253 | 337 | 473 | 0.11450381679389313 | 20538 |
| J03WPY | clean | 0.518217 | 0.900732 | 217 | 160 | 0.1693548387096774 | 131 |
| J03WPY | corrupted | 0.254735 | 0.770340 | 306 | 425 | 0.11290322580645161 | 20414 |

Gate: {"tests_passed": true, "promoted": false, "paired_spell_deltas": {"J03WMX": -0.001330611393443093, "J03WN1": 0.011170571629686599, "J03WOH": 0.0007340662911897722, "J03WOY": -0.006110932781708545, "J03WPY": -0.01510234462037291}, "paired_macro_deltas": {"J03WMX": 0.0019830228775348235, "J03WN1": 0.004694436125618484, "J03WOH": 0.0001489851308605905, "J03WOY": 0.0005638503486049551, "J03WPY": -0.0024805172517867735}}


### J016 — 2026-11-06 — rejected short-turnover adjustment and stopped additions

Change 3, protocol f765bf3: H/A switching cost4 with D transitions8 failed on all five matches, median paired spellF1 delta -0.054448 and median macroF1 delta -0.008120. Tests passed. Reject; current best remains uniform penalty8. Consecutive rejected changes: 2. Stopping because each supported frequent error category has received its one targeted test; lookahead lacks matching late-boundary evidence. The three-consecutive-rejection ceiling was not reached. Rejected mean-speed code moved out of production into experiment archive; production predictor rejects that feature configuration. Table follows.
| Match | Condition | spellF1 | macroF1 | Missed@.5 | Spurious@.5 | Short recall@.5 | Dead/live errors |
|---|---|---:|---:|---:|---:|---:|---:|
| J03WMX | clean | 0.440181 | 0.894418 | 270 | 353 | 0.21649484536082475 | 127 |
| J03WMX | corrupted | 0.234334 | 0.743181 | 372 | 649 | 0.16494845360824742 | 23320 |
| J03WN1 | clean | 0.456526 | 0.867015 | 242 | 353 | 0.31976744186046513 | 227 |
| J03WN1 | corrupted | 0.260708 | 0.726571 | 358 | 544 | 0.21511627906976744 | 19487 |
| J03WOH | clean | 0.431496 | 0.883597 | 185 | 397 | 0.26126126126126126 | 152 |
| J03WOH | corrupted | 0.259567 | 0.749261 | 261 | 565 | 0.21621621621621623 | 19131 |
| J03WOY | clean | 0.373559 | 0.857557 | 238 | 506 | 0.2748091603053435 | 281 |
| J03WOY | corrupted | 0.210510 | 0.725432 | 335 | 679 | 0.22900763358778625 | 20580 |
| J03WPY | clean | 0.459227 | 0.895341 | 201 | 291 | 0.23387096774193547 | 119 |
| J03WPY | corrupted | 0.235032 | 0.766138 | 305 | 542 | 0.16129032258064516 | 20477 |

Gate: {"tests_passed": true, "promoted": false, "paired_spell_deltas": {"J03WMX": -0.0460244974660356, "J03WN1": -0.030503974472165185, "J03WOH": -0.06654634864347708, "J03WOY": -0.0772522705501913, "J03WPY": -0.05444799795092592}, "paired_macro_deltas": {"J03WMX": -0.008119984056398577, "J03WN1": -0.005686018730243103, "J03WOH": -0.010918228696249366, "J03WOY": -0.015326543095595335, "J03WPY": -0.007277203495620221}}


### J017 — 2026-11-06 — Phase 1 complete, selected candidate generated

Completed strict adapters → nine masked core features → CatBoost H/A/D probabilities → Viterbi (uniform switch cost8) → deterministic CSV. Final model trained on five development matches only. Local target candidate: data/competition/predictions/candidate.csv, 199319 frames; official schema validator passed. Saved-model reload and fresh probability/decoder execution produced byte-identical candidate-repeat.csv. 23 tests passed; all 34 reference files unchanged; sealed match assets absent. Evidence: experiments/core-development/completion.json; private target hashes/validation in predictions/provenance.json and official-validation.txt. Mean development clean spellF1/macroF1 and corrupted metrics are recorded in completion.json; per-match tables above. No target quality score or sealed generalisation claim. Kept only penalty8; rejected mean speed and short-turnover cost4. Earlier broader architectural/feature queues are superseded by the user's core-only, error-driven scope. Phase 1 implementation complete; next is review of this development-selected candidate and future phase work without opening sealed matches unless explicitly authorised.


### J018 — 2026-11-06 — Authorized GitHub delivery
User explicitly requested direct delivery to dhrooovvv/football main, using Git author name dhroovvv. Checked tracked history: competition assets, local models, audit environment and reference starter remain excluded. Publishing implementation and research records only; no competition submission.


### J019 — 2026-11-06 — Status review and ongoing journal maintenance

User reaffirmed that important decisions, actions, evidence, failures and next steps must be appended here. Preserve earlier journal entries; later dated corrections take precedence over stale summaries.

- GitHub delivery completed: origin/main at 9ae2ab7 after implementation commit 6056397; author name configured as dhroovvv. Private assets and model files excluded.
- Phase 1 exit gate passed according to recorded evidence in experiments/core-development/completion.json: 23 tests, official CSV validation, identical saved-model regeneration, 199319 output frames. This status review inspected code and records; it did not rerun tests or inference.
- Selected candidate remains nine core features + CatBoost + uniform Viterbi penalty8. Mean development clean spellF1/macroF1: 0.508566/0.889775; fixed-corruption: 0.273572/0.750858. Penalty8 improved all five paired matches; median paired spellF1 gain 0.136625. Mean-speed and asymmetric short-turnover changes rejected. Two consecutive rejections, not three; additions stopped because supported candidate categories were exhausted.
- Correctness checks establish tested contracts and export validity, not competition accuracy. Corruption robustness remains weak; sealed generalisation and target quality remain unmeasured. No target public-label tuning, sealed evaluation or competition submission occurred.
- Documentation review found stale zero-external-run statements and a null baseline mirror. Older broad feature/model queues are superseded by the user's core-only error-driven scope. Reconcile current summaries without rewriting historical journal entries.
- Next: focused correctness review and clean-environment reproduction (not yet executed); any subsequent experimental change requires a committed protocol and the existing paired promotion gate. Freeze architecture November 12; November 13–16 reserved for frozen evaluation, reproducibility and packaging. Keep sealed matches closed during development. Automation remains paused.


### J020 — 2026-11-06 — Frozen diagnostics, grid audit and pending proposal
Protocol d61a02f committed before execution. Frozen target inference and unchanged public scorer executed once solely for alignment checks; score/details remain private under data/diagnostics-review/public-score.json, excluded from selection. No target rows printed. Frame indexing, explicit named teams, direction invariance, configured metric scaling and X outside configured graded blocks pass contracts. Public score cannot independently prove semantic correctness.
Label-free target gap bootstrap refitted: missing fraction .4069, missing-run median268/p90 845.3/max5537 frames; original25–100-frame gaps were too short. External ball-speed median1.1757 versus target5.0818m/s signals feature shift. Fixed seeds and original player corruption retained; empirical alternating runs do not model conditional missingness. All target run lists and detailed distributions remain private.
Frozen penalty8 mean clean spellF1/macroF1 .508566/.889775; target-like .312864/.672865. Corruption settings changed, so do not directly compare old/new corrupted scores for promotion. Same-match baseline raw/smooth25/50/125 and nearest+decoder completed. Best smoothed baseline50: clean .296145/.384029; target-like .196645/.438793. Full per-match metrics, missed/spurious, short recall, boundary quantiles and oracle repairs in experiments/diagnostics-review/results.json and summary.md.
Penalty8 was upper grid edge;16 and32 evaluated.16 passes gate (3/5 improve, median paired spell +.010056, macro +.006132);32 fails. Production remains8 pending review; no combined change applied.23 tests pass. Execution-order deviation: grid computations ran alongside Step2, before Step3 baselines and final taxonomy; primary four diagnostic steps themselves ran in order. Scorer unchanged; sealed matches untouched.
Clean wrong-team/ownership oracle repair dominates all5; target-like wrong-team dominates3/5, dead/live2/5, with27k–34k dead/live wrong frames. Categories overlap; unique causal spellF1 attribution is not proven. Boundary medians zero describe matched typed boundaries only. One proposal preregistered: seeded half of training feature samples replaced by target-pattern corrupted features, same total samples/features/CatBoost/decoder budget. See proposed-gap-training.md. NOT approved or executed; wait for user approval and confirm parent, avoiding combined grid/augmentation changes.
Documentation append initially failed under system Python missing numpy; no diagnostic failed. Corrected using project environment.
