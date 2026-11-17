# Run the final fixed pretraining comparison

This is the approved plan's next learning experiment. It keeps the successful motion TCN and compares two schedules:40k possession updates with a reset halfway, versus20k masked-ball reconstruction updates followed by20k possession updates. The candidate pretrains on eligible PFF geometry plus each fold's four training IDSSE matches; it never trains on PFF possession labels. The held-out matches remain excluded even from unlabelled pretraining.

Run this once after the registration commit exists; required checks are included before training:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_pretrain.py --run
```

Allow **roughly6–8hours as an unmeasured planning estimate**. It runs five held-out folds for each of two schedules, with two identical fits per fold to verify repeatability:20fit pipelines, each40k updates. One CPU thread, no custom RAM cap. Both schedules reset Adam and supervised sampling at20k; this is not continuous40k training. Equal updates do not guarantee equal actual computational cost. Keep the Mac powered and avoid simultaneous model jobs.

Results are written separately under experiments/tcn-pretrain-2026-11-11/evaluation/control/ and evaluation/pretrain/. Control is evaluated first against the retained rotation model (.6022clean/.4777targetlike spellF1). The pretraining candidate then faces whichever is retained by the complete promotion gate. Both references are preserved for interpretation. No model is automatically deployed or exported to the target game.

Checkpoints preserve optimizer, all random states, stage, losses and membership every1000updates. If interrupted, preserve evidence and report the error. Identical-source resumption is implemented but remains unexecuted by the assistant. Do not alter settings or delete evidence to bypass a failure.

Send “done” when the run completes. We will inspect saved per-match results and hashes; keep a change only if the full gate passes, including +.01median corrupted spellF1 improvement. A failed pretraining objective closes this route; no automatic parameter search follows. Target accuracy remains unknown. All tests, compilation, training, inference and scoring are left for the user; the assistant has only inspected/written source.
