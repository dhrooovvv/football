# Export and qualify the selected final Trial-B ensemble

Prepared November14,2026. All commands below are user-run; none were executed by the assistant. This exports the already fitted two-member ensemble, without training, scoring target labels, opening sealed matches or promoting production. Target accuracy is unknown.

## First: private export

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/export_tcn_final_b.py --run
```

This runs eleven synthetic contracts first, verifies the pinned final artifact, then performs three fresh-load inference passes. Each pass uses both members and both rotation views. It validates each CSV with the unchanged official validator, requires identical bytes for batch1/reloaded batch1/batch4, and requires exact per-view probabilities across the two batch1 loads. It reads tracking/team metadata only, never target labels. No reliable runtime measurement exists for this exporter yet; it is inference only, not another training run.

Success writes `data/competition/tcn-final-b-exports/local/candidate.csv` and `provenance.json`. Keep these private. The provenance includes label-free prediction aggregates and all hashes; it contains no competition rows. H/A possession spells and H/A/D segments are reported separately. Do not submit it or replace production automatically.

If it fails, retain the terminal output and `pending-local-*`/checks evidence. Rerunning is allowed only after review and correction of the actual failure. An existing completed output is refused; no automatic overwrites or deletion.

## Second: fresh environment

Run only after the local export succeeds. These commands install pinned dependencies, not datasets. They use no pip cache and refuse pre-existing environment destinations. The new environment and clone count toward the combined2GiBartifact cap; retain at least12GiBfree. Installation itself is a third-party operation: the pre/post checks are not a hard quota or guarantee against transient installer usage. Stop if the reservation fails, installation fails, or postflight exceeds the budget; do not substitute versions or delete project assets automatically.

The currently recorded original environment is about1.2GiB. Reserve1.3GiB before setup; this is a conservative preflight estimate, not a measured size guarantee for a new install. Python/platform must match the pinned snapshot. All29 package versions are checked by export.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=experiments/tcn-final-b-export-2026-11-13 data/gru-env/bin/python -c \
  'from export_contract import check_storage, require; from pathlib import Path; require(not Path("data/tcn-final-b-clean-env").exists(), "Preserve existing environment"); print(check_storage(reserve=1400000000))'
data/gru-env/bin/python -m venv data/tcn-final-b-clean-env
data/tcn-final-b-clean-env/bin/python -m pip install --no-cache-dir \
  -r experiments/tcn-winner-release-2026-11-12/environment-lock.txt
PYTHONPATH=experiments/tcn-final-b-export-2026-11-13 data/tcn-final-b-clean-env/bin/python -c \
  'from export_contract import check_storage; print(check_storage())'
PYTHONPATH=src:scripts caffeinate -i data/tcn-final-b-clean-env/bin/python scripts/export_tcn_final_b.py \
  --run --output data/competition/tcn-final-b-exports/clean
cmp data/competition/tcn-final-b-exports/local/candidate.csv \
  data/competition/tcn-final-b-exports/clean/candidate.csv
```

Execute each command only after the preceding command succeeds. `cmp` succeeds silently on identical bytes. A new environment provides independent installed dependencies but remains the same Mac; wheel-byte identity and cross-platform reproducibility are not claimed. This does not repeat training.

## Third: fresh local clone

This copies committed code locally, without remote access. Models, target assets and the unchanged reference scorer remain private shared inputs. Only the final checks log is copied to its exact expected relative path; no training data is copied and no private data is added to Git.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
BALL_PROJECT_DIR="$PWD"
PYTHONPATH=experiments/tcn-final-b-export-2026-11-13 data/tcn-final-b-clean-env/bin/python -c \
  'from export_contract import check_storage, require; from pathlib import Path; require(not Path("data/tcn-final-b-clean-clone").exists(), "Preserve existing clone"); print(check_storage(reserve=134217728))'
git clone --no-hardlinks "$BALL_PROJECT_DIR" "$BALL_PROJECT_DIR/data/tcn-final-b-clean-clone"
cd "$BALL_PROJECT_DIR/data/tcn-final-b-clean-clone"
ln -s "$BALL_PROJECT_DIR/data" data
ln -s "$BALL_PROJECT_DIR/models" models
ln -s "$BALL_PROJECT_DIR/reference" reference
"$BALL_PROJECT_DIR/data/tcn-final-b-clean-env/bin/python" - "$BALL_PROJECT_DIR" <<'PY'
import json
from pathlib import Path
import shutil
import sys
origin = Path(sys.argv[1])
manifest = json.loads((origin / 'models/tcn-final-b/manifest.json').read_text())
for member in manifest['members'].values():
    proof = json.loads((origin / member['proof']).read_text())
    relative = Path(proof['checks_path'])
    if relative.is_absolute() or '..' in relative.parts or relative.parent != Path('experiments/tcn-final-b-2026-11-13/evaluation'):
        raise RuntimeError('Unexpected checks path')
    relative.parent.mkdir(parents=True, exist_ok=True)
    if relative.exists():
        if relative.read_bytes() != (origin / relative).read_bytes():
            raise RuntimeError('Existing checks bytes differ')
    else:
        shutil.copyfile(origin / relative, relative)
PY
PYTHONPATH=experiments/tcn-final-b-export-2026-11-13 "$BALL_PROJECT_DIR/data/tcn-final-b-clean-env/bin/python" -c \
  'from export_contract import check_storage; print(check_storage())'
PYTHONPATH=src:scripts caffeinate -i "$BALL_PROJECT_DIR/data/tcn-final-b-clean-env/bin/python" \
  scripts/export_tcn_final_b.py --run --output data/competition/tcn-final-b-exports/clone
cmp "$BALL_PROJECT_DIR/data/competition/tcn-final-b-exports/local/candidate.csv" \
  data/competition/tcn-final-b-exports/clone/candidate.csv
```

Inspect the three private provenance files: model manifest, both model/repeat hashes, export registration/input hashes, target/config hashes and CSV hash must agree. Fresh-clone commit may include later documentation-only commits if all registered source bytes remain unchanged. Preserve all three exports. Return the terminal success or error; the assistant will audit saved aggregate evidence without reading target rows.

Do not run additional model experiments automatically. Final sealed evaluation and the release decision remain separate; no actions after November17,2026.
