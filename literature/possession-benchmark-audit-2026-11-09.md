# Possession benchmark audit — 2026-11-09

## Question and method

Can published tracking-based soccer models justify predicting an increase from the selected model's clean development spellF1 of .5177 to .8, and which approach deserves further investigation? Searched primary papers, author/institutional full texts and official repositories for possession estimation, temporal convolutions, TranSPORTmer, PathCRF and masked multimodal learning. Public sources only; no competition or sealed assets read, and no model executed. This is a targeted technology assessment, not a systematic review or new performance evidence.

**Verdict: no verified study reports this project's official H/A/D spellF1 under the same observation conditions and split. No defensible numerical gain forecast follows from the literature.** Accuracy, event F1 and spellF1 must not be interchanged.

## Evidence table

### 1. PathCRF — relevant structured player-interaction design, not a .7569 spellF1 benchmark

[Primary paper, KDD 2026](https://arxiv.org/html/2602.12080v1). Seven Sportec Open DFL matches, split 5/1/1; test contains 1,831 events. Player-only inference uses 10-second windows at 5Hz, then upsamples to25Hz. Training and inference are restricted to known in-play segments. Labels are synchronized/refined using ball trajectories and events.

Dynamic masked CRF achieves event F1 .7569 versus .6534 independent non-CRF and .7314 constrained Viterbi with the same backbone. Event correctness requires matching event type and acting player within1second after sequence alignment. Edge accuracy is .6964. These are not team-spell IoU scores. One held-out test match provides weak evidence for broad cross-provider generalization; the study does not solve independent dead/live detection in full matches.

[Official repository](https://github.com/hyunsungkim-ds/pathcrf) supplies code and trained checkpoints; [root licence](https://raw.githubusercontent.com/hyunsungkim-ds/pathcrf/main/LICENSE) is MPL2.0. Existing local metadata audit identifies possible checkpoint/development and sealed-validation overlap; exact checkpoint training hashes remain unverified. Do not use public weights as an independent comparison. A clean scratch implementation with declared training provenance would be needed. CPU/Mac training cost and deterministic full-match integration are unmeasured.

### 2. TranSPORTmer — social/temporal masking is relevant; headline accuracy is not the target

[Primary ACCV2024 paper](https://arxiv.org/html/2410.17785v2). Soccer experiments use283 LaLiga2022–23 matches, disjoint match splits,9.6second sequences at6.25Hz:82,954/7,500/6,258 train/validation/test sequences. Labels are pass, possession, uncontrolled and out-of-play, not team H/A/D.

The approximately90% state-accuracy headline concerns tasks where the ball is visible; authors explicitly identify ball visibility as a principal reason. Separate ball inference/imputation experiments must not be conflated with that result. This paper motivates masked player-interaction representations but does not establish .8 team-spellF1 or domain transfer. Original runnable licensed checkpoints were not established by this audit or the prior repository audit. The paper's licence does not license unavailable code/weights. PathCRF's adaptation is not evidence of an original turnkey release.

### 3. CropDrop multimodal model — extra visual information helps a different benchmark

[Primary WACV2026 paper](https://arxiv.org/html/2512.19528v1). Proprietary283-match2022–23 top-league dataset, disjoint matches,43,397/3,968/3,347 sequence splits. Inputs combine player trajectories, types and player image crops, with no ball positions at inference. All out-of-play-containing sequences are excluded.

Best reported state accuracy is .8585 and possessor accuracy .8956; these are frame accuracies, not full-match H/A/D spellF1. Without masking, full modalities reach .8767 possessor accuracy versus .8366 trajectories+types; the ablation supports additional visual evidence on that dataset, not a transferable gain estimate. No usable licensed public checkpoint/training corpus was verified. Reconstructing the multimodal training pipeline is a substantial effort, not an available local model switch. Its omitted dead-ball regime is a major applicability limitation here.

### 4. Temporal convolution + self-attention — closest label formulation, still not comparable spellF1

Borghesi, Costa, Morra & Lamberti,2023, [publisher](https://doi.org/10.1016/j.eswa.2023.119780), [institutional full text](https://iris.polito.it/retrieve/d9aa6bfd-b26e-44cd-bf9e-6004e676211a/1-s2.0-S0957417423002816-main.pdf). Confidential35-match source at approximately16Hz. Main model selection uses eight matches with least live-ball missingness, split4/2/2 with sampled100k/5k/5k training/validation/test windows. Additional ablations evaluate20matches.

Uses per-object temporal embeddings with permutation-invariant aggregation;64frame windows predict frame48, incorporating future context. Inputs include positions, velocities, roles, team identity and missingness. Ball positions are Akima-interpolated. Reported possession accuracy .862 and dead/alive accuracy .892 are separate classification tasks; possession comparison excludes inactive samples. Main global model-selection accuracy is .8639, while extended20match mean global accuracy is .8159. These differing evaluation populations matter.

This is the closest three-state formulation among reviewed models, but its selected low-missingness games, sampled windows, interpolation and accuracy metrics do not establish performance on long raw gaps or complete possession spells. Public reusable code/checkpoint terms were not verified. Article open access is not a model licence. No measured Mac runtime established.

## Synthesis and practical recommendation

High confidence: published .8–.9 figures do not establish that .8 is attainable here. High confidence: current benchmark mismatch is large enough that importing headline scores would mislead. Moderate confidence: explicit temporal interactions between players, roles/teams and ball provide a more relevant new-information route than changing the tabular estimator over the same nine features. Confidence in any exact gain is low.

Near-term recommendation is an error audit on the selected penalty16 parent before reopening experiments. If clean wrong-team/short-spell errors dominate, test one compact temporal player–ball-control representation before a large architecture. A TCN with player-set aggregation is an alternative new sequence-model hypothesis, not a rescue of the failed GRU or a guaranteed improvement. If long missing-ball errors dominate, consider masked player-only interactions, while predicting dead/live independently rather than providing true in-play windows.

Do not silently reopen stopped feature/decoder/sequence tracks. Any new experiment requires an explicit plan amendment, committed protocol, fixed seeds and budget, unchanged official scorer, complete match timelines and the existing promotion gate. Retain the sealed evaluation and prohibit public-label selection. A fresh reproducible improvement can be measured; a literature-derived .6/.7/.8 forecast cannot.

## Gaps and next searches

Exact original code/checkpoint licences and training manifests remain unresolved for TranSPORTmer/CropDrop/TCN. Independent full-match evaluation with naturally missing ball, provider shifts and spell-IoU metrics is absent from the inspected evidence. Additional papers predicting match phase from already-known possession/status should be excluded as circular. The literature does not identify an achievable ceiling under this project's observations or labels.
