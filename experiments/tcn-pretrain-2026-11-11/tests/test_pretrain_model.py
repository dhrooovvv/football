"""Synthetic user-run contracts; no experiment quality claim follows from these."""
from pathlib import Path
import json
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pretrain_data as data_code
import pretrain_model as model_code
import pretrain_training as training
from pretrain_data import GeometryCase, eligible_starts, validate_membership, IDS
from pretrain_model import TCN, OriginalTCN, WIDTH, WINDOW, HALO, CORE, reconstruction_loss


def make_case(root, match, provider='idsse'):
    directory = root / (provider + '-' + match)
    directory.mkdir()
    frames = 600
    rng = np.random.default_rng(17)
    objects = np.zeros((frames, 64, 5), np.float32)
    objects[:, [0, 1, 2, 3, 63], :4] = rng.normal(0, .1, (frames, 5, 4))
    objects[:, [0, 1, 2, 3, 63], 4] = 1
    objects[70:80, -1, :5] = 0  # Naturally missing: never a target.
    roles = np.zeros((64, 3), np.float32)
    roles[:2, 0] = 1; roles[2:4, 1] = 1; roles[-1, 2] = 1
    core = np.zeros((frames, 9), np.float32)
    core[:, 5] = objects[:, -1, 4]
    gap_ball = objects[:, -1].copy()
    gap_ball[30:180] = 0; gap_ball[350:500] = 0
    gap_core = core.copy(); gap_core[:, 5] = gap_ball[:, 4]
    arrays = {'objects.npy': objects, 'roles.npy': roles, 'core.npy': core,
              'gap_ball.npy': gap_ball, 'gap_core.npy': gap_core}
    for name, value in arrays.items(): np.save(directory / name, value)
    (directory / 'metadata.json').write_text(json.dumps(dict(key=directory.name,
        provider=provider, frames=frames, blocks=[[0, 300], [300, 600]], match=match)))
    # A geometry loader must not open this intentionally invalid label file.
    (directory / 'labels.npy').write_text('forbidden geometry-only label input')
    case = GeometryCase(directory)
    labels = np.resize(np.arange(3, dtype=np.int8), frames)
    supervised = SimpleNamespace(key=case.key, provider=provider, labels=labels,
                                 blocks=case.blocks, read=case.read)
    return case, supervised


class PretrainingContracts(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.backends.mkldnn.enabled = False
        torch.use_deterministic_algorithms(True)
        torch.manual_seed(20261106)
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def cases(self):
        pairs = [make_case(self.root, match) for match in IDS[1:]]
        return [v[0] for v in pairs], [v[1] for v in pairs]

    def fit(self, supervised, geometry, path, arm, stage_steps=2):
        return training.train_fit(supervised, geometry, path, 'synthetic', arm,
                                  IDS[0], stage_steps=stage_steps, save_every=1, allowed_pff=[])

    def test_original_initialization_and_inference_path_preserved(self):
        torch.manual_seed(20261106); parent = OriginalTCN().eval()
        torch.manual_seed(20261106); candidate = TCN().eval()
        self.assertEqual(sum(p.numel() for p in candidate.parameters()), 9701)
        for name, value in parent.state_dict().items():
            self.assertTrue(torch.equal(value, candidate.state_dict()[name]), name)
        case, _ = make_case(self.root, IDS[1])
        x = torch.from_numpy(case.read(np.arange(WINDOW), False)[None])
        with torch.no_grad():
            expected = parent(x)
            self.assertTrue(torch.equal(expected, candidate(x)))
            self.assertEqual(candidate.forward_reconstruction(x).shape, (1, WINDOW, 2))
            candidate.reconstruction.weight.fill_(100)
            candidate.reconstruction.bias.fill_(-200)
            self.assertTrue(torch.equal(expected, candidate(x)))

    def test_geometry_reader_never_opens_labels(self):
        case, _ = make_case(self.root, IDS[1])
        original_load = np.load
        opened = []
        def guarded(path, *args, **kwargs):
            opened.append(Path(path).name)
            if Path(path).name == 'labels.npy': raise AssertionError('Label access')
            return original_load(path, *args, **kwargs)
        with patch.object(data_code.np, 'load', guarded):
            loaded = GeometryCase(case.directory)
            eligible_starts(loaded)
            loaded.read(np.arange(WINDOW), True)
        self.assertNotIn('labels.npy', opened)
        self.assertFalse(hasattr(loaded, 'labels'))

    def test_mask_targets_exclude_natural_gaps_and_do_not_leak_into_input(self):
        case, _ = make_case(self.root, IDS[1])
        indices = np.arange(WINDOW)
        target, valid = case.targets(indices)
        self.assertTrue(valid[30:70].all())
        self.assertFalse(valid[70:80].any())
        self.assertTrue(valid[80:180].all())
        self.assertFalse(valid[:30].any())
        np.testing.assert_array_equal(target[~valid], np.zeros_like(target[~valid]))
        before = case.read(indices, True)
        objects = np.load(case.directory / 'objects.npy').copy()
        objects[indices[valid], -1, :2] += .5
        temporary = case.directory / 'objects-replaced.npy'
        np.save(temporary, objects)
        temporary.replace(case.directory / 'objects.npy')
        changed = GeometryCase(case.directory)
        np.testing.assert_array_equal(before, changed.read(indices, True))
        after_target, after_valid = changed.targets(indices)
        np.testing.assert_array_equal(valid, after_valid)
        self.assertFalse(np.array_equal(target[valid], after_target[valid]))

    def test_geometry_windows_are_half_local_and_observation_only(self):
        case, _ = make_case(self.root, IDS[1])
        starts = eligible_starts(case)
        self.assertTrue(all(0 <= s <= 50 or 300 <= s <= 350 for s in starts))
        for start in starts:
            _, mask = case.targets(np.arange(start + HALO, start + HALO + CORE))
            self.assertTrue(mask.any())
        self.assertFalse(hasattr(case, 'labels'))
        case.arrays['gap_ball.npy'] = case.arrays['objects.npy'][:, -1]
        with self.assertRaisesRegex(ValueError, 'No observed'):
            eligible_starts(case)

    def test_reconstruction_loss_masks_invalid_and_reaches_shared_encoder(self):
        prediction = torch.zeros((1, 3, 2), requires_grad=True)
        target = torch.tensor([[[1., 2.], [float('nan'), float('nan')], [3., 4.]]])
        valid = torch.tensor([[True, False, True]])
        loss = reconstruction_loss(prediction, target, valid)
        self.assertEqual(loss.item(), 7.5)
        loss.backward()
        self.assertTrue(torch.equal(prediction.grad[0, 1], torch.zeros(2)))
        with self.assertRaisesRegex(ValueError, 'No genuinely'):
            reconstruction_loss(prediction, target, torch.zeros_like(valid))
        case, _ = make_case(self.root, IDS[1]); model = TCN()
        target, valid = case.targets(np.arange(HALO, HALO + CORE))
        values = torch.from_numpy(case.read(np.arange(WINDOW), True)[None])
        model.zero_grad(set_to_none=True)
        loss = reconstruction_loss(model.forward_reconstruction(values)[:, HALO:HALO + CORE],
                                   torch.from_numpy(target[None]), torch.from_numpy(valid[None]))
        loss.backward()
        self.assertGreater(model.object.weight.grad.abs().sum().item(), 0)
        self.assertGreater(model.layers[0].weight.grad.abs().sum().item(), 0)
        self.assertIsNone(model.layers[-1].weight.grad)

    def test_fold_membership_rejects_held_out_and_protected_sources(self):
        geometry, supervised = self.cases()
        validate_membership(supervised, geometry, IDS[0], [])
        with self.assertRaisesRegex(ValueError, 'four training'):
            validate_membership(supervised[:-1], geometry, IDS[0], [])
        fake = SimpleNamespace(key='idsse-' + IDS[0], provider='idsse')
        with self.assertRaisesRegex(ValueError, 'fold-local'):
            validate_membership(supervised, geometry + [fake], IDS[0], [])
        with self.assertRaisesRegex(ValueError, 'Protected'):
            validate_membership(supervised, geometry, IDS[0], ['3846'])
        with self.assertRaisesRegex(ValueError, 'Protected'):
            GeometryCase(self.root / 'idsse-J03WQQ')

    def test_control_and_pretraining_stage_reset_and_supervised_rng_match(self):
        geometry, supervised = self.cases()
        self.fit(supervised, [], self.root / 'control', 'control', stage_steps=3)
        self.fit(supervised, geometry, self.root / 'pretrain', 'pretrain', stage_steps=3)
        control = torch.load(self.root / 'control/progress.pt', map_location='cpu', weights_only=True)
        pretrain = torch.load(self.root / 'pretrain/progress.pt', map_location='cpu', weights_only=True)
        self.assertEqual(control['coverage']['stage2'], pretrain['coverage']['stage2'])
        self.assertEqual(control['coverage']['stage1'], control['coverage']['stage2'])
        self.assertEqual(control['window_rng'], pretrain['window_rng'])
        self.assertEqual(control['view_rng'], pretrain['view_rng'])
        self.assertEqual(control['supervised_views']['stage2'], pretrain['supervised_views']['stage2'])
        self.assertEqual(control['target_counts'], {'stage1': 0, 'stage2': 0})
        self.assertGreater(pretrain['target_counts']['stage1'], 0)
        self.assertEqual(pretrain['target_counts']['stage2'], 0)
        for saved in (control, pretrain):
            self.assertEqual(set(saved['stage_seconds']), {'stage1', 'stage2'})
            self.assertTrue(all(np.isfinite(v) and v >= 0 for v in saved['stage_seconds'].values()))
            steps = [float(state['step']) for state in saved['optimizer']['state'].values()]
            self.assertTrue(steps)
            self.assertEqual(set(steps), {3.})

    def test_repeat_and_resume_at_stage_boundary_and_mid_second_stage(self):
        geometry, supervised = self.cases()
        reference, losses, coverage = self.fit(supervised, geometry, self.root / 'reference', 'pretrain', 3)
        repeated, repeat_losses, repeat_coverage = self.fit(supervised, geometry, self.root / 'repeat', 'pretrain', 3)
        training.confirm_repeat(reference, repeated, losses, repeat_losses, coverage, repeat_coverage)
        original_writer = training.write_checkpoint
        for interruption in (3, 4):
            directory = self.root / ('resumed-' + str(interruption))
            def interrupted(path, payload):
                original_writer(path, payload)
                if payload['step'] == interruption: raise KeyboardInterrupt()
            with patch.object(training, 'write_checkpoint', interrupted):
                with self.assertRaises(KeyboardInterrupt):
                    self.fit(supervised, geometry, directory, 'pretrain', 3)
            resumed, resumed_losses, resumed_coverage = self.fit(supervised, geometry, directory, 'pretrain', 3)
            training.confirm_repeat(reference, resumed, losses, resumed_losses, coverage, resumed_coverage)
            saved = torch.load(directory / 'progress.pt', map_location='cpu', weights_only=True)
            target = torch.load(self.root / 'reference/progress.pt', map_location='cpu', weights_only=True)
            self.assertEqual(saved['target_counts'], target['target_counts'])
            self.assertEqual(saved['supervised_views'], target['supervised_views'])
        with self.assertRaisesRegex(RuntimeError, 'identity'):
            training.train_fit(supervised, geometry, self.root / 'reference', 'different', 'pretrain', IDS[0],
                               stage_steps=3, save_every=1, allowed_pff=[])


if __name__ == '__main__':
    unittest.main()
