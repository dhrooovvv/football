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


## J039 — November8 open-model research
TabICLv2 is a newly identified permissively licensed pretrained probability-model lead: public BSD-3-Clause code/weights, synthetic pretraining and local classification. No possession spellF1 or project CPU/determinism result; no trial or download. Generic benchmarks do not justify promotion. PathCRF weights have conditional overlap risk: canonical fold6 implies dev5 fitting and sealedWQQ validation; exact training hashes unknown. Known-live wrapper and complete-player requirements also block turnkey use. Original TranSPORTmer checkpoints remain unverified; BallRadar root licence/weights unresolved; CropDrop excludes dead play. No newly verified comparable soccer checkpoint in the limited Oct9–Nov8 scan. Production and closed budgets unchanged. Reports: literature/open-models-review-2026-11-08.md and open-model-primary-audit-2026-11-08.md. Next optional model work would need explicit track extension and a committed feasibility protocol before execution.


## J040 — TabICLv2 and fixed blend admission
User authorized new model experiments and two-model blend. Committed protocol plus independent sampling correction; exact parent113507rowLOMOcontext. Small1000/10000row probes deterministic after float64 probability normalization, but actual context exceeded preregistered6GiB observedRSS cap (6.377GiB,15.787s) and terminated before accuracy scoring. No standalone/blend metrics or promotion; resource rejection only, no claim TabICL lowers accuracy. Bounded track stopped, no rescue.29tests pass, production9coreCatBoost16/CSV unchanged; sealed and target labels untouched. See experiments/tabicl-2026-11-08/report.md.


## J042 — Higher-memory admission
User-approved10GiB CPUretry stopped at3GiBsystemavailablefloor after8.738s, processobservedpeak4.881GiB. Didnotreach10GiB orcompleteactualcontext; fit18GiB remainsunknown. No metrics/blend/productionchange. Awaituserclosingunneededapps andchangedheadroom beforecommittedretry. See experiments/tabicl-highmem-2026-11-08/report.md.


## J043 — Changed-headroom retry stopped
Userclosedapps;8.23555GiBbaselineavailable. Same10GiB/3GiBCPUprobe reached7.388GiBprocessRSS butstopped3GiBavailablefloorafter19.816s. Fullfit/actualdeterminism/accuracyremainunknown. Threefullcontextadmissionsnowstoppedforresourceguards; boundedtrackclosed,no unchangedretry, metricfailures0. No standalone/blend scored; productionunchanged. Report experiments/tabicl-highmem-retry-2026-11-08/report.md.


## J044 — Uncapped admission authorized
User explicitly overrode resourcecaps/resourcestop. Protocola0f5dd3 committed; identicalCPUadmission runningwithoutmemory/timekillthresholds. No resultsyet. Modelgate/privacy/CPU/splits/freezeunchanged.


## J044 result — M3Pro full-context completion/repeatability
Uncapped113507context/64querytwofitCPUtestPASS:exactprobabilities/CSV,41.586mintotal,9.016GiBobservedprocesspeak. Earlierresourcefailuresdidnotprovehardwareincompatibility. Noqualityscores/fullmatchevaluationyet. Preregisteredcachecorrectness915d198next, quality9656b93onlyaftercachepass. Productionunchanged, targetaccuracyunknown.


## J045 — Cache admission in progress
Synthetic1000/10000cacheFalse/Trueprobabilities/CSV andcachedreload/refitchecks passed;10000maxabsdelta0. Full113507context/16384querycachechecks running, noqualityscores. Cacheprecomputescostlytrainingcontext; measuredsyntheticrepeatqueryspeedisnotfullmatchperformance. Productionunchanged.


## J045 result / J046 next step
Cache correctness passed: synthetic numeric delta0; actual64CSV matches uncapped; cached reload/refit exact for64/16384queries. Full uncached numeric equivalence is not established. No quality result. User explicitly approved11-core development speed testing with single-thread winner checks; protocol/inputs locked before execution. Production unchanged.


## J046 failure / J047 approved endpoint
CPU11 fit was332.785s;64CSV matched CPU1, but max probability delta1.47821e-5 failed the registered1e-6 criterion. No quality/16k/repeatability test followed. User then approved a separate full16kCSV-based cross-mode test with exact within-mode repeatability and single-thread winner verification. Original failed result preserved; production unchanged.


## J048 — User stop
Active cross-core CSV test terminated at user request. Admission incomplete; no quality scores or model promotion. Production CatBoost16 unchanged. No background inference remains from this experiment.

J048 clarification: the process had already failed on disk space before stop inspection. Removed its incomplete generated cache only; no experiment restarted.


## J049 — Saved results reviewed, no restart
CPU11 initial64/16384CSV matches CPU1 exactly; numerical probabilities differ slightly. Observed fit/prediction speed about3x, but11-core reload/refit failed to complete due disk space. No F1/blend evaluation or proven accuracy gain. Current production unchanged; user stop active. See experiments/tabicl-threads-csv-2026-11-08/report.md.


## Reduced-context manual screen audited — 2026-11-08
User reported completing the manual run. Reviewed experiments/tabicl-small-2026-11-08/{report.md,results.json,gate.json,quality-gate.json,cost.json,provenance.json,production-tests.txt}; independently recomputed gate statistics from all30 aggregate score records. Run completed QUALITY_REJECTED, no active runner process. All26 locked inputs verified;31 contract tests passed. Five fold inference stages total489.955s (8.17min), excluding setup/scoring overhead. Full25Hz development timelines evaluated clean and target-like corrupted; context10,000 rows,11CPU threads, one estimator, fixed50/50 blend.

Mean spellF1 clean/corrupted: parent .517654/.323476; TabICL .497206/.291740; blend .510049/.325513. Mean macroF1 clean/corrupted: parent .895099/.679401; TabICL .885604/.635747; blend .892967/.680548. Standalone median paired spell delta−.024034,0/5 improved, median macro delta−.022967, primary corrupted median delta−.031262: rejected. Blend median paired spell delta−.004733,1/5 improved, median macro delta−.000573, primary corrupted median delta+.001995 (required+.01): rejected. Per-match scores and deltas are preserved in report.md/results.json/gate.json. Independent recomputation agrees with recorded gate.

Decision: stop this bounded two-arm screen; keep nine-core-feature, unaugmented CatBoost + penalty16 production. No new experiment launched, no promotion or repeatability/clean-environment claim for the rejected candidates. This rejects only the registered reduced-context/one-estimator configuration; it does not establish that every TabICL configuration is inferior. Existing development reuse limits generalization; target accuracy unknown, sealed matches untouched. No target/public-label selection. Next: maintain frozen parent and existing delivery plan; no automatic larger-context or seed search.


## Manual30k follow-up rejected — 2026-11-09
 Reviewed experiments/tabicl-medium-2026-11-08 aggregate results, gate, provenance, costs and test log; independently recomputed all per-match paired spell deltas and primary corrupted deltas and confirmed recorded gate within1e-12. Complete QUALITY_REJECTED; no runner active. Provenance records26 locked inputs,30,000 context rows,11cores;33 contract tests passed. Five fold processing stages total1373.004s (22.88min), excluding setup/scoring overhead.

Mean spellF1 clean/target-like corrupted: parent .517654/.323476; TabICL .493411/.291949; fixed50/50blend .508988/.327294. Mean macroF1 clean/corrupted: parent .895099/.679401; TabICL .879168/.637765; blend .892221/.680216. Standalone median paired spell delta−.031473,0/5 improved, median macro delta−.027112, primary median delta−.031552. Blend median paired spell delta−.004627,1/5 improved, median macro delta−.002116, primary median delta+.001606, below+.01. Both reject. Full per-match clean/corrupted scores preserved in report.md/results.json and deltas in gate.json.

Decision: close this bounded follow-up; no further context-size/seed/blend search, no new run started. Keep nine core features + unaugmented CatBoost + penalty16. Increasing context from10k to30k did not rescue the registered model; this does not disprove other TabICL configurations. These reused development matches cannot establish independent target quality. No candidate repeatability or clean-environment verification performed because numeric gate failed; no production changes. Sealed matches remain untouched, target accuracy unknown, no target/public-label selection. Next independent evaluation remainsNovember13 under the frozen interpretation rule; deliveryNovember14–16.


## Technology review — 2026-11-09
No comparable published official spellF1 supports a forecast to.8. Public primary papers favour temporal player-interaction representations as a hypothesis; current gap representation is limited. Recent engine coverage thin/irrelevant, not proof of no releases. Recommended current16error audit, followed by at most one authorized/preregistered intervention; no experiments or production changes. See literature/possession-improvement-market-review-2026-11-09.md and its three companion reviews. Decoder-X-reset concern is general, not a demonstrated current score driver. Existing stop rules and freeze remain.


## November9 control-context diagnostic / prepared trial
Frozen parent metrics reproduced from cached emissions; clean ownership errors dominate frame counts, corrupted live recovery collapses. One bounded temporal-control feature trial authorized/prepared;35contract tests, not quality. No new model fit or inference executed; user-run only. Evidence/protocol: experiments/control-context-2026-11-09/. Production unchanged, sealed untouched.


Temporal-control result November9: rejected; median corrupted gain+.000115 versus+.01required,3/5pairedwins,35tests. Independent gate verified. Production unchanged; see experiments/control-context-2026-11-09/report.md.


Schedule supersession November10: user moved architecture freeze/sealed evaluation toNovember16. Active plan docs/plan-2026-11-10.md; historical dates retained as history. Gates, stoplimits and production unchanged.


## November10 scratch trajectoryTCN prepared, not evaluated
One fixed richer-input localTCN candidate and user-run preparation/evaluation CLI registered under experiments/tcn-2026-11-10/.35productioncontracts+4isolatedsyntheticTCNtests pass, no external quality evidence. User executes dataset runs only. See docs/run-tcn.md for commands and declared shortcontext/cleantraining/budget limitations. Uses PyTorch/NumPy existing research dependencies; original scratch implementation inspired by temporal-trajectory literature, no borrowed weights or assumed model licence.46input/source hashes and dependencyversions locked; no production change. Full adapter contracts, fitrepeatability, runtime/memory and cleanenvverification pending userrun. Targetaccuracyunknown/sealedprotected.


## November10 trajectoryTCN result — rejected
Fixed200stepcandidate mean spellF1 .117838clean/.082347corrupted vs .517654/.323476parent;0/5improve, primarymedian−.233750. Independentgate verified.39tests and10within-environment repeatfit/reload/batchCSVchecks pass; not cleanenvironmentproof. Rejectboundedcandidate, no automaticbudgetrescue. Fullpermatch results experiments/tcn-2026-11-10/report.md; productionunchanged, targetaccuracyunknown/sealeduntouched.


## November10 competitor/practice research
MoreThanAHack2026IpurdIAr conversationalanalysisproduct is not comparableintervalbenchmark. SoccerNet2025/2026winners document pretraining, temporal/playercontext andensembles on differentmetrics. Currentrivals/privateapproaches/scoreunknown. Redditprovidedanecdotalbaseline/recruitmentsignals, Xretrievalunavailable; no validatedspellF1. See literature/competitor-practice-review-2026-11-10.md andcompanions. No modelrun, productionchange or publiclabelselection.


November10learningdiagnostic prepared, not executed/tested: scripts/check_tcn_learning.py, experiments/tcn-learning-check-2026-11-10/protocol.md. Fixedtrainingsegment scores are diagnostic only; no promotion/generalizationclaim. User reserves all tests/datasetexecution. Productionunchanged.
