import unittest,numpy as np,torch
from gru_candidate import GRU,fit_scaler,transform,windows,predict,blend
class GRUContracts(unittest.TestCase):
 def test_fold_only_preprocessing_and_unknown_runs(self):
  s={'x':np.ones((600,9)),'y':np.array(['H']*250+['X']*100+['A']*250),'blocks':[(0,300),(300,600)]};scaler=fit_scaler([s]);self.assertTrue(np.isfinite(transform(np.full((2,9),np.nan),scaler)).all());self.assertEqual(windows([s]),[(0,0,1),(0,350,1)])
 def test_exact_coverage_half_isolation_and_blend_normalization(self):
  torch.manual_seed(3);m=GRU().eval();rng=np.random.default_rng(3);x=rng.normal(size=(407,9));bb=[(0,203),(203,407)];sc=(np.zeros(9),np.ones(9));p=predict(m,x,bb,sc);q=x.copy();q[203:]+=10;pp=predict(m,q,bb,sc);np.testing.assert_array_equal(p[:203],pp[:203]);out=blend(np.full_like(p,1/3),p);np.testing.assert_allclose(out.sum(axis=1),1,rtol=0,atol=1e-15)
