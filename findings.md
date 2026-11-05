# Research findings

## Current understanding
Possession ranking depends on whole H/A spells; stoppage mistakes and flickering can damage it even when frame scores appear reasonable. Missing observations are not dead-ball labels. The supplied baselines score reproducibly, but a complete pipeline has not been implemented or trained. The input/feature/export foundation and decoder pass 18 synthetic tests. Tactical inputs validate and real label-free features are materialised locally.

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

Phase 1 remains partial: external-label adapter, sealed match IDs and learned inference are outstanding. Existing paused automation remains paused.
