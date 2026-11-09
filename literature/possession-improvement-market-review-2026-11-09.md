# Possession improvement technology review — November 9, 2026

## Decision and scope

Current evidence does not support a numerical forecast of achievable official spellF1, including .8. Keep CatBoost16 selected. Research suggests representation of temporal player–ball control is more relevant than another generic tabular-model substitution. The immediate action is a current-penalty16 external error audit; any model/feature trial needs explicit reopening of its stopped track and a committed protocol. No training, inference, sealed evaluation or target-label selection was performed for this report.

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
| GNN-LSTM match-phase classification (October8,2026) |203matches, seven tactical phases, authors report baseline gap4.6% macroF1; possession/status are inputs | Not an alternative possession predictor without removing unavailable inputs and retraining. October8 is outside strictOct10–Nov9 freshness window, despite search engine calling it recent. |

Primary sources: [TCN publisher](https://www.sciencedirect.com/science/article/pii/S0957417423002816), [TCN institutional manuscript](https://iris.polito.it/retrieve/d9aa6bfd-b26e-44cd-bf9e-6004e676211a/1-s2.0-S0957417423002816-main.pdf), [PathCRF paper](https://arxiv.org/abs/2602.12080), [PathCRF code](https://github.com/hyunsungkim-ds/pathcrf), [TranSPORTmer](https://arxiv.org/abs/2410.17785), [CropDrop primary PDF](https://openaccess.thecvf.com/content/WACV2026/papers/Peral_Multi-Modal_Soccer_Scene_Analysis_with_Masked_Pre-Training_WACV_2026_paper.pdf), [T-GAN](https://arxiv.org/html/2606.09289v1), [GNN-LSTM](https://arxiv.org/html/2610.11571v1). Root publisher/institution landing requests forTCN returned403; benchmark agent subsequently accessed the institutional full text. Its review documents the35-match confidential source,8-match main selection with4/2/2split, sampled windows, ball interpolation and .8159 mean global accuracy in an extended20-match evaluation. None is official spellF1. See companion benchmark audit.

## Local evidence that narrows the choice

See docs/improvement-evidence-review-2026-11-09.md. Core inputs lose distance/margin/speed/edge information when ball is absent. A compact trajectory TCN would add per-player temporal observations and team identity rather than merely replacing the classifier over the same nine scalar columns. Current parent predictsD on99.9655% of corrupted missing-ball frames, live recall .0638% (pooled diagnostic rates, not equal-match scores). PFF training moved live recall but worsened spell quality. Rolling whole-pitch aggregates, gap augmentation, small9-feature GRU, settings/decoder trials and10k/30kTabICL did not pass their gates. Thus neither more rows, larger generic emissions nor coarse geometry alone has demonstrated a solution.

Correction to earlier discussion: label-X decoder resets are a general caveat, not a discovered source of current score loss. Reviewed completed scored cohorts have full known-label coverage; prior GRU half-only/legacy parent scores match. No label-transition inference reset defect was found in the inspected paths.

## Ranked next steps, conditional rather than approved protocols

1. Refresh penalty16 error taxonomy and support masks with fixed diagnostic definitions; no new selection. Old oracle repair gains overlap and are not an achievable additive bound. Quantify short-spell, wrong-team, dead/live and boundary losses by gap length. This is the decision input.
2. If ownership handovers dominate, one fixed temporal control representation with observed-support masks, retaining CatBoost16. Choose either short history/look-ahead evidence OR relative player–ball motion; do not bundle both. No slot-continuity assumptions without external identity contracts. Reject under unchanged gate if benefit absent. Track reopening and protocol commit required.
3. A raw per-player trajectory TCN/set-pooling model is a more substantial alternative to the failed9-featureGRU, but only after data/identity/visibility feasibility and explicit sequence-track amendment. A new architecture with the same information-poor inputs is not the same intervention. Mac runtime and deterministic output remain unmeasured.
4. A provider-mixture intervention is conditional on a training-only provider×class×visibility row audit. Do not choose source weights using PFF16 transfer scores. LargerPFF volume already failed, and label consistency may dominate.

Do not start all candidates. Same five folds/seeds/budget/corruption, primary corrupted median gain>=+.01 plus original gate and reproducibility remain. Stop limits andNov13freeze apply. A development win remains provisional until the one-time sealed comparison. No .6/.7/.8 forecast, no automatic promotion, no publication of data/predictions or external submission.

## Companion evidence

- literature/possession-benchmark-audit-2026-11-09.md: specialist primary-source metric/checkpoint audit.
- literature/recent-possession-2026-11-09.md: recent engine scope/results/coverage limitations.
- docs/improvement-evidence-review-2026-11-09.md: local evidence and inference-boundary review.
