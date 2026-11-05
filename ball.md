# Ball possession — project plan and running record

Created 2026-11-06, India time. This is the primary human-readable project memory. Read it before work and append important actions after each meaningful step. Detailed prior evidence: [audit](audit/DEEP_AUDIT_AND_IMPLEMENTATION_PLAN.md).

## Objective and current truth

Produce a reproducible algorithmic `frame,label` CSV for 199,319 tactical-video frames, plus a public source repository and technical document. Rank objective: spellF1; macroF1 is the first tie-break. Three contributors are confirmed. Match assets are not yet available (last user confirmation November 5); no new access has been reported. Existing reference files are starter material, not our implemented model.

The November 5/6 checkpoints in the earlier plan were planned, not completed. Reset the remaining work from November 6. Target submission November 16; published deadline November 17, exact cutoff/timezone unconfirmed. Registration status must be checked before the published November 10 close.

## Best current approach — a testable candidate

Use a local CPU-first pipeline:

`strict tactical adapter → masked geometric/context features → rules or CatBoost probabilities → soft Smart Tagging evidence → H/A/D Viterbi decoder → deterministic CSV → official validator`

Start with rules plus decoding as the fallback. Compare direct three-class CatBoost against a two-stage alternative (dead/live, then home/away while live). The previous recommendation of two classifiers was an engineering hypothesis, not established superiority. Missing-value support helps implementation but does not establish that CatBoost beats another model. Neither learned candidate has been trained here.

Make these decisions explicit:

- Model features: per-team nearest distances and margin, ball speed when observed, team movement/density, pitch-edge distance, observation masks and gap age, temporal summaries. No persistent player identity assumptions.
- Missing ball does not imply dead play. Infer stoppages using multiple signals; preserve last controlled ownership through uncertainty where warranted.
- Decoder: deterministic Viterbi with soft switching penalties, separate halves, no long hard minimum spell length. Add duration priors only after evidence supports them.
- Tags: offensive/defensive polarity, unknown/N/A neutral, restart intervals are soft evidence rather than exact restart instants. Do not blindly copy phase tags to possession labels.
- Local execution and pinned environment. Keep competition assets and reconstructive derivatives out of public source and hosted-model calls.
- TCN, broadcast synchronisation, ball reconstruction and a dashboard are deferred. Reopen only if the core is complete and validated before freeze.

## Three phases

### Phase 1 — establish trust and build a valid fallback (November 6–8)

Goal: prove the data/evaluation contracts and obtain one complete inference path.

1. Contributor A: resolve enrolment/data access; create strict frame, slot/team, coordinate and missingness contracts. Keep private assets outside public source.
2. Contributor B: build features, rule emissions, three-state decoder and exact CSV exporter using synthetic sequences while assets are pending.
3. Contributor C: verify IDSSE label semantics and load external matches; fix whole-match development/test splits before modelling; create the experiment harness using the unchanged scorer.
4. Test malformed IDs, partial NaNs, unknown teams, team-swap symmetry, short turnovers, live-ball gaps, moving dead balls, restarts and half boundaries.
5. When assets arrive, validate ATD frame_id−1, tag round(seconds×25), homography frame indexing and full-match output length. Regenerate a reference baseline for the first time; existing audit only rescored supplied CSVs.

Exit gate: synthetic contracts pass; full inference command and exporter exist; real full-match CSV passes the official validator when data is available. If assets remain missing, explicitly record partial completion rather than claiming this gate passed.

### Phase 2 — find which changes improve possessions (November 9–12)

Goal: select a defensible candidate on other matches, using a small set of hypothesis-driven comparisons.

1. Establish the rules fallback and raw/smoothed baselines on the same external matches.
2. Test sequence decoding independently of model changes (H1).
3. Train direct H/A/D CatBoost, then compare the dead/live + team factorisation (H2). Use identical features, splits and constrained search budgets.
4. Test burst-gap augmentation and missingness/context features (H3); report clean and corrupted settings separately.
5. Add Smart Tagging adapters and synthetic semantic tests (H4). External data may lack equivalent tags; do not invent measured target gains.
6. Inspect missed/spurious spells, dead/live errors, short-spell recall and boundary shifts. Log refutations as well as successes.
7. Freeze architecture/config/model choices November 12. Drop unfinished optional work.

Exit gate: selected candidate beats or offers a documented robustness advantage over fallback in development evidence; all contracts pass; model/config/input provenance recorded. If evidence is mixed or external labels unusable, retain fallback and say why. No promised hidden score.

### Phase 3 — verify, reproduce and deliver (November 13–16; November 17 buffer)

Goal: turn the frozen candidate into a verifiable submission.

1. Evaluate frozen candidate and fallback once on sealed external matches; do not reopen tuning based on those results.
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
    Phase 1 - trusted foundation and fallback :crit, 2026-11-06, 3d
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
- [ ] B: preregister and implement synthetic decoder contract experiment.
- [ ] A/B: strict loader and exporter tests.
- [ ] C: instantiate match splits and save hashes before learned experiments.

If external labels are unusable by the end of November 8, drop supervised training from the critical path. If competition assets remain absent November 9, report the delivery risk and prioritise a ready-to-run fallback. New research stops November 12; there is no value in an unverified late model.

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
