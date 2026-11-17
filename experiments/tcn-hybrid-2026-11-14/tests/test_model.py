"""Synthetic tests supplied for user execution, without any real match input."""
from pathlib import Path
import sys
import unittest

import numpy as np
import torch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hybrid_data import TemporalContext, HybridCase
from hybrid_model import (TemporalRefiner, GraphRefiner, model_for_stage, PARAMETERS,
                          adjacency, corrected_logits, corrected_probabilities,
                          configure, predict, interpolate)


def parent_array(frames):
    rng = np.random.default_rng(14)
    p = rng.random((frames, 3))+.1
    return p/p.sum(1, keepdims=True)


def encoded(frames):
    x = np.zeros((frames, 521), dtype=np.float32)
    objects = x[:, :512].reshape(frames, 64, 8)
    for node in range(6):
        objects[:, node, :2] = np.array([node/10, node/20])
        objects[:, node, 4] = 1
        objects[:, node, 5 if node < 3 else 6] = 1
    objects[:, -1, :2] = .1
    objects[:, -1, 4] = 1
    objects[:, -1, 7] = 1
    x[:, -4] = 1
    return x


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure()

    def test_parameter_counts_and_zero_heads(self):
        for stage in ('temporal', 'graph'):
            model = model_for_stage(stage)
            self.assertEqual(sum(p.numel() for p in model.parameters()), PARAMETERS[stage])
            self.assertEqual(torch.count_nonzero(model.head.weight).item(), 0)
            self.assertEqual(torch.count_nonzero(model.head.bias).item(), 0)

    def test_actual_partial_bin_centres_and_means(self):
        p = parent_array(13)
        context = TemporalContext(p, np.ones(13), np.arange(13)/13, [(1, 13)])
        _, _, centres, features = context.rows[0]
        np.testing.assert_array_equal(centres, [3., 8., 11.5])
        np.testing.assert_allclose(features[-1, :3], p[11:13].mean(0), atol=1e-7)

    def test_window_grid_is_half_anchored_and_unknown_independent(self):
        p = parent_array(520)
        context = TemporalContext(p, np.ones(520), np.zeros(520), [(0, 259), (270, 520)])
        for start in (0, 1, 2, 3, 4, 5, 59, 270, 271, 320):
            right = min(start+200, 259 if start < 270 else 520)
            values, lower, upper, weight = context.window(start, right)
            self.assertEqual(values.shape, (169, 5))
            self.assertTrue(np.all(lower >= 63))
            self.assertTrue(np.all(upper <= 105))
            self.assertTrue(np.all((weight >= 0) & (weight <= 1)))
        with self.assertRaises(ValueError):
            context.window(250, 280)

    def test_temporal_chunk_matches_replicated_whole_half(self):
        torch.manual_seed(4)
        model = TemporalRefiner()
        torch.nn.init.normal_(model.head.weight, std=.01)
        x, parent = encoded(417), parent_array(417)
        blocks = [(0, 211), (220, 417)]
        result = predict(model, x, parent, blocks, batch=2)
        context = TemporalContext(parent, x[:, -4], x[:, -1], blocks)
        expected = parent.copy()
        with torch.no_grad():
            for start, stop, centres, features in context.rows:
                padded = np.pad(features, ((63, 63), (0, 0)), mode='edge')
                delta = model(torch.from_numpy(padded)[None])[0, 63:63+len(features)].numpy()
                full = np.column_stack([np.interp(np.arange(start, stop), centres, delta[:, i]) for i in range(3)])
                expected[start:stop] = corrected_probabilities(parent[start:stop], full)
        np.testing.assert_allclose(result, expected, atol=2e-8, rtol=1e-7)
        np.testing.assert_array_equal(result[211:220], parent[211:220])

    def test_zero_correction_exact_parent_and_live_gradient(self):
        parent = parent_array(200)
        np.testing.assert_array_equal(corrected_probabilities(parent, np.zeros_like(parent)), parent)
        model = TemporalRefiner()
        delta = model(torch.ones((1, 169, 5)))[:, :200]
        logits = corrected_logits(torch.from_numpy(parent[:169])[None], delta)
        torch.nn.functional.cross_entropy(logits.reshape(-1, 3), torch.zeros(169, dtype=torch.long)).backward()
        self.assertGreater(torch.count_nonzero(model.head.bias.grad).item(), 0)

    def test_graph_missing_ball_and_neighbour_ties(self):
        objects = torch.from_numpy(encoded(1)[:, :512].reshape(1, 64, 8))
        # Five equidistant senders survive the fourth-neighbour cutoff.
        objects[0, 0, :2] = 0
        objects[0, 1:6, :2] = torch.tensor([[1., 0.], [-1., 0.], [0., 1.], [0., -1.], [1., 0.]])
        edge = adjacency(objects)
        self.assertTrue(edge[0, 0, 1:6].all())
        self.assertTrue(edge[0, :6, 63].all())
        self.assertTrue(edge[0, 63, :6].all())
        self.assertFalse(edge.diagonal(dim1=1, dim2=2).any())
        objects[0, 63, 4] = 0
        edge = adjacency(objects)
        self.assertFalse(edge[0, :, 63].any())
        self.assertFalse(edge[0, 63].any())

    def test_graph_pool_permutation_invariance_and_empty_teams(self):
        torch.manual_seed(3)
        model = GraphRefiner()
        objects = torch.from_numpy(encoded(2)[:, :512].reshape(2, 64, 8))
        permutation = torch.arange(64)
        permutation[:6] = torch.tensor([5, 2, 4, 1, 3, 0])
        left, right = model.graph_features(objects), model.graph_features(objects[:, permutation])
        torch.testing.assert_close(left, right, atol=1e-6, rtol=1e-6)
        empty = torch.zeros((1, 64, 8))
        torch.testing.assert_close(model.graph_features(empty), torch.zeros((1, 24)), rtol=0, atol=0)

    def test_graph_predict_zero_head_and_half_isolation(self):
        model = GraphRefiner()
        x, parent = encoded(30), parent_array(30)
        np.testing.assert_array_equal(predict(model, x, parent, [(0, 10), (20, 30)], batch=2), parent)
        torch.nn.init.normal_(model.head.weight, std=.01)
        original = predict(model, x, parent, [(0, 10), (20, 30)])
        altered = x.copy(); altered[:10, :512] *= .5
        result = predict(model, altered, parent, [(0, 10), (20, 30)])
        np.testing.assert_array_equal(original[20:30], result[20:30])


if __name__ == '__main__':
    unittest.main()
