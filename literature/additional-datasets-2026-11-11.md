# Additional dataset refresh — November 11, 2026

Documentation-only search at the user's request. No dataset, archive, video, array, weights or sample rows downloaded, cloned or inspected. Browsed official public descriptions/licences only. No tests or model runs. Existing training splits/protocols remain unchanged.

## Decision

SkillCorner remains the strongest conditional lead, but this refresh admits **zero new labelled matches**. It was already considered on November7. Possession fields and phase intervals are promising; missing phase coverage cannot automatically become dead-ball supervision. Do not add another provider before it passes the original label/observation/licence/split checks. The failed PFF expansion shows that more matches alone do not establish better scores. Current balanced trial stays exactly as registered.

|Source|Published material|Direct H/A/D suitability|
|---|---|---|
|[SkillCorner/PySport open data](https://github.com/SkillCorner/opendata)|10Hz player/ball tracking, centered metres, possession.group/player_id and in-play phases. Detected/extrapolated flags. [Repository MIT licence](https://github.com/SkillCorner/opendata/blob/master/LICENSE).|Strongest conditional candidate. Need explicit exhaustive live/dead coverage and possession semantics; do not equate null possession/missing ball/absent phase with D. Restrict inputs to authorized observed data; audit whether extrapolation uses labels.|
|[Metrica sample data](https://github.com/metrica-sports/sample-data)|Synchronized tracking and events; prior project audit records3games,25Hz,normalizedXY (third EPTS).|Potential Metrica-domain relevance, not confirmed same capture system/conventions as target. No verified continuous H/A/D supervision or explicit repository data licence in this audit. Event propagation would be new proxy labels, not automatically ground truth.|
|[SoccerTrack v2](https://atomscott.github.io/SoccerTrack-v2/)|10full panoramic4Kmatches; GSRcoordinates/roles/teams/IDs and12ball-actionclasses. Official site says datasetCCBY4.0,codeMIT,university amateur matches.|Useful possible tracking/event pretraining source. Continuous possession-team plus live/dead supervision not verified. GSR/actionlabels are not H/A/D. Do not claim direct compatibility.|
|[SoccerNet GSR](https://www.soccer-net.org/tasks/game-state-reconstruction)|30secondbroadcastclips with pitchlocalization, team/role/jersey labels; task focuses on athlete reconstruction.|Not verified continuous possession/live-dead labels. Short clips do not replace full-match possession-spell evaluation.|
|[Alfheim/Simula](https://datasets.simula.no/alfheim/)|20HzZXYplayertracking and synchronized panorama; ballpixeltracks described for some videosegments.|No verified continuous pitch-ball/H/A/D combination; auxiliary tracking lead only, not admitted.|
|[StatsBomb open data](https://github.com/hudl/open-data)|Eventdata and selected360files.|Event/freezeframe observations do not supply native continuous trajectories for the currentTCN; not a drop-in source.|

Count caution: SkillCorner's current README describes10matches, while the project's November7audit found20matchdirectories. This refresh did not enumerate/download the catalogue, so neither number is a newly verified usable-match count. Dataset directory count is not compatible labelled-match count.

An attempted guessed SkillCorner phases-doc URL returned404; the official repository README and official linked tutorial are sufficient to confirm in-play phase descriptions, not exhaustive dead-label semantics. No absence claim is strengthened by the404. Additional official tutorial: https://skillcorner.github.io/opendata/notebooks/tutorials/02_Working_with_Game_Intelligence_and_Dynamic_Events/Part7_Pitch_Maps_Tracking_by_Phase_Tutorial/ .

Next evidence, if the user later supplies/authorizes files: validate actual schema/codes, phase completeness/unknowns, observed-only player/ball masks, licence scope and provider overlap; register hashes and match split before any modelling. Current task authorizes discovery only, not downloading/admission/training. Preserve sealed exclusions and the stopped-track rule. No score gain predicted.
