# Open possession models: primary-source audit

Audit date: 2026-11-08. Read-only public metadata and source inspection. No weights, raw matches or prediction rows downloaded; no training or inference executed. This is feasibility evidence, not evidence of improved project spellF1.

## Search scope and recency

Three pre-engine searches covered open soccer ball-possession models, checkpoint releases, and relevant communities. Verified topic discussions in r/computervision and r/sportsanalytics; r/MachineLearning is an inferred broader community. Search surfaced an October 9 YOLO11/BoT-SORT analytics demo, but no controlled H/A/D spellF1 result or demonstrated replacement for our possession classifier. A recent soccer reinforcement-learning paper concerns action valuation using possession context, a different task. Search dates and crawl dates are not model release dates. Absence from these searches does not prove no other open model exists.

## PathCRF: strongest auditable research lead, not a drop-in replacement

Official paper: <https://arxiv.org/html/2602.12080v2> (v2 June 1, 2026; KDD 2026). Official repository HEAD inspected: `1b7c6f85a6b78c92e4543fde72ca2b86a933f997`, commit June 8, 2026. Public GitHub metadata last-pushed June 8, 2026; this is older foundational work, not a newly verified October/November release.

- Repository code licence: MPL-2.0, explicitly present in [LICENSE](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/LICENSE). This does not by itself establish unrestricted rights to underlying data or separately licensed assets.
- [README](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/README.md) lists five trained variants in `saved/100`, `110`, `120`, `130`, `140`; public tree contains `state_dict_best.pt` and `state_dict_best_acc.pt` for each. Inspected filenames/JSON metadata only, not binary contents.
- [saved/140/args.json](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/saved/140/args.json): Sportec source, `lomocv=true`, `cv_fold_idx=6`, target 5 Hz, ten-second windows, eight node inputs, set-transformer/socio-temporal backbone, dynamic sparse CRF, approximately 3.43 million parameters. This is not a TranSPORTmer checkpoint.
- [datatools/utils.py](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/datatools/utils.py#L98) constructs episode IDs only on frames where `ball_state == "alive"`. [inference.py](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/inference.py#L880) loops only over positive episode IDs. Public wrapper therefore assumes supplied live segmentation; its results do not establish end-to-end dead/live inference.
- [inference.py lines 394 onward](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/inference.py#L394) gathers stable named-player columns and selected coordinate/velocity/speed/acceleration inputs; if any selected feature is missing, it returns no episode prediction. Agent permutation equivariance does not establish tolerance to arbitrary identity switches across time.

### Checkpoint overlap warning: conditional, not a verified training manifest

The [public tree](https://github.com/hyunsungkim-ds/pathcrf/tree/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/data/sportec_synced) lists filenames `J03WMX`, `J03WN1`, `J03WOH`, `J03WOY`, `J03WPY`, `J03WQQ`, `J03WR9`. No parquet contents were opened. [train.py lines 472-496](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/train.py#L472) sorts processed filenames; in LOMOCV, index 6 is test and preceding index 5 is validation; both are excluded from fitting.

**If** the processed training directory contained that canonical seven-file set when `saved/140` was trained, its JSON and current code imply fitting on our five development matches, validation on `J03WQQ`, and test on `J03WR9`. Exact checkpoint-to-input hashes and a contemporaneous training manifest were not established. Do not state that either sealed match was definitely fitted, nor claim the checkpoint is uncontaminated: development reuse and sealed-validation exposure are material risks. Do not load it for independent development/sealed comparison. Metadata inspection has not opened either sealed match's observations or labels.

## TranSPORTmer: relevant masked-trajectory architecture, unavailable turnkey model

Original [ACCV 2024 paper](https://arxiv.org/html/2410.17785v2) describes masked socio-temporal attention and four states: pass, possession, uncontrolled, out of play. These are not directly H/A/D. Original runnable code, licensed original checkpoints and training manifests were not verified in the inspected paper/repository sources; a paper licence is not a code/weights licence.

PathCRF supplies an [adaptation](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/models/transportmer.py) plus training scripts ([edge](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/scripts/transportmer_edge.sh), [CRF](https://github.com/hyunsungkim-ds/pathcrf/blob/1b7c6f85a6b78c92e4543fde72ca2b86a933f997/scripts/transportmer_crf.sh)). These select trials 710/750, absent from the public saved checkpoint tree. The adaptation exposes ball/possession-edge outputs and optional possession macro heads; it does not establish delivery of the original four-state CLS model. It runs through PathCRF's data/inference wrappers and inherits the integration constraints above unless deliberately redesigned and tested.

## BallRadar: public implementation, licence and weights gaps

Official [repository](https://github.com/hyunsungkim-ds/ballradar), inspected HEAD `2486896cfb933ecd304489883241a00e3645ca8c`, commit July 6, 2023. GitHub repository metadata last-pushed February 3, 2026, which differs from main HEAD commit date and is not evidence of a new model release. No published GitHub releases were returned.

[README](https://github.com/hyunsungkim-ds/ballradar/blob/2486896cfb933ecd304489883241a00e3645ca8c/README.md) describes player-trajectory possessor classification followed by conditional ball reconstruction. Recursive tree inspection found no saved model binaries or root-level project licence. GitHub repository licence metadata is null; the vendored `set_transformer/LICENSE` does not establish a licence for all BallRadar code. Public visibility alone is insufficient to call the entire project freely reusable or pretrained. These findings are scoped to the inspected repository tree, not a proof that author-hosted checkpoints or permissions cannot exist elsewhere.

## CropDrop / multi-modal masked pre-training: paper evidence only

[WACV 2026 paper](https://arxiv.org/html/2512.19528v1) describes player trajectories, types and image crops, trained on 283 proprietary matches; out-of-play sequences are excluded. Its reported possessor/state accuracies address related tasks, not our H/A/D spellF1. No runnable licensed code/checkpoint link was verified in the inspected paper. This is a research direction, not an available drop-in open model.

## Decision

High confidence: public PathCRF code and weights exist, but its known-live wrapper, missing-player contract and checkpoint overlap risks prevent an immediate clean replacement test. Moderate confidence: TranSPORTmer-style masked player interactions are a plausible way to address missing-ball information; this is an architectural hypothesis, not a performance claim. BallRadar and CropDrop are currently weaker implementation candidates because usable licence/checkpoint provenance is unresolved.

Keep production unchanged. The next useful evidence is a bounded metadata/input-contract audit that establishes a licence, exact checkpoint training provenance, label-free live/dead behavior and adequate player identity/coverage without touching sealed matches or target labels. A new performance experiment would require its own committed protocol and explicit reopening of the already completed bounded sequence-model track; this audit does not authorize that reopening.

## Post-engine supplement: three searches, no performance experiments

After the engine completed, exactly three batched search queries covered (1) open soccer possession pretrained releases in October/November 2026, (2) original TranSPORTmer/CropDrop public code and checkpoints, and (3) general open tabular models applicable to the existing feature matrix. Follow-up opens and metadata reads verified the following primary sources. No additional search-query dispatch followed this batch.

### TabICLv2: new-to-this-project, credible emissions-only benchmark lead

Official [repository](https://github.com/soda-inria/tabicl), [documentation](https://tabicl.readthedocs.io/en/latest/), [paper](https://arxiv.org/abs/2602.11139), and [model card](https://huggingface.co/jingang/TabICL). Inspected source HEAD `d83091b845a8c5f7c087bd54964f755a9e560f45` was committed October 27, 2026; the [commit](https://github.com/soda-inria/tabicl/commit/d83091b845a8c5f7c087bd54964f755a9e560f45) adds prediction-consistency tests using synthetic data. This is a verified in-window maintenance event, not a new checkpoint or soccer-quality result.

- [Licence](https://github.com/soda-inria/tabicl/blob/d83091b845a8c5f7c087bd54964f755a9e560f45/LICENSE): BSD-3-Clause core; derived forecasting subdirectory has an Apache-2.0 notice. Author model card also declares BSD-3-Clause for weights.
- [README](https://github.com/soda-inria/tabicl/blob/d83091b845a8c5f7c087bd54964f755a9e560f45/README.md) lists default classifier `tabicl-classifier-v2-20260212.ckpt`. The paper was submitted February 11 and revised September 16, 2026, outside the fresh window. The checkpoint filename alone is not independent evidence of an exact public release timestamp.
- Synthetic tabular pretraining; explicit `fit`/`predict_proba` interface, local inference, and support for missing values. `fit` supplies labelled context to a pretrained predictor; absence of gradient training does not remove the need for match-grouped folds and fold-local preprocessing/context selection.
- CPU is supported. Author documentation recommends GPU for large datasets and describes CPU/disk offloading for large contexts. Million-row GPU scalability is not a measured single-thread CPU runtime or byte-reproducibility guarantee on this machine.
- Authors report strong generic TabArena/TALENT results; no H/A/D spellF1 result or direct comparison with this project's CatBoost exists. Treat this as a candidate, not a measured winner.

**Inference:** this is the most practical newly identified *open pretrained emissions-only* lead because it could retain the existing nine-feature interface and penalty-16 decoder, has available weights and a permissive licence, and synthetic pretraining avoids an identified football match-overlap dependency. However, identical nine-core inputs contain no extra whole-pitch player evidence when the ball is missing. A more powerful predictor cannot recover information absent from its inputs; whether it improves usable conditional probabilities and spellF1 remains empirical. Context cost on hundreds of thousands of correlated frames is the main operational uncertainty. A bounded CPU/memory/determinism feasibility test would come before any scored experiment, and requires a committed protocol if executed. No trial is authorized merely by this literature audit or by the earlier closed CatBoost/GRU track budgets.

### TabPFN-3.5: local open weights, restrictive terms and unproven fit

Primary [model card](https://huggingface.co/Prior-Labs/tabpfn_3_5) lists September-dated checkpoints, synthetic tabular pretraining, local inference code, and custom `tabpfn-3-5-license-v1.0`. [Official model documentation](https://docs.priorlabs.ai/models) dates the family report to September 2026 and lists up to one million training rows; this is older than the requested October 9-November 8 window. The card permits research/internal evaluation but restricts commercial or production use of model, derivatives and outputs. Do not treat Apache-2.0 inference code as the weights licence, or assume competition-deliverable rights without checking the actual intended use. No weights downloaded or terms accepted here. Hosted variants are excluded from this project regardless of availability. No evidence establishes better spellF1 or acceptable CPU cost; TabICLv2 has the cleaner open-licence path.

### Freshness result and recommendation after supplements

No newly released, suitably licensed soccer H/A/D checkpoint with a clean training manifest and measured comparable spellF1 was verified in the fresh-window searches. This is a limited-search result, not proof of absence. The searches did not establish original TranSPORTmer/CropDrop runnable licensed checkpoint availability. The main useful addition is the older TabICLv2 model plus verified October maintenance, while PathCRF remains the strongest domain-specific research architecture with material evaluation/integration constraints.

Recommendation: retain production now. If the user chooses to authorize a new model track, rank (1) a bounded TabICLv2 emissions-only feasibility/benchmark protocol for ease of clean comparison, (2) a substantially larger masked player-interaction architecture effort using clean, known training provenance. Do not present either as an established improvement. Existing stop rules, strengthened promotion gate, fixed splits, sealed boundary, CPU constraint and November 13 freeze remain unchanged.
