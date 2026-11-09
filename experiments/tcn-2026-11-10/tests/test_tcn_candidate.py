import unittest,sys
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from tcn_candidate import TCN,WIDTH,SLOTS,transform,predict
from prepare_tcn import encode
from possession.inputs import Tracking
class TCNContracts(unittest.TestCase):
 def fixture(self):
  rng=np.random.default_rng(7);p=rng.uniform(.1,.9,(70,4,3));ball=rng.uniform(.1,.9,(70,3));p[20:25,0]=np.nan;ball[10:30]=np.nan
  core=np.zeros((70,9));core[:,5:8]=1;core[10:30,5]=0
  return Tracking(p,ball),np.array([0,0,1,1]),[(0,35),(35,70)],core
 def test_adapter_masks_and_velocity_resets(self):
  t,tm,bb,c=self.fixture();x=encode(t,tm,bb,c);self.assertEqual(x.shape,(70,WIDTH));o=x[:,:SLOTS*8].reshape(70,SLOTS,8)
  self.assertTrue(np.isfinite(x).all());self.assertEqual(o[20,0,4],0);self.assertEqual(o[20,0,2],0);self.assertEqual(o[25,0,2],0);self.assertTrue((o[35,:,2:4]==0).all());self.assertTrue((o[10:30,-1,4]==0).all())
 def test_player_permutation_equivariance_and_repeat(self):
  torch.set_num_threads(1);torch.manual_seed(7);m=TCN().eval();t,tm,bb,c=self.fixture();a=encode(t,tm,bb,c);perm=[3,1,2,0];b=encode(Tracking(t.players[:,perm],t.ball),tm[perm],bb,c)
  with torch.no_grad():
   x=m(torch.from_numpy(a[None]));y=m(torch.from_numpy(b[None]));z=m(torch.from_numpy(a[None]));torch.testing.assert_close(x,y,rtol=1e-5,atol=1e-6);self.assertTrue(torch.equal(x,z))
 def test_prediction_coverage_and_half_isolation(self):
  torch.set_num_threads(1);torch.manual_seed(1);m=TCN().eval();t,tm,bb,c=self.fixture();x=encode(t,tm,bb,c);p=predict(m,x,bb,(0,1));y=x.copy();y[35:]=0;q=predict(m,y,bb,(0,1));np.testing.assert_array_equal(p[:35],q[:35]);np.testing.assert_allclose(p.sum(1),1)
 def test_two_step_synthetic_training_repeatability(self):
  from tcn_candidate import train
  t,tm,bb,c=self.fixture();x=encode(t,tm,bb,c);x=np.tile(x,(5,1));sets=[{'x':x,'y':np.full(len(x),'H'),'blocks':[(0,len(x))]}]
  a,sc,la=train(sets,steps=2);b,ss,lb=train(sets,steps=2)
  self.assertEqual(la,lb);self.assertTrue(np.isfinite(la).all());self.assertTrue(all(torch.equal(v,b.state_dict()[k]) for k,v in a.state_dict().items()))
