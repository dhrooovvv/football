# Research findings

## Current understanding
Possession ranking depends on whole H/A spells; stoppage mistakes and flickering can damage it even when frame scores appear reasonable. Missing observations are not dead-ball labels. The supplied baselines score reproducibly, but a complete pipeline has not been implemented or trained. A standalone decoder now passes its synthetic contracts.

## Evidence
See ball.md J001 and audit/evaluation/scoreboard.csv. Prior supplied-file public spellF1 values: raw 0.0378, smooth25 0.2868, smooth50 0.3256, smooth125 0.4242. These are pipeline-check measurements, not a tuning leaderboard. Synthetic audit faults are retained in audit/probe-results.json.

## Working direction
Rules + Viterbi is the first delivery path. CatBoost + Viterbi is the first learned candidate, conditional on external labels. Direct and factorised prediction need comparison. No current evidence proves either superior. Full-ball reconstruction adds an intermediate problem whose benefit is unmeasured.

## Lessons and constraints
Never tune against target public labels or claim a hidden score. Whole-match splits and structured occlusion tests are required. Preserve short possessions. Keep target-only Smart Tagging separate from external model performance claims. Read ball.md before work and append evidence after meaningful actions.

## Open questions
Match access and registration; external label completeness; contributor availability; domain shift; runtime; exact official cutoff. No optimisation trajectory exists yet: one synthetic correctness run completed; external performance runs = 0.

## H1 contract result (November 6)
Six confirmatory and three exploratory tests passed. The tested decoder preserves strongly supported short spells and removes the prescribed ambiguous flicker. Exhaustive enumeration checks agree on ten small exploratory sequences. This supports component correctness, not external spellF1 improvement. Evidence: experiments/h1-decoder-contracts/analysis.md.
