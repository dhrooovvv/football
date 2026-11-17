"""Synthetic audit probes; no match assets or ground-truth tuning."""
import json, sys, tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1] / 'reference/more-than-a-hack-2027-main'
sys.path[:0] = [str(ROOT),str(ROOT/'evaluation')]
from starter import baseline, load_atd, load_homography
import possession_metrics as pm
out = {}
with tempfile.TemporaryDirectory() as td:
 p=Path(td)
 raw=p/'atd.txt';raw.write_text('1::\n2::\n2::\n4::\n')
 with patch.object(load_atd,'require',return_value=[str(raw)]), patch.object(load_atd,'source_frames',return_value=4):
  out['duplicate_ids_1_2_2_4_accepted']=load_atd.check_alignment_raw()['agrees']
 out['smoothing_single_home_among_missing']=baseline.smooth(np.array([-1,-1,0,-1,-1]),2).tolist()
 raw.write_text('1:0.1,NaN,0;0.5,0.5,0:0.5,0.5,0\n')
 out['partial_nan_first_player_overrides_valid_away']=baseline.nearest_player_labels(str(raw),np.array([0,1]),1,(105.3,68)).tolist()
 raw.write_text('0:0.1,0.1,0:0.1,0.1,0\n')
 out['frame_zero_writes_last_output']=baseline.nearest_player_labels(str(raw),np.array([0]),3,(105.3,68)).tolist()
 cols={'frame':[1,0],**{f'h{i}{j}':[float(i==j)]*2 for i in range(3) for j in range(3)},'reprojection_error':[0.,0.],'valid':[1,1]}
 hp=p/'hom.csv';pd.DataFrame(cols).to_csv(hp,index=False)
 with patch.object(load_homography,'require',return_value=[str(hp)]):
  out['reordered_homography_loads_without_error']=load_homography.load()[0].shape== (2,3,3)
 out['extra_csv_column_accepted']=pm.validate_submission(pd.DataFrame({'frame':[0,1],'label':['H','D'],'extra':[1,2]}),2) is None
 out['constant_home_synthetic_spellF1']=pm.evaluate(np.array([0]*8+[1]*2,dtype=np.int8),np.zeros(10,dtype=np.int8))['spell_f1_mean']
 out['abstention_fill']=pm.fill_abstentions(np.array([3,0,3,1,3],dtype=np.int8),[(0,5)]).tolist()
 out['all_abstain_retained']=pm.fill_abstentions(np.array([3,3],dtype=np.int8),[(0,2)]).tolist()
 print(json.dumps(out,indent=2))
 Path(__file__).with_name('probe-results.json').write_text(json.dumps(out,indent=2)+'\n')
