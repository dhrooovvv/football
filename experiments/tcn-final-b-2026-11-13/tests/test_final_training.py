"""Synthetic final-training contracts, never an accuracy measurement."""
from contextlib import contextmanager
import copy
from datetime import datetime
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import final_training as final


class IdentityOnlyCase:
    def __init__(self, key, provider='idsse'):
        self.key, self.provider = key, provider


class SyntheticCase(IdentityOnlyCase):
    def __init__(self, key):
        super().__init__(key)
        self.labels = np.full(700, 2, dtype=np.int8)
        self.labels[100:110] = 0
        self.labels[300:350] = 1
        self.labels[450:501] = 0
        self.blocks = [(0, 700)]

    def read(self, indices, gap):
        values = np.zeros((len(indices), final.WIDTH), dtype=np.float32)
        values[:, 0] = np.asarray(indices, dtype=np.float32) / 1000
        values[:, 1] = float(gap)
        return values


@contextmanager
def guard():
    yield


class FinalIdentity(unittest.TestCase):
    def test_exact_five_identity_and_frozen_trial_b_recipe(self):
        for seed in final.SEEDS:
            identity = final.expected_identity('synthetic', seed)
            self.assertEqual(identity['training_matches'], ['idsse-' + m for m in final.IDS])
            self.assertNotIn('held_out', identity)
            self.assertEqual(identity['purpose'], 'final_five_trial_b')
            self.assertEqual(identity['sampler'], 'short_mix')
            self.assertEqual(identity['auxiliary_loss'], 'segment_soft_iou')
            self.assertEqual(identity['auxiliary_coefficient'], .1)
            self.assertEqual(identity['initialization_seed'], seed)
            self.assertEqual((identity['total_steps'], identity['stage_steps']), (40000, 20000))
            self.assertEqual((identity['window_seed'], identity['view_seed'], identity['sampler_seed']),
                             (20261106, 20685348, 20261106 + 515151))

    def test_invalid_seed_and_missing_registration_rejected(self):
        for seed in (True, False, '20261106', 999):
            with self.subTest(seed=seed), self.assertRaises(RuntimeError):
                final.expected_identity('synthetic', seed)
        with self.assertRaises(RuntimeError):
            final.expected_identity('', 20261106)

    def test_membership_rejected_before_arrays_or_model_loading(self):
        keys = ['idsse-' + m for m in final.IDS]
        invalid_cases = [
            [IdentityOnlyCase(k) for k in keys[:-1]],
            [IdentityOnlyCase(k) for k in reversed(keys)],
            [IdentityOnlyCase(k) for k in keys] + [IdentityOnlyCase('idsse-J03WQQ')],
            [IdentityOnlyCase(k) for k in keys[:-1]] + [IdentityOnlyCase('idsse-J03WQQ')],
            [IdentityOnlyCase(k) for k in keys[:-1]] + [IdentityOnlyCase('pff-1', 'pff')],
            [IdentityOnlyCase(k, 'pff') for k in keys],
        ]
        with mock.patch.object(final, 'research_open'), \
             mock.patch.object(final, 'WindowSampler') as sampler, \
             mock.patch.object(final, 'model_for_arm') as model:
            for cases in invalid_cases:
                with self.subTest(keys=[c.key for c in cases]), self.assertRaises(RuntimeError):
                    final.train_final(cases, 'unused', 'synthetic', 20261106, guard)
            sampler.assert_not_called()
            model.assert_not_called()

    def test_freeze_blocks_training_before_membership_processing(self):
        class FrozenClock:
            @classmethod
            def now(cls, timezone):
                return datetime(2026, 11, 16, 0, 0, tzinfo=timezone)
        with mock.patch.object(final, 'datetime', FrozenClock), \
             mock.patch.object(final, 'WindowSampler') as sampler:
            with self.assertRaisesRegex(RuntimeError, 'frozen'):
                final.train_final([], 'unused', 'synthetic', 20261106, guard)
            sampler.assert_not_called()


class FinalResume(unittest.TestCase):
    def test_interrupted_trial_b_final_fit_repeats_exactly(self):
        cases = [SyntheticCase('idsse-' + m) for m in final.IDS]
        original_batch = final.WindowSampler.batch

        def all_five_synthetic(sampling, window_rng, sampler_rng, size=8):
            # Same labels in every case; force tiny-test coverage without changing random draws.
            return [(i % 5, start, branch) for i, (_, start, branch) in
                    enumerate(original_batch(sampling, window_rng, sampler_rng, size))]

        def tiny_model(_):
            return torch.nn.Linear(final.WIDTH, 3)

        class Interrupted(Exception):
            pass

        writes = 0

        @contextmanager
        def stop_before_second_save():
            nonlocal writes
            writes += 1
            if writes == 3:  # Directory, step1 save, interrupted step2 save.
                raise Interrupted()
            yield

        with tempfile.TemporaryDirectory() as directory, \
             mock.patch.object(final, 'TOTAL_STEPS', 2), \
             mock.patch.object(final, 'STAGE_STEPS', 1), \
             mock.patch.object(final, 'SAVE_EVERY', 1), \
             mock.patch.object(final, 'research_open'), \
             mock.patch.object(final, 'model_for_arm', tiny_model), \
             mock.patch.object(final.WindowSampler, 'batch', all_five_synthetic):
            full, resumed = Path(directory) / 'full', Path(directory) / 'resumed'
            final.train_final(cases, full, 'synthetic', 20261106, guard)
            with self.assertRaises(Interrupted):
                final.train_final(cases, resumed, 'synthetic', 20261106, stop_before_second_save)
            final.train_final(cases, resumed, 'synthetic', 20261106, guard)
            a = torch.load(full / 'progress.pt', weights_only=True)
            b = torch.load(resumed / 'progress.pt', weights_only=True)
            final.validate_saved(a, final.expected_identity('synthetic', 20261106))
            final.confirm_repeat(a, b)
            changed = copy.deepcopy(b)
            changed['component_losses']['cross_entropy'][0] += 1
            with self.assertRaisesRegex(RuntimeError, 'component'):
                final.confirm_repeat(a, changed)
            changed_identity = dict(b['identity'], purpose='fold_experiment')
            with self.assertRaisesRegex(RuntimeError, 'identity'):
                final.validate_saved(b, changed_identity)


if __name__ == '__main__':
    unittest.main()
