# Boundary objective: audited rejection

November 11, 2026. The registered fixed auxiliary-boundary objective fails the development promotion gate. Retain the original gap-trained motion TCN with equal identity/rotation probability averaging and decoder16. Production CatBoost16 remains unchanged; target accuracy is unknown.

|Mean metric|Rotation parent clean|Boundary clean|Rotation parent corrupted|Boundary corrupted|
|---|---:|---:|---:|---:|
|spellF1|0.602154622|0.583063400|0.477681884|0.464355253|
|macroF1|0.919369777|0.913443301|0.838610693|0.832788402|

Only J03WMX improves on the paired mean of clean/corrupted spellF1:1/5 wins, required at least3/5. Median paired spell delta -0.012318298 fails positive median; median corrupted delta -0.017761930 fails required +0.01. Median paired macro delta -0.004693177 meets the macro tolerance, but cannot override the failed spell criteria. Corrupted spellF1 improves on WMX/WOY and declines on WN1/WOH/WPY. Reject the fixed objective; do not retune coefficient, target width or decoder as an automatic rescue.

|Match|Setting|Parent spellF1|Boundary spellF1|Parent macroF1|Boundary macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.564908|0.565501|0.929536|0.928178|
|J03WMX|targetlike|0.449571|0.454501|0.866045|0.858017|
|J03WN1|clean|0.539192|0.505212|0.887772|0.874731|
|J03WN1|targetlike|0.406341|0.378999|0.796257|0.772973|
|J03WOH|clean|0.671676|0.642336|0.932105|0.928881|
|J03WOH|targetlike|0.514451|0.482899|0.842906|0.820204|
|J03WOY|clean|0.639181|0.609451|0.920628|0.912035|
|J03WOY|targetlike|0.489575|0.494668|0.825537|0.849141|
|J03WPY|clean|0.595816|0.592818|0.926808|0.923391|
|J03WPY|targetlike|0.528471|0.510709|0.862309|0.863607|

The intended diagnostic did not improve: short-spell recall at IoU0.5 declines125/732→122/732 clean and92/732→81/732 corrupted. Missed spells increase1119→1138 clean and1379→1399 corrupted; spurious spells increase386→404 and616→638. Dead/live wrong frames decline2362→1799 and51589→50072, but that does not compensate for worse spell quality. These dependent diagnostics differ from official averaged-over-IoU spellF1 and do not establish a causal decomposition or model ceiling.

Root independently recomputed ten-cell completeness, aggregate/fold row agreement, parent metric agreement, all per-match paired/primary deltas and gate decisions from saved external aggregate JSON using standard-library arithmetic. Verified185 registered fingerprints(133source,47input/reference,5compact manifests),35compact member hashes,10checkpoint hashes,30candidateCSV hashes and10parentCSV hashes. Committed protocol/source match registration; five folds use exactly the otherfour development matches and20k steps. Saved combined and component loss histories are complete and internally consistent; no selection uses training loss.

User logs record54contracts(35+4+2+5+8) passing; saved records report exact repeated training and ten both-viewreload/batchCSV cases. No last-failure record. This audit inspected stored evidence and file hashes; it did not execute tests, model/data imports, compilation, inference, scorer or training, and did not load raw arrays/checkpoints. Reproducibility evidence does not make a rejected quality result eligible.

Recorded fold stages sum4969.533363seconds(82.83minutes), not totalwalltime or peakRAM. Highest historical clean mean remains a different unaugmentedTCN .609882; retained robust candidate .602155/.477682 is unchanged. Five reused development matches limit generalization; serving slot-identity risk and neural finalfit/export/clean-environment qualification remain outstanding. Protected/target inputs and public labels were not used in this audit.

Preregistration e51cec3 preceded the user run. Preserve stopped source/representation/decoder tracks and the bounded objective failure. The prospective final substantive direction remains masked-geometry pretraining followed by IDSSE-only fine-tuning with an explicit budget and matched-compute control, subject to feasibility and separate preregistration; no such experiment is registered or started by this review. No automatic follow-up, new downloads, external push or submission.
