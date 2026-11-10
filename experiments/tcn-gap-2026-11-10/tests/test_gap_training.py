import sys,unittest
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from gap_training import train,WIDTH
from prepare_tcn_gap import mask_ball
class GapTests(unittest.TestCase):
 def test_mask_copy_seed_and_half_bounds(self):
  b=np.ones((1000,3));args=([(0,500),(500,1000)],[7,19],[11,23],.4)
  x=mask_ball(b,*args,20261206);y=mask_ball(b,*args,20261206);z=mask_ball(b,*args,20261106)
  np.testing.assert_array_equal(b,np.ones_like(b));np.testing.assert_array_equal(x,y);self.assertFalse(np.array_equal(np.isnan(x),np.isnan(z)));self.assertTrue(np.isnan(x).any());self.assertTrue(np.isfinite(x).any())
 def test_repeatable_augmented_train_and_separate_view(self):
  torch.set_num_threads(1);x=np.zeros((500,WIDTH),np.float32);aug=np.ones_like(x);y=np.resize(np.array(['H','A','D']),500);s={'x':x,'aug':aug,'y':y,'blocks':[(0,500)]}
  a,_,la=train([s],steps=2);b,_,lb=train([s],steps=2);c,_,_=train([{**s,'aug':x}],steps=2)
  self.assertEqual(la,lb);self.assertTrue(all(torch.equal(v,b.state_dict()[k]) for k,v in a.state_dict().items()));self.assertTrue(any(not torch.equal(v,c.state_dict()[k]) for k,v in a.state_dict().items()))
