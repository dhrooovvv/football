"""User-run contracts; synthetic evidence is not possession quality evidence."""
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import boundary_model as model_code
import boundary_training as training
from boundary_model import (TCN, OriginalTCN, predict, WIDTH, WINDOW, HALO, CORE,
                            boundary_targets, balanced_boundary_loss)
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


class BoundaryContracts(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.backends.mkldnn.enabled = False
        torch.use_deterministic_algorithms(True)
        torch.manual_seed(20261106)
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_original_initialization_and_class_path_preserved(self):
        torch.manual_seed(20261106)
        parent = OriginalTCN().eval()
        torch.manual_seed(20261106)
        candidate = TCN().eval()
        self.assertEqual(sum(p.numel() for p in candidate.parameters()), 9668)
        for name, value in parent.state_dict().items():
            self.assertTrue(torch.equal(value, candidate.state_dict()[name]), name)
        _, values = make_case()
        x = torch.from_numpy(values[:250][None])
        with torch.no_grad():
            expected = parent(x)
            actual, boundaries = candidate.forward_with_boundary(x)
            self.assertTrue(torch.equal(expected, candidate(x)))
            self.assertTrue(torch.equal(expected, actual))
            self.assertEqual(boundaries.shape, (1, 250))
            candidate.boundary.weight.fill_(100)
            candidate.boundary.bias.fill_(-300)
            self.assertTrue(torch.equal(expected, candidate(x)))

    def test_boundary_targets_mask_unknown_half_and_crop_edges(self):
        labels = torch.tensor([[0, 0, 1, -1, 2, 0, 1, 1]])
        starts = torch.tensor([[True, False, False, False, False, True, False, False]])
        target, valid = boundary_targets(labels, starts)
        self.assertEqual(valid.tolist(), [[False, True, True, False, False, False, True, True]])
        self.assertEqual(target.tolist(), [[0., 0., 1., 0., 0., 0., 1., 0.]])
        # Central loss's first label has a real predecessor in the left halo.
        full = torch.zeros((1, WINDOW), dtype=torch.int64)
        full[:, HALO:] = 1
        target, valid = boundary_targets(full)
        self.assertTrue(valid[0, HALO])
        self.assertEqual(target[0, HALO].item(), 1.)
        self.assertFalse(valid[0, 0])
        self.assertEqual(target[:, HALO:HALO + CORE].sum().item(), 1.)

    def test_balanced_loss_equal_present_class_means(self):
        logits = torch.tensor([[2., 0., -1., -3.]], requires_grad=True)
        target = torch.tensor([[1., 0., 0., 0.]])
        valid = torch.ones_like(target, dtype=torch.bool)
        losses = torch.nn.functional.binary_cross_entropy_with_logits(logits, target, reduction='none')
        expected = .5 * (losses[0, 0] + losses[0, 1:].mean())
        actual = balanced_boundary_loss(logits, target, valid)
        torch.testing.assert_close(actual, expected, atol=0, rtol=0)
        actual.backward()
        self.assertTrue(torch.isfinite(logits.grad).all())

    def test_boundary_loss_absent_classes_and_unknown_only(self):
        for value in (0., 1.):
            logits = torch.tensor([[2., -1.]], requires_grad=True)
            target = torch.full_like(logits, value)
            valid = torch.ones_like(target, dtype=torch.bool)
            expected = torch.nn.functional.binary_cross_entropy_with_logits(logits, target)
            torch.testing.assert_close(balanced_boundary_loss(logits, target, valid), expected)
        logits = torch.tensor([[2., -1.]], requires_grad=True)
        loss = balanced_boundary_loss(logits, torch.zeros_like(logits),
                                      torch.zeros_like(logits, dtype=torch.bool))
        self.assertEqual(loss.item(), 0.)
        loss.backward()
        self.assertTrue(torch.equal(logits.grad, torch.zeros_like(logits)))

    def test_auxiliary_gradient_reaches_motion_encoder(self):
        _, values = make_case()
        model = TCN()
        _, boundary_logits = model.forward_with_boundary(torch.from_numpy(values[:250][None]))
        labels = torch.zeros((1, WINDOW), dtype=torch.int64)
        labels[:, 100:150] = 1
        target, valid = boundary_targets(labels)
        loss = balanced_boundary_loss(boundary_logits[:, HALO:HALO + CORE],
                                      target[:, HALO:HALO + CORE], valid[:, HALO:HALO + CORE])
        loss.backward()
        self.assertGreater(model.object.weight.grad.abs().sum().item(), 0)
        self.assertGreater(model.layers[0].weight.grad.abs().sum().item(), 0)
        self.assertIsNone(model.layers[-1].weight.grad)

    def test_parent_window_support_and_forbidden_sources(self):
        case, _ = make_case(unknown=True)
        self.assertEqual(training.valid_windows([case], WINDOW), [(0, 300, 51)])
        case.provider = 'pff'
        with self.assertRaisesRegex(ValueError, 'IDSSE'):
            training.train_fit([case], self.root / 'pff', 'synthetic', steps=2)
        case.provider = 'idsse'; case.key = 'idsse-J03WQQ'
        with self.assertRaisesRegex(ValueError, 'Sealed'):
            training.train_fit([case], self.root / 'sealed', 'synthetic', steps=2)

    def test_half_isolation_reload_batch_and_x_output(self):
        _, values = make_case()
        blocks = [(5, 295), (305, 595)]
        model = TCN().eval()
        path = self.root / 'synthetic.pt'
        torch.save(model.state_dict(), path)
        loaded = TCN().eval()
        loaded.load_state_dict(torch.load(path, map_location='cpu', weights_only=True))
        scaler = np.zeros(WIDTH), np.ones(WIDTH)
        first = predict(model, values, blocks, scaler)
        np.testing.assert_array_equal(first, predict(loaded, values, blocks, scaler))
        batched = predict(model, values, blocks, scaler, batch=4)
        cost = (1 - np.eye(3)) * 16
        labels = decode(first, cost, blocks)
        np.testing.assert_array_equal(labels, decode(batched, cost, blocks))
        outside = np.ones(len(values), bool)
        for start, stop in blocks: outside[start:stop] = False
        self.assertTrue((labels[outside] == 'X').all())
        changed = values.copy(); changed[305:] *= 10
        np.testing.assert_array_equal(first[5:295], predict(model, changed, blocks, scaler)[5:295])

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
        component_histories = [torch.load(self.root / name / 'progress.pt',
                              map_location='cpu', weights_only=True)['loss_components']
                              for name in ('reference', 'repeat', 'resumed')]
        self.assertEqual(component_histories[0], component_histories[1])
        self.assertEqual(component_histories[0], component_histories[2])
        self.assertEqual(len(component_histories[0]['class']), 4)
        self.assertEqual(len(component_histories[0]['boundary']), 4)
        with self.assertRaisesRegex(RuntimeError, 'identity'):
            training.train_fit([case], self.root / 'resumed', 'different', steps=4, save_every=2)
        case.key = 'idsse-other-synthetic'
        with self.assertRaisesRegex(RuntimeError, 'identity'):
            training.train_fit([case], self.root / 'resumed', 'synthetic', steps=4, save_every=2)


if __name__ == '__main__':
    unittest.main()
