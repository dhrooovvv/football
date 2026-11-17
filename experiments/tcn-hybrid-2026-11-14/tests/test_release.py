"""User-run synthetic release contracts. Real models and match inputs stay closed."""
from datetime import datetime
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

PROJECT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(PROJECT / 'scripts'), str(PROJECT / 'experiments/tcn-hybrid-2026-11-14')]
spec = importlib.util.spec_from_file_location('tested_hybrid_release', PROJECT / 'scripts/release_tcn_hybrid.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def test_selection_includes_only_reviewed_accepted_stages(self):
        records = {'temporal': {'accepted': True}, 'graph': {'accepted': False}}
        with patch.object(release, 'validated_review', side_effect=lambda s, _: records[s]), \
             patch.object(release, 'sha', return_value='pinned'):
            stages, reviews = release.selected_stages('graph', 'source')
        self.assertEqual(stages, ['temporal'])
        self.assertEqual(set(reviews), {'temporal', 'graph'})

    def test_final_temporal_does_not_require_unrun_graph(self):
        review = Mock(return_value={'accepted': True})
        with patch.object(release, 'validated_review', review), patch.object(release, 'sha', return_value='pinned'):
            stages, _ = release.selected_stages('temporal', 'source')
        self.assertEqual(stages, ['temporal'])
        review.assert_called_once_with('temporal', 'source')

    def test_both_accepted_form_ordered_composite(self):
        with patch.object(release, 'validated_review', return_value={'accepted': True}), \
             patch.object(release, 'sha', return_value='pinned'):
            stages, _ = release.selected_stages('graph', 'source')
        self.assertEqual(stages, ['temporal', 'graph'])

    def test_signature_changes_with_selected_review(self):
        with patch.object(release, 'sha', return_value='pinned'), \
             patch.object(release, 'validated_review', return_value={'accepted': True}):
            first, digest = release.release_identity('temporal', 'source')
        with patch.object(release, 'sha', return_value='pinned'), \
             patch.object(release, 'validated_review', return_value={'accepted': False}):
            second, different = release.release_identity('temporal', 'source')
        self.assertNotEqual(digest, different)
        self.assertEqual(len(first['training_matches']), 5)
        self.assertEqual(second['stages'], [])
        self.assertNotIn('idsse-J03WQQ', first['training_matches'])

    def test_sealed_date_rejects_before_any_manifest_or_match_read(self):
        clock = Mock()
        clock.now.return_value = datetime(2026, 11, 15, tzinfo=ZoneInfo('Asia/Kolkata'))
        with patch.object(release, 'datetime', clock), patch.object(release, 'validate_manifest') as validate:
            with self.assertRaises(RuntimeError):
                release.sealed(Path('unused.json'), 'source', {})
        validate.assert_not_called()

    def test_stage_inference_does_not_rotate_graph_twice(self):
        import numpy as np
        parent = np.array([[.6, .3, .1]], dtype=np.float64)
        predictor = Mock(return_value=parent.copy())
        d = {'np': np, 'hybrid_model': Mock(predict=predictor),
             'average_views': Mock(side_effect=AssertionError('Identity must preserve parent bytes'))}
        with patch.object(release, 'final_model', return_value='model'):
            actual = release.apply_stage('graph', None, parent, [(0, 1)], 'source', d)
        np.testing.assert_array_equal(actual, parent)
        self.assertEqual(predictor.call_count, 2)

    def test_sealed_corruption_masks_raw_ball_before_features(self):
        import numpy as np
        from possession.inputs import Tracking
        track = Tracking(np.zeros((20, 2, 3)), np.ones((20, 3)))
        summary = {'missing_runs': [20], 'observed_runs': [1], 'missing_fraction': 1.0}
        with patch.object(release, 'load', return_value=summary):
            corrupt = release.sealed_corruption(track, [(0, 20)], 20261206, {'np': np})
        self.assertTrue(np.isnan(corrupt.ball).all())
        self.assertFalse(np.isnan(track.ball).any())


if __name__ == '__main__':
    unittest.main()
