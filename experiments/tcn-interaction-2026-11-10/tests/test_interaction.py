import sys,unittest
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interaction_model import TCN,relations,SLOTS,CHANNELS,ParentTCN
from interaction_training import train,WIDTH
class InteractionTests(unittest.TestCase):
 def test_mask_translation_and_relative_identity(self):
  o=torch.zeros(1,10,SLOTS,CHANNELS);o[:,:,0,4]=1;o[:,:,-1,4]=1;o[:,:,0,:2]=.4;o[:,:,-1,:2]=.1
  a=relations(o);torch.testing.assert_close(a[:,:,0,:2],torch.full((1,10,2),.3));self.assertTrue((a[:,:,-1]==0).all());z=o.clone();z[:,:,:,:2]+=.2;torch.testing.assert_close(a,relations(z));o[:,:,-1,4]=0;self.assertTrue((relations(o)==0).all())
 def test_permutation_repeat_and_size(self):
  torch.set_num_threads(1);torch.manual_seed(7);x=torch.randn(1,40,WIDTH);o=x[:,:,:SLOTS*CHANNELS].reshape(1,40,SLOTS,CHANNELS);o[:,:,:,4]=1;perm=list(range(SLOTS-1));perm.reverse();perm.append(SLOTS-1);y=x.clone();y[:,:,:SLOTS*CHANNELS]=o[:,:,perm].reshape(1,40,-1);m=TCN().eval()
  with torch.no_grad():a=m(x);b=m(y);c=m(x)
  torch.testing.assert_close(a,b,rtol=1e-5,atol=1e-6);self.assertTrue(torch.equal(a,c));self.assertEqual(sum(p.numel() for p in m.parameters())-sum(p.numel() for p in ParentTCN().parameters()),72)
 def test_training_two_steps_exact(self):
  torch.set_num_threads(1);x=np.zeros((500,WIDTH),np.float32);y=np.resize(np.array(['H','A','D']),500);s={'x':x,'aug':x,'y':y,'blocks':[(0,500)]};a,_,la=train([s],steps=2);b,_,lb=train([s],steps=2);self.assertEqual(la,lb);self.assertTrue(all(torch.equal(v,b.state_dict()[k]) for k,v in a.state_dict().items()))
 def test_inference_half_isolation(self):
  from interaction_training import predict
  torch.set_num_threads(1);torch.manual_seed(5);m=TCN().eval();x=np.zeros((80,WIDTH),np.float32);y=x.copy();y[40:]=1;a=predict(m,x,[(0,40),(40,80)],(0,1));b=predict(m,y,[(0,40),(40,80)],(0,1));np.testing.assert_array_equal(a[:40],b[:40]);np.testing.assert_allclose(a.sum(1),1)
