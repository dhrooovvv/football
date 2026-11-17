"""Synthetic compact-input and checkpoint-resume regressions. User-run only."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from expanded_data import CompactCase, pack_case, valid_windows
import expanded_training


class ExpandedContracts(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def make_case(self, unknown=False):
        rng = np.random.default_rng(41)
        objects = np.zeros((600, 64, 8), dtype=np.float32)
        for slot in (0, 1, 2, 3, 63):
            objects[:, slot, :4] = rng.normal(size=(600, 4))
            objects[:, slot, 4] = 1
        objects[:, :2, 5] = 1
        objects[:, 2:4, 6] = 1
        objects[:, 63, 7] = 1
        core = rng.normal(size=(600, 9)).astype(np.float32)
        clean = np.column_stack((objects.reshape(600, 512), core))
        gap = clean.copy()
        gap[100:200, 63 * 8:63 * 8 + 5] = 0
        gap[100:200, -9:] = 0
        labels = np.resize(np.array(["H", "A", "D"]), 600)
        if unknown:
            labels[280:320] = "X"
        directory = self.root / "synthetic"
        directory.mkdir()
        pack_case(directory, clean, gap, labels, [(0, 300), (300, 600)],
                  dict(key="synthetic", provider="test", registration="synthetic"))
        return CompactCase(directory), clean, gap, labels

    def test_lossless_reads_preserve_masks_and_clipped_indices(self):
        case, clean, gap, _ = self.make_case()
        indices = np.array([0, 0, 99, 100, 199, 200, 299, 300, 599, 599])
        np.testing.assert_array_equal(case.read(indices, False), clean[indices])
        np.testing.assert_array_equal(case.read(indices, True), gap[indices])
        self.assertIsInstance(case.arrays["objects.npy"], np.memmap)
        self.assertEqual(sum(isinstance(value, np.memmap) for value in case.arrays.values()), 4)

    def test_windows_exclude_unknowns_and_half_crossings(self):
        case, _, _, _ = self.make_case(unknown=True)
        self.assertEqual(valid_windows([case]), [(0, 0, 31), (0, 320, 31)])

    def test_compaction_rejects_player_corruption_in_ball_only_view(self):
        _, clean, gap, labels = self.make_case()
        gap[25, 0] += 1
        directory = self.root / "invalid"
        directory.mkdir()
        with self.assertRaisesRegex(ValueError, "player inputs"):
            pack_case(directory, clean, gap, labels, [(0, 300), (300, 600)],
                      dict(key="invalid", provider="test", registration="synthetic"))

    def test_checkpoint_resume_matches_uninterrupted_training(self):
        case, _, _, _ = self.make_case()
        reference, losses, coverage = expanded_training.train_fit(
            [case], self.root / "reference", "synthetic", steps=4, save_every=2)
        original_writer = expanded_training.write_checkpoint

        def interrupt_after_checkpoint(path, payload):
            original_writer(path, payload)
            if payload["step"] == 2:
                raise KeyboardInterrupt()

        with patch.object(expanded_training, "write_checkpoint", interrupt_after_checkpoint):
            with self.assertRaises(KeyboardInterrupt):
                expanded_training.train_fit([case], self.root / "resumed", "synthetic", steps=4, save_every=2)
        resumed, other_losses, other_coverage = expanded_training.train_fit(
            [case], self.root / "resumed", "synthetic", steps=4, save_every=2)
        expanded_training.confirm_repeat(reference, resumed, losses, other_losses, coverage, other_coverage)
        with self.assertRaisesRegex(RuntimeError, "identity"):
            expanded_training.train_fit([case], self.root / "resumed", "different", steps=4, save_every=2)
