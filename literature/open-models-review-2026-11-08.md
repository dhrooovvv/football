# Open-model decision review, November 8, 2026

## Decision and evidence standard

No audited replacement has demonstrated a higher project spellF1 than production. Keep nine core masked features, unaugmented CatBoost and Viterbi penalty 16. This is a research audit, not a model comparison or permission to reopen a completed experiment track. No training, inference, target-label access or sealed evaluation was performed.

The last30days engine ran once over October 9–November 8, with an explicit soccer-possession plan, no browser cookies and no private input. It returned 14 items: nine Reddit, three Hacker News and two GitHub. Social results were predominantly unrelated to possession inference. Reddit direct requests were blocked, archive requests partially failed, Polymarket was unreachable, YouTube returned no items, and X was not enabled. These limits prevent a comprehensive claim that no newer model exists. GitHub entries dated November 8 are observations of existing repositories, not verified releases that day. Earlier library findings were historical context only.

Evidence files: `open-models-2026-11-08-engine.txt`, corresponding `.log`, and `open-model-primary-audit-2026-11-08.md`. The primary audit pins repository revisions and records the limits of checkpoint provenance. Community popularity is not evidence of higher possession spellF1.

## Candidates

| Candidate | Verified availability | Relevant capability | Admission problem | Decision |
|---|---|---|---|---|
| TabICLv2, ICML 2026 | BSD-3-Clause code and public classifier weights | Local probability prediction over the existing nine columns; synthetic pretraining | CPU cost and deterministic output untested at our scale; generic tabular benchmarks do not establish spellF1 gain | Most immediately reusable new-to-this-audit pretrained classifier lead, feasibility only |
| PathCRF, KDD 2026 | MPL-2.0 code and five checkpoint variants listed in public tree | Infers player possession paths from player trajectories without ball coordinates | Supplied wrapper requires known live episodes and complete selected player features; checkpoint split overlaps this project's evaluation corpus | Strongest auditable lead, but existing weights are unsuitable for an independent comparison |
| TranSPORTmer, ACCV 2024 | Original paper; MPL-2.0 adaptation in PathCRF | Masked socio-temporal attention, imputation and semantic states in original paper | Original licensed runnable model/checkpoints not verified; adaptation is not the original four-state model and has no matching published checkpoint in inspected tree | Best architectural lead for masked player interactions, with benefit unmeasured |
| BallRadar, KDD 2023 | Public training implementation | Possessor classifier followed by ball reconstruction | Root project licence and downloadable pretrained weights not established in inspected tree | Lower priority until permission and checkpoint provenance are established |
| CropDrop / masked multimodal pre-training, WACV 2026 | Research paper | Fuses player positions, types and local image crops | Public runnable licensed code/weights not verified; proprietary data excludes out-of-play sequences | Literature context, not an available replacement |

Primary references: [PathCRF paper](https://arxiv.org/html/2602.12080v2), [PathCRF repository](https://github.com/hyunsungkim-ds/pathcrf), [TranSPORTmer paper](https://arxiv.org/html/2410.17785v2), [BallRadar repository](https://github.com/hyunsungkim-ds/ballradar), [CropDrop paper](https://arxiv.org/html/2512.19528v1). Reported event F1, possessor accuracy, state accuracy and ball-position error are different metrics from our unchanged H/A/D spell scorer. None of these results establishes a gain against our CatBoost parent.

### Additional tabular lead, not a new soccer release

[TabICLv2 official repository](https://github.com/soda-inria/tabicl) and [model card](https://huggingface.co/jingang/TabICL) establish public code/weights, BSD-3-Clause licensing and a classification interface. The authors report broad tabular benchmark gains over tuned CatBoost; those are author-reported results on other tasks, not possession or spellF1 evidence. Large contexts favor GPU execution/offloading, while this project requires CPU. Checkpoint identity, local memory/time, fold-only conditioning, missing values, fixed seeds, internal ensembles/temperature and byte reproducibility would have to be locked before any comparison. No weights were downloaded or run. The February checkpoint and October 27 repository maintenance activity are not evidence of an October soccer model release.

TabPFN was also checked through its [official repository](https://github.com/PriorLabs/TabPFN). Local execution exists, but default CPU context limits and separate model usage terms make it less straightforward for this CPU, many-frame project. Code licence and weight licence are separate. Hosted inference is excluded by project rules. No conclusion about relative possession accuracy follows from this feasibility ranking.

## Critical checkpoint finding

PathCRF revision `1b7c6f85a6b78c92e4543fde72ca2b86a933f997` publishes `saved/140/args.json` with Sportec, LOMOCV and fold index 6. Its current training code sorts filenames, uses index 6 for test and index 5 for validation, and excludes both from fitting. With the canonical seven filenames listed in its public tree, this implies fitting on our five development matches, validation on sealed J03WQQ and test on sealed J03WR9. This is conditional on that directory being the actual training input: an exact contemporaneous checkpoint training manifest and hashes were not established. Do not claim either sealed match was fitted; do not claim the checkpoint is uncontaminated. Metadata and filenames only were inspected, with no sealed observations or labels opened and no weights loaded.

## What could address the actual failure

Inference, not an experimental result: a model that retains masked per-player spatial context is more directly aimed at long missing-ball intervals than another classifier over the same nine columns. In `src/possession/core.py`, missing ball coordinates remove both nearest distances, their margin, speed and edge distance; the nearest-distance observation indicators also become zero. A generic tabular replacement cannot recreate the discarded player configuration from these columns. Temporal context may help, but the one fixed GRU blend already failed its gate; that result does not test all spatial attention models.

A future explicitly authorized track has two distinct options: a lower-integration TabICLv2 feasibility check over the unchanged nine columns, or a larger masked spatial-model implementation. The latter first needs a label-free player-coverage and identity-continuity contract, an H/A/D output that does not use true live segmentation, and an overlap-free training/checkpoint manifest. Either performance comparison needs its own committed protocol and an explicit amendment to the completed bounded research budget; it is not a routine implementation of this audit. No expected metric gain or training cost has been measured. Preserve existing splits, strengthened gate, stop rule, November 13 freeze and November 14–16 delivery period.

## Evidence fingerprints

- `open-models-2026-11-08-engine.txt` SHA256 `be29847cf62c28630f63a5c6cb0669e4e48c3c4578074df79203d27b5eb0499b`
- `open-models-2026-11-08-engine.log` SHA256 `4857be16a5e70a9289547a07c9ce507f376d3aa647ff96de156786c1a8049894`
- `open-model-primary-audit-2026-11-08.md` SHA256 `89f35fb99394088a12a0a5465064d106d7efdee6d54f95dbe76ba00e2752cf90`
