"""Synthetic sampler contracts; no model imports or quality claims."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import numpy as np

class MediumContextContracts(unittest.TestCase):
    def setUp(self):
        s=importlib.util.spec_from_file_location('small_runner',Path(__file__).resolve().parents[1]/'scripts/run_tabicl_medium.py')
        self.m=importlib.util.module_from_spec(s);s.loader.exec_module(self.m)
        self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name)
        self.m.PREPARED=root;self.m.OUT=root/'out'
        self.ids=list(self.m.EXPECTED_IDS)
        for k,name in enumerate(self.ids):
            x=np.zeros((50000,9));x[:,0]=k*300000+np.arange(50000)
            y=np.full(50000,'H');y[::35]='X'
            np.savez(root/(name+'.npz'),x=x,y=y,blocks=np.array([[0,50000]]))
    def tearDown(self):self.tmp.cleanup()
    def test_reproducible_sample_excludes_heldout_and_unknown(self):
        x,y,r=self.m.context(self.ids,self.ids[0]);again,yy,rr=self.m.context(self.ids,self.ids[0])
        self.assertEqual(len(x),30000);self.assertTrue((x[:,0]>=300000).all())
        self.assertFalse((y=='X').any());self.assertTrue(np.array_equal(x,again));self.assertEqual(r,rr)
        self.assertTrue((x[:,0]%5==0).all());self.assertTrue(np.array_equal(y,yy))
    def test_evaluation_timeline_is_not_sampled(self):
        self.m.context(self.ids,self.ids[0])
        x=self.m.case_features(self.ids[0],'clean');self.assertEqual(len(x),50000)
        self.assertTrue(np.array_equal(x[:,0],np.arange(50000)))
