# Independent saved-result review: Trial A — November 13, 2026

Verdict: Trial A qualifies under the preregistered version2 gate, conditional on the root byte/source/provenance audit. Retain its short-mix sampler for the already authorized Trial B. This is provisional development selection, not a production switch or independent accuracy claim.

## Gate arithmetic

Recomputed from the ten saved aggregate metric cells without project imports, models, arrays, CSV rows, tests, inference or scoring:

- Median target-like corrupted spellF1 change: +0.011695374371911371 (>0).
- Median paired clean/corrupted spellF1 change: +0.00530387320148118 (>0).
- Paired spell improvement on 3/5 matches (WMX, WN1, WOY).
- Median paired macroF1 change: -0.009168188781474185 (>=-0.01). Margin to the guardrail is only 0.000831811218525815.
- Ten saved fit proofs report40k steps, the same trial signature, exact repeats, and the other-four-match training memberships. The referenced checks log records91 passed tests in seven successful suites (35+4+2+5+8+14+23). These are user execution records, not tests executed by this reviewer.

The saved gate agrees exactly with this arithmetic. The mean corrupted macroF1 falls by0.0105071026097211; that does not override the prespecified median-paired macro gate, but must be reported rather than hidden. No thresholds or metrics should be changed after seeing this outcome.

## Quality and dominant-error changes

|Setting|Mean parent spellF1|Mean A spellF1|Mean parent macroF1|Mean A macroF1|
|---|---:|---:|---:|---:|
|clean|0.633872006|0.645261041|0.925171920|0.924253358|
|targetlike|0.506191099|0.513496193|0.854009568|0.843502465|

At IoU0.5 (diagnostic only; official spellF1 averages five thresholds):

|Setting|Missed parent→A|Spurious parent→A|Recalled short spells parent→A|Dead/live wrong frames parent→A|
|---|---:|---:|---:|---:|
|Clean|1046→972|346→463|151→189 of732|1719→2386|
|Corrupted|1308→1268|564→647|100→124 of732|42828→50889|

Short-spell counts above are recovered by multiplying saved per-match recall ratios by their ground-truth short-spell counts and rounding to integer counts. Aggregate short recall rises20.63%→25.82% clean and13.66%→16.94% corrupted. This supports the targeted exposure hypothesis: fewer possessions are omitted and more short spells are recovered. It also reveals the cost: more extra spells and worse dead/live classification. These counts do not prove a causal decomposition of the spellF1 gain.

The improvement is not universal. Corrupted spellF1 declines on WOY(-0.002194932) and WPY(-0.024353943); paired macroF1 drops more than0.01 on WOY(-0.010082052) and WPY(-0.012516024), while the median remains within the declared guard. Clean WOH spellF1 declines. Matched-boundary medians remain0frames across all matches/settings; conditional matched-boundary summaries alone cannot establish global boundary improvement because unmatched possessions are omitted from that diagnostic.

## Next action

Use Trial A as the parent, retain short_mix and execute only the already preregistered segment soft-IoU loss change in Trial B after the A review binding is committed. Trial B must still pass the full version2 gate; do not rescue it with sampler/weight/decoder tuning if it fails. Preserve the macro/false-positive tradeoff and regressions in ball.md and the technical report. Root owns final source/byte checks and reviewed-a.json. No sealed or target labels were inspected; no generalization estimate follows from the repeatedly reused five development matches.
