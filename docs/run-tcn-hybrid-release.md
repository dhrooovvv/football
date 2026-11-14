# Qualify the retained hybrid for delivery

Prepared November14,2026. These commands are for the user. All tests, fits, inference and scoring are currently unexecuted by the assistant. Complete and review development stages using docs/run-tcn-hybrid.md first. Retained branch decisions and results must be committed before final fitting.

## Final five-match fit

Use `--through temporal` after the temporal stage review if graph work cannot fit before the freeze. Use `--through graph` after the graph stage review. The decision files determine which branches qualified. A rejected branch is omitted, and every retained branch uses the identical registered recipe on exactly the five permitted development matches.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/release_tcn_hybrid.py --fit --through graph
```

Each included branch fits both seeds twice, four40kfits, with exact state/optimizer/RNG/loss equality. Final fitting is serial with one numerical thread per process. The runner recomputes remaining serial final work from the user-measured stage preflights and requires its1.5safety-factor projection to fit before November16. That estimate supplies no runtime guarantee. The date guard is checked throughout training. Use the identical command to resume interrupted final fits. This reuses final B weights and adds zero new TCN fits.

Success writes `models/tcn-hybrid/final/manifest-graph.json`. A temporal-only command writes `manifest-temporal.json`. Return completion for review of the final weights/proofs before export. The all-five fit adds no independent quality score.

## Private export

After saved-artifact review, use the same `--through` value used for the final manifest.

```sh
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/release_tcn_hybrid.py --export --through graph
```

Success writes `data/competition/tcn-hybrid-exports/local/candidate.csv` and private provenance. The unchanged official format validator must pass on each of three fresh-load passes. Reload probabilities must be exact and CSV bytes must agree for first/reload/batch4. Outputs preserve full-frame numbering and X outside graded blocks. Existing outputs are refused. Preserve pending directories and logs on failure. Target labels are never scored by export.

## Clean environment and fresh local clone

Run only after local export succeeds. The existing final-B clean environment may be reused if all29version/platform pins match. If it does not exist, the following commands create a new pinned environment. Its files and clone count toward the combined2GiBceiling. Pre/post storage checks are required. Pip installation can use temporary storage beyond a preflight estimate, so installation itself is not a hard quota. Use no cache and execute each line only after the preceding line succeeds.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=experiments/tcn-hybrid-2026-11-14 data/gru-env/bin/python -c \
  'from hybrid_contract import check_storage,require; from pathlib import Path; require(not Path("data/tcn-hybrid-clean-env").exists(), "Preserve existing environment"); print(check_storage(reserve=1400000000))'
data/gru-env/bin/python -m venv data/tcn-hybrid-clean-env
data/tcn-hybrid-clean-env/bin/python -m pip install --no-cache-dir \
  -r experiments/tcn-winner-release-2026-11-12/environment-lock.txt
PYTHONPATH=experiments/tcn-hybrid-2026-11-14 data/tcn-hybrid-clean-env/bin/python -c \
  'from hybrid_contract import check_storage; print(check_storage())'
PYTHONPATH=src:scripts caffeinate -i data/tcn-hybrid-clean-env/bin/python \
  scripts/release_tcn_hybrid.py --export --through graph --output-tag clean
cmp data/competition/tcn-hybrid-exports/local/candidate.csv \
  data/competition/tcn-hybrid-exports/clean/candidate.csv
```

If reusing `data/tcn-final-b-clean-env`, omit installation and replace the interpreter path in the export command. Do not create both environments merely to repeat the same qualification.

The fresh clone uses committed source and private shared data/models/reference. Small runtime metadata and checks logs are copied locally so their pinned paths remain valid. No assets are uploaded.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
BALL_PROJECT_DIR="$PWD"
PYTHONPATH=experiments/tcn-hybrid-2026-11-14 data/tcn-hybrid-clean-env/bin/python -c \
  'from hybrid_contract import check_storage,require; from pathlib import Path; require(not Path("data/tcn-hybrid-clean-clone").exists(), "Preserve existing clone"); print(check_storage(reserve=134217728))'
git clone --no-hardlinks "$BALL_PROJECT_DIR" "$BALL_PROJECT_DIR/data/tcn-hybrid-clean-clone"
cd "$BALL_PROJECT_DIR/data/tcn-hybrid-clean-clone"
ln -s "$BALL_PROJECT_DIR/data" data
ln -s "$BALL_PROJECT_DIR/models" models
ln -s "$BALL_PROJECT_DIR/reference" reference
"$BALL_PROJECT_DIR/data/tcn-hybrid-clean-env/bin/python" - "$BALL_PROJECT_DIR" <<'PY'
import json
from pathlib import Path
import shutil
import sys
origin = Path(sys.argv[1])
root = Path('experiments/tcn-hybrid-2026-11-14')
for name in ('evaluation', 'preflight', 'release'):
    source = origin / root / name
    if source.exists():
        shutil.copytree(source, root / name, dirs_exist_ok=True)
manifest = json.loads((origin / 'models/tcn-final-b/manifest.json').read_text())
for member in manifest['members'].values():
    proof = json.loads((origin / member['proof']).read_text())
    relative = Path(proof['checks_path'])
    if relative.is_absolute() or '..' in relative.parts or relative.parent != Path('experiments/tcn-final-b-2026-11-13/evaluation'):
        raise RuntimeError('Unexpected frozen final-B checks path')
    relative.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origin / relative, relative)
PY
PYTHONPATH=experiments/tcn-hybrid-2026-11-14 "$BALL_PROJECT_DIR/data/tcn-hybrid-clean-env/bin/python" -c \
  'from hybrid_contract import check_storage; print(check_storage())'
PYTHONPATH=src:scripts caffeinate -i "$BALL_PROJECT_DIR/data/tcn-hybrid-clean-env/bin/python" \
  scripts/release_tcn_hybrid.py --export --through graph --output-tag clone
cmp "$BALL_PROJECT_DIR/data/competition/tcn-hybrid-exports/local/candidate.csv" \
  data/competition/tcn-hybrid-exports/clone/candidate.csv
```

When reusing the final-B clean interpreter, replace all `tcn-hybrid-clean-env` interpreter paths consistently. Local/clean/clone manifests, branch/checkpoint/source/input hashes and final CSV hash must agree. This qualifies frozen inference from shared authorized assets. Full training reproduction in a fresh environment is a separate longer computation and is not claimed by these commands.

## Once-only sealed evaluation at freeze

The interpretation rule is prospective. A sealed result far below development or below the supplied smoothing50baseline triggers investigation for implementation or transfer problems. Sealed results cannot select A/B, tune the hybrid, choose a smoothing width or modify any parameter. All four supplied widths are reported together.

On November16or17only, after final artifact qualification, execute once for the frozen selected manifest.

```sh
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/release_tcn_hybrid.py --sealed --through graph
```

The runner locks one manifest and two sealed match identities, J03WQQ/J03WR9, hashes raw files at first permitted access, and evaluates clean and the frozen target-like burst model. Fixed new independent corruption seeds20261206/20261207are preregistered for these previously unused matches. Raw ball positions are masked before features. The supplied baseline logic is applied at widths0/25/50/125within real halves. The candidate and all baselines use the unchanged official scorer.

Completed per-match reports are hash-bound and resumed only for unfinished matches under the same frozen identity. A completed evaluation is reported from saved evidence. No automatic rerun, new model, target-public score, publication or submission follows. No actions after November17. Append all reviewed outcomes and failures to ball.md, state mirrors and the technical report.
