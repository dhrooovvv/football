"""Synthetic reproducibility contracts to be executed only by the user."""
from contextlib import nullcontext
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hybrid_data import HybridCase
from hybrid_model import configure, corrected_logits
from hybrid_training import (IDS, SEEDS, expected_identity, train_fit, validate_saved,
                             confirm_repeat, training_logits)


class SyntheticCase:
    provider = 'idsse'

    def __init__(self, match):
        self.key = 'idsse-'+match
        self.labels = np.full(400, 2, dtype=np.int8)
        self.labels[180:210] = 0
        self.blocks = [[0, 400]]
        self.arrays = {'core.npy': np.zeros((400, 9), dtype=np.float32),
                       'gap_core.npy': np.zeros((400, 9), dtype=np.float32)}
        self.arrays['core.npy'][:, 5] = 1
        self.arrays['gap_core.npy'][:, 8] = .2

    def read(self, indices, augmented):
        result = np.zeros((len(indices), 521), dtype=np.float32)
        result[:, -9:] = self.arrays['gap_core.npy' if augmented else 'core.npy'][indices]
        return result


def cases(held_out=IDS[-1]):
    result = []
    for match in IDS:
        if match == held_out:
            continue
        p = np.tile(np.array([[.2, .3, .5]], dtype=np.float64), (400, 1))
        result.append(HybridCase(SyntheticCase(match), p, p.copy()))
    return result


class TrainingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure()

    def test_fold_final_and_probe_identities(self):
        fold = expected_identity('registered', 'temporal', SEEDS[0], IDS[0])
        self.assertNotIn('idsse-'+IDS[0], fold['training_matches'])
        final = expected_identity('registered', 'graph', SEEDS[1], None, purpose='final')
        self.assertEqual(final['training_matches'], ['idsse-'+m for m in IDS])
        for kwargs in (dict(stage='temporal', held_out=IDS[0], steps=200),
                       dict(stage='graph', held_out=None),
                       dict(stage='temporal', held_out=IDS[0], probe=True, steps=1001)):
            with self.assertRaises(RuntimeError):
                expected_identity('registered', seed=SEEDS[0], **kwargs)

    def test_heldout_case_cannot_enter_training(self):
        with tempfile.TemporaryDirectory() as root, patch('hybrid_training.research_open'):
            with self.assertRaises(RuntimeError):
                train_fit(cases(), root, 'registered', 'temporal', SEEDS[0], IDS[0], nullcontext,
                          steps=1, probe=True)

    def test_exact_repeat_and_resumed_training(self):
        source = cases()
        with tempfile.TemporaryDirectory() as directory, patch('hybrid_training.research_open'):
            root = Path(directory)
            args = ('registered', 'temporal', SEEDS[0], IDS[-1], nullcontext)
            train_fit(source, root/'first', *args, steps=2, probe=True)
            train_fit(source, root/'repeat', *args, steps=2, probe=True)
            train_fit(source, root/'resume', *args, steps=2, probe=True, stop_after=1)
            train_fit(source, root/'resume', *args, steps=2, probe=True)
            values = [torch.load(root/name/'progress.pt', weights_only=True, map_location='cpu')
                      for name in ('first', 'repeat', 'resume')]
            identity = expected_identity('registered', 'temporal', SEEDS[0], IDS[-1], steps=2, probe=True)
            for value in values:
                validate_saved(value, identity)
            confirm_repeat(values[0], values[1])
            confirm_repeat(values[0], values[2])
            self.assertEqual(sum(values[0]['coverage']['stage1'].values()), 16)
            broken = dict(values[0]); broken['identity'] = dict(identity, probe=False)
            with self.assertRaises(RuntimeError):
                validate_saved(broken, identity)

    def test_stage_boundary_resets_optimizer_and_sampling(self):
        with tempfile.TemporaryDirectory() as root, patch('hybrid_training.research_open'), \
             patch('hybrid_training.STAGE_STEPS', 2):
            train_fit(cases(), root, 'registered', 'temporal', SEEDS[0], IDS[-1], nullcontext,
                      steps=4, probe=True)
            value = torch.load(Path(root)/'progress.pt', map_location='cpu', weights_only=True)
            self.assertEqual(value['coverage']['stage1'], value['coverage']['stage2'])
            self.assertEqual(value['supervised_views']['stage1'], value['supervised_views']['stage2'])
            self.assertEqual(value['exposure']['stage1'], value['exposure']['stage2'])
            for state in value['optimizer']['state'].values():
                self.assertEqual(float(state['step']), 2.)

    def test_unknown_labels_rejected_from_loss(self):
        source = cases()
        source[0].labels[100] = -1
        from hybrid_model import TemporalRefiner
        with self.assertRaises(RuntimeError):
            training_logits(TemporalRefiner(), source, [(0, 25, 'uniform')], [False])

    def test_parent_has_no_training_gradient(self):
        parent = torch.full((1, 3), 1/3, dtype=torch.float64, requires_grad=True)
        correction = torch.zeros((1, 3), requires_grad=True)
        corrected_logits(parent, correction).sum().backward()
        self.assertIsNone(parent.grad)
        self.assertIsNotNone(correction.grad)

    def test_malformed_cache_probabilities_rejected(self):
        bad = np.ones((400, 3), dtype=np.float64)
        with self.assertRaises(ValueError):
            HybridCase(SyntheticCase(IDS[0]), bad, bad)


if __name__ == '__main__':
    unittest.main()
