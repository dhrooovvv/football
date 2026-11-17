# Provider-balanced TCN static review — November 11, 2026

Scope: newly written `scripts/run_tcn_balanced.py`, `experiments/tcn-balanced-2026-11-11/balanced_training.py` and `tests/test_balanced.py`, plus the archived expanded engine functions they call. This review is source inspection only. No imports, compilation, tests, inference, training, prepared arrays or model tensors were executed/loaded. Protocol and inputs.json were still being authored when this pass began; their final lock coverage is therefore not yet reviewed.

## Verdict

No blocking sampler, RNG restoration or output-isolation defect found in the inspected source. The proposed fixed equal-provider sampler is coherent. Runtime compatibility and the supplied tests remain unverified and must be user-run. Two small final-fit/evidence checks would strengthen fail-closed behavior before the long run.

## Behavior traced statically

- `ProviderSampler` requires exactly IDSSE/PFF and unique case keys. It builds valid records through the archived known-label/half-safe window enumeration. For each provider, cumulative support maps each integer to exactly one valid start; provider is sampled uniformly before conditional uniform window selection. Match weighting within provider is proportional to valid-start count, as intended.
- Fresh initialization, architecture, 20k budget, optimizer, loss, 50% gap selection, view seed, CPU policy, frozen CatBoost/blend and decoder are unchanged. The new provider RNG is independent from both window and view RNGs. Checkpoint identity includes sampler and provider seed; checkpoints restore all three NumPy RNGs plus Torch state, optimizer, loss history and coverage.
- `configure_engine()` replaces globals in the imported engine module, so its `fit_twice()` calls the balanced `train_fit` and its scorer/evaluator writes to balanced output directories. `fit_final()` also uses those globals. No archived source file is edited; old compact input paths remain explicit and read-only. The final basename still says53matches, which is correct for the approved pool.
- Pinned compact manifest checks happen before training, followed by archived per-file hashes and prepared registration checks. This ties reuse to existing bytes without a new adapter/preparation intervention. New experiment signature captures inputs.json, so prepared fingerprints affect checkpoint identity through that lock.
- Both old-expanded and new-balanced operation locks are held during checks/evaluation/final fitting. Old preparation cannot run concurrently. `--check` performs registration plus synthetic suites and returns before full array verification/model training; it nevertheless requires the preregistered compact manifests to exist.
- On resume, completed folds require exact training membership, two expected conditions, recorded repeated-training proof and all three matching candidate CSV hashes. This closes the archived evaluator's signature-only reuse gap.
- `--run` evaluates only. `--fit-final` is separate and requires a saved passing gate, so failed trials do not automatically consume a final fit. There is no checkpoint warm start from the rejected final53 model. The original engine requires exactly52trainingmatches after removing each heldout key.

## Recommended hardening before finalization

### P2: final-fit eligibility depends on a cached gate boolean

`run_tcn_balanced.py:197–201` trusts `evaluation/gate.json[quality_eligible]` after validating individual existing fold files. A changed/stale gate file is not bound to their rows or the current signature. The normal evaluation sequence generates consistent files, so this is not evidence of an observed false promotion. However, the intended rule is that **the current five folds pass**, not merely that an adjacent file says true.

Smallest mitigation: before final fitting, require every exact expected development fold to exist, reconstruct its ten rows and recompute the unchanged promotion gate; require saved gate fields to agree. Validate five expected files explicitly instead of only `len(glob('J*.json')) == 5`, because that count can include an unexpected file while an expected fold is absent. Keep the archived scorer unchanged; this is artifact validation, not model tuning. A failure should preserve artifacts and stop, with no automatic refit or gate rewrite.

### P2: new runner's evidence failure branches have no supplied direct tests yet

The four new tests exercise support enumeration, conditional provider choice, invalid support, and repeated/interrupted trainer recovery. They do not exercise `registration`, compact-manifest drift, completed fold/CSV evidence, output remapping or final-fit gate rejection. Existing trainer tests cannot prove those orchestration properties.

Smallest mitigation: supply user-run source-level/mocked runner tests for changed compact manifest, missing expected fold, changed CSV hash, wrong membership, and a false/tampered saved gate. A normal path should verify that the engine's final-fit function is reached only with complete passing evidence and that failure does not call it. This need not train a model. Do not execute those tests while preparing; the user reserves all testing.

## Registration items to verify when authored

The committed code lock should include the new runner/trainer/tests, the archived expanded engine/trainer/compact reader, original TCN/encoder/scorer/core/decode dependencies, protected split/cohort and the original membership/registration. All53 compact manifest hashes should be pinned. The data lock should include unchanged development prepared arrays, frozen CatBoost emissions, parent gap CSVs and the rejected uniform-expansion aggregate reference used only descriptively. `prepared_registration` must be the original preparation signature, not the longer training signature that appends compact fingerprints. The new gate comparison must remain the retained gap blend; the uniform expansion is not a promotion parent.

## Validation status and residual risk

Normal path, interrupted resume, failure handling and integration edge were traced only from source. No run has established equality, test success or score improvement for this new candidate. Exact repeat fits and reload/batch CSV checks are inherited requirements, not yet successful evidence. Equal-provider sampling does not preserve the IDSSE-only parent's exact window sequence and does not isolate all causes of the expansion failure. Provider semantics, a short learned receptive field, reused development selection, clean-environment reproduction and target player-slot continuity remain unresolved. No score ceiling, expected gain or competition-winning threshold is claimed.

## Final static follow-up before preregistration

Read the completed protocol.md and inputs.json, added `verified_gate()` and `tests/test_balanced_runner.py`. No execution/import/compilation/test run occurred.

The two recommendations above are **resolved in the supplied source**: `verified_gate()` now requires the exact five expected fold filenames, checks cached fold membership/conditions/CSV evidence, requires aggregate rows to equal fold rows, checks metric finiteness/range, recomputes paired/primary arithmetic with the unchanged promotion function, and verifies saved gate/deltas/evidence before optional final fitting. Four additional runner tests cover normal complete evidence, missing fold, held-out membership contamination, tampered repeated CSV, and a forged saved true gate. These tests remain user-run and have not passed merely because their source was reviewed.

The new lock includes archived engine/reader/trainer, original TCN/encoder, scorer/core/decode, split/cohort/original membership and preparation protocol/inputs, new runner/trainer/test files, all53 compact case manifests, ten frozen evaluation inputs/emissions/parent CSV sets, and descriptive rejected-expansion aggregate results. The stored `prepared_registration` is the original64-character preparation signature beginning `9e64e427`, rather than the longer fold signature with appended prepared fingerprint. The existing verifier checks it against metadata at user execution. No prepared arrays were read by this review.

Protocol accurately distinguishes the retained best as the promotion reference from the rejected expansion as a mechanism reference. It states that the intervention against retained best is the fixed mixed-source training policy, not a pure isolated balancing effect. Budget, seeds, corruption, architecture, decoder, blend and holdouts stay fixed; source mass is the only intended policy change. The prior two expansion failures and stop-after-third rule are explicit. No warm-start from final53 is permitted.

Minor provenance suggestion: add `experiments/tcn-gap-2026-11-10/gap_training.py` (imported by the inherited gap test) and the official starter `baseline.py` (imported by review_frozen, although smooth is unused by this evaluator) to the code hash lock. No evidence they changed and no scoring defect follows from the omission; this completes transitive imported-source provenance.

**Final verdict:** no concrete remaining blocking defect found in this static pass. Ready to commit the protocol/code for user-run checks, with runtime/test success, fresh-environment compatibility and any quality gain still unverified. Do not represent this review as a test pass or authorize a production switch from it.

Registration closure: the parent applied the provenance suggestion by pinning gap_training.py, official starter/baseline.py and its games.py dependency. No test or model execution followed.
