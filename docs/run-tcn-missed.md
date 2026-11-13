# User commands: missed-possession trials

Prepared November13,2026. Source/protocol/fingerprints must be committed first. All tests and model execution remain user-owned. Old reports/scorer unchanged, no datasets downloaded, no competition or protected matches read.

## Start Trial A

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_missed.py --trial a --run
```

This runs correctness checks, reconstructs all ten parent ensemble CSVs, then two one-thread seed jobs concurrently (five folds/two exact40k fits each), followed by ensemble evaluation.20fits total. The previous ten-fit seed job took3h07m; twice that work is a planning reference, not a guarantee. No RAM cap. Use --workers 1 only to serialize these same jobs. Do not run separate copies; isolated operation/seed locks reject duplicates. Keep registered sources and inputs unchanged. Progress is under experiments/tcn-missed-2026-11-13/evaluation/a/worker-SEED-TIMESTAMP.txt; checkpoint every1000updates. Ctrl-C stops child jobs, same command resumes. Checks are repeated on resume. New artifacts limited2GiB; pause if free would fallbelow12GiB; never delete old evidence automatically.

When complete, send “Trial A done” for review. Do not start B yet.

## Prepare the pending A review (no training)

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_missed.py --review-a --run
```

This verifies saved model/CSV/fit/metric hashes and creates pending-review-a.json. It does not make the review effective. After independently checking completed A evidence, the assistant records the decision, copies its exact reviewed content to reviewed-a.json and commits it with results. B refuses a missing, stale, uncommitted or inconsistent review. Do not copy/edit the decision to bypass a failed gate.

## Trial B, only after committed A review

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_missed.py --trial b --run
```

Same20fit budget and two workers; it retains A's sampler only if A passed, otherwise uniform. Only loss changes. It binds the committed decision and selected parent fingerprints. Stop afterB and report completion. Do not expect any automatic production switch or final-all-five training. No research on/afterNovember16; unfinished checkpoints are preserved.

## Interpretation

policy-v2.json explicitly reinterprets the completed ensemble under the newly authorized positive-median gate; original failed-gate reports remain unchanged. Baseline means .633872006clean/.506191099targetlike corrupted; target accuracy unknown. Reports give all five development matches and both conditions, not independent generalization. Official unchanged scorer, masks, gap views, splits, decoder16, rotation and seed averaging remain. There is no promised80% or automatic third trial.
