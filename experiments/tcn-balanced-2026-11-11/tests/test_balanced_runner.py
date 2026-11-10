"""Synthetic saved-result integrity contracts; supplied for user execution only."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path("scripts").resolve()))
import run_tcn_balanced as runner


class BalancedRunnerContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        base = Path(self.temporary.name)
        self.root, self.data = base / "experiment", base / "data"
        (self.root / "evaluation").mkdir(parents=True)
        (self.data / "predictions").mkdir(parents=True)
        self.patches = [patch.object(runner, "ROOT", self.root), patch.object(runner, "DATA", self.data)]
        for item in self.patches:
            item.start()
        self.signature = "synthetic-result-integrity"
        self.matches = ["JTEST1", "JTEST2", "JTEST3", "JTEST4", "JTEST5"]
        self.members = {"training": [dict(key="idsse-" + match, match=match, provider="idsse")
                                      for match in self.matches]
                                   + [dict(key="pff-P1", match="P1", provider="pff")]}

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.temporary.cleanup()

    def write_fixture(self, gain=True):
        rows = []
        all_keys = [item["key"] for item in self.members["training"]]
        csv_bytes = b"frame,label\n0,H\n"
        digest = hashlib.sha256(csv_bytes).hexdigest()
        candidate_spell = .52 if gain else .5
        delta = candidate_spell - .5
        for match in self.matches:
            pair = []
            for condition in ("clean", "targetlike"):
                row = dict(match=match, condition=condition, repeated_training_exact=True,
                           csv_sha256=digest, parent=dict(spellF1=.5, macroF1=.8),
                           candidate=dict(spellF1=candidate_spell, macroF1=.8))
                pair.append(row)
                for tag in ("first", "repeat", "batch4"):
                    (self.data / "predictions" / f"{match}-{condition}-{tag}.csv").write_bytes(csv_bytes)
            training = [key for key in all_keys if key != "idsse-" + match]
            fold = dict(registration=self.signature, training_matches=training,
                        training_coverage={key: {} for key in training}, rows=pair)
            (self.root / "evaluation" / (match + ".json")).write_text(json.dumps(fold))
            rows.extend(pair)
        gate = dict(quality_eligible=gain, primary_median_delta=delta,
                    primary_deltas={match: delta for match in self.matches},
                    paired_spell_deltas={match: delta for match in self.matches},
                    paired_macro_deltas={match: 0. for match in self.matches},
                    matches_improved=5 if gain else 0, contract_checks_passed=True,
                    repeated_training_exact=True, csv_repeatability_cases=10)
        (self.root / "evaluation/results.json").write_text(json.dumps(rows))
        (self.root / "evaluation/gate.json").write_text(json.dumps(gate))

    def test_complete_consistent_evidence_passes_but_incomplete_folds_reject(self):
        self.write_fixture()
        self.assertTrue(runner.verified_gate(self.members, self.signature))
        (self.root / "evaluation/JTEST5.json").unlink()
        with self.assertRaisesRegex(RuntimeError, "All five exact"):
            runner.verified_gate(self.members, self.signature)

    def test_cached_fold_cannot_include_its_held_out_match(self):
        self.write_fixture()
        path = self.root / "evaluation/JTEST1.json"
        fold = json.loads(path.read_text())
        fold["training_matches"].append("idsse-JTEST1")
        path.write_text(json.dumps(fold))
        with self.assertRaisesRegex(RuntimeError, "membership differs"):
            runner.verify_completed_folds(self.members, self.signature)

    def test_tampered_repeat_csv_is_rejected(self):
        self.write_fixture()
        path = self.data / "predictions/JTEST1-targetlike-repeat.csv"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(RuntimeError, "CSV hash differs"):
            runner.verify_completed_folds(self.members, self.signature)

    def test_saved_true_gate_cannot_override_zero_gain_complete_metrics(self):
        self.write_fixture(gain=False)
        self.assertFalse(runner.verified_gate(self.members, self.signature))
        path = self.root / "evaluation/gate.json"
        gate = json.loads(path.read_text())
        gate["quality_eligible"] = True
        path.write_text(json.dumps(gate))
        with self.assertRaisesRegex(RuntimeError, "Saved gate disagrees"):
            runner.verified_gate(self.members, self.signature)
