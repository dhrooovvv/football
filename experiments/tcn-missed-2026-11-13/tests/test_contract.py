"""Synthetic contracts only; supplied for user execution, not run at preparation."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import contract as c


def cells(value=.5, macro=.8):
    return [dict(match=m, condition=condition, spellF1=value, macroF1=macro)
            for m in c.IDS for condition in c.SETTINGS]


class PositiveMedianGate(unittest.TestCase):
    def test_small_positive_gain_qualifies_but_zero_does_not(self):
        base = cells()
        self.assertTrue(c.gate_v2(base, cells(.500001))['quality_eligible'])
        self.assertFalse(c.gate_v2(base, cells())['quality_eligible'])

    def test_positive_mean_cannot_replace_positive_median(self):
        after = cells()
        for row in after:
            row['spellF1'] += .1 if row['match'] in c.IDS[:2] else -.001
        result = c.gate_v2(cells(), after)
        self.assertGreater(sum(r['spellF1'] for r in after) / 10, .5)
        self.assertEqual(result['matches_improved'], 2)
        self.assertFalse(result['quality_eligible'])

    def test_corrupted_median_and_paired_gain_are_both_required(self):
        after = cells()
        for row in after:
            row['spellF1'] += .03 if row['condition'] == 'clean' else -.01
        result = c.gate_v2(cells(), after)
        self.assertTrue(result['existing_gate'])
        self.assertFalse(result['quality_eligible'])
        for row in after:
            row['spellF1'] = .51 if row['condition'] == 'targetlike' else .47
        self.assertGreater(c.gate_v2(cells(), after)['primary_median_delta'], 0)
        self.assertFalse(c.gate_v2(cells(), after)['quality_eligible'])

    def test_macro_guard_and_runtime_proofs_remain(self):
        self.assertFalse(c.gate_v2(cells(), cells(.51, .789))['quality_eligible'])
        self.assertTrue(c.gate_v2(cells(), cells(.51, .79))['quality_eligible'])
        self.assertFalse(c.gate_v2(cells(), cells(.51), contracts=False)['quality_eligible'])
        self.assertFalse(c.gate_v2(cells(), cells(.51), repeats=False)['quality_eligible'])

    def test_duplicate_missing_nonfinite_boolean_metrics_rejected(self):
        for bad in (cells()[:-1], cells()[:-1] + [cells()[0]]):
            with self.assertRaises(RuntimeError):
                c.gate_v2(cells(), bad)
        for bad_value in (float('nan'), float('inf'), True, -1, 1.1):
            bad = cells()
            bad[0]['spellF1'] = bad_value
            with self.assertRaises(RuntimeError):
                c.gate_v2(cells(), bad)


class StorageAndReview(unittest.TestCase):
    def test_disk_guard_checks_total_and_free_space_before_write(self):
        disk = type('Disk', (), {'free': c.MIN_FREE_BYTES + c.RESERVE_BYTES})()
        with patch.object(c, 'artifact_bytes', return_value=0), patch.object(c.shutil, 'disk_usage', return_value=disk):
            self.assertEqual(c.check_storage()['artifact_bytes'], 0)
        disk.free -= 1
        with patch.object(c, 'artifact_bytes', return_value=0), patch.object(c.shutil, 'disk_usage', return_value=disk):
            with self.assertRaises(RuntimeError):
                c.check_storage()
        disk.free = 100 * 1024 ** 3
        with patch.object(c, 'artifact_bytes', return_value=c.MAX_BYTES), patch.object(c.shutil, 'disk_usage', return_value=disk):
            with self.assertRaises(RuntimeError):
                c.check_storage()

    def test_artifact_accounting_does_not_follow_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'file').write_bytes(b'123')
            with patch.object(c, 'ARTIFACT_ROOTS', (root,)):
                self.assertEqual(c.artifact_bytes(), 3)
                (root / 'link').symlink_to(root / 'file')
                with self.assertRaises(RuntimeError):
                    c.artifact_bytes()

    def test_trial_b_requires_review_and_exact_binding(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            expected = dict(registration='sig', reviewed=True, accepted=False, sampler='uniform',
                            parent_trial='baseline', parent_results_sha256='parent', a_completion_sha256='completion')
            with patch.object(c, 'R', root), patch.object(c, 'expected_review_a', return_value=expected), patch.object(c, 'committed_bytes') as committed:
                with self.assertRaises(RuntimeError):
                    c.binding('b', 'sig')
                path = root / 'reviewed-a.json'
                path.write_text(json.dumps(expected))
                got = c.binding('b', 'sig')
                self.assertEqual(got['sampler'], 'uniform')
                self.assertEqual(got['parent_trial'], 'baseline')
                self.assertEqual(got['reviewed_a_sha256'], c.sha(path))
                committed.assert_called_once_with(path)
                path.write_text(json.dumps(dict(expected, accepted=True)))
                with self.assertRaises(RuntimeError):
                    c.binding('b', 'sig')

    def test_freeze_blocks_research_at_start_of_november16(self):
        class FrozenTime:
            @staticmethod
            def now(zone):
                return type('Stamp', (), {'date': lambda self: c.date(2026, 11, 16)})()
        with patch.object(c, 'datetime', FrozenTime):
            with self.assertRaises(RuntimeError):
                c.check_date()


if __name__ == '__main__':
    unittest.main()
