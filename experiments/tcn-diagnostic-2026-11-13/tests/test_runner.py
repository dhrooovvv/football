"""No real match files, checkpoints, target assets or numerical inference."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
sys.path[:0] = [str(Path('scripts').resolve()), str(Path('experiments/tcn-diagnostic-2026-11-13').resolve())]
import diagnose_tcn_possessions as runner


class RunnerTests(unittest.TestCase):
    def test_csv_digest_matches_export_contract(self):
        expected = hashlib.sha256(b'frame,label\n0,H\n1,A\n2,D\n3,X\n').hexdigest()
        self.assertEqual(runner.csv_digest(np.array(list('HADX'))), expected)

    def test_cache_requires_signature_content_and_checks(self):
        with tempfile.TemporaryDirectory() as root:
            checks = Path(root)/'checks.txt'; checks.write_text('synthetic checks evidence')
            path = Path(root)/'unit.json'
            value = dict(signature='registered', complete=True,
                         checks_path=str(checks), checks_sha256=runner.sha(checks))
            value['content_sha256'] = hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()
            path.write_text(json.dumps(value))
            self.assertTrue(runner.cached_unit(path, 'registered')['complete'])
            with self.assertRaises(RuntimeError):
                runner.cached_unit(path, 'different')
            value['complete'] = False; path.write_text(json.dumps(value))
            with self.assertRaises(RuntimeError):
                runner.cached_unit(path, 'registered')

    def test_absent_cache_and_archive_hash_fail_closed(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertIsNone(runner.cached_unit(Path(root)/'missing.json', 'registered'))
        with patch.object(runner, 'sha', return_value='bad'):
            with self.assertRaises(RuntimeError):
                runner.read_archive({'csv_paths': ['unused.csv'], 'csv_sha256': 'good'}, 2, None)


if __name__ == '__main__':
    unittest.main()
