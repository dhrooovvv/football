# Competitors, precedents and possession practices — November10,2026

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

## What rivals may bring — inference, not observed submissions

Plausible entries span three levels: proximity/rule baselines; learned temporal player-control systems with carefully audited labels/masks; and resource-intensive video+tracking systems with stronger pretraining and ensembles. The strongest practical advantages may be cleaner supervision, better missing-ball evidence, explicit control/boundary modelling and training/validation discipline rather than one fashionable model name. No probability, architecture distribution, competitor identity or score estimate is justified by the public record.

## Implications for our project

Our selected .517654clean/.323476corrupted are external development results, not competition standing. The200-step scratchTCN failed .117838/.082347, despite contract/repeatability passes. It was a compact fixedpilot, not a reproduction of the publishedTCN or a competitive training programme. We should not call its failure proof that temporal models cannot work, or assume moresteps willfix it. The next justified diagnostic is a preregistered small-training-segment overfit test with classshares/learningcurve/unsmoothedversusdecoded behaviour. This remains a proposal: the boundedTCNtrial is closed and no dataset commands run here. An amendment and protocol are required before any diagnostic or longer-fit experiment; user retains execution. Modelpromotiongate, sourceoverlaplicencechecks, no targetpubliclabelselection and November16freeze remain.

## Social evidence and limitations

See possession-social-2026-11-10.md for actual engine coverage, Redditpermalinks and Xavailability. Recruitment posts establish interest only; mirroredcrossposts do not identify multiple independent teams. Technicalcomments are practitioner anecdotes, not benchmarkvalidation. Publicsearches forXyielded no usable relevant posts, so no privatecompetitorintel or Xconsensus claim is made. Socialretrieval limitations cannot establish absence of stronger competitors.
