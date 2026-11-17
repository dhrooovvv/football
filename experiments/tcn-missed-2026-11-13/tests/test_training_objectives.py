"""Synthetic contracts only; they do not measure possession quality."""
from contextlib import contextmanager
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from objectives import SegmentIndex, WindowSampler, segment_soft_iou, CORE
import training


class Case:
    provider = 'idsse'

    def __init__(self, labels, key='synthetic', blocks=None):
        self.labels = np.asarray(labels, dtype=np.int8)
        self.key = key
        self.blocks = blocks if blocks is not None else [(0, len(labels))]

    def read(self, indices, gap):
        x = np.zeros((len(indices), training.WIDTH), dtype=np.float32)
        x[:, 0] = np.asarray(indices, dtype=np.float32) / 1000
        x[:, 1] = float(gap)
        return x


def case_with_spells(key='synthetic'):
    labels = np.full(700, 2, dtype=np.int8)
    labels[100:110] = 0
    labels[300:350] = 1
    labels[450:501] = 0
    return Case(labels, key)


class ShortSampling(unittest.TestCase):
    def test_uniform_matches_original_flat_valid_draws(self):
        sampler = WindowSampler([case_with_spells()], 'uniform')
        rng = np.random.default_rng(training.WINDOW_SEED)
        expected_rng = np.random.default_rng(training.WINDOW_SEED)
        actual = sampler.batch(rng, np.random.default_rng(999), size=31)
        expected = [(*sampler.uniform(int(v)), 'uniform')
                    for v in expected_rng.integers(0, sampler.cumulative[-1], size=31)]
        self.assertEqual(actual, expected)

    def test_short_threshold_and_all_containing_start_endpoints(self):
        sampler = WindowSampler([case_with_spells()], 'short_mix')
        self.assertEqual(sampler.audit['synthetic']['eligible_short_spells'], 2)
        self.assertEqual(len(sampler.eligible), 2)
        for ci, a, b, team, lo, hi in sampler.eligible:
            self.assertLessEqual(b - a, 50)
            for start in range(lo, hi + 1):
                self.assertLessEqual(start + 25, a)
                self.assertGreaterEqual(start + 225, b)
                self.assertGreaterEqual(start, 0)
                self.assertLessEqual(start + 250, 700)
            self.assertTrue(lo == 0 or lo - 1 + 225 < b)
            self.assertEqual(hi + 25, a)

    def test_unknown_and_half_boundaries_never_crossed(self):
        labels = np.full(900, 2, dtype=np.int8)
        labels[50:55] = 0
        labels[410:415] = 1
        labels[400] = -1
        labels[700:710] = 0
        case = Case(labels, blocks=[(0, 450), (450, 900)])
        sampler = WindowSampler([case], 'short_mix')
        self.assertGreater(sampler.audit['synthetic']['excluded_short_spells'], 0)
        for _, start, _ in sampler.batch(np.random.default_rng(2), np.random.default_rng(3), 100):
            self.assertTrue(any(a <= start and start + 250 <= b for a, b in case.blocks))
            self.assertTrue((labels[start:start + 250] >= 0).all())

    def test_mixture_draws_and_rng_resume_exact(self):
        sampler = WindowSampler([case_with_spells()], 'short_mix')
        wr, sr = np.random.default_rng(12), np.random.default_rng(34)
        sampler.batch(wr, sr, 17)
        ws, ss = copy.deepcopy(wr.bit_generator.state), copy.deepcopy(sr.bit_generator.state)
        expected = sampler.batch(wr, sr, 37)
        restored_w, restored_s = np.random.default_rng(), np.random.default_rng()
        restored_w.bit_generator.state, restored_s.bit_generator.state = ws, ss
        self.assertEqual(expected, sampler.batch(restored_w, restored_s, 37))
        self.assertEqual(set(row[2] for row in expected), {'short', 'uniform'})

    def test_no_short_spell_does_not_silently_change_mixture(self):
        with self.assertRaisesRegex(ValueError, 'No eligible short'):
            WindowSampler([Case(np.full(600, 2))], 'short_mix')


class SegmentOverlap(unittest.TestCase):
    def test_full_match_completeness_and_immediate_neighbor_context(self):
        labels = np.full(700, 2, dtype=np.int8)
        labels[90:100] = 0
        labels[100:101] = 1
        labels[101:110] = 0
        index = SegmentIndex(Case(labels))
        supports = index.supports(50)  # core [75,275)
        first = next(v for v in supports if v[1] == 15)
        self.assertEqual(first, (0, 15, 25, 0, 26))
        # Cropping through the first H spell excludes it, even though its visible suffix is H.
        cut = index.supports(70)  # core [95,295)
        self.assertFalse(any(team == 0 and left == 0 for team, left, *_ in cut))

    def test_half_and_unknown_edges_make_separate_segments(self):
        labels = np.zeros(600, dtype=np.int8)
        labels[300] = -1
        rows = SegmentIndex(Case(labels, blocks=[(0, 250), (250, 600)])).rows
        self.assertEqual([(a, b) for a, b, *_ in rows], [(0, 250), (250, 300), (301, 600)])

    def test_iou_matches_formula_and_equal_segment_weighting(self):
        logits = torch.zeros((1, CORE, 3), requires_grad=True)
        supports = [[(0, 10, 20, 0, 25), (1, 50, 100, 40, 110)]]
        result, count = segment_soft_iou(logits, supports)
        expected = sum(1 - (length / 3 + 1e-6) / (length + (width - length) / 3 + 1e-6)
                       for length, width in [(10, 25), (50, 70)]) / 2
        self.assertAlmostEqual(float(result.detach()), expected, places=6)
        self.assertEqual(count, 2)
        result.backward()
        self.assertTrue(torch.isfinite(logits.grad).all())
        self.assertLess(float(logits.grad[0, 12, 0]), 0.)
        self.assertGreater(float(logits.grad[0, 3, 0]), 0.)

    def test_empty_segments_have_differentiable_zero(self):
        logits = torch.zeros((2, CORE, 3), requires_grad=True)
        value, count = segment_soft_iou(logits, [[], []])
        self.assertEqual(float(value.detach()), 0.)
        self.assertEqual(count, 0)
        value.backward()
        self.assertTrue(torch.equal(logits.grad, torch.zeros_like(logits)))


class TrainingContracts(unittest.TestCase):
    def test_fold_and_seed_identity_rejects_protected_or_unknown_inputs(self):
        with self.assertRaises(RuntimeError):
            training.expected_identity('synthetic', 'a', 20261106, 'J03WQQ', 'short_mix')
        with self.assertRaises(RuntimeError):
            training.expected_identity('synthetic', 'a', 999, 'J03WMX', 'short_mix')
        with self.assertRaises(RuntimeError):
            training.expected_identity('synthetic', 'a', 20261106, 'J03WMX', 'uniform')

    def test_interrupted_checkpoint_resume_matches_complete_tiny_fit(self):
        cases = [case_with_spells('idsse-' + m) for m in training.IDS if m != 'J03WMX']

        @contextmanager
        def guard():
            yield

        class Interrupted(Exception):
            pass

        writes = 0

        @contextmanager
        def interrupt_second_checkpoint():
            nonlocal writes
            writes += 1
            # First guard creates directory; second saves step1; third interrupts step2 save.
            if writes == 3:
                raise Interrupted()
            yield

        def tiny_model(_):
            return torch.nn.Linear(training.WIDTH, 3)

        original_batch = WindowSampler.batch

        def balanced_synthetic_batch(sampling, window_rng, sampler_rng, size=8):
            # All four cases have identical labels; force complete synthetic membership exposure.
            return [(i % 4, start, branch) for i, (_, start, branch) in
                    enumerate(original_batch(sampling, window_rng, sampler_rng, size))]

        with tempfile.TemporaryDirectory() as temporary, \
             mock.patch.object(training, 'TOTAL_STEPS', 2), \
             mock.patch.object(training, 'STAGE_STEPS', 1), \
             mock.patch.object(training, 'SAVE_EVERY', 1), \
             mock.patch.object(training, 'model_for_arm', tiny_model), \
             mock.patch.object(training, 'research_open'), \
             mock.patch.object(WindowSampler, 'batch', balanced_synthetic_batch):
            full, resumed = Path(temporary) / 'full', Path(temporary) / 'resumed'
            training.train_fit(cases, full, 'synthetic', 'a', 20261106, 'J03WMX', 'short_mix', guard)
            with self.assertRaises(Interrupted):
                training.train_fit(cases, resumed, 'synthetic', 'a', 20261106, 'J03WMX', 'short_mix',
                                   interrupt_second_checkpoint)
            training.train_fit(cases, resumed, 'synthetic', 'a', 20261106, 'J03WMX', 'short_mix', guard)
            left = torch.load(full / 'progress.pt', weights_only=True)
            right = torch.load(resumed / 'progress.pt', weights_only=True)
            training.confirm_repeat(left, right)
            altered = copy.deepcopy(right)
            altered['component_losses']['cross_entropy'][0] += 1
            with self.assertRaisesRegex(RuntimeError, 'cross|component'):
                training.confirm_repeat(left, altered)


if __name__ == '__main__':
    unittest.main()
