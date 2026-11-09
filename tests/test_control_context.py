import importlib.util,unittest
from pathlib import Path
import numpy as np
s=importlib.util.spec_from_file_location('control',Path(__file__).resolve().parents[1]/'scripts/run_control_context.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ControlContract(unittest.TestCase):
 def test_missing_support_and_half_isolation(self):
  x=np.full((60,9),np.nan);x[0,:2]=[1,4];x[30:,:2]=[4,1]
  z=m.temporal(x,[(0,30),(30,60)])
  self.assertTrue(np.isnan(z[0,9]));self.assertEqual(z[1,9],1);self.assertTrue(np.isnan(z[29,9]));self.assertEqual(z[30,9],-1);self.assertEqual(z[29,10],0)
 def test_team_swap_and_no_current_row(self):
  x=np.zeros((70,9));x[:,:2]=[1,2];y=x.copy();y[:,:2]=y[:,[1,0]]
  a=m.temporal(x,[(0,70)]);b=m.temporal(y,[(0,70)])
  np.testing.assert_allclose(a[:,9],-b[:,9]);np.testing.assert_array_equal(a[:,10],b[:,10]);x[35,:2]=[100,1]
  self.assertEqual(m.temporal(x,[(0,70)])[35,9],a[35,9])
