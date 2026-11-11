"""User-run rotation semantics and fixed-probability-average contracts."""
import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rotation import rotate180, average_views


class Rotation(unittest.TestCase):
    def make(self):
        rng = np.random.default_rng(64)
        x = rng.normal(size=(17, 521)).astype(np.float32)
        o = x[:, :512].reshape(17, 64, 8)
        o[:, :, 4:] = 0
        o[:, :3, 4:6] = 1
        o[:, 3:6, 4] = 1
        o[:, 3:6, 6] = 1
        o[:, 63, 4] = 1
        o[:, 63, 7] = 1
        o[3:5, :2, :5] = 0
        return x

    def test_involution_dtype_and_no_input_mutation(self):
        x = self.make(); before = x.copy()
        changed = rotate180(x)
        self.assertEqual(changed.dtype, x.dtype)
        np.testing.assert_array_equal(rotate180(changed), x)
        np.testing.assert_array_equal(x, before)
        self.assertFalse(np.shares_memory(changed, x))

    def test_only_centered_geometry_and_velocity_change(self):
        x = self.make(); changed = rotate180(x)
        a = x[:, :512].reshape(17, 64, 8)
        b = changed[:, :512].reshape(17, 64, 8)
        np.testing.assert_array_equal(b[:, :, :4], -a[:, :, :4])
        np.testing.assert_array_equal(b[:, :, 4:], a[:, :, 4:])
        np.testing.assert_array_equal(changed[:, -9:], x[:, -9:])
        # H/A flags, observation masks, ball role and gap age have no relabelling.
        np.testing.assert_array_equal(b[:, :, 5:8], a[:, :, 5:8])

    def test_raw_synthetic_tracking_encoding_agrees(self):
        from prepare_tcn import encode
        from possession.inputs import Tracking
        from possession.core import features
        n = 12; teams = np.array([0, 0, 1, 1]); blocks = [(0, 6), (6, 12)]
        players = np.zeros((n, 4, 3), float)
        for slot in range(4):
            players[:, slot, 0] = (16 + slot * 20 + np.arange(n)) / 128
            players[:, slot, 1] = (24 + slot * 16 - np.arange(n)) / 128
        ball = np.zeros((n, 3), float)
        ball[:, 0] = (40 + np.arange(n)) / 128
        ball[:, 1] = (48 - np.arange(n)) / 128
        players[7:9, 2, :2] = np.nan; ball[3:5, :2] = np.nan
        track = Tracking(players, ball)
        rp, rb = players.copy(), ball.copy()
        rp[:, :, :2] = 1 - rp[:, :, :2]; rb[:, :2] = 1 - rb[:, :2]
        reflected = Tracking(rp, rb); pitch = np.array([105., 68.])
        core, names = features(track, teams, blocks, pitch)
        rotated_core, rotated_names = features(reflected, teams, blocks, pitch)
        self.assertEqual(names, rotated_names)
        np.testing.assert_allclose(core, rotated_core, atol=1e-6, rtol=0, equal_nan=True)
        first = encode(track, teams, blocks, core)
        second = encode(reflected, teams, blocks, rotated_core)
        np.testing.assert_allclose(rotate180(first), second, atol=1e-6, rtol=0)

    def test_equal_average_is_group_invariant_without_column_swap(self):
        x = self.make()
        def fake_probabilities(values):
            logits = np.column_stack((values[:, 0], values[:, 1], values[:, 2])).astype(np.float64)
            p = np.exp(logits - logits.max(1, keepdims=True))
            return p / p.sum(1, keepdims=True)
        a = fake_probabilities(x); b = fake_probabilities(rotate180(x))
        np.testing.assert_array_equal(average_views(a, b), average_views(b, a))
        p = np.tile(np.array([.7, .2, .1]), (len(x), 1))
        np.testing.assert_allclose(average_views(p, p), p, atol=1e-15, rtol=0)
        self.assertEqual(np.argmax(average_views(p, p)[0]), 0)

    def test_malformed_inputs_and_probabilities_fail(self):
        x = self.make()
        for wrong in (x[:, :-1], x[0], x.astype(int)):
            with self.assertRaises(ValueError): rotate180(wrong)
        x[0, 0] = np.nan
        with self.assertRaises(ValueError): rotate180(x)
        for a, b in ((np.ones((2, 2)), np.ones((2, 2))),
                     (np.ones((2, 3)), np.ones((2, 3))),
                     (np.array([[1., -1., 1.]]), np.array([[1., 0., 0.]]))):
            with self.assertRaises(ValueError): average_views(a, b)


if __name__ == '__main__':
    unittest.main()
