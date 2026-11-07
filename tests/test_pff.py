import unittest,numpy as np
from possession.pff import consensus,event_state,resample
class PFFContracts(unittest.TestCase):
 def test_observation_consensus(self):
  np.testing.assert_array_equal(consensus([[1,2],[1,2]]),[1,2]);self.assertTrue(np.isnan(consensus([[1,2],[1,3]])).all());self.assertTrue(np.isnan(consensus([[1,2],None])).all())
 def test_event_duplicates_conflicts_and_clock(self):
  a={'game_event_type':'OTB','home_ball':True};self.assertEqual(event_state([a,a])[2],'H');self.assertEqual(event_state([a,dict(a,home_ball=False)])[2],'X');self.assertEqual(event_state([{'game_event_type':'CLK'}],'live','A')[2],'X');self.assertEqual(event_state([{'game_event_type':'VID'}],'live','A')[2],'X');self.assertEqual(event_state([a,{'game_event_type':'OUT'}])[2],'X')
 def test_missing_gap_no_interpolation_or_future_label(self):
  times=np.array([0,.0333667,.20]);p=np.ones((3,2,3));b=np.ones((3,3));x,z,y,g=resample(times,p,b,['H','A','D'],29.97);self.assertEqual(y[0],'H');self.assertTrue(np.isnan(x[2:5]).all());self.assertTrue((y[2:5]=='X').all());self.assertEqual(y[-1],'D')
 def test_unknown_clears_stale_owner_and_repeat_resampling(self):
  state,owner,label=event_state([{'game_event_type':'VID'}],'live','H');self.assertIsNone(owner);self.assertEqual(event_state([{'game_event_type':'G'}],state,owner)[2],'X')
  args=([0,.04],np.ones((2,2,3)),np.ones((2,3)),['H','A'],25)
  for a,b in zip(resample(*args),resample(*args)):np.testing.assert_array_equal(a,b)
 def test_clock_contract(self):
  with self.assertRaises(ValueError):resample([0,0],np.ones((2,2,3)),np.ones((2,3)),['H','A'],29.97)

class RawPFFContract(unittest.TestCase):
 def test_loader_never_uses_smoothed_or_estimated_ball(self):
  import tempfile,json,bz2
  from pathlib import Path
  from possession.pff import load_pff
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   for name in ['Metadata','Rosters','Tracking Data']:(root/name).mkdir()
   meta={'id':1,'fps':25,'stadium':{'pitches':[{'length':100,'width':60}]},'homeTeam':{'id':1},'awayTeam':{'id':2}}
   (root/'Metadata/1.json').write_text(json.dumps([meta]));(root/'Rosters/1.json').write_text(json.dumps([{'team':{'id':1},'shirtNumber':1},{'team':{'id':2},'shirtNumber':2}]))
   rows=[]
   for period in [1,2]:
    for frame in [0,1]:
     rows.append({'period':period,'frameNum':frame,'videoTimeMs':period*4000+frame*40,'homePlayers':[{'jerseyNum':1,'visibility':'VISIBLE','x':0,'y':0}],'awayPlayers':[{'jerseyNum':2,'visibility':'VISIBLE','x':10,'y':0}],'balls':[{'visibility':'VISIBLE' if frame==0 else 'ESTIMATED','x':0,'y':0}],'ballsSmoothed':{'x':99,'y':99},'game_event':{'game_event_type':'OTB','home_ball':True}})
   with bz2.open(root/'Tracking Data/1.jsonl.bz2','wt') as f:
    for r in rows:f.write(json.dumps(r)+'\n')
   t,_,_,_,y,_=load_pff(root,'1');self.assertEqual(t.ball[0,0],.5);self.assertTrue(np.isnan(t.ball[1,:2]).all());self.assertTrue((y=='H').all())
