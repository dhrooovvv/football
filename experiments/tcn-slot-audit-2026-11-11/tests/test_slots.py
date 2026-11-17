"""Synthetic user-run contracts for external-only slot stress."""
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from slot_transforms import permute_slots


class Slots(unittest.TestCase):
    def make(self):
        x = np.zeros((12, 521), np.float32)
        objects = x[:, :512].reshape(12, 64, 8)
        objects[:, :3, 5] = 1
        objects[:, 3:6, 6] = 1
        objects[:, 63, 7] = 1
        objects[:, :6, 4] = 1
        objects[:, 63, 4] = 1
        for slot in range(6):
            objects[:, slot, 0] = slot / 10 + np.arange(12) / 100
        x[:, -9:] = np.arange(9)
        return x

    def test_preserves_team_sets_ball_core_and_input(self):
        x = self.make(); before = x.copy()
        for mode in ("static", "dynamic", "rederived_identity"):
            y = permute_slots(x, [(0, 6), (6, 12)], 88, mode)
            a = x[:, :512].reshape(12, 64, 8)
            b = y[:, :512].reshape(12, 64, 8)
            np.testing.assert_array_equal(y[:, -9:], x[:, -9:])
            np.testing.assert_array_equal(b[:, -1], a[:, -1])
            np.testing.assert_array_equal(b[:, :, 5:8], a[:, :, 5:8])
            for frame in range(12):
                for slots in (slice(0, 3), slice(3, 6)):
                    np.testing.assert_array_equal(np.sort(a[frame, slots, 0]),
                                                  np.sort(b[frame, slots, 0]))
        np.testing.assert_array_equal(x, before)

    def test_seed_exact_and_dynamic_churn(self):
        x = self.make()
        a = permute_slots(x, [(0, 12)], 17, "dynamic")
        b = permute_slots(x, [(0, 12)], 17, "dynamic")
        np.testing.assert_array_equal(a, b)
        self.assertFalse(np.array_equal(a, permute_slots(x, [(0, 12)], 17, "static")))

    def test_velocity_masks_half_reset_and_clip(self):
        x = self.make(); o = x[:, :512].reshape(12, 64, 8)
        o[3, :6, 4] = 0
        o[3, :6, :2] = 0
        y = permute_slots(x, [(0, 6), (6, 12)], 15, "dynamic")
        p = y[:, :512].reshape(12, 64, 8)
        for frame in (0, 3, 4, 6):
            np.testing.assert_array_equal(p[frame, :6, 2:4], 0)
        self.assertTrue((np.abs(p[:, :6, 2:4]) <= 5).all())
        valid = (p[2, :6, 4] == 1) & (p[1, :6, 4] == 1)
        expected = np.clip((p[2, :6, :2] - p[1, :6, :2]) * 12.5, -5, 5)
        np.testing.assert_array_equal(p[2, :6, 2:4], np.where(valid[:, None], expected, 0))

    def test_identity_control_preserves_order(self):
        x = self.make()
        y = permute_slots(x, [(0, 12)], 44, "rederived_identity")
        a = x[:, :512].reshape(12, 64, 8)
        b = y[:, :512].reshape(12, 64, 8)
        np.testing.assert_array_equal(a[:, :, :2], b[:, :, :2])
        np.testing.assert_array_equal(a[:, :, 4:], b[:, :, 4:])
        np.testing.assert_allclose(b[1:, :6, 2], .125, atol=1e-6)

    def test_bad_shape_roles_and_blocks(self):
        x = self.make()
        with self.assertRaises(ValueError): permute_slots(x[:, :-1], [(0, 12)], 1)
        with self.assertRaises(ValueError): permute_slots(x, [(3, 14)], 1)
        x[2, 5] = 0
        with self.assertRaises(ValueError): permute_slots(x, [(0, 12)], 1)


if __name__ == '__main__':
    unittest.main()
