"""Synthetic export contracts. User-run only; no real assets or models loaded."""
from copy import deepcopy
from datetime import date
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import export_contract as contract
spec = importlib.util.spec_from_file_location('tested_final_b_export', ROOT.parents[1] / 'scripts/export_tcn_final_b.py')
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


def manifest_fixture():
    value = dict(schema=contract.SCHEMA, registration='registered', training_matches=list(contract.KEYS),
        training_steps_per_member=40000, sampler='short_mix', loss='cross_entropy_plus_0.1_segment_soft_iou',
        class_order=['H', 'A', 'D'], scaler_policy='zeros_ones_521', environment={},
        inference=dict(rotation180_probability_weights=[.5, .5], seed_probability_weights=[.5, .5],
                       switching_penalty=16), quality_evaluation_performed=False, production_promoted=False,
        private_export_completed=False, target_accuracy='unknown', source_lock_sha256='hash',
        selection_review_sha256='hash', members={})
    proofs = {}
    for seed in contract.SEEDS:
        base = f'models/tcn-final-b/{seed}'
        member = dict(model=base + '/first/progress.pt', repeat_model=base + '/repeat/progress.pt',
                      proof=base + '/proof.json', sha256='hash', repeat_sha256='hash', proof_sha256='hash')
        value['members'][str(seed)] = member
        proofs[member['proof']] = dict(registration='registered', seed=seed, steps=40000,
            training_matches=list(contract.KEYS), repeated_training_exact=True, checkpoint_state_reload_exact=True,
            checkpoint_hashes={member['model']: 'hash', member['repeat_model']: 'hash'},
            checks_path=str(contract.FINAL / 'evaluation/checks-synthetic.txt'), checks_sha256='hash')
    return value, proofs


class ExportContractTests(unittest.TestCase):
    def validate(self, value, proofs):
        with patch.object(contract, 'sha', return_value='hash'), patch.object(contract, 'load', side_effect=proofs.__getitem__):
            contract.validate_manifest(value, 'registered', {})

    def test_manifest_exact_two_member_contract(self):
        self.validate(*manifest_fixture())

    def test_reject_recipe_or_membership_changes(self):
        original, proofs = manifest_fixture()
        for key, bad in [('training_matches', list(contract.KEYS[:-1])), ('training_steps_per_member', 20000),
                         ('loss', 'cross_entropy'), ('class_order', ['A', 'H', 'D']),
                         ('production_promoted', True), ('quality_evaluation_performed', True),
                         ('private_export_completed', True), ('environment', {'changed': True})]:
            value = deepcopy(original); value[key] = bad
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                self.validate(value, proofs)

    def test_reject_decoder_or_seed_weight_change(self):
        for key, bad in [('switching_penalty', 8), ('seed_probability_weights', [.75, .25]),
                         ('rotation180_probability_weights', [1, 0])]:
            value, proofs = manifest_fixture(); value['inference'][key] = bad
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                self.validate(value, proofs)

    def test_reject_missing_member_or_repeat_proof(self):
        value, proofs = manifest_fixture(); del value['members']['20261107']
        with self.assertRaises(RuntimeError):
            self.validate(value, proofs)
        value, proofs = manifest_fixture()
        proofs[value['members']['20261106']['proof']]['repeated_training_exact'] = False
        with self.assertRaises(RuntimeError):
            self.validate(value, proofs)

    def test_private_path_and_existing_output_guard(self):
        with patch.object(Path, 'exists', return_value=False), patch.object(Path, 'is_symlink', return_value=False):
            contract.validate_output(contract.OUTPUT_ROOT / 'local')
            for path in ('candidate.csv', 'data/competition/predictions', 'data/competition/tcn-final-b-exports/../local'):
                with self.assertRaises(RuntimeError):
                    contract.validate_output(path)
        with patch.object(Path, 'exists', return_value=True), self.assertRaises(RuntimeError):
            contract.validate_output(contract.OUTPUT_ROOT / 'local')

    def test_delivery_dates_without_training_guard(self):
        contract.permitted_date(date(2026, 11, 16))
        contract.permitted_date(date(2026, 11, 17))
        with self.assertRaises(RuntimeError):
            contract.permitted_date(date(2026, 11, 18))

    def test_validator_requires_none_not_truthy_success(self):
        official = Mock()
        official.validate_submission.return_value = None
        export.validate_csv(Path('synthetic.csv'), official)
        official.validate_submission.assert_called_once_with(official.read_label_csv.return_value, 199319)
        for reason in ('invalid', True, False):
            official.validate_submission.return_value = reason
            with self.assertRaises(RuntimeError):
                export.validate_csv(Path('synthetic.csv'), official)

    def test_half_edges_keep_spells_separate_and_x_excluded(self):
        row = export.output_aggregates(['X', 'H', 'H', 'X', 'H', 'D', 'X'], [(1, 3), (4, 6)], 25)
        self.assertEqual(row['valid_frames'], 4)
        self.assertEqual(row['ha_spell_count'], 2)
        self.assertEqual(row['had_segment_count'], 3)
        self.assertEqual(row['shares'], {'H': .75, 'A': 0, 'D': .25})
        self.assertAlmostEqual(row['mean_ha_spell_seconds'], .06)

    def test_all_dead_has_no_ha_spells(self):
        row = export.output_aggregates(['D', 'D'], [(0, 2)], 25)
        self.assertEqual(row['ha_spell_count'], 0)
        self.assertIsNone(row['mean_ha_spell_seconds'])

    def test_probability_average_order_and_four_views(self):
        import numpy as np
        sys.path.insert(0, str(ROOT.parent / 'tcn-rotation-2026-11-11'))
        from rotation import average_views
        values = [np.array([[.8, .1, .1]]), np.array([[.6, .2, .2]]),
                  np.array([[.2, .7, .1]]), np.array([[.4, .4, .2]])]
        model_code = Mock(WIDTH=521)
        model_code.predict.side_effect = values
        result, views = export.ensemble_probabilities(['one', 'two'], 'x', 'rotated', [(0, 1)],
                                                      model_code, average_views, np, 4)
        expected = average_views(average_views(*values[:2]), average_views(*values[2:]))
        np.testing.assert_array_equal(result, expected)
        self.assertEqual(len(views), 4)
        self.assertEqual([call.args[:2] for call in model_code.predict.call_args_list],
                         [('one', 'x'), ('one', 'rotated'), ('two', 'x'), ('two', 'rotated')])
        self.assertTrue(all(call.kwargs['batch'] == 4 for call in model_code.predict.call_args_list))

    def test_storage_floor_rejects_without_deletion(self):
        with patch.object(contract, 'artifact_bytes', return_value=contract.MAX_BYTES), \
             patch.object(contract.shutil, 'disk_usage', return_value=Mock(free=20 * 1024 ** 3)):
            with self.assertRaises(RuntimeError):
                contract.check_storage()
        with patch.object(contract, 'artifact_bytes', return_value=0), \
             patch.object(contract.shutil, 'disk_usage', return_value=Mock(free=contract.MIN_FREE)):
            with self.assertRaises(RuntimeError):
                contract.check_storage()


if __name__ == '__main__':
    unittest.main()
