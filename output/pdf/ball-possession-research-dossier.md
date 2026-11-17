# Ball Possession Intelligence

Market, models and research dossier

Snapshot: November 10, 2026. Prepared for dhrooovvv.

# Executive brief

**Ball Possession Intelligence** turns player and ball observations into complete, reproducible possession timelines. The product opportunity is reliable tactical annotation when proximity rules are ambiguous and ball tracking is incomplete.

The research programme has produced a genuine development improvement: the best clean model reaches **0.6099 spellF1**, compared with **0.5177** for the CatBoost reference. The leading candidate under the agreed robustness-aware gate reaches **0.5925 clean / 0.4284 corrupted**. These are different strengths, not interchangeable winners.

**Positioning:** a possession-inference engine backed by match-grouped experiments, explicit missing-data handling and reproducible outputs. This is an engineering proposition, not a claim of commercial readiness or a verified competition lead.

**Evidence boundary:** five external development matches; about 7 hours 56 minutes and 713,489 graded frames at 25 Hz. Repeated development reuse limits independence. Target-match accuracy is unknown. Two sealed matches remain untouched until the November 16 freeze.

**Current status:** production remains CatBoost + penalty 16. Neural and ensemble candidates have passed development checks but still require clean-environment reproduction, target adapter integration and official validation before release. The interaction-aware TCN is prepared; no reviewed quality result is available in this dossier.

# Product story and market relevance

## The problem
An opponent may be closest to a passing ball without controlling it. Scrambles, aerial play, brief recoveries, stoppages and missing observations make possession intervals harder than a distance calculation. Frame accuracy alone can hide badly fragmented or mistimed possession spells.

## The proposed capability
Input: synchronised player/ball trajectories and explicit observation masks. Output: home, away and dead-ball timelines, with deterministic CSV export and independent half handling. Potential downstream uses include tactical review, possession sequences, event alignment and analyst workflow automation.

## What is supported today
A working strict adapter, baseline inference, temporal models, reproducible development experiments and a validated production export pipeline. The strongest evidence is the repeated held-out-match comparison against a frozen parent, not a polished interface or a public model's headline accuracy.

## What has not been established
Customer demand, market size, pricing, latency at production scale, willingness to pay, superiority over commercial providers or readiness to deploy the neural candidate. No TAM, revenue or customer claim is invented here. This dossier is technology/competitive research, not a commercial market-sizing study.

# How to read the scores

**spellF1:** one-to-one matching of H/A possession intervals at temporal IoUs 0.3, 0.4, 0.5, 0.6 and 0.7, then average F1. Dead-ball D segments are not possession spells. MacroF1 over H/A/D is the frame-level companion metric.

Clean means original external tracking. Target-like corrupted means the same matches with the frozen missing-ball pattern applied; it is not an independent second dataset and is not target-match accuracy.

Each development fold trains on four matches and evaluates the fifth. Scores are equal-match means. A large frame count does not create equally many independent examples: adjacent frames are correlated, and there are only five development match environments.

**The promotion rule is unchanged:** positive median paired clean/corrupted spellF1 gain; improvement on a majority of five matches; median macroF1 drop no greater than 0.01; plus median target-like corrupted spellF1 gain of at least 0.01. Tests and required reproducibility checks must pass. A numerical pass is provisional until release verification.

Reported paper accuracy, ball-position error, tactical-phase F1, event mAP and possession percentage cannot be converted into official spellF1. **0.8 is an aspiration, not a verified winning threshold.**

# Data assets, supervision and safeguards

|Source|Available / used|Compatibility and limits|
|---|---|---|
|IDSSE / DFL|Five development matches; two sealed matches excluded|25 Hz, team and alive/dead labels; provider conventions govern supervision. CC BY 4.0 with source credit.|
|PFF World Cup 2022|64 admitted matches: 48 training expansion, 16 transfer-only holdout|29.97 Hz broadcast-derived source resampled to 25 Hz. More-data trial failed; transfer measurements are not selection scores. No blanket redistribution rights inferred.|
|Competition delivery|Official tactical video, tracking, homography and tagging supplied|Used only for permitted format/alignment and label-free checks. Public labels never choose, tune or select a model. No hosted-model processing.|
|Metrica / SkillCorner and other open sources|Audited as possible additional data|Do not admit merely because tracking is open; usable compatible H/A/D supervision and terms must be verified. No additional compatible match count is claimed here.|

Dataset availability removes an access blocker; it does not ensure compatible labels, adequate supervision or cross-provider transfer. Adding PFF rows without a better source/label strategy worsened the tested model.

Sources: [IDSSE publication](https://doi.org/10.1038/s41597-025-04505-y), [IDSSE release](https://github.com/spoho-datascience/idsse-data), [PFF release](https://www.blog.fc.pff.com/blog/pff-fc-release-2022-world-cup-data).

# Platforms researched and actual coverage

|Platform / surface|What was done|What the evidence supports|
|---|---|---|
|Primary papers and institutional repositories|Reviewed soccer possession, ball inference, action spotting and temporal segmentation papers|Architectural hypotheses and benchmark definitions; not a transferable spellF1 forecast.|
|GitHub|Inspected author repositories, code, checkpoint metadata, licences and demo pipelines|Implementation feasibility and overlap risks. Repository activity is not proof of a new model release.|
|Hugging Face / author model cards|Checked TabICL and TabPFN weight sources and terms|Local tabular-model availability; no soccer possession advantage established.|
|Reddit|Research engine plus public-thread supplements; direct site requests sometimes returned 403 and fallback discovery was used|Recruitment and practitioner anecdotes. Proximity struggles on aerial balls/scrambles; no verified competitor spellF1.|
|Hacker News|Engine discovery in recent scans|Mostly irrelevant to possession modelling; no technical adoption decision based on it.|
|Twitter / X|Backend unavailable; domain-restricted public searches found no usable relevant posts|No successful X scrape or X consensus is claimed.|
|YouTube / GitHub discovery lanes|Requested or available in some earlier engine plans|Availability is not completed coverage; later quick scans reduced to Reddit/HN. No relevant full transcript study is claimed.|
|Polymarket|Earlier requested lane was unreachable|No relevant evidence; prediction markets are not a possession benchmark.|
|TikTok / Instagram / LinkedIn and other social lanes|No completed systematic technical collection established|Do not advertise coverage of all platforms.|

**Research windows:** October 7-November 6, October 9-November 8, October 10-November 9 and October 11-November 10, depending on the dated campaign. The November 9 engine retained one Reddit thread and three HN stories, largely irrelevant. The November 10 engine retained one recruitment thread and four HN stories; useful technical context came from direct Reddit supplements. Counts are not independent model findings.

No authenticated private competitor submissions, target labels or restricted match assets were sent to research services. Raw social outputs remain local; the curated technical findings are what informs decisions.

# Competitions and competitor expectations

## Documented precedents
**More Than a Hack 2026:** IpurdIAr won with a conversational tactical analyst combining positions, events and commentary. It did not publish a comparable possession-spell winning threshold. [FC Barcelona interview](https://barcainnovationhub.fcbarcelona.com/blog/ipurdiar-football-analysis-chatbot/)

**SoccerNet 2025:** dudek won Team Ball Action Spotting with 60.03 Team-mAP@1, using joint team/action prediction, broad pretraining and dense fine-tuning. Public training code exists. This is a different metric. [Official results](https://arxiv.org/html/2508.19182v1), [author code](https://github.com/int8/dude.k).

**SoccerNet 2026:** PAVE achieved 58.94 player-centric event macro-F1 through temporal player features, spatial attention and four complementary models. Action/player/timing matching is not possession interval matching. [Official results](https://arxiv.org/html/2607.07320v1).

## What rivals may bring - inference only
Plausible approaches range from proximity rules to trained temporal/player-interaction systems and multimodal video-plus-tracking pipelines. Cleaner labels, explicit control evidence, sufficient training and careful ensembles may matter more than model branding. We do not know current rivals' architectures, compute, private results or eventual ranks.

# Model landscape: possession and ball inference

|Model / family|What it offers|Decision and caveat|
|---|---|---|
|Nearest-player rules|Cheap possession heuristic and reference|Useful baseline, fragile around passes, contested frames and aerial balls.|
|CatBoost + Viterbi|Missing-value-aware tabular probabilities with coherent H/A/D decoding|Validated production reference, not a claim of state of the art.|
|Scratch BiGRU|Temporal learning over the original nine features|Fixed small blend failed; does not test every recurrent architecture or richer geometry.|
|Scratch trajectory TCN|Shared player encoding, team pooling, temporal convolutions, core context|20k updates improved held-out clean spellF1; current focal research family.|
|PathCRF|Player-only possession paths and dynamic structured inference|Code MPL-2.0; known-live dependency and conditional checkpoint split overlap prevent clean drop-in comparison. Event F1 is not spellF1.|
|TranSPORTmer|Masked socio-temporal attention and joint trajectory/state inference|Four state labels differ from H/A/D; original runnable licensed weights/manifests not verified. An adaptation in PathCRF is not the original checkpoint.|
|BallRadar|Set Transformer and hierarchical recurrent ball/possession inference|Public code found; root licence and pretrained-weight availability were unresolved in the audit.|
|CropDrop|Player image crops plus trajectories, masked multimodal pretraining|89.56% possessor / 85.85% state accuracy on different proprietary conditions; out-of-play sequences excluded. No verified turnkey checkpoint for this task.|

# Model landscape: alternatives and auxiliary tools

|Lead|Possible role|Current evidence / limitation|
|---|---|---|
|TabICLv2|Local pretrained tabular probability model|BSD-3-Clause code/weights; 10k/30k single-estimator trials and fixed blends failed the gate. Strong generic tabular results did not transfer here.|
|TabPFN / TabPFN-3.5|Local tabular alternative|Weight terms differ from code licence; competition/production rights and practical CPU fit need review. No project trial.|
|Set Transformer / attention pooling|Permutation-invariant interaction modelling|MIT author code checked; larger change than the current masked relative-XY experiment. No possession gain measured here.|
|MS-TCN / MS-TCN++|Temporal refinement and segmentation coherence|Other-domain segmental improvements are not our spellF1. Inspected MS-TCN code is MIT plus Commons Clause, not plain MIT.|
|ASRF / ASFormer|Boundary-aware refinement / temporal attention|Potential only if errors justify it; wrong-class refinement can hurt. ASFormer root code MIT checked; no project adoption.|
|TCN dilation / longer receptive field|Use a broader temporal history|Current network has 17 encoded-frame context, not 10 seconds merely because windows are 250 frames. Separate untested change.|
|ELASTIC|Event/tracking alignment aid|Auxiliary alignment lead, not a possession replacement.|
|TOTNet / ball trackers|Potential ball recovery|Ball tracking rather than H/A/D inference; requires its own visibility/alignment and lawful training study.|
|YOLO + ByteTrack / DeepSORT / BoT-SORT / Norfair demos|Detection, identity tracking and video analytics|Useful pipeline ideas; demo possession percentages and toy detector weights do not establish robust spell accuracy.|
|Tactical GNN-LSTM / temporal graph attention papers|Spatial and temporal team structure|Some use possession/status as inputs or work within known possessions, so their scores cannot benchmark inferring those labels.|

Model family names and downloadable code do not establish checkpoint rights, training independence or performance under missing-ball conditions. Do not import source solely because it is described as open.

# Development results and measured progress

<!-- CHART -->

The long TCN run demonstrated that the 200-update pilot was not a fair ceiling. The later blend and augmentation improved robustness at a clean-score cost. Each version is retained in the record; the clean leader and gate leader are explicitly different.

|Candidate|Clean spellF1|Corrupted spellF1|
|---|---:|---:|
|CatBoost + Viterbi 16|0.5177|0.3235|
|TCN 200 updates|0.1178|0.0823|
|TCN 2,000 updates|0.4349|0.2719|
|TCN 20,000 updates|0.6099|0.3867|
|50/50 CatBoost-TCN|0.6026|0.3970|
|Gap-trained 50/50 blend|0.5925|0.4284|

All means above use the same five development matches, evaluated clean and corrupted. They are reused development comparisons, not independent competition results. Neural/ensemble versions are development candidates; the production pipeline remains the validated CatBoost reference.

# Experiment ledger: what did not earn a place

|Experiment / track|Recorded outcome|What we learned|
|---|---|---|
|Penalty 8 -> 16|Promoted earlier under the then-current gate|Temporal decoding mattered; no long hard minimum spell length was imposed.|
|CatBoost gap augmentation + penalty 16|Rejected: paired median -0.001331, 2/5 improve|Corruption exposure alone did not help that fixed representation.|
|Rolling whole-pitch aggregates, 2.5s|Rejected: primary median -0.005208|Broad speed/compactness context was insufficient in that bundle.|
|Gap-dependent / asymmetric / duration decoder variants|Three failures; track stopped|No more penalty search automatically. Duration estimator had censoring limitations; failure does not disprove all duration models.|
|Nested CatBoost settings search|Rejected: 1/5 improve, primary about -0.000035|No benefit from the registered settings policy.|
|IDSSE + PFF48 training expansion|Rejected: 0/5 improve, primary median -0.034930|More rows did not resolve source/label/visibility differences. Transfer results remain diagnostic only.|
|Small nine-feature GRU blend|Rejected: primary median -0.007520|Sequence learning cannot be judged independently of input information and training budget.|
|TabICL 10k / 30k contexts + fixed blends|Rejected: blend primary medians +0.001995 / +0.001606|Tiny corrupted gains did not pass the full gate. No seed/weight sweep followed.|
|Short temporal-control feature bundle|Rejected: primary median +0.000115|Short proximity summaries did not meaningfully beat the parent.|
|TCN 200 / 2,000 updates|Rejected: both below CatBoost|More training helped substantially, but insufficient held-out quality at those budgets.|
|TCN 20,000 updates|Passed development gate|5/5 paired improvements; clean mean 0.6099, corrupted 0.3867.|
|Fixed 50/50 CatBoost-TCN blend|Passed vs 20k TCN|3/5 paired improve; primary median +0.015717; clean mean declined.|
|Training-gap TCN + fixed blend|Passed vs unaugmented blend|3/5 paired improve; primary median +0.020149; clean declined on all five, corrupted improved on all five.|
|Masked player-ball relative XY|Prepared; no reviewed quality result|One representation change, +72 weights; large run is user-operated.|

These outcomes are protocol-specific. Failed trials remain failures; broader families are not disproven. Earlier narrower gates and later +0.01 requirements are not retroactively conflated.

# Why the TCN started working

A fixed training-segment diagnostic separated learnability from generalization. At 200 updates it reached 64.95% training accuracy, full-segment cross-entropy 0.810 and decoded training spellF1 0.0545. At 2,000 updates it reached 97.88% accuracy, cross-entropy 0.0716 and decoded training spellF1 0.8056.

**That 0.8056 is training fit only. It is not our development score and cannot qualify a model for promotion.** It justified a larger fixed-budget held-out comparison. The 20,000-update experiment then supplied actual development evidence.

The TCN uses per-object temporal encoding, masked home/away/ball pooling and temporal convolutions. Its neural receptive field is 17 encoded frames: +/-8 samples, approximately 0.68 seconds of samples. Velocities extend raw dependence slightly backward, and gap age contains longer history as a scalar. A 10-second input window does not make the learned receptive field 10 seconds.

The parent has no explicit player-ball interaction channel before player pooling. The prepared experiment tests whether a direct masked relative position helps distinguish genuine control from mere nearby motion, without a new attention architecture.

# Error audit: what remains hard

Forty cached cases compare CatBoost, standalone 20k TCN, unaugmented blend and augmented blend. This is descriptive analysis of existing predictions, not another model trial.

|Model|Short-spell recall, clean|Short-spell recall, corrupted|
|---|---:|---:|
|CatBoost|0.101|0.077|
|Standalone TCN|0.201|0.131|
|Unaugmented blend|0.143|0.096|
|Gap-augmented blend|0.138|0.100|

Short means <=2 seconds and recall uses IoU 0.5. Pooling short-spell counts here differs from equal-match headline means.

For the leading gap blend, observed-ball wrong-team errors total 44,143 clean frames versus 1,233 dead/live errors. Under corruption, observed-frame wrong-team errors total 28,147 versus 960 dead/live errors. These are correlated frame counts, not an additive attribution of spellF1 loss.

The gap blend reduces corrupted spurious spells from 523 to 440 versus the unaugmented blend. This weakens the case for adding indiscriminate smoothing. Missed brief possessions and team-control evidence deserve attention. Matched boundary offsets are conditional on a match within two seconds; unmatched boundaries must not be hidden by reporting only a median shift.

# Improvement roadmap: one question at a time

## Now: masked relative player-ball XY
Add relative position and a pair-valid mask before object pooling. Both observations must exist; otherwise relation channels are zero with mask zero. Ball-self relations remain zero. No fabricated ball position, relative velocity, attention, larger context or decoder change is bundled. Input 5->8 adds 72 weights; output width stays eight.

Same 20k budget, five LOMO folds, training-gap mix, frozen evaluation, fixed 50/50 CatBoost blend and penalty 16. The comparison parent is the current augmented blend. A quality pass still requires release verification.

## Conditional later directions - not queued automatic experiments
If control errors persist, evaluate a separately registered attention or relational-pooling change. If matched and missed-boundary evidence supports a context deficit, test one receptive-field expansion with a fixed halo contract. If over-fragmentation dominates, investigate a boundary-aware loss rather than a hard long minimum spell duration. If provider dominance is supported by training-row analysis, test source mixture separately.

None is an expected numerical gain. Do not combine several ideas into one trial, tune on public labels, use sealed results to rescue a model, or treat a social-media demo as an independent benchmark. Stop each track at the applicable failure limit.

## Before any production promotion
Reproduce in a clean environment and fresh clone; establish the target adapter's tracklet/identity contracts; train the approved final configuration with fixed seeds; run the official CSV validator; confirm identical bytes across repeated runs. Format validity is not accuracy evidence. These checks remain pending for the neural candidates.

# Compute, reproducibility and long-run workflow

The main registered training runners use one CPU thread and no custom memory cap. The M3 GPU is not used. A previous process observation around 1.7 GB is not a peak-memory measurement or a guarantee for later runs.

A subsequent synthetic operational check found two threads faster than one for small update batches, while 11 threads were slower. A 16,384-frame label-free check with trained parent weights lifted to the interaction input shape produced identical one/two-thread CSVs, but did not test actual future interaction weights or prove full training equivalence. The user chose the original single-thread runner. No faster training runner was adopted.

Two fits per fold check exact training repeatability; saved-model reload and batch-size variants check output bytes. Within-environment repeatability is not clean-environment reproduction, and synthetic tests are not predictive-quality evidence.

Hours-long jobs are user-operated. Short development checks may run autonomously under the latest authorization. Failures and partial outputs are retained for review; no deletion to turn a failed protocol into an unrecorded retry.

# Delivery timeline and decision gates

**Current architecture freeze: November 16, 2026.** Older notes referring to November 12 or 13 are historical and superseded. Existing runners conservatively block new research starts at the beginning of November 16 to reserve the day for freezing and delivery checks.

|Window|Priority|Exit condition|
|---|---|---|
|November 10-13|Complete the fixed interaction experiment; review evidence|All five clean/corrupted cells and gate; no cherry-picked match or checkpoint.|
|November 14|At most one separately justified follow-up if time and stop rules allow|Protocol committed first; enough time remains for complete verification.|
|November 15|Reproduction, integration and technical packaging|Clean-environment/fresh-clone checks; no known release gap disguised by a better development score.|
|November 16|Freeze configuration, then sealed evaluation once|Candidate plus supplied baselines, clean/corrupted. Poor results trigger bug/transfer investigation, not tuning.|
|November 17|Deadline buffer / explicitly authorized delivery only|Confirm official cutoff/timezone before relying on the buffer. No action after November 17.|

An identical-configuration all-compatible-data retrain variant may be prepared for the user's decision; it is not selected automatically. Never include sealed matches in training. No external submission is authorized by this dossier.

# Research interpretation and communication rules

## Claims that can be made
A fixed-budget trajectory model improved the recorded external development results. A fixed blend and training-gap intervention improved the robustness-focused gate with a documented clean-performance trade-off. Experiments were registered before execution and rejected changes were retained in the record.

## Claims that cannot be made
Competition-winning performance; target accuracy; a forecast of 0.7 or 0.8; commercial deployment readiness; comprehensive social-platform coverage; an independent proof from five repeatedly reused matches; unrestricted rights to all datasets or pretrained weights.

## Suggested external-facing positioning, if later approved
"A reproducible possession-inference pipeline designed for incomplete football tracking, combining temporal player modelling, explicit observation masks and structured possession timelines. Development results are measured by whole possession intervals rather than possession percentage alone."

This wording is a draft proposition, not permission to publish. Do not attach reviewed neural development scores to a production claim until release validation and independent evaluation are complete.

# Source map and archival reading guide

This dossier consolidates the recorded research through November 10. It is not a new systematic search. Links and licence findings reflect the dated inspections in the source notes; verify again before adoption.

The next appendix preserves every root-level literature Markdown brief and selected independent scientific/data/architecture reviews. Historical assertions such as "not yet executed", model choices and earlier freeze dates are preserved as written, not current status. **The executive brief and measured-results section supersede those historical statuses.**

Raw search-engine dumps, source code, training weights, video, tracking arrays, private prediction rows and competition labels are not embedded. The full project journal remains in ball.md; this dossier summarizes its decisions and carries a hash-based source inventory for traceability. No new model test or target-score evaluation was run to create the document.


# Research archive 01 - borghesi2023

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/borghesi2023.md

# Using Temporal Convolutional Networks to estimate ball possession in soccer games

Authors: Borghesi, Costa, Morra, Lamberti. Year: 2023.
Source: https://iris.polito.it/handle/11583/2976470

Prior audit verified author abstract: H/A/D tracking task; reported frame accuracy does not measure this competition spellF1. Full reproduction not performed.

Evidence scope: documentation/abstract or earlier audit record, not reproduced experimental results.



# Research archive 02 - catboost

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/catboost.md

# CatBoost missing-value processing

Authors: CatBoost maintainers. Year: living documentation.
Source: https://catboost.ai/docs/en/concepts/algorithm-missing-values-processing

Numerical NaNs are supported with configurable handling. This removes a preprocessing obstacle but does not prove possession accuracy.

Evidence scope: documentation/abstract or earlier audit record, not reproduced experimental results.



# Research archive 03 - competition-precedents-2026-11-10

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/competition-precedents-2026-11-10.md

# Comparable competitions and documented solutions  -  November 10, 2026

## Scope and verdict

Primary organizer papers, official task repositories and a winner's own repository were checked. No competition match assets, labels, current public scores, private competitor submissions or model runs were accessed. This is an adjacent-competition audit, not a prediction of the current leaderboard. The 2026 More than a Hack edition is a direct organizational precedent, but its winning product was a tactical conversational system rather than a publicly scored H/A/D interval predictor. SoccerNet supplies documented quantitative precedents for soccer perception and temporal reasoning; its metrics are different from this project's spellF1.

**High confidence:** strong competitors can bring domain-specific pipelines, learned temporal/player interaction models, transfer learning and carefully validated ensembles. **Low confidence:** which current teams are actually doing any of these, what their score will be, or whether a released model will transfer to this task. No public evidence supports a numerical competitor-score forecast.

## Direct predecessor: More than a Hack 2026

FC Barcelona Innovation Hub's April 30, 2026 interview identifies **IpurdIAr** as the winning project. It combines positional information, derived match events and commentary transcription into a conversational tactical analyst. The team describes using provided 25Hz positions, spatial zones, pressure/proximity, ball motion and defensive-block descriptors; it did not build its own computer-vision tracker. Whisper transcription was linked to game moments. The interview is evidence of the product and its ingredients, not a benchmark of possession boundaries: no comparable possession-spell score or independently replicated error rate is provided.

Sources: [FC Barcelona Innovation Hub interview](https://barcainnovationhub.fcbarcelona.com/blog/ipurdiar-football-analysis-chatbot/), [Metrica organizer recap, March 5, 2026](https://www.metrica-sports.com/blog/inside-the-bar%C3%A7a-innovation-hack-ai-football-data-and-tactical-intelligence-at-talent-arena-2026).

The [official 2026 starter repository](https://github.com/metrica-sports/more-than-a-hack) describes tools for loading tracking/Smart Tagging, producing visualizations and exporting custom pattern XML for Nexus playlists. It is a starter, not the verified winner's source. I did not locate an authenticated public IpurdIAr source/checkpoint release. This means release status is unverified, not that no release exists.

**Implication:** a polished tactical assistant can win an application hackathon without establishing the accuracy of possession segmentation. Building a chatbot would not address the current Phase 1 ranking objective and is not recommended as a metric intervention.

## SoccerNet 2025: team ball action spotting

The [official results paper](https://arxiv.org/html/2508.19182v1) reports **dudek, 60.03 Team-mAP@1**, versus baseline 51.72. Inputs are broadcast videos; labels are 12 action types and acting team. Seven annotated games plus two private challenge games are described. Matching is for point events within one second, using team-aware average precision - not possession intervals.

The winner refined T-DEED, unified action/team predictions, used video augmentation, pre-trained on 500+ broadcast matches and fine-tuned on the dense challenge data. Its [author repository, int8/dude.k](https://github.com/int8/dude.k), releases training/evaluation and preprocessing code. Public code is verified; licence rights and a usable pretrained checkpoint were not audited here. This is not a plug-in H/A/D model.

The author README warns its full frame-extraction route can require around **1.2TB extra disk** and up to **24 hours**, depending on hardware. That is an author estimate for its own workflow, not a measured cost on this Mac. Copying the entire video-pretraining pipeline is therefore a substantial commitment, not an immediate small experiment.

## SoccerNet 2026: player-centric ball action spotting

The [official July 8, 2026 results paper](https://arxiv.org/html/2607.07320v1) reports **PAVE, 58.94 Macro-F1@0.15**, versus baseline 46.41. Predictions must match action class, team, jersey and timing within ±12 frames. These are eight point-event classes, not H/A/D spans.

PAVE adds temporal attention to per-player visual features and spatial relations between players before following them through time. Four independently trained variants are fused, using agreement to suppress false positives with special handling for rare tackles. This supports complementary player/spatial/temporal reasoning as an architectural lead. It does not justify ensembling arbitrary weak models, guarantee possession performance or establish hardware feasibility. A public winning implementation/checkpoint was not verified in this audit.

## What current competitors may bring  -  inference only

| Plausible approach | Basis for expecting it | Uncertainty / project consequence |
|---|---|---|
| Strong geometric rules with explicit temporal ownership/state logic | Prior tracking-based products and official starters make this accessible | Simple rules can still win when semantics and timing are correct; no evidence of current team use |
| Larger temporal/player-interaction models with verified pretraining or sufficient supervised training | SoccerNet winners use temporal context, per-player features and transfer learning | Dataset/model licence, input identity, missingness and H/A/D conversion remain obstacles |
| Local visual evidence to recover the ball or identify possession cues | SoccerNet tasks use video/player crops and interaction cues | Homography, detection errors, GPU/storage cost and target-data restrictions limit immediate transfer |
| Complementary ensembles and calibration | PAVE's diverse independently trained components | Existing project TabICL/GRU blend failures show combination alone is not enough; gate remains decisive |
| Better labels, transitions and validation rather than novel architecture | Task-specific temporal matching and team association alter competition rankings | Requires compatible supervision and independent match evidence; no current competitor labels available |

These are informed hypotheses about the competitive field, not a report of inspected current submissions. The prior competitions do not establish a standard spellF1 target, and a score near 0.6 in one task cannot rank above or below 0.5177 in another.

## Practical recommendation

Do not adopt a published competition model merely because it won. Extract the principles: fit labels to the actual task, retain relevant player/ball evidence, establish that training learns the task, use genuinely complementary outputs, and validate on independent matches. Given the completed TCN failure, first diagnose its ability to fit a small external training segment under a separately registered diagnostic before increasing budget. No competition precedent rescues its failed score or authorizes a sweep. Preserve the user-run experiment policy and November 16 sealed evaluation; no new experiment was performed here.

Open questions that matter: admissible local checkpoints and their training overlap; enough compatible supervision for player-interaction learning; visibility/domain differences; and competitor methods that remain private. A current score forecast is not possible from these sources.



# Research archive 04 - competitor-practice-review-2026-11-10

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/competitor-practice-review-2026-11-10.md

# Competitors, precedents and possession practices  -  November10,2026

## Executive finding

Public evidence does not reveal current competitors' private submissions or attainable official spellF1. Predicting rival scores or saying they all use transformers would be unsupported. Adjacent winning systems show that strong video/football entries can combine spatial player interactions, temporal context, pretrained visual representations, training refinements and selective ensembling. Those are research directions, not direct replacements for the frozen CatBoost16 or evidence of .8spellF1. No experiments or new datasets run for this research.

## Documented precedents

See competition-precedents-2026-11-10.md for primary official sources and scope. More Than a Hack2026 rewarded a conversational football analyst integrating tracking, events and commentary, rather than a comparable H/A/D possession interval benchmark. Its winner does not supply a score ceiling for this qualifier. SoccerNet2025TeamBallActionSpotting and2026PlayerCentricBallActionSpotting are closer technical precedents but detect discrete timed actions and team/player identities rather than full possession intervals.

The official [SoccerNet2026results](https://arxiv.org/html/2607.07320v1) documents PAVE's temporal player features, spatial/temporal attention and fusion of four trained variants. It achieved58.94macroF1 under action/actor/temporal matching, not possession-spellF1. Other submissions explicitly used ball geometry, kinematics and observation masks. This supports prioritizing data/interaction quality and adequate training, not copying an ensemble before it contains strong complementary candidates.

## Current possession practices: not one universal standard

1. Rules/kinematics: near-ball players, ballspeed/direction changes, sustainedcontrol versus fly-by, transfers, separate restart/deadball logic. [Vidal-Codina2022](https://link.springer.com/article/10.1007/s12283-022-00381-6) describes a possession-first eventing framework. It has game-status information; it does not establish robust inference when our ball disappears. Detection-rate headlines are not spellF1.
2. Learned temporal models: per-player trajectory embeddings, team aggregation, TCN/RNN/attention and structured sequence decoding. [TCN2023](https://www.sciencedirect.com/science/article/pii/S0957417423002816) addresses H/A/D-like states but reports accuracy on different data conditions. [PathCRF](https://arxiv.org/abs/2602.12080) models possession paths for events in known-live segments. Neither is a verified drop-in benchmark for this challenge.
3. Multimodal research: trajectories plus local player image features, with missing-modality handling. [CropDrop](https://arxiv.org/abs/2512.19528) is a research example, not a verified available checkpoint for our conditions. Local video work needs lawful training data, alignment and expensive engineering; restricted assets must not be sent to hosted models.

Definitions also differ. [Opta](https://theanalyst.com/articles/opta-football-stats-definitions) ends possession when the opposition gains control; [FIFApossessioncontrol](https://www.fifatrainingcentre.com/en/fwc2022/efi-metrics/efi-metric--possession-control.php) explicitly includes in-contest time. Neither should be silently remapped to projectH/A/D labels. Follow the challenge definitions and validate adapters. Match possession percentages, frame accuracy, eventmAP and spellF1 answer different questions.

Public demo pipelines should not be mistaken for robust solutions: [Tryolabs' ownREADME](https://github.com/tryolabs/soccer-video-analytics) describes the released ball detector as a toy overfit to a few videos. Its implementation is illustrative, not evidence of a competitive possession score.

## What rivals may bring  -  inference, not observed submissions

Plausible entries span three levels: proximity/rule baselines; learned temporal player-control systems with carefully audited labels/masks; and resource-intensive video+tracking systems with stronger pretraining and ensembles. The strongest practical advantages may be cleaner supervision, better missing-ball evidence, explicit control/boundary modelling and training/validation discipline rather than one fashionable model name. No probability, architecture distribution, competitor identity or score estimate is justified by the public record.

## Implications for our project

Our selected .517654clean/.323476corrupted are external development results, not competition standing. The200-step scratchTCN failed .117838/.082347, despite contract/repeatability passes. It was a compact fixedpilot, not a reproduction of the publishedTCN or a competitive training programme. We should not call its failure proof that temporal models cannot work, or assume moresteps willfix it. The next justified diagnostic is a preregistered small-training-segment overfit test with classshares/learningcurve/unsmoothedversusdecoded behaviour. This remains a proposal: the boundedTCNtrial is closed and no dataset commands run here. An amendment and protocol are required before any diagnostic or longer-fit experiment; user retains execution. Modelpromotiongate, sourceoverlaplicencechecks, no targetpubliclabelselection and November16freeze remain.

## Social evidence and limitations

See possession-social-2026-11-10.md for actual engine coverage, Redditpermalinks and Xavailability. Recruitment posts establish interest only; mirroredcrossposts do not identify multiple independent teams. Technicalcomments are practitioner anecdotes, not benchmarkvalidation. Publicsearches forXyielded no usable relevant posts, so no privatecompetitorintel or Xconsensus claim is made. Socialretrieval limitations cannot establish absence of stronger competitors.



# Research archive 05 - expanded-model-review-2026-11-06

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/expanded-model-review-2026-11-06.md

# Expanded alternative-model search, November 6, 2026

User explicitly requested a further search for a better approach. Executed a new last30days three-query search for possession transformers, TranSPORTmer/BallRadar/PathCRF and masked multimodal pretraining over October 7-November 6. Engine output and diagnostics saved beside this note. Returned community material did not establish a relevant possession-model improvement. Reddit discovery had partial coverage; Polymarket unreachable; X disabled. Do not treat these outcomes as absence of new research. Older primary papers were included as explicitly older architectural context.

## Stronger related-task research is real, but project superiority remains untested

**Multi-Modal Soccer Scene Analysis with Masked Pre-Training**, WACV 2026 (arXiv December 2025): https://arxiv.org/html/2512.19528v1 . Combines player trajectories/types/crops, socio-temporal transformers and CropDrop. Table 1 reports 89.56% possessor accuracy and 85.85% ball-state accuracy, versus TranSPORTmer 83.79% / 79.77% and BallRadar 78.12% possessor accuracy. These are authors' frame-accuracy measurements on their proprietary 283-match dataset, not competition spellF1, not a CatBoost comparison. Crucially §4.1 excludes sequences containing out-of-play frames. Its state accuracy therefore does not demonstrate live/dead detection. Public runnable implementation/checkpoints were not verified by paper and targeted code searches. This is a serious research architecture, but not currently a turnkey candidate.

**TranSPORTmer**, ACCV 2024: https://arxiv.org/html/2410.17785v2 . Set-based socio-temporal attention, explicit observation masks, trajectory imputation/inference and global pass/possession/uncontrolled/out-of-play states. Appendix §4.2 shows support for incomplete player observations and improved ball inference versus BallRadar on its dataset. The model does not directly establish target H/A/D spell performance or handle changing slot identities automatically. Public runnable implementation/checkpoints not verified. Most relevant additional architecture lead for masked inputs; no adopted replacement without code/data/runtime and independent evaluation.

**BallRadar**, KDD 2023: https://github.com/hyunsungkim-ds/ballradar . Public code, Set Transformer + hierarchical Bi-LSTM, possession classification then ball reconstruction. README documents public Metrica data and private Fitogether data, with a public-data reproduction path and training scripts. Pretrained checkpoint availability not verified. More reproducible research lead than undocumented demo pipelines, but identity/missingness/dead-live compatibility remains unresolved.

**PathCRF**, KDD 2026: prior detailed review remains valid. Pretrained weights make it the clearest checkpoint lead, but known-in-play and complete-player assumptions require major adaptation. No newly executed checkpoint inference in this search.

## Decision

Correct any implication that CatBoost is the state of the art. It remains a practical first trainable candidate for our current aggregate features, not a proven best architecture. Expand the neural shortlist to TranSPORTmer-style masked socio-temporal modelling and the multimodal CropDrop approach, conditional on verifiable implementation, training sources and compute. Published accuracy on other tasks/datasets is insufficient to promote one over our candidate. No model experiments executed; no target assets accessed or labels used. Next remains external label/split verification; any comparison requires preregistration.

Supplemental code lead: PathCRF includes a TranSPORTmer-named adaptation at https://raw.githubusercontent.com/hyunsungkim-ds/pathcrf/main/models/transportmer.py . Research subagent verified its existence; it is not verified as the original four-state model or a matching pretrained checkpoint. Reuse requires input/state/weight audit before experiment. Set permutation equivariance does not automatically solve identities changing within temporal windows.



# Research archive 06 - idsse

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/idsse.md

# An integrated dataset of spatiotemporal and event data in elite soccer

Authors: Bassek, Rein, Weber, Memmert. Year: 2025.
Source: https://github.com/spoho-datascience/idsse-data

Official repository confirms seven matches, tracking/events, and CC-BY attribution. Label adapter still unexecuted.

Evidence scope: documentation/abstract or earlier audit record, not reproduced experimental results.

2026-11-06 adapter evidence: official floodlight DFL parser at https://raw.githubusercontent.com/floodlight-sports/floodlight/master/floodlight/io/dfl.py defines possession {1:Home,2:Away}, ballstatus {0:Dead,1:Alive}; raw frame N is source identity, T supports 25Hz verification, pitch coordinates centered. Metadata HomeTeamId and GuestTeamId provide explicit mapping. Figshare API article 28196177 provides file sizes and MD5 checksums. Only five development matches downloaded under protocol 6b71d10; sealed assets excluded. Attribution: Deutsche Fußball Liga (DFL), Bassek et al. Scientific Data 12,195 (2025), CC-BY4.0.



# Research archive 07 - kim2023

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/kim2023.md

# Ball Trajectory Inference from Multi-Agent Sports Contexts Using Set Transformer and Hierarchical Bi-LSTM

Authors: Hyunsung Kim, Han-Jun Choi, Chang Jo Kim, Jinsung Yoon, Sang-Ki Ko. Year: 2023.
Source: https://arxiv.org/abs/2306.08206

Player-context inference uses intermediate possession prediction. Relevant to missing ball; deferred because coordinate reconstruction is not required for the output.

Evidence scope: documentation/abstract or earlier audit record, not reproduced experimental results.



# Research archive 08 - open-model-primary-audit-2026-11-08

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/open-model-primary-audit-2026-11-08.md

# Open possession models: primary-source audit

Audit date: 2026-11-08. Read-only public metadata and source inspection. No weights, raw matches or prediction rows downloaded; no training or inference executed. This is feasibility evidence, not evidence of improved project spellF1.

## Search scope and recency

Three pre-engine searches covered open soccer ball-possession models, checkpoint releases, and relevant communities. Verified topic discussions in r/computervision and r/sportsanalytics; r/MachineLearning is an inferred broader community. Search surfaced an October 9 YOLO11/BoT-SORT analytics demo, but no controlled H/A/D spellF1 result or demonstrated replacement for our possession classifier. A recent soccer reinforcement-learning paper concerns action valuation using possession context, a different task. Search dates and crawl dates are not model release dates. Absence from these searches does not prove no other open model exists.

## PathCRF: strongest auditable research lead, not a drop-in replacement

Official paper: <https://arxiv.org/html/2602.12080v2> (v2 June 1, 2026; KDD 2026). Official repository HEAD inspected: `1b7c6f85a6b78c92e4543fde72ca2b86a933f997`, commit June 8, 2026. Public GitHub metadata last-pushed June 8, 2026; this is older foundational work, not a newly verified October/November release.

- Repository code licence: MPL-2.0, explicitly present in [LICENSE](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/LICENSE). This does not by itself establish unrestricted rights to underlying data or separately licensed assets.
- [README](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/README.md) lists five trained variants in `saved/100`, `110`, `120`, `130`, `140`; public tree contains `state_dict_best.pt` and `state_dict_best_acc.pt` for each. Inspected filenames/JSON metadata only, not binary contents.
- [saved/140/args.json](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/saved/140/args.json): Sportec source, `lomocv=true`, `cv_fold_idx=6`, target 5 Hz, ten-second windows, eight node inputs, set-transformer/socio-temporal backbone, dynamic sparse CRF, approximately 3.43 million parameters. This is not a TranSPORTmer checkpoint.
- [datatools/utils.py](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/datatools/utils.py#L98) constructs episode IDs only on frames where `ball_state == "alive"`. [inference.py](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/inference.py#L880) loops only over positive episode IDs. Public wrapper therefore assumes supplied live segmentation; its results do not establish end-to-end dead/live inference.
- [inference.py lines 394 onward](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/inference.py#L394) gathers stable named-player columns and selected coordinate/velocity/speed/acceleration inputs; if any selected feature is missing, it returns no episode prediction. Agent permutation equivariance does not establish tolerance to arbitrary identity switches across time.

### Checkpoint overlap warning: conditional, not a verified training manifest

The [public tree](https://github.com/hyunsungkim-ds/pathcrf/tree/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/data/sportec_synced) lists filenames `J03WMX`, `J03WN1`, `J03WOH`, `J03WOY`, `J03WPY`, `J03WQQ`, `J03WR9`. No parquet contents were opened. [train.py lines 472-496](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/train.py#L472) sorts processed filenames; in LOMOCV, index 6 is test and preceding index 5 is validation; both are excluded from fitting.

**If** the processed training directory contained that canonical seven-file set when `saved/140` was trained, its JSON and current code imply fitting on our five development matches, validation on `J03WQQ`, and test on `J03WR9`. Exact checkpoint-to-input hashes and a contemporaneous training manifest were not established. Do not state that either sealed match was definitely fitted, nor claim the checkpoint is uncontaminated: development reuse and sealed-validation exposure are material risks. Do not load it for independent development/sealed comparison. Metadata inspection has not opened either sealed match's observations or labels.

## TranSPORTmer: relevant masked-trajectory architecture, unavailable turnkey model

Original [ACCV 2024 paper](https://arxiv.org/html/2410.17785v2) describes masked socio-temporal attention and four states: pass, possession, uncontrolled, out of play. These are not directly H/A/D. Original runnable code, licensed original checkpoints and training manifests were not verified in the inspected paper/repository sources; a paper licence is not a code/weights licence.

PathCRF supplies an [adaptation](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/models/transportmer.py) plus training scripts ([edge](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/scripts/transportmer_edge.sh), [CRF](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/scripts/transportmer_crf.sh)). These select trials 710/750, absent from the public saved checkpoint tree. The adaptation exposes ball/possession-edge outputs and optional possession macro heads; it does not establish delivery of the original four-state CLS model. It runs through PathCRF's data/inference wrappers and inherits the integration constraints above unless deliberately redesigned and tested.

## BallRadar: public implementation, licence and weights gaps

Official [repository](https://github.com/hyunsungkim-ds/ballradar), inspected HEAD `2486896cfb933ecd304489883241a00e3645ca8c`, commit July 6, 2023. GitHub repository metadata last-pushed February 3, 2026, which differs from main HEAD commit date and is not evidence of a new model release. No published GitHub releases were returned.

[README](https://github.com/hyunsungkim-ds/ballradar/blob/2486896cfb933ecd304489883241a00e3645ca8c/README.md) describes player-trajectory possessor classification followed by conditional ball reconstruction. Recursive tree inspection found no saved model binaries or root-level project licence. GitHub repository licence metadata is null; the vendored `set_transformer/LICENSE` does not establish a licence for all BallRadar code. Public visibility alone is insufficient to call the entire project freely reusable or pretrained. These findings are scoped to the inspected repository tree, not a proof that author-hosted checkpoints or permissions cannot exist elsewhere.

## CropDrop / multi-modal masked pre-training: paper evidence only

[WACV 2026 paper](https://arxiv.org/html/2512.19528v1) describes player trajectories, types and image crops, trained on 283 proprietary matches; out-of-play sequences are excluded. Its reported possessor/state accuracies address related tasks, not our H/A/D spellF1. No runnable licensed code/checkpoint link was verified in the inspected paper. This is a research direction, not an available drop-in open model.

## Decision

High confidence: public PathCRF code and weights exist, but its known-live wrapper, missing-player contract and checkpoint overlap risks prevent an immediate clean replacement test. Moderate confidence: TranSPORTmer-style masked player interactions are a plausible way to address missing-ball information; this is an architectural hypothesis, not a performance claim. BallRadar and CropDrop are currently weaker implementation candidates because usable licence/checkpoint provenance is unresolved.

Keep production unchanged. The next useful evidence is a bounded metadata/input-contract audit that establishes a licence, exact checkpoint training provenance, label-free live/dead behavior and adequate player identity/coverage without touching sealed matches or target labels. A new performance experiment would require its own committed protocol and explicit reopening of the already completed bounded sequence-model track; this audit does not authorize that reopening.

## Post-engine supplement: three searches, no performance experiments

After the engine completed, exactly three batched search queries covered (1) open soccer possession pretrained releases in October/November 2026, (2) original TranSPORTmer/CropDrop public code and checkpoints, and (3) general open tabular models applicable to the existing feature matrix. Follow-up opens and metadata reads verified the following primary sources. No additional search-query dispatch followed this batch.

### TabICLv2: new-to-this-project, credible emissions-only benchmark lead

Official [repository](https://github.com/soda-inria/tabicl), [documentation](https://tabicl.readthedocs.io/en/latest/), [paper](https://arxiv.org/abs/2602.11139), and [model card](https://huggingface.co/jingang/TabICL). Inspected source HEAD `d83091b845a8c5f7c087bd54964f755a9e560f45` was committed October 27, 2026; the [commit](https://github.com/soda-inria/tabicl/commit/d83091b845a8c5f7c087bd54964f755a9e560f45) adds prediction-consistency tests using synthetic data. This is a verified in-window maintenance event, not a new checkpoint or soccer-quality result.

- [Licence](https://github.com/soda-inria/tabicl/blob/d83091b845a8c5f7c087bd54964f755a9e560f45/LICENSE): BSD-3-Clause core; derived forecasting subdirectory has an Apache-2.0 notice. Author model card also declares BSD-3-Clause for weights.
- [README](https://github.com/soda-inria/tabicl/blob/d83091b845a8c5f7c087bd54964f755a9e560f45/README.md) lists default classifier `tabicl-classifier-v2-20260212.ckpt`. The paper was submitted February 11 and revised September 16, 2026, outside the fresh window. The checkpoint filename alone is not independent evidence of an exact public release timestamp.
- Synthetic tabular pretraining; explicit `fit`/`predict_proba` interface, local inference, and support for missing values. `fit` supplies labelled context to a pretrained predictor; absence of gradient training does not remove the need for match-grouped folds and fold-local preprocessing/context selection.
- CPU is supported. Author documentation recommends GPU for large datasets and describes CPU/disk offloading for large contexts. Million-row GPU scalability is not a measured single-thread CPU runtime or byte-reproducibility guarantee on this machine.
- Authors report strong generic TabArena/TALENT results; no H/A/D spellF1 result or direct comparison with this project's CatBoost exists. Treat this as a candidate, not a measured winner.

**Inference:** this is the most practical newly identified *open pretrained emissions-only* lead because it could retain the existing nine-feature interface and penalty-16 decoder, has available weights and a permissive licence, and synthetic pretraining avoids an identified football match-overlap dependency. However, identical nine-core inputs contain no extra whole-pitch player evidence when the ball is missing. A more powerful predictor cannot recover information absent from its inputs; whether it improves usable conditional probabilities and spellF1 remains empirical. Context cost on hundreds of thousands of correlated frames is the main operational uncertainty. A bounded CPU/memory/determinism feasibility test would come before any scored experiment, and requires a committed protocol if executed. No trial is authorized merely by this literature audit or by the earlier closed CatBoost/GRU track budgets.

### TabPFN-3.5: local open weights, restrictive terms and unproven fit

Primary [model card](https://huggingface.co/Prior-Labs/tabpfn_3_5) lists September-dated checkpoints, synthetic tabular pretraining, local inference code, and custom `tabpfn-3-5-license-v1.0`. [Official model documentation](https://docs.priorlabs.ai/models) dates the family report to September 2026 and lists up to one million training rows; this is older than the requested October 9-November 8 window. The card permits research/internal evaluation but restricts commercial or production use of model, derivatives and outputs. Do not treat Apache-2.0 inference code as the weights licence, or assume competition-deliverable rights without checking the actual intended use. No weights downloaded or terms accepted here. Hosted variants are excluded from this project regardless of availability. No evidence establishes better spellF1 or acceptable CPU cost; TabICLv2 has the cleaner open-licence path.

### Freshness result and recommendation after supplements

No newly released, suitably licensed soccer H/A/D checkpoint with a clean training manifest and measured comparable spellF1 was verified in the fresh-window searches. This is a limited-search result, not proof of absence. The searches did not establish original TranSPORTmer/CropDrop runnable licensed checkpoint availability. The main useful addition is the older TabICLv2 model plus verified October maintenance, while PathCRF remains the strongest domain-specific research architecture with material evaluation/integration constraints.

Recommendation: retain production now. If the user chooses to authorize a new model track, rank (1) a bounded TabICLv2 emissions-only feasibility/benchmark protocol for ease of clean comparison, (2) a substantially larger masked player-interaction architecture effort using clean, known training provenance. Do not present either as an established improvement. Existing stop rules, strengthened promotion gate, fixed splits, sealed boundary, CPU constraint and November 13 freeze remain unchanged.



# Research archive 09 - open-models-review-2026-11-08

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/open-models-review-2026-11-08.md

# Open-model decision review, November 8, 2026

## Decision and evidence standard

No audited replacement has demonstrated a higher project spellF1 than production. Keep nine core masked features, unaugmented CatBoost and Viterbi penalty 16. This is a research audit, not a model comparison or permission to reopen a completed experiment track. No training, inference, target-label access or sealed evaluation was performed.

The last30days engine ran once over October 9-November 8, with an explicit soccer-possession plan, no browser cookies and no private input. It returned 14 items: nine Reddit, three Hacker News and two GitHub. Social results were predominantly unrelated to possession inference. Reddit direct requests were blocked, archive requests partially failed, Polymarket was unreachable, YouTube returned no items, and X was not enabled. These limits prevent a comprehensive claim that no newer model exists. GitHub entries dated November 8 are observations of existing repositories, not verified releases that day. Earlier library findings were historical context only.

Evidence files: `open-models-2026-11-08-engine.txt`, corresponding `.log`, and `open-model-primary-audit-2026-11-08.md`. The primary audit pins repository revisions and records the limits of checkpoint provenance. Community popularity is not evidence of higher possession spellF1.

## Candidates

| Candidate | Verified availability | Relevant capability | Admission problem | Decision |
|---|---|---|---|---|
| TabICLv2, ICML 2026 | BSD-3-Clause code and public classifier weights | Local probability prediction over the existing nine columns; synthetic pretraining | CPU cost and deterministic output untested at our scale; generic tabular benchmarks do not establish spellF1 gain | Most immediately reusable new-to-this-audit pretrained classifier lead, feasibility only |
| PathCRF, KDD 2026 | MPL-2.0 code and five checkpoint variants listed in public tree | Infers player possession paths from player trajectories without ball coordinates | Supplied wrapper requires known live episodes and complete selected player features; checkpoint split overlaps this project's evaluation corpus | Strongest auditable lead, but existing weights are unsuitable for an independent comparison |
| TranSPORTmer, ACCV 2024 | Original paper; MPL-2.0 adaptation in PathCRF | Masked socio-temporal attention, imputation and semantic states in original paper | Original licensed runnable model/checkpoints not verified; adaptation is not the original four-state model and has no matching published checkpoint in inspected tree | Best architectural lead for masked player interactions, with benefit unmeasured |
| BallRadar, KDD 2023 | Public training implementation | Possessor classifier followed by ball reconstruction | Root project licence and downloadable pretrained weights not established in inspected tree | Lower priority until permission and checkpoint provenance are established |
| CropDrop / masked multimodal pre-training, WACV 2026 | Research paper | Fuses player positions, types and local image crops | Public runnable licensed code/weights not verified; proprietary data excludes out-of-play sequences | Literature context, not an available replacement |

Primary references: [PathCRF paper](https://arxiv.org/html/2602.12080v2), [PathCRF repository](https://github.com/hyunsungkim-ds/pathcrf), [TranSPORTmer paper](https://arxiv.org/html/2410.17785v2), [BallRadar repository](https://github.com/hyunsungkim-ds/ballradar), [CropDrop paper](https://arxiv.org/html/2512.19528v1). Reported event F1, possessor accuracy, state accuracy and ball-position error are different metrics from our unchanged H/A/D spell scorer. None of these results establishes a gain against our CatBoost parent.

### Additional tabular lead, not a new soccer release

[TabICLv2 official repository](https://github.com/soda-inria/tabicl) and [model card](https://huggingface.co/jingang/TabICL) establish public code/weights, BSD-3-Clause licensing and a classification interface. The authors report broad tabular benchmark gains over tuned CatBoost; those are author-reported results on other tasks, not possession or spellF1 evidence. Large contexts favor GPU execution/offloading, while this project requires CPU. Checkpoint identity, local memory/time, fold-only conditioning, missing values, fixed seeds, internal ensembles/temperature and byte reproducibility would have to be locked before any comparison. No weights were downloaded or run. The February checkpoint and October 27 repository maintenance activity are not evidence of an October soccer model release.

TabPFN was also checked through its [official repository](https://github.com/PriorLabs/TabPFN). Local execution exists, but default CPU context limits and separate model usage terms make it less straightforward for this CPU, many-frame project. Code licence and weight licence are separate. Hosted inference is excluded by project rules. No conclusion about relative possession accuracy follows from this feasibility ranking.

## Critical checkpoint finding

PathCRF revision `1b7c6f85a6b78c92e4543fde72ca2b86a933f997` publishes `saved/140/args.json` with Sportec, LOMOCV and fold index 6. Its current training code sorts filenames, uses index 6 for test and index 5 for validation, and excludes both from fitting. With the canonical seven filenames listed in its public tree, this implies fitting on our five development matches, validation on sealed J03WQQ and test on sealed J03WR9. This is conditional on that directory being the actual training input: an exact contemporaneous checkpoint training manifest and hashes were not established. Do not claim either sealed match was fitted; do not claim the checkpoint is uncontaminated. Metadata and filenames only were inspected, with no sealed observations or labels opened and no weights loaded.

## What could address the actual failure

Inference, not an experimental result: a model that retains masked per-player spatial context is more directly aimed at long missing-ball intervals than another classifier over the same nine columns. In `src/possession/core.py`, missing ball coordinates remove both nearest distances, their margin, speed and edge distance; the nearest-distance observation indicators also become zero. A generic tabular replacement cannot recreate the discarded player configuration from these columns. Temporal context may help, but the one fixed GRU blend already failed its gate; that result does not test all spatial attention models.

A future explicitly authorized track has two distinct options: a lower-integration TabICLv2 feasibility check over the unchanged nine columns, or a larger masked spatial-model implementation. The latter first needs a label-free player-coverage and identity-continuity contract, an H/A/D output that does not use true live segmentation, and an overlap-free training/checkpoint manifest. Either performance comparison needs its own committed protocol and an explicit amendment to the completed bounded research budget; it is not a routine implementation of this audit. No expected metric gain or training cost has been measured. Preserve existing splits, strengthened gate, stop rule, November 13 freeze and November 14-16 delivery period.

## Evidence fingerprints

- `open-models-2026-11-08-engine.txt` SHA256 `be29847cf62c28630f63a5c6cb0669e4e48c3c4578074df79203d27b5eb0499b`
- `open-models-2026-11-08-engine.log` SHA256 `4857be16a5e70a9289547a07c9ce507f376d3aa647ff96de156786c1a8049894`
- `open-model-primary-audit-2026-11-08.md` SHA256 `89f35fb99394088a12a0a5465064d106d7efdee6d54f95dbe76ba00e2752cf90`



# Research archive 10 - possession-benchmark-audit-2026-11-09

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/possession-benchmark-audit-2026-11-09.md

# Possession benchmark audit  -  2026-11-09

## Question and method

Can published tracking-based soccer models justify predicting an increase from the selected model's clean development spellF1 of .5177 to .8, and which approach deserves further investigation? Searched primary papers, author/institutional full texts and official repositories for possession estimation, temporal convolutions, TranSPORTmer, PathCRF and masked multimodal learning. Public sources only; no competition or sealed assets read, and no model executed. This is a targeted technology assessment, not a systematic review or new performance evidence.

**Verdict: no verified study reports this project's official H/A/D spellF1 under the same observation conditions and split. No defensible numerical gain forecast follows from the literature.** Accuracy, event F1 and spellF1 must not be interchanged.

## Evidence table

### 1. PathCRF  -  relevant structured player-interaction design, not a .7569 spellF1 benchmark

[Primary paper, KDD 2026](https://arxiv.org/html/2602.12080v1). Seven Sportec Open DFL matches, split 5/1/1; test contains 1,831 events. Player-only inference uses 10-second windows at 5Hz, then upsamples to25Hz. Training and inference are restricted to known in-play segments. Labels are synchronized/refined using ball trajectories and events.

Dynamic masked CRF achieves event F1 .7569 versus .6534 independent non-CRF and .7314 constrained Viterbi with the same backbone. Event correctness requires matching event type and acting player within1second after sequence alignment. Edge accuracy is .6964. These are not team-spell IoU scores. One held-out test match provides weak evidence for broad cross-provider generalization; the study does not solve independent dead/live detection in full matches.

[Official repository](https://github.com/hyunsungkim-ds/pathcrf) supplies code and trained checkpoints; [root licence](https://raw.githubusercontent.com/hyunsungkim-ds/pathcrf/main/LICENSE) is MPL2.0. Existing local metadata audit identifies possible checkpoint/development and sealed-validation overlap; exact checkpoint training hashes remain unverified. Do not use public weights as an independent comparison. A clean scratch implementation with declared training provenance would be needed. CPU/Mac training cost and deterministic full-match integration are unmeasured.

### 2. TranSPORTmer  -  social/temporal masking is relevant; headline accuracy is not the target

[Primary ACCV2024 paper](https://arxiv.org/html/2410.17785v2). Soccer experiments use283 LaLiga2022-23 matches, disjoint match splits,9.6second sequences at6.25Hz:82,954/7,500/6,258 train/validation/test sequences. Labels are pass, possession, uncontrolled and out-of-play, not team H/A/D.

The approximately90% state-accuracy headline concerns tasks where the ball is visible; authors explicitly identify ball visibility as a principal reason. Separate ball inference/imputation experiments must not be conflated with that result. This paper motivates masked player-interaction representations but does not establish .8 team-spellF1 or domain transfer. Original runnable licensed checkpoints were not established by this audit or the prior repository audit. The paper's licence does not license unavailable code/weights. PathCRF's adaptation is not evidence of an original turnkey release.

### 3. CropDrop multimodal model  -  extra visual information helps a different benchmark

[Primary WACV2026 paper](https://arxiv.org/html/2512.19528v1). Proprietary283-match2022-23 top-league dataset, disjoint matches,43,397/3,968/3,347 sequence splits. Inputs combine player trajectories, types and player image crops, with no ball positions at inference. All out-of-play-containing sequences are excluded.

Best reported state accuracy is .8585 and possessor accuracy .8956; these are frame accuracies, not full-match H/A/D spellF1. Without masking, full modalities reach .8767 possessor accuracy versus .8366 trajectories+types; the ablation supports additional visual evidence on that dataset, not a transferable gain estimate. No usable licensed public checkpoint/training corpus was verified. Reconstructing the multimodal training pipeline is a substantial effort, not an available local model switch. Its omitted dead-ball regime is a major applicability limitation here.

### 4. Temporal convolution + self-attention  -  closest label formulation, still not comparable spellF1

Borghesi, Costa, Morra & Lamberti,2023, [publisher](https://doi.org/10.1016/j.eswa.2023.119780), [institutional full text](https://iris.polito.it/retrieve/d9aa6bfd-b26e-44cd-bf9e-6004e676211a/1-s2.0-S0957417423002816-main.pdf). Confidential35-match source at approximately16Hz. Main model selection uses eight matches with least live-ball missingness, split4/2/2 with sampled100k/5k/5k training/validation/test windows. Additional ablations evaluate20matches.

Uses per-object temporal embeddings with permutation-invariant aggregation;64frame windows predict frame48, incorporating future context. Inputs include positions, velocities, roles, team identity and missingness. Ball positions are Akima-interpolated. Reported possession accuracy .862 and dead/alive accuracy .892 are separate classification tasks; possession comparison excludes inactive samples. Main global model-selection accuracy is .8639, while extended20match mean global accuracy is .8159. These differing evaluation populations matter.

This is the closest three-state formulation among reviewed models, but its selected low-missingness games, sampled windows, interpolation and accuracy metrics do not establish performance on long raw gaps or complete possession spells. Public reusable code/checkpoint terms were not verified. Article open access is not a model licence. No measured Mac runtime established.

## Synthesis and practical recommendation

High confidence: published .8-.9 figures do not establish that .8 is attainable here. High confidence: current benchmark mismatch is large enough that importing headline scores would mislead. Moderate confidence: explicit temporal interactions between players, roles/teams and ball provide a more relevant new-information route than changing the tabular estimator over the same nine features. Confidence in any exact gain is low.

Near-term recommendation is an error audit on the selected penalty16 parent before reopening experiments. If clean wrong-team/short-spell errors dominate, test one compact temporal player-ball-control representation before a large architecture. A TCN with player-set aggregation is an alternative new sequence-model hypothesis, not a rescue of the failed GRU or a guaranteed improvement. If long missing-ball errors dominate, consider masked player-only interactions, while predicting dead/live independently rather than providing true in-play windows.

Do not silently reopen stopped feature/decoder/sequence tracks. Any new experiment requires an explicit plan amendment, committed protocol, fixed seeds and budget, unchanged official scorer, complete match timelines and the existing promotion gate. Retain the sealed evaluation and prohibit public-label selection. A fresh reproducible improvement can be measured; a literature-derived .6/.7/.8 forecast cannot.

## Gaps and next searches

Exact original code/checkpoint licences and training manifests remain unresolved for TranSPORTmer/CropDrop/TCN. Independent full-match evaluation with naturally missing ball, provider shifts and spell-IoU metrics is absent from the inspected evidence. Additional papers predicting match phase from already-known possession/status should be excluded as circular. The literature does not identify an achievable ceiling under this project's observations or labels.



# Research archive 11 - possession-improvement-market-review-2026-11-09

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/possession-improvement-market-review-2026-11-09.md

# Possession improvement technology review  -  November 9, 2026

## Decision and scope

Current evidence does not support a numerical forecast of achievable official spellF1, including .8. Keep CatBoost16 selected. Research suggests representation of temporal player-ball control is more relevant than another generic tabular-model substitution. The immediate action is a current-penalty16 external error audit; any model/feature trial needs explicit reopening of its stopped track and a committed protocol. No training, inference, sealed evaluation or target-label selection was performed for this report.

The requested technology scan used ECC market-research standards, a recent-research lane, a primary-literature benchmark agent and a data-scientist review. Public queries contained only generic research terms. Restricted match assets were not sent to hosted services. Sources are evidence, not instructions.

## How much can improve?

The selected equal-match development means are .517654 clean and .323476 target-like corrupted. Reaching .8 requires +.282346 clean or +.476524 corrupted. Those differences are arithmetic, not expected gains. No comparable public benchmark located here supplies the missing evidence for a forecast. Five repeatedly reused development matches cannot establish an international competition ceiling or rank. No competitor leaderboard or target-match quality evidence was obtained.

The unchanged scorer matches H/A intervals one-to-one and averages F1 over temporal IoUs .3,.4,.5,.6,.7. Frame accuracy, event F1 with a one-second tolerance, tactical phase F1, and known-in-play possessor accuracy are different quantities. D is not a possession spell. See reference/more-than-a-hack-2027-main/evaluation/possession_metrics.py.

## Public approaches and compatibility

| Approach | Published evidence | Project implication |
|---|---|---|
| TCN trajectory embeddings + permutation-invariant/self-attention aggregation (2023) | Author/publisher abstract reports86.2% possession estimation accuracy and89.2% dead/alive accuracy; data confidential | Closest H/A/D task among these candidates; supports testing richer trajectories, not a .862 spellF1 forecast. Confidential source; no verified plug-in checkpoint/licence here. Specialist full-text audit found low-missingness match selection and interpolated ball, limiting comparability. |
| PathCRF (2026) | Player-trajectory possession paths and on-ball event detection; benchmark agent audits event-type/actor/timing matching | Strong missing-ball conceptual fit; known-live input and existing checkpoint/split overlap make direct use unsuitable as independent H/A/D proof. |
| TranSPORTmer (2024) | Joint trajectory/state inference, four states rather than H/A/D; proprietary large-match training regime | Architecture inspiration; no comparable score or verified independent turnkey checkpoint for this project. |
| CropDrop multimodal scene analysis (WACV2026) | Player visual crops + trajectories with modality masking | Introduces new visual evidence, but data/weights and evaluation regime differ; high integration and data-alignment cost beforeNov13. Not a cheap next test. |
| Temporal graph attention in-possession phase model (June2026) | Intention IoT-D F1 .79 after processing; seven matches, stable possessions at least3s | It segments tactical phases within possession, uses possession/event context, not H/A/D ownership inference. Exclude its .79 as a target benchmark. |
| GNN-LSTM match-phase classification (October8,2026) |203matches, seven tactical phases, authors report baseline gap4.6% macroF1; possession/status are inputs | Not an alternative possession predictor without removing unavailable inputs and retraining. October8 is outside strictOct10-Nov9 freshness window, despite search engine calling it recent. |

Primary sources: [TCN publisher](https://www.sciencedirect.com/science/article/pii/S0957417423002816), [TCN institutional manuscript](https://iris.polito.it/retrieve/d9aa6bfd-b26e-44cd-bf9e-6004e676211a/1-s2.0-S0957417423002816-main.pdf), [PathCRF paper](https://arxiv.org/abs/2602.12080), [PathCRF code](https://github.com/hyunsungkim-ds/pathcrf), [TranSPORTmer](https://arxiv.org/abs/2410.17785), [CropDrop primary PDF](https://openaccess.thecvf.com/content/WACV2026/papers/Peral_Multi-Modal_Soccer_Scene_Analysis_with_Masked_Pre-Training_WACV_2026_paper.pdf), [T-GAN](https://arxiv.org/html/2606.09289v1), [GNN-LSTM](https://arxiv.org/html/2610.11571v1). Root publisher/institution landing requests forTCN returned403; benchmark agent subsequently accessed the institutional full text. Its review documents the35-match confidential source,8-match main selection with4/2/2split, sampled windows, ball interpolation and .8159 mean global accuracy in an extended20-match evaluation. None is official spellF1. See companion benchmark audit.

## Local evidence that narrows the choice

See docs/improvement-evidence-review-2026-11-09.md. Core inputs lose distance/margin/speed/edge information when ball is absent. A compact trajectory TCN would add per-player temporal observations and team identity rather than merely replacing the classifier over the same nine scalar columns. Current parent predictsD on99.9655% of corrupted missing-ball frames, live recall .0638% (pooled diagnostic rates, not equal-match scores). PFF training moved live recall but worsened spell quality. Rolling whole-pitch aggregates, gap augmentation, small9-feature GRU, settings/decoder trials and10k/30kTabICL did not pass their gates. Thus neither more rows, larger generic emissions nor coarse geometry alone has demonstrated a solution.

Correction to earlier discussion: label-X decoder resets are a general caveat, not a discovered source of current score loss. Reviewed completed scored cohorts have full known-label coverage; prior GRU half-only/legacy parent scores match. No label-transition inference reset defect was found in the inspected paths.

## Ranked next steps, conditional rather than approved protocols

1. Refresh penalty16 error taxonomy and support masks with fixed diagnostic definitions; no new selection. Old oracle repair gains overlap and are not an achievable additive bound. Quantify short-spell, wrong-team, dead/live and boundary losses by gap length. This is the decision input.
2. If ownership handovers dominate, one fixed temporal control representation with observed-support masks, retaining CatBoost16. Choose either short history/look-ahead evidence OR relative player-ball motion; do not bundle both. No slot-continuity assumptions without external identity contracts. Reject under unchanged gate if benefit absent. Track reopening and protocol commit required.
3. A raw per-player trajectory TCN/set-pooling model is a more substantial alternative to the failed9-featureGRU, but only after data/identity/visibility feasibility and explicit sequence-track amendment. A new architecture with the same information-poor inputs is not the same intervention. Mac runtime and deterministic output remain unmeasured.
4. A provider-mixture intervention is conditional on a training-only providerxclassxvisibility row audit. Do not choose source weights using PFF16 transfer scores. LargerPFF volume already failed, and label consistency may dominate.

Do not start all candidates. Same five folds/seeds/budget/corruption, primary corrupted median gain>=+.01 plus original gate and reproducibility remain. Stop limits andNov13freeze apply. A development win remains provisional until the one-time sealed comparison. No .6/.7/.8 forecast, no automatic promotion, no publication of data/predictions or external submission.

## Companion evidence

- literature/possession-benchmark-audit-2026-11-09.md: specialist primary-source metric/checkpoint audit.
- literature/recent-possession-2026-11-09.md: recent engine scope/results/coverage limitations.
- docs/improvement-evidence-review-2026-11-09.md: local evidence and inference-boundary review.



# Research archive 12 - possession-social-2026-11-10

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/possession-social-2026-11-10.md

# Public community evidence  -  November10,2026

## Scope and verdict

Research question: what do actual More Than A Hack participants and football-CV practitioners publicly reveal about methods, standards and likely competition? Public sources only. No target/sealed match data, modelling or current competition public-score selection. No outreach or private-group access. This is a small, self-selected community sample, not a census of submissions.

**High confidence:** public recruitment exists and common demo pipelines combine detection/tracking/calibration with simple possession logic. **Low confidence:** what leading current competitors will actually submit or achieve. No inspected post discloses a verified current-competition spellF1 or a winning implementation. Do not attribute posts to this user or infer that multiple crossposts represent multiple teams.

## Observed posts and comments

- [r/FootballDataAnalysis recruitment](https://www.reddit.com/r/FootballDataAnalysis/comments/1xaqrrr/title_recruiting_football_enthusiasts_for_the_fc/): engine dates post October20,2026,4upvotes/3comments at fetch. A comment by u/OddsRelay identifies the usual proximity baseline and warns that "it falls apart on aerial balls and scrambles." It recommends settling treatment of contested frames. This is useful practitioner opinion, not measured benchmark evidence or a confirmed participant solution. [Exact comment permalink](https://www.reddit.com/r/FootballDataAnalysis/comments/1xaqrrr/comment/phwxz0p/).
- [r/computervision recruitment](https://www.reddit.com/r/computervision/comments/1xaqmra/recruiting_football_enthusiasts_for_the_fc/): describes intended serious experimentation/documentation and seeks a mixed team, but gives no model, score or implementation. Cached relative dates vary across rendered pages; no exact publication date claimed from that rendering. It is not evidence that this team has a stronger solution.
- [r/hackathon teammate search](https://www.reddit.com/r/hackathon/comments/1xezly3/looking_for_1_teammate_more_than_a_hack_2027/): says the team is predicting possession from tracking data and seeks Python/data/statistics/ML-evaluation skills. No algorithm, training protocol or score disclosed. Rendered as16daysago at fetch; exact date not independently established.
- [Seven AI Components Analyzing Football Video](https://www.reddit.com/r/computervision/comments/1wldmdq/seven_ai_components_analyzing_football_video/): author describes detector, ball tracking, identity persistence, calibration, pose, jersey recognition and tactical visualization. In an [author comment](https://www.reddit.com/r/computervision/comments/1wldmdq/comment/paxz7k0/), the author says they combine detections with "temporal tracking/smoothing" because the ball is small, fast and occluded. Other comments list PyTorch/Ultralytics, OpenCV, ByteTrack/DeepSORT, EasyOCR and TensorRT/CUDA. These are self-reported system components; no possession interval evaluation, verified winning submission or project metric is given. Rendering varies1-2monthsago: treat as older contextual evidence, not definitely within fresh window. CUDA/TensorRT specifics do not imply Mac compatibility.

The technical implication is modest: domain conventions, aerial/contested control and robust tracking matter; model names alone do not demonstrate possession quality. Generic public CV demos often solve upstream tracking that this challenge already provides. Public enthusiasm and polished overlays cannot be converted into expected spellF1.

## Reddit/X collection and limits

Installed last30days3.31.0 engine executed under validatedPython3.13 with explicit named-entity query plan and as-ofNovember10, windowOctober11-November10. Runtime62.7seconds. Passed plan covered competition and possession-method terms, four resolved subreddits and available sources. Quickmode internally reduced actual collection to primaryquery/Reddit+HN. Do not claim a completed YouTube/GitHub scan from the plan alone.

DirectReddit site/global/subreddit requests returned403. ArcticShift fallback retrieved40posts,36removed as off-topic, then3of4removed by relevance floor;1Reddit recruitment thread retained. HN4stories retained in overall engine output, but no qualifying technical competitor-method claim is drawn from them. A separate direct publicRedditJSON attempt for post timestamps also returned403; no bypass/repeated retries. Host-web rendering supplied the linked direct-thread/comment supplements above.

**X/Twitter:** engine diagnostic found no authenticated Xbackend. Browser cookies were not read and no login initiated. Two X-domain-restricted host searches for competition and soccer-possession terms returned no indexed results. Therefore this report does **not** claim an actual Xtimeline scrape or that Xis quiet. Optional source omitted: X/Twitter was not enabled; research continued with the available sources. The third-party TwStalker profile search result is excluded as insufficient original-post evidence.

Source availability was checked via diagnostic and cacheddoctor; configuredGitHub credentials meant setup was unnecessary despite absentglobalsetupmarker. No keys/cookies printed or changed. No paid source enabled.

## Decision and remaining uncertainty

No social source justifies changing production, assuming competitors have0.8spellF1, or claiming no sophisticated competitor exists. The plausible method families in the main technology report remain hypotheses informed primarily by published work, not insider knowledge. To strengthen competitor knowledge, inspect released official finalist repositories/technical reports after they are public; do not treat recruitment posts as submissions. No request to contact participants or obtain confidential materials is implied.

Evidence artifacts: possession-social-2026-11-10-engine.log and .txt; rawengineMarkdown under possession-social-engine-2026-11-10/. Root will commit this report and log only, retaining noisy raw outputs locally. No experiment ran.



# Research archive 13 - recent-methods-2026-11-06

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/recent-methods-2026-11-06.md

# Method review, 2026-11-06

Requested window: 2026-10-07 through 2026-11-06. Executed last30days v3.31.0 with a two-query host plan, targeted computervision/sportsanalytics/FootballDataAnalysis communities, and GitHub/HN/YouTube/Reddit/Polymarket sources. Output: last30days-engine-output.txt; diagnostics: last30days-engine-runlog.txt. Engine returned 20 items, but inspected ranked matches primarily concern simulations or match-result prediction. These do not support a possession-model recommendation. X was not enabled; Polymarket was unreachable; Reddit site search was blocked but a listing supplement returned evidence. Coverage is incomplete, not proof no new methods exist.

## Decision

Retain CatBoost plus H/A/D temporal decoding as the first main learned candidate, not a fallback and not a demonstrated winner. Do not switch to PathCRF solely because pretrained weights exist. Before any PathCRF run, preregister an adapter feasibility experiment addressing persistent-player identities, missingness, known-live-episode dependency and independent validation provenance.

## PathCRF (older useful lead, February 12 / revised June 1, 2026)

Primary paper: https://arxiv.org/html/2602.12080v2
Official repository: https://github.com/hyunsungkim-ds/pathcrf

Ball-free player-trajectory model with dynamic structured decoding. Repository supplies five pretrained variants. Paper restricts training and inference to known in-play episodes and downsamples 25 to 5 FPS. It does not establish a standalone H/A/D predictor for this task. Its event F1 is not our spellF1.

Public-code inspection by the research subagent (not executed):
- https://raw.githubusercontent.com/hyunsungkim-ds/pathcrf/main/inference.py : missing selected-player features can return no prediction; node count padding can truncate excess nodes. Unlabelled inference requires evaluate=False.
- https://raw.githubusercontent.com/hyunsungkim-ds/pathcrf/main/datatools/utils.py : phases depend on player entry/exit and ball_state alive. Our changing tracklets require an adapter; assigning slots directly to persistent players is unjustified.
- https://raw.githubusercontent.com/hyunsungkim-ds/pathcrf/main/dataset.py : team/goalkeeper indicators, xy, velocity, speed and acceleration; artificial boundary nodes.
- https://raw.githubusercontent.com/hyunsungkim-ds/pathcrf/main/saved/140/args.json and https://raw.githubusercontent.com/hyunsungkim-ds/pathcrf/main/train.py : LOMOCV fold 6 and sorted-file indexing imply five training files, prior file validation, final test for the canonical seven-file collection. Exact identities/checkpoint hashes not verified. Do not score pretrained weights on all seven Sportec matches and call it independent testing.

These compatibility concerns are code/paper evidence, not a model experiment. No checkpoints downloaded, loaded or run.

## New in-window GNN-LSTM paper (October 8, 2026)

Renner et al., Automated Detection of Match Phases in Football from Spatio-Temporal Tracking Data Using Graph Neural Networks: https://arxiv.org/abs/2610.11571

Seven-class tactical-phase classification. Abstract explicitly includes possession and ball-status indicators as inputs. Its reported superiority over aggregated-feature models concerns a different task with inputs we are trying to infer. Not evidence for replacing the possession pipeline. No implementation verified or executed.

## Other discovery leads, not promoted

- Multi-Modal Soccer Scene Analysis with Masked Pre-Training: https://arxiv.org/abs/2512.19528 (December 2025). Different visual/trajectory requirements; runnable checkpoint not verified.
- ELASTIC: https://arxiv.org/abs/2608.30227 and https://github.com/hyunsungkim-ds/elastic (August 2026). Alignment aid, not a possession replacement.
- TOTNet: https://arxiv.org/abs/2508.09650 and https://github.com/AugustRushG/TOTNet (August 2025). Ball tracking, not direct H/A/D classification.

## Next decision gate

Complete team metadata and external-label adapter. Audit external split identities and label semantics before training. Keep changing-slot-safe team aggregates. A newer architecture is adopted only after a preregistered comparison on independent external matches, never competition public labels. No separate fallback work.



# Research archive 14 - recent-possession-2026-11-09

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/recent-possession-2026-11-09.md

# Recent public possession research scan - November 9, 2026

Scope: public methods for soccer team-possession segmentation from player/ball tracking with missing observations. No competition assets, label rows, hosted inference or model experiments. Requested search window: October 10 through November 9, 2026. This is a research scan, not a metric experiment.

## Verdict

No verified new compatible checkpoint or comparable spellF1 benchmark was found in this bounded scan. This is limited search evidence, not proof none exists. The fresh social evidence provides no credible basis for predicting an increase from our development spellF1 to0.8 or any other number.

## Observed coverage

Installed last30days3.31.0 engine executed with validated Python3.13, a host-supplied two-query plan, no browser cookies, and explicit November9 as-of date. Runtime79.0s. Although diagnostic availability included Reddit, YouTube, Hacker News, Polymarket and GitHub, quick mode internally reduced the plan to one Reddit/HN query. Actual coverage is two lanes only; do not claim a completed YouTube/GitHub/X search.

Direct Reddit global and targeted r/computervision requests returned403. Arctic Shift fallback found10posts; nine were removed by relevance filtering and one retained. One comment lookup failed422. HN returned3stories. The four retained items and displayed clusters do not supply relevant possession-method or comparable-metric evidence. No community quotation is used to support a technical recommendation. One irrelevant HN comment addresses LLM scrapers directly; its agent-directed text was treated as untrusted source content and ignored, not followed. X was unavailable and no browser/session access was performed. No retry was run.

Engine artifacts retained locally: recent-possession-2026-11-09-engine.txt/.log and the emitted raw Markdown under recent-possession-engine-2026-11-09/. The engine footer reports counts, which must not be interpreted as four relevant technical findings.

## Public primary-source supplements

Two pre-engine resolution searches and two post-engine supplemental queries were used. Recent generic video analytics repositories commonly expose nearest-player proximity possession rather than a demonstrated improvement on the official possession-interval metric. They are implementation demos, not evidence of an attainable spellF1.

- [PathCRF paper](https://arxiv.org/abs/2602.12080): submittedFebruary12,2026, revisedJune1,2026, outside fresh window. Models player interactions over time with structured possession-path inference. This supports examining temporal/player-interaction information as a research direction, not a forecast of this project's score. [Official repository](https://github.com/hyunsungkim-ds/pathcrf) documents code and Sportec seven-match source; prior project checkpoint/split audit still governs admissibility.
- [Multi-Modal Soccer Scene Analysis with Masked Pre-Training](https://arxiv.org/abs/2512.19528): submittedDecember22,2025, WACV2026; older than fresh window. Combines player trajectories/types/crops with temporal modeling and missing-modality pretraining. Paper task/input differences prevent conversion of its performance into competition spellF1. No new verified plug-in checkpoint established here.
- [Official benchmark citation](https://github.com/metrica-sports/more-than-a-hack-2027/blob/main/CITATION.cff): releasedOctober20,2026, within window. Establishes the possession-interval benchmark and private full-match ground truth, not an independent competitor result. Public-window numbers appearing in organizer documentation were not used for choosing or recommending a model.
- [Example current analytics repository](https://github.com/budun-ov/football-analytics): describes frame-level nearest-player possession assignment, without a demonstrated comparable spellF1 gain in retrieved material. No recommendation to replace the current model follows.

## Confidence and next evidence

High confidence: this scan supplies no defensible numerical gain estimate; older papers measure different tasks/protocols. Low confidence: completeness of fresh-release coverage because actual social coverage was narrow/degraded. Recommendation strength: no model adoption from this lane. The next useful evidence is the current penalty16 error taxonomy and strict metric/task comparability audit, followed by at most one preregistered intervention if separately authorized. Production and stopped research tracks remain unchanged.



# Research archive 15 - survey

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/survey.md

# Research source index

- [CatBoost missing-value processing](catboost.md): Numerical NaNs are supported with configurable handling. This removes a preprocessing obstacle but does not prove possession accuracy.
- [An integrated dataset of spatiotemporal and event data in elite soccer](idsse.md): Official repository confirms seven matches, tracking/events, and CC-BY attribution. Label adapter still unexecuted.
- [Ball Trajectory Inference from Multi-Agent Sports Contexts Using Set Transformer and Hierarchical Bi-LSTM](kim2023.md): Player-context inference uses intermediate possession prediction. Relevant to missing ball; deferred because coordinate reconstruction is not required for the output.
- [Using Temporal Convolutional Networks to estimate ball possession in soccer games](borghesi2023.md): Prior audit verified author abstract: H/A/D tracking task; reported frame accuracy does not measure this competition spellF1. Full reproduction not performed.
- [Automatic event detection in football using tracking data](vidalcodina2022.md): Prior audit verified primary record; possession and restart logic motivate interpretable features. No measured transfer result.

Gap: robust possession boundaries under non-random missingness and provider label differences; no current project experiment resolves it.



# Research archive 16 - tcn-improvement-refresh-2026-11-10

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/tcn-improvement-refresh-2026-11-10.md

# TCN improvement refresh  -  November 10, 2026

## Question, scope and decision

Which published ideas justify one feasible change to the existing team-pooled trajectory TCN, given possession-spell/boundary errors? Read project journal/state/findings, previous benchmark audit and current model source; searched primary literature for permutation-invariant interaction encoding and boundary-sensitive temporal action segmentation. Public papers/author repositories only. No private arrays, match observations, target labels or sealed assets read; no experiment executed. This is a targeted technology review, not a systematic review or evidence of a new measured project gain.

**Decision:** if the current-parent audit confirms wrong-team/contested-control errors, prefer one explicit masked player-ball relation bundle with the current TCN, budget and decoder held fixed. Do not simultaneously add attention, longer context and new losses. If errors instead show predominantly fragmented spells with otherwise correct ownership, a boundary-sensitive learning change is a separate candidate. Current eligible parent remains the gap-augmented fixed blend under the unchanged robustness gate; best-clean standalone TCN is not automatically the selection parent. No literature permits forecasting .7/.8 spellF1.

## Evidence by mechanism

### Football-specific temporal/set aggregation  -  moderate relevance, weak score transportability

[Borghesi et al., 2023, ESWA](https://doi.org/10.1016/j.eswa.2023.119780), [institutional paper](https://iris.polito.it/retrieve/d9aa6bfd-b26e-44cd-bf9e-6004e676211a/1-s2.0-S0957417423002816-main.pdf): independent temporal object embeddings plus permutation-invariant sum/self-attention/convolution aggregation. Prior full-text audit records a confidential 35-match source, main 8-match selection with low live-ball missingness, 4/2/2 match split and sampled windows, plus 20-match extension. Three-state formulation is close, but ball interpolation and accuracy metrics differ from full-match raw-gap spellF1. Supports testing interactions, not a transferable effect size. Code/weights licence and public checkpoint remain unverified; do not treat open-access article as permission to reuse unavailable artifacts.

[PathCRF, KDD2026 primary paper](https://arxiv.org/html/2602.12080v1): seven Sportec matches, 5/1/1 split, known-live input segments. Directed player-pair edge embeddings feed emissions and dynamic structured transitions. Event F1 .7569 versus .6534 independent edge classification is evidence that relational and sequential constraints help that event task. It is not H/A/D possession-spellF1; a single test match, different supervision and known-play restriction limit transfer. Existing public checkpoint overlap issues remain. Borrow the interaction principle, not pretrained weights or its score as an expected gain. The study does not isolate a player-ball relative feature as the causal improvement.

### Set interactions and pooling  -  strong mathematical fit, indirect task evidence

[Lee et al., ICML2019 Set Transformer](https://proceedings.mlr.press/v97/lee19d.html): attention-based encoders/decoders explicitly model interactions in an unordered set. Experiments span synthetic set functions, few-shot classification and 3D point-cloud recognition; there are no soccer possession-spell tests. The paper motivates an order-invariant alternative to pooling, but neither task sample sizes nor reported generic scores establish a football effect estimate. [Author code](https://github.com/juho-lee/set_transformer), [actual root licence](https://raw.githubusercontent.com/juho-lee/set_transformer/master/LICENSE), checked November10: MIT. No code downloaded or adopted here.

A full Set Transformer adds pairwise computation and extra parameters. Relative observation channels in a shared object encoder are the smaller first intervention; attention pooling can be a later separate hypothesis if uniform averaging still loses local control evidence.

### Boundary-sensitive action segmentation  -  credible cross-domain mechanism, conditional applicability

[MS-TCN, CVPR2019 primary paper](https://arxiv.org/html/1903.01945v2): dilated multi-stage temporal convolutions with classification and smoothing losses, tested on 50Salads, GTEA and Breakfast. The ablations support refinement/smoothing against over-segmentation on those daily-activity datasets. Those labels, background conventions and F1 thresholds differ from H/A/D interval matching; no independent football test exists in the paper. More smoothing is not justified if our major error is missed brief possessions or over-merged handovers. **Licence caution:** [official source licence](https://raw.githubusercontent.com/yabufarha/ms-tcn/master/LICENSE) is MIT plus Commons Clause, including a restriction on selling the software; it is not plain permissive MIT. A scratch implementation of an independently described method avoids silently importing that source licence.

[ASRF, Ishikawa et al. primary paper](https://arxiv.org/html/2007.06866v1): separate action and boundary branches refine frame predictions. Evaluation uses 50Salads (50 videos/25 people), GTEA (28 videos/4 people) and Breakfast (>77h/52 people); 5-fold evaluation for Salads and 4-fold for others. Authors demonstrate segmental-F1 gains, but also show a failure where segment-level reassignment selects the wrong class even with good boundaries. This supports a boundary-specific diagnostic, not indiscriminate smoothing. No numeric gain is transferred here; no code licence checked because no adoption is recommended.

[ASFormer, BMVC2021 paper](https://arxiv.org/abs/2110.08568) combines local temporal priors and attention/refinement. It remains cross-domain evidence rather than a better off-the-shelf possession model. [Author licence](https://raw.githubusercontent.com/ChinaYi/ASFormer/main/LICENSE), verified November10: MIT. A full architecture replacement would confound interaction/boundary questions and is not the preferred near-term trial.

## What the current code leaves unresolved

Current object Conv1d sees absolute XY, velocities and visibility, then masked mean pooling separately for home, away and ball. The ball embedding is pooled independently; there is no explicit per-player relative ball XY/motion before pooling. Nonlinear layers can learn some relationships later, so this is not proof the information is mathematically absent. However, compressing players before expressing local relations plausibly makes control identification harder. This is an implementation-based inference, not an ablation result.

The effective receptive field is 17 frames, roughly .68s at25Hz; the 250-frame input window is not a 10-second model receptive field. Extending dilation/context could help handovers, but must be a separate change with halo/half contracts, and will not reveal a ball absent for arbitrarily long periods.

## One-change proposal, conditional on the audit

Append player-ball relative XY and relative velocity, plus separate position-pair and velocity-pair validity flags, to the shared object encoder. Require both objects observed for relative XY; velocity additionally requires consecutive support inside the same half. Set unsupported values to zero only behind explicit validity masks. Never turn missing ball into a fabricated confident relation; original player channels remain available during gaps. Ball/padding slots should not create false self-control features. Shared weights and masked team pooling preserve player-order invariance. Recompute or derive relations from each condition independently, including raw training gaps; no target labels or identity shortcuts.

Hold all other neural, augmentation, blend, CatBoost, decoder and fold/seed/budget settings to the current best eligible parent. Increasing first-layer channels inevitably changes its parameter count; disclose this, rather than claiming an equal-parameter isolation. Do not bundle attention weights or a boundary head into this representation trial. Register source/input hashes/protocol before execution; user runs any hours-long fit. Keep the original quality gate and stopped-track history. Clean-environment/integration validation remains outstanding and cannot be replaced by further development gains.

## Confidence, contradictions and next evidence

High confidence in metric incompatibility, permutation-invariance requirements, receptive-field calculation and verified licence texts. Moderate confidence that explicit relational representation is a relevant mechanism. Low confidence in direction or magnitude of held-out improvement: prior whole-pitch features, temporal-control bundle and short-budget models failed, while later training/augmentation/blending improved different objectives. Five reused development matches introduce selection optimism. No reviewed primary study resolves this project's full-match missing-ball regime or competitive ceiling. Current-parent boundary/error slices are therefore more decision-relevant than another generic model list.



# Research archive 17 - vidalcodina2022

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: literature/vidalcodina2022.md

# Automatic event detection in football using tracking data

Authors: Vidal-Codina, Evans, El Fakir, Billingham. Year: 2022.
Source: https://arxiv.org/abs/2202.00804

Prior audit verified primary record; possession and restart logic motivate interpretable features. No measured transfer result.

Evidence scope: documentation/abstract or earlier audit record, not reproduced experimental results.



# Research archive 18 - improvement-evidence-review-2026-11-09

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: docs/improvement-evidence-review-2026-11-09.md

# Improvement evidence review  -  November 9, 2026

Scope: local aggregate reports, research journal/state and source inspection only. No training, inference, evaluation, private arrays, competition observations, public-label rows or sealed assets were accessed. This document is evidence analysis, not a model protocol or authority to reopen stopped tracks.

## Decision

Keep nine-core unaugmented CatBoost + penalty16 selected. There is no defensible numerical forecast that a new model will raise official spellF1 to .8. The strongest next work is a current-parent, gap-stratified error audit followed, only if warranted and explicitly authorized, by one temporal team-control feature experiment. Do not spend another bounded trial merely scaling TabICL context or sweeping blend weights.

Confidence is high in the rejection of the tested configurations and in the feature information bottleneck described below. Confidence is low in the size of any future gain or in target generalization.

## What the headline score means

The selected .517654 is the equal-match mean clean spellF1 over five IDSSE development matches, evaluated leave-one-match-out. Target-like corrupted mean is .323476. Neither measures the target match or two sealed matches. The official scorer matches H/A possession intervals one-to-one at temporal IoUs .3,.4,.5,.6,.7, then averages F1; D is not a possession spell. Frame accuracy, possession-team accuracy on known-live clips, ball reconstruction accuracy and F1 at a single IoU cannot be treated as this metric.

A .8 target would require a clean absolute gain of .282346, about55% relative to the current score. This arithmetic is a distance to a goal, not an expected effect. On the corrupted task, reaching .8 would require .476524 absolute gain. Published scores cannot determine that feasibility without matched task, input visibility, labels, split and scorer.

The promotion rule is an engineering decision rule, not a significance test: five matches, positive median paired clean/corrupted spell delta, a majority positive, median macro delta at least-.01, plus median corrupted spell gain at least+.01 and correctness/reproducibility checks. Reusing these five matches across many hypotheses creates selection optimism. Frames are temporally dependent; millions of frames do not create millions of independent tests. No new confidence interval or power estimate was computed here.

Source: reference/more-than-a-hack-2027-main/evaluation/possession_metrics.py; experiments/gru-2026-11-08/report.md; research-state.yaml.

## Strongest supported mechanism: lack of control information during gaps

Source inspection of src/possession/core.py and features.py shows the nine columns contain nearest H/A distances, their margin, instantaneous consecutive-observation ball speed, edge distance, three observation indicators and elapsed missing-ball time. When ball XY is missing, distances, margin, speed and edge are unavailable; home/away distance-observed masks also become zero. Thus many missing frames differ principally in gap age. Player motion/geometry and prior owner are not encoded in the CatBoost row. Viterbi can propagate surrounding emissions, but cannot manufacture unobserved team-control evidence.

Aggregate missing-ball results are consistent with this limitation: the parent predicted D on99.9655% of corrupted missing-ball frames, with live recall .0638%. Adding PFF training improved live recall to8.9503% but worsened global scores. This is evidence of poor recovery, not proof that missingness alone causes every error, nor evidence that a specific new feature will fix it. Rates are pooled frame-weighted diagnostics and cannot replace equal-match spell results.

Source: docs/pff-evaluation-review-2026-11-07.md, completed-results addendum.

## What the rejected experiments do and do not imply

| Intervention | Recorded primary/paired evidence | Interpretation |
|---|---|---|
| Rolling whole-pitch feature bundle | Median corrupted spell-.005208; paired-.006600;1/5 improve | The tested2.5s broad aggregates failed; does not test explicit player-ball control history. Feature track was stopped. |
| Gap augmentation + penalty16 | Paired median-.001331;2/5 improve | Corruption exposure alone did not repair this representation at the fixed budget. |
| IDSSE + PFF48 | Median corrupted-.034930; paired-.056268;0/5 improve | This unweighted provider expansion failed. Row volume, visibility, convention and capacity are confounded; "PFF cannot help" is unsupported. |
| Scratch BiGRU hidden16 fixed25% blend | Corrupted median-.007520; paired-.008148;1/5 improve | A small fixed model over the same nine features did not help. It did not test richer player geometry. |
| TabICL10k /30k, one estimator, fixed50/50 blend | Blend primary medians+.001995 /+.001606; both1/5 paired improve | Small corrupted gains fail the full gate and do not justify further blind context-size search. No general conclusion about all TabICL settings. |
| Duration prior | Rejected; estimator includes censored fragments as complete endpoints | The implementation is not evidence against every duration prior, but decoder track has3failures and is closed. |

Sources: experiments/whole-pitch/report.md; experiments/combined16/report.md; docs/pff-evaluation-review-2026-11-07.md; experiments/gru-2026-11-08/report.md; experiments/tabicl-small-2026-11-08/gate.json; experiments/tabicl-medium-2026-11-08/gate.json; docs/review-data-scientist-2026-11-07.md.

## Decoder-reset concern: already narrowed, not a promising score rescue

Legacy scripts call blocks_valid(y, half_blocks), resetting at annotation X gaps; production uses metadata half blocks. That is a real general training/evaluation-serving concern for cohorts with unknown-label gaps. However, the completed evaluation review records known-label fraction1.0 for all scored arrays in the relevant cohort, so these resets do not create a demonstrated difference here. The GRU report explicitly verifies identical parent half-only versus legacy scores. Recent TabICL runners use half blocks for inference. No H/A/D label-transition reset was found in the inspected code paths. Do not present this already-known caveat as a likely explanation for the missing .28 or silently alter legacy scores.

Sources: scripts/review_frozen.py:blocks_valid; scripts/run_core.py; scripts/run_tabicl_medium.py:first_inference/score_initial; docs/pff-evaluation-review-2026-11-07.md:completed-results addendum; experiments/gru-2026-11-08/report.md.

## Next highest-value slice and conditional experiment

First refresh the error taxonomy for current penalty16 emissions/decoder, with no model selection or parameter changes: separate observed versus missing ball, fixed gap-duration bins, wrong-team versus dead/live errors, short-spell recall, and missed/spurious spells and boundaries. Prior detailed diagnostics use penalty8 and oracle repairs overlap; those repairs are counterfactual diagnostics, not additive headroom or achievable upper bounds. Use external development examples only; do not hand-label target video.

If that confirms ownership errors around handovers and gap endpoints dominate, propose one fixed temporal team-control feature bundle, preserving CatBoost/penalty16. A minimal candidate can summarize nearest-team evidence over a preregistered short past/future window with explicit observed-support masks, using no player-slot identity continuity. Relative player-ball motion is another candidate, but must not be bundled with look-ahead/history in the same trial: choose one from the failure slice. Never fill long missing gaps with fabricated confident ownership; unsupported context remains missing. Same folds/seeds/budget/corruption/gate; freezeNovember13. A feature-track amendment and committed protocol must precede execution.

A more-data alternative should first audit actual sampled training row counts by provider x H/A/D x ball visibility and per-match exposure. If confirmed provider dominance is addressed, source balancing would be a distinct one-change training experiment, not a retrospective rewrite of the failed unweighted PFF run. PFF16 stays descriptive transfer data, not a selection leaderboard.

Expected impact direction: temporal control evidence could improve short/hand-over spell correctness and robustness near observed gap endpoints. Magnitude is unknown, and gain may be zero or negative; long gaps without identifiable endpoints may remain ambiguous. The case for it would weaken if current-parent errors are primarily incompatible labels, observation noise or dead/live episodes that no proposed feature distinguishes.

Keep the sealed evaluation untouched untilNovember13. If a future development gain fails there, investigate bugs/transfer rather than tune on the sealed matches. This is the strongest protection against a visually attractive .8 that does not generalize.

## Ranking representation options before the freeze

1. **Light temporal ball-control evidence + existing CatBoost:** first choice after the diagnostic slice. It changes the missing information while retaining the tested classifier/decoder and has a smaller implementation/verification burden. No promised gain or runtime number.
2. **Raw player/ball trajectory temporal convolution with permutation-invariant team set pooling:** a scientifically plausible later architecture if richer geometric evidence is needed. It could learn motion/control rather than being confined to the nine-column bottleneck. However, it introduces player-presence masks, team pooling, temporal context, standardization, training objective and a new model implementation; provider/slot discontinuities and deterministic inference require explicit contracts. It is a substantially larger research intervention beforeNovember13 and should not be treated as an inexpensive follow-on to the failed small GRU. Scratch training on only four matches per fold also leaves generalization uncertain. Rank behind the minimal evidence test, not an immediate parallel architecture search.

The prior GRU result cannot distinguish a weak representation from an inadequate temporal architecture/training budget because both were fixed together. Neither a TCN nor a larger transformer has an identifiable attainable spellF1 from current evidence. In particular, no defensible .6-.8 range or probability of reaching .8 can be supplied.



# Research archive 19 - tcn-learning-review-2026-11-10

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: docs/tcn-learning-review-2026-11-10.md

# TCN learning-diagnostic review  -  November 10, 2026

Scope: review of completed aggregate `experiments/tcn-learning-check-2026-11-10/results.json`, `verdict.json`, the committed diagnostic/trial protocols, source and initial-trial cost records. No arrays, model runs, tests or new scoring were accessed/executed. Production remains nine-core unaugmented CatBoost + penalty16. This review recommends a new bounded training-budget test; it does not reopen or revise the failed200-step trial retroactively.

## Verdict

**A longer fixed training budget is justified as a hypothesis test; a held-out gain is not established. Recommend exactly2,000 Adam updates per fold, with the final update as the only scored checkpoint.** This is a tenfold budget change from200. Change no architecture, features, loss, sampling, learning rate, batch size, corruption, decoder, seed or split. Do not select between1,000/2,000 checkpoints on development scores. A separate committed protocol/amendment must precede execution.

Hypothesis: the200-step candidate did not have enough optimizer exposure to learn the available control signal. Outcome: official held-out clean/corrupted spellF1 and macroF1 on the existing fiveLOMO folds. Decision: retain the new2,000-step candidate only under the unchanged CatBoost-parent promotion gate and required reproducibility. Also report against the rejected200-step TCN as an explanatory comparison; beating that weak model is insufficient for promotion.

## Evidence supporting the test

The fixed training-only10,000-frame segment diagnostic shows:

| Updates | Full-segment CE | Argmax accuracy | Home recall | Decoded training spellF1 |
|---:|---:|---:|---:|---:|
|200|.810039|.6495|0|.054545|
|1,000|.172743|.9374|.8807|.688000|
|2,000|.071580|.9788|.9394|.805556|

At200updates the model predicts noH despiteH being21.46% of this segment. At2,000 it fits all three classes (H/A/D recalls .9394/.9871/.9974), and the full-segment loss falls by about91% from200updates. These are comparable evaluations of the same full segment at preregistered checkpoints, stronger learning evidence than unrelated final minibatch losses from different folds. They demonstrate that the unchanged implementation can learn this small segment rather than being permanently stuck at a trivial class predictor.

The training-only verdict's thresholds were satisfied. **The .805556 is training fit on one segment, not development performance, a ceiling, a target estimate or evidence that .8 will generalize.** AtIoU.5 the decoded model still misses11of41training spells and short-spell recall is.4; good frame fit alone does not solve the spell task.

## Why2,000, and what it does not establish

2,000 is the longest preregistered diagnostic budget at which all basic fitting checks passed, and is a simple fixed10x exposure change rather than a new budget sweep. Each update has8windows x200retained loss frames:200updates yield320,000 loss-frame presentations;2,000 yield3.2million. These overlap and are sampled with replacement, so they are neither unique frames nor independent observations. The full four-match training population is much larger and more heterogeneous than the diagnostic segment;2,000updates is not proved sufficient for convergence there. Its value is to test whether the current gross failure was substantially training-budget limited while keeping other explanations fixed.

The recorded diagnostic took46.5seconds; old per-fold200-step initial fits took5.27-5.66seconds. These support a rough order-of-magnitude expectation of tens of seconds per2,000-step fit on the same machine, **not a measured end-to-end runtime**. Repeated training, full-match inference/scoring and environment verification add costs; do not promise a total from the fit timing alone. Existing user execution policy and any newer explicit scope controls who launches the run.

## Required interpretation and guardrails

- Keep CatBoost16 as the selection reference and all fiveLOMO matches/clean and fixed target-like conditions. Sealed and target labels untouched.
- Require positive median paired clean/corrupted spell delta, majority of matches positive, median macro delta>=-.01, median corrupted spell gain>=+.01, tests and reproducibility. Candidate quality eligibility is not production promotion.
- Report all per-match scores and missing-ball dead/live quality. Longer clean-only training may strengthen missing-ball -> D behavior or overfit person-independent trajectory quirks; representation still has17-frame receptive field and does not acquire long-gap context from extra steps.
- No early stopping or choosing budgets from held-out results. Final2,000-step results only; training loss checkpoints may be recorded as diagnostics, not candidate-selection options.
- If the full trial remains far below parent, close it and investigate model/input limitations rather than automatically extending again. If it improves over200steps but still fails the CatBoost gate, record partial learning success and retain CatBoost.
- Repeatfit/reload/batch exact-CSV checks remain necessary. No change to existing November16 freeze or sealed interpretation rule.

Confidence: high that additional training improves fit on this specific training segment; moderate that200steps was an insufficient learning exposure there; low/unknown about2,000-step held-out spellF1 effect, corrupted improvement or target transfer. Plausible alternative explanations remain memorization, sample/label distribution, limited context and model capacity. Only the controlled fullLOMO comparison can address the relevant decision.



# Research archive 20 - tcn-next-change-review-2026-11-10

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: docs/tcn-next-change-review-2026-11-10.md

# TCN next-change review  -  November 10, 2026

Scope: source and completed aggregate reports only. Read ball.md, research-state.yaml and findings.md; inspected the original TCN/adapter, augmentation trainer and completed gate reports. No raw/prepared match arrays, competition observations, public labels, sealed assets, model inference, training, tests or new scoring were accessed/executed. This is a methodological review, not authority to alter production or an experiment protocol.

## Decision

The strongest source-level representation limitation is **ball-independent mean pooling of a small per-player embedding**, not an established optimizer failure. The model pools eight-dimensional player embeddings separately for H and A, then concatenates a separate ball embedding. It has no explicit ball-conditioned player relation before pooling. This can dilute the small number of players contesting the ball among many off-ball players. A network can in principle approximate some interaction from pooled nonlinear spatial summaries, so this is a plausible information/inductive-bias bottleneck, not a proof that pooling destroyed every useful control signal.

Recommend one conditional experiment: add **masked player-ball relative XY plus an explicit pair-observed indicator** to the shared object encoder, calculated from already encoded inputs. Keep temporal architecture, 20,000-update budget, sampling/seeds, 50% augmentation, 50/50 CatBoost blend and penalty16 fixed. Do not also add relative velocity, attention, a new loss, or longer dilation in this trial. First let the refreshed boundary/error audit establish that visible-ball ownership/handovers or observed gap endpoints are a substantial remaining loss. If long unobserved dead/live episodes dominate, this feature cannot directly distinguish them; the case for this trial is weaker.

## Exact context calculation

The object encoder is Conv1d(k=3,d=1), followed after pooling by temporal k=3 convolutions with dilations1,2,4 and a k=1 head. With stride1:

`R = 1 + (3-1) + (3-1)*(1+2+4) = 17 encoded samples`.

Thus the learned convolutional dependency is ±8 samples, or ±0.32seconds at25Hz; the span between the first/last encoded timestamps is0.64seconds. Counting17sample durations gives0.68seconds. The250-frame/10second input window does not create10seconds of learned context; most of that window provides sampled loss positions or unused halo.

Qualification: input velocities depend on the preceding raw position, so the raw-coordinate support can extend one frame farther into the past (`t-9..t+8`), spanning0.68seconds. Precomputed gap_age summarizes potentially much longer past missingness as one scalar; it is incorrect to say every input is independent of history beyond17frames. It does not provide a learned trajectory of that longer history. The25framehalo safely exceeds the current ±8 neural radius.

A larger receptive field is a valid alternative hypothesis, but should be tested separately. Any dilation change must calculate exact support, avoid input-window/halo inconsistencies, and check boundary padding and batch/chunk equivalence. Increasing only WINDOW without changing the convolution stack does not increase R. Very sparse dilation can introduce support holes, and neither this field nor a modest extension establishes inference through arbitrarily long ball gaps.

## Hypothesis and estimand

Hypothesis: explicit masked relative XY lets the same fixed-budget network identify local control and handovers more efficiently than global player means plus a separate ball embedding. Expected direction, if true: better wrong-team/short-spell or boundary performance where the ball is observed, with potential indirect benefits near gap endpoints. Magnitude is unknown; effect can be zero or negative. It does not create ball information during missing frames.

Decision outcome remains the **official per-match clean and fixed-corrupted spellF1/macroF1** against the current best eligible gap-augmented blend (.592502clean/.428386corrupted). The unaugmented standalone .609882clean TCN may be shown descriptively, but is not the current gate parent. The user has questioned clean regressions without explicitly replacing the agreed promotion gate; do not silently change it or cherry-pick the clean reference to make a result pass.

All five clean scores dropped under augmentation while all five corrupted scores improved. This supports a clean/robustness trade-off under that intervention, not that augmentation broadly failed or that another method will raise both. Preserve both historical candidates.

## Minimal implementation contract for relative XY

- Derive the relation from the existing normalized XY of player and ball at the same frame. Pair validity is player-observed AND ball-observed; no label input.
- Multiply relative XY by that validity and pass the validity as a distinct input. Missing coordinates encoded as0 must never be interpreted as an observed ball at pitch centre.
- Leave original absolute coordinates, velocities and their observation indicator intact. Append relativeXY/pair-valid to the object input only, retaining its output dimension8 and all later layers.
- Shared Conv1d input rises5 -> 8 channels. This necessarily adds72 weights (`3extra * 8outputs * k3`), with unchanged biases/output widths; disclose this modest capacity confound. This is one feature intervention with its required input plumbing, not an identical-parameter test. No additional attention or capacity change.
- Keep padding/half isolation and same clean/augmented input paths. Compute relations separately for every view, so an augmented gap suppresses both the coordinates and pair-valid mask.
- No object-slot identity assumptions beyond the audited adapter. Preserve player permutation equivariance under same-team slot permutation; test relation masking, missing/reappearing observations, ballslot identification, checkpoint reload and exact repeatability.
- Test translation invariance of **the relative feature calculation**, not invariance of the full model that still receives absolute coordinates. Neither full rotation nor attack-direction invariance is guaranteed by the current parent architecture.

## Valid comparison and uncertainty

Commit the feature formula/architecture/source/input hashes and fixed protocol before any execution. Same five LOMO folds, seeds, raw corruption arrays, batch/window sampling, optimizer, final20k checkpoint, CatBoost probabilities, blend and decoder. No held-out labels in features/normalization/calibration, no target/public-label selection, and no sealed access. Keep production untouched pending separate clean-environment/fresh-clone/integration/official-validator checks.

Gate: median paired(clean/corrupted) spell gain>0, majority of five improve, median macro delta>=-.01, median corrupted spell gain>=+.01, contract tests and repeatability. Record per-match clean losses as well as gains. Failure drops the feature and closes this bounded change; do not rescue it by adjusting window, augmentation probability, blend or seed. Long training remains user-run.

Five matches repeatedly reused across many hypotheses provide limited independent evidence. Frames overlap strongly and are not independent samples. The promotion rule is an engineering screen, not a p-value or confidence guarantee. No confidence interval, effect-size distribution or power calculation was newly computed here. The sealed November16 evaluation remains the independent check; future poor sealed scores prompt bug/transfer investigation rather than tuning.

Confidence: high in code-level receptive-field/feature-path facts; moderate that explicit interaction is a useful targeted hypothesis; low in attainable spellF1 gain or target transfer. Findings that could invalidate prioritization: current errors mainly arise from long ball gaps without distinguishable player evidence, label convention mismatch, missing identity/visibility problems, or decoder over-merging rather than observed control ambiguity.

Sources: experiments/tcn-2026-11-10/tcn_candidate.py; scripts/prepare_tcn.py; experiments/tcn-gap-2026-11-10/gap_training.py, report.md and gate.json; experiments/tcn-long-2026-11-10/report.md; research-state.yaml; ball.md. No new performance result is claimed.



# Research archive 21 - review-data-scientist-2026-11-07

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: docs/review-data-scientist-2026-11-07.md

# Independent data-scientist review  -  November 7, 2026

Scope: committed experiment protocols, aggregate JSON results, research state and implementation code only. No restricted target assets, public labels, sealed matches, private prediction arrays or raw PFF records were read. No training, scoring, experiment rerun or production change. This review recomputed decision arithmetic from existing aggregate results; it is not a new performance experiment.

## Decision summary

Keep the current nine-core, unaugmented CatBoost + penalty16 candidate. The strongest supported result is that temporal decoding materially improves these five development matches; the current evidence does not establish target-match accuracy or unbiased provider generalization. Prioritize PFF adapter validation over another model search. Confidence is high in the recent rejection decisions' arithmetic, moderate in same-condition relative development performance, and low in external generalization until provider transfer and the later sealed evaluation exist.

I independently checked all ten match/condition cells in each recent decoder/settings comparison and recomputed paired medians and improvement counts. Rejections agree with stored gates:

| Candidate vs penalty16 | Median paired spellF1 delta | Median corrupted spellF1 delta | Paired matches improving |
|---|---:|---:|---:|
| Gap-age switching | 0.000000 | 0.000000 | 0/5 |
| Separate H/A and D costs | -0.006705 | -0.014535 | 2/5 |
| Learned duration prior | -0.007980 | -0.005646 | 0/5 |
| Nested CatBoost setting policy | -0.000306 | -0.000035 | 1/5 |

Sources: `experiments/extension-2026-11-07/decoder/*-results.json`, `settings/outer-results.json`, and penalty16 rows of `experiments/gap-augmentation/decoder-isolation.json`. Each has exactly one clean and one target-like corrupted cell per match. All 80 nested-search records exclude both outer held-out match and inner validation match from training; inner validation never equals the outer match. No split-membership leakage was found in these records.

## Concrete issues, distinguished from uncertainty

1. **Error-repair gains are not mathematical upper bounds or causal attribution.** `scripts/review_frozen.py:32` calls deterministic class-error repairs "upper bounds." SpellF1 is non-monotone in frame corrections: the committed clean J03WPY dead/live repair gain is negative (about -0.00235). That is possible for a specific counterfactual repair, but not a supremum over permissible repairs that includes doing nothing. Rename the interpretation to "specific label-informed counterfactual repair"; keep gains non-additive and do not infer the uniquely largest causal error source from them. This changes interpretation, not measured candidate scores or promotion decisions.

2. **The rejected duration estimator treats censored spell fragments as complete durations.** `experiments/extension-2026-11-07/decoder/methods.py:19-27` records each maximal known-label run up to a half edge or X boundary as an observed endpoint. Half-terminal runs can be right-censored, and runs starting/ending beside unknown labels can be left/right censored. Treating these as ordinary exits biases hazard estimates; resetting at X also changes the measured duration population. Exact decoder optimization tests do not validate that statistical estimator. The result supports rejection of this implementation, not rejection of all duration priors. Do not reopen the stopped decoder track; document this limitation and require censor-aware estimation if such work is authorized later.

3. **Research-state mirrors lag the executed experiment history.** `research-state.yaml` still reports `total_runs: 6` and `external_performance_runs: 4`, and hypotheses remain broadly pending, despite subsequent augmentation, feature, decoder and settings experiments. This is an auditability defect rather than evidence that model scores are wrong. Reconcile a machine-readable experiment register with the dated journal; preserve historical entries.

## Statistical and evaluation caveats

- Five outer matches are five clustered observations, not hundreds of thousands of independent frame samples. Their training folds overlap. The majority/median gate is a practical engineering decision rule, not a significance test or a confidence guarantee. Do not derive frame-level confidence intervals or treat fold SD as uncertainty on target accuracy.
- Penalty16's historical promotion improved only 3/5 paired matches. Its corrupted median gain over8 was +0.017998; leave-one-match-out sensitivity medians range about +0.01052 to +0.01817. That supports the recorded gate passage but shows how little independent information exists near the new +0.01 threshold. This is descriptive sensitivity, not a new selection criterion and not grounds to change production.
- Nested setting selection correctly excludes each outer match *within this search*. Earlier feature/decoder/model choices already used all five matches, so nesting cannot retroactively make the final architecture an unbiased estimate. The current negative search result is useful restraint, not proof that the current settings are globally optimal.
- One fixed evaluation corruption realization per match makes paired comparisons fair for that realization but leaves corruption-seed sensitivity unknown. Alternating run bootstrap reproduces unconditional gaps approximately; it does not reproduce the association between visibility, stoppages, location or possession transitions. Missing fractions vary materially between matches. Existing masks should stay fixed for the authorized comparisons. Any extra corruption-seed analysis would need separate preregistration and must not become an unannounced new selection set.
- Original-versus-target-like corruption comparisons changed both missingness amount and run structure. Fewer spurious spells together with lower frame macroF1 is consistent with reduced fragmentation and longer wrong intervals; it is not an isolated causal estimate of gap duration.

## PFF admission: highest-value next work

The current block is legitimate: `experiments/pff-intake/coverage-summary.json` certifies annotation presence over delivered records, not correct labels on unique frames. All64 files have non-increasing IDs; only the first-match probe establishes that its anomalies are duplicates rather than backward steps. The probe's401 conflicting payloads are not yet split into coordinate, time and label conflicts. Do not generalize that decomposition to all64.

Before modelling, the adapter should produce an admission manifest for every match with:

- unique `(period, frame)` count and separate identical, coordinate-conflicting, timestamp-conflicting and label-conflicting groups;
- documented resolution precedence, if provider timestamps genuinely establish one; otherwise retain per-field missing/unknown status or fail the contract instead of choosing by eventual score;
- explicit CLK policy and event interval/clock consistency, without silently mixing updated standalone events and embedded tracking annotations;
- 25Hz mapping with source-time provenance, preserved missing observations, half isolation and no invented ownership through unknown intervals;
- retained and excluded frames/spells, coverage near boundaries, and missing-ball rates separately for the locked48/16 groups. Excluding ambiguous boundaries can make evaluated spells easier, so denominators must be visible.

Coordinate ambiguity need not automatically destroy a consistent teacher label: labels and observations should remain separate channels. Conversely, plausible coordinates do not resolve conflicting labels. Keep the hash split unchanged and do not replace failing matches according to performance.

After admission, the highest-value *already authorized* experiment is the fixed train-more comparison on IDSSE5, followed by descriptive frozen IDSSE -> PFF16 and PFF48 -> IDSSE5 transfer. Never tune or select using PFF16 transfer outcomes. Report cross-provider results as provider-label agreement, not automatically equivalent possession truth. If conventions are not equivalent, that may invalidate a transfer interpretation even when the adapter is numerically correct.

## Recommendation and invalidation conditions

Expected benefit direction: trustworthy additional labels could improve robustness and reduce dependence on five-match reuse; gains are unproven and can reverse under label-convention shift. Keep the strengthened gate and production unchanged until contracts and a preregistered comparison pass. Preserve November13 freeze and November14-16 delivery-only window.

What could invalidate the favorable interpretation of the current method: undiscovered train/test overlap, a scorer/data alignment error, provider label semantics that do not match the intended possession rules, or large frozen-transfer/sealed degradation. These should trigger investigation under the existing rules, not tuning against sealed or public scores. No new architecture experiment is the immediate priority.



# Research archive 22 - pff-admission-review-2026-11-07

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: docs/pff-admission-review-2026-11-07.md

# Independent data-science review: PFF admission  -  November 7, 2026

Scope: `AGENTS.md`, project memories, PFF admission protocol, `src/possession/pff.py`, its tests, committed aggregate intake evidence, and user-supplied external PFF specification text/PDF. No target assets, competition public labels, sealed IDSSE files, model training or performance evaluation. Only this review document was edited; no code or commits.

## Decision and hypothesis

**Do not admit the currently reviewed smoothed-ball adapter for the planned train-more/transfer evaluations.** The principal blocker is documented annotation-conditioned feature construction, not duplicated frame IDs.

The intended hypothesis is that adding compatible external tracking/labels improves the unchanged production configuration on the original five development matches. Outcome: matched per-match clean/corrupted spellF1 and macroF1, with the existing paired gate plus median corrupted gain >= .01. Independent PFF transfer scores are risk measurements, never selection criteria. A necessary precondition is that possession labels are not also used to manufacture the input ball trajectory in a way unavailable on target tracking.

Confidence is **high** in the smoothed-ball leakage/serving-mismatch finding and the identified code-contract gaps. Confidence is **low** in exact cross-provider possession-convention equivalence; schema agreement cannot establish it.

## 1. Blocking: smoothed ball positions are annotation-conditioned

The supplied *PFF FC Tracking Data Specification v2.2*, PDF page 2, explicitly describes player Kalman smoothing and a different ball procedure: PFF uses its events, places ball positions at the ball carrier and interpolates between events. This is external-source documentation, not an inference from model scores. Extracted evidence is in `data/pff/document-text/PFF FC Tracking Data Specification v2.2.txt`, around lines 175-232.

The reviewed adapter reads `ballsSmoothed` and `homePlayersSmoothed`/`awayPlayersSmoothed`. Several core features then directly depend on distance from players to that annotated carrier-conditioned ball position. A successful provider transfer score with these fields could partly reflect how the label helped create the features. More-data training would also see a feature-generation process absent from raw target tracking. This can make PFF look artificially easy without improving real transfer.

**Required action:** preregister a raw-ball policy before modelling. Prefer raw `balls` as independent source observations; do not fall back to `ballsSmoothed` when raw ball is absent. Keep the entire smoothed variant out of the selection comparison. If smoothed player positions are retained, state that they use a Kalman procedure and verify they are not event-derived. Using raw player observations too is the cleaner comparable measurement policy. Do not compare several such policies on model scores to choose one under the guise of preprocessing.

The specification, PDF pages 3-4, defines `visibility` as VISIBLE versus ESTIMATED. Ignoring it conflates detected and estimated positions. Require a fixed, documented observed-only policy or explicitly separate both provenance classes. An ESTIMATED finite coordinate must not silently count as an observed raw ball. Audit raw/smoothed and visible/estimated availability by state; do not use those descriptive cuts to relabel or rebalance classes.

Expected impact: credible scores may be lower than a carrier-conditioned-ball evaluation; actual generalization could improve or worsen. Neither direction is established before the raw-data comparison.

## 2. CLK: not established as a safe play/ownership event

`CLK` is absent from the supplied tracking-spec game-event enum (page 6; extracted text around lines 765-820). Its name alone is not sufficient evidence that it cannot signal a discontinuity relevant to state carry.

In the reviewed `event_state`, marking CLK NEUTRAL only prevents a play-state update; the subsequent common `home_ball` logic still updates ownership from CLK. Thus "CLK neutral" does not currently mean fully neutral.

**Required action:** either obtain a provider-supported explanation and explicit policy, or fail closed for affected segments: clear state and owner on CLK, require a fresh supported state/team assertion before recovering H/A/D, and report the exclusions. Do not alter the primary reference-video time using an undocumented game-clock correction. Absence of CLK in the fixed pilot does not validate it for all 64 matches.

## 3. Unknown carry and interval validity

VID now clears stale owner, which addresses one real risk. However, the loader can preserve live state/owner across a long gap in native observations if no VID event is present. `resample` marks the middle of a source-time gap X, but the first subsequent native record can recover an old label from carried state even with no fresh supported event.

**Required action:** preregister whether gaps exceeding native support clear state/owner; the conservative choice is to clear them until a fresh assertion. Also validate embedded `game_event.start_frame/end_frame` against the grouped source frame, or explicitly justify a provider state-transition carry contract rather than assuming an event can assert current ownership indefinitely. Track the last supporting event/frame and why each output label is known. "Annotated record present" is not the same as a valid unique-frame label.

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

## Resolution assessment  -  November 7, follow-up during full admission preparation

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

## Final admission assessment  -  November 7, after cohort lock d4b72ac

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

"Natural missing" here includes source absence, non-VISIBLE coordinates and observations conservatively discarded by the fixed consensus rule. It should not be described as a pure camera-occlusion indicator. The table concerns the 25 Hz prepared representation and provider conventions, not human-verified game truth.

### Caveats that remain, without justifying post-hoc cleanup

1. Label coverage is extremely high but not literal completeness: the aggregate X support is 1,348 frames. CLK/VID/unsupported-gap handling can make exclusions non-random. Retain per-match coverage and unknown counts in transfer interpretation.
2. PFF "clean" data already contain substantial missing observations. Additional synthetic corruption can only increase missingness; its total missing rate need not match the target's observed rate. Report natural, newly masked and total missing subsets separately as the evaluation protocol requires. Do not rank providers by comparing their different clean/corrupted conditions as if the observation regimes were matched.
3. Nearest native observations and past-only labels may straddle transitions by a native frame. This is a fixed documented resampling choice, not perfect simultaneity. It remains an alignment/noise limitation, not grounds for changing the rule after scores arrive.
4. The visible tests do not exercise every malformed metadata, half-order and cumulative-clock path. Finite-fps/distinct-team/period-order defensive checks remain worthwhile engineering follow-up, but the reviewed 64-match verified cohort provides no observed invalid input demonstrating a new stop condition. Keep those safeguards distinct from an allegation of corrupt current data.
5. The code/snapshot checks are reproducibility evidence, not independent validation of provider annotation semantics. Event-defined ownership, dead-ball transitions and unknown intervals may differ from IDSSE. Provider transfer also changes competition/teams/camera coverage. A good or poor transfer score cannot isolate one cause.

### Evaluation interpretation

Keep the original five-match outer held-out IDSSE matches out of both parent and expanded training in comparison A. Its strengthened gate is the only promotion decision. Evaluation B must remain descriptive; no tuning, source cleanup, calibration, match replacement or version choice may depend on the 16 transfer matches. Both sealed IDSSE matches remain untouched and permanently excluded from training.

A's legacy known-label-run decoder resets and B's half-only inference are explicitly different in the preregistration. Do not present their score difference as an isolated provider effect. Once results are available, report per-match heterogeneity and live-gap recovery alongside the aggregate gate; no synthetic or admission result substitutes for performance evidence. Keep production at the current candidate unless A passes the full gate and clean-environment reproduction.



# Research archive 23 - pff-evaluation-review-2026-11-07

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: docs/pff-evaluation-review-2026-11-07.md

# Independent PFF evaluation-design review  -  November 7, 2026

Scope: AGENTS.md, project memories, committed split, source configuration/features/decoder and prior aggregate reports. No competition assets, public-label rows, sealed matches, private predictions or new performance experiments were accessed. This is a design review, not evidence that PFF will improve the model. I own only this document; no production code or commits changed.

## Decision

Proceed to the two authorized evaluations only after all-64 admission contracts pass or a fixed, non-performance failure policy is recorded. Keep nine-core unaugmented CatBoost and penalty16 unchanged. Freeze remains November13. Confidence is high in this no-leak design; confidence in actual provider transfer is currently low because it has not been measured.

## A. Train-more comparison: exact paired design

For each of the original five IDSSE development matches j:

- Parent fit: the other four IDSSE development matches.
- Expanded fit: those SAME four IDSSE matches plus admitted matches from the locked PFF48 additional-training group. Never include j or PFF16 transfer-holdout matches in either training/calibration path.
- Training is clean/unaugmented: every-fifth-frame sampling after excluding unknown labels, same nine columns, seed20261106, CPUthread1,300iterations,depth6,rate.05,l2=3, no early stopping, calibration, weights or new preprocessing. Do not cap/rebalance PFF after seeing results. Increased source rows and provider dominance are consequences of the authorized one data-volume change; report actual sampled rows and wall time.
- Evaluate BOTH fits on identical clean j and the identical existing fixed target-like corrupted j features/masks. Prefer fresh one-thread parents or explicitly verify cached-parent predictive equality. Distinct cache keys must include training IDs, split hash, features, parameters and corruption fingerprint.

Gate is per match, not pooled frames: let S be official spellF1 and F be macroF1. Paired spell delta is mean(clean S delta, corrupted S delta); paired macro delta is analogous. Require median paired spell delta>0, at least3/5 positive paired spell deltas, median paired macro delta>=-.01, AND median corrupted S delta>=+.01; tests pass and clean deterministic reproduction before use. Report all ten cells, all five deltas, failures, missing-ball quality and variability. A positive overall mean or one large match gain does not substitute for the gate. This gate is an engineering rule, not a statistical-significance guarantee.

A rejection leaves original model untouched. No more-data weighting, provider-specific thresholds or feature changes may be folded into a rescue attempt without a separate authorized protocol.

## B. Cross-provider risk: do not select versions from it

- IDSSE -> PFF: train on all original five IDSSE development matches, evaluate all admitted matches in the locked PFF16 transfer holdout. The current final model can be reused only with verified identical config/training provenance and one-thread inference.
- Reverse: train on admitted PFF48 ONLY, evaluate the original five IDSSE development matches. Do not include any IDSSE samples in that fit. This is the requested reverse transfer measurement, not another promotion gate.
- Never include either sealed IDSSE match. Preserve PFF48/16 membership even if admission fails; report missing/failed matches and reasons rather than replacing difficult matches.
- Fix all adapter choices, class mappings, feature definitions, execution seeds, corruption seeds and decoder choices BEFORE reading transfer scores. No fitting temperature/class balance/thresholds, choosing a variant, or choosing a cleanup rule by PFF16 performance. Transfer is descriptive risk measurement even when surprising.

Report each match clean and corrupted, provider-specific equal-match means/medians/ranges/SD and source label/observation coverage. A pooled frame-weighted number would overrepresent longer or less-excluded matches. Do not pool two providers into one quality claim; their supervision conventions may differ. With16 PFF matches and5 historically reused IDSSE matches, report the population difference; do not call reverse results independent confirmation of prior IDSSE development results.

## Critical inference-block caveat

Existing scripts use blocks_valid(y, half_blocks) to reset decoding at true-label X gaps. That is annotation-informed segmentation, whereas production target inference uses only supplied half blocks. It can affect continuity and spell boundaries. This is a methodological caveat, not proof a promotion decision was wrong.

For A, preserve the legacy parent's segmentation on both sides for a controlled one-change comparison and explicitly disclose it. For the new transfer-risk protocol, preregister observation/metadata-only inference blocks (prefer half boundaries only), then let the unchanged scorer mask X labels. Do not select decoder reset points from actual H/A/D transitions. If legacy X-reset evaluation is retained for transfer, label it as annotation-supported evaluation and do not claim full production-equivalent inference. Never compare A and B aggregate numbers as though their segmentation protocols/populations were identical without documenting that difference.

## Missing-ball dead/live metric contract

Define E as frames inside included half/time blocks with known ground truth y∈{H,A,D}. Define M0 from the adapter's clean ball XY visibility BEFORE synthetic corruption, and M1 from visibility AFTER corruption, recomputing masks/gap age from raw masked positions. Frame denominators must use unique resampled25Hz frames, never expanded duplicate native records.

For each match/condition report:

1. |E|, excluded-X frames, known-label time coverage and H/A/D support.
2. Natural missing subset E∩M0, additional newly missing subset E∩M1∩not M0, and all currently missing subset E∩M1. PFF clean already has natural missingness; do not call clean "fully observed." Do not impute naturally missing balls to force its total missing rate to equal a target rate.
3. For each nonempty subset, TP_D,FP_D,FN_D,TN_D, then D precision/recall/F1, live recall=TN_D/(TN_D+FP_D), binary macroF1 and predicted-D fraction=(TP_D+FP_D)/N. Here D is positive, live is H/A collapsed. Include class support; when no live or no dead support exists, mark the affected metric undefined with the denominator, not a convenient zero or silently dropped class.
4. Explicitly show missingness fractions over E for each condition and the fixed seeds/hash of each raw-position mask. Existing IDSSE evaluation masks/seeds remain unchanged. New PFF masks require a preregistered deterministic ID/seed rule; do not choose seeds by resulting scores.

The prior development failure is near-constant D during missing-ball frames. D recall alone can look perfect while live recall is almost zero. The proposed table tests whether naturally missing PFF examples improve that behavior without hiding class-support changes. It cannot by itself isolate the causal source between emissions, decoder and label convention.

## Admission and interpretation risks, ranked

**High confidence / high impact:** native duplicates and unknown/X exclusions change the evaluation population. Publish per-field duplicate, coordinate-missingness, state/owner-conflict and unique25Hz known-label counts per half before models. Provisional100% delivered-record annotation presence is not an admission statistic. Report censored fragments and short-spell support; excluded intervals can artificially shorten observed spells.

**High confidence / high impact:** PFF48 vastly outnumbers four IDSSE training matches. Class/source mixture and naturally missing broadcast tracking may drive any gain or regression. Treat that as part of the one data-source change; do not infer that label count alone caused the outcome or silently rebalance to fix it.

**High confidence / medium impact:** nine-column output must retain the same order, units,25Hz speed/gap semantics and half resets. Normalize each source using its own metric pitch; verify player-team slot membership and classes_ probability reordering. No provider ID feature or target-label-derived mapping.

**Unresolved / potentially high impact:** PFF and IDSSE possession continuation through loose balls/flight and interruptions may differ. Even valid schema and passing tests establish an executable contract, not cross-provider possession truth. Poor transfer should trigger a documented bug/convention investigation, not tuning to its labels.

**Persistent limitation:** the original five matches were reused historically. Nested previous searches and a new source do not erase this. PFF16 risk measurements and later sealed evaluation improve evidence only if they remain outside selection/tuning decisions.

## Highest-value next slice

Before any fit, publish one admission matrix for all64 matches: source records -> unique native keys -> duplicate observations -> coordinate/missingness disagreements -> state/team conflicts -> half/time checks -> unique25Hz frames -> known/unknown labels, with natural missing-ball x H/A/D support. Keep rows private, aggregates/hashes committed. Then preregister A/B exact training populations, mask seeds, inference-block policy and gate; execute once, report failures without replacement or retrospective threshold changes.

Sources: experiments/pff-intake/split.json; src/possession/config.py/core.py/decode.py; scripts/run_core.py/review_frozen.py; docs/review-data-analyst-2026-11-07.md; project memories. No newly measured performance is asserted here.

## Outcome verification  -  completed A/B, November 7

I independently recomputed the decision and headline summaries from current aggregate JSON only. No raw/target/public/sealed assets, model files or prediction arrays were read; no training or scoring was rerun. The cohort contains all48 fixed training matches and all16 fixed holdout matches, with zero admission exclusions. Completeness is20 A cells and42 B cells (16forward+5reverse matches, each clean/corrupted).

**No decision-changing arithmetic issue found. Reject expanded training and retain the original unaugmented penalty16 configuration.** All five paired spell changes are negative; median paired spell change is-.056268, median paired macro change-.099643, and median corrupted spell change-.034930. Both gates fail, not merely the+.01 corrupted minimum. Stored gate deltas/decision agree with independent recomputation. Tests are recorded as passing, but this review did not rerun them.

| Evaluation | Condition | Equal-match mean spellF1 | Equal-match mean macroF1 | SpellF1 sample SD |
|---|---|---:|---:|---:|
| A parent | clean | .517654 | .895099 | .031366 |
| A parent | target-like | .323476 | .679401 | .012640 |
| A expanded | clean | .423010 | .771147 | .022289 |
| A expanded | target-like | .289040 | .623183 | .009950 |
| B IDSSE5 -> PFF16 | clean | .177631 | .698513 | .052004 |
| B IDSSE5 -> PFF16 | target-like | .111395 | .546575 | .030475 |
| B PFF48 -> IDSSE5 | clean | .390468 | .732170 | .018423 |
| B PFF48 -> IDSSE5 | target-like | .271346 | .602691 | .013021 |

B remains descriptive transfer-risk evidence, never a promotion/cleanup/calibration selection tool. The asymmetric scores cannot isolate a causal provider effect because training populations, labels, observed coverage and domain distributions differ. A rejects this particular unweighted expanded-data intervention at the fixed budget; it does not establish that PFF labels or any future compatible use can never help.

### Missing-ball trade-off, not a successful fix

On A's identical286943 corrupted missing-ball frames across the five matches, pooled confusion counts imply parent predicted-D share99.9655% and live recall.0638%; expanded training predicts D93.8434% with live recall8.9503% and D recall97.1340%. This is genuine movement away from the nearly constant-D response, yet it coexists with worse whole-match spellF1 and macroF1 and does not override the gate. These pooled confusion rates are explicitly frame-weighted diagnostic summaries, distinct from equal-match headline scores. They cannot identify whether source mixture, label conventions, visibility distribution, model capacity/budget or another factor caused the degradation.

### Segmentation caveat narrowed by actual data

The A/B implementation policies differ (legacyX resets versus halves only), as previously documented. However, every completed result reports known_label_fraction1.0; there are no X gaps in these scored arrays. Therefore the X-reset disparity is a **general protocol caveat, not a demonstrated active driver of this run's score difference**. Keep the distinction documented for future cohorts, but do not attribute the observed transfer gap to X resets here.

### Immediate decision and next slice

Keep production unchanged. Record the failed train-more result and the transfer risk without retroactively changing source weights or reusing PFF16 as a tuning leaderboard. The next useful observational slice is an aggregate source-mixture/label-support/visibility table over actual sampled training rows, to distinguish plausible drivers without rerunning models. Any proposed data weighting or mixture intervention would be a new preregistered change and must not be silently bundled into this rejected comparison. Preserve sealed evaluation and target-score restrictions.

Verification sources: experiments/pff-evaluation/train-more-results.json, transfer-results.json, gate.json, cohort.json and the generated report. All numeric summaries above were recomputed directly from those aggregate files. No new independent generalization guarantee is claimed.



# Research archive 24 - gru-results-review-2026-11-08

Historical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: docs/gru-results-review-2026-11-08.md

# Independent GRU result review  -  November 8, 2026

Scope: AGENTS.md and project memories; experiments/gru-2026-11-08/{results,parent,gate,determinism,cost,protocol}.json/md; legacy penalty16 aggregates in experiments/gap-augmentation/decoder-isolation.json. Only aggregate files and the preregistered protocol were read. No raw data, PFF holdout files, target/public labels, sealed matches, prediction arrays, model files, training or scorer execution were used. This arithmetic review is not a new performance experiment. I edited only this document and made no commits.

## Decision

**Reject this fixed GRU blend and retain the unaugmented nine-core CatBoost+penalty16 production candidate. No decision-changing arithmetic issue found.** Determinism passes the recorded operational checks, but predictive quality fails both required spellF1 conditions. No extra blend, epoch, window or hidden-size search is justified by this result; it tests one bounded configuration, not all sequence models.

Completeness checks:10candidate cells,10matched parent cells and10determinism cells cover exactly the same five matches x clean/target-like conditions. There are five initial-fit cost records. I independently recomputed all15 per-match deltas and checked them against gate.json within1e-12.

| Gate component | Independently recomputed result | Required | Outcome |
|---|---:|---|---|
| Median paired spellF1 change | -.008147538 | >0 | Fail |
| Positive paired spell changes | 1/5 | >=3/5 | Fail |
| Median paired macroF1 change | +.000052442 | >=-.01 | Pass |
| Median target-like corrupted spellF1 change | -.007520197 | >=+.01 | Fail |
| Stored production tests | Pass | Pass | Recorded pass; not rerun here |
| Recorded deterministic checks | All10case flags pass | All pass | Recorded pass; not rerun here |

Two of five corrupted-only spell deltas are positive, but that does not satisfy the majority paired gate or the minimum median corrupted gain. Overall average macroF1 improves slightly while spellF1 worsens; it would be wrong to use that small frame-level gain to override the ranking metric or prespecified gate.

## Headline scores and fold variation

Equal weight per match; SD is the sample SD over five matches, not a confidence interval.

| Model | Condition | Mean spellF1 | Mean macroF1 | SpellF1 SD |
|---|---|---:|---:|---:|
| Parent penalty16 | clean | .517654 | .895099 | .031366 |
| Parent penalty16 | target-like | .323476 | .679401 | .012640 |
| Fixed GRU blend | clean | .504499 | .895223 | .039395 |
| Fixed GRU blend | target-like | .317274 | .680278 | .017940 |

| Match | Paired spell delta | Paired macro delta | Corrupted spell delta |
|---|---:|---:|---:|
| J03WMX | -.018115 | -.000435 | -.012831 |
| J03WN1 | -.008074 | +.000559 | +.001781 |
| J03WOH | +.001107 | +.002742 | +.002559 |
| J03WOY | -.015165 | -.000416 | -.015001 |
| J03WPY | -.008148 | +.000052 | -.007520 |

Parent half-only decoding and legacy penalty16 decoding agree **exactly** on every match/condition spellF1 and macroF1 value: maximum absolute difference0 for both metrics. Thus the inference-block policy change is not an active explanation of this run's score difference. The protocol still correctly makes inference independent of true-label reset points.

## Determinism and cost: what is and is not established

All10records report repeated_training_equal, reload_probabilities_equal and csv_bytes_equal_reload_batch4 as true. This supports the tested same-version, same-CPU software contract for external development inference, including saved/reloaded models and the extra batch4 check. It is not a fresh-environment, cross-hardware, cross-release or target-game CSV reproduction claim. No target run is needed to reject this candidate.

The five initial fits sum to24.385491 recorded seconds. Each used200updates, batch8,250input frames and200retained loss frames. That time excludes repeated-training checks, model loading, inference, validation and setup; do not label it end-to-end experiment cost. CatBoost parent budget is unchanged, while the GRU adds compute, so this is not a compute-matched architecture comparison. Falling training losses do not establish generalization or justify extending the fixed budget after seeing the rejection.

## Missing-ball behavior and uncertainty

Across286943corrupted missing-ball frames, pooling the aggregate confusion counts gives:

| Model | Predicted-D share | Live recall |
|---|---:|---:|
| Parent | 99.9655% | .0638% |
| Fixed blend | 99.9460% | .0999% |

These are explicitly frame-weighted diagnostics, not the equal-match gate inputs. The tiny movement does not fix the near-constant-dead failure mode, and no causal allocation between emissions, blend, decoder, training distribution or window length follows from it.

The protocol already identified two important limitations before results: clean IDSSE training has no ball gaps, so corrupted mask/gap inputs remain out of distribution; and the fixed10-second input window cannot see an observed endpoint in some long-gap interiors. Both fit the observed weak missing-live recovery as plausible mechanisms, not proven causes. One rejected short-budget setting does not rule out sequence modelling in general. Historical reuse of these five matches continues to limit independent generalization claims; no statistical significance or target accuracy is established.

## Immediate recommendation

Keep production unchanged, archive the candidate and preserve the fixed one-model stop. Record that deterministic execution succeeded while quality failed. Do not reopen stopped tracks or use transfer/target/public/sealed results to rescue this configuration. Remaining work should follow the frozen-candidate review and scheduled November13 evaluation/delivery rules; any future research would require explicit scope and a committed protocol, not an implicit extension of this rejected trial.

