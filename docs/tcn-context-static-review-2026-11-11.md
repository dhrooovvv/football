# Longer-context TCN static review — November 11, 2026

## Scope and verdict

Reviewed scripts/run_tcn_context.py; experiments/tcn-context-2026-11-11/context_model.py, context_training.py and six supplied test_context.py contracts; archived TCN/gap/compact training and evaluator helpers; independent design review; project AGENTS, journal, state and findings. Source-only review. No imports, compilation, tests, checkpoint/model reads, raw/prepared arrays, inference or training executed. Only this review document is edited.

**No concrete blocking defect found in the traced source.** This is not runtime validation, proof of determinism, evidence of a score gain or a production promotion. Protocol/input-lock completion is reviewed separately below when available.

## Normal path and scientific boundary

context_model.py:12–20 declares dilations(1,4,12,36,108), radius162, RF325, halo163, core200, window526. The object k3 convolution contributes radius1; successive temporal radii2,6,18,54,162 have overlapping integer support, so no theoretical holes occur. Widths and channels match the original per-object/team pooling contract. Candidate15,843 parameters versus parent9,635, increase6,208, follows source arithmetic. Depth/capacity change along with context; the result cannot identify a pure receptive-field effect.

context_training.py:16–42 maps the original valid250-frame records to their containing real half and retains the same ordering/counts. For anchor s, its larger crop's central200 indices are s+25..s+224. Context clips to the real half, not the teacher known-label run. Unknown labels can occur in surrounding inputs without entering loss. context_training.py:58–60 and82–85 preserve the parent's seed, vector-eight window draws and separate gap-view draws. Context changes cannot silently shift the sampled loss-label population through a526-known-frame requirement.

The runner filters exactly five IDSSE members against the pinned development split and excludes sealed IDs (registration lines58–68). Training rejects any non-IDSSE case (context_training.py:45–49). Evaluation holds one out and requires exactly four training cases. No final53 warm-start or PFF training path is offered. The retained gap-blend CSV path is used as the scoring parent, not the rejected expansion.

Runner configure_engine substitutes the context trainer/model/predictor and private output paths only in the isolated process. Archived fit_twice resolves its module-global train_fit at call time, so it reaches the context trainer. The local evaluator constructs the context TCN for reload. Checkpoint and CSV outputs use models/tcn-context and data/tcn-context, preserving archived artifacts.

## Failure path and resumption

Checkpoint identity includes new architecture/halo/window, parent-anchor dimensions, source registration, membership, budget and seed. Resumption restores model, optimizer, torch RNG, window RNG, gap-view RNG, loss history and per-match view counts, and rejects identity/step mismatches (context_training.py:53–77). Fresh initialization is used unless an exact own-trial progress checkpoint exists. The two-repeat helper compares full states/losses/counts.

Completed-fold cache checks require exact membership, match/conditions, coverage keys, repeat-fit evidence and all three private CSV hashes before reuse. verified_gate requires the exact five filenames, fold/aggregate equality, finite metric ranges and independently recomputed gate/deltas. Thus a stale boolean, missing fold or tampered repeated CSV cannot silently authorize the decision. These are source-level traced guards, not executed failure tests in this review.

## Integration edge: halves, crops and inference

context_model.py:57–74 validates ordered/disjoint half intervals and constructs every inference crop by clipping to that half. With halo163 greater than radius162, returned central outputs cannot depend on the internal window boundary. Replicated-edge whole-half reference padding must match these clipped inputs. The supplied reference test explicitly pads each true half before forwarding, avoiding a false comparison against an unpadded model's zero-convolution edge semantics. It also changes the second half and requires unchanged first-half probabilities; partial cores and reload/batch decoding are covered.

The user-run evaluator requires exact reloaded probabilities and identical CSV bytes across batch1/reload/batch4. Whole-half/chunk numeric tolerance is fixed at1e-6 in the separate synthetic diagnostic, without relaxing the CSV gate. Full-data compatibility and these checks' success remain unverified.

## Supplied validation and residual risks

Six new contracts cover theoretical support/capacity, exact parent-anchor mapping, unknown contextual labels/half clipping, whole-half/chunk agreement and half isolation, reload/batch labels, and repeated/interrupted four-step synthetic training with checkpoint mismatch/PFF rejection. They are supplied for user execution only. Existing scorer/gate evidence branches were previously tested in the balanced runner, but direct new-context runner registration/cache/gate tests are not yet supplied; copying the helpers does not itself establish a new pass. A small mocked runner evidence suite would improve protection against future orchestration edits, but no concrete current defect makes that a blocker.

Potential remaining quality risks are hypotheses: more depth may not optimize at the same20kbudget; player-slot continuity/velocity can limit transfer; longer gaps may remain unidentifiable; reused development matches invite selection optimism. Larger crops/depth change memory/compute cost, so walltime/RAM need measurement by the user. Clean-environment/fresh-clone reproduction and target adapter/release qualification are separate outstanding work. No external submission or publication is performed here.

## Final registration closure

Read the completed protocol.md, inputs.json, docs/run-tcn-context.md and four added tests/test_context_runner.py contracts. All reads remained source/manifest only; no test, import, compile, data verification, model or checkpoint execution occurred.

The new lock pins model/trainer/runner/allten new tests, archived checkpoint/compact/scoring helpers, original TCN/encoder/gap trainer, production and related contract sources, official scorer/baseline/games, development split, old compact membership and preparation registration inputs. Five compact manifest paths are all IDSSE development members; no PFF compact manifest/data path appears. Thirty evaluation paths cover the five matches times clean/corrupted times input/CatBoost emission/retained gap-blend CSV. Stored preparation registration is the original64-character preparation signature. New source/protocol/input fingerprints are required committed before user execution; runtime rehashes compact files via the inherited verifier.

The four runner evidence tests resolve the earlier optional orchestration gap: normal full evidence, missing exact fold, held-out contamination, tampered CSV and forged saved eligibility are represented with IDSSE-only fixtures. These are unexecuted supplied tests, not evidence of success. No registration fixture executes a model or loads real match inputs.

Protocol accurately fixes depth/field/crop, preserves parent anchors/supervision/seeds/budget/augmentation/blend/decoder/gate, distinguishes capacity from a pure receptive-field claim, and leaves the data-expansion track stopped. Standalone scores are descriptive. Failure closes this fixed trial, with no automatic rescue. User commands stop at development comparison and preserve release checks.

Minor documentation precision: run-tcn-context.md says existing “raw/source hashes” must match; this runner actually checks code/source files, prepared compact arrays and evaluation references rather than rereading the original raw match assets. Replace that phrase with “code/source and prepared-input hashes” to avoid overstating validation. It is not a scoring or training blocker.

**Final verdict:** no concrete remaining blocking defect found in this static review. Ready for local preregistration and user-run checks, with runtime, deterministic full-data behavior, resource cost and quality improvement unverified. Clean-environment/target integration remains separate and unresolved.
