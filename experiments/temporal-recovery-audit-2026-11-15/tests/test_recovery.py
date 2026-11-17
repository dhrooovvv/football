import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'experiments/temporal-recovery-audit-2026-11-15'),
               str(ROOT/'experiments/tcn-diagnostic-2026-11-13'),
               str(ROOT/'reference/more-than-a-hack-2027-main/evaluation')]
import numpy as np
import recovery
import diagnostics
import possession_metrics as official


class RecoveryContracts(unittest.TestCase):
    def test_auc_ties_and_direction(self):
        self.assertEqual(recovery.auc([2, 3], [0, 1]), 1)
        self.assertEqual(recovery.auc([0], [1]), 0)
        self.assertEqual(recovery.auc([1], [1]), .5)

    def test_auc_absent_class(self):
        self.assertIsNone(recovery.auc([], [1]))
        self.assertIsNone(recovery.auc([1], []))

    def test_string_and_numeric_label_equivalence(self):
        strings = np.array(['H', 'A', 'D', 'X'])
        codes = np.arange(4, dtype=np.int64)
        np.testing.assert_array_equal(recovery.label_codes(strings, official), codes)
        np.testing.assert_array_equal(recovery.label_codes(codes, official), codes)

    def test_invalid_numeric_labels_rejected(self):
        for values in ([-1], [4], [[0, 1]], ['0']):
            with self.assertRaises(ValueError):
                recovery.label_codes(values, official)

    def records(self, y, before, after, blocks=None):
        y, before, after = map(lambda v: np.array(v, dtype=np.int8), (y, before, after))
        parent, temporal = np.eye(3)[before], np.eye(3)[after]
        return recovery.spell_records(y, before, after, parent, temporal, [temporal, temporal],
            np.zeros(len(y), bool), blocks or [[0, len(y)]], official, diagnostics)

    def test_recovered_complete_spell(self):
        rows = self.records([0]*6+[2]*6, [2]*12, [0]*6+[2]*6)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['category'], 'recovered')
        self.assertEqual(rows[0]['parent_team_margin'], -1)
        self.assertEqual(rows[0]['member_agreement'], 1)

    def test_introduced_and_persistent_spurious(self):
        rows = self.records([2]*12, [2]*6+[1]*6, [0]*6+[1]*6)
        self.assertEqual([r['category'] for r in rows], ['introduced_spurious', 'persistent_spurious'])

    def test_unknown_and_half_boundaries(self):
        rows = self.records([0]*3+[3]*2+[0]*3+[1]*4,
            [2]*12, [0]*8+[1]*4, [[0, 8], [8, 12]])
        self.assertEqual([(r['start'], r['stop']) for r in rows], [(0,3), (5,8), (8,12)])
        self.assertTrue(all(r['category'] == 'recovered' for r in rows))

    def test_preserved_truth_is_not_new_recovery(self):
        rows = self.records([0]*12, [0]*12, [0]*12)
        self.assertEqual(rows[0]['category'], 'preserved_true')

    def test_loss_stages_not_conflated(self):
        result = recovery.loss_summary([1]*20000+[2]*20000)
        self.assertEqual(result[0]['last_1000_mean'], 1)
        self.assertEqual(result[1]['first_1000_mean'], 2)
        self.assertEqual(result[1]['late_5000_change'], 0)
        with self.assertRaises(ValueError):
            recovery.loss_summary([1]*39999)

    def test_empty_spells_no_invented_separability(self):
        rows = self.records([2]*12, [2]*12, [2]*12)
        summary = recovery.summarize(rows)
        self.assertEqual(summary['counts'], {})
        self.assertIsNone(summary['signals']['parent_team_margin']['recovered_vs_introduced_spurious_auc'])


if __name__ == '__main__':
    unittest.main()
