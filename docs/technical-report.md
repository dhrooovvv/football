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
