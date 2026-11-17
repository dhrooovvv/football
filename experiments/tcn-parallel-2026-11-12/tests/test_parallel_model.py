"""User-run synthetic model contracts; no assets or quality measurements."""
from pathlib import Path
import sys
import unittest

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parallel_model import (AttentionTCN, OriginalTCN, model_for_arm,
                            PARAMETERS, WIDTH, SLOTS, CHANNELS)


class ParallelModel(unittest.TestCase):
    def inputs(self):
        x = torch.zeros(2, 9, WIDTH)
        objects = x[:, :, :SLOTS * CHANNELS].reshape(2, 9, SLOTS, CHANNELS)
        objects[:, :, :6, :5] = torch.randn(2, 9, 6, 5) * .1
        objects[:, :, :6, 4] = 1
        objects[:, :, :3, 5] = 1
        objects[:, :, 3:6, 6] = 1
        objects[:, :, -1, :5] = torch.randn(2, 9, 5) * .1
        objects[:, :, -1, 4] = 1
        objects[:, :, -1, 7] = 1
        return x

    def test_original_initialization_and_parameter_count_preserved(self):
        torch.manual_seed(20261106)
        parent = OriginalTCN()
        torch.manual_seed(20261106)
        candidate = AttentionTCN()
        for name, tensor in parent.state_dict().items():
            self.assertTrue(torch.equal(tensor, candidate.state_dict()[name]), name)
        self.assertEqual(sum(p.numel() for p in candidate.parameters()), PARAMETERS['attention'])
        self.assertEqual(sum(p.numel() for p in parent.parameters()), PARAMETERS['ensemble'])
        self.assertEqual(PARAMETERS['attention'] - PARAMETERS['ensemble'], 216)

    def test_seed_arm_is_original_architecture(self):
        torch.manual_seed(20261107)
        expected = OriginalTCN()
        torch.manual_seed(20261107)
        actual = model_for_arm('ensemble')
        self.assertIs(type(actual), OriginalTCN)
        self.assertTrue(all(torch.equal(t, actual.state_dict()[name])
                            for name, t in expected.state_dict().items()))
        with self.assertRaises(ValueError):
            model_for_arm('unregistered')

    def test_all_missing_team_zero_and_masked_objects_do_not_leak(self):
        model = AttentionTCN()
        hidden = torch.randn(2, 3, 5, 8, requires_grad=True)
        visible = torch.tensor([True, True, False, False, False]).expand(2, 3, 5)
        expected = model.attend(hidden, visible)
        changed = hidden.detach().clone()
        changed[:, :, 2:] = 1000
        self.assertTrue(torch.equal(expected.detach(), model.attend(changed, visible)))
        expected.sum().backward()
        self.assertTrue(torch.equal(hidden.grad[:, :, 2:], torch.zeros_like(hidden.grad[:, :, 2:])))
        absent = model.attend(hidden.detach(), torch.zeros_like(visible))
        self.assertTrue(torch.isfinite(absent).all())
        self.assertTrue(torch.equal(absent, torch.zeros_like(absent)))

    def test_full_forward_static_team_permutation_and_no_reconstruction_use(self):
        torch.manual_seed(11)
        model = AttentionTCN().eval()
        x = self.inputs()
        changed = x.clone()
        before = x[:, :, :512].reshape(2, 9, 64, 8)
        after = changed[:, :, :512].reshape(2, 9, 64, 8)
        after[:, :, :3] = before[:, :, [2, 0, 1]]
        after[:, :, 3:6] = before[:, :, [5, 3, 4]]
        output = model(x)
        self.assertEqual(tuple(output.shape), (2, 9, 3))
        self.assertTrue(torch.isfinite(output).all())
        self.assertTrue(torch.allclose(output, model(changed), atol=1.e-6, rtol=1.e-5))
        output.sum().backward()
        self.assertIsNotNone(model.value.weight.grad)
        self.assertIsNone(model.reconstruction.weight.grad)


if __name__ == '__main__':
    unittest.main()
