# Main pipeline preparation

Run from repository root, with numpy/pandas installed (requirements-pipeline.txt). Existing audit/.venv is usable.

```
PYTHONPATH=src audit/.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src audit/.venv/bin/python scripts/prepare_data.py --root data/competition
PYTHONPATH=src audit/.venv/bin/python scripts/prepare_features.py --root data/competition
```

Only for a new empty destination, add `--archive /path/to/Archive.zip` to prepare_data.py. It refuses to overwrite existing files. Real data/reports stay in ignored data/. Never copy their contents into hosted-model context. Optional `--source tactical` or `--source broadcast` limits validation; do not repeat unchanged blocked checks.

prepare_features requires tactical ATD metadata and writes label-free feature arrays, not predictions. It does not yet train or load a classifier. Smart Tagging intervals/hints are kept separate; published phases are not possession labels. Broadcast is a different timeline and currently fails the homography numeric gate. No broadcasting alignment or fallback model is implemented.
