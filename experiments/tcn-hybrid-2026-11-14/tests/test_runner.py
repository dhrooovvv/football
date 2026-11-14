"""Small serializer/cache/decision tests, without real model or match access."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path('scripts').resolve()), str(Path(__file__).resolve().parents[1])]
import run_tcn_hybrid as runner


class Labels:
    def tolist(self):
        return list('HADX')


class RunnerTests(unittest.TestCase):
    def test_serializer_matches_official_zero_based_export(self):
        expected = hashlib.sha256(b'frame,label\n0,H\n1,A\n2,D\n3,X\n').hexdigest()
        self.assertEqual(runner.csv_digest(Labels()), expected)

    def test_training_cache_rejects_held_out(self):
        with self.assertRaises(RuntimeError):
            runner.cache_paths('temporal', 'J03WMX', 'J03WMX', 'clean', 'training')
        _, path = runner.cache_paths('temporal', 'J03WMX', 'J03WN1', 'gap', 'training')
        self.assertIn('training', path.parts)

    def test_cache_paths_are_separate_by_fold_and_training_evaluation(self):
        a = runner.cache_paths('temporal', 'J03WMX', 'J03WN1', 'clean', 'training')[0]
        b = runner.cache_paths('temporal', 'J03WOH', 'J03WN1', 'clean', 'training')[0]
        c = runner.cache_paths('temporal', 'J03WN1', 'J03WN1', 'clean', 'evaluation')[0]
        self.assertEqual(len({a, b, c}), 3)

    def test_cache_membership_and_view_restrictions(self):
        for stage, key, view in (('invalid', 'J03WMX', 'clean'),
                                 ('temporal', 'J03WQQ', 'clean'),
                                 ('temporal', 'J03WMX', 'public')):
            with self.subTest(stage=stage, key=key, view=view), self.assertRaises(RuntimeError):
                runner.cache_paths(stage, 'J03WN1', key, view, 'training')

    def test_parent_result_bytes_must_match_binding(self):
        with patch.object(runner, 'sha', return_value='changed'):
            with self.assertRaises(RuntimeError):
                runner.parent_rows(dict(temporal_selected=False, parent_results_sha256='registered'))

    def test_missing_preflight_blocks_full_run(self):
        with patch.object(Path, 'is_file', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'preflight'):
                runner.verify_preflight('temporal', 'signature', {}, 2)

    def test_fit_proof_rejects_wrong_identity_before_checkpoint_load(self):
        value = dict(stage='graph', held_out='J03WMX', seed=20261106, signature='source',
                     exact_repeat=True, steps=40000,
                     training_matches=['idsse-'+m for m in runner.IDS if m != 'J03WMX'])
        with patch.object(Path, 'exists', return_value=True), patch.object(runner, 'load', return_value=value):
            with self.assertRaisesRegex(RuntimeError, 'identity'):
                runner.verify_fit('temporal', 'J03WMX', 20261106, 'source')


if __name__ == '__main__':
    unittest.main()
