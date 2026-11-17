# Final selected two-member ensemble

This fits the approved Trial B recipe on the five permitted development matches, with no held-out quality evaluation. The two sealed matches, PFF and target remain excluded. All runtime is yours. Protocol/source/input locks must be committed before execution.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/fit_tcn_final_b.py --run
```

Correctness checks run first, then two one-thread workers train the two existing seeds. Each40k member is fitted twice exactly:fourfits total. Same short-spell sampler and segment loss as B; no new experiment. Keep plugged in/lid open, terminal alive. Worker logs under experiments/tcn-final-b-2026-11-13/evaluation/; every1000updates saves resumable progress. Ctrl-C stops children; rerun samecommand toresume. Do not edit sources/preparedinputs, run duplicate jobs or start othermodel work. --workers1 serializes the identicalbudget. No RAMcap. Combinedoldmissed+newartifactbudget2GiB/12GiBfreefloor, no downloads/deletions.

Previous20-fitBwork sums5h52m;fourfits imply about70minutes summedwork beforeoverhead, notelapsedguarantee. Twojobs sharememory/thermals; expectactualtimingfromlogs. Trainingblockedon/afterNov16start, preservingpartialcheckpoints.

When finished send “Final ensemble done.” Manifest models/tcn-final-b/manifest.json binds both members/repeatproofs, recipe, environment and source/data hashes. This adds NO new quality score. SelectedBcleanmean65.04%,corrupt50.98%; A retains highercorruptmean51.35%. No targetaccuracyknown or automaticproductionswitch.

Do not use the old original-TCN fit/export commands for this ensemble. After artifactaudit we prepare its private export/officialvalidator/identicalCSV/cleanenvironment checks and once-onlysealed evaluationatfreeze. No external submission/push.
