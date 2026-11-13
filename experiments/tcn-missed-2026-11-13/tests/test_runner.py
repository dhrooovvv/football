"""Runner proof/binding contracts; synthetic only, user executes."""
import importlib.util
import builtins
from types import SimpleNamespace
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('missed_runner', ROOT.parents[1] / 'scripts/run_tcn_missed.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class RunnerContracts(unittest.TestCase):
    def test_trial_signature_changes_with_review_fingerprint(self):
        with patch.object(r, 'binding', return_value={'reviewed_a_sha256': 'one'}):
            _, first = r.trial_identity('b', 'base')
        with patch.object(r, 'binding', return_value={'reviewed_a_sha256': 'two'}):
            _, second = r.trial_identity('b', 'base')
        self.assertNotEqual(first, second)

    def test_dependency_loader_is_process_cached(self):
        configure = Mock()
        names = {
            'numpy': SimpleNamespace(), 'torch': SimpleNamespace(),
            'parallel_model': SimpleNamespace(configure=configure),
            'expanded_data': SimpleNamespace(CompactCase=object),
            'training': SimpleNamespace(train_fit=object, validate_saved=object,
                        expected_identity=object, confirm_repeat=object),
            'rotation': SimpleNamespace(rotate180=object, average_views=object),
            'possession.decode': SimpleNamespace(decode=object),
            'possession.inputs': SimpleNamespace(export_labels=object),
            'review_frozen': SimpleNamespace(score=object),
            'evaluate_pff': SimpleNamespace(missing=object),
            'possession_metrics': SimpleNamespace(),
            'run_tcn_parallel': SimpleNamespace(metrics=object)}
        original_import = builtins.__import__
        def fake_import(name, *args, **kwargs):
            return names[name] if name in names else original_import(name, *args, **kwargs)
        r.dependencies.cache_clear()
        try:
            with patch('builtins.__import__', side_effect=fake_import):
                self.assertIs(r.dependencies(), r.dependencies())
            configure.assert_called_once_with()
        finally:
            r.dependencies.cache_clear()

    def test_fit_verifier_rejects_changed_checkpoint_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'proof.json'
            first, repeat = Path(temp) / 'first.pt', Path(temp) / 'repeat.pt'
            log = Path(temp) / 'checks.txt'
            log.write_text('OK\n'); first.write_bytes(b'first'); repeat.write_bytes(b'repeat')
            value = dict(trial_signature='sig', sampler='short_mix', seed=20261106, match=r.IDS[0],
                         exact_repeat=True, training_steps=40000, checks_path=str(log), checks_sha256=r.sha(log),
                         training_matches=['idsse-' + m for m in r.IDS if m != r.IDS[0]],
                         checkpoint_hashes={str(p): r.sha(p) for p in (first, repeat)})
            path.write_text(json.dumps(value))
            with patch.object(r, 'proof_path', return_value=path), patch.object(r, 'fit_path', side_effect=[first, repeat]):
                self.assertEqual(r.verify_fit('a', r.IDS[0], 20261106, 'sig', 'short_mix'), value)
            first.write_bytes(b'changed')
            with patch.object(r, 'proof_path', return_value=path), patch.object(r, 'fit_path', side_effect=[first, repeat]):
                with self.assertRaises(RuntimeError):
                    r.verify_fit('a', r.IDS[0], 20261106, 'sig', 'short_mix')


if __name__ == '__main__':
    unittest.main()
