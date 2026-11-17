# Expanded TCN static review — November 11, 2026

## Scope and verdict

Reviewed `scripts/run_tcn_expanded.py`, `experiments/tcn-expanded-2026-11-10/{expanded_data.py,expanded_training.py,tests/test_expanded.py}`, the original encoder/model, the gap parent trainer/mask builder, both provider adapters, and saved aggregate expansion results. Read AGENTS.md, ball.md, research-state.yaml and findings.md. No modules, tests, inference or training executed. No raw match assets, prepared arrays, model tensors, target/public labels or sealed observations were loaded. Only this review document was written.

**No confirmed implementation defect in the reviewed path explains the measured regression.** Preserve the rejection. Repeatability and structural admission do not establish provider equivalence. There are worthwhile defensive checks for the next runner, but no evidence justifies labeling the failed result a bug or rerunning it unchanged.

## Behavior traced

- **Provider coordinates:** IDSSE `external.py:46` and PFF `pff.py`'s final resampling loop both convert centred metre XY into normalized XY using pitch size plus .5. The shared `prepare_tcn.py:31–37` encoder centres/scales these positions identically, derives velocities at 25Hz, clips identically and retains observation/role masks. The core features use each provider's pitch dimensions before common scaling. No obvious factor-of-two, axis-order or home/away inversion is introduced by expansion. Raw supplier correctness and attack-direction conventions were not independently revalidated in this static review.
- **PFF observation contract:** `load_pff` admits only raw VISIBLE positions, uses side+jersey roster slots, excludes extra periods, clears event state on unsupported clock/video and native-time gaps, and resamples to 25Hz. The training preparation compares new labels/blocks/core features exactly to the admitted arrays (`run_tcn_expanded.py:141–147`). Event-derived possession semantics remain a provider contract, not the same annotation process as IDSSE's per-frame labels. `event_state` carries supported state/owner forward; this is not newly introduced by the TCN expansion.
- **Augmentation:** raw PFF ball positions are masked before recomputing features and encoding (`run_tcn_expanded.py:148–153`). Players remain unchanged. IDSSE reuses the original independent training-gap arrays. `pack_case` explicitly rejects player/role differences and reconstructs each clean/gap view exactly. Missing ball cannot be converted into a valid coordinate by compact storage.
- **Train/test separation:** the runner removes each held-out IDSSE key before fitting and requires 52 remaining matches (`:217–221`). Fit input membership enters checkpoint identity. The final53 fit is separate, after evaluation. Constant scaler means no learned normalization can leak test statistics. The existing CatBoost emissions and parent CSVs are hash checked on each new fold.
- **Sampling:** `expanded_training.py:49–62` samples uniformly from the cumulative count of known 250-frame starts, exactly matching the gap parent's algorithm. `valid_windows` excludes X and half crossings. Thus PFF dominating the larger window population is an intentional policy with measured consequences, not a sampling arithmetic bug.
- **Loss and temporal support:** 250-frame windows, 25-frame halo, 200 loss frames, batch eight, Adam .001, clipping1, 20k updates and independent gap-view RNG match the parent. The convolution support is 17 encoded frames (radius8), so halo25 is sufficient. There is no hidden ten-second receptive field; the large sampled window does not enlarge the three temporal convolutions. Inference clips its halo at half boundaries and writes each retained frame once.
- **CPU/repetition:** configure sets CPU/inter-op1, deterministic algorithms and MKLDNN off. Checkpoints restore optimizer, both NumPy RNGs and Torch RNG. Two full fits compare weights/losses/sample counts, and evaluation compares reload probabilities and repeated/batch CSVs. Saved logs report45 contracts and10 inference cases passing, but these were not rerun here and are not clean-environment proof.

## Specific follow-up risks

### P1 prospective leakage risk: never initialize held-out folds from final53

`run_tcn_expanded.py:310–325` saves a model trained on every IDSSE development match. Using it as a fine-tuning initialization in any later leave-one-match-out fold would expose that fold's held-out labels through pretrained weights. This has **not** happened in the reviewed run, which initializes fresh. For any adaptation experiment, use a PFF-only pretraining checkpoint or fold-specific training-only checkpoint and assert its entire ancestry excludes the held-out/protected keys. Reject missing ancestry metadata. Merely removing a match from the fine-tuning loader is insufficient.

### P2 defensive integrity gap: compact manifests are self-contained, not separately pinned

`verify_prepared:100–113` verifies data against the adjacent manifest and metadata registration. `prepared_cases:180–189` fingerprints that manifest for checkpoint identity. A simple data-byte change is detected. A simultaneous data+manifest change with retained registration can be accepted by a fresh fit: the new fingerprint prevents old checkpoint reuse, but is not compared with an independently registered prepared snapshot. There is no evidence this occurred and it does not explain regression. Small mitigation for the new runner: pin every existing compact manifest SHA in its committed registration, then run the existing per-file verification. This binds the new comparison to the exact already prepared arrays without rebuilding them or changing the completed protocol.

### P2 resume evidence gap: completed fold records are trusted by signature alone

At `run_tcn_expanded.py:223–229`, a completed fold is accepted after checking its registration string; row match/condition uniqueness, exact training membership, recorded CSV hash and private CSV presence are not rechecked in this branch. The completed audit independently checked row/membership consistency, so no demonstrated result contamination is claimed. Minimal new-run mitigation: when retaining a completed fold, require the two expected match/condition cells, exactly the expected training membership, expected sampler identity, and matching saved candidate CSV hashes. Fail with a review message if evidence is absent or changed; do not silently refit or select around a bad fold.

## Recommended smallest next experiment

A single fixed provider mixture can test whether useful PFF exposure survives when IDSSE practice is preserved. Keep all prepared arrays, architecture, loss, 20k budget, seeds, gap-view policy, CatBoost50/50 blend and penalty16 fixed. Choose provider IDSSE/PFF with a preregistered probability, then choose uniformly among valid window starts **within** that provider. Fixed50/50 is a simple defensible first setting; do not search mixture weights on the five reused matches. Within-provider sampling should remain proportional to valid starts, rather than adding match-uniform sampling as another intervention.

Use fresh initialization and a new output/checkpoint namespace. Give the sampler its own identity in the checkpoint registration and record actual per-provider/match/clean-gap counts. If an independent provider RNG is added, save/restore it and preserve the separate gap-view RNG. Do not reuse expansion progress checkpoints with an altered sampler. Confirmatory promotion must be versus the retained eligible gap blend (.592502/.428386), not versus the rejected .520562/.376959 expansion; the failed expansion is only an explanatory reference. Comparing a 50/50 mix with IDSSE-only estimates the effect of that fixed training mixture under the fixed budget, not an isolated proof that balancing is the causal repair.

This proposal does not establish that50/50 is optimal or promise a gain. Pretraining plus adaptation and longer context are separate, later interventions. Respect the existing failure counters and freeze. Repeated use of five matches is selection evidence only, with the sealed evaluation reserved for the frozen candidate.

## User-run validation to include before the next long run

These are requirements for supplied tests, **not executed checks**:

1. Normal path: synthetic providers with unequal available starts; check valid selected offsets, absence of X/half crossings, repeat draws and provider-count reporting under the fixed sampler.
2. Failure path: missing provider/empty valid pool, changed compact manifest, mismatched sampler/checkpoint identity and a checkpoint ancestry containing the held-out match must fail closed.
3. Integration edge: interrupted training restored with provider/window/view RNG states must match uninterrupted weights, losses and sample counts; clean/gap representations remain byte-identical to the frozen compact reader. Repeated full-fit, reload and batch-CSV checks remain required for all scored cases.
4. Resume edge: completed result missing either condition or with a changed CSV hash must be refused before aggregation.

Residual uncertainty: fresh-environment operation, target tracklet temporal identity, supplier annotation semantics, transfer to the actual competition game, and the extent of five-match selection optimism. No project-specific claim of a maximum TCN score or competition-winning score follows from this audit.
