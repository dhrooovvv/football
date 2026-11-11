# Run the fixed longer-context TCN trial

This experiment extends learned context from17encoded samples to325 (about13seconds). It returns to the retained IDSSE-only gap-trained parent. The PFF/data-expansion track stays stopped. Five original development matches are evaluated leave-one-match-out; every fit trains on the otherfour. Two sealed matches remain excluded.

Architecture: original object encoder and team pooling, temporal dilations1/4/12/36/108,15,843parameters (+6,208). Crop526frames/halo163, while preserving the exact original250-frame anchor sampling and central200supervised positions. Same20kupdates/batch8/gapviews/seeds/optimizer, fixedCatBoost50/50blend and penalty16. The gate reference remains .592502clean/.428386corrupted, not a failed expanded model. Protocol: experiments/tcn-context-2026-11-11/protocol.md.

**No tests, compilation, inference or training have been executed by the assistant.** Independent source review is not a test pass. Run the small contracts first:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_context.py --check
```

If they pass, run the full comparison:

```sh
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_context.py --run
```

This is a substantial run: **rough planning range4–8hours**, not a measured runtime. Larger crops and more temporal layers cost more than the previous roughly90–100minutes of recordedfoldstages. Dilationkernels, disk/systemload, thermal behavior and sleep may change elapsedtime. Keep the Mac powered and allow the job to finish before beginning other dataset runs. CPU uses one thread/interopone, deterministic settings, no custom RAM cap. PeakRAM is unmeasured. Existing five compact inputs are reused; no new datasets or preparation are needed.

Progress checkpoints every1000updates include optimizer and all RNG states. Repeating the same command can resume compatible checkpoints after reviewing an interruption. Never delete failed evidence or change scientific settings to bypass a contract. Old compact-data operations are locked out while this runner is active. Code/source and prepared-input hashes, the five prepared manifests/arrays, evaluation inputs, CatBoost emissions and parent CSVs must match registration.

The command performs two full20kfits per fold for exact weights/loss/count agreement, checkpoint reload probability checks, and identical CSVbytes across initial/reloaded/batch4 inference. It reports full-matchclean and frozen-targetlike-corrupted metrics using the unchanged scorer. It ends after the fivefold comparison, with no all5finalfit, targetexport, protected-match evaluation, external submission or production switch.

Outputs:

- experiments/tcn-context-2026-11-11/checks.txt — user-run correctness logs.
- experiments/tcn-context-2026-11-11/evaluation/report.md — all ten match/condition scores and gate.
- experiments/tcn-context-2026-11-11/evaluation/results.json — metrics, error taxonomy and missing-ball quality.
- experiments/tcn-context-2026-11-11/decision.json — provisional eligibility and unchanged production status.
- models/tcn-context/evaluation/ — private resumption checkpoints.
- data/tcn-context/predictions/ — private repeat CSV evidence.

Send the result for review when finished. Keep the candidate only under the unchanged gate, including median corrupted spellF1 gain>=+.01, positive medianpairedspell,3/5pairedwins, medianmacrodelta>=−.01 and requiredchecks. A pass still needs release reproduction/integration; failure closes this fixedcontexttrial without an automatic context/architecture/budget search. Five development matches have already been reused; their scores are not independent target accuracy. No research starts on/afterNovember16.
