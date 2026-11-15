"""User-run synthetic contracts; never label synthetic results as match quality."""
from contextlib import nullcontext
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(PROJECT/'scripts'),str(PROJECT/'experiments/tcn-hybrid-2026-11-14'),
             str(PROJECT/'experiments/graph-long-2026-11-15')]
import torch
import hybrid_training as original
import long_training as longer
from hybrid_model import configure
from parallel_training import deep_equal
from long_contract import projection

spec=importlib.util.spec_from_file_location('original_graph_synthetic_cases',
    PROJECT/'experiments/tcn-hybrid-2026-11-14/tests/test_training.py')
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)


class LongGraphContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):configure()

    def test_identity_changes_only_budget_and_registration(self):
        old=original.expected_identity('old','graph',original.SEEDS[0],original.IDS[-1])
        new=longer.expected_identity('new','graph',original.SEEDS[0],original.IDS[-1])
        self.assertEqual(new['total_steps'],50000)
        self.assertEqual({k for k in old if old[k]!=new[k]}, {'registration','total_steps'})
        with self.assertRaises(RuntimeError):
            longer.expected_identity('new','graph',original.SEEDS[0],original.IDS[-1],steps=60000)

    def test_warm_start_exact_repeat_resume_and_source_preservation(self):
        cases=fixtures.cases();seed=original.SEEDS[0];match=original.IDS[-1]
        with tempfile.TemporaryDirectory() as root,patch('hybrid_training.research_open'),patch('long_training.research_open'):
            root=Path(root)
            for tag in ('first','repeat'):
                original.train_fit(cases,root/('source-'+tag),'old','graph',seed,match,nullcontext,steps=2,probe=True)
            source=root/'source-first/progress.pt'
            digest=hashlib.sha256(source.read_bytes()).hexdigest()
            old_id=original.expected_identity('old','graph',seed,match,steps=2,probe=True)
            for tag,source_tag,limit in (('first','first',None),('repeat','repeat',None),('resume','first',3)):
                longer.train_fit(cases,root/tag,'new','graph',seed,match,nullcontext,steps=4,probe=True,
                    warm_start=root/('source-'+source_tag)/'progress.pt',source_identity=old_id,stop_after=limit)
            longer.train_fit(cases,root/'resume','new','graph',seed,match,nullcontext,steps=4,probe=True,
                warm_start=source,source_identity=old_id)
            values=[torch.load(root/tag/'progress.pt',map_location='cpu',weights_only=True) for tag in ('first','repeat','resume')]
            longer.confirm_repeat(values[0],values[1]);longer.confirm_repeat(values[0],values[2])
            saved=torch.load(source,map_location='cpu',weights_only=True)
            self.assertEqual(values[0]['losses'][:2],saved['losses'])
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),digest)
            new_id=longer.expected_identity('new','graph',seed,match,steps=4,probe=True)
            adopted=longer.adopt_warm_start(saved,old_id,new_id)
            self.assertTrue(deep_equal(saved['optimizer'],adopted['optimizer']))
            self.assertTrue(deep_equal(saved['window_rng'],adopted['window_rng']))
            with self.assertRaises(RuntimeError):
                longer.adopt_warm_start(saved,old_id,dict(new_id,initialization_seed=original.SEEDS[1]))

    def test_continuation_has_no_extra_optimizer_reset(self):
        seed=original.SEEDS[0];match=original.IDS[-1]
        with tempfile.TemporaryDirectory() as root,patch('hybrid_training.research_open'),patch('long_training.research_open'),\
             patch('hybrid_training.STAGE_STEPS',2),patch('long_training.STAGE_STEPS',2):
            root=Path(root);cases=fixtures.cases()
            original.train_fit(cases,root/'source','old','graph',seed,match,nullcontext,steps=4,probe=True)
            old_id=original.expected_identity('old','graph',seed,match,steps=4,probe=True)
            longer.train_fit(cases,root/'continued','new','graph',seed,match,nullcontext,steps=6,probe=True,
                warm_start=root/'source/progress.pt',source_identity=old_id)
            saved=torch.load(root/'continued/progress.pt',map_location='cpu',weights_only=True)
            self.assertEqual(sum(saved['coverage']['stage1'].values()),16)
            self.assertEqual(sum(saved['coverage']['stage2'].values()),32)
            self.assertTrue(all(float(s['step'])==4 for s in saved['optimizer']['state'].values()))

    def test_wrong_fold_cases_rejected_before_training(self):
        with tempfile.TemporaryDirectory() as root,patch('long_training.research_open'):
            with self.assertRaises(RuntimeError):
                longer.train_fit(fixtures.cases(),root,'new','graph',original.SEEDS[0],original.IDS[0],
                    nullcontext,steps=1,probe=True)

    def test_incomplete_warm_start_rejected(self):
        seed=original.SEEDS[0];match=original.IDS[-1]
        with tempfile.TemporaryDirectory() as root,patch('hybrid_training.research_open'):
            original.train_fit(fixtures.cases(),root,'old','graph',seed,match,nullcontext,
                steps=2,probe=True,stop_after=1)
            saved=torch.load(Path(root)/'progress.pt',map_location='cpu',weights_only=True)
            old_id=original.expected_identity('old','graph',seed,match,steps=2,probe=True)
            new_id=longer.expected_identity('new','graph',seed,match,steps=4,probe=True)
            with self.assertRaises(RuntimeError):longer.adopt_warm_start(saved,old_id,new_id)

    def test_projection_reserves_final_fits(self):
        self.assertGreater(projection(.1,remaining_pairs=10),projection(.1,remaining_pairs=1))
        self.assertGreater(projection(.1,remaining_pairs=0),50000*.1)
        with self.assertRaises(RuntimeError):projection(0)


if __name__=='__main__':unittest.main()
