# Reproduce the frozen winning TCN export

Prepared November 12, 2026. These commands are for the user to run after the current-winner slot diagnostic has been reviewed, the five-IDSSE final fit has passed its repeated-fit checks, and the local export has passed. They have not been executed by the assistant. Do not use the legacy 53-match blend exporter.

This verifies frozen-model inference from the same authorized local assets. It does not independently reproduce training or establish target accuracy. Production remains unchanged until the release decision. Preserve November 16's once-only sealed evaluation and the rule that unexpected sealed results trigger investigation, never tuning.

## Prerequisites

- The reviewed diagnostic aggregates and final qualification code are committed locally. Private models and target files remain ignored.
- `models/tcn-winner-release/manifest.json` binds the repeated five-match 40k/reset fit. `data/competition/tcn-winner-local/candidate.csv` and its provenance exist from the registered exporter.
- Use the original Mac architecture and Python 3.13.15. Choose unused environment, clone and export directories; preserve any failed attempt for review.
- `--acknowledge-slot-risk` records review of the diagnostic and its unresolved transfer limitation. It is not an automatic diagnostic pass, a target-quality claim or a production switch.

## Fresh environment

The environment lock records all 29 distributions declared in the winning run's existing environment, including transitive dependencies and package tools. It was collected by reading installed metadata, without importing packages. These are version pins, not binary wheel hashes. Installation availability and numerical reproduction remain unverified until these user commands pass; do not substitute versions after a failure.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
data/gru-env/bin/python -m venv data/tcn-winner-clean-env
data/tcn-winner-clean-env/bin/python -m pip install \
  -r experiments/tcn-winner-release-2026-11-12/environment-lock.txt
PYTHONPATH=src:scripts data/tcn-winner-clean-env/bin/python scripts/export_tcn_winner.py \
  --manifest models/tcn-winner-release/manifest.json \
  --output data/competition/tcn-winner-clean \
  --acknowledge-slot-risk
cmp data/competition/tcn-winner-local/candidate.csv \
  data/competition/tcn-winner-clean/candidate.csv
data/tcn-winner-clean-env/bin/python -m pip freeze \
  > data/competition/tcn-winner-clean/environment.txt
```

The exporter checks the recorded environment, source, model and input identities, runs the unchanged official validator, and requires exact first/reload/batch-four CSV bytes. `cmp` succeeds silently when the local and fresh-environment CSV bytes agree. Retain both provenance files and the environment record. An installation or output mismatch is a failed qualification step, not permission to alter the model.

## Fresh local clone

This uses committed code from a new local checkout. Authorized private assets are linked locally; nothing is uploaded and no remote is contacted. It is a fresh code checkout with shared frozen inputs, not a new data acquisition or full training rebuild.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
BALL_PROJECT_DIR="$PWD"
git clone --no-hardlinks "$BALL_PROJECT_DIR" "$BALL_PROJECT_DIR/data/tcn-winner-clean-clone"
cd "$BALL_PROJECT_DIR/data/tcn-winner-clean-clone"
ln -s "$BALL_PROJECT_DIR/data" data
ln -s "$BALL_PROJECT_DIR/models" models
ln -s "$BALL_PROJECT_DIR/reference" reference
PYTHONPATH=src:scripts "$BALL_PROJECT_DIR/data/tcn-winner-clean-env/bin/python" \
  -m unittest discover -s tests -q
PYTHONPATH=src:scripts "$BALL_PROJECT_DIR/data/tcn-winner-clean-env/bin/python" \
  -m unittest discover -s experiments/tcn-winner-release-2026-11-12/tests -q
PYTHONPATH=src:scripts "$BALL_PROJECT_DIR/data/tcn-winner-clean-env/bin/python" \
  scripts/export_tcn_winner.py \
  --manifest models/tcn-winner-release/manifest.json \
  --output data/competition/tcn-winner-clone \
  --acknowledge-slot-risk
cmp "$BALL_PROJECT_DIR/data/competition/tcn-winner-local/candidate.csv" \
  data/competition/tcn-winner-clone/candidate.csv
git rev-parse HEAD > data/competition/tcn-winner-clone/clone-commit.txt
```

Review provenance across all three exports: identical checkpoint, registration, configuration, target input and CSV hashes are required. Export directory names and timing fields can differ. Keep logs private; share aggregate pass/fail and hashes rather than target rows. The assistant will inspect the saved evidence after completion.

## What remains separate

Two identical final fits in the original environment verify training repeatability there. A complete training reproduction from raw external inputs in a fresh environment is a separate, longer user run and is not claimed by these export commands. Sealed clean/corrupted evaluation, the permitted final public-window correctness check, technical-document completion and the final release decision remain distinct steps. No further action after November 17, 2026.
