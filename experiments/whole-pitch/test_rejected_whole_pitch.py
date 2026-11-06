import unittest
import numpy as np
from possession.inputs import Tracking
from rejected_whole_pitch import whole_pitch
class WholePitch(unittest.TestCase):
 def test_ball_independence_reflection_team_swap_and_half_reset(self):
  rng=np.random.default_rng(7);p=rng.random((140,4,3));b=rng.random((140,3));tm=np.array([0,0,1,1]);bb=[(0,70),(70,140)]
  x=whole_pitch(Tracking(p,b),tm,bb,[100,60]);self.assertTrue(np.allclose(x,whole_pitch(Tracking(p,np.full_like(b,np.nan)),tm,bb,[100,60]),equal_nan=True))
  q=p.copy();q[...,:2]=1-q[...,:2];self.assertTrue(np.allclose(x,whole_pitch(Tracking(q,b),tm,bb,[100,60]),equal_nan=True))
  swapped=whole_pitch(Tracking(p,b),1-tm,bb,[100,60]);self.assertTrue(np.allclose(x[:,[0,1,3,2,4]],swapped,equal_nan=True));self.assertTrue(np.isnan(x[70,:2]).all())
 def test_window_expiry_and_no_player_observations(self):
  p=np.full((70,4,3),np.nan);p[0,:,:2]=[[0,0],[0,.2],[1,0],[1,.2]];x=whole_pitch(Tracking(p,np.zeros((70,3))),np.array([0,0,1,1]),[(0,70)],[100,60]);self.assertEqual(x[62,4],100);self.assertTrue(np.isnan(x[63:]).all())
