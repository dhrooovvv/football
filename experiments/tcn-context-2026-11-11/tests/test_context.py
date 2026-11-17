"""Synthetic context, parent-anchor and checkpoint contracts; user-run only."""
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import context_model as model_code
import context_training as training
from context_model import TCN, predict, WIDTH, HALO, CORE, RADIUS, RECEPTIVE_FIELD, DILATIONS
from possession.decode import decode


def make_case(key="idsse-synthetic", unknown=False):
    rng = np.random.default_rng(41)
    objects = np.zeros((600, 64, 8), dtype=np.float32)
    for slot in (0, 1, 2, 3, 63):
        objects[:, slot, :4] = rng.normal(size=(600, 4))
        objects[:, slot, 4] = 1
    objects[:, :2, 5] = 1
    objects[:, 2:4, 6] = 1
    objects[:, 63, 7] = 1
    clean = np.column_stack((objects.reshape(600, 512), rng.normal(size=(600, 9)).astype(np.float32)))
    gap = clean.copy()
    gap[100:200, 63 * 8:63 * 8 + 5] = 0
    gap[100:200, -9:] = 0
    labels = np.resize(np.arange(3, dtype=np.int8), 600)
    if unknown:
        labels[:100] = -1
    reader = lambda indices, augmented: (gap if augmented else clean)[indices]
    return SimpleNamespace(key=key, provider="idsse", labels=labels,
                           blocks=[(0, 300), (300, 600)], read=reader), clean


class ContextContracts(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.backends.mkldnn.enabled = False
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_dense_field_and_declared_capacity(self):
        support = {-1, 0, 1}  # The object k3 layer precedes the temporal layers.
        for dilation in DILATIONS:
            support = {value + offset for value in support for offset in (-dilation, 0, dilation)}
        self.assertEqual(support, set(range(-162, 163)))
        self.assertEqual((RADIUS, RECEPTIVE_FIELD, HALO, CORE, model_code.WINDOW), (162, 325, 163, 200, 526))
        self.assertGreaterEqual(HALO, RADIUS)
        self.assertEqual(sum(parameter.numel() for parameter in TCN().parameters()), 15843)

    def test_anchor_support_and_rng_mapping_equal_parent(self):
        case, _ = make_case()
        windows = training.training_windows([case])
        old = training.valid_windows([case], 250)
        self.assertEqual([record[:3] for record in windows], old)
        cumulative = np.cumsum([record[2] for record in old])
        parent_rng = np.random.default_rng(20261106)
        context_rng = np.random.default_rng(20261106)
        for _ in range(3):
            expected_draws = parent_rng.integers(0, int(cumulative[-1]), size=8)
            actual_draws = context_rng.integers(0, int(cumulative[-1]), size=8)
            np.testing.assert_array_equal(expected_draws, actual_draws)
            for draw in actual_draws:
                index = int(np.searchsorted(cumulative, draw, side="right"))
                match, first, count = old[index]
                expected_start = first + int(draw - (cumulative[index - 1] if index else 0))
                actual = training.locate_draw(windows, cumulative, draw)
                self.assertEqual(actual[:2], (match, expected_start))
                crop = training.context_indices(actual[1], actual[2], actual[3])
                np.testing.assert_array_equal(crop[HALO:HALO + CORE],
                                              np.arange(expected_start + 25, expected_start + 225))

    def test_context_can_include_unknown_labels_but_never_cross_real_half(self):
        case, _ = make_case(unknown=True)
        case.blocks = [(0, 600)]
        windows = training.training_windows([case])
        self.assertEqual(windows, [(0, 100, 251, 0, 600)])
        indices = training.context_indices(100, 0, 600)
        self.assertTrue((case.labels[indices[:HALO]] < 0).any())
        self.assertTrue((case.labels[indices[HALO:HALO + CORE]] >= 0).all())
        self.assertEqual(indices[0], 0)
        second_half = training.context_indices(300, 300, 600)
        self.assertGreaterEqual(second_half.min(), 300)
        self.assertLess(second_half.max(), 600)
        with self.assertRaisesRegex(ValueError, "crosses"):
            training.context_indices(299, 300, 600)

    def test_chunk_prediction_matches_edge_extended_whole_half_and_isolates_halves(self):
        _, x = make_case()
        torch.manual_seed(20261106)
        model = TCN().eval()
        scaler = np.zeros(WIDTH), np.ones(WIDTH)
        blocks = [(0, 300), (300, 600)]
        chunked = predict(model, x, blocks, scaler)
        for start, stop in blocks:
            indices = np.clip(np.arange(start - HALO, stop + HALO), start, stop - 1)
            with torch.no_grad():
                logits = model(torch.from_numpy(x[indices][None]))
                whole = torch.softmax(logits, dim=-1).numpy()[0, HALO:HALO + stop - start]
            np.testing.assert_allclose(chunked[start:stop], whole, atol=1e-6, rtol=0)
        modified = x.copy()
        modified[300:] *= 10
        other = predict(model, modified, blocks, scaler)
        np.testing.assert_array_equal(chunked[:300], other[:300])

    def test_reloaded_probabilities_and_batch_decoded_labels_match(self):
        _, x = make_case()
        torch.manual_seed(20261106)
        model = TCN().eval()
        path = self.root / "synthetic.pt"
        torch.save(model.state_dict(), path)
        reloaded = TCN().eval()
        reloaded.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
        blocks = [(0, 300), (300, 600)]
        scaler = np.zeros(WIDTH), np.ones(WIDTH)
        first = predict(model, x, blocks, scaler)
        reload = predict(reloaded, x, blocks, scaler)
        np.testing.assert_array_equal(first, reload)
        batched = predict(model, x, blocks, scaler, batch=4)
        cost = (1 - np.eye(3)) * 16
        np.testing.assert_array_equal(decode(first, cost, blocks), decode(batched, cost, blocks))

    def test_repeat_fit_and_interrupted_resume_restore_exact_training(self):
        case, _ = make_case()
        reference, losses, coverage = training.train_fit(
            [case], self.root / "reference", "synthetic", steps=4, save_every=2)
        repeated, other_losses, other_coverage = training.train_fit(
            [case], self.root / "repeat", "synthetic", steps=4, save_every=2)
        training.confirm_repeat(reference, repeated, losses, other_losses, coverage, other_coverage)
        writer = training.write_checkpoint

        def interrupt(path, payload):
            writer(path, payload)
            if payload["step"] == 2:
                raise KeyboardInterrupt()

        with patch.object(training, "write_checkpoint", interrupt):
            with self.assertRaises(KeyboardInterrupt):
                training.train_fit([case], self.root / "resumed", "synthetic", steps=4, save_every=2)
        resumed, resumed_losses, resumed_coverage = training.train_fit(
            [case], self.root / "resumed", "synthetic", steps=4, save_every=2)
        training.confirm_repeat(reference, resumed, losses, resumed_losses, coverage, resumed_coverage)
        self.assertEqual(sum(sum(counts.values()) for counts in coverage.values()), 32)
        with self.assertRaisesRegex(RuntimeError, "identity"):
            training.train_fit([case], self.root / "resumed", "different", steps=4, save_every=2)
        case.provider = "pff"
        with self.assertRaisesRegex(ValueError, "IDSSE"):
            training.train_fit([case], self.root / "forbidden", "synthetic", steps=4)
