"""User-run synthetic invariance, temporal-boundary and training-state contracts."""
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import set_model as model_code
import set_training as training
from set_model import TCN, predict, WIDTH, WINDOW, HALO, CORE, RADIUS, RECEPTIVE_FIELD
from possession.decode import decode


def make_case(key='idsse-synthetic', unknown=False):
    rng = np.random.default_rng(41)
    objects = np.zeros((600, 64, 8), dtype=np.float32)
    for slot in (0, 1, 2, 3, 63):
        objects[:, slot, :4] = rng.normal(size=(600, 4))
        objects[:, slot, 4] = 1
    objects[:, :2, 5] = 1
    objects[:, 2:4, 6] = 1
    objects[:, 63, 7] = 1
    objects[110:130, 0, :5] = 0
    clean = np.column_stack((objects.reshape(600, 512), rng.normal(size=(600, 9)).astype(np.float32)))
    gap = clean.copy()
    gap[100:200, 63 * 8:63 * 8 + 5] = 0
    gap[100:200, -9:] = 0
    labels = np.resize(np.arange(3, dtype=np.int8), 600)
    if unknown:
        labels[50:70] = -1
    reader = lambda indices, augmented: (gap if augmented else clean)[indices]
    case = SimpleNamespace(key=key, provider='idsse', labels=labels,
                           blocks=[(0, 300), (300, 600)], read=reader)
    return case, clean


class SetContracts(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.backends.mkldnn.enabled = False
        torch.use_deterministic_algorithms(True)
        torch.manual_seed(20261106)
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_capacity_schema_and_temporal_field(self):
        model = TCN()
        self.assertEqual(sum(p.numel() for p in model.parameters()), 9539)
        self.assertEqual(model.object.in_features, 3)
        self.assertEqual(model.object.out_features, 8)
        self.assertEqual(model_code.OBJECT_CHANNELS, (0, 1, 4))
        self.assertEqual((WIDTH, WINDOW, HALO, CORE, RADIUS, RECEPTIVE_FIELD),
                         (521, 250, 25, 200, 7, 15))
        self.assertGreaterEqual(HALO, RADIUS)
        with self.assertRaisesRegex(ValueError, '521'):
            model(torch.zeros(1, 20, 520))

    def test_independent_framewise_same_team_permutations(self):
        _, original = make_case()
        changed = original.copy()
        before = original[:, :512].reshape(600, 64, 8)
        after = changed[:, :512].reshape(600, 64, 8)
        rng = np.random.default_rng(231)
        for frame in range(len(original)):
            for team in ([0, 1], [2, 3]):
                after[frame, team] = before[frame, rng.permutation(team)]
        # Adversarial supplied velocities may change at the identity switch.
        after[:, :, 2:4] = rng.normal(size=after[:, :, 2:4].shape) * 100
        model = TCN().eval()
        with torch.no_grad():
            a = model(torch.from_numpy(original[None]))
            b = model(torch.from_numpy(changed[None]))
        torch.testing.assert_close(a, b, atol=1e-6, rtol=1e-5)
        np.testing.assert_array_equal(original[:, -9:], changed[:, -9:])
        np.testing.assert_array_equal(before[:, -1, [0, 1, 4, 5, 6, 7]],
                                      after[:, -1, [0, 1, 4, 5, 6, 7]])

    def test_stored_object_velocity_is_completely_ignored(self):
        _, original = make_case()
        changed = original.copy()
        objects = changed[:, :512].reshape(600, 64, 8)
        objects[:, :, 2:4] = 12345
        model = TCN().eval()
        with torch.no_grad():
            a = model(torch.from_numpy(original[None]))
            b = model(torch.from_numpy(changed[None]))
        self.assertTrue(torch.equal(a, b))

    def test_masked_and_unassigned_coordinates_do_not_reach_pool(self):
        _, original = make_case()
        changed = original.copy()
        objects = changed[:, :512].reshape(600, 64, 8)
        # Slot0 is absent in these rows; slot12 has no team/ball role at any row.
        objects[110:130, 0, :4] = 987
        objects[:, 12, :4] = -123
        objects[:, 12, 4] = 1
        model = TCN().eval()
        with torch.no_grad():
            a = model(torch.from_numpy(original[None]))
            b = model(torch.from_numpy(changed[None]))
        self.assertTrue(torch.equal(a, b))

    def test_parent_window_and_central_label_support(self):
        case, _ = make_case(unknown=True)
        records = training.valid_windows([case], WINDOW)
        self.assertEqual(records, [(0, 300, 51)])
        for match_index, first, count in records:
            self.assertEqual(match_index, 0)
            for start in (first, first + count - 1):
                self.assertTrue((case.labels[start:start + WINDOW] >= 0).all())
                self.assertEqual(len(case.labels[start + HALO:start + HALO + CORE]), CORE)
        case.provider = 'pff'
        with self.assertRaisesRegex(ValueError, 'IDSSE'):
            training.train_fit([case], self.root / 'forbidden', 'synthetic', steps=2)
        case.provider = 'idsse'; case.key = 'idsse-J03WQQ'
        with self.assertRaisesRegex(ValueError, 'Sealed'):
            training.train_fit([case], self.root / 'sealed', 'synthetic', steps=2)

    def test_half_clipped_chunks_match_extended_whole_half(self):
        _, values = make_case()
        blocks = [(0, 300), (300, 600)]
        model = TCN().eval()
        scaler = np.zeros(WIDTH), np.ones(WIDTH)
        chunked = predict(model, values, blocks, scaler)
        for start, stop in blocks:
            indices = np.clip(np.arange(start - HALO, stop + HALO), start, stop - 1)
            with torch.no_grad():
                logits = model(torch.from_numpy(values[indices][None]))
                whole = torch.softmax(logits, dim=-1).numpy()[0, HALO:HALO + stop - start]
            np.testing.assert_allclose(chunked[start:stop], whole, atol=1e-6, rtol=0)
        modified = values.copy(); modified[300:] *= 10
        other = predict(model, modified, blocks, scaler)
        np.testing.assert_array_equal(chunked[:300], other[:300])

    def test_reload_batch_and_uncovered_frame_contracts(self):
        _, values = make_case()
        blocks = [(5, 295), (305, 595)]
        model = TCN().eval()
        path = self.root / 'synthetic.pt'
        torch.save(model.state_dict(), path)
        loaded = TCN().eval()
        loaded.load_state_dict(torch.load(path, map_location='cpu', weights_only=True))
        scaler = np.zeros(WIDTH), np.ones(WIDTH)
        first = predict(model, values, blocks, scaler)
        reloaded = predict(loaded, values, blocks, scaler)
        np.testing.assert_array_equal(first, reloaded)
        batched = predict(model, values, blocks, scaler, batch=4)
        cost = (1 - np.eye(3)) * 16
        labels = decode(first, cost, blocks)
        np.testing.assert_array_equal(labels, decode(batched, cost, blocks))
        outside = np.ones(len(values), bool)
        for start, stop in blocks: outside[start:stop] = False
        self.assertTrue((labels[outside] == 'X').all())

    def test_repeat_fit_and_interruption_restore_exact_state(self):
        case, _ = make_case()
        reference, losses, coverage = training.train_fit(
            [case], self.root / 'reference', 'synthetic', steps=4, save_every=2)
        repeated, other_losses, other_coverage = training.train_fit(
            [case], self.root / 'repeat', 'synthetic', steps=4, save_every=2)
        training.confirm_repeat(reference, repeated, losses, other_losses, coverage, other_coverage)
        writer = training.write_checkpoint
        def interrupt(path, payload):
            writer(path, payload)
            if payload['step'] == 2: raise KeyboardInterrupt()
        with patch.object(training, 'write_checkpoint', interrupt):
            with self.assertRaises(KeyboardInterrupt):
                training.train_fit([case], self.root / 'resumed', 'synthetic', steps=4, save_every=2)
        resumed, resumed_losses, resumed_coverage = training.train_fit(
            [case], self.root / 'resumed', 'synthetic', steps=4, save_every=2)
        training.confirm_repeat(reference, resumed, losses, resumed_losses, coverage, resumed_coverage)
        self.assertEqual(sum(sum(v.values()) for v in coverage.values()), 32)
        with self.assertRaisesRegex(RuntimeError, 'identity'):
            training.train_fit([case], self.root / 'resumed', 'different', steps=4, save_every=2)
        case.key = 'idsse-other-synthetic'
        with self.assertRaisesRegex(RuntimeError, 'identity'):
            training.train_fit([case], self.root / 'resumed', 'synthetic', steps=4, save_every=2)


if __name__ == '__main__':
    unittest.main()
