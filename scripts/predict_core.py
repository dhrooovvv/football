"""Train on development matches only; generate deterministic target CSV locally."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from catboost import CatBoostClassifier
from possession.inputs import load_atd,load_teams,export_labels
from possession.core import features
from possession.decode import decode
from run_core import PARAMS,CACHE,ROOT

def main():
 p=argparse.ArgumentParser();p.add_argument('--selection',type=Path,default=ROOT/'selection.json');p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--outdir',type=Path,default=Path('data/competition/predictions'));p.add_argument('--model-path',type=Path,default=Path('models/core-final.cbm'));a=p.parse_args()
 selection=json.loads(a.selection.read_text());penalty=selection['penalty']
 if selection['mean_player_speed']: raise ValueError('Rejected feature cannot enter production')
 ids=json.loads((ROOT/'split.json').read_text())['development'];xs=[];ys=[]
 for m in ids:
  d=np.load(a.cache/(m+'.npz'));idx=np.arange(0,len(d['y']),5);idx=idx[d['y'][idx]!='X'];x=d['x']
  xs.append(x[idx]);ys.append(d['y'][idx])
 model=CatBoostClassifier(**PARAMS);model.fit(np.concatenate(xs),np.concatenate(ys))
 a.model_path.parent.mkdir(parents=True,exist_ok=True);model.save_model(str(a.model_path))
 cfg=json.loads(Path('configs/competition.json').read_text());root=Path('data/competition');base=root/'tactical/BAR-ATH_tactical'
 team=load_teams(str(base)+'_atd.xml',46,cfg['home_team'],cfg['away_team']);track=load_atd(str(base)+'_atd.txt',199319,46)
 x,names=features(track,team,cfg['tactical_half_open_blocks'],cfg['pitch_metres'])
 probs=model.predict_proba(x,thread_count=1)[:,[list(model.classes_).index(c) for c in ['H','A','D']]]
 pred=decode(probs,(np.ones((3,3))-np.eye(3))*penalty,cfg['tactical_half_open_blocks'])
 out=a.outdir;out.mkdir(parents=True,exist_ok=True)
 export_labels(out/'candidate.csv',pred,199319)
 reloaded=CatBoostClassifier();reloaded.load_model(str(a.model_path))
 again=reloaded.predict_proba(x,thread_count=1)[:,[list(reloaded.classes_).index(c) for c in ['H','A','D']]]
 repeat=decode(again,(np.ones((3,3))-np.eye(3))*penalty,cfg['tactical_half_open_blocks'])
 export_labels(out/'candidate-repeat.csv',repeat,199319)
 assert (out/'candidate.csv').read_bytes()==(out/'candidate-repeat.csv').read_bytes()
 (out/'provenance.json').write_text(json.dumps({'training_matches':ids,'features':names,'parameters':PARAMS,'penalty':penalty,'sha256':hashlib.sha256((out/'candidate.csv').read_bytes()).hexdigest()},indent=2))
 print('Local target CSV generated; identical export bytes verified.')
if __name__=='__main__':main()
