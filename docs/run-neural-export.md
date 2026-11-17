# Local neural candidate export and reproduction

Run these steps **after the expanded training command has finished** and `experiments/tcn-expanded-2026-11-10/final-model.json` exists. The five-match development gate must be reviewed before selecting this model. Export is permitted as a format diagnostic even if the gate fails, but the artifact remains research-only. No production switch occurs.

Only the TCN is trained in the current job. This exporter combines its final checkpoint with the existing frozen CatBoost model at the registered 50/50 probability weights, followed by penalty 16. It does not train either model. No competition labels or score are used.

The commands below are supplied for the user to execute. They have not been run by the assistant. Each export makes three inference passes on the target match, using CPU one thread: initial load, checkpoint reload, and batch-size four. Exact CSV bytes must agree; every CSV goes through the unchanged official format validator. Runtime has not been measured. Do not start this alongside the current training job.

## 1. Export in the current environment

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/export_neural_candidate.py \
  --manifest experiments/tcn-expanded-2026-11-10/final-model.json \
  --output data/competition/neural-check-local
```

The new private directory contains `candidate.csv`, two repeat CSVs and `provenance.json`. Existing directories are refused to preserve evidence. The exporter fingerprints the model, frozen CatBoost, local inputs and configuration without printing input rows. It checks the 53-match membership, budget, seed and recorded repeated-fit proof. A failed check requires review; preserve the error rather than changing settings.

## 2. Repeat in a clean environment

Use the same Python minor version and Mac architecture as the training environment. Dependencies are pinned to the recorded research versions; availability of a fresh installation has not yet been checked. Keep installation logs local. Do not change versions to work around a failure without review.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
data/gru-env/bin/python -m venv data/neural-release-env
data/neural-release-env/bin/python -m pip install \
  -r experiments/neural-export-2026-11-11/requirements.txt
PYTHONPATH=src:scripts data/neural-release-env/bin/python scripts/export_neural_candidate.py \
  --manifest experiments/tcn-expanded-2026-11-10/final-model.json \
  --output data/competition/neural-check-clean
cmp data/competition/neural-check-local/candidate.csv \
  data/competition/neural-check-clean/candidate.csv
```

`cmp` exits successfully with no output when bytes agree. Installing the five direct pins does not lock every transitive dependency; record the resolved environment as well:

```sh
data/neural-release-env/bin/python -m pip freeze > data/competition/neural-check-clean/environment.txt
```

## 3. Repeat from a fresh local clone

This is a **local** clone of the committed code, with symlinks to authorized private assets. No upload, external submission or remote push. It tests fresh code checkout plus frozen-model inference, not independent asset download. Run only after the previous commands succeed. The clone destination must not exist.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PROJECT_DIR="$PWD"
git clone --no-hardlinks "$PROJECT_DIR" "$PROJECT_DIR/data/neural-release-clone"
cd "$PROJECT_DIR/data/neural-release-clone"
ln -s "$PROJECT_DIR/data" data
ln -s "$PROJECT_DIR/models" models
ln -s "$PROJECT_DIR/reference" reference
ln -s "$PROJECT_DIR/experiments/tcn-expanded-2026-11-10/final-model.json" \
  experiments/tcn-expanded-2026-11-10/final-model.json
PYTHONPATH=src:scripts "$PROJECT_DIR/data/neural-release-env/bin/python" \
  scripts/export_neural_candidate.py \
  --manifest experiments/tcn-expanded-2026-11-10/final-model.json \
  --output data/competition/neural-check-clone
cmp "$PROJECT_DIR/data/competition/neural-check-local/candidate.csv" \
  data/competition/neural-check-clone/candidate.csv
```

Retain all three provenance files. Compare their checkpoint, input, configuration and CSV hashes. The clean environment and clone are unverified until these commands pass.

## Interpretation and remaining checks

This workflow verifies frozen-model export, official CSV format, class order, X outside the configured blocks, and byte equality. It does not estimate target accuracy, certify target player-slot identity through time, or reproduce training in a clean environment. The expanded runner's repeated training proof is within its original environment. Full training reproduction is a separate hours-long user run.

Target temporal slot continuity remains an unresolved adapter property. The existing encoder assumes a slot describes the same player over adjacent observed frames when calculating velocity. Format/team checks alone do not prove that property. No neural candidate is release-ready solely because these export checks pass. The original CatBoost production output remains in place. Sealed evaluation follows the frozen plan; neither sealed IDSSE nor PFF transfer matches are loaded here.
