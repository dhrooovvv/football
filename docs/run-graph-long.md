# Longer graph training — direct user-run command

Prepared November15,2026. This trains the graph correction branch of the hybrid; the selected Trial-B TCN stays frozen. Fixed50k cumulative graph updates per fit, continuing each archived40k fit for10000more updates with optimizer/random states preserved. Same architecture/loss/decoder/splits/seeds; four independent jobs, one numerical thread each.20continuations including exact repeats, no dataset download.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_graph_long.py --run
```

This single command checks committed fingerprints, pinned environment, freeze-time/storage admission and37original+6new synthetic contracts before launching training. No checks or training were run by the assistant. It automatically scores clean and frozen targetlike development cases, compares the full TCN+graph hybrid against frozen TCN alone with the unchanged gate, and stops for review. It also shows the previous40k graph scores. This is not standalone graph classification and not TCN retraining.

Plan roughly3–4hours for development continuation and scoring based on earlier speeds, not a measured guarantee for this runner. The conservative admission reserves about8hours including possible later final fitting. It refuses if complete comparison plus that reserve cannot fit before November16start; no hidden freeze extension. Caffeinate prevents idle sleep while running; do not close the lid, manually sleep the Mac or power it off.

Progress/logs: experiments/graph-long-2026-11-15/logs/. Checkpoints: models/graph-long-2026-11-15/. Results: experiments/graph-long-2026-11-15/evaluation/report.md, results.json, gate-v2.json and completion.json. Interrupted runs resume with the same command, subject to remaining freeze/storage budget. Original models/logs are preserved. Keep12GiBfree; combined research artifact ceiling2GiB/new allowance512MiB. No automatic deletion.

After completion report “done” for review. There is no automatic60k/80k trial, final fitting, target export, submission or production replacement. If the candidate qualifies, a separately prepared final50k fit/export must still complete before freeze. Otherwise retain selected Trial B. Target-match accuracy remains unknown.
