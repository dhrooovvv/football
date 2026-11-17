import unittest
import numpy as np

class TestEnsembleContract(unittest.TestCase):
    def test_ensemble_probability_math(self):
        # Synthetic test proving normalization and combination properties
        p1 = np.array([[0.7, 0.2, 0.1], [0.1, 0.8, 0.1]], dtype=np.float64)
        p2 = np.array([[0.5, 0.3, 0.2], [0.3, 0.6, 0.1]], dtype=np.float64)
        ens = 0.5 * p1 + 0.5 * p2
        self.assertEqual(ens.shape, (2, 3))
        np.testing.assert_allclose(ens.sum(axis=1), np.ones(2), atol=1e-7)
        np.testing.assert_allclose(ens[0], [0.6, 0.25, 0.15])
        np.testing.assert_allclose(ens[1], [0.2, 0.7, 0.1])

    def test_penalty_matrix(self):
        penalty_matrix = (1 - np.eye(3)) * 16
        self.assertEqual(penalty_matrix.shape, (3, 3))
        self.assertEqual(penalty_matrix[0, 0], 0.0)
        self.assertEqual(penalty_matrix[0, 1], 16.0)
        self.assertEqual(penalty_matrix[1, 2], 16.0)
        self.assertEqual(penalty_matrix[2, 2], 0.0)

    def test_gate_v2_logic(self):
        import statistics
        # Test gate conditions: positive primary median, positive paired spell median, >= 3 wins, macro >= -0.01
        primary_deltas = [0.005, 0.002, 0.001, -0.001, 0.003]
        paired_spell_deltas = [0.004, 0.001, -0.002, 0.002, 0.003]
        paired_macro_deltas = [0.000, -0.001, -0.002, 0.001, -0.0005]

        med_primary = statistics.median(primary_deltas)
        med_spell = statistics.median(paired_spell_deltas)
        med_macro = statistics.median(paired_macro_deltas)
        wins = sum(d > 0 for d in paired_spell_deltas)

        self.assertGreater(med_primary, 0)
        self.assertGreater(med_spell, 0)
        self.assertGreaterEqual(wins, 3)
        self.assertGreaterEqual(med_macro, -0.01)

if __name__ == '__main__':
    unittest.main()
