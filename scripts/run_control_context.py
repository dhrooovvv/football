"""User-run one-change temporal-control quality screen. Never promotes production."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
import json,hashlib,subprocess,time
from pathlib import Path
import numpy as np
from possession.decode import decode
from possession.core import promote
from review_frozen import score
R=Path('experiments/control-context-2026-11-09')
IDS=('J03WMX','J03WN1','J03WOH','J03WOY','J03WPY')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def temporal(x,blocks):
 """Centered +/-25 frames, excludes current frame, uses only jointly observed distances."""
 out=np.full((len(x),2),np.nan)
 for a,b in blocks:
  a,b=int(a),int(b);v=np.isfinite(x[a:b,0])&np.isfinite(x[a:b,1]);z=np.where(v,np.sign(x[a:b,1]-x[a:b,0]),0.)
  cs=np.r_[0.,np.cumsum(z)];ct=np.r_[0,np.cumsum(v)];i=np.arange(b-a);lo=np.maximum(0,i-25);hi=np.minimum(b-a,i+26)
  count=ct[hi]-ct[lo]-v;total=cs[hi]-cs[lo]-z;support=hi-lo-1
  out[a:b,0]=np.divide(total,count,out=np.full(len(i),np.nan),where=count>0)
  out[a:b,1]=np.divide(count,support,out=np.zeros(len(i)),where=support>0)
 return np.column_stack([x,out])
def main():
 from datetime import datetime,date
 from zoneinfo import ZoneInfo
 if datetime.now(ZoneInfo('Asia/Kolkata')).date()>date(2026,11,13):raise RuntimeError('Research freeze passed')
 for p in [R/'protocol.md',R/'locked-inputs.json']:
  assert subprocess.check_output(['git','show','HEAD:'+str(p)])==p.read_bytes()
 for p,h in json.loads((R/'locked-inputs.json').read_text()).items():assert sha(p)==h,p
 assert not (R/'results.json').exists(),'No overwriting results'
 from catboost import CatBoostClassifier
 from run_core import PARAMS
 ids=json.loads(Path('experiments/core-development/split.json').read_text())['development'];assert tuple(ids)==IDS
 check=subprocess.run([os.sys.executable,'-m','unittest','discover','-s','tests','-q'],capture_output=True,text=True)
 (R/'tests.txt').write_text(check.stdout+check.stderr);assert check.returncode==0
 sets={}
 for m in ids:
  with np.load('data/external/prepared/'+m+'.npz') as d:
   sets[m]={'x':d['x'].copy(),'y':d['y'].copy(),'blocks':d['blocks'].tolist()}
 rows=[];parents=[];cost=[]
 for m in ids:
  xs=[];ys=[]
  for k,d in sets.items():
   if k==m:continue
   x=temporal(d['x'],d['blocks']);ix=np.arange(0,len(x),5);ix=ix[d['y'][ix]!='X'];xs.append(x[ix]);ys.append(d['y'][ix])
  start=time.monotonic();model=CatBoostClassifier(**PARAMS);model.fit(np.concatenate(xs),np.concatenate(ys));order=[list(model.classes_).index(c) for c in ['H','A','D']]
  d=sets[m]
  for c in ['clean','targetlike']:
   x=d['x'] if c=='clean' else np.load('data/diagnostics-review/'+m+'-targetlike.npz')['x'];prob=model.predict_proba(temporal(x,d['blocks']))[:,order];pred=decode(prob,(1-np.eye(3))*16,d['blocks']);p=np.load('data/diagnostics-review/'+m+'-'+c+'-probs.npz')['p'];base=decode(p,(1-np.eye(3))*16,d['blocks'])
   rows.append({'match':m,'condition':c,**score(d['y'],pred,d['blocks'])});parents.append({'match':m,'condition':c,**score(d['y'],base,d['blocks'])})
  cost.append({'match':m,'seconds':time.monotonic()-start})
  for name,obj in [('results.json',rows),('parent.json',parents),('cost.json',cost)]: (R/name).write_text(json.dumps(obj,indent=2))
  print('Completed',m,flush=True)
 pair=lambda rr:{m:tuple(np.mean([[r['spellF1'],r['macroF1']] for r in rr if r['match']==m],axis=0)) for m in ids}
 a,b=pair(rows),pair(parents);co={m:next(r['spellF1'] for r in rows if r['match']==m and r['condition']=='targetlike')-next(r['spellF1'] for r in parents if r['match']==m and r['condition']=='targetlike') for m in ids}
 gate={'quality_eligible':bool(promote(b,a,True) and np.median(list(co.values()))>=.01),'production_changed':False,'primary_deltas':co,'primary_median_delta':float(np.median(list(co.values()))),'paired_spell_deltas':{m:float(a[m][0]-b[m][0]) for m in ids},'paired_macro_deltas':{m:float(a[m][1]-b[m][1]) for m in ids},'verification_required':'single-thread repeated fit/CSV and clean environment before promotion','sealed_opened':False}
 (R/'gate.json').write_text(json.dumps(gate,indent=2));print(json.dumps(gate),flush=True)
 with Path('ball.md').open('a') as f:f.write('\nManual temporal-control screen completed: '+json.dumps(gate)+'\n')
if __name__=='__main__':main()
