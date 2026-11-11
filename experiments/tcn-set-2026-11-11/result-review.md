# Frame-set TCN — audited rejection

November11. The approved identity-robust representation redesign fails the registered quality gate against the retained standalone gap-trained TCN. No new tests, imports, compilation, model loading, inference, scorer execution, training or dataset-array loading was performed for this audit. Saved external aggregate metrics/loss histories and byte fingerprints were inspected only.

|Mean metric|Retained parent clean|Candidate clean|Retained parent corrupted|Candidate corrupted|
|---|---:|---:|---:|---:|
|spellF1|.597707089|.502256202|.463139170|.361284717|
|macroF1|.917088737|.891761586|.825775931|.752693905|

SpellF1 declines on every match in both conditions. Zero of five paired match improvements; median paired spell delta−.108800129; median paired macro−.044516672, below−.01; median corrupted spell delta−.108958654, below required+.01. Independently recomputed all saved per-match deltas, medians, completeness and gate within1e-12. Both candidate decision and gate agree: reject. Per-match table/error/missing-ball evidence remains in evaluation/report.md and results.json.

Verified all158registered fingerprints,35compactmember hashes,10checkpoint hashes,30candidateCSV hashes, ten parent CSV/metric references and aggregate/fold agreement. Each fold trains on exactly otherfour IDSSE; coverage160000windowdraws/fold,20klosses/hash records complete. User checks record35+4+2+8=49 passing contracts and ten exact repeated-fit/reload/batch cases. These checks support the recorded execution, not proof that every possible implementation defect is absent. No last-failure file. Fold-stage sum1660.826651seconds (27.68minutes), excluding setup/tests/fingerprinting and not a full walltime or peakRAM measurement. Earlier1–2h was an unmeasured planning estimate.

The redesign removed stored object velocities AND pre-pooling temporal object history, and reduced capacity/support. The regression is consistent with loss of informative motion/context, but this coupled trial does not identify a causal component or prove that an invariant model cannot work. It does not resolve the retained model's documented target-slot identity risk, establish a TCN ceiling, or estimate target accuracy. Five reused development matches remain limited evidence.

Apply prewritten conservative stop accounting: relativeXY, longercontext and this frame-set rejection give three failed representation interventions. Stop this representation-improvement line; no automatic width/kernel/motion/extra-update rescue. Source expansion and decoder stops also remain. Retain standalone gapTCN+16 (.597707/.463139) as eligible development leader, with original unaugmented TCN still highest historical clean mean .609882. Production remains CatBoost16; no finalfit/export, protected assets, public labels or submission.

Next allowed possibility is a separately registered fixed inference-only symmetry comparison on the retained model, rather than another architecture trial. No such new comparison is registered or executed here. Actual winner finalfit/export, serving compatibility, official validation, clean-environment/fresh-clone reproduction and frozen sealed evaluation remain outstanding. November16freeze and sealed interpretation remain unchanged; target accuracy unknown.
