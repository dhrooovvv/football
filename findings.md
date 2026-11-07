# Research findings

## Current understanding
Possession ranking depends on whole H/A spells; stoppage mistakes and flickering can damage it even when frame scores appear reasonable. Missing observations are not dead-ball labels. The supplied baselines score reproducibly, and the complete CatBoost inference pipeline is now implemented and trained on external development matches. The input/feature/export foundation and decoder pass 18 synthetic tests. Tactical inputs validate and real label-free features are materialised locally.

## Evidence
See ball.md J001 and audit/evaluation/scoreboard.csv. Prior supplied-file public spellF1 values: raw 0.0378, smooth25 0.2868, smooth50 0.3256, smooth125 0.4242. These are pipeline-check measurements, not a tuning leaderboard. Synthetic audit faults are retained in audit/probe-results.json.

## Working direction
User removed the fallback track on November 6. Work now targets the main model pipeline directly. CatBoost + Viterbi is the first learned candidate, conditional on external labels. Direct and factorised prediction need comparison. No current evidence proves either superior. Full-ball reconstruction adds an intermediate problem whose benefit is unmeasured.

## Lessons and constraints
Never tune against target public labels or claim a hidden score. Whole-match splits and structured occlusion tests are required. Preserve short possessions. Keep target-only Smart Tagging separate from external model performance claims. Read ball.md before work and append evidence after meaningful actions.

## Open questions
Registration; external label completeness; contributor availability; domain shift; runtime; exact official cutoff. No optimisation trajectory exists yet: two synthetic correctness experiment protocols completed; external performance runs = 0.

## H1 contract result (November 6)
Six confirmatory and three exploratory tests passed. The tested decoder preserves strongly supported short spells and removes the prescribed ambiguous flicker. Exhaustive enumeration checks agree on ten small exploratory sequences. This supports component correctness, not external spellF1 improvement. Evidence: experiments/h1-decoder-contracts/analysis.md.

## November 6 input and method update

All main tactical assets now available. Archive supplied tracking, homographies and tactical video; user supplied Smart Tagging separately; tactical ATD metadata found in the extracted Downloads dataset folder. Tactical input checks and feature materialisation pass. Optional broadcast homography fails the valid-row numeric contract; optional broadcast metadata is absent. Neither blocks tactical feature preparation. No labels trained on, predictions generated, or hosted asset inspection.

Recent-method review: retain CatBoost plus temporal decoding as the first candidate, not a measured winner. PathCRF assumes known live episodes and needs stable, complete player trajectories; its pretrained Sportec split must be audited before independent scoring. October 8 GNN-LSTM paper consumes possession/ball status, so it solves a different task. See literature/recent-methods-2026-11-06.md. No newer method has been demonstrated better for this project.

Phase 1 is complete: external adapter, locked splits, core training, development evaluation and deterministic target export are executed. Existing paused automation remains paused.

Expanded review (J011): TranSPORTmer and multimodal CropDrop are serious additional neural leads. CropDrop reports higher related-task accuracy on proprietary data but excludes out-of-play sequences; usable checkpoints/code unverified. CatBoost is practical, not established state of the art. See literature/expanded-model-review-2026-11-06.md.

J012: separately supplied tactical ATD and homography match the validated archive copies byte-for-byte; existing tactical feature preparation remains applicable.

## Completed core development experiment

Five development matches, leave-one-match-out; two sealed matches never downloaded. Core plus switching penalty8 promoted on all five paired development matches. Mean-player-speed and reduced H/A switching penalty both rejected. Final production uses only the nine core columns. 23 tests pass and target CSV passes the official schema validator with identical saved-model regeneration. See experiments/core-development/completion.json and per-match summaries. Development corruption still materially hurts quality; no sealed or target performance measurement exists.


## Status clarification — November 6 (J019)
Earlier zero-external-run and no-prediction statements describe earlier work and are superseded by the completed core experiment: four external performance runs and a validated target export. Clean-environment reproduction remains pending; current checks do not establish sealed or target accuracy. Current scope is the nine-feature pipeline and error-driven promotion gate, not the older broad architecture queue.


## J020 frozen diagnostics
Target contracts pass; public score private and excluded from selection. Empirical target gaps greatly exceed original corruption. Same-match baselines trail frozen CatBoost. Ownership and dead/live errors dominate oracle repairs; categories overlap. Penalty16 passes expanded-grid gate; production remains8 pending review. One training-gap augmentation protocol is proposed, not approved or executed. Full per-match evidence: experiments/diagnostics-review/summary.md.


## J021 approved augmentation completed
Both isolated changes pass the unchanged paired gate: augmentation at8 (4/5, median spell+.003268, macro-.001228) and decoder16 without augmentation (3/5,+.010056,+.006132). Selected config now16; augmentation8 retained separately, no combined test. TargetCSV remains previous8 artifact. Corruption fidelity35.7–47.5% missing vs target40.7%; independent training/evaluation seeds and raw-mask feature consistency audited. Label shares/durations suggest convention or domain differences requiring caution, not a proven mapping error. See experiments/gap-augmentation/report.md. Stopped as requested.


## J022 combined16 rejected
Augmentation16 fails gate:2/5 improve, median spell-.001331, macro-.000708. Drop augmentation; simpler penalty16 stays selected. Target label-free output36.56%H/21.48%A/41.95%D,467 H/A spells averaging7.90s, not accuracy evidence. Whole-pitch bundle preregistered but unapproved/unrun; see experiments/combined16/report.md. Stop; freeze November12 unchanged.


## J023 — November7 finalization
Rolling whole-pitch bundle failed both gates (median corrupted spell-.005208; paired-.006600;1/5 improve), dropped and feature additions stopped. Final unaugmented nine-core penalty16 targetCSV regenerated, officially validated, identical across two full runs plus clean-venv rebuild/retrain/inference. CSVsha256 ab253e43f46fc9a7885b689498a220595e78d67ad2a6099a07316e081ca3f815. Technical draft docs/technical-report.md started.25 experiment tests/23 final production tests pass. Sealed and target quality unmeasured; no public labels this round.


## November7 authorized extension
Freeze moved toNovember13, delivery14–16. Production9core unaugmented16 remains. Track1 audit:0new verified compatible matches; train-more/transfer unavailable, PFF access requested from user. Decoder track3consecutive failures stops before calibration. CPUthread1 matches old CSV across clean environment. Nested grouped settings search now executing; no promotion yet. Independent generalization still unmeasured, sealed untilfreeze. Current docs/audit evidence in experiments/extension-2026-11-07.


## Extension checkpoint — J029
Track1 additional labelled data/transfer unavailable; Track2 threefails→stop (joint calibration notrun); Track3 nested4-setting policy fails (1/5, corrupted median-.000035). Track4 deferred because prerequisite1 incomplete. Production original9core unaugmented16 remains; CPUthread1 verified and fresh-clone raw external rebuild/cleanenvCSV identical. New freezeNovember13,delivery14–16. No sealed evaluation/finalpublicscore yet; no independent transfer evidence.


## J030 official PFF received
Missing-file blocker changed: user delivered64PFFmatches with matchingmetadata/rosters and specs; hashes and prospective48/16provider split committed before modelling. Native29.97Hz, embeddedstate/team events; coverageaudit and25Hzadapter validation pending. No model results yet; transfer evidence remains unmeasured. Existing production16unchanged; sealed untouched.


## J031 PFF native audit complete, adapter pending
64streams,11707598standard-time deliveredrecords,H/A/D present all64under provisional rule. All64non-increasingIDs; firstprobe849duplicates incl401conflictingpayloads, no backwardframe/time steps. Need explicitduplicate/CLK/time/resampling contract before training.48/16prospective split/hash locked; no PFFperformance results or production change.


## J032 recommendation
Prioritize strict PFFadapter contracts→train-more gate→cross-provider diagnostics. Threecontributor/date plan docs/next-steps-2026-11-07.md. More-data benefit unproven; transfer must not select versions. No production change or experiment this planning turn.


## J033 adapter and independent reviews
PFFduplicates are explicitly documented annotation expansion; conflict probe mixed event and tracking changes, not purecoordinateconflict. New conservative adapter/pilot and28tests implemented; full64admission pending. Both requested reviews confirm recent rejection arithmetic; missing-ball model behavior is nearconstantD, counterfactual repair gains are not upperbounds, and rejectedduration model mishandled censoring. No production change or reopening stopped research track. Review docs preserve evidence and priorities.


## J035 PFF admitted with raw-observation contract
Independent review excluded annotation-conditioned ballsSmoothed before modelling. RawVISIBLEonly,CLK/VIDunknown, nativegap/cumulativeclock guards, full64pass source/feature hashes verified,48train16holdoutlocked.2021996knownliveframes naturallymissingball.29tests pass. Models notyetmeasured; Track1A/B nowauthorized/preregistered. No provider-equivalence or targetquality claim.


## J037 PFF sequence complete
All64rawVISIBLEadmitted48/16 afterexcluding label-conditioned smoothing;29tests. Expandeddatareject0/5, corrupted medspell-.034930, macrodegrades; keep IDSSE5ninecore16. Missinglive recallimproves .0638%→8.9503% without passingglobalgate. Forwardtransfer spell .177631/.111395 clean/corrupt; reverse .390468/.271346. Descriptiveonly, providertransfer risk remains substantial, targetaccuracyunknown. No productionchange; originalCSVhashmatches. OptionalGRUeligiblebutnotstarted;freezeNov13unchanged.


## J038 — November8 sequence model rejected
FixedCPU BiGRU16blend25% failsoriginaland+.01gates:1/5pairedimprove,medianspell-.008148,corrupt-.007520;macro+.000052. Reload/retraining/batchCSVdeterminism passed allcases. Parenthalf-vslegacy metricsidentical. Keeporiginal9coreunaugmentedCatBoost16;no productionTorchrequirement ornewtargetCSV. Singlemodelbudgetclosed, no rescuevariants. Five-matchreuse/OOD/contextlimitations remain; no general claim against allsequence models. Report experiments/gru-2026-11-08/report.md.
