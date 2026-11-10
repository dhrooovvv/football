# Comparable competitions and documented solutions — November 10, 2026

## Scope and verdict

Primary organizer papers, official task repositories and a winner's own repository were checked. No competition match assets, labels, current public scores, private competitor submissions or model runs were accessed. This is an adjacent-competition audit, not a prediction of the current leaderboard. The 2026 More than a Hack edition is a direct organizational precedent, but its winning product was a tactical conversational system rather than a publicly scored H/A/D interval predictor. SoccerNet supplies documented quantitative precedents for soccer perception and temporal reasoning; its metrics are different from this project's spellF1.

**High confidence:** strong competitors can bring domain-specific pipelines, learned temporal/player interaction models, transfer learning and carefully validated ensembles. **Low confidence:** which current teams are actually doing any of these, what their score will be, or whether a released model will transfer to this task. No public evidence supports a numerical competitor-score forecast.

## Direct predecessor: More than a Hack 2026

FC Barcelona Innovation Hub's April 30, 2026 interview identifies **IpurdIAr** as the winning project. It combines positional information, derived match events and commentary transcription into a conversational tactical analyst. The team describes using provided 25Hz positions, spatial zones, pressure/proximity, ball motion and defensive-block descriptors; it did not build its own computer-vision tracker. Whisper transcription was linked to game moments. The interview is evidence of the product and its ingredients, not a benchmark of possession boundaries: no comparable possession-spell score or independently replicated error rate is provided.

Sources: [FC Barcelona Innovation Hub interview](https://barcainnovationhub.fcbarcelona.com/blog/ipurdiar-football-analysis-chatbot/), [Metrica organizer recap, March 5, 2026](https://www.metrica-sports.com/blog/inside-the-bar%C3%A7a-innovation-hack-ai-football-data-and-tactical-intelligence-at-talent-arena-2026).

The [official 2026 starter repository](https://github.com/metrica-sports/more-than-a-hack) describes tools for loading tracking/Smart Tagging, producing visualizations and exporting custom pattern XML for Nexus playlists. It is a starter, not the verified winner's source. I did not locate an authenticated public IpurdIAr source/checkpoint release. This means release status is unverified, not that no release exists.

**Implication:** a polished tactical assistant can win an application hackathon without establishing the accuracy of possession segmentation. Building a chatbot would not address the current Phase 1 ranking objective and is not recommended as a metric intervention.

## SoccerNet 2025: team ball action spotting

The [official results paper](https://arxiv.org/html/2508.19182v1) reports **dudek, 60.03 Team-mAP@1**, versus baseline 51.72. Inputs are broadcast videos; labels are 12 action types and acting team. Seven annotated games plus two private challenge games are described. Matching is for point events within one second, using team-aware average precision—not possession intervals.

The winner refined T-DEED, unified action/team predictions, used video augmentation, pre-trained on 500+ broadcast matches and fine-tuned on the dense challenge data. Its [author repository, int8/dude.k](https://github.com/int8/dude.k), releases training/evaluation and preprocessing code. Public code is verified; licence rights and a usable pretrained checkpoint were not audited here. This is not a plug-in H/A/D model.

The author README warns its full frame-extraction route can require around **1.2TB extra disk** and up to **24 hours**, depending on hardware. That is an author estimate for its own workflow, not a measured cost on this Mac. Copying the entire video-pretraining pipeline is therefore a substantial commitment, not an immediate small experiment.

## SoccerNet 2026: player-centric ball action spotting

The [official July 8, 2026 results paper](https://arxiv.org/html/2607.07320v1) reports **PAVE, 58.94 Macro-F1@0.15**, versus baseline 46.41. Predictions must match action class, team, jersey and timing within ±12 frames. These are eight point-event classes, not H/A/D spans.

PAVE adds temporal attention to per-player visual features and spatial relations between players before following them through time. Four independently trained variants are fused, using agreement to suppress false positives with special handling for rare tackles. This supports complementary player/spatial/temporal reasoning as an architectural lead. It does not justify ensembling arbitrary weak models, guarantee possession performance or establish hardware feasibility. A public winning implementation/checkpoint was not verified in this audit.

## What current competitors may bring — inference only

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
