# Run the two sequential hybrid trials

Prepared November14,2026. The assistant has not run tests, probes, inference or training. Use the same pinned environment. Commands run one numericalthread per process with up to two seedworkers. The existing TCN remains frozen. All runs must finish fitting before the start ofNovember16 Asia/Kolkata.

## Temporal preflight first

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_hybrid.py --stage temporal --preflight
```

This runs correctnesschecks, reconstructs the parent predictions, prepares fold-bound probabilitycaches, checks zero-correctionCSVidentity and measures64probeupdates per fold. It records preparationtime, fitrate, peakmemory and projectedstorage/time in experiments/tcn-hybrid-2026-11-14/preflight/temporal/report.json. It produces no probequalityscore. Report the preflight result for review before the full run. Runtime is unmeasured until this command completes.

After reviewing the preflight and confirming it fits before the freeze, run:

```sh
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_hybrid.py --stage temporal --run
```

Append `--workers 1` for serial execution. The default is `--workers 2`. Full comparison uses20fits, each40kupdates. Completed checkpoints resume with the identical command. A failed budgetprojection pauses beforefitting. Preserve errorlogs and orphanarrays for review, rather than changing settings to force progress.

## Review the complete temporal result

Full completion stops for review. Share the result, then use the explicit review command after the saved evidence has been checked:

```sh
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_hybrid.py --stage temporal --review
```

This computes the unchangedgate from savedscores and prepares reviewed-temporal.json. It does not gitcommit. The assistant audits and commits the exactrevieweddecision before graph execution. Passing temporal makes it the graphparent, otherwise graphcorrects B. Preserve all failed results.

## Graph after reviewed temporal

```sh
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_hybrid.py --stage graph --preflight
```

Review measured graphcost before proceeding. Graph preflight has the same checks and probes but uses the actual retainedparent. If its fullcomparison plus finalfit budget still fits:

```sh
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_hybrid.py --stage graph --run
```

After completion and evidence review:

```sh
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_hybrid.py --stage graph --review
```

Again, the assistant must audit and gitcommit the reviewedrecord before release. No stage starts automatically. No automatic thirdvariation follows failure. The two developmentstages require at most40newbranchfits andzeroTCNfits.

## Outputs and qualification

Per-match officialscores, allIoUthresholds, errorstrata and missing-ballquality are under experiments/tcn-hybrid-2026-11-14/evaluation/<stage>/. PredictionCSVs remain private under data/tcn-hybrid/<stage>/predictions. Weights remain private under models/tcn-hybrid. Targets/publiclabels and thetwo sealedmatches are excluded from development.

Use the separately supplied release guide after the accepteddecisions are committed. Finalbranchfits must finish beforeNovember16. Export/officialvalidator/repeatCSV/cleanenvironment/freshclone and once-onlysealedqualification follow explicitusercommands. Targetaccuracy remains unknown. Allartifacts including earliertrials share the2GiBcap/12GiBfreefloor, without automaticdeletion. A partialtrial atfreeze cannot become a releasecandidate.
