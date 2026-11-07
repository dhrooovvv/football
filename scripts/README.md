# Phase one: main learned pipeline

Run from repository root in a Python environment with requirements-pipeline.txt installed. Current tested runtime: Python 3.13, CatBoost 1.2.10, numpy 2.5.4, pandas 3.1.1.

## Reproduce selected candidate

```
PYTHONPATH=src audit/.venv/bin/python scripts/predict_core.py
```

Uses the locked development caches and selection.json, trains the final model on the five development matches, loads local tactical inputs, writes data/competition/predictions/candidate.csv, reloads the saved model and regenerates predictions to candidate-repeat.csv. Requires identical bytes. No sealed data or target labels are opened. This is a development-selected candidate, not a sealed evaluation or submission.

## Rebuild development baseline

```
python3 scripts/fetch_external.py
PYTHONPATH=src audit/.venv/bin/python scripts/run_core.py --prepare
PYTHONPATH=src audit/.venv/bin/python scripts/run_core.py
PYTHONPATH=src audit/.venv/bin/python scripts/run_core.py --penalty 8 --tag penalty8
PYTHONPATH=src audit/.venv/bin/python scripts/report_development.py penalty8 core
PYTHONPATH=src audit/.venv/bin/python -m unittest discover -s tests -v
```

Existing model/cache files are reused; for a deliberate full rebuild move models/core and data/external/prepared to a separate archive first. Do not change budget/features and reuse old caches/models. Protocol and actual IDs: experiments/core-development/protocol.md and split.json. Source provenance: data/external/manifest.json. DFL dataset CC-BY4.0 attribution: Deutsche Fußball Liga; Bassek et al. Scientific Data 12,195 (2025), https://doi.org/10.1038/s41597-025-04505-y . Labels use provider possession1=Home,2=Away; ballstatus0=Dead,1=Alive. Unknown labels are excluded and break evaluated spells; this is a provider-label proxy for the competition semantics.

The core has nine columns: H/A nearest distances, signed margin, observed ball displacement speed, signed pitch-edge distance, ball/H-distance/A-distance observation masks, ball gap age. Half boundaries reset speed/gaps/decoding. No supplied speed unit assumptions, Smart Tagging, visual features or identity inference. Target input remains under ignored data/.

## Gated experiments

Each change needs its own committed protocol before execution. Compare against selection.json current best, identical folds/seeds/budget. Score clean and fixed burst-corrupted inputs. Per-match mean over the two conditions drives the gate, with both conditions also reported separately. Positive median paired spellF1, majority matches improve, median macroF1 delta >= -.01, tests pass. Stop after three consecutive rejections; do not add unsupported candidates.

The rejected mean-speed experiment is archived in experiments/core-development/rejected_mean_speed.py. To reproduce only: run_core.py --prepare --extra, then --extra --penalty 8 --tag mean-speed. The rejected short-turnover experiment uses --penalty 8 --team-penalty 4 --tag short-turnover. Neither is part of target prediction.

## Input checks

prepare_data.py validates extracted files; prepare_features.py is the earlier ingestion-feature utility, not the selected nine-column model input. predict_core.py computes selected core features directly. Optional broadcast homography failed validation and is excluded.


## November7 finalization
Selected production is unaugmented nine-core CatBoost+penalty16. Rolling whole-pitch bundle rejected, archived under experiments/whole-pitch; do not add it to production. Final CSV regenerated and identical across two full runs plus clean-venv raw-input rebuild. See docs/technical-report.md for fresh-environment commands and experiments/whole-pitch/reproduction.json for hashes. predict_core.py accepts --cache, --outdir and --model-path for isolated runs. Full transitive dependency pins: experiments/whole-pitch/clean-environment-lock.txt. Default production paths remain unchanged. No target labels or sealed matches required.


## Fresh-clone preparation (November7 extension)
Install experiments/whole-pitch/clean-environment-lock.txt in a Python3.13 venv. Arrange the private tactical files under data/competition/tactical (not Git), then run:

```
python scripts/fetch_external.py
PYTHONPATH=src python scripts/prepare_training_inputs.py
PYTHONPATH=src python scripts/predict_core.py
```

Only five external development matches are fetched. Preparation and target prediction need no organizer evaluation tree. The last line is the regeneration command once inputs are prepared. Official validation/research scoring additionally require the unchanged organizer starter evaluation code, kept outside public source. No sealed matches downloaded. New freezeNovember13; November14–16 delivery only.
