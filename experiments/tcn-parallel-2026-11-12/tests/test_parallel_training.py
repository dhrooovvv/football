"""User-run fold guard, seed isolation and interrupted-stage training contracts."""
import copy
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import parallel_training as training


class ParallelTraining(unittest.TestCase):
    def test_identity_isolates_architecture_or_initialization_seed(self):
        attention = training.expected_identity('synthetic', 'attention', training.IDS[0])
        ensemble = training.expected_identity('synthetic', 'ensemble', training.IDS[0])
        self.assertEqual(attention['initialization_seed'], 20261106)
        self.assertEqual(ensemble['initialization_seed'], 20261107)
        for identity in (attention, ensemble):
            self.assertEqual(identity['training_matches'], ['idsse-' + m for m in training.IDS[1:]])
            self.assertEqual(identity['window_seed'], 20261106)
            self.assertEqual(identity['view_seed'], 20685348)
            self.assertEqual((identity['total_steps'], identity['stage_steps']), (40000, 20000))
            self.assertEqual(identity['geometry_matches'], [])
        with self.assertRaises(RuntimeError):
            training.expected_identity('x', 'attention', 'J03WQQ')
        with self.assertRaises(RuntimeError):
            training.expected_identity('x', 'other', training.IDS[0])

    def test_training_rejects_final_five_wrong_fold_or_provider_before_loading(self):
        identity = training.expected_identity('x', 'ensemble', training.IDS[0])
        valid = [SimpleNamespace(key=k, provider='idsse') for k in identity['training_matches']]
        cases = [valid[:-1], valid + [SimpleNamespace(key='idsse-' + training.IDS[0], provider='idsse')],
                 list(reversed(valid)), [SimpleNamespace(key=c.key, provider='pff') for c in valid]]
        with patch.object(training, 'research_open'):
            for case in cases:
                with self.assertRaises(RuntimeError):
                    training.train_fit(case, 'unused', 'x', 'ensemble', training.IDS[0])

    def test_checkpoint_rejects_invalid_counts_identity_and_nonfinite_loss(self):
        identity = training.expected_identity('x', 'attention', training.IDS[0])
        saved = dict(identity=identity, step=0, stage='stage1', losses=[],
                     coverage={s: dict.fromkeys(identity['training_matches'], 0) for s in ('stage1', 'stage2')},
                     supervised_views={s: dict(clean=0, gap=0) for s in ('stage1', 'stage2')},
                     stage_seconds=dict(stage1=0., stage2=0.))
        training.validate_saved(saved, identity)
        for name, value in [('step', 1), ('stage', 'stage2'), ('losses', [float('nan')]),
                            ('identity', {'wrong': True})]:
            changed = copy.deepcopy(saved)
            changed[name] = value
            with self.assertRaises(RuntimeError):
                training.validate_saved(changed, identity)

    def test_repeat_equality_rejects_state_change_and_excludes_time(self):
        a = dict(step=40000, identity={'x': 1}, state={'x': torch.tensor([1.])}, optimizer={},
                 window_rng={}, view_rng={}, torch_rng=torch.tensor([1]), losses=[1.],
                 coverage={}, supervised_views={}, stage_seconds={'stage1': 1.})
        b = copy.deepcopy(a)
        b['stage_seconds']['stage1'] = 4.
        training.confirm_repeat(a, b)
        b['state']['x'][0] = 2.
        with self.assertRaises(RuntimeError):
            training.confirm_repeat(a, b)

    def test_interruption_at_and_after_reset_matches_uninterrupted(self):
        class TinyTCN(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.head = torch.nn.Linear(521, 3)

            def forward(self, values):
                return self.head(values)

        class Case:
            provider = 'idsse'
            blocks = [[0, 300]]
            labels = np.zeros(300, np.int8)

            def __init__(self, key):
                self.key = key

            def read(self, indices, gap):
                values = np.zeros((len(indices), 521), np.float32)
                values[:, 0] = indices / 300
                values[:, 1] = float(gap)
                return values

        held_out = training.IDS[0]
        cases = [Case('idsse-' + m) for m in training.IDS[1:]]
        with tempfile.TemporaryDirectory() as temporary, \
                patch.object(training, 'model_for_arm', lambda arm: TinyTCN()), \
                patch.object(training, 'research_open'), \
                patch.object(training, 'STAGE_STEPS', 10), \
                patch.object(training, 'TOTAL_STEPS', 20), \
                patch.object(training, 'SAVE_EVERY', 1):
            root = Path(temporary)
            training.train_fit(cases, root / 'complete', 'synthetic', 'ensemble', held_out)
            expected = torch.load(root / 'complete/progress.pt', weights_only=True)
            self.assertEqual(expected['coverage']['stage1'], expected['coverage']['stage2'])
            self.assertEqual(expected['supervised_views']['stage1'], expected['supervised_views']['stage2'])
            self.assertEqual({int(v['step']) for v in expected['optimizer']['state'].values()}, {10})
            for stop_at in (10, 11):
                directory = root / str(stop_at)
                original_replace = os.replace
                count = [0]

                def interrupt(source, destination):
                    original_replace(source, destination)
                    count[0] += 1
                    if count[0] == stop_at:
                        raise InterruptedError('Synthetic interruption after completed checkpoint')

                with patch.object(training.os, 'replace', side_effect=interrupt):
                    with self.assertRaises(InterruptedError):
                        training.train_fit(cases, directory, 'synthetic', 'ensemble', held_out)
                training.train_fit(cases, directory, 'synthetic', 'ensemble', held_out)
                actual = torch.load(directory / 'progress.pt', weights_only=True)
                training.confirm_repeat(expected, actual)


if __name__ == '__main__':
    unittest.main()
