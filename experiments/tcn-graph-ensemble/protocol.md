# Protocol: Frozen 50/50 Probability Ensemble of Retained Trial B TCN and Graph50k

**Date**: 2026-11-16  
**Status**: Preregistered  
**Experiment ID**: `tcn-graph-ensemble`

## 1. Objective and Scope
Evaluate a single bounded, frozen probability ensemble combining the retained Trial B TCN model and the graph50k continuation model (`experiments/graph-long-2026-11-15`) with equal (50/50) weighting. Neither model is retrained, refitted, fine-tuned, or adapted.

This experiment investigates whether probability-level ensembling between the sequence-level temporal representations (Trial B TCN) and relational spatial graph refinements (graph50k) yields complementary robustness gains under clean and targetlike corruption conditions without introducing any new learned parameters or tuned post-processing heuristics.

## 2. Model Inputs and Probability Definition
For each development match $m \in \{\text{J03WMX}, \text{J03WN1}, \text{J03WOH}, \text{J03WOY}, \text{J03WPY}\}$ and condition $c \in \{\text{clean}, \text{targetlike}\}$:

1. **Trial B TCN Out-of-Fold Probabilities ($p_{\text{tcn}}$)**:
   - Source: Frozen cached probability arrays at `data/tcn-hybrid/graph/parents/<match>/evaluation/<match>-<condition>.npy`.
   - Dimensions: $(N, 3)$, representing frame-level probabilities for classes Home (H), Away (A), and Dead (D).
   - Normalization: Row sum equals 1.0; all values finite and non-negative.

2. **Graph50k Out-of-Fold Probabilities ($p_{\text{graph50k}}$)**:
   - Source: Deterministic forward inference using frozen checkpoints from `models/graph-long-2026-11-15/<match>/<seed>/first/progress.pt` for seeds 20261106 and 20261107.
   - Forward pass: Evaluated over feature arrays `x`, `parent` ($p_{\text{tcn}}$), and match `blocks` from `data/tcn-prepared/<match>-<condition>.npz` via `hybrid_model.predict`.
   - Aggregation across seeds: Arithmetic mean across seeds 20261106 and 20261107 (`average_views`).
   - Dimensions: $(N, 3)$, with identical frame indexing, block boundaries, and team semantics.

3. **Ensemble Probability Combination**:
   $$p_{\text{ensemble}} = 0.5 \cdot p_{\text{tcn}} + 0.5 \cdot p_{\text{graph50k}}$$
   - Normalization verification: Explicit check that $\sum_{k \in \{H, A, D\}} p_{\text{ensemble}}(t, k) = 1.0$ within floating point tolerance ($10^{-5}$), with clipping/renormalization if non-finite or drifting.
   - Row alignment: Frame counts, team mapping, half/block boundaries must match identically.

## 3. Decoding and Scoring
1. **Decoder**:
   - Exact unchanged frozen Viterbi dynamic programming decoder (`possession.decode.decode`).
   - Transition penalty matrix: $(1 - I_3) \times 16$, where penalty is 16 for any state change, 0 for self-transition.
   - Segmented strictly per half/block as defined in `blocks`.
   - No threshold tuning, penalty search, duration filtering, or heuristic post-filtering.

2. **Scoring**:
   - Unchanged official competition evaluation scorer (`possession_metrics` / `review_frozen.score` / `evaluate_pff`).
   - Metrics computed per match and condition:
     - Spell-level F1, Precision, Recall at IoU thresholds 0.3, 0.4, 0.5, 0.6, 0.7 (official primary is mean over IoU thresholds 0.3:0.7).
     - Frame-level Macro F1 (average across H, A, D).
     - Error diagnostics: short-spell recall (IoU 0.5), missed spells, spurious spells, dead/live misclassification frames.
     - Paired clean/targetlike deltas against both Trial B TCN and Graph50k.

## 4. Benchmark Comparators
The ensemble will be compared against both frozen constituents under identical evaluation splits and corruption conditions:
1. **Trial B TCN** (Parent): Baseline retained from `experiments/tcn-missed-2026-11-13` / `experiments/graph-long-2026-11-15`.
2. **Graph50k** (Candidate): 50,000-step graph refiner from `experiments/graph-long-2026-11-15`.

## 5. Promotion Gate (Gate v2 Criteria)
Evaluation against the preregistered promotion gate v2 (defined in `hybrid_contract.py` / `research-state.yaml`):
1. **Primary Corrupted Median Delta**: Median of $( \text{spellF1}_{\text{ensemble}}^{\text{targetlike}} - \text{spellF1}_{\text{baseline}}^{\text{targetlike}} ) > 0$ (strictly positive).
2. **Paired Median Spell Delta**: Median of $\frac{1}{2}\Delta_{\text{clean}} + \frac{1}{2}\Delta_{\text{targetlike}} > 0$.
3. **Paired Match Wins**: $\ge 3$ of 5 development matches improve on paired spell F1.
4. **Paired Median Macro Delta**: Median of $\frac{1}{2}\Delta\text{macro}_{\text{clean}} + \frac{1}{2}\Delta\text{macro}_{\text{targetlike}} \ge -0.01$.
5. **Exact Repeatability**: Re-running full evaluation independently must produce byte-identical prediction CSVs (verified by SHA256 digest equality).

Both comparators (Trial B TCN and Graph50k) will be evaluated against these gate criteria.

## 6. Prohibited Actions and Boundary Safeguards
- **No Retraining or Fitting**: Absolutely no gradient updates, weight adjustments, or learning on any partition.
- **No Hyperparameter Search**: Fixed mixing weight (0.5 / 0.5) and fixed transition penalty (16). No grid search, Bayesian optimization, or post hoc selection.
- **No Access to Sealed Matches**: Matches `J03WQQ` and `J03WR9` remain strictly sealed and untouched.
- **No Tuning on Target/Public Competition Labels**: No test/public label access or tuning.
- **No Automatic Promotion or Submission**: Results will be reported with exact gate outcomes. No automatic promotion to production, export replacement, or external submission.
- **Reference Scorer Preserved**: No alterations to scoring formulas, tolerance windows, or metric contracts.
