"""Release provenance/storage contracts; supplied for user-run execution only."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import release_contract as c


class ReleaseStorage(unittest.TestCase):
    def test_prior_roots_count_without_mutating_old_global_roots(self):
        old_roots = (Path('old/data'), Path('old/models'), Path('old/experiment'))
        old = SimpleNamespace(ARTIFACT_ROOTS=old_roots)
        with patch.object(c, '_missed', return_value=old):
            self.assertEqual(c.artifact_roots(), old_roots + (c.DATA, c.MODELS, c.R))
            self.assertIs(old.ARTIFACT_ROOTS, old_roots)

    def test_storage_floor_and_shared_budget(self):
        disk = SimpleNamespace(free=c.MIN_FREE_BYTES + c.RESERVE_BYTES)
        with patch.object(c, 'artifact_bytes', return_value=0), patch.object(c.shutil, 'disk_usage', return_value=disk):
            self.assertEqual(c.check_storage()['free_bytes'], disk.free)
            disk.free -= 1
            with self.assertRaises(RuntimeError):
                c.check_storage()
        disk.free = 100 * 1024 ** 3
        with patch.object(c, 'artifact_bytes', return_value=c.MAX_BYTES), patch.object(c.shutil, 'disk_usage', return_value=disk):
            with self.assertRaises(RuntimeError):
                c.check_storage()

    def test_accounting_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'value').write_bytes(b'abc')
            with patch.object(c, 'artifact_roots', return_value=(root,)):
                self.assertEqual(c.artifact_bytes(), 3)
                (root / 'link').symlink_to(root / 'value')
                with self.assertRaises(RuntimeError):
                    c.artifact_bytes()

    def test_invalid_seed_rejected_before_lock_acquisition(self):
        for seed in (True, '20261106', 42):
            with self.assertRaises(RuntimeError):
                with c.operation_lock(seed):
                    self.fail('Invalid seed entered operation')


def evidence_fixture():
    paths = {}
    hashes = {}
    def digest(path):
        return hashes.get(str(path), 'sha:' + str(path))
    signature = 'registered-missed'
    parent_path = c.MISSED / 'evaluation/a/results.json'
    bound = dict(sampler='short_mix', parent_trial='a', parent_results_sha256=digest(parent_path),
                 reviewed_a_sha256='review-a')
    trial_signature = hashlib.sha256((signature + json.dumps(bound, sort_keys=True)).encode()).hexdigest()
    directory = c.MISSED / 'evaluation/b'
    rows = []
    parent_rows = []
    for match in c.IDS:
        for condition in ('clean', 'targetlike'):
            metric = dict(spellF1=.5, macroF1=.8)
            parent_rows.append(dict(match=match, condition=condition, candidate=metric, csv_sha256='parent-csv'))
            parent_reconstruction = f'data/tcn-missed/b/predictions/{match}-{condition}-parent.csv'
            hashes[parent_reconstruction] = 'parent-csv'
            csvs = [f'data/tcn-missed/b/predictions/{match}-{condition}-{tag}.csv' for tag in ('first', 'reload', 'batch4')]
            for name in csvs:
                hashes[name] = 'candidate-csv'
            rows.append(dict(match=match, condition=condition, parent=metric,
                             candidate=dict(spellF1=.51, macroF1=.8),
                             reload_probabilities_equal_both_views=True, csv_bytes_equal_reload_batch4=True,
                             csv_paths=csvs, csv_sha256='candidate-csv', parent_reconstruction_path=parent_reconstruction,
                             parent_csv_sha256='parent-csv'))
    paths[str(parent_path)] = parent_rows
    paths[str(directory / 'results.json')] = rows
    gate = dict(quality_eligible=True, primary_median_delta=.01)
    paths[str(directory / 'gate-v2.json')] = gate
    proof_hashes = {}
    for match in c.IDS:
        for seed in c.SEEDS:
            name = str(directory / 'fits' / f'{match}-{seed}.json')
            proof_hashes[name] = digest(name)
            checks_path = str(directory / 'checks.txt')
            checkpoints = {f'models/tcn-missed/b/{match}/{seed}/{fit}/progress.pt':
                           digest(f'models/tcn-missed/b/{match}/{seed}/{fit}/progress.pt')
                           for fit in ('first', 'repeat')}
            paths[name] = dict(match=match, seed=seed, trial='b', trial_signature=trial_signature,
                               sampler='short_mix', training_steps=40000, exact_repeat=True,
                               training_matches=['idsse-' + m for m in c.IDS if m != match],
                               checks_path=checks_path, checks_sha256=digest(checks_path), checkpoint_hashes=checkpoints)
    paths[str(directory / 'completion.json')] = dict(completed=True, trial='b', registration=signature,
        trial_signature=trial_signature, binding=bound, case_count=10, contracts_passed=True,
        repeated_training_exact=True, production_changed=False, fit_proofs=proof_hashes,
        results_sha256=digest(directory / 'results.json'), gate_sha256=digest(directory / 'gate-v2.json'))
    paths[str(c.MISSED / 'reviewed-b.json')] = dict(reviewed=True, accepted_under_registered_gate=True,
        selected_trial='b', sampler='short_mix', loss='cross_entropy_plus_0.1_segment_soft_iou',
        results_sha256=digest(directory / 'results.json'), production_changed=False,
        authorized_experiment_round_complete=True)
    old = SimpleNamespace(binding=lambda trial, sig: bound, gate_v2=lambda *args: gate)
    return paths, hashes, digest, old, signature


class BReleaseBinding(unittest.TestCase):
    def _run(self, mutate=None):
        paths, hashes, digest, old, signature = evidence_fixture()
        if mutate:
            mutate(paths, hashes)
        with patch.object(c, '_missed', return_value=old), patch.object(c, '_load', side_effect=lambda path: paths[str(path)]), patch.object(c, 'sha', side_effect=digest), patch.object(c, 'committed_bytes') as commit:
            result = c.validate_b_evidence(signature)
            self.assertEqual(commit.call_count, 2)
            return result

    def test_complete_accepted_b_requires_every_checkpoint_and_prediction_pin(self):
        paths = self._run()
        self.assertIn('models/tcn-missed/b/J03WMX/20261106/first/progress.pt', paths)
        self.assertIn('data/tcn-missed/b/predictions/J03WMX-clean-batch4.csv', paths)
        self.assertIn(str(c.MISSED / 'reviewed-b.json'), paths)

    def test_rejected_or_unreviewed_b_cannot_prepare_release(self):
        for field in ('reviewed', 'accepted_under_registered_gate', 'authorized_experiment_round_complete'):
            def mutate(paths, hashes, field=field):
                paths[str(c.MISSED / 'reviewed-b.json')][field] = False
            with self.assertRaises(RuntimeError):
                self._run(mutate)

    def test_forged_parent_or_missing_repeat_proof_is_rejected(self):
        def bad_parent(paths, hashes):
            paths[str(c.MISSED / 'evaluation/b/results.json')][0]['parent'] = dict(spellF1=.1, macroF1=.8)
        with self.assertRaises(RuntimeError):
            self._run(bad_parent)
        def no_repeat(paths, hashes):
            paths[str(c.MISSED / 'evaluation/b/fits/J03WMX-20261106.json')]['exact_repeat'] = False
        with self.assertRaises(RuntimeError):
            self._run(no_repeat)

    def test_checkpoint_or_csv_byte_changes_reject_registration(self):
        for name in ('models/tcn-missed/b/J03WMX/20261106/first/progress.pt',
                     'data/tcn-missed/b/predictions/J03WMX-clean-batch4.csv'):
            with self.assertRaises(RuntimeError):
                self._run(lambda paths, hashes, name=name: hashes.update({name: 'changed'}))


if __name__ == '__main__':
    unittest.main()
