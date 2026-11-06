import unittest,tempfile
from pathlib import Path
import numpy as np
from possession.core import features,corrupt,promote
from possession.inputs import Tracking
from possession.external import load_match
class CoreContracts(unittest.TestCase):
 def test_features_and_masks(self):
  t=Tracking(np.tile([[0.,0.,0.],[1.,0.,0.]],(3,1,1)),np.array([[.25,0,0],[.5,0,0],[np.nan,np.nan,np.nan]]))
  x,n=features(t,[0,1],[(0,3)],(100,60))
  self.assertEqual(x[0,n.index('distance_margin')],50)
  self.assertEqual(x[1,n.index('ball_speed')],625)
  self.assertTrue(np.isnan(x[2,n.index('edge_distance')]))
  self.assertEqual(x[2,n.index('ball_observed')],0)
  a=corrupt(t,[(0,3)],7);b=corrupt(t,[(0,3)],7)
  np.testing.assert_equal(a.ball,b.ball)
 def test_gate(self):
  before={str(i):(.5,.7) for i in range(5)}
  self.assertTrue(promote(before,{str(i):(.51,.69) for i in range(5)},True))
  self.assertFalse(promote(before,before,True))
  self.assertFalse(promote(before,{str(i):(.6,.68) for i in range(5)},True))
  self.assertFalse(promote(before,{str(i):(.6,.7) for i in range(5)},False))
 def test_external_mapping_and_gaps(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'m.xml').write_text('<root><General HomeTeamId="h" GuestTeamId="a"/><Environment PitchX="100" PitchY="60"/></root>')
   sets=[]
   for half in ['firstHalf','secondHalf']:
    for team in ['h','a','BALL']:
     frames=''.join(f'<Frame N="{i}" T="2023-01-01T00:00:00.{i*40:03d}+00:00" X="0" Y="0" BallStatus="{int(i!=2)}" BallPossession="{i+1}"/>' for i in range(3))
     sets.append(f'<FrameSet GameSection="{half}" TeamId="{team}" PersonId="{team}">{frames}</FrameSet>')
   (p/'p.xml').write_text('<root>'+''.join(sets)+'</root>')
   t,teams,blocks,pitch,y=load_match(p/'m.xml',p/'p.xml')
   self.assertEqual(y.tolist(),list('HADHAD'));self.assertEqual(blocks,[(0,3),(3,6)])
   np.testing.assert_equal(t.ball[:,:2],.5)

class ModelSmoke(unittest.TestCase):
 def test_probability_order_serialization_and_export(self):
  from catboost import CatBoostClassifier
  from possession.decode import decode
  from possession.inputs import export_labels
  x=np.array([[0.],[1.],[2.],[np.nan]]*12);y=np.array(['H','A','D','D']*12)
  model=CatBoostClassifier(iterations=8,depth=2,random_seed=20261106,thread_count=1,verbose=False,allow_writing_files=False,loss_function='MultiClass');model.fit(x,y)
  with tempfile.TemporaryDirectory() as d:
   path=Path(d);model.save_model(path/'m.cbm');other=CatBoostClassifier();other.load_model(path/'m.cbm')
   a=model.predict_proba(x);b=other.predict_proba(x);np.testing.assert_array_equal(a,b)
   p=a[:,[list(model.classes_).index(c) for c in ['H','A','D']]]
   labels=decode(p,np.ones((3,3))-np.eye(3));export_labels(path/'out.csv',labels,len(x))
   self.assertEqual(len((path/'out.csv').read_text().splitlines()),len(x)+1)

class SpeedContract(unittest.TestCase):
 def test_mean_speed_excludes_missing_and_resets(self):
  from possession.core import mean_player_speed
  p=np.array([[[0,0,0],[np.nan,0,0]],[[.01,0,0],[.9,0,0]],[[.9,0,0],[.9,0,0]]])
  t=Tracking(p,np.full((3,3),np.nan));s=mean_player_speed(t,[(0,2),(2,3)],(100,60))
  self.assertTrue(np.isnan(s[0]));self.assertAlmostEqual(s[1],25);self.assertTrue(np.isnan(s[2]))
