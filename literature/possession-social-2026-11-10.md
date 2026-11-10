# Public community evidence — November10,2026

## Scope and verdict

Research question: what do actual More Than A Hack participants and football-CV practitioners publicly reveal about methods, standards and likely competition? Public sources only. No target/sealed match data, modelling or current competition public-score selection. No outreach or private-group access. This is a small, self-selected community sample, not a census of submissions.

**High confidence:** public recruitment exists and common demo pipelines combine detection/tracking/calibration with simple possession logic. **Low confidence:** what leading current competitors will actually submit or achieve. No inspected post discloses a verified current-competition spellF1 or a winning implementation. Do not attribute posts to this user or infer that multiple crossposts represent multiple teams.

## Observed posts and comments

- [r/FootballDataAnalysis recruitment](https://www.reddit.com/r/FootballDataAnalysis/comments/1xaqrrr/title_recruiting_football_enthusiasts_for_the_fc/): engine dates post October20,2026,4upvotes/3comments at fetch. A comment by u/OddsRelay identifies the usual proximity baseline and warns that “it falls apart on aerial balls and scrambles.” It recommends settling treatment of contested frames. This is useful practitioner opinion, not measured benchmark evidence or a confirmed participant solution. [Exact comment permalink](https://www.reddit.com/r/FootballDataAnalysis/comments/1xaqrrr/comment/phwxz0p/).
- [r/computervision recruitment](https://www.reddit.com/r/computervision/comments/1xaqmra/recruiting_football_enthusiasts_for_the_fc/): describes intended serious experimentation/documentation and seeks a mixed team, but gives no model, score or implementation. Cached relative dates vary across rendered pages; no exact publication date claimed from that rendering. It is not evidence that this team has a stronger solution.
- [r/hackathon teammate search](https://www.reddit.com/r/hackathon/comments/1xezly3/looking_for_1_teammate_more_than_a_hack_2027/): says the team is predicting possession from tracking data and seeks Python/data/statistics/ML-evaluation skills. No algorithm, training protocol or score disclosed. Rendered as16daysago at fetch; exact date not independently established.
- [Seven AI Components Analyzing Football Video](https://www.reddit.com/r/computervision/comments/1wldmdq/seven_ai_components_analyzing_football_video/): author describes detector, ball tracking, identity persistence, calibration, pose, jersey recognition and tactical visualization. In an [author comment](https://www.reddit.com/r/computervision/comments/1wldmdq/comment/paxz7k0/), the author says they combine detections with “temporal tracking/smoothing” because the ball is small, fast and occluded. Other comments list PyTorch/Ultralytics, OpenCV, ByteTrack/DeepSORT, EasyOCR and TensorRT/CUDA. These are self-reported system components; no possession interval evaluation, verified winning submission or project metric is given. Rendering varies1–2monthsago: treat as older contextual evidence, not definitely within fresh window. CUDA/TensorRT specifics do not imply Mac compatibility.

The technical implication is modest: domain conventions, aerial/contested control and robust tracking matter; model names alone do not demonstrate possession quality. Generic public CV demos often solve upstream tracking that this challenge already provides. Public enthusiasm and polished overlays cannot be converted into expected spellF1.

## Reddit/X collection and limits

Installed last30days3.31.0 engine executed under validatedPython3.13 with explicit named-entity query plan and as-ofNovember10, windowOctober11–November10. Runtime62.7seconds. Passed plan covered competition and possession-method terms, four resolved subreddits and available sources. Quickmode internally reduced actual collection to primaryquery/Reddit+HN. Do not claim a completed YouTube/GitHub scan from the plan alone.

DirectReddit site/global/subreddit requests returned403. ArcticShift fallback retrieved40posts,36removed as off-topic, then3of4removed by relevance floor;1Reddit recruitment thread retained. HN4stories retained in overall engine output, but no qualifying technical competitor-method claim is drawn from them. A separate direct publicRedditJSON attempt for post timestamps also returned403; no bypass/repeated retries. Host-web rendering supplied the linked direct-thread/comment supplements above.

**X/Twitter:** engine diagnostic found no authenticated Xbackend. Browser cookies were not read and no login initiated. Two X-domain-restricted host searches for competition and soccer-possession terms returned no indexed results. Therefore this report does **not** claim an actual Xtimeline scrape or that Xis quiet. Optional source omitted: X/Twitter was not enabled; research continued with the available sources. The third-party TwStalker profile search result is excluded as insufficient original-post evidence.

Source availability was checked via diagnostic and cacheddoctor; configuredGitHub credentials meant setup was unnecessary despite absentglobalsetupmarker. No keys/cookies printed or changed. No paid source enabled.

## Decision and remaining uncertainty

No social source justifies changing production, assuming competitors have0.8spellF1, or claiming no sophisticated competitor exists. The plausible method families in the main technology report remain hypotheses informed primarily by published work, not insider knowledge. To strengthen competitor knowledge, inspect released official finalist repositories/technical reports after they are public; do not treat recruitment posts as submissions. No request to contact participants or obtain confidential materials is implied.

Evidence artifacts: possession-social-2026-11-10-engine.log and .txt; rawengineMarkdown under possession-social-engine-2026-11-10/. Root will commit this report and log only, retaining noisy raw outputs locally. No experiment ran.
