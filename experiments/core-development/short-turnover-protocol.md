# Change 3: preserve short H/A turnovers

Current best penalty8 substantially reduced short-spell recall on all clean development matches. Test exactly one asymmetric decoder adjustment: H->A and A->H cost 4; all transitions involving D remain cost8. Same core emissions, models, folds, seeds, features. No minimum duration. Hypothesis: recover short handovers while retaining stoppage smoothing. Compare against penalty8, not rejected mean-speed. Gate and metrics unchanged. No lookahead: matched boundaries are predominantly early, not late. Commit before run.
