# Change 1: switching penalty 2 -> 8

Baseline evidence: 579–831 spurious clean possessions per match at IoU .5, plus 734–927 corrupted, despite clean macroF1 .846–.884. This supports flicker as frequent. One change: uniform off-diagonal Viterbi penalty 8 rather than 2, same fitted emissions, inputs, folds, seeds and budget. Hypothesis: suppress unsupported spurious spells without material macroF1 loss. No minimum duration. Gate exactly core protocol; compare against core. Short-spell recall remains reported. Commit before run.
