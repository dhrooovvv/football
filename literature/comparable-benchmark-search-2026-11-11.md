# Comparable possession benchmark search

November11,2026. User explicitly requested research agents and scraping papers, Reddit andTwitter/X. Three agents were dispatched; the papers agent supplied the official-metric lead, then all three hit service usage limits before complete reports. Root completed the public-source verification. No exhaustive search or unrestricted social-platform crawl is claimed. No model/test/scorer execution, raw data/ground-truth files, protected matches, downloads of datasets/weights/repositories, submission or publication. Saved external aggregate arithmetic and public documents only.

## Conclusion

Found an exact official-metric baseline and a separate same-scorer synthetic research project. No verified public real-match research result matched our full evaluation conditions well enough to rank our model or infer a winning cutoff. This is a bounded-search finding, not proof no such result exists. The strongest current direct comparison remains supplied baselines evaluated on the same five external matches.

## Exact task/scorer reference

[Official EVALUATION.md](https://raw.githubusercontent.com/metrica-sports/more-than-a-hack-2027/main/EVALUATION.md) explicitly labels these as full-match results:

|Official baseline|macroF1|spellF1|
|---|---:|---:|
|raw|.6532|.0486|
|smooth25|.6752|.1996|
|smooth50|.6724|.2433|
|smooth125|.6356|.2242|

The challenge calls smooth50 the published floor. It is neither a reported winning score nor a minimumtop20 qualification threshold. It uses the target match; our development mean uses external matches. Do not subtract or divide these numbers to claim superior target performance. No target score was run or used to choose a method.

Source inspection of the unchanged local official scorer establishes matching semantics: maximalH/A intervals only, same-team IoU-descending greedy one-to-one matching, F1 averaged overIoU .3/.4/.5/.6/.7. D influences possession boundaries but is not itself a possession object. GT X is ungraded; predictedX is charged in frame metrics and forward-filled/back-filled inside gradedruns for temporal metrics. Halves remain separate. MacroF1 is the equal mean of H/A/D frameF1. Our saved score is an equal mean over five matches, not a pooled target-match score. The documented~.04 full-match noise heuristic is not a universal confidence interval for our paired-development gate; gatepass does not claim statistical significance. Public-window tuning remains forbidden.

## Direct existing comparison on the same external matches

No retraining or rescoring. Recomputed means from experiments/diagnostics-review/results.json and experiments/tcn-rotation-2026-11-11/results.json, exact same fiveIDs/conditions. Earlier TCN preparation checks aligned derived inputs/labels with frozen core clean/corrupted sources.

|Model|Clean spellF1|Target-like corrupted spellF1|
|---|---:|---:|
|Supplied smooth50 baseline|.296145|.196645|
|CatBoost16|.517654|.323476|
|Retained rotation TCN|.602155|.477682|

Retained versus smooth50 mean gains are+.306010clean/+.281037corrupted. This is measured improvement on reused external development matches. It is not an independent held-out generalization claim or an externalSOTA leaderboard. Training folds overlap and methods have been selected on the same five.

## New social lead traced to first-party methodology

PublicLinkedIn repost byMetricaSports: https://me.linkedin.com/company/metrica-sports identifies PrithvirajPatil's PossessionLab. The cited short GitHublink resolved through publicpageHTML to [project repository](https://github.com/prithvi-kaizen/football-analytics/tree/main/projects/possession-lab). Root inspected publicREADME/reports only, never datasets, privatecompetitionlabels or archives.

[ProjectREADME](https://raw.githubusercontent.com/prithvi-kaizen/football-analytics/main/projects/possession-lab/README.md) says it uses the unchanged official scorer but with scripted synthetic motion. [Historical Phase1report](https://raw.githubusercontent.com/prithvi-kaizen/football-analytics/main/projects/possession-lab/docs/phase1/REPORT.md) reports hierarchy.851 versusHMM.041 on stationary-live synthetictrials; no numerical replication here. Certain stoppage tests retain zeroDrecall. PublicMetrica excerpts lack independently trusted possession labels, so accuracy is withheld. Thus this is same-metric syntheticdiagnosis, not a real-match score comparable to ours.

The [new motion-v2report](https://raw.githubusercontent.com/prithvi-kaizen/football-analytics/main/projects/possession-lab/reports/motion-v2/comparison.md) further warns against taking.851as a target: stationary-live hierarchy.552 versusstatemachine.777 under a different continuous generator. The author explicitly separates those results from historical benchmarks. Neither generator establishes competition quality, ranking or attainable gain. Useful mechanisms are factorized live/dead and conditionalteam evidence, uncertainty/observability tests and independent event information; adoption would require a separately justified external experiment, not a decoder-stop bypass. Do not change the running pretraining protocol from this search.

## Academic near-matches

|Primary work|Reported quantity|Why it does not rank our spellF1|
|---|---|---|
|[TCN2023](https://doi.org/10.1016/j.eswa.2023.119780)|86.2%live possessionaccuracy;89.2%dead/aliveaccuracy|Frameclassification, sampled/confidentialdata anddifferentmissingness; notspellIoU. Abstract+7.3 differsfromTable3+7.1pp, recordedpreviously.|
|[PathCRFv2](https://arxiv.org/html/2602.12080v2)|Published SporteceventF1~.7388;crossprovider~.4916 inone direction|Player/eventpath metric, knownliveepisodes/supervision andprovidertransfer assumptions differ. SameSportecsourcealone does not yield samebenchmark.|
|[BallRadar](https://arxiv.org/html/2306.08206v1)|Teamframeaccuracy/ballpositionerror under masking|Inplaywindows andrandommasking differ fromfullmatchD andlongbursts.|
|[Vidal-Codinaetal2022](https://arxiv.org/html/2202.00804v1)|Mosteventcategories exceed90%detectionrate|Discreteeventdetection, notone-to-one wholepossessionIoU F1.|
|[Guoetal2026](https://www.mdpi.com/1424-8220/26/4/1252)|PossessionpercentageRMSE|Aggregatedurationagreement doesnot measurepossessionboundaries.|

These are primary method sources, not an orderedSOTA table. EPV/outcome prediction, playerIDF1/HOTA, detectorAP andcooking-videoF1@50 were excluded as rankingcomparators.

## Reddit and X coverage

Searches covered exactspellF1/possession-spellF1, challenge/modelscore phrases, soccertracking benchmarks, and domain-restrictedReddit/X/Twitter queries. They yielded:

- [r/computervision footballtracking thread](https://www.reddit.com/r/computervision/comments/1vjnu4i/football_match_tracking/): YOLO/trackingdemo andidentity-loss discussion, no independentlylabelled possession-spellbenchmark.
- [r/computervision seven-componentpipeline](https://www.reddit.com/r/computervision/comments/1wldmdq/seven_ai_components_analyzing_football_video/): detector/tracking/camera pipeline andexplicitgroundtruth concerns; no comparablespellscore.
- [r/sportsanalytics possessionvalue](https://www.reddit.com/r/sportsanalytics/comments/1i0gijz/): valuationquestions, a differenttask.
- Otherindexedhits concerned NBAtracking, matchoutcome prediction, eventpressure or genericdemos. No benchmarknumber adopted from them.
- X/Twitter domainsearches returned irrelevantposts/trendpages andlogin-limitedresults; no verified comparablemodelscore. No comprehensiveXcrawl, authenticatedsearch orabsenceclaim. Socialengagement is not benchmarkevidence.

## Retrieval limits and decision

GitHubrenderedproject subfolder was restrictedbywebfetch; publicrootREADME/rawprojectdocumentation were accessible. LinkedInshortlink yielded a publicinterstitial, resolved from its outboundhref withoutlogin. No authentication bypass or contact with authors. Searchsnippets were treated as leads until primarydocuments were opened. Agentusagefailures were not interpreted as scientific evidence. No fullmatch competitor leaderboard or independently reproduced competitor model found.

Decision: report clearprogress versus same-match suppliedbaselines, retain targetaccuracyunknown and do not claimSOTA. Complete the registered pretraining comparison unchanged; use authorized sealed evaluation atfreeze for the independent check. No new model/experiment/threshold from this research. Persist sources and limitations; no further broad modelshopping is warranted by these findings.
