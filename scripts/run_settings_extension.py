import sys,json,hashlib,itertools,subprocess
from pathlib import Path
import numpy as np
from catboost import CatBoostClassifier
from possession.decode import decode
from possession.core import promote
from review_frozen import score,blocks_valid,pm
from run_core import PARAMS
R=Path('experiments/extension-2026-11-07/settings');M=Path('models/extension-settings');M.mkdir(exist_ok=True);DATA=Path('data/external/prepared');P=Path('data/diagnostics-review');CONFIGS=[(4,.05,300,3),(6,.03,300,6),(6,.08,200,3),(8,.05,200,6)]
def main():
 ids=json.loads(Path('experiments/core-development/split.json').read_text())['development'];sets={m:np.load(DATA/(m+'.npz')) for m in ids};xs={};ys={};vbs={};xc={}
 for m,d in sets.items():
  ix=np.arange(0,len(d['y']),5);ix=ix[d['y'][ix]!='X'];xs[m]=d['x'][ix];ys[m]=d['y'][ix];vbs[m]=blocks_valid(d['y'],d['blocks']);xc[m]=np.load(P/(m+'-targetlike.npz'))['x']
 inner=[];outer=[];chosen={}
 for held in ids:
  train=[m for m in ids if m!=held];scores=[]
  for c,(depth,rate,it,l2) in enumerate(CONFIGS):
   vals=[]
   for valid in train:
    fit=sorted(set(train)-{valid});key='-'.join(fit)+'-c'+str(c);model=CatBoostClassifier(**dict(PARAMS,depth=depth,learning_rate=rate,iterations=it,l2_leaf_reg=l2,thread_count=1));path=M/(key+'.cbm')
    if path.exists():model.load_model(str(path))
    else:model.fit(np.concatenate([xs[m] for m in fit]),np.concatenate([ys[m] for m in fit]));model.save_model(str(path))
    order=[list(model.classes_).index(z) for z in ['H','A','D']];prob=model.predict_proba(xc[valid],thread_count=1)[:,order];pred=decode(prob,(1-np.eye(3))*16,vbs[valid]);g=pm.label_codes(sets[valid]['y']);q=pm.label_codes(pred)
    for _,end in sorted(sets[valid]['blocks'][:-1],reverse=True):g=np.insert(g,int(end),pm.X);q=np.insert(q,int(end),pm.X)
    s=pm.spell_scores(g,q,pm.valid_runs(g))['mean_f1'];vals.append(s);inner.append({'outer':held,'inner_valid':valid,'fit':fit,'config_index':c,'corrupted_spellF1':s})
    (R/'inner-results.json').write_text(json.dumps(inner,indent=2))
   scores.append(float(np.mean(vals)));print('Inner',held,c,flush=True)
  best=int(np.argmax(scores));chosen[held]={'index':best,'configuration':CONFIGS[best],'inner_means':scores};depth,rate,it,l2=CONFIGS[best];model=CatBoostClassifier(**dict(PARAMS,depth=depth,learning_rate=rate,iterations=it,l2_leaf_reg=l2,thread_count=1));model.fit(np.concatenate([xs[m] for m in train]),np.concatenate([ys[m] for m in train]));model.save_model(str(M/(held+'-outer.cbm')));order=[list(model.classes_).index(z) for z in ['H','A','D']]
  for condition,x in [('clean',sets[held]['x']),('targetlike',xc[held])]:
   prob=model.predict_proba(x,thread_count=1)[:,order];pred=decode(prob,(1-np.eye(3))*16,vbs[held]);outer.append({'match':held,'condition':condition,**score(sets[held]['y'],pred,sets[held]['blocks'].tolist())})
  (R/'outer-results.json').write_text(json.dumps(outer,indent=2));(R/'chosen.json').write_text(json.dumps(chosen,indent=2));print('Outer completed',held,flush=True)
 parent=[r for r in json.loads(Path('experiments/gap-augmentation/decoder-isolation.json').read_text()) if r['method']=='penalty16'];pair=lambda rr:{m:tuple(np.mean([[r['spellF1'],r['macroF1']] for r in rr if r['match']==m],axis=0)) for m in ids};a=pair(outer);b=pair(parent);ds={m:a[m][0]-b[m][0] for m in ids};dm={m:a[m][1]-b[m][1] for m in ids};co={m:next(r['spellF1'] for r in outer if r['match']==m and r['condition']=='targetlike')-next(r['spellF1'] for r in parent if r['match']==m and r['condition']=='targetlike') for m in ids};test=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-q'],capture_output=True,text=True);(R/'tests.txt').write_text(test.stdout+test.stderr);base=promote(b,a,test.returncode==0);delta=float(np.median(list(co.values())));gate={'promoted':base and delta>=.01,'existing_gate':base,'median_primary_delta':delta,'paired_spell_deltas':ds,'paired_macro_deltas':dm,'primary_deltas':co,'matches_improved':int(sum(v>0 for v in ds.values())),'tests_passed':test.returncode==0,'logical_inner_fits':80,'unique_inner_fits':len(list(M.glob('*-c*.cbm'))),'outer_fits':5,'outer_corrupted_spell_std':float(np.std([r['spellF1'] for r in outer if r['condition']=='targetlike'],ddof=1))};(R/'gate.json').write_text(json.dumps(gate,indent=2));print(json.dumps(gate))
if __name__=='__main__':main()
