"""Synthetic balanced-sampler and resumption contracts; supplied for user execution."""
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import balanced_training
from balanced_training import ProviderSampler


def support_case(key, provider, frames, blocks, unknown=()):
    labels = np.zeros(frames, dtype=np.int8)
    for start, stop in unknown:
        labels[start:stop] = -1
    return SimpleNamespace(key=key, provider=provider, labels=labels, blocks=blocks)


class BalancedContracts(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_provider_support_is_exact_and_respects_unknowns_and_halves(self):
        cases = [support_case("i1", "idsse", 600, [(0, 300), (300, 600)], [(280, 320)]),
                 support_case("i2", "idsse", 251, [(0, 251)]),
                 support_case("p1", "pff", 252, [(0, 252)])]
        sampler = ProviderSampler(cases)
        self.assertEqual(sampler.totals, {"idsse": 64, "pff": 3})
        actual = [sampler.locate("idsse", draw) for draw in range(64)]
        expected = [(0, start) for start in range(31)]
        expected += [(0, start) for start in range(320, 351)]
        expected += [(1, 0), (1, 1)]
        self.assertEqual(actual, expected)
        self.assertEqual(len(set(actual)), 64)
        self.assertEqual([sampler.locate("pff", draw) for draw in range(3)],
                         [(2, 0), (2, 1), (2, 2)])
        for match, start in actual:
            self.assertTrue((cases[match].labels[start:start + 250] >= 0).all())
            self.assertTrue(any(left <= start and start + 250 <= right
                                for left, right in cases[match].blocks))

    def test_provider_choice_has_equal_mass_independent_of_window_volume(self):
        cases = [support_case("i", "idsse", 250, [(0, 250)]),
                 support_case("p", "pff", 1000, [(0, 1000)])]
        sampler = ProviderSampler(cases)
        # Enumerate the two possible provider choices instead of a flaky frequency threshold.
        provider_rng = SimpleNamespace(integers=lambda low, high, size: np.array([0, 1]))
        window_rng = SimpleNamespace(integers=lambda low, high: high - 1)
        self.assertEqual(sampler.sample_batch(window_rng, provider_rng, size=2), [(0, 0), (1, 750)])
        self.assertEqual(sampler.providers, ("idsse", "pff"))

    def test_rejects_missing_unknown_or_empty_provider_support(self):
        one = support_case("i", "idsse", 250, [(0, 250)])
        with self.assertRaisesRegex(ValueError, "Exactly"):
            ProviderSampler([one])
        with self.assertRaisesRegex(ValueError, "Exactly"):
            ProviderSampler([one, support_case("o", "other", 250, [(0, 250)])])
        with self.assertRaisesRegex(ValueError, "No complete"):
            ProviderSampler([one, support_case("p", "pff", 250, [(0, 250)], [(0, 1)])])
        sampler = ProviderSampler([one, support_case("p", "pff", 250, [(0, 250)])])
        for draw in (-1, 1, True, 0.5):
            with self.assertRaises(ValueError):
                sampler.locate("idsse", draw)
        with self.assertRaisesRegex(ValueError, "Unknown"):
            sampler.locate("other", 0)

    def training_cases(self):
        cases = []
        for index, provider in enumerate(("idsse", "pff")):
            rng = np.random.default_rng(41 + index)
            obj = np.zeros((600, 64, 8), dtype=np.float32)
            for slot in (0, 1, 2, 3, 63):
                obj[:, slot, :4] = rng.normal(size=(600, 4))
                obj[:, slot, 4] = 1
            obj[:, :2, 5] = 1
            obj[:, 2:4, 6] = 1
            obj[:, 63, 7] = 1
            clean = np.column_stack((obj.reshape(600, 512), rng.normal(size=(600, 9)).astype(np.float32)))
            gap = clean.copy()
            gap[100:200, 63 * 8:63 * 8 + 5] = 0
            labels = np.resize(np.arange(3, dtype=np.int8), 600)
            # Default arguments bind each synthetic case's arrays independently.
            reader = lambda indices, augmented, x=clean, g=gap: (g if augmented else x)[indices]
            cases.append(SimpleNamespace(key=provider + "-synthetic", provider=provider,
                                         labels=labels, blocks=[(0, 300), (300, 600)], read=reader))
        return cases

    def test_checkpoint_resume_restores_provider_rng_and_matches_repeated_fit(self):
        cases = self.training_cases()
        reference, losses, coverage = balanced_training.train_fit(
            cases, self.root / "reference", "synthetic", steps=4, save_every=2)
        repeated, losses2, coverage2 = balanced_training.train_fit(
            cases, self.root / "repeat", "synthetic", steps=4, save_every=2)
        balanced_training.confirm_repeat(reference, repeated, losses, losses2, coverage, coverage2)
        original = balanced_training.write_checkpoint

        def interrupt_after_checkpoint(path, payload):
            original(path, payload)
            if payload["step"] == 2:
                raise KeyboardInterrupt()

        with patch.object(balanced_training, "write_checkpoint", interrupt_after_checkpoint):
            with self.assertRaises(KeyboardInterrupt):
                balanced_training.train_fit(cases, self.root / "resumed", "synthetic", steps=4, save_every=2)
        resumed, other_losses, other_coverage = balanced_training.train_fit(
            cases, self.root / "resumed", "synthetic", steps=4, save_every=2)
        balanced_training.confirm_repeat(reference, resumed, losses, other_losses, coverage, other_coverage)
        self.assertEqual(sum(sum(counts.values()) for counts in coverage.values()), 32)
        with self.assertRaisesRegex(RuntimeError, "identity"):
            balanced_training.train_fit(cases, self.root / "resumed", "different", steps=4, save_every=2)
