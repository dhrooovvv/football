# Static review: missed-possession trials — November 13, 2026

Scope: `scripts/run_tcn_missed.py`; `experiments/tcn-missed-2026-11-13/{contract.py,objectives.py,training.py}` and their synthetic contracts. Also inspected inherited compact-window construction, original model configuration, rotation averaging and completed-arm proof APIs. Applied the ECC Python-patterns guidance to explicit state, context-managed writes and deterministic interfaces. No tests, imports, compilation, model fitting/inference/scoring, datasets, arrays or checkpoints were executed or deserialized by this reviewer.

## Findings and resolution

An integration blocker was caught before preregistration: the dependency loader called the original Torch `configure()` for both preflight and final evaluation. Its inter-op thread configuration must be initialized once per process; repeated initialization could fail after expensive fitting. The runner now process-caches `dependencies()` with `lru_cache(maxsize=1)`. The supplied synthetic runner contract checks the presence of this cache; actual two-stage execution still requires the user run.

Two smaller execution safeguards were strengthened during review: research-date validation now occurs at each training iteration, and the storage guard rechecks the date after acquiring its interprocess mutex. Duplicate hidden worker launches also have a per-seed exclusive lock. These changes do not alter the scientific intervention.

No remaining blocking defect was found in the reviewed source. This is static review, not runtime certification or evidence of metric gain.

## Normal, failure and integration paths inspected

- Trial A chooses one eligible spell uniformly, then a start uniformly from the inclusive containment interval `[spell_end-225, spell_start-25]` intersected with existing complete known-label window starts. The original uniform branch retains its draw ordering. Eligibility/exclusion and actual complete-short-spell exposure are recorded. No half or unknown-label region is crossed.
- Trial B obtains segment identity from the original training-match labels, excludes crop-cut spells, and bounds each flank by the immediate adjacent segment. The soft-IoU numerator/denominator and equal segment averaging agree with the protocol. Empty segment batches retain differentiable zero. No boundary head or decoder minimum duration is introduced.
- Each fold accepts only the ordered other-four IDSSE cases, uses fixed two initialization seeds and staged40k/reset training, and retains all three RNG states, optimizer, coverage and component losses for resumption. Repeated-fit equality excludes timings and includes model/optimizer/RNG/loss/exposure state.
- Parent preflight uses both fold-safe ensemble members, each rotation-averaged before the equal ensemble. All ten parent CSVs and metrics are checked before new fits. The original all-five final artifact is absent from this path.
- Gate v2 preserves the majority, paired-spell, macro and correctness requirements while changing only the primary floor to strictly positive median corrupted gain. Trial B requires an exact, committed reviewed-A binding; its signature includes that binding, and the runner verifies A completion and its fit/prediction fingerprints before B execution.
- Storage writes serialize under one mutex and reserve64MiB before an operation; new artifact roots are counted toward2GiB and a12GiB free-space floor. Atomic checkpoint replacement preserves prior progress after interruption. No automatic deletion or download is present. Streamed worker logs are small expected writes, rather than a disk quota enforced by the operating system; the implementation does not protect against unrelated applications consuming disk between checks.

## Runtime verification still required

The supplied contracts cover tiny positive/zero gains, favorable-mean/negative-median rejection, majority and macro failures, missing/changed review binding, disk limits, symlinks and freeze boundaries; sampler endpoints, threshold50, half/X exclusion, missing eligible spells, exact RNG continuation; segment completeness, immediate-neighbor bounds, soft-IoU formula/gradients and empty batches; tiny interrupted/resumed training equality; altered checkpoint rejection and dependency caching. None has been run during preparation.

The user must run correctness checks, ten parent reconstruction cases,20full fits per trial, exact repeats, both-seed/both-view reload probability checks, and all three CSV byte comparisons. Trial B remains blocked pending an independently reviewed and committed A decision. Keep historical protocols/results unchanged, log failures separately and stop after the two authorized trials. Generalization, metric improvement, actual runtime, peak RAM and clean-environment/fresh-clone reproduction remain unverified for these candidates.
