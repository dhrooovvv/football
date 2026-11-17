# MDPI possession paper: project relevance

Reviewed November 11, 2026. Primary article: https://www.mdpi.com/1424-8220/26/4/1252 . Public author repository: https://github.com/jiecao233/YOLOv8-P2S3A-HWD3A (AGPL-3.0 listed; weights/provenance not admitted).

The study detects the ball/players, clusters jersey colours and uses proximity with hysteresis/duration/holding rules. It evaluates aggregate possession percentages against match statistics, not spellF1. Table3 RMSE4.85 differs from abstract4.87. Algorithm1 has team/UNKNOWN states without a validated full-match H/A/D evaluation. Goalkeepers are excluded from colour clustering.

Project inference: useful conditional detector lead to recover a visible but untracked ball. Detection cannot supply off-camera observations. Our existing pitch tracking and team assignments reduce the value of replacing the entire pipeline; duration/holding could worsen missed short spells. Require synchronized external video, compatible labels, homography, provenance and downstream evaluation before admission. No evidence warrants replacing current TCN or forecasting a gain.

No downloads, tests, training, inference, protected inputs, new experiment or publication. Current winner remains.602155clean/.477682corrupted; next learning proposal remains prospective.
