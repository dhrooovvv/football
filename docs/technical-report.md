# Ball possession technical report — November 7, 2026

## Current candidate

Production remains **nine masked core features → unaugmented CatBoost H/A/D probabilities → Viterbi switching penalty16 → deterministic CSV**. Training uses only the five IDSSE development matches. Neither PFF expansion, extra features nor a sequence model is deployed.

The current199319-frame target CSV SHA-256 is `ab253e43f46fc9a7885b689498a220595e78d67ad2a6099a07316e081ca3f815` (see production manifest). Two independent training/inference runs, clean-environment reproduction and fresh-clone raw-input rebuild produced identical bytes and passed the official validator. CPU execution uses one thread. Target-match accuracy remains unknown; schema validity is not performance evidence.

## Sources, labels and licences

- **IDSSE / DFL:** Bassek, Rein, Weber and Memmert (2025), *An integrated dataset of spatiotemporal and event data in elite soccer*, Scientific Data12,195, [DOI](https://doi.org/10.1038/s41597-025-04505-y), [official repository](https://github.com/spoho-datascience/idsse-data). CC-BY4.0; credit Deutsche Fußball Liga and the publication. Observed TRACAB tactical tracking at25Hz, centered metric coordinates, explicit pitch/team metadata. Provider fields: BallStatus0dead/1alive; BallPossession1home/2away; unsupported ownership unknownX. Provider labels are not new human labels created by this project; their manual-versus-automated origin was not independently established.
- **PFF FC World Cup2022:** [official release](https://www.blog.fc.pff.com/blog/pff-fc-release-2022-world-cup-data). User supplied64tracking matches with metadata, rosters and specifications, native29.97Hz. Tracking is Sportlogiq broadcast-derived; state/ownership labels are PFF embedded event annotations. No general redistribution licence is inferred from receiving the release. Raw files/specifications/model artifacts remain local; access terms should be retained separately. File hashes fingerprint the delivery, not a publisher signature.
- **Organizer starter:** unchanged DATA.md/EVALUATION.md/SUBMISSION.md/RULES.md and evaluation/possession_metrics.py define the scoring/submission contract. Kept locally in reference/more-than-a-hack-2027-main, not bundled with restricted assets.
- **Parser cross-check:** pinned [PySport/Kloppy PFF loader](https://kloppy.pysport.org/user-guide/loading-data/pff/) and DFL/Floodlight mapping were inspected as implementation references, not ground truth for provider equivalence. Provider code licences do not grant data redistribution rights.
- **Dependencies:** Python3.13, CatBoost1.2.10, NumPy2.5.4, Pandas3.1.1. Top-level pins requirements-pipeline.txt; full resolved pins experiments/whole-pitch/clean-environment-lock.txt. Actual clean-runtime licence declarations: experiments/extension-2026-11-07/production-dependency-licenses.json. CatBoost Apache2.0; NumPy/Pandas BSD-family; consult full inventory and wheel notices. PFF parsing uses standard library plus existing NumPy, no additional serving dependency.

## Training populations and fixed budget

Production development IDs: J03WMX,J03WN1,J03WOH,J03WOY,J03WPY. These contain713489native frames; final clean training samples every fifth frame after excludingX (142701samples). Five leave-one-match-out folds train on the other four. No target-game labels are training samples. J03WQQ/J03WR9 stay sealed and excluded from ALL training, including any future retraining variant.

CatBoost: MultiClass,300iterations,depth6,learning_rate.05,l2_leaf_reg3,random_seed20261106,CPUthread_count1, no early stopping, no class rebalancing or fitted calibration. NaNs remain missing values. Viterbi has no long hard minimum spell duration. Equal-score handling is deterministic.

PFF split was committed before modelling by SHA256 ordering:48additional-training,16transfer-holdout. All64passed strict admission with source/release/feature fingerprints; no score-based exclusions or replacements. The PFF dataset was evaluated as a candidate source and rejected from current production training. Split and manifests are under experiments/pff-intake and pff-evaluation/cohort-lock.json.

## Input, feature and possession rules

Target ATD frame IDs must be1..199319 and export indices0..199318;46slots, explicit named home/away metadata, fixed slot count, no infinities. Slots are tracklets, not persistent player identities. Normalized coordinates scale by105.3×68m. External centered metric positions use their own pitch dimensions. Attacking direction is not used by the core.

Nine columns: home nearest-ball distance, away nearest-ball distance, away-minus-home margin, consecutive-observation ball displacement speed, signed pitch-edge distance, ball-observed mask, home-distance-observed mask, away-distance-observed mask, ball-gap age. Speeds and gap age reset at halves. Missing ball does not directly assignD. Loose balls, challenges and restarts are learned from provider supervision; there is no hand-written target relabelling or Smart Tagging ownership override.

Viterbi sums log probabilities minus16on every class change. Halves decode independently. Target half-open blocks:[11185,90652),[110808,190198); outside framesX. Export is exactly frame,label, one row per video frame. The official validator checks format only.

## PFF admission safeguards

The tracking specification explicitly says frames are duplicated for multiple associated possession events. Duplication alone is expected. Group equal(period,frameNum); no arbitrary first/last/newest choice. File generated/smoothed timestamps are not treated as documented per-frame quality precedence. Per-observation finite consensus is kept; conflicting observations become missing. State/team contradictions become unknown. Coordinate, missingness, within-list repetition and label assertions are counted separately.

**Label-informed input excluded:** PFFdocuments say ballsSmoothed uses event/carrier locations and interpolation. It was used only in an engineering pilot, then excluded BEFORE modelling. Admitted features use raw homePlayers/awayPlayers/balls, VISIBLEonly; ESTIMATED/absent values missing; no smoothed fallback or event-based ball reconstruction.

OUT/END→dead; kickoff/OTB/G→alive; home_ball boolean determines team. CLKmeaning is unresolved, so CLK/VIDclear state/owner until fresh supported evidence. Unsupported native-time gaps also clear carry. Native videoTimeMs is checked against cumulative frame/fps time within each half. Convert standard halves1/2to25Hz with bounded nearest observed positions, no interpolation through gaps, past-only supported labels. Extra-time periods are excluded from these comparisons.

All64admission yielded2021996known live H/A frames with naturally missing raw ball. Missing observations and known teacher labels are deliberately separate.1348resampled frames have unknown labels, excluded; the exclusions need not be random. Admission proves tested contracts, not possession-rule equivalence. Full tables/provenance: experiments/pff-admission/report.md and snapshot.json.29tests pass, including actual-loader exclusion of smoothed/estimated observations.

## Evaluation and decisions

Official spellF1 and macroF1 are reported per match. Target-like synthetic corruption bootstraps empirical target observed/missing runs using only tracking, with fixed per-match seeds and original independent player masks. Raw ball masking precedes feature computation. It is not a conditional occlusion model; PFFclean already contains natural missingness, so adding masks does not rate-match its total missingness to target. Natural/newlymasked/allmissing/observed subsets report confusion, Dprecision/recall, live recall and predictedDshare.

Current gate: per-match mean(clean,corrupted) spellF1 positive median gain and majority improvement, median macro delta>=-.01, tests pass, PLUS median corrupted spellF1 gain>=+.01. Repeated historical use of IDSSE5limits generalization claims; nestedCV does not erase that reuse. Track failure counters are local, not counts of inner fits or reproducibility runs.

| Candidate | Decision / evidence |
|---|---|
| Uniform switch8 then16 | Promoted on their applicable paired gates; final16retained |
| Instantaneous mean player speed | Rejected; core-development/mean-speed |
| Short-turnover/asymmetric decoder variants | Rejected; core-development/short-turnover and extension decoder |
| Gap augmentation8 | Passed vs8, subsequently dropped after augmentation16failed current-parent gate |
| Rolling whole-pitch bundle | Rejected original and+.01gates; whole-pitch |
| Gap-age switching / separate live-D switching / learned duration prior | Threefailures stopped decoder track; joint calibration not run |
| Nested4-setting CatBoost policy | Rejected; extension settings |
| Add48raw PFFtraining matches | Rejected0/5; paired medspell−.056268,medmacro−.099643,corrupted medspell−.034930 |
| Fixed25% bidirectional GRU blend | Executed November8 and rejected both spell gates; gru-2026-11-08/report.md |

The rejected duration implementation mishandled boundary censoring, so its failure is not evidence against all duration priors. Previous deterministic error-repair gains are counterfactuals, NOT upper bounds or additive causal loss attribution. These corrections do not reopen stopped tracks.

### Completed data experiment

Fresh controlled parents train4IDSSE versus the same4+48PFF, same settings and fixed masks. Controlled A preserves the legacy label-supported decoder reset convention; transfer B uses half-only inference. All completed A/B scored records have known-label fraction1.0, so this policy distinction is a general caveat, not a demonstrated cause here.

| Evaluation | Clean spellF1 / macroF1 | Corrupted spellF1 / macroF1 |
|---|---:|---:|
| Parent IDSSELOMO | .517654 / .895099 | .323476 / .679401 |
| Expanded-data IDSSELOMO | .423010 / .771147 | .289040 / .623183 |
| IDSSE5→PFF16transfer | .177631 / .698513 | .111395 / .546575 |
| PFF48→IDSSE5transfer | .390468 / .732170 | .271346 / .602691 |

Expanded training improves pooled missing-ball live recall .0638%→8.9503%, but whole-match gate fails. No submetric-only promotion. Transfer results are descriptive, never used for model/cleanup/calibration selection; provider noise, conventions, visible subsets and data volume vary jointly. They do not identify a single causal source of the gap. No rescue weights or grid changes were tried.11fits took663.163recorded training seconds, excluding preparation/inference. Per-match scores, SDs, confusion and costs: experiments/pff-evaluation/report.md. Independent scientist/analyst reviews found no decision-changing arithmetic issue.

## Regeneration and artifacts

Arrange the provided private tactical files under data/competition/tactical, install the full dependency lock in a Python3.13venv, download only IDSSEdevelopment via scripts/fetch_external.py, then prepare raw training inputs with scripts/prepare_training_inputs.py. PFF is not needed for production regeneration.

**One regeneration command once inputs are prepared:**

```
PYTHONPATH=src python scripts/predict_core.py
```

This freshly trains the five-match model, infers locally, saves/reloads the model and requires identical repeated CSV bytes. For official format validation use the unchanged organizer evaluation/validate_submission.py on data/competition/predictions/candidate.csv. No public-label evaluation is required to regenerate or validate.

Evidence/hashes: experiments/whole-pitch/finalization.json and reproduction.json; extension-2026-11-07/one-thread-result.json, fresh-clone.json and production-hashes.json; current PFFstudies have separate fingerprints. Independent fits may have different model-info serialization metadata despite identical predictive output; CSVbyte equality is verified. PFFstudy reproduction additionally requires its locked rawrelease and private label-free empirical-gap file; do not rerun a public-score script merely to reconstruct corruption inputs.

## Limitations and delivery

Target-match accuracy remains unknown. Missing-ball live recovery, short spells, provider conventions and transfer are unresolved weaknesses. Data expansion failed here; this does not prove all PFFusage or all additional data harmful. No target hand labels, public-label tuning, restricted-row publication or sealed access occurred in this sequence. No model promotion, targetCSV replacement or new target score was needed; the existing verified production artifact is unchanged.

Architecture freezeNovember13; November14–16delivery only. At freeze, evaluate candidate+supplied baselines once on sealed2, with interpretation committed first: large decline or below preregistered smoothing baseline triggers bug/transfer investigation, NOT tuning. Final frozen public score once for correctness only. Any all-compatible-labelled retrain variant must exclude sealed2, remain separate and await the user's decision before switching.

Three deliverables: team-named possessionCSV, public reproducible source, short PDF/Markdown technical document. Final review, team naming/packaging and freeze checks remain pending. No external submission has been made or authorized automatically. Paused automation remains paused.


## November8 optional sequence result — current status
The previously pending sequence model was executed as one preregistered fixedcandidate and rejected. Fold-onlycleanIDSSE4scaling/windows, nineinputs, one-layerbidirectionalGRU(hidden16perdirection),200Adamupdates/batch8/window250/losscentral200, fixed75%CatBoost+25%GRU, Viterbi16. CPUtorch2.15thread1, deterministicalgorithms, no pretrainedweights/augmentation/PFFdata. No model/window/blendsearch.

Gatefails1/5pairedimprovements; medianpairedspell−.008148,macro+.000052,corruptedspell−.007520. Meanblendclean spell/macro .504499/.895223 andcorrupt .317274/.680278 versusparent .517654/.895099 and .323476/.679401. Bothparent/candidatehalf-only inference; parent exactlymatcheslegacy metrics inallcases. Repeatedtraining states/scaler/lossesmatch, save/reloadprobabilitiesmatch, decodedCSVbytesmatch batch1/4 on10externalcases. TwoGRUcontracttests and29productiontests pass. No crosshardware/versionguarantee, targetneuralCSV orcleanenvironmentneuralreproduction claimed. Production unchanged andexistingbyteproofs remain applicable.

The10scontext is shorter than median10.72sgaps, andclean-only training leaves missingmask/gap featuresOOD. Failureconcerns thisfixedsmallbudgetcandidate, notallsequence methods. ResearchTorchdependency/licences remainisolated; no productionintegration. No rescuetrials. Fullper-match/missingball/variance/source/determinism evidence experiments/gru-2026-11-08/report.md; independentreviewdocs/gru-design-review-2026-11-08.md and gru-results-review-2026-11-08.md. Target-match accuracy remainsunknown; currentCSV unchanged. Allauthorizedboundedtracks exercised; freezeNov13/delivery14–16unchanged.


## November8 open-model audit
Production remains unchanged after a read-only public-source review; no additional model dependencies, weights, inference or performance experiment were added. TabICLv2 has public BSD-3-Clause code/weights and could supply probabilities over the existing feature interface, but CPU scaling, deterministic output and project spellF1 remain untested. General tabular benchmark claims are not possession-quality evidence. PathCRF's published canonical fold appears to reuse our development matches and one sealed match for validation; contemporaneous training hashes are not verified. Its supplied wrapper assumes known live segments and complete selected player inputs, so neither its checkpoint nor event-F1 result provides a clean comparison here. Original TranSPORTmer runnable weights, BallRadar root licensing/weights and CropDrop open runnable weights remain unresolved. No experimental budget was reopened. Full source/licence/metric distinctions and immutable revisions: literature/open-model-primary-audit-2026-11-08.md; decision and coverage limits: literature/open-models-review-2026-11-08.md. Target-match accuracy remains unknown.


## November8 TabICLv2 feasibility extension
After user authorization, a committed local CPU admission protocol preceded conditional standalone and fixed50/50CatBoost blend comparisons. Independent review corrected context to exact parent stride5 rows. Synthetic probes were deterministic after a logged float64 row-normalization adapter correction. The actual113507rowcontext exceeded6GiB preregistered observedRSS cap and terminated before prediction completion; no possession score or blend was run. This is resource admission failure, not evidence of lower accuracy. Public BSD3weights remain ignored/private locally; checkpoint/dependency provenance and all failures in experiments/tabicl-2026-11-08/report.md. No production dependency/config change;29tests pass and canonicalCSVhash unchanged. Targetaccuracyunknown, no sealed/public-label access. Track stopped without rescue variants.


## Higher-memory CPU admission clarification, November8
User approved10GiB process budget; unchanged full-context TabICL run was stopped after8.738s by the3GiB systemavailable guard, processpeak4.881GiB. This does not demonstrate10GiBbudget failure or fullworkload compatibility/incompatibility with18GiB. Actual inference unfinished, no quality scores orblend. Await changedmemoryheadroom before anynewcommittedretry; production and existingreproductionevidence unchanged. See experiments/tabicl-highmem-2026-11-08/report.md.


## Changed-headroom retry, November8
After userclosedapps, baselineavailable8.23555GiB. Preregistered identicalCPUretry reached7.388GiBprocessRSS, then3GiBsystemavailableguard stopped it after19.816s;10GiBprocesscapnotreached. No actualcontextcompletion/qualityscore/blendevaluation. Threeconsecutivefullcontextresourceadmissionsstopped, boundedtrackclosed. This doesnotprovefullworkloadcannotfit18GiB with a differentmemoryconfiguration; no suchvarianttested. Production/previousreproductionunchanged. Evidence experiments/tabicl-highmem-retry-2026-11-08/report.md.


## Uncapped admission completed, November8
Explicituserresourceoverride, unchanged full113507rowcontext/64queryCPUtwofitadmission passed exactprobability/CSV equality.41.586minwall,9.016GiBsampledprocesspeak; RSSnotallsystem/compressed/swapmemory. ConfirmscompletionforM3Pro18GiBtestedcase, notfullmatchcapacity,quality orcrosshardwareguarantees. No metriccomparison orproductionchange. Preregisteredcomputationalcachechecks915d198 next; conditionaltwoarm10casescoring9656b93afterpassonly. Dependencies/licences/sourcehashes pinned; no public/sealed/targetlabels accessed. Evidence experiments/tabicl-uncapped-2026-11-08/report.md.

## Research-only TabICLv2 source and dependencies

The candidate uses [TabICLv2](https://arxiv.org/abs/2602.11139), Qu, Holzmüller, Varoquaux and Le Morvan (2026), with [public classifier weights](https://huggingface.co/jingang/TabICL). The installed TabICL 2.2.0 wheel includes a BSD 3-Clause licence; the model card declares BSD-3-Clause for the weights. The exact checkpoint revision and SHA256 are recorded in the experiment's weight-source.json.

These dependencies remain isolated from the production regeneration environment. The local declaration inventory is `experiments/tabicl-cache-2026-11-08/dependency-licenses.json`. It records actual versions and compact licence expressions, including bundled-component expressions for Torch and NumPy. Missing compact metadata is not an absence of a licence: the TabICL wheel has `licenses/LICENSE`, and SciPy has a bundled `LICENSE.txt` with a BSD-family notice. The wheel notices remain the source for full bundled terms. No cached training arrays or model pickles are published.

Current operational evidence supports uncapped full-context completion and exact repeatability on the tested M3 Pro. Cache correctness is still being checked. No TabICL quality result or production promotion is claimed here.


## Cache admission completed; threading test pending
The registered cache checks passed. Synthetic probabilities match exactly; full-context64CSV matches the uncapped reference; cached reload/refit probabilities and CSVs match exactly at64/16384queries. Full-context uncached probability equality and arbitrary chunk invariance were not tested. Actual procedure2540.665s includes multiple operations. Detailed costs and limited-scope memory observations: experiments/tabicl-cache-2026-11-08/report.md. No quality scores or promotion. User-approved11-core equivalence testing is separately preregistered; single-thread verification remains required for winners.


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


November10interactiontrial finished/rejected: .579542clean/.413382corrupted;2/5pairedwins, primarymedian−.009586.45tests/10repeatabilitycasespass; independentgateverified. Previousgapblendretained, no productionchange. See experiments/tcn-interaction-2026-11-10/report.md.


## November 10 — expanded training code prepared
User chose expanded training while preserving holdouts. New registered pool53matches, development52perfold, finalfit53. Memory-mapped lossless input storage, source/label/feature equality checks, checkpoint resumption, exact repeat fits and unchanged gate against current gap-trained blend. Code and four regression checks are provided but have not been executed. PFF may dominate the unchanged uniform-window sampler. All fixed model/budget/augmentation/blend settings are preserved. Commands docs/run-tcn-expanded.md, registration experiments/tcn-expanded-2026-11-10/. Two sealed IDSSE and16PFF holdouts remain excluded. Final artifact is a research variant even if generated after a failed gate. Production and release verification status are unchanged.


## November 11 — Neural export and clean inference reproduction prepared
User authorized integration preparation while expanded TCN trains. Added scripts/export_neural_candidate.py and docs/run-neural-export.md; registered protocol/source hashes under experiments/neural-export-2026-11-11/. Future final53checkpoint plus frozen CatBoost50/50 and penalty16; no CatBoost training. Private candidate output, exact checkpoint membership/budget/seed checks, local input/model hashes, unchanged official format validator and initial/reload/batch4 CSV equality. User commands cover current environment, fresh environment and fresh local clone. No tests, inference, dependency installation or export executed by assistant; no reproduction success claimed. Output is diagnostic even if expanded gate fails, never automatic promotion. Persistent target slot identity is not established by structural metadata checks; frozen inference checks also do not certify clean-environment training reproduction. Production unchanged, target accuracy unknown, protected matches untouched. Next: finish user training, audit development gate/final manifest, then user-run export checks; investigate adapter continuity before neural release.


## November 11 — Expanded-data TCN finished; rejected
User-run 52-match-per-fold expansion lowered blend mean spellF1 from .592502/.428386 to .520562/.376959 clean/corrupted; standalone .490922/.371692 descriptively. Independently recomputed unchanged gate:0/5pairedwins, medianpairedspell−.070287, medianmacro−.029278, primarymedian−.059098; reject. Recorded45contracts and10repeatabilitycasespass;32codehashesmatch. Final53fit exists, manifest/modelSHA verified, research-only. PFF supplied~92.8–92.9% of development sampled windows,91.19% of finalfit; provider imbalance and fixed-budget dilution are plausible, not isolated causes. No new tests/inference/training. Retain previous eligible gapblend and productionCatBoost16. Prepared exporter loads rejected expandedmodel, so a retained-candidate export requires separate registration. No targetexport/cleanenvironmentproof; targetaccuracyunknown/sealeduntouched. Full per-match evidence evaluation/report.md, audit experiments/tcn-expanded-2026-11-10/result-review.md. No automatic sampling/budget rescue.


## November 11 — Independent improvement review and fixed provider sampler registered
User authorized improvement research/preparation with all execution left to them. Independent scientist, literature researcher and static reviewer found no confirmed adapter/trainer/scorer bug explaining expansion regression. Primary literature supports considering source allocation and longer context, not a football score forecast or an optimal ratio. Prepared one fixed50/50provider scratch-training trial, uniform validstarts withinprovider, same52pool/20kbudget/originalTCN/gaps/blend/decoder and fivefolds. Selection gate remains against retainedbest (.592502/.428386), failed expansion descriptive only. New provider RNG seed20392419 is checkpointed; source/prepared manifests and evaluation references pinned. Eight synthetic sampler/resume/result-integrity contracts supplied but NOT executed. No tests/importchecks/training/inference run. Preserve two data-expansion failures; rejection stops thattrack atthree, no ratio/budget rescue. Final53 warmstart forbidden for development evaluation because it saw allfive labels. Future longer-context experiment needs separate parent-specific registration; adaptation deferred if expansiontrackstops. User commands docs/run-tcn-balanced.md; schedule docs/improvement-plan-2026-11-11.md. Release qualification/targetcontinuity/sealedfreeze checks still outstanding, productionunchanged/targetaccuracyunknown.


November11balanced-providerresult: complete/rejected. Meanblendspell .512005clean/.370875corrupted vs retained .592502/.428386;0/5pairedwins, primarymedian−.065475, medianmacro−.023643. Actualproviderdraws79,546IDSSE/80,454PFFperfold confirmbalancing; it didnotrescueexpansion. Independentlyverifiedgate/53recordedtests/10repeatabilitycases/30CSVhashes/42codehashes/53preparedmanifests. No newtests/training/inference; no target/sealedaccess. Third data-expansionfailure stops track, no ratio/adaptationrescue. Keep retainedcandidate/production; separatecontextproposalnotyetregistered. Fullreport experiments/tcn-balanced-2026-11-11/result-review.md. Targetaccuracyunknown.


## November 11 — Fixed longer-context experiment prepared, user executes
User approves nextcontexttrial after sourceexpansion stopped. Parent retainedIDSSE-onlygapblend .592502/.428386. Originalobjectencoder/pooling retained; temporal5layers atdilations1/4/12/36/108,325encodedfield/radius162,halo163/input526,15843params versus9635(+6208). Capacity/depthchange disclosed; notpureRFcausality. Preserve original250known-anchor support/RNGdraws/central200labels and20kbudget/aug/seeds/blend/decoder/gate. Context clipsREALhalves, mayincludeunknowncontextlabels withoutusingthem inloss; no526knownwindowcensoring. Reuse fivecompactIDSSEcasesonly, noPFF/target/sealed or warmstart. Twofullrepeatfits/reload/batchCSVproof, checkpoints and completegate/evidenceguards. Tennewsyntheticcontracts supplied but no tests/import/compile/modelrun executed. Independentdesign/staticreviews andfixedprotocol/sourcehashes beforeuserexecution; commands docs/run-tcn-context.md. Runtime4–8hroughunmeasuredestimate, no customRAMcap/CPU1. Dataexpansionremainsstopped; no automaticvariant/finalfit/export. Productionunchanged/targetaccuracyunknown.


November11longer-contexttrialcomplete/rejected: blend .579905clean/.428623corrupted vs retained .592502/.428386. Primarymedian−.014256, pairedmedian−.006220,2/5wins; tinymeanrobustgain doesnotpassmedian/majoritygate. Standalone .570995/.432275 descriptiveonly, not posthocpromoted.55recordedtests/10repeatcases/30CSV/43code/fivepreparedmanifesthasheschecked; independentarithmeticagrees. Originalcandidate retained, contextfixedtrialclosed(onefailure), dataexpansionstillSTOP3. No newmodel/testexecution. Standalone/blendcomparisonrequiresseparateregistration; cachedfold-safecheckpointinferencecouldavoidretraining. Evidence experiments/tcn-context-2026-11-11/result-review.md. Targetunknown/releaseverificationpending.

## November 11: fixed standalone gap-TCN comparison pending

Registered removal of CatBoost from the retained short-context gap-trained blend, with identical fold checkpoints, inputs and penalty16. No retraining. The run must reconstruct historical parent CSV bytes, reproduce standalone CSVs after reload and batch changes, and pass the full gate including +0.01 median corrupted spellF1 improvement. Five development matches remain reused, so this is not independent generalization evidence. Checkpoints do not embed training membership; original run/protocol and repeat-fit records provide ancestry, supplemented by parent reconstruction. No tests or inference executed during preparation. Commands: docs/run-tcn-standalone.md. Production remains CatBoost16; target-match accuracy is unknown.


## November 11: standalone gap-trained TCN passes development gate

Removing CatBoost from the retained short-context gap-trained model raises mean spellF1 from .592502/.428386 to .597707/.463139 clean/corrupted. Mean macroF1 becomes .917089/.825776 (parent .919588/.768685). Median corrupted spell gain +.040271, median paired spell +.034910,4/5wins and paired median macro +.018038 pass the registered gate. J03WN1 regresses; clean mean macro slightly declines. Per-match evidence: experiments/tcn-standalone-2026-11-11/report.md and result-review.md. Recorded41contracts and10reload/batch cases pass;152registered hashes and40CSV hashes independently checked. No new scoring/modelrun by reviewer. Candidate becomes development leader pending finalfit and release qualification; production remains CatBoost16. Reused-five-match evidence does not establish target-match accuracy, which remains unknown. Target slot continuity and candidate-specific clean environment/fresh-clone/official validation remain unresolved. Rejected expanded53exporter cannot release this winner.

## November 11: documented temporal identity mismatch and registered diagnostic

Official input documentation DATA.md99–101/OVERVIEW.md90–93 says target slots swap identity. External PersonId training slots are stable; the encoder's adjacent-slot velocity and objectConv3beforepooling depend on that temporal identity. Fixed-order permutation invariance does not certify serving compatibility. The actual target metric impact is unknown. Prepared an external-only four-arm diagnostic isolating fixed-order numerical behavior, velocity-rederivation effects and severe per-frame identity churn; no target assets/labels or modelselection. Protocol experiments/tcn-slot-audit-2026-11-11/protocol.md; usercommand docs/run-tcn-slot-audit.md. Five transform contracts supplied; no tests/imports/compile/modelrun performed. No repair or new production promotion. Independent reviews and choices recorded in docs/next-step-decision-2026-11-11.md. Candidate-specific finalfit/export/reproduction and officialvalidation remain pending. Target-match accuracy is unknown.

## November 11: approved frame-set TCN training candidate, pending execution

To remove temporal player-slot identity dependence, registered a pointwiseXY/visibility encoder, per-frame masked H/A/ball means, then the original temporal TCN. Both stored objectvelocity input (including ball vectorvelocity) and pre-pooling temporal convolution are removed as one semantic redesign; unchanged core scalar ball speed remains. Capacity9539 vs9635, encoded support15vs17. It cannot resolve missing/duplicated observations or team errors. Existing521schema/20kbudget/independenttraininggapviews/seed/fiveLOMO/decoder16 remain fixed. Parent standalonegapTCN .597707clean/.463139corrupted. Fullgate unchanged. Protocol experiments/tcn-set-2026-11-11/protocol.md, usercommand docs/run-tcn-set.md. One integrated tests+training run;49contracts supplied, no tests/import/compile/model/scorer executed byassistant. Optional slotdiagnostic deferred byuserapproval. Checkpoint/repeat/inference/release proofs remain required; targetaccuracyunknown and productionunchanged.


## November 11: frame-set representation trial rejected

The identity-robust pointwise encoder lowered mean spellF1 to .502256clean/.361285corrupted versus .597707/.463139, with allfive matches declining in both settings. Primary median−.108959, pairedmedian−.108800, pairedmacro−.044517,0/5wins: fullgatefails. Recorded49contracts and10repeatabilitycases passed; independentgate and158registered/35compact/10checkpoint/30CSVhash checks agree. Result evidence experiments/tcn-set-2026-11-11/result-review.md; per-match evaluation/report.md. Coupled information/support/capacity changes prevent causal attribution. Representation line stops atthree perprotocol. Retained standalonegapTCN remains besteligible, productionunchanged. Its target-slotidentity transfer risk is unresolved; target-match accuracy unknown. Finalfit/export/reproduction/validator/sealedevaluation remain pending. No new tests/model/scorer execution during audit.

## November 11: fixed two-view rotation ensemble pending

Registered one inference-only probability average of original and180degree rotated input, using retainedgapTCN checkpoints and uniform16decode. Negate centeredobjectXY/velocity forplayers ANDball; preserveH/Aroles/outputorder/core9. Samefivefolds/tenfrozenconditions; parentreconstruction andbothviewreload/exactensembleCSV required. No learnertraining, CatBoost, geometry/weightsearch or protecteddata. Fullgate unchangedagainst .597707/.463139. Source/protocol experiments/tcn-rotation-2026-11-11/, command docs/run-tcn-rotation.md.46contracts supplied but unexecuted; quality/runtimeunknown. Extra neuralforwardviews increaseinferencecost anddo not resolve temporalidentityrisk. No productionpromotion; targetaccuracyunknown.


## November11: rotation ensemble passes development gate

Equal original/180rotation probability averaging raises mean spellF1 to .602155clean/.477682corrupted, macro .919370/.838611. Median corruptedgain+.014850, pairedspell+.016578,3/5wins and pairedmacro+.005864 pass allcriteria. J03WOH/J03WPYpairedregressions disclosed.46recordedcontracts/10bothviewreload/batchcases,158sourceinput/30candidateCSV/10parentCSV/5modelhashes verified byread-onlyaudit; no newmodel/scorer execution. Evidence experiments/tcn-rotation-2026-11-11/result-review.md. Neweligibleleader, notproductionpromotion. Extra2neuralviews and targetslotidentityrisk remain; targetaccuracyunknown. Winner-specificfinalfit/export/validator/cleanenvironment/freshclone/sealedsteps outstanding.

## November11: broader research refresh, no model adoption

New literature lead arxiv2604.01859 (CVPR2026workshop) supports examining boundary-aware training rather than another encoder replacement. A single training-only boundary objective is a prospective project proposal, not a faithful implementation of its two-loss method or a proven football gain. Coefficients/targets/masks/budget must be locked after an explicit bounded amendment. Fixed seed ensembling is another practical option with increased total compute. Conditional RFDETR-Soccernet metadata offers a possible video-ball observation branch, but checkpoint rights/provenance/compatibility and an externally labelled synchronized possession-video evaluation path remain unverified. No dataset/weights/code downloaded or new model tested. Reports literature/high-upside-methods-synthesis-2026-11-11.md and companions document source/metric limitations, transfer evidence and failedfetches. No estimate of a winning/ceiling score. Target-match accuracy remains unknown.


## November 11 — Approved boundary objective, prepared for user execution
The completed rotation run remains the eligible development leader: mean spellF1 .602155 clean / .477682 target-like corrupted. Its16 audit artifact hashes and30 CSV hashes were rechecked unchanged; this is the same result, not an independent rerun. Production remains CatBoost16; target accuracy unknown.

One explicitly approved, bounded objective amendment adds a training-only32-to-1 boundary head to the original motion TCN: original crossentropy +0.1 balanced BCE on exact adjacent H/A/D transitions. Preserve motion/history, main initialization, original five LOMO splits,20k updates/batch8, independent training/evaluation gaps, rotation average and decoder16. No artificial X/half/crop transitions or target/held-out training labels. Eight synthetic tests supplied alongside existing46; all execution remains user-owned and none has been run by the assistant. Two full fits per fold, saved objective components, checkpoint RNG restoration and both-view reload/batch CSV checks precede the unchanged full promotion gate including+.01 median corrupted gain.

Protocol/source/input locks under experiments/tcn-boundary-2026-11-11; command docs/run-tcn-boundary.md. Partial independent core review plus root remaining source review documented in docs/tcn-boundary-design-review-2026-11-11.md (agents hit usage limits). This is not runtime verification. Research rationale literature/high-upside-methods-synthesis-2026-11-11.md; paper motivates a hypothesis, not a predicted football improvement. No new dependencies, data, weights, external publication or submission. Stopped tracks remain closed; failure rejects this fixed objective with no automatic rescue. Nov16 freeze and release qualification remain.


November11 plateau reassessment: three agent reviews distinguish clean plateau (~.60) from robust improvement (.323476 CatBoost→.477682 currentTCN). Current short recall remains125/732clean and92/732corrupted atIoU.5; rotation mainly reduced spurious spells. No ceiling established. New primary T-MAE2025 soccer masked-trajectory pretraining evidence motivates conditional eligible-PFF-geometry pretraining followed by IDSSE-only fine-tuning, without mixing provider possession labels. Different eventmAP task/stabletracks/halftime splits and unknown implementation licence mean no adopted model or forecast. Additional compute requires a locked budget amendment and matched-compute control. Root recommends pendingboundary plus at most one conditional learning route before qualification; scientist ranks seedensemble lower risk. No stoppedtrack reopened or experiment executed. Boundary userlog54contracts pass; no finalquality result at inspection. Reports docs/metric-plateau-review-2026-11-11.md, docs/error-strategy-reassessment-2026-11-11.md and literature/training-methods-reassessment-2026-11-11.md. Production unchanged, targetaccuracyunknown.


## November 11 — Boundary objective rejected
The user-run fixed training-only boundary objective lowers mean spellF1 to.583063clean/.464355corrupted versus rotationparent .602155/.477682; macro .913443/.832788 versus .919370/.838611. Independently audited gateFAIL: medianprimary−.017762, pairedmedian−.012318,1/5wins; macromedian−.004693 passes alone. Shortspell recall atIoU.5 declines125→122/732clean and92→81/732corrupted despite fewerdead/livewrongframes. Rejectthisfixedobjective; no automaticcoefficient/width/refinementrescue.

Userlogs54contracts and10repeatfit/reload/batchCSVcasespass. Verified185registeredhashes,35compactmembers,10checkpoints,30candidate+10parentCSVhashes; no tests/model/scorerexecution or array/checkpointloadingbyassistant. Fullpermatchmetricsanddiagnostics under experiments/tcn-boundary-2026-11-11/evaluation/; independentreview result-review.md/result-audit.json inthatdirectory'sparent. Foldstagessum82.83minutes, nottotalwalltime/RAM. Keepeligible rotationmodel; productionCatBoost16unchanged, targetaccuracyunknown/slotidentityriskunresolved/releasequalificationpending. No protected/targetlabeluse or externalpublication. Prospectivepretrain/fine-tune route requires separatefeasibility/budget/protocol; none startedhere.

November11 supplied2019EPV paper read: possession valuation differs from full-matchH/A/D identification. Pressure/control surfaces and relativeformationlines are contextualideas; no spellF1benchmark/admittedcheckpoint or immediateexperiment. Avoid possession-labelconditioning when constructing attacker/defender features. Sourcehash/page-specific assessment literature/epv-paper-reading-2026-11-11.md. Winner/planunchanged.

November11TCN2023comparison: headlineframeaccuracy gains are not spellF1. Table3possession86.2−79.1=7.1pp differsfromabstract7.3; dead/alive89.2−56.0=33.2ppagrees. Current .602155/.477682spell and.919370/.838611macro cannotrankagainstpaperframeaccuracies/differentdata. Paperdefinedcurrentaccuraciesnotlogged. Evidence/retrievallimits literature/tcn-paper-metric-comparison-2026-11-11.md; no newrun.

November11 consolidated plan: docs/metric-improvement-plan-2026-11-11.md maps suppliedTCN/EPV/MDPI and T-MAE/structuredresearch to oneprospective maskedpretraining→IDSSEfinetuningroute with an extra-training control. Proposed40ktotalupdates perarm changesbudget andrequires exactprotocol/amendment;20fitpipelines withrepeats maximum,6–8hroughplanningestimate only. No code/runregistered/executed; no newresultbeyondboundaryrejection. Preserve allgate/stops/protectedrules andNov14–15qualification/Nov16freeze. Sourcepaperaccuracies/EPV/possessionpercentageerrors arenotspellF1forecasts.


November11 approved masked-geometry route prepared/preregistered: scripts/run_tcn_pretrain.py compares staged40k-supervised control to20k-observedmaskedballXY-reconstruction +20k-IDSSE fine-tuning. Both resetAdam and supervised RNG at20k; currentrotationparent/fullgate retained, then candidatefacesactualbest. Originalmotion/classnetwork/views/16decoder unchanged;66parameter training-onlyhead, no reconstructedcoordinates added to inputs. Geometrypool eachfoldPFF48+IDSSEother4, observation-onlyeligibleanchors and label-free loader; excludesheldout evenunlabelled/sealed/PFF16/target. Cachedgapfeatures were recomputed afterrawballmasking. Two exactfits perarm/fold,54contracts/bothviewreload/batchCSV supplied but NOTEXECUTEDbyassistant. Source review corrected fixture indexing and mappingretention.53manifests/371members bytehashes verified without loadingarrays. Protocol and source/input locks experiments/tcn-pretrain-2026-11-11; source review docs/tcn-pretrain-design-review-2026-11-11.md; command docs/run-tcn-pretrain.md. Maximum20pipelines/800kupdates,6–8hplanningestimate, updatesmatched notexactcompute. Noautomaticfollowup/productionpromotion/export or externalpush. Currentmetric usefuldevelopmentbaseline, nottargetaccuracy/competitionrank;17framecontext andidentity-transfer risks remain.

November11 comparablebenchmarksearch: officialtargetfullmatchsmooth50.2433spellF1 isexactmetricfloor, notwinningthresholdandnotdirectlyrankableagainstexternalmeans. Same5externalmatches smooth50.296145/.196645 versusretainedTCN.602155/.477682 isfairinternalcomparison. NewPossessionLab usesofficialscorer but.851stationary-live scoreissynthetic; realpublicclipsunlabelled, changedmotiongeneratorgivesdifferentranking. Reddit/XlimitedpublicsearchverifiednorealmatchcomparableSOTAscore; agentserviceusagelimits preventedcompletereports, rootfinishedsourceverification. Details literature/comparable-benchmark-search-2026-11-11.md; nonewmodel/scorerrun orprotocolchange. Targetunknown/registeredpretrainingunchanged.
