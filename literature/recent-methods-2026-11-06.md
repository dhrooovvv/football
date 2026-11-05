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
