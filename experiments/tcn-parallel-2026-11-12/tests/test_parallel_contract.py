"""Synthetic aggregate-gate contracts; user executes, no match assets needed."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parallel_contract import IDS, SETTINGS, gate, ordered_decision


def rows(spell=.4, macro=.8):
    return [dict(match=m, condition=c, spellF1=spell, macroF1=macro) for m in IDS for c in SETTINGS]


class Gates(unittest.TestCase):
    def test_positive_mean_cannot_bypass_primary_median(self):
        parent, candidate = rows(), rows(.405)
        self.assertFalse(gate(parent, candidate)['quality_eligible'])
        for row in candidate[:2]: row['spellF1'] = .8
        self.assertFalse(gate(parent, candidate)['quality_eligible'])

    def test_macro_and_reproducibility_gates_are_required(self):
        self.assertTrue(gate(rows(), rows(.42))['quality_eligible'])
        self.assertFalse(gate(rows(), rows(.42, .78))['quality_eligible'])
        self.assertFalse(gate(rows(), rows(.42), contracts=False)['quality_eligible'])
        self.assertFalse(gate(rows(), rows(.42), repeats=False)['quality_eligible'])

    def test_duplicate_or_missing_cells_are_rejected(self):
        with self.assertRaises(RuntimeError): gate(rows(), rows()[:-1])
        bad = rows(); bad[-1] = bad[0]
        with self.assertRaises(RuntimeError): gate(rows(), bad)

    def test_parallel_screens_do_not_override_ordered_promotion(self):
        parent, attention, ensemble = rows(), rows(.43), rows(.435)
        self.assertTrue(gate(parent, ensemble)['quality_eligible'])
        decision = ordered_decision(parent, attention, ensemble)
        self.assertEqual(decision['ensemble_compared_against'], 'attention')
        self.assertFalse(decision['ensemble_vs_current_best']['quality_eligible'])
        self.assertEqual(decision['selected_development_candidate'], 'attention')
        self.assertFalse(decision['combined_attention_ensemble_tested'])

    def test_failed_attention_keeps_original_parent_for_second_candidate(self):
        result = ordered_decision(rows(), rows(.39), rows(.42))
        self.assertEqual(result['ensemble_compared_against'], 'parent')
        self.assertEqual(result['selected_development_candidate'], 'ensemble')


if __name__ == '__main__': unittest.main()
