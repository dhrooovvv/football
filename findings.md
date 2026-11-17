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


November10trainingdiagnostic PASS: 2000steps fitfixedexternaltrainingsegment .9788accuracy/.07158CE/.805556decodedspellF1; NOT development/testquality. Supportsonepreregisteredlongertrainingcomparison, not modelpromotion. Latestuserallowsshortautonomoustests; hourslongrunsuserexecuted.


## November10 fixed2000stepLOMO result — rejected
SameTCN withbudget200->2000 raisesmeanheldoutspell from .117838/.082347 to .434855/.271903clean/corrupted; stillbelowCatBoost .517654/.323476.0/5pairedwins, primarymedian−.055559, medianmacro−.017240. Independentgateverified;39tests and10repeatfit/reload/batchCSVchecks pass. Notcleanenvironmentproof; trainingsegment .805556 isnotheldoutresult. Boundedextensionclosed; no furtherautomaticbudgetrescue. See experiments/tcn-budget2000-2026-11-10/report.md. Productionunchanged/sealeduntouched.


November10userauthorized20kstepTCNbudgetextensionprepared,notrun. SamefiveLOMOandcorruptionasCatBoost; gateunchanged. Sealedexcluded. Protocol experiments/tcn-long-2026-11-10/protocol.md.


## November10 longTCN — developmentqualitygatePASS
20kTCN meanheldoutspell .609882clean/.386651corrupted, versusCatBoost .517654/.323476.5/5pairedwins, medianprimary+.058637, medianmacro+.011711. Independentgateverified;39tests+10exactrepeatfit/reload/batchCSVchecks pass. Newbestdevelopmentcandidate ONLY; productionCatBoostunchanged pendingcleanenvironment/freshclone/integration/officialvalidation. Sealeduntouched/targetaccuracyunknown. Fullpermatchreport experiments/tcn-long-2026-11-10/report.md.


## November10 fixed50/50blend — provisionalqualitypass
Against20kTCN, meanblendspell .602554clean/.397037corrupted (TCN .609882/.386651). Cleandeclineexplicit;3/5pairedwins, primarymedian+.015717, medianmacro+.015701passunchangedgate.35tests+10exactparentreconstructions/10repeatedblendCSVchecks. No retraining/weightsearch. Leadingdevelopmentcandidateonly; releasecleanenv/integrationverificationpending, productionunchanged. Evidence experiments/tcn-cat-blend-2026-11-10/report.md.


November10approvedTCNtraining-ball-gaptrialpreparednotrun: experiments/tcn-gap-2026-11-10/protocol.md; commands docs/run-tcn-gap.md.41synthetic/productioncontracts pass. Same20kbudget/currentblendreference, independenttrainingmasks beforefeatures, no player/labelaugmentation. Quality/reproduction/integrationpending; no datasetexecution orproductionchange.


## November10 gapaugmentedblend qualityPASS
Mean .592502clean/.428386corrupted vs .602554/.397037parent. CleanALL5decline/corruptedALL5improve;3/5pairedwins, medianprimary+.020149, medianmacro+.017984.41tests/10exactrepeatfit-reload-batchCSVcasespass; independentgateverified. Newleadingdevelopmentcandidateonly; production/releaseverificationpending, sealeduntouched/targetunknown. Evidence experiments/tcn-gap-2026-11-10/report.md.


## November 10 — boundary audit and interaction hypothesis
Cached 40-case audit: leading gap blend short-spell recall .138 clean/.100 corrupted at IoU .5; observed team-control errors remain substantial. These are descriptive reused-development diagnostics, not causal headroom. Audit: experiments/tcn-boundary-audit-2026-11-10/report.md. Online/agent refresh supports one explicit player–ball relative-XY + validity-mask intervention (+72 weights); attention, relative velocity, larger context and loss changes excluded. 45 short contracts pass. New long experiment registered under experiments/tcn-interaction-2026-11-10/; no dataset training started, user command docs/run-tcn-interaction.md. Current gate/augmented-blend parent/production/sealed restrictions unchanged; release verification remains pending.


November10: 74-page consolidated market/model/research dossier and editable Markdown saved in output/pdf/. Includes24historicalresearchnotes, scoretradeoffs/platformlimitations and pendinginteractionstatus; no new experiment. Visual/textQAcomplete.


November10interactiontrial finished/rejected: .579542clean/.413382corrupted;2/5pairedwins, primarymedian−.009586.45tests/10repeatabilitycasespass; independentgateverified. Previousgapblendretained, no productionchange. See experiments/tcn-interaction-2026-11-10/report.md.


## November 10 — expanded training code prepared
User chose expanded training while preserving holdouts. New registered pool53matches, development52perfold, finalfit53. Memory-mapped lossless input storage, source/label/feature equality checks, checkpoint resumption, exact repeat fits and unchanged gate against current gap-trained blend. Code and four regression checks are provided but have not been executed. PFF may dominate the unchanged uniform-window sampler. All fixed model/budget/augmentation/blend settings are preserved. Commands docs/run-tcn-expanded.md, registration experiments/tcn-expanded-2026-11-10/. Two sealed IDSSE and16PFF holdouts remain excluded. Final artifact is a research variant even if generated after a failed gate. Production and release verification status are unchanged.


## November 11 — Neural export and clean inference reproduction prepared
User authorized integration preparation while expanded TCN trains. Added scripts/export_neural_candidate.py and docs/run-neural-export.md; registered protocol/source hashes under experiments/neural-export-2026-11-11/. Future final53checkpoint plus frozen CatBoost50/50 and penalty16; no CatBoost training. Private candidate output, exact checkpoint membership/budget/seed checks, local input/model hashes, unchanged official format validator and initial/reload/batch4 CSV equality. User commands cover current environment, fresh environment and fresh local clone. No tests, inference, dependency installation or export executed by assistant; no reproduction success claimed. Output is diagnostic even if expanded gate fails, never automatic promotion. Persistent target slot identity is not established by structural metadata checks; frozen inference checks also do not certify clean-environment training reproduction. Production unchanged, target accuracy unknown, protected matches untouched. Next: finish user training, audit development gate/final manifest, then user-run export checks; investigate adapter continuity before neural release.


## November 11 — Expanded-data TCN finished; rejected
User-run 52-match-per-fold expansion lowered blend mean spellF1 from .592502/.428386 to .520562/.376959 clean/corrupted; standalone .490922/.371692 descriptively. Independently recomputed unchanged gate:0/5pairedwins, medianpairedspell−.070287, medianmacro−.029278, primarymedian−.059098; reject. Recorded45contracts and10repeatabilitycasespass;32codehashesmatch. Final53fit exists, manifest/modelSHA verified, research-only. PFF supplied~92.8–92.9% of development sampled windows,91.19% of finalfit; provider imbalance and fixed-budget dilution are plausible, not isolated causes. No new tests/inference/training. Retain previous eligible gapblend and productionCatBoost16. Prepared exporter loads rejected expandedmodel, so a retained-candidate export requires separate registration. No targetexport/cleanenvironmentproof; targetaccuracyunknown/sealeduntouched. Full per-match evidence evaluation/report.md, audit experiments/tcn-expanded-2026-11-10/result-review.md. No automatic sampling/budget rescue.


## November 11 — Independent improvement review and fixed provider sampler registered
User authorized improvement research/preparation with all execution left to them. Independent scientist, literature researcher and static reviewer found no confirmed adapter/trainer/scorer bug explaining expansion regression. Primary literature supports considering source allocation and longer context, not a football score forecast or an optimal ratio. Prepared one fixed50/50provider scratch-training trial, uniform validstarts withinprovider, same52pool/20kbudget/originalTCN/gaps/blend/decoder and fivefolds. Selection gate remains against retainedbest (.592502/.428386), failed expansion descriptive only. New provider RNG seed20392419 is checkpointed; source/prepared manifests and evaluation references pinned. Eight synthetic sampler/resume/result-integrity contracts supplied but NOT executed. No tests/importchecks/training/inference run. Preserve two data-expansion failures; rejection stops thattrack atthree, no ratio/budget rescue. Final53 warmstart forbidden for development evaluation because it saw allfive labels. Future longer-context experiment needs separate parent-specific registration; adaptation deferred if expansiontrackstops. User commands docs/run-tcn-balanced.md; schedule docs/improvement-plan-2026-11-11.md. Release qualification/targetcontinuity/sealedfreeze checks still outstanding, productionunchanged/targetaccuracyunknown.


November11 datasetrefresh: documentationonly/no downloads. SkillCornerstrongestconditionallead, continuousdead/unknowncoverageunverified; SoccerTrackv2/SoccerNet/Alfheim auxiliaryratherthandirectH/A/Dsources. No newlyadmittedmatches, no model/splitchange. Sources literature/additional-datasets-2026-11-11.md; priorNovember7auditremainsrelevant.


November11balanced-providerresult: complete/rejected. Meanblendspell .512005clean/.370875corrupted vs retained .592502/.428386;0/5pairedwins, primarymedian−.065475, medianmacro−.023643. Actualproviderdraws79,546IDSSE/80,454PFFperfold confirmbalancing; it didnotrescueexpansion. Independentlyverifiedgate/53recordedtests/10repeatabilitycases/30CSVhashes/42codehashes/53preparedmanifests. No newtests/training/inference; no target/sealedaccess. Third data-expansionfailure stops track, no ratio/adaptationrescue. Keep retainedcandidate/production; separatecontextproposalnotyetregistered. Fullreport experiments/tcn-balanced-2026-11-11/result-review.md. Targetaccuracyunknown.


## November 11 — Fixed longer-context experiment prepared, user executes
User approves nextcontexttrial after sourceexpansion stopped. Parent retainedIDSSE-onlygapblend .592502/.428386. Originalobjectencoder/pooling retained; temporal5layers atdilations1/4/12/36/108,325encodedfield/radius162,halo163/input526,15843params versus9635(+6208). Capacity/depthchange disclosed; notpureRFcausality. Preserve original250known-anchor support/RNGdraws/central200labels and20kbudget/aug/seeds/blend/decoder/gate. Context clipsREALhalves, mayincludeunknowncontextlabels withoutusingthem inloss; no526knownwindowcensoring. Reuse fivecompactIDSSEcasesonly, noPFF/target/sealed or warmstart. Twofullrepeatfits/reload/batchCSVproof, checkpoints and completegate/evidenceguards. Tennewsyntheticcontracts supplied but no tests/import/compile/modelrun executed. Independentdesign/staticreviews andfixedprotocol/sourcehashes beforeuserexecution; commands docs/run-tcn-context.md. Runtime4–8hroughunmeasuredestimate, no customRAMcap/CPU1. Dataexpansionremainsstopped; no automaticvariant/finalfit/export. Productionunchanged/targetaccuracyunknown.


November11longer-contexttrialcomplete/rejected: blend .579905clean/.428623corrupted vs retained .592502/.428386. Primarymedian−.014256, pairedmedian−.006220,2/5wins; tinymeanrobustgain doesnotpassmedian/majoritygate. Standalone .570995/.432275 descriptiveonly, not posthocpromoted.55recordedtests/10repeatcases/30CSV/43code/fivepreparedmanifesthasheschecked; independentarithmeticagrees. Originalcandidate retained, contextfixedtrialclosed(onefailure), dataexpansionstillSTOP3. No newmodel/testexecution. Standalone/blendcomparisonrequiresseparateregistration; cachedfold-safecheckpointinferencecouldavoidretraining. Evidence experiments/tcn-context-2026-11-11/result-review.md. Targetunknown/releaseverificationpending.

November11 standalone gap-TCN trial prepared: one fixed removal of CatBoost from the retained short-context gap-trained blend, same checkpoints/ten evaluation cases/penalty16 and unchanged +.01 median corrupted gate. No training. Existing parent CSV reconstruction is mandatory to validate cached model/input alignment. No tests or model execution by assistant; user command docs/run-tcn-standalone.md. Long-context descriptive scores are not promoted posthoc. Production and retained candidate unchanged; target accuracy unknown.


November11 standalone gapTCN PASS: .597707clean/.463139targetlike mean spellF1 vs blend .592502/.428386;4/5pairedwins, primarymedian+.040271, pairedmedian+.034910, macromedian+.018038. J03WN1 declines; clean meanmacro−.002500.41recordedtests/10repeatcases/152inputhashes/30candidate+10parentCSVhashes verified; no new model/testexecution. New best eligible development candidate is standalone gap-trained short-contextTCN+16. Production unchanged, targetaccuracyunknown, release/finalfit/slotcontinuity pending. Evidence experiments/tcn-standalone-2026-11-11/result-review.md.

November11 next-step synthesis: officialDATA/OVERVIEW explicitly deny persistent targetslot identities; current external PersonId encoder computes adjacent-slot velocity and per-slot3frameconv before pooling. This is a transfer mechanism, not measured targetdamage. Prioritize external-only four-arm slotstress diagnostic (parent/staticwholevector/rederivedidentity/dynamicrederived) before symmetry or longertraining. No promotionfromstress; exactprotocol experiments/tcn-slot-audit-2026-11-11/protocol.md, command docs/run-tcn-slot-audit.md. Five newsyntheticcontracts supplied, all46checks/modelruns stilluser-owned/unexecuted. Scientist/literature/MLreviews and decision docs/next-step-decision-2026-11-11.md. Bestcandidate/production unchanged, targetunknown; slotsupport must be addressed in candidate-specific release. No stoppedtrackreopening or newdownloads.

November11 userapproved directframe-setTCN training, superseding slotdiagnostic prerequisite (stillunexecuted/deferred). One representation redesign: pointwiseXY+visibility3->8, instantaneousmaskedH/A/ballmeans thenoriginaltemporalTCN; storedobjectvelocity/prepooltimeconv removed,9539params/RF15 vs9635/RF17. Same20kbudget/seeds/gaps/fiveLOMO/core9/16decoder and gate againststandaloneparent .597707/.463139.8newcontracts+41existing integrated into user --run, none executed byassistant. Code/protocol experiments/tcn-set-2026-11-11; command docs/run-tcn-set.md. Two priorrepresentationfailures conservativelycounted; failureherestopsthird. No newdata/target/protectedusage, productionunchanged/targetunknown.


November11 status/researchrefresh: userframe-setTCNrunactive, firstfoldcheckpoint/49passingcontracts observed; nofinalqualityscore/gateyet. PrimarySoccerNet2026PAVE spatial-temporal+fourvariantensemble evidence reverified, but actionF1 not spellF1. TranSPORTmer maskedsetattention andMS-TCNrefinement remain architectureideas, notscoreforecasts. Finishregisteredtraining first; potentialnextfixedsymmetryaverage onlyafterwinnerknown/preregistration. No newrun orprotocolchange; currentbest/productionunchanged.


November11 frame-setTCN FAIL: .502256clean/.361285corrupted spellF1 vs parent .597707/.463139. All5decline inbothsettings,0/5wins, primarymedian−.108959, pairedmacro−.044517. Independentlyrecomputed gate;49recordedtests/10repeatcases/158registered+35compact+10checkpoint+30candidateCSVhashes verified. No newmodel/testexecution. Coupledremovalofmotion/history/changedcapacity failed, causalcomponentunknown. Thirdrepresentationfailure stopsline; retainoldgapTCN16. Targetidentityrisk remainsunresolved/accuracyunknown. Evidence experiments/tcn-set-2026-11-11/result-review.md; noautomaticretrain/rescue.

November11 fixedsymmetryensembleprepared: retainedoriginalgapTCN onidentity+180pitchrotation,50/50probabilityaverage, penalty16. No newtraining/architecture/CatBoost; classorder/roles/core invariant. Same5checkpoints/10cases/currentstandaloneparent/fullgate.46contracts supplied/user-run only; no model/testexecution. Protocol experiments/tcn-rotation-2026-11-11/protocol.md, command docs/run-tcn-rotation.md. Stoppedtracks retained, noalternatetransformsearch. Targetidentityrisk/accuracyunresolved, productionunchanged.


November11 rotationensemble PASS auditedduringresearch: .602155clean/.477682corrupted vs .597707/.463139;3/5pairedwins, medianprimary+.014850, pairedspell+.016578, pairedmacro+.005864.46recordedcontracts/10repeatcases/158locked+30candidate+10parentCSV+5modelhashes verified. Retainnewrotationcandidate onlypendingrelease, productionunchanged/targetunknown. No newmodel/testexecution. Evidence experiments/tcn-rotation-2026-11-11/result-review.md.

November11 high-upside researchrefresh (3agents): NEWprojectlead CVPRW2026arxiv2604.01859 boundary/segmenttrainingobjectives, primaryfulltextverified; rootprefersONEboundaryauxloss usingexternaltrainingH/A/Dtransitions andretainedmotionencoder, nottwo-loss/refinementbundle. Scientistprefersfixed2seedensembleforfeasibility (extraTOTALcompute). VideoRFDETR-Soccernet conditionalball-detectorlead butmodelprovenance/alignedevaluableexternalfootage unverified; no downloads. PathCRFv2transferdrop furtherwarnsagainstheadlines. No ceiling/.8forecast/newexperimentamendment/run. Synthesis literature/high-upside-methods-synthesis-2026-11-11.md. Actualfutureparent isnewrotation .602155/.477682, targetunknown.


## November 11 — Approved boundary objective, prepared for user execution
The completed rotation run remains the eligible development leader: mean spellF1 .602155 clean / .477682 target-like corrupted. Its16 audit artifact hashes and30 CSV hashes were rechecked unchanged; this is the same result, not an independent rerun. Production remains CatBoost16; target accuracy unknown.

One explicitly approved, bounded objective amendment adds a training-only32-to-1 boundary head to the original motion TCN: original crossentropy +0.1 balanced BCE on exact adjacent H/A/D transitions. Preserve motion/history, main initialization, original five LOMO splits,20k updates/batch8, independent training/evaluation gaps, rotation average and decoder16. No artificial X/half/crop transitions or target/held-out training labels. Eight synthetic tests supplied alongside existing46; all execution remains user-owned and none has been run by the assistant. Two full fits per fold, saved objective components, checkpoint RNG restoration and both-view reload/batch CSV checks precede the unchanged full promotion gate including+.01 median corrupted gain.

Protocol/source/input locks under experiments/tcn-boundary-2026-11-11; command docs/run-tcn-boundary.md. Partial independent core review plus root remaining source review documented in docs/tcn-boundary-design-review-2026-11-11.md (agents hit usage limits). This is not runtime verification. Research rationale literature/high-upside-methods-synthesis-2026-11-11.md; paper motivates a hypothesis, not a predicted football improvement. No new dependencies, data, weights, external publication or submission. Stopped tracks remain closed; failure rejects this fixed objective with no automatic rescue. Nov16 freeze and release qualification remain.


November11 plateau reassessment: three agent reviews distinguish clean plateau (~.60) from robust improvement (.323476 CatBoost→.477682 currentTCN). Current short recall remains125/732clean and92/732corrupted atIoU.5; rotation mainly reduced spurious spells. No ceiling established. New primary T-MAE2025 soccer masked-trajectory pretraining evidence motivates conditional eligible-PFF-geometry pretraining followed by IDSSE-only fine-tuning, without mixing provider possession labels. Different eventmAP task/stabletracks/halftime splits and unknown implementation licence mean no adopted model or forecast. Additional compute requires a locked budget amendment and matched-compute control. Root recommends pendingboundary plus at most one conditional learning route before qualification; scientist ranks seedensemble lower risk. No stoppedtrack reopened or experiment executed. Boundary userlog54contracts pass; no finalquality result at inspection. Reports docs/metric-plateau-review-2026-11-11.md, docs/error-strategy-reassessment-2026-11-11.md and literature/training-methods-reassessment-2026-11-11.md. Production unchanged, targetaccuracyunknown.


## November 11 — Boundary objective rejected
The user-run fixed training-only boundary objective lowers mean spellF1 to.583063clean/.464355corrupted versus rotationparent .602155/.477682; macro .913443/.832788 versus .919370/.838611. Independently audited gateFAIL: medianprimary−.017762, pairedmedian−.012318,1/5wins; macromedian−.004693 passes alone. Shortspell recall atIoU.5 declines125→122/732clean and92→81/732corrupted despite fewerdead/livewrongframes. Rejectthisfixedobjective; no automaticcoefficient/width/refinementrescue.

Userlogs54contracts and10repeatfit/reload/batchCSVcasespass. Verified185registeredhashes,35compactmembers,10checkpoints,30candidate+10parentCSVhashes; no tests/model/scorerexecution or array/checkpointloadingbyassistant. Fullpermatchmetricsanddiagnostics under experiments/tcn-boundary-2026-11-11/evaluation/; independentreview result-review.md/result-audit.json inthatdirectory'sparent. Foldstagessum82.83minutes, nottotalwalltime/RAM. Keepeligible rotationmodel; productionCatBoost16unchanged, targetaccuracyunknown/slotidentityriskunresolved/releasequalificationpending. No protected/targetlabeluse or externalpublication. Prospectivepretrain/fine-tune route requires separatefeasibility/budget/protocol; none startedhere.

November11 user-linked MDPI paper reviewed: conditional detection lead, not admitted model or comparable spellF1 result. Assessment literature/mdpi-possession-relevance-2026-11-11.md. No experiment; winner unchanged.

November11 supplied2019EPV paper read: possession valuation differs from full-matchH/A/D identification. Pressure/control surfaces and relativeformationlines are contextualideas; no spellF1benchmark/admittedcheckpoint or immediateexperiment. Avoid possession-labelconditioning when constructing attacker/defender features. Sourcehash/page-specific assessment literature/epv-paper-reading-2026-11-11.md. Winner/planunchanged.

November11TCN2023comparison: headlineframeaccuracy gains are not spellF1. Table3possession86.2−79.1=7.1pp differsfromabstract7.3; dead/alive89.2−56.0=33.2ppagrees. Current .602155/.477682spell and.919370/.838611macro cannotrankagainstpaperframeaccuracies/differentdata. Paperdefinedcurrentaccuraciesnotlogged. Evidence/retrievallimits literature/tcn-paper-metric-comparison-2026-11-11.md; no newrun.

November11 consolidated plan: docs/metric-improvement-plan-2026-11-11.md maps suppliedTCN/EPV/MDPI and T-MAE/structuredresearch to oneprospective maskedpretraining→IDSSEfinetuningroute with an extra-training control. Proposed40ktotalupdates perarm changesbudget andrequires exactprotocol/amendment;20fitpipelines withrepeats maximum,6–8hroughplanningestimate only. No code/runregistered/executed; no newresultbeyondboundaryrejection. Preserve allgate/stops/protectedrules andNov14–15qualification/Nov16freeze. Sourcepaperaccuracies/EPV/possessionpercentageerrors arenotspellF1forecasts.


November11 approved masked-geometry route prepared/preregistered: scripts/run_tcn_pretrain.py compares staged40k-supervised control to20k-observedmaskedballXY-reconstruction +20k-IDSSE fine-tuning. Both resetAdam and supervised RNG at20k; currentrotationparent/fullgate retained, then candidatefacesactualbest. Originalmotion/classnetwork/views/16decoder unchanged;66parameter training-onlyhead, no reconstructedcoordinates added to inputs. Geometrypool eachfoldPFF48+IDSSEother4, observation-onlyeligibleanchors and label-free loader; excludesheldout evenunlabelled/sealed/PFF16/target. Cachedgapfeatures were recomputed afterrawballmasking. Two exactfits perarm/fold,54contracts/bothviewreload/batchCSV supplied but NOTEXECUTEDbyassistant. Source review corrected fixture indexing and mappingretention.53manifests/371members bytehashes verified without loadingarrays. Protocol and source/input locks experiments/tcn-pretrain-2026-11-11; source review docs/tcn-pretrain-design-review-2026-11-11.md; command docs/run-tcn-pretrain.md. Maximum20pipelines/800kupdates,6–8hplanningestimate, updatesmatched notexactcompute. Noautomaticfollowup/productionpromotion/export or externalpush. Currentmetric usefuldevelopmentbaseline, nottargetaccuracy/competitionrank;17framecontext andidentity-transfer risks remain.

November11 comparablebenchmarksearch: officialtargetfullmatchsmooth50.2433spellF1 isexactmetricfloor, notwinningthresholdandnotdirectlyrankableagainstexternalmeans. Same5externalmatches smooth50.296145/.196645 versusretainedTCN.602155/.477682 isfairinternalcomparison. NewPossessionLab usesofficialscorer but.851stationary-live scoreissynthetic; realpublicclipsunlabelled, changedmotiongeneratorgivesdifferentranking. Reddit/XlimitedpublicsearchverifiednorealmatchcomparableSOTAscore; agentserviceusagelimits preventedcompletereports, rootfinishedsourceverification. Details literature/comparable-benchmark-search-2026-11-11.md; nonewmodel/scorerrun orprotocolchange. Targetunknown/registeredpretrainingunchanged.


## November12 — Staged supervised training improves; pretraining fails
Audited20cells: newbesteligibledevelopmentrecipe is40kIDSSEsupervisedTCN withAdam/samplerreset at20k, equalrotationaverage anddecoder16. Mean spellF1 .632870845clean/.497549978corrupted; macro .925899545/.848142823. FullgatePASS: primarymedian+.026049300, pairedmedian+.025578341,5/5wins, macromedian+.008763574. Highesthistoricalclean score also exceeded. Controlshortrecall150/732clean/104/732corrupt; corruptedspuriousspellsincrease645vs616despiteoverallgain.

Fixed20kgeometrypretrain+20kIDSSEfine-tune gives.533631828/.443298439spell, failsall5againstcontrol, primarymedian−.064596722. Reject/closeroutewithoutautomaticrescue. Extra-updatesandresetcoupled; notprooflongertrainingalonecausedgainorallpretrainingfails. Verified249registration+371member+20checkpoint+60candidateCSV+20parentreferencehashes;54recordedcontracts/20repeatabilitycasespass. RootauditsavedJSON/hashbytesonly,no newtests/model/scorerrunsorarrayloading. Recordedstages5h45m22notfullwalltime/RAM. Source experiments/tcn-pretrain-2026-11-11/result-review.md/result-audit.json andperarmreports. Productionunchanged/targetunknown/sealeduntouched. Finiteimprovementcomparisoncomplete; actualwinnerreleasequalificationpending. Goals.55robust/.60stretchareaspirationsnotgateorforecast.

November12nextdecision: actual40k/resetgain supportsretainingTCN, notautomatic80kcontinuation. Prioritizecurrentwinner slot-transferdiagnostic andfive-matchfinalfit/exportqualification. Fixedsecondseedensemble remainsconditionalfuturehypothesisrequiringexplicitbudgetextension; no newrun/protocol. Source docs/next-decision-2026-11-12.md.

## November 12 — Approved winner qualification implemented, execution pending

Prepared a new external-only slot diagnostic for the actual winning staged40k/reset TCN, with rotation averaging and penalty16. It verifies current checkpoint identity and ten archived parent CSV/metric reproductions before reporting four fixed conditions on five clean/corrupted development matches. Static permutation and identity-preserving velocity rederivation control the interpretation of dynamic slot churn. Forty aggregate cells, forty reload/batch repeatability cases and 240 prediction-view passes are planned, not executed. This diagnostic measures sensitivity; it cannot select a model or estimate target accuracy.

Also implemented a separate exact-five-IDSSE final-fit entrypoint and standalone exporter, preserving the original four-match LOMO guard and exact winning recipe. Final fitting requires review of the completed diagnostic, uses two full40k fits, and checks state/optimizer/RNG/loss/sampling equality. Export preserves equal rotation probabilities and decoder16, explicitly checks the unchanged official validator's success return, and requires identical reload/batch CSV bytes. No CatBoost blend or silent identity repair. Production remains unchanged.

Two implementation agents and an independent scientist reviewed the source. Diagnostic-signature binding, concurrent-manifest protection and post-inference checkpoint/diagnostic rehashing were hardened. Nine diagnostic and seven release synthetic contracts are supplied but unexecuted. ECC verification guidance is recorded with runtime checks marked not performed. Full29-package version pins and declared licence metadata were collected from installed metadata without importing packages; wheel-byte identity is not certified.

Protocols, locks and source are registered before the user's run. Commands: docs/run-tcn-winner-slot-audit.md, then after review docs/run-tcn-winner-release.md and docs/run-tcn-winner-reproduction.md. Frozen-model fresh-environment/clone inference differs from full training reproduction; neither has run for this release. No new metric result, protected-match access, target rows/labels in assistant context, downloads, push or submission. Best development spellF1 remains .632870845 clean / .497549978 corrupted; target accuracy unknown. Freeze remains November16.

## November 12 — Slot stress complete; actual input structure is the next qualification step

The user-run diagnostic reproduces the winning ten parent CSV/metric cases and passes63 logged contracts/forty reload-batch CSV cases. Fixed slot permutation and identity-preserving velocity recomputation change no decoded labels. Dynamic per-frame random identity churn collapses mean spellF1 .632871→.052858clean and .497550→.046667corrupted, allfive worse in both settings. Root byte/aggregate audit and independent scientist agree; no new model/scorer/test execution by assistant. Recorded fold time6m21, not total wall time or RAM.

This establishes strong sensitivity to the extreme synthetic joint disruption of velocity and object history. It does not estimate target accuracy or actual identity-switch frequency. Keep the development winner and production unchanged; no quality gate/stop counter change. Before final fitting, prepare a separately committed, user-run geometry-only target/external structure audit. Report continuity/clipping/coverage/runs/duplicates and nearest-set proxies as aggregates, never as verified identities or target-quality selection. No target labels, repairs, additional training budget, sealed access or uploads. Full evidence under experiments/tcn-winner-slot-audit-2026-11-12/result-review.md and result-review-scientist.md.

November12 actual-input structure diagnostic is now prepared/preregistered for user execution: scripts/audit_tcn_target_structure.py, protocol under experiments/tcn-target-structure-2026-11-12/, command docs/run-tcn-target-structure.md. Fixed source/provider scales and41fingerprints bind geometry-only inputs and completed stress evidence; six synthetic contracts supplied but unexecuted. Original strict parser reused, matched-support nearest-set comparison, aggregate-only private reports and explicit proxy limits. Independent source review found no blocking defect. No target geometry/model/labels were processed here; best model/production/gates unchanged. Review these actual-input summaries before final training.

## November 12 — Actual-input structure completed; proceed to registered final artifact

User-run geometry audit completed with six logged contracts passing and all41registered fingerprints intact. Twelve case/team aggregate cells and coverage/run/bin/fraction accounting agree; executionf9da058 follows protocol7636faa. Detailed target aggregates and two reviews stay private in data/competition/tcn-target-structure/. Public compact summary contains hashes/status only. No raw target rows, arrays, labels, models or scores were processed by the reviewers.

Typical adjacent-observed target movement is within the external mean range, with negligible same-slot versus nearest-set mean differences and no encoder-clipping events. This does not support treating extreme every-frame random churn as the typical target pattern. Residual shifts remain: far more fragmented visible runs/reappearances, variable visible-slot counts, and more >=.5m displacement steps despite low absolute rates. No identity certificate or target accuracy follows; masked reappearances and nearby swaps remain ambiguous. Independent scientist agrees that the already-approved exact-five final fit can proceed with these limitations recorded. No model/config/gate/stop changes or production switch. Existing190release fingerprints remain unchanged; new final training has not started and remains user-owned. Recorded aggregation27.607s excludes initial checks/registration/import overhead; RAM unmeasured.

November12 final-fit first attempt stopped before tests/training due omitted config fingerprint. Corrected registration adds unchanged configs/competition.json; protocol correction committed before user retry. No model or recipe change. All191listed fingerprints match; runtime remains user-owned. Failure preserved separately.

November12reportedretryerror: savedfailure predates correction; no fresh log. Need actual terminal output to diagnose. No further patch or run justified from stale evidence.

November12registrationdiagnostic: current checkout contains all21required sources; guard now names missing paths on failure. Updated source/protocol fingerprints committed before user retry; no training or tests executed.

November12secondregistrationfailure: organizer reference files incorrectly required Git tracking. Reclassified all10 into hash-only references, retained digests and verify them during fit/export. No scorer change/publication/model change. Both failure records preserved; user execution still required.

November12 final-five artifact fit completed: two40kreset fits,61loggedcontracts pass, exact repeated state/optimizer/RNG/loss/sampling equality and reload recorded. Root verifies190fingerprints/158committedsources/35members/two checkpoint hashes/lossdigest via metadata+bytes only. Recorded32m51 elapsed, no newqualityscore. Privateexport is next; targetaccuracy unknown, productionunchanged, sealedNov16. Audit experiments/tcn-winner-release-2026-11-12/final-fit-result-audit.json.

November12privateexport complete: recordedofficialvalidator/bothviewreloadpass,3CSVbytehashes andmodel/manifesthashes verified withoutreadingrows. Nextincrementalqualityproposal remainsfixedsecondseed40kensemble using5foldsafe fits, requires explicitclosedbudgetextension andnewpreregistration. Samecurrentmetrics; no newexperimentrun.

November12paper-to-error reassessment: docs/papers-to-spell-improvements-2026-11-12.md links userpapers torelationalattention,localpressure,visibleballrecovery andsegmentobjectives; separatesunverifiedadaptationsfrompublishedresults andourfailedboundary/pretraining trials. No newexperiment orbudgetapproval inferred.

November12userapproves two fixed parallel alternatives: within-team maskedattention vsfrozen40kparent, andinitializationseed20261107originalTCN+.5/.5parentensemble. Bothfoldsafe40kreset2exactrepeats,20fits800kupdates total. Predeclaredattention-firstorderedfinalgate, no combinedvariant. Source/protocol docs/run-tcn-parallel.md andexp/tcn-parallel-2026-11-12;14newcontracts unexecuted, independentreviewno blocker. Hardware18GiB11cores,1threadperjob2jobs sharedRAM/thermals; attentioncost unmeasured andcanfar exceedparent. Priorstopcounts/gates/freeze preservedwithboundedexplicitexception; no actualruns ornewqualityresult.


November13 cross-sport benchmark review: literature/cross-sport-segment-benchmarks-2026-11-13.md distinguishes figure-skating segment-overlap F1 (VIFSS/FACT), SoccerNet2026 player-event F1 (PAVE challenge winner) and football known-possession tactical-phase IoU (T-GAN). No exact real-match counterpart to our full-match possession spellF1 verified. Published scores are not numerical targets for our task. Relational/segment-aware modelling is a hypothesis; complete registered attention/ordered gate before any further proposal. No experiment or test run; production/best/gates/sealed/freeze unchanged.


November13 completed parallel review: both user arms pass68loggedcontracts/exactrepeat/reload proofs;378unique bytehashes verified. Attention mean spell .631785/.493400 clean/corrupt fails median corrupted gain(-.000205) and pairedmacro(-.010357). Ensemble .633872/.506191 is highest observed mean but fails+.01corruptedmedian(+.007731); no promotion. Attention-first order therefore retains original40kTCN .632871/.497550. Ensemble reduces spurious spells but not short-spell recall. Both authorized alternatives exhausted; no automatic follow-up. Evidence experiments/tcn-parallel-2026-11-12/result-review-2026-11-13.{json,md}; officialfinalizerunrun, independentmetadataarithmeticonly. Production/sealed/freeze unchanged, targetunknown.


November13 authorized policyv2: primarymedian corruptedgain>0 replaces+.01; allothergatesunchanged. Historicalfailedv1reportsremain. Completedensemble .633872clean/.506191corrupted nowprovisionaldevelopmentbest,productionunchanged. Exactlytwomissed-possessiontrialsimplemented:A shortspelluniform-mixturesampler;B CE+.1segmentsoftIoU retainingreviewedbest sampler.20fits/trial twoinitseeds,unchanged40k/reset/rotation/decoder16. B requirescommittedAdecision. Threeagents/staticreview;23newsyntheticcontracts suppliedUNEXECUTED. No runtime/model/scorer/tests launched. docs/run-tcn-missed.md; newsource/protocol/fingerprints underexperiments/tcn-missed-2026-11-13/. No downloads;2GiBnewartifactcap/12GiBfreefloor;freezeNov16. Targetaccuracyunknown.

November13 targeted dataset refresh: SkillCorner remains conditional broadcast/possession lead; continuous H/A/D coverage, provenance and selected-file size unverified. IDSSE already directly relevant; sealed exclusions stay. No downloads/new matches admitted; A audit pending. See ball.md J124.

November13 TrialA accepted:91usercontracts/exactrepeat/inferenceproofs,295pins/369uniquehasheschecked. Meanspell .645261clean/.513496corrupt,primarymedian+.011695,pairedspell+.005304,3/5wins,pairedmacro-.009168narrowpass. Shortrecallimproves100→124/732corrupt butspurious/deadliveincrease;corruptmacro .854010→.843502. reviewed-a.json bindsA asBparent/short_mix aftercommit. No runtimereviewerexecution;productionunchanged,targetunknown.

November13 B qualifiesv2 median+.001962/paired+.004976/3wins/macro+.002403, butcorruptedmean declinesA .513496→B .509836;clean .645261→.650385. Aremainshighercorruptedmean;Bprovisionalselectedbyagreedgate,preserveboth. Shortrecall124→133/732butcorruptmissed/spurious/deadliveworse.295pins/443uniquehashes/91loggedcontracts;nouserruntime rerunbyassistant. Two-trialroundcomplete;nextfinalartifactrecipe+deliveryqualification,nofurtherexperiments.

November13 approved finalBartifact preparation: exactfive permittedIDSSE,twoseedsx2repeatfits,unchangedshort_mix/segmentloss40krecipe. Newrunner scripts/fit_tcn_final_b.py and docs/run-tcn-final-b.md;13newcontracts UNEXECUTED,104expectedwithinherited. Separatelockedidentity/source/evidence/storage accounting;nofinalfit/inference/exportrun. Bmediangatechoice/Ahighercorruptmeanpreserved;productionunchanged,targetunknown.

November13 reportedfinalcompletionunverified: expectedfinalBmodel/manifest/evaluationoutputabsent. Needactualterminaloutput; do notinfertrainingcompleted orautomaticallyrerun.

November13 finalBensembleactualfitcomplete:2seedsx2exactfits/104loggedcontracts/reloadproofs,383pins/177committedsourceinputs/392bytehashesaudited. ManifestSHA c57c55fe77c2808efbf3e72cf51df801d869a399221202ec8136eb414cf14d2f;~36m41sperseedpair,nonewqualityscore. Neednewmanifest-awareexportcommand,officialvalidator/CSV/cleanenv/sealeddeliverychecks;productionunchanged,targetunknown. J128absentevidenceresolved.


November14 frozen diagnostic and final-B exporter prepared: new scripts/diagnose_tcn_possessions.py and scripts/export_tcn_final_b.py, independently statically reviewed. Diagnostic reproduces archived five-match A/B OOF scores/CSV bytes before explaining missed spells, full-gap exposure and pre-decoder evidence; zero training, no model selection, at most one conditional proposal. Export preserves finaltwo-member recipe, official validator and freshload/batch CSV equality with separate private outputs. All runtime USER RUN and UNEXECUTED; no new quality result. Combined storage guard and freeze preserved. Cleanenv/freshclone and once-onlysealed remain pending;targetunknown. See ball.md J130.


November14 diagnostic+localexportcompleteaudited:25loggedchecks,20archivedcellsreproduced,76pins/194hashesverified. Longgapwithoutargmaxmatch535/1278Bcorruptmisses,leadall5matches.289/359cleanmatchedspellslostaftercorruptionintersect>10sgaps. Decoderremoves265argmaxmatchesandrescues172,soitsrecallcostalonecannotjustifychangingpenalty. Recommendonelonger-contexttemporalproposalonly,requiresseparateprotocol/approval. LocalfinalBofficialvalidatorand3CSVbyteproofspass,SHA3dca80aa3b18a8c8e880b9f26cf1dc4f17a13018df18a2e4b39cf30f7da63463. Cleanenv/freshclone/sealedremainpending,targetunknown. ball.md J131 and exp/tcn-diagnostic-2026-11-13/result-review-2026-11-14.md.


November14 GNNclaimreview: currentTCNalreadysharedobjectencoder+maskedteamsetpool, so screenshotpermutationargumentdoesnotestablishreplacement. Pairwiserelationsremainplausibleimprovement. PrimaryBallRadar/PathCRF/GNN-LSTMphasepaperssupporthybridspatial+temporalmodelling,notuniversalGNNdominanceorcomparableourscorer. Longgapcontextremainsoneprospectivepriorityfromactualdiagnostic. ball.md J132.


November14 exportterminalconfirmsalreadyverifiedlocalCSVhash. Earlier13secondcontexttrialhadfailedandmustinformnextproposal. Proposedhybrid is frozenlocalTCN+smallcoarsetemporalresidualrefiner; exactprotocol/budget/approvalpending, no trainingstarted. GNN alone doesnotresolvetemporalsupport. docs/hybrid-next-proposal-2026-11-14.md and ball.md J133. Cleanenv/clonepending,targetunknown.


November14hybridresearchwithtwoagentsselectsfrozenB+coarsetemporalresidualrefinerbeforeGNNreplacement. Exposure-adjustedgapmisses621/910(68.24%)vsobserved540/1134(47.62%);all5consistent. MS-TCN++supportsrefinementmechanism,prior13secondTCNfailurepreserved. Rootinputchoice3probs+mask/gapage,agentinputdisagreementdocumented. PathCRFbundledweightsunresolvedSportecmatchoverlaprisk,noadmission. Decision docs/hybrid-research-decision-2026-11-14.md,source literature/hybrid-primary-evidence-2026-11-14.md,independentassessment docs/hybrid-independent-assessment-2026-11-14.md. Implementationanduserpreflightpending,noruns/newmetrics.


November14 approvedtwohybridplanimplemented: temporal6483andgraph9835correctionmodels, fixedparents/20fitsperstage; userpreflight37suppliedtestsUNEXECUTED,50boundparentarrays,64probeupdates/fold,RSS/time/storageprojection. StagegraphrequirescommittedTreview. Finalfit/export/cleanclone/sealedusercommandsprovided.102source/evidencepinsverified,nonewmodelqualityresult;allruntimeuserowned. Independentintegrationreviewinterruptedatagentlimit,rootfinishedstaticintegrationreview. ball.md J135, docs/run-tcn-hybrid.md and docs/run-tcn-hybrid-release.md.


November14 temporalpreflightpassed37loggedchecks,50cachearrays/metadata and10zero-parentCSVproofs,210hashesverified. Measuredworst.02746s/update,nominal20fits2workers~3.05hbeforeeval;conservative6.77hincludesfinalfits/allowance. Singleprocesspeak3.04GiB,twojobestimate6.08GiB;artifactprojection.558GiB/free16.50GiB. Fulltemporalruneligiblebeforefreeze;noqualityscoreyet. See ball.md J136 and exp/tcn-hybrid-2026-11-14/preflight-temporal-audit.json.


November14temporalhybridreject:cleanmean.654253/corrupt.510676vsB.650385/.509836;medianprimary−.000728failsdespitemacrocorrupt.858140and3pairedwins. Missedcorrupt1278→1157andlonggap621→564improve,butspurious658→997increase.37loggedcontracts/20fitproofs/169hashesaudited. CommittedreviewacceptedfalsebindsgraphparentB. Nextgraphpreflightonly,nonewtemporalrescue. ball.md J137.


November14userwilldownloadadditionaldata. SkillCorner1886347officialmetadataverified;recommendfourtracking/metadata/event/phasefilesforonematchauditfirst.10Hz,possessionfields,visibilityprovenanceuseful,butexhaustiveHADcoverageunverified. No datasetdownloadortrainingadmission. ball.md J138.


November14userre-authorizesassistantdownload: SkillCorner1886347fourmatchfiles+README/licencedownloadedandbyte/Gitverified,pinned4340d274572876239c154c90bc507a9b3250a656,total~90MiB. Folderdata/external-candidates/skillcorner/1886347,receiptliterature/skillcorner-1886347-download-2026-11-14.json. Zero trainingadmissionpendingcoverageaudit. ball.md J139.


November14graphpreflightcompletecorrectness37checks/50caches/10parentproofs,211hashesverified. Timeadmissionfails:nominaldevelopment16.79h,conservativetotal36.35hvs27.22hremainingbeforefreeze. Memory/storagepass. No graphqualityscore,fullcomparisonnotrun. PreserveBdeliveryandprotocol. ball.md J140.


November14Macinspection11cores/18GiB;currenttwo-seedworker scheduling leavesfoldparallelismunused. Bestnextspeedstepisbounded2vs4fold/seedjobbenchmark,includingfinalfitparallelisation,withsameone-threadnumericsandexactrepro. Nofourworkercommandimplementedorbenchmarkrunyet;ideal8.4hdevfitestimateisnotmeasured. ball.md J141.


November14approvedschedulingextensionimplemented: fourfold/seedjobsandfourparallelfinalfits, unchangedmodel/budget/gate. New2vs4benchmarkrequiresexactstatesandserialreference+16384frameCSVidentitybeforeselectingthroughput. FournewtestsUNRUN,speedunmeasured. Source/evidence12pinsregistered,firstusercommand scripts/run_tcn_hybrid_parallel.py --benchmark. ball.md J142.


November14fourjobbenchmarkpassed4checks/exactstateandserialreference/CSVidentity. Runtime97.67→61.46s(1.59xspeedup),sampledsumRSS3.30GiB. Revised20.41hconservativebudgetfitsremainingtime;parallelgraphfullruneligible. No qualityscore. ball.md J143.


November15graphcomparisonrejected:mean.647364clean/.508415corruptvsB.650385/.509836;primarymedian+.002031passesbutpairedmedian−.003345/only1of5winsfail. Missedcorrupt1278→1276/spurious658→699.114pins/180hashesaudited,20fitsrecordexactrepeats/CSVproofs. Bothhybridsclosed,retainalreadyfittedB,noadditionalbranchtraining. Nextdeliveryreproductionandsealedfreeze. ball.md J144.

November15 original SUBMISSION.md checked: three deliverables are full-match CSV, public reproducible repository URL, short technical PDF/Markdown; team-based filenames; Nov17 deadline. Private ignored submission-package-2026-11-15 contains selected-B exact CSV, short current report and locked source/model/evidence copies. CSV SHA256 3dca80aa3b18a8c8e880b9f26cf1dc4f17a13018df18a2e4b39cf30f7da63463. Team name unconfirmed. Draft only: public release/weights visibility, standalone post-Nov17 exporter portability, clean-env/clone reproduction, sealed evaluation and exact renamed-copy validator remain pending. No raw match assets copied or project numerical execution; no publication/submission. See ball.md J145.

November15 user-approved temporal-recovery diagnostic prepared/preregistered: five OOF matches, clean/corrupted archive reproduction, recovered-versus-introduced-spurious parent/temporal margin and two-seed agreement; per-match AUC/denominators, no threshold search or candidate promotion. Eight tests UNEXECUTED; command docs/run-temporal-recovery-audit.md. Reads saved graph losses only to assess training trends, not held-out benefit; no longer graph training registered.204source/163evidence fingerprints; registration ddf1b7a987107693b3780cd3c3e18cf72a8563e167f1a38128887503cd0c15c9. User runs all numerical work. Next review then at most one fixed correction rule if supported; B/CSV/gate/freeze unchanged. ball.md J146.

November15 recovery audit initial user run:3/8checks pass,5errors from numeric0..3 fixtures reaching official string-label parser. No inference/scoring began. Failure preserved/committed0874a1d. Diagnostic adapter now validates numeric codes or uses unchanged official H/A/D/X parsing; two extra contracts make10, not run by assistant. Retry logs unique/current-registration-bound; originalchecks.txt retained. Corrected identity91a4395fe91ef2b55a0022af1c7b4d3c6e444c6c1e531d550aec20ccce34f9ec,206source/165evidence pins; same user command. No scientific/model/gate change. ball.md J147–J148.

November15 recovery diagnostic completed:10userchecks pass;10archived CSV/scores reproduce;206source/165evidencepins and5units verified. Corrupted212recovered versus570introduced-spurious, with temporal confidence rank separation in5/5matches(AUC.667–.740,mean.698), not a spellF1 gain. Recommend one separately approved/preregistered fixed margin.5 postdecoder filter restoringB on unsupported temporalH/Aspells, preservingD; no rule executed. Graph training loss declines in20/20stage summaries but no held-out learning trend, so longer training benefit unproven. Bunchanged; ball.md J149 and recovery audit result-review.md.

November15userchooseslongergraphtrainingoverconfidencefilter. Registered direct scripts/run_graph_long.py --run: frozenB TCN+graph hybrid, graphonly40k→50k(+10k)withAdam/RNGstatecontinuation,20exact-repeatfits/fourone-threadjobs. PrimarygateagainstretainedB,old40kgraphreference. Sixnew+37originaltestsUSER-RUN/pending; no numericalexecutionbyassistant. Source210/evidence216pins, identity6445985c4e325bb38396c12ef8fcc863bd8e0548fcae54c26fdd37f6af007e49. Nominalextra-dev2.76h, conservativewithfinalreserve8.09h;freezeunchanged,60k/80kdonotfitconservativebudget. No final50kreleasepathyet; ifwinnerseparatequalificationrequired. B/CSVunchanged; ball.md J150.


November16 50/50 TCN-Graph probability ensemble evaluated: frozen Trial B TCN and Graph50k averaged with equal 0.5/0.5 weight. Exact clean mean spellF1 0.659432 (vs TCN 0.650385, vs G50k 0.648875); corrupted targetlike mean spellF1 0.522431 (vs TCN 0.509836, vs G50k 0.518200). Medians: clean 0.660465 (TCN 0.647843, G50k 0.651401), corrupted 0.517526 (TCN 0.516391, G50k 0.519042). MacroF1 clean mean 0.929070, corrupted mean 0.848072.
Against Trial B TCN: Gate v2 passes on all criteria (primary corrupted median delta +0.014097 > 0, paired spell median delta +0.008891 > 0, paired macro median delta +0.004555 >= -0.01, 5/5 matches improved, repeatability exact).
Against Graph50k: primary corrupted median delta is -0.001516 (4/5 paired wins, but fails primary corrupted median requirement > 0).
Deterministic repeatability verified: 10/10 CSVs byte-identical. No automatic promotion performed; Trial B remains production baseline pending user decision. See ball.md J151–J152 and experiments/tcn-graph-ensemble/evaluation/report.md.


November16 frozen 50/50 TCN-Graph ensemble promoted to production: user authorizes promotion over Trial B baseline based on 5/5 development match wins and gate v2 pass (+0.0141 corrupted median delta, clean mean 0.659432 vs 0.650385, corrupted mean 0.522431 vs 0.509836). Frozen configuration registered in experiments/tcn-graph-ensemble/manifest.json. Trial B candidate preserved for rollback at submission-package-2026-11-15/upload/TEAM_NAME_trial_b_rollback.csv (SHA256 3dca80aa3b18a8c8e880b9f26cf1dc4f17a13018df18a2e4b39cf30f7da63463). Sealed matches J03WQQ and J03WR9 raw assets not present on disk; sealed evaluation blocked. Target predictions generated across 199,319 tactical frames of BAR-ATH: independent repeated passes verified byte-identical CSV SHA256 5c59ed3004dc6be208ebeecbea46855acb1bacf511d1ec934079f53c121c2751. Official format validator passed. Deliverables assembled in submission-package-2026-11-15/upload/. See ball.md J153.
