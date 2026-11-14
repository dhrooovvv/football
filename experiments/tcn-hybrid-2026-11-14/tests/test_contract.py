"""Synthetic provenance, budget and date contracts. User execution only."""
from datetime import datetime
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hybrid_contract as contract


def scores(delta=0.):
    return [dict(match=m, condition=c, spellF1=.5+delta, macroF1=.8)
            for m in contract.IDS for c in contract.SETTINGS]


class HybridContractTests(unittest.TestCase):
    def test_positive_gain_gate_and_exact_tie(self):
        self.assertTrue(contract.gate_v2(scores(), scores(.0001))['quality_eligible'])
        self.assertFalse(contract.gate_v2(scores(), scores())['quality_eligible'])

    def test_macro_and_majority_guards_remain(self):
        after = scores(.01)
        for row in after:
            row['macroF1'] = .78
        self.assertFalse(contract.gate_v2(scores(), after)['quality_eligible'])
        after = scores()
        for row in after:
            row['spellF1'] += .01 if row['match'] in contract.IDS[:2] else -.001
        self.assertFalse(contract.gate_v2(scores(), after)['quality_eligible'])

    def test_reproduction_evidence_required(self):
        self.assertFalse(contract.gate_v2(scores(), scores(.01), contracts=False)['quality_eligible'])
        self.assertFalse(contract.gate_v2(scores(), scores(.01), repeats=False)['quality_eligible'])

    def test_serial_final_work_not_divided_by_worker_count(self):
        now = datetime(2026, 11, 14, tzinfo=ZoneInfo('Asia/Kolkata'))
        row = contract.deadline_projection(.01, 100, 2, included_branches=2, now=now)
        self.assertAlmostEqual(row['projected_seconds'], 1.5*(.01*40000*(20/2+8)+100))
        self.assertTrue(row['projected_to_finish'])
        late = datetime(2026, 11, 15, 23, 59, tzinfo=ZoneInfo('Asia/Kolkata'))
        self.assertFalse(contract.deadline_projection(.01, 100, 2, now=late)['projected_to_finish'])

    def test_projection_rejects_invalid_measurements(self):
        for value in (0, -1, float('nan'), float('inf')):
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                contract.deadline_projection(value, 0, 2)

    def test_projected_storage_counts_histories_csvs_and_final_fits(self):
        with patch.object(contract, 'check_storage', return_value=dict(artifact_bytes=1000, free_bytes=20*1024**3)):
            one = contract.artifact_projection(1000, 1)
            two = contract.artifact_projection(1000, 2)
        self.assertEqual(two['projected_additional_bytes']-one['projected_additional_bytes'], 4*8*1024**2)
        self.assertTrue(one['within_budget'])
        with patch.object(contract, 'check_storage', return_value=dict(artifact_bytes=contract.MAX_BYTES, free_bytes=20*1024**3)):
            self.assertFalse(contract.artifact_projection(1000)['within_budget'])

    def test_graph_requires_committed_review(self):
        with patch.object(contract, 'sha', return_value='hash'), patch.object(Path, 'is_file', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'Graph waits'):
                contract.stage_binding('graph', 'source')
        with self.assertRaises(RuntimeError):
            contract.stage_binding('unknown', 'source')

    def test_temporal_binding_is_frozen_baseline(self):
        with patch.object(contract, 'sha', return_value='hash'):
            value = contract.stage_binding('temporal', 'source')
        self.assertEqual(value['parent'], 'trial_b')
        self.assertFalse(value['temporal_selected'])


if __name__ == '__main__':
    unittest.main()
