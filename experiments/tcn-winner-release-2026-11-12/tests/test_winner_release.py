"""Synthetic release contracts; no real assets, fitting or quality claims."""
import copy
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import tempfile

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
from release_contract import KEYS, check_membership, expected_identity
from export_tcn_winner import output_aggregates


class MembershipContracts(unittest.TestCase):
    def cases(self, keys=KEYS):
        return [SimpleNamespace(key=key, provider='idsse') for key in keys]

    def test_exact_five_only(self):
        check_membership(self.cases())
        for keys in (KEYS[:-1], KEYS + ('idsse-J03WQQ',), tuple(reversed(KEYS)),
                     KEYS[:-1] + ('idsse-J03WR9',), KEYS[:-1] + ('pff-extra',)):
            with self.assertRaises(RuntimeError):
                check_membership(self.cases(keys))

    def test_provider_not_inferred_from_key(self):
        cases = self.cases()
        cases[0].provider = 'pff'
        with self.assertRaises(RuntimeError):
            check_membership(cases)

    def test_identity_locks_winning_recipe(self):
        identity = expected_identity('a' * 64, {'sha256': 'b' * 64})
        self.assertEqual(identity['total_steps'], 40000)
        self.assertEqual(identity['stage_steps'], 20000)
        self.assertEqual(identity['training_matches'], list(KEYS))
        self.assertEqual(identity['geometry_matches'], [])
        self.assertEqual((identity['seed'], identity['view_seed']), (20261106, 20685348))
        self.assertEqual((identity['window'], identity['halo'], identity['core'], identity['batch']),
                         (250, 25, 200, 8))
        self.assertEqual(identity['stage_boundary'], 'reset_Adam_and_supervised_RNG_in_both_arms')
        self.assertNotIn('held_out', identity)

    def test_aggregates_do_not_join_across_halves(self):
        aggregate = output_aggregates(['X', 'H', 'H', 'X', 'H', 'D', 'X'], [[1, 3], [4, 6]], 2)
        self.assertEqual(aggregate['spell_count'], 3)
        self.assertEqual(aggregate['shares'], dict(H=.75, A=0., D=.25))
        self.assertEqual(aggregate['mean_spell_seconds'], 2 / 3)


class SavedContracts(unittest.TestCase):
    def checkpoint(self):
        from winner_training import validate_saved
        identity = expected_identity('a' * 64, {})
        record = dict(identity=identity, step=0, losses=[], stage='stage1',
                      coverage={s: dict.fromkeys(KEYS, 0) for s in ('stage1', 'stage2')},
                      supervised_views={s: dict(clean=0, gap=0) for s in ('stage1', 'stage2')},
                      stage_seconds=dict(stage1=0., stage2=0.))
        validate_saved(record, identity)
        return record, identity

    def test_resume_rejects_changed_identity_or_counts(self):
        from winner_training import validate_saved
        record, identity = self.checkpoint()
        for key, value in [('step', 40001), ('losses', [1.]), ('stage', 'stage2')]:
            changed = copy.deepcopy(record)
            changed[key] = value
            with self.assertRaises(RuntimeError):
                validate_saved(changed, identity)
        changed = copy.deepcopy(record)
        changed['coverage']['stage1'][KEYS[0]] = 1
        with self.assertRaises(RuntimeError):
            validate_saved(changed, identity)

    def test_exact_tensor_equality_and_unequal_nested_state(self):
        import torch
        from winner_training import deep_equal
        left = dict(state={'x': torch.tensor([1.])}, rng={'state': 1}, losses=[1., 2.])
        self.assertTrue(deep_equal(left, copy.deepcopy(left)))
        right = copy.deepcopy(left)
        right['state']['x'][0] += .00001
        self.assertFalse(deep_equal(left, right))

    def test_interrupted_resume_on_both_sides_of_optimizer_reset(self):
        import os
        import numpy as np
        import torch
        import winner_training as training

        class TinyTCN(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.head = torch.nn.Linear(521, 3)

            def forward(self, values):
                return self.head(values)

        class Case:
            provider = 'idsse'
            blocks = [[0, 300]]
            labels = np.zeros(300, dtype=np.int8)

            def __init__(self, key):
                self.key = key

            def read(self, indices, augmented):
                values = np.zeros((len(indices), 521), np.float32)
                values[:, 0] = indices / 300
                values[:, 1] = float(augmented)
                return values

        # Budget/model replacements are test-local; the public runner exposes no overrides.
        cases = [Case(key) for key in KEYS]
        with tempfile.TemporaryDirectory() as temporary, \
                patch.object(training, 'TCN', TinyTCN), \
                patch.object(training, 'STAGE_STEPS', 10), \
                patch.object(training, 'TOTAL_STEPS', 20), \
                patch.object(training, 'SAVE_EVERY', 1), \
                patch.object(training, 'permitted_date'):
            root = Path(temporary)
            training.train_final(cases, root / 'complete', 'synthetic', {})
            expected = torch.load(root / 'complete/progress.pt', weights_only=True)
            self.assertEqual(expected['coverage']['stage1'], expected['coverage']['stage2'])
            self.assertEqual(expected['supervised_views']['stage1'], expected['supervised_views']['stage2'])
            self.assertEqual({int(value['step']) for value in expected['optimizer']['state'].values()}, {10})
            for stop_at in (10, 11):
                with self.subTest(interruption_after_update=stop_at):
                    directory = root / str(stop_at)
                    calls = [0]
                    replace = os.replace

                    def interrupt_after_checkpoint(source, target):
                        replace(source, target)
                        calls[0] += 1
                        if calls[0] == stop_at:
                            raise InterruptedError('Synthetic interruption after checkpoint')

                    with patch.object(training.os, 'replace', side_effect=interrupt_after_checkpoint):
                        with self.assertRaises(InterruptedError):
                            training.train_final(cases, directory, 'synthetic', {})
                    training.train_final(cases, directory, 'synthetic', {})
                    actual = torch.load(directory / 'progress.pt', weights_only=True)
                    for key in ('identity', 'state', 'optimizer', 'window_rng', 'view_rng',
                                'torch_rng', 'losses', 'coverage', 'supervised_views'):
                        self.assertTrue(training.deep_equal(expected[key], actual[key]), key)


if __name__ == '__main__':
    unittest.main()
