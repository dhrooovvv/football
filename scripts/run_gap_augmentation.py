"""Approved isolated gap training; prerequisites complete before fitting."""
import json,sys
from pathlib import Path
import numpy as np
from catboost import CatBoostClassifier
from possession.core import features,corrupt,promote
from possession.inputs import Tracking
from possession.external import load_match
from possession.decode import decode
from run_core import PARAMS
from review_frozen import score,blocks_valid,smooth,pm
R=Path('experiments/gap-augmentation');P=Path('data/diagnostics-review');C=Path('data/external/prepared');IDS=json.loads(Path('experiments/core-development/split.json').read_text())['development']
def save(name,x):(R/name).write_text(json.dumps(x,indent=2))
def summaries(y,blocks):
 g=pm.label_codes(y);ss=[]
 for a,b in blocks:ss+=pm.possession_spells(g,pm.valid_runs(np.where(np.arange(len(g))>=a,np.where(np.arange(len(g))<b,g,pm.X),pm.X)))
 valid=y!='X';return {'dead_share':float((y[valid]=='D').mean()),'mean_possession_spell_seconds':float(np.mean([b-a for a,b,_ in ss])/25),'possession_spells':len(ss),'graded_frames':int(valid.sum())}
def main():
 target=json.loads((P/'target-shift.json').read_text());gap=target['missing_runs'];seen=target['observed_runs'];sets={m:np.load(C/(m+'.npz')) for m in IDS};fid=[];conventions=[];decoder=[]
 old=json.loads(Path('experiments/core-development/penalty8/results.json').read_text());prev=json.loads(Path('experiments/diagnostics-review/results.json').read_text())
 for m,d in sets.items():
  y=d['y'];v=y!='X';xc=np.load(P/(m+'-targetlike.npz'))['x'];bb=d['blocks'].tolist();vb=blocks_valid(y,bb)
  fid.append({'match':m,'target_observed_missing_fraction':target['missing_fraction'],'clean_missing_fraction':float((d['x'][v,5]==0).mean()),'original_corrupted_missing_fraction':float((d['xc'][v,5]==0).mean()),'targetlike_missing_fraction':float((xc[v,5]==0).mean()),'original_corrupted':next({'spellF1':r['spell_f1_mean'],'macroF1':r['macro_f1']} for r in old if r['match']==m and r['condition']=='corrupted'),'targetlike':next({'spellF1':r['spellF1'],'macroF1':r['macroF1']} for r in prev if r['match']==m and r['condition']=='targetlike' and r['method']=='catboost_penalty8')})
  conventions.append({'match':m,**summaries(y,bb)})
  for condition in ['clean','targetlike']:
   probs=np.load(P/(m+'-'+condition+'-probs.npz'))['p'];raw=np.array(['H','A','D'])[probs.argmax(axis=1)]
   for method in ['argmax','smooth50','penalty8','penalty16']:
    if method.startswith('penalty'):pred=decode(probs,(1-np.eye(3))*int(method[7:]),vb)
    else:
     pred=np.full(len(y),'X')
     for a,b in vb:
      pred[a:b]=raw[a:b] if method=='argmax' else smooth(np.where(raw[a:b]=='H',0,np.where(raw[a:b]=='A',1,-1)),50)
    decoder.append({'match':m,'condition':condition,'method':method,**score(y,pred,bb)})
  print('Prerequisites evaluated',m,flush=True)
 # Public labels: summary only, never scores or target-model selection.
 public=pm.read_label_csv('reference/more-than-a-hack-2027-main/evaluation/gt/BAR-ATH_possession_gt_public.csv').label.to_numpy();pub=summaries(public,[(0,len(public))])
 save('fidelity.json',fid);save('label-conventions.json',{'external':conventions,'public_window_semantics_only':pub});save('decoder-isolation.json',decoder)
 print('All prerequisite diagnostics complete; training begins.',flush=True)
 trainsets={}
 for i,m in enumerate(IDS):
  path=P/(m+'-training-targetlike.npz')
  if path.exists():xx=np.load(path)['x']
  else:
   t,tm,bb,pp,y=load_match(next(Path('data/external').glob('*matchinformation*'+m+'.xml')),next(Path('data/external').glob('*positions*'+m+'.xml')))
   rng=np.random.default_rng(20271106+i);c=corrupt(t,bb,20271106+i);ball=t.ball.copy()
   for a,b in bb:
    pos=a;missing=bool(rng.random()<target['missing_fraction'])
    while pos<b:
     n=int(rng.choice(gap if missing else seen));end=min(b,pos+n)
     if missing:ball[pos:end]=np.nan
     pos=end;missing=not missing
   xx,names=features(Tracking(c.players,ball),tm,bb,pp);np.savez_compressed(path,x=xx)
  d=sets[m];idx=np.arange(0,len(d['y']),5);idx=idx[d['y'][idx]!='X'];x=d['x'][idx].copy();rng=np.random.default_rng(20281106+i);replace=rng.choice(len(idx),len(idx)//2,replace=False);x[replace]=xx[idx[replace]];trainsets[m]=(x,d['y'][idx])
 rows=[];folder=Path('models/gap-augmentation');folder.mkdir(exist_ok=True)
 for m,d in sets.items():
  model=CatBoostClassifier(**PARAMS);model.fit(np.concatenate([xy[0] for k,xy in trainsets.items() if k!=m]),np.concatenate([xy[1] for k,xy in trainsets.items() if k!=m]));model.save_model(str(folder/(m+'.cbm')));order=[list(model.classes_).index(c) for c in ['H','A','D']];vb=blocks_valid(d['y'],d['blocks'])
  for condition,x in [('clean',d['x']),('targetlike',np.load(P/(m+'-targetlike.npz'))['x'])]:
   prob=model.predict_proba(x)[:,order];pred=decode(prob,(1-np.eye(3))*8,vb);rows.append({'match':m,'condition':condition,'method':'augmentation_penalty8',**score(d['y'],pred,d['blocks'].tolist())})
  save('augmentation-results.json',rows);print('Augmentation fold complete',m,flush=True)
if __name__=='__main__':main()
