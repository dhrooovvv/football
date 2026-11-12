# Cross-sport benchmarks and implications — 2026-11-13

## Scope and method

Question: which sports evaluate temporal segments with an F1 related to our possession spellF1, and what leading methods might transfer? This is a bounded scoping review, not a systematic review or exhaustive leaderboard. Applied ECC market-research and scientific-thinking-literature-review workflows. Primary papers and organizer reports support technical claims; search results and social discussion are discovery aids only. Search notes are retrospective, not a preregistered review protocol. No experiments, tests, models, arrays, restricted assets or downloads were executed/read. No Reddit/X scraping engine was run for this review.

Search families included football possession/phase temporal IoU, SoccerNet challenge F1, figure-skating temporal segmentation F1, and FACT frame/action attention. Rechecked earlier literature/comparable-benchmark-search-2026-11-11.md. Excluded frame accuracy, event mAP and synthetic-only results from direct score comparisons. Public author/organizer pages were checked November 13, 2026. Author preprints are evidence of reported results, not independently verified current world records.

## Metric alignment

Our unchanged reference scorer matches same-team H/A intervals one-to-one greedily by descending IoU, then averages F1 across IoU .3/.4/.5/.6/.7. D affects interval boundaries but is not a possession spell; X is ungraded; halves are separate. A valid external numerical comparison would also need matching label semantics, matching/aggregation, full-match coverage, missing-ball conditions and independent splits. No exact real-match equivalent was verified in this bounded search. Absence of a verified comparator is not proof none exists.

## Primary evidence

### Figure skating: closest metric family

[VIFSS, Tanaka et al., 2025 preprint](https://arxiv.org/html/2508.10281v1) uses view-invariant contrastive pose pretraining, sport-specific fine-tuning and FACT frame/action cross-attention. Element-level F1@50 is 92.56%, versus 49.62% at F1@90. Evaluation excludes entry, landing and None labels, with competition-year separation. These are reported segment-overlap F1 scores; the paper's overlap wording is less precise than a scorer implementation, which was not independently executed. Different labels, exclusions, thresholds and aggregation prevent numerical comparison to possession spellF1. This is a published method lead, not a verified 2026 global leader.

### Football: explicit challenge winner, different F1

[SoccerNet 2026 organizer report](https://arxiv.org/html/2607.07320v1), section 3: PAVE wins player-centric ball-action spotting at 58.94 macro F1; baseline 46.41. It combines player spatial attention, temporal transformers and four differently configured trained variants. Matching requires correct action/team/jersey within ±12 frames. The notation F1@0.15 denotes a confidence cutoff, NOT segment IoU. It measures event points, not possession intervals; it is a verified winner of this specific challenge, not a possession benchmark.

### Football tracking: related segmentation problem

[Li and Link, 2026 preprint](https://arxiv.org/html/2606.09289v3) studies seven Bundesliga matches with leave-one-match-out evaluation. T-GAN combines player graph modelling, attention pooling and temporal transformers. Tactical phases are inferred inside already identified stable possessions; evaluation includes all-overlap temporal IoU, not our one-to-one spellF1. Known possession episodes/owner are unavailable assumptions for our ownership task. Its temporal filtering must not be imported as a long minimum possession duration.

## Implications and decision

Inference: the useful common direction is relational player representation plus reasoning about temporal segments, rather than simply enlarging a frame classifier. Strong ensembles can also use complementary representations; a second random seed is a narrower intervention than architectural diversity. None of these papers establishes an attainable possession spellF1 of .8, or demonstrates that our data/protocol has reached a ceiling.

Current eligible development winner remains the staged40k original-motion TCN: mean clean spellF1 .632870845 and target-like corrupted .497549978. These five repeatedly reused development matches do not support a world-ranking claim. Production remains nine-core-feature, unaugmented CatBoost with penalty16; target accuracy is unknown. The preliminary completed ensemble screen is not a promoted best and is not used as one here.

Finish the already registered attention trial and ordered comparison before considering another architecture. Current within-team masked attention tests only one component of these richer systems; it is not a reproduction of PAVE or T-GAN. If further research is separately authorized, the strongest substantive proposal is a symmetric player/ball relational encoder with segment-aware temporal reasoning, registered as one controlled change at a time. Prior failed BCE-boundary and masked-ball-pretraining adaptations are not rescued by papers using different objectives. Keep stopped tracks, promotion gates, sealed matches and November16 freeze unchanged. No new experiment is registered or authorized by this review.
