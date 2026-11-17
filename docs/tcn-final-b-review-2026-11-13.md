# Static review: final Trial B ensemble — November 13, 2026

Scope: scripts/fit_tcn_final_b.py; experiments/tcn-final-b-2026-11-13/final_training.py, release_contract.py and both synthetic test files; final-fit protocol and user command. Read current ball/state/findings and compared the final trainer directly against the locked Trial B fold trainer. Review uses source and documentation only; no tests, imports, compilation, arrays, model/checkpoint deserialization, fitting, inference or scoring.

No remaining blocking source defect was identified. Runtime correctness remains unverified until the user executes the command and root audits its saved outputs.

## Verified behavior boundaries

The optimization loop remains identical to Trial B. Changes are final-purpose identity, ordered all-five membership, API/import placement and output wording. The architecture remains9701parameters, two fixed initialization seeds, short_mix, CE+.1segment soft-IoU and staged40k/reset training. No held-out field disguises this final training as development evaluation. Exactly two member models, each repeated once, produce four fits; repeat copies do not count as ensemble diversity. Training refuses missing, reordered, protected or non-IDSSE memberships before sampler/model work.

The coordinator runs inherited/new contracts in separate processes, then launches at most two seed workers. Each worker configures Torch exactly once. Its actual returned first-fit state is compared with a newly instantiated, saved/reloaded model. Both full fits compare model/optimizer/RNG/loss/component/exposure state, excluding timing. Atomic progress and exact identities support resumption; duplicate master/seed operations are locked and compact data use a shared reader lock.

Registration reuses original data/environment/source pins and verifies the committed reviewed-A/B decisions, full ten-cell B results, computed gate, fold membership/budget/repeat records and all required prediction/checkpoint/log bytes. It then requires committed final source/protocol/member locks. Final membership excludes sealed IDSSE, target and PFF. There is no inference, public-score or sealed-evaluation path in this fit runner.

The final manifest binds both members and repeats, proof paths/hashes, class order H/A/D, scaler, source lock, selected-review hash, environment and inference policy. Review recommended tightening completed-manifest checks beyond initial member weights; root implemented exact schema/sampler/loss/order/scaler/source/review/environment and repeat/proof-path checks. Completed artifacts cannot silently accept different semantic metadata on resume.

Combined storage accounting includes prior missed-trial artifacts plus new final experiment/data/model roots, with the shared storage mutex,2GiB cap,12GiB free floor and64MiB atomic-write reserve. Existing evidence is never automatically deleted. Training checks the November16 boundary each iteration; guarded writes check after lock acquisition. Streamed logs and unrelated applications are not controlled by an operating-system disk quota.

## User-run verification and residual limits

Thirteen new synthetic contracts are supplied: five final identity/membership/freeze/resume contracts and eight release evidence/storage contracts. Their source covers a normal accepted evidence chain, rejected/unreviewed B, forged parent or repeat proof, altered model/CSV bytes, storage floor/symlinks, prohibited memberships and interrupted/resumed final-loss training. Together with91 inherited checks,104 tests are expected; none was run during preparation.

The user must execute these checks and the four fits. Root must subsequently audit repeat, reload, coverage, component-loss and member/manifest hashes. Actual runtime, RAM, scientific generalization and clean-environment reproduction remain unverified. Fitting all five development matches produces a release artifact and no new quality score. B remains median-gate-selected despite A's higher corrupted development mean. Preserve A and all earlier artifacts. Private export, official validator, CSV byte reproducibility, fresh-clone reproduction and once-only frozen sealed evaluation remain separate delivery steps; no production switch or external submission occurs here.
