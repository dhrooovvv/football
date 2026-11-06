import json,sys,subprocess
from pathlib import Path
import numpy as np
from catboost import CatBoostClassifier
sys.path.insert(0,str(Path('experiments/whole-pitch').resolve()))
from rejected_whole_pitch import whole_pitch,NAMES
from possession.external import load_match
from possession.core import corrupt,promote
from possession.decode import decode
from run_core import PARAMS
from review_frozen import score,blocks_valid
R=Path('experiments/whole-pitch');CACHE=Path('data/external/prepared');PRIVATE=Path('data/diagnostics-review');M=Path('models/whole-pitch');M.mkdir(exist_ok=True)
def missing_quality(y,p,x):
 mask=(y!='X')&(x[:,5]==0);g=y[mask]=='D';q=p[mask]=='D';tp=int((g&q).sum());fp=int((~g&q).sum());fn=int((g&~q).sum());tn=int((~g&~q).sum());f=lambda a,b: a/b if b else None
 return {'frames':int(mask.sum()),'wrong_frames':fp+fn,'D_precision':f(tp,tp+fp),'D_recall':f(tp,tp+fn),'D_f1':f(2*tp,2*tp+fp+fn),'binary_macroF1':np.mean([v for v in [f(2*tp,2*tp+fp+fn),f(2*tn,2*tn+fp+fn)] if v is not None]) if len(g) else None}
def main():
 ids=json.loads(Path('experiments/core-development/split.json').read_text())['development'];sets={}
 for i,m in enumerate(ids):
  d=np.load(CACHE/(m+'.npz'));t,tm,bb,pp,y=load_match(next(Path('data/external').glob('*matchinformation*'+m+'.xml')),next(Path('data/external').glob('*positions*'+m+'.xml')));c=corrupt(t,bb,20261106+i)
  ext=whole_pitch(t,tm,bb,pp);extc=whole_pitch(c,tm,bb,pp);np.savez_compressed(CACHE/(m+'-whole-pitch.npz'),x=ext,xc=extc)
  corec=np.load(PRIVATE/(m+'-targetlike.npz'))['x'];sets[m]={'x':np.column_stack([d['x'],ext]),'xc':np.column_stack([corec,extc]),'y':y,'blocks':bb};print('Prepared',m,flush=True)
 rows=[];parentrows=[]
 for m,d in sets.items():
  xs=[];ys=[]
  for k,s in sets.items():
   if k==m:continue
   ix=np.arange(0,len(s['y']),5);ix=ix[s['y'][ix]!='X'];xs.append(s['x'][ix]);ys.append(s['y'][ix])
  model=CatBoostClassifier(**PARAMS);model.fit(np.concatenate(xs),np.concatenate(ys));model.save_model(str(M/(m+'.cbm')));order=[list(model.classes_).index(c) for c in ['H','A','D']];vb=blocks_valid(d['y'],d['blocks'])
  for condition,key in [('clean','x'),('targetlike','xc')]:
   prob=model.predict_proba(d[key])[:,order];pred=decode(prob,(1-np.eye(3))*16,vb);rows.append({'match':m,'condition':condition,**score(d['y'],pred,d['blocks']),'missing_ball_dead_live':missing_quality(d['y'],pred,d[key])})
   prob=np.load(PRIVATE/(m+'-'+condition+'-probs.npz'))['p'];parent=decode(prob,(1-np.eye(3))*16,vb);parentrows.append({'match':m,'condition':condition,**score(d['y'],parent,d['blocks']),'missing_ball_dead_live':missing_quality(d['y'],parent,d[key])})
  (R/'results.json').write_text(json.dumps(rows,indent=2));(R/'parent-results.json').write_text(json.dumps(parentrows,indent=2));print('Fold completed',m,flush=True)
 tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],capture_output=True,text=True);(R/'tests.txt').write_text(tests.stdout+tests.stderr)
 pair=lambda rr:{m:tuple(np.mean([[r['spellF1'],r['macroF1']] for r in rr if r['match']==m],axis=0)) for m in ids};b=pair(parentrows);a=pair(rows);ds={m:a[m][0]-b[m][0] for m in ids};dm={m:a[m][1]-b[m][1] for m in ids};cor={m:next(r['spellF1'] for r in rows if r['match']==m and r['condition']=='targetlike')-next(r['spellF1'] for r in parentrows if r['match']==m and r['condition']=='targetlike') for m in ids};base=promote(b,a,tests.returncode==0);minimum=float(np.median(list(cor.values())));gate={'promoted':base and minimum>=.01,'existing_gate_pass':base,'minimum_primary_gate_pass':minimum>=.01,'median_corrupted_spell_delta':minimum,'paired_spell_deltas':ds,'paired_macro_deltas':dm,'median_paired_spell_delta':float(np.median(list(ds.values()))),'median_paired_macro_delta':float(np.median(list(dm.values()))),'matches_improved':int(sum(v>0 for v in ds.values())),'primary_corrupted_deltas':cor,'tests_passed':tests.returncode==0};(R/'gate.json').write_text(json.dumps(gate,indent=2));print(json.dumps(gate),flush=True)
if __name__=='__main__':main()
