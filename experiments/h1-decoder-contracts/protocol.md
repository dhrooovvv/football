# H1 preliminary contract experiment — locked before execution

Status: preregistered, not executed. Date: 2026-11-06.

Question: can a deterministic H/A/D decoder suppress isolated ambiguous evidence while preserving a strongly supported short possession and restart?

This experiment tests correctness only. External-match H1 performance needs a separate protocol after labels and splits exist.

Implement log-emission Viterbi with fixed class order H,A,D and a supplied 3×3 transition cost. Reset at half boundaries. Missing ball alone must not replace an emission with D. Invalid probabilities, shape errors and nonfinite input should fail explicitly. Use a fixed probability floor only for zeros and document it.

Confirmatory fixtures (specified before decoder implementation):
1. Five frames: H probabilities .9,.9,.45,.9,.9; A .05,.05,.50,.05,.05; D remaining. Switch cost 1 per change. Expected all H.
2. H run of five, A run of two, H run of five; each true class .98 and others .01. Switch cost 1. Expected all three spells including the two-frame A.
3. H×5, D×5, A×5 at .98 true/.01 others. Expected three exact segments.
4. Uniform .3333333333333333 emissions in two independent halves; modifying half one cannot change half two decoding.
5. Repeat each fixture twice: require identical arrays; swap H/A inputs and costs on non-tied fixtures: require swapped output.
6. Reject negative probabilities, rows not summing to one within documented tolerance, NaN/Inf and wrong dimensions.

Metrics: exact fixture agreement, tests passed/total, deterministic equality. Required gate: all expected contracts pass. Save fixtures, source revision, environment, command, output and runtime. A failure requires recording the cause before any change; new fixtures are exploratory.

No target or external-match labels used. No competition performance conclusion is permitted from these fixtures.
