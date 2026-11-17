# Run the two independent TCN comparisons

Prepared November12,2026. These commands are for the user to execute only after the new protocol, sources, membership and fingerprints are committed. The assistant has not executed tests, imports, compilation, model inference, scoring or training. Neither job reads competition assets, public labels, sealed matches or PFF data. Production and the current qualified model remain unchanged.

## Two terminals

In **Terminal1**, run the single attention-pooling change:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_parallel.py --arm attention --run
```

In **Terminal2**, run the second-seed equal-weight ensemble comparison:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_parallel.py --arm ensemble --run
```

Each process fixes Torch intra-op/inter-op and numerical-library thread limits to one. Two active fits therefore request two compute threads in total, not one shared core. This does not pin processes to particular CPU cores. The observed Mac has18GiB and11logical cores; concurrent processes still share RAM, caches, memory bandwidth and cooling. No custom RAM cap is imposed. Two jobs need not finish twice as fast as sequential jobs. Do not rebuild prepared inputs or start other model jobs while these run.

The ensemble arm costs ten new40k fits: five held-out folds, each repeated identically. Prior repeat-pair training took about33minutes, giving roughly three hours sequential single-arm planning cost including overhead; it is not a measured guarantee for this job. Attention computes pairwise weights and may be substantially slower; its runtime and peak RAM are unmeasured. Concurrency can lengthen either estimate. Each arm contains400k new optimizer updates; together800k. Exactly20new fits are planned. No sweep or automatic follow-up is included.

Both jobs run correctness checks first, then reconstruct all ten frozen parent CSVs and metrics before the first new fit. Each fold trains exactly the other four development matches, with20k updates, reset Adam/window/view RNGs, then20k updates. The attention arm changes pooling only. The ensemble arm changes model initialization seed only, retains the original sampler/view seeds, and averages its probabilities50/50 with the frozen first-seed model. Identical repeat fits are determinism evidence, not ensemble members. Existing all-five final weights are never used for held-out evaluation.

Checkpoints are saved every1000updates under models/tcn-parallel/ARM/MATCH/{first,repeat}/progress.pt. An interrupted, identical-source run can resume using the same command. Preserve failure evidence; do not change settings or delete a completed record to bypass a mismatch. Same-arm locking prevents duplicate jobs; shared input locks allow both read-only jobs and block existing exclusive input writers. Model/check, prediction and result paths are separate by arm.

Keep this checkout and prepared inputs unchanged while either job is active. If one errors, preserve its output and report it before editing or rerunning; a source correction must account for the other job's frozen registration. A failure in one arm does not justify silently changing the other arm's experiment.

## Review and ordered finalization

Each arm writes per-match clean/corrupted results and its frozen-parent screening gate under experiments/tcn-parallel-2026-11-12/evaluation/ARM/. Reports include spell precision/recall/F1 at each official IoU threshold, missed/spurious and short-spell diagnostics, boundary shifts, missing-ball dead/live quality and runtime evidence. Private CSVs stay under data/tcn-parallel/ARM/predictions/.

After **both** jobs finish, run this separate command; it does no training:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_parallel.py --finalize --run
```

Finalization verifies both complete result sets, models and CSV fingerprints. It applies the preregistered order: attention versus the frozen parent first; ensemble then versus attention if attention passed, otherwise versus the parent. This prevents two independent parent screens from choosing an inferior candidate by a favorable mean. Full original promotion rules remain: positive median paired spell change, improvement on at least3/5 matches, median paired macro drop no worse than.01, median corrupted spell gain at least.01, and passing contracts/exact repeats. No automatic production switch occurs.

No attention-plus-ensemble mixture is tested or inferred from these jobs. Stop after these two fixed comparisons and send “done” for audit. The five repeatedly reused matches do not supply independent target-accuracy evidence. No new research starts on/after November16; protected evaluation remains once at the freeze, without tuning. No dataset downloads, hosted processing, publication or submission occurs.
