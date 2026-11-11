# New visual evidence routes — November 11, 2026

## Decision

Video can add evidence that our existing trajectory model never sees. The strongest new conditional lead is a soccer-specific ball detector whose outputs could recover balls visible in the tactical image but absent from tracking. No evidence establishes how much of the target's missingness is recoverable this way. This is not a verified path to .8spellF1 or an admitted model. Four targeted search queries plus primary-source opens only; no video, dataset, weights, repository, code or inference downloaded/executed. No target/public/sealed/PFF-holdout assets read. Only this report edited; parent owns journal/state.

## 1. Conditional reusable model: RFDETR-Soccernet

Uploader's [model card](https://huggingface.co/julianzu9612/RFDETR-Soccernet) declares Apache2.0, SoccerNet-Tracking training, and four classes including ball. The [public file listing](https://huggingface.co/julianzu9612/RFDETR-Soccernet/tree/main) shows inference code, a weights directory and1.57GB repository at displayed commit1e388b9. Card benchmarks and CPU rates are uploader claims, not independently reproduced; they are detection metrics, not possession spellF1. Its2025changelog makes this an older model newly identified for this project, not a fresh2026release. No per-match training manifest or overlap proof was found. Direct weights-subdirectory and metadata views were inaccessible, so exact checkpoint compatibility/hash was not verified and no binaries were fetched.

[Upstream RF-DETR](https://github.com/roboflow/rf-detr) lists Apache2.0 for package and Nano/Small/Medium/Large detection, with other variants under different terms. Its [develop LICENSE](https://raw.githubusercontent.com/roboflow/rf-detr/develop/LICENSE) confirms Apache2.0 code. That does not independently verify the uploader's training-data rights or checkpoint provenance. Initial guessedmain/LICENSE andmain/LICENSE.md404s were resolved by the actualdevelop branch; no repeated unchanged blocked requests.

**Inference, moderate confidence:** a dedicated detector offers a concrete source of additional ball observations. Exact gains, tiny-ball performance on this tactical view, deterministic inference and M3runtime remain unknown. The uploader card's large-model description differs from current upstream naming/capacity; pin architecture/version before any possible load. No turnkey adoption recommended.

## 2. Stronger published mechanism: separate ball detection and temporal association

Amazon's author [MOT4MOT technical report](https://www.amazon.science/publications/soccernet-2023-tracking-challenge-mot4mot-team-technical-report), [primary PDF](https://cdn.amazon.science/85/d3/d80367db49e193628f1214bdd10a/soccernet-2023-tracking-challenge-mot4mot-team-technical-report.pdf), documents a dedicated fine-tuned YOLOv8l ball detector, temporal filtering and interpolation, rather than treating ball tracking exactly like player association. It trained the detector from2,084SoccerNet frames and used200manually inspected test frames for validation. Its reported66.27HOTA concerns combined tracking, not possession. No author-released tuned detector checkpoint with complete licence/provenance was verified here.

**Project implication:** the mechanism is credible; do not copy its validation split or interpolation policy. Our held-out-match rules and raw-observation masks remain binding. [Ultralytics' own FAQ](https://docs.ultralytics.com/help/FAQ/) provides the AGPL/enterprise licensing route; the report itself is not a reusable-model licence. Generic sports-ball weights are not evidence of tactical-video ball recall.

## 3. Higher-cost multimodal route: CropDrop

[Primary paper](https://arxiv.org/html/2512.19528v1) uses trajectories, types and player crops to jointly infer ball trajectory/state/possessor. It supplies a reason visual body/context information can complement positions. Its proprietary283-match data include possessor supervision and synchronized crops; out-of-play sequences are excluded. Publicly reusable training corpus and licensed runnable checkpoint were not established. Reported frame accuracies do not measure our full-match H/A/D spellF1.

**Inference:** useful architecture inspiration if synchronized external footage and suitable labels are admitted. It is not an available pretrained replacement, and evidence excluding dead play cannot establish performance on ourDclass. Rebuilding it beforeNov16 has substantial unmeasured engineering/training cost.

## Admission gate before any video experiment

High-confidence blocker: reviewed registered inputs establish tracking/label arrays for the five IDSSE development matches and PFF cohort, but not an admitted synchronized-video-plus-H/A/D evaluation path for those same matches. This review did not inventory private videos, so it does not assert they are absent. [SoccerNet's official tracking kit](https://github.com/SoccerNet/sn-tracking) offers ball/player boxes and videos, but trackingHOTA labels are not continuous H/A/D. Its video access/data terms are separate from the [MIT downloader licence](https://github.com/SoccerNet/SoccerNet/blob/main/LICENSE). Do not silently add such clips to the possession promotion cohort or use their test/challenge assets for training.

Required next evidence, before model code/downloads: confirm authorized synchronized external video, frame/time/homography mapping and compatible continuous possession/dead labels; otherwise preregister a genuinely new external labelled cohort before modelling, preserving all18protectedmatches. DetectionAP may establish detector quality separately but cannot satisfy the existing possession promotion gate. No target hand-labels or public-score tuning can substitute for an external evaluation.

A detector cannot observe an off-camera or fully occluded ball. Homography maps image observations to pitch coordinates; it does not reveal invisible objects, and aerial balls need geometric care. Recovered detections must retain confidence and provenance; interpolated/hallucinated positions must not become observed truth. False balls can corrupt distance/speed features and reduce spell quality. Existing player-slot identity/coverage problems are separate.

## Recommendation strength and next step

**Conditional recommendation, moderate mechanism confidence, low expected-gain confidence:** pursue external video/label/provenance admission for a detector-based new-information branch, prioritizing metadata inspection of RFDETR-Soccernet over writing a full visual possessor model. Do not download or run it under this research request. If compatible external evaluation footage cannot be established, defer video integration and finish the already registered rotation comparison/release qualification. Representation/source/decoder stop rules are unchanged; a new branch needs an explicit plan amendment and precommitted protocol, never relabelling a stopped search. CPU/M3runtime, RAM and byte-repeatability remain unmeasured. No new experiment or model was selected/promoted.
