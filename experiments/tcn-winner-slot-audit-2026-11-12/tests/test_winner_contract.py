"""Synthetic metadata checks only; user executes, no real assets needed."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from winner_contract import expected_identity, validate_control, IDS, ARCHITECTURE


class WinnerContract(unittest.TestCase):
    def fixture(self):
        match=IDS[0];signature='synthetic';membership={'pff_training':['synthetic-unused']}
        identity=expected_identity(match,signature,membership['pff_training'])
        coverage={stage:{key:40000 for key in identity['supervised_matches']}
                  for stage in ('stage1','stage2')}
        views={stage:{'clean':80000,'gap':80000} for stage in ('stage1','stage2')}
        saved=dict(identity=identity,step=40000,stage='stage2',losses=[1.]*40000,
                   target_counts={'stage1':0,'stage2':0},coverage=coverage,supervised_views=views)
        record=dict(registration=signature,arm='control',architecture=ARCHITECTURE,parent='rotation20k',
                    training_steps=40000,stage_steps=20000,training_matches=identity['supervised_matches'],
                    geometry_matches=[],repeated_training_exact=True,target_counts=saved['target_counts'],
                    coverage=coverage,supervised_views=views,
                    training_loss_sha256=hashlib.sha256(json.dumps(saved['losses']).encode()).hexdigest())
        return saved,match,signature,membership,record

    def test_complete_registered_control_accepted(self):
        validate_control(*self.fixture())

    def test_rejects_wrong_arm_fold_geometry_and_recipe(self):
        for field,value in [('arm','pretrain'),('held_out',IDS[1]),('geometry_matches',['pff-bad']),
                            ('total_steps',20000),('stage_steps',10000),('seed',9),('view_seed',9),
                            ('stage_boundary','continuous'),('architecture','other'),('schema','other')]:
            args=list(self.fixture());args[0]=copy.deepcopy(args[0]);args[0]['identity'][field]=value
            with self.subTest(field=field),self.assertRaises(RuntimeError):validate_control(*args)
        with self.assertRaises(RuntimeError):expected_identity('J03WQQ','x',[])

    def test_rejects_five_member_fit_and_incomplete_checkpoint(self):
        args=list(self.fixture());args[0]['identity']['supervised_matches']=['idsse-'+m for m in IDS]
        with self.assertRaises(RuntimeError):validate_control(*args)
        for field,value in [('step',20000),('stage','stage1')]:
            args=list(self.fixture());args[0][field]=value
            with self.assertRaises(RuntimeError):validate_control(*args)

    def test_rejects_archive_loss_or_sampling_mismatch(self):
        args=list(self.fixture());args[0]['losses'][0]=2.
        with self.assertRaises(RuntimeError):validate_control(*args)
        args=list(self.fixture());args[0]['coverage']=copy.deepcopy(args[0]['coverage'])
        args[0]['coverage']['stage2']['idsse-'+IDS[1]]-=1
        with self.assertRaises(RuntimeError):validate_control(*args)
        args=list(self.fixture());args[4]['repeated_training_exact']=False
        with self.assertRaises(RuntimeError):validate_control(*args)


if __name__=='__main__':unittest.main()
