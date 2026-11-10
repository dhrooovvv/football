# TCN next-change review — November 10, 2026

Scope: source and completed aggregate reports only. Read ball.md, research-state.yaml and findings.md; inspected the original TCN/adapter, augmentation trainer and completed gate reports. No raw/prepared match arrays, competition observations, public labels, sealed assets, model inference, training, tests or new scoring were accessed/executed. This is a methodological review, not authority to alter production or an experiment protocol.

## Decision

The strongest source-level representation limitation is **ball-independent mean pooling of a small per-player embedding**, not an established optimizer failure. The model pools eight-dimensional player embeddings separately for H and A, then concatenates a separate ball embedding. It has no explicit ball-conditioned player relation before pooling. This can dilute the small number of players contesting the ball among many off-ball players. A network can in principle approximate some interaction from pooled nonlinear spatial summaries, so this is a plausible information/inductive-bias bottleneck, not a proof that pooling destroyed every useful control signal.

Recommend one conditional experiment: add **masked player–ball relative XY plus an explicit pair-observed indicator** to the shared object encoder, calculated from already encoded inputs. Keep temporal architecture, 20,000-update budget, sampling/seeds, 50% augmentation, 50/50 CatBoost blend and penalty16 fixed. Do not also add relative velocity, attention, a new loss, or longer dilation in this trial. First let the refreshed boundary/error audit establish that visible-ball ownership/handovers or observed gap endpoints are a substantial remaining loss. If long unobserved dead/live episodes dominate, this feature cannot directly distinguish them; the case for this trial is weaker.

## Exact context calculation

The object encoder is Conv1d(k=3,d=1), followed after pooling by temporal k=3 convolutions with dilations1,2,4 and a k=1 head. With stride1:

`R = 1 + (3−1) + (3−1)*(1+2+4) = 17 encoded samples`.

Thus the learned convolutional dependency is ±8 samples, or ±0.32seconds at25Hz; the span between the first/last encoded timestamps is0.64seconds. Counting17sample durations gives0.68seconds. The250-frame/10second input window does not create10seconds of learned context; most of that window provides sampled loss positions or unused halo.

Qualification: input velocities depend on the preceding raw position, so the raw-coordinate support can extend one frame farther into the past (`t−9..t+8`), spanning0.68seconds. Precomputed gap_age summarizes potentially much longer past missingness as one scalar; it is incorrect to say every input is independent of history beyond17frames. It does not provide a learned trajectory of that longer history. The25framehalo safely exceeds the current ±8 neural radius.

A larger receptive field is a valid alternative hypothesis, but should be tested separately. Any dilation change must calculate exact support, avoid input-window/halo inconsistencies, and check boundary padding and batch/chunk equivalence. Increasing only WINDOW without changing the convolution stack does not increase R. Very sparse dilation can introduce support holes, and neither this field nor a modest extension establishes inference through arbitrarily long ball gaps.

## Hypothesis and estimand

Hypothesis: explicit masked relative XY lets the same fixed-budget network identify local control and handovers more efficiently than global player means plus a separate ball embedding. Expected direction, if true: better wrong-team/short-spell or boundary performance where the ball is observed, with potential indirect benefits near gap endpoints. Magnitude is unknown; effect can be zero or negative. It does not create ball information during missing frames.

Decision outcome remains the **official per-match clean and fixed-corrupted spellF1/macroF1** against the current best eligible gap-augmented blend (.592502clean/.428386corrupted). The unaugmented standalone .609882clean TCN may be shown descriptively, but is not the current gate parent. The user has questioned clean regressions without explicitly replacing the agreed promotion gate; do not silently change it or cherry-pick the clean reference to make a result pass.

All five clean scores dropped under augmentation while all five corrupted scores improved. This supports a clean/robustness trade-off under that intervention, not that augmentation broadly failed or that another method will raise both. Preserve both historical candidates.

## Minimal implementation contract for relative XY

- Derive the relation from the existing normalized XY of player and ball at the same frame. Pair validity is player-observed AND ball-observed; no label input.
- Multiply relative XY by that validity and pass the validity as a distinct input. Missing coordinates encoded as0 must never be interpreted as an observed ball at pitch centre.
- Leave original absolute coordinates, velocities and their observation indicator intact. Append relativeXY/pair-valid to the object input only, retaining its output dimension8 and all later layers.
- Shared Conv1d input rises5→8 channels. This necessarily adds72 weights (`3extra * 8outputs * k3`), with unchanged biases/output widths; disclose this modest capacity confound. This is one feature intervention with its required input plumbing, not an identical-parameter test. No additional attention or capacity change.
- Keep padding/half isolation and same clean/augmented input paths. Compute relations separately for every view, so an augmented gap suppresses both the coordinates and pair-valid mask.
- No object-slot identity assumptions beyond the audited adapter. Preserve player permutation equivariance under same-team slot permutation; test relation masking, missing/reappearing observations, ballslot identification, checkpoint reload and exact repeatability.
- Test translation invariance of **the relative feature calculation**, not invariance of the full model that still receives absolute coordinates. Neither full rotation nor attack-direction invariance is guaranteed by the current parent architecture.

## Valid comparison and uncertainty

Commit the feature formula/architecture/source/input hashes and fixed protocol before any execution. Same five LOMO folds, seeds, raw corruption arrays, batch/window sampling, optimizer, final20k checkpoint, CatBoost probabilities, blend and decoder. No held-out labels in features/normalization/calibration, no target/public-label selection, and no sealed access. Keep production untouched pending separate clean-environment/fresh-clone/integration/official-validator checks.

Gate: median paired(clean/corrupted) spell gain>0, majority of five improve, median macro delta≥−.01, median corrupted spell gain≥+.01, contract tests and repeatability. Record per-match clean losses as well as gains. Failure drops the feature and closes this bounded change; do not rescue it by adjusting window, augmentation probability, blend or seed. Long training remains user-run.

Five matches repeatedly reused across many hypotheses provide limited independent evidence. Frames overlap strongly and are not independent samples. The promotion rule is an engineering screen, not a p-value or confidence guarantee. No confidence interval, effect-size distribution or power calculation was newly computed here. The sealed November16 evaluation remains the independent check; future poor sealed scores prompt bug/transfer investigation rather than tuning.

Confidence: high in code-level receptive-field/feature-path facts; moderate that explicit interaction is a useful targeted hypothesis; low in attainable spellF1 gain or target transfer. Findings that could invalidate prioritization: current errors mainly arise from long ball gaps without distinguishable player evidence, label convention mismatch, missing identity/visibility problems, or decoder over-merging rather than observed control ambiguity.

Sources: experiments/tcn-2026-11-10/tcn_candidate.py; scripts/prepare_tcn.py; experiments/tcn-gap-2026-11-10/gap_training.py, report.md and gate.json; experiments/tcn-long-2026-11-10/report.md; research-state.yaml; ball.md. No new performance result is claimed.
