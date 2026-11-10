# TCN learning-diagnostic review — November 10, 2026

Scope: review of completed aggregate `experiments/tcn-learning-check-2026-11-10/results.json`, `verdict.json`, the committed diagnostic/trial protocols, source and initial-trial cost records. No arrays, model runs, tests or new scoring were accessed/executed. Production remains nine-core unaugmented CatBoost + penalty16. This review recommends a new bounded training-budget test; it does not reopen or revise the failed200-step trial retroactively.

## Verdict

**A longer fixed training budget is justified as a hypothesis test; a held-out gain is not established. Recommend exactly2,000 Adam updates per fold, with the final update as the only scored checkpoint.** This is a tenfold budget change from200. Change no architecture, features, loss, sampling, learning rate, batch size, corruption, decoder, seed or split. Do not select between1,000/2,000 checkpoints on development scores. A separate committed protocol/amendment must precede execution.

Hypothesis: the200-step candidate did not have enough optimizer exposure to learn the available control signal. Outcome: official held-out clean/corrupted spellF1 and macroF1 on the existing fiveLOMO folds. Decision: retain the new2,000-step candidate only under the unchanged CatBoost-parent promotion gate and required reproducibility. Also report against the rejected200-step TCN as an explanatory comparison; beating that weak model is insufficient for promotion.

## Evidence supporting the test

The fixed training-only10,000-frame segment diagnostic shows:

| Updates | Full-segment CE | Argmax accuracy | Home recall | Decoded training spellF1 |
|---:|---:|---:|---:|---:|
|200|.810039|.6495|0|.054545|
|1,000|.172743|.9374|.8807|.688000|
|2,000|.071580|.9788|.9394|.805556|

At200updates the model predicts noH despiteH being21.46% of this segment. At2,000 it fits all three classes (H/A/D recalls .9394/.9871/.9974), and the full-segment loss falls by about91% from200updates. These are comparable evaluations of the same full segment at preregistered checkpoints, stronger learning evidence than unrelated final minibatch losses from different folds. They demonstrate that the unchanged implementation can learn this small segment rather than being permanently stuck at a trivial class predictor.

The training-only verdict's thresholds were satisfied. **The .805556 is training fit on one segment, not development performance, a ceiling, a target estimate or evidence that .8 will generalize.** AtIoU.5 the decoded model still misses11of41training spells and short-spell recall is.4; good frame fit alone does not solve the spell task.

## Why2,000, and what it does not establish

2,000 is the longest preregistered diagnostic budget at which all basic fitting checks passed, and is a simple fixed10× exposure change rather than a new budget sweep. Each update has8windows ×200retained loss frames:200updates yield320,000 loss-frame presentations;2,000 yield3.2million. These overlap and are sampled with replacement, so they are neither unique frames nor independent observations. The full four-match training population is much larger and more heterogeneous than the diagnostic segment;2,000updates is not proved sufficient for convergence there. Its value is to test whether the current gross failure was substantially training-budget limited while keeping other explanations fixed.

The recorded diagnostic took46.5seconds; old per-fold200-step initial fits took5.27–5.66seconds. These support a rough order-of-magnitude expectation of tens of seconds per2,000-step fit on the same machine, **not a measured end-to-end runtime**. Repeated training, full-match inference/scoring and environment verification add costs; do not promise a total from the fit timing alone. Existing user execution policy and any newer explicit scope controls who launches the run.

## Required interpretation and guardrails

- Keep CatBoost16 as the selection reference and all fiveLOMO matches/clean and fixed target-like conditions. Sealed and target labels untouched.
- Require positive median paired clean/corrupted spell delta, majority of matches positive, median macro delta≥−.01, median corrupted spell gain≥+.01, tests and reproducibility. Candidate quality eligibility is not production promotion.
- Report all per-match scores and missing-ball dead/live quality. Longer clean-only training may strengthen missing-ball→D behavior or overfit person-independent trajectory quirks; representation still has17-frame receptive field and does not acquire long-gap context from extra steps.
- No early stopping or choosing budgets from held-out results. Final2,000-step results only; training loss checkpoints may be recorded as diagnostics, not candidate-selection options.
- If the full trial remains far below parent, close it and investigate model/input limitations rather than automatically extending again. If it improves over200steps but still fails the CatBoost gate, record partial learning success and retain CatBoost.
- Repeatfit/reload/batch exact-CSV checks remain necessary. No change to existing November16 freeze or sealed interpretation rule.

Confidence: high that additional training improves fit on this specific training segment; moderate that200steps was an insufficient learning exposure there; low/unknown about2,000-step held-out spellF1 effect, corrupted improvement or target transfer. Plausible alternative explanations remain memorization, sample/label distribution, limited context and model capacity. Only the controlled fullLOMO comparison can address the relevant decision.
