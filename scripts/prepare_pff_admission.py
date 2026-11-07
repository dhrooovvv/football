import json,hashlib,gc,time,concurrent.futures,multiprocessing
from pathlib import Path
import numpy as np
from possession.pff import load_pff
from possession.core import features,corrupt
from possession.inputs import Tracking
R=Path('experiments/pff-admission');OUT=Path('data/pff/features')
def prepare(args):
 i,m,target=args;start=time.monotonic()
 try:
  t,teams,bb,pitch,y,counts=load_pff('data/pff/release',m);x,names=features(t,teams,bb,pitch);natural=~np.isfinite(t.ball[:,:2]).all(axis=1);c=corrupt(t,bb,20261106+i);ball=t.ball.copy();rng=np.random.default_rng(20261106+i)
  for a,b in bb:
   pos=a;missing=bool(rng.random()<target['missing_fraction'])
   while pos<b:
    end=min(b,pos+int(rng.choice(target['missing_runs'] if missing else target['observed_runs'])))
    if missing:ball[pos:end]=np.nan
    pos=end;missing=not missing
  xc,_=features(Tracking(c.players,ball),teams,bb,pitch);v=y!='X';path=OUT/(m+'.npz');np.savez_compressed(path,x=x,xc=xc,y=y,blocks=bb,natural_missing=natural,names=names)
  row={'match':m,'status':'pass','frames':len(y),'known_labels':int(v.sum()),'known_fraction':float(v.mean()),'natural_missing_graded':int((natural&v).sum()),'corrupted_missing_graded':int(((xc[:,5]==0)&v).sum()),'label_by_natural_observation':{z:{'visible':int(((y==z)&~natural).sum()),'missing':int(((y==z)&natural).sum())} for z in ['H','A','D','X']},'counts':counts,'feature_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'seconds':time.monotonic()-start}
 except (ValueError,KeyError,AssertionError) as e:row={'match':m,'status':'fail','reason':str(e),'seconds':time.monotonic()-start}
 return row

def main():
 OUT.mkdir(parents=True,exist_ok=True);split=json.loads(Path('experiments/pff-intake/split.json').read_text());ids=sorted(split['pff_additional_training']+split['pff_transfer_holdout']);target=json.loads(Path('data/diagnostics-review/target-shift.json').read_text());paths=['src/possession/pff.py','src/possession/core.py','src/possession/features.py','experiments/pff-admission/protocol.md','experiments/pff-intake/split.json','experiments/pff-intake/release-manifest.json'];(R/'snapshot.json').write_text(json.dumps({p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},indent=2));rows=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn')) as pool:
  futures=[pool.submit(prepare,(i,m,target)) for i,m in enumerate(ids)]
  for f in concurrent.futures.as_completed(futures):
   r=f.result();rows.append(r);(R/'admission.json').write_text(json.dumps(sorted(rows,key=lambda r:r['match']),indent=2));print(r['match'],r['status'],flush=True)
 print('All64 admission attempts complete',flush=True)
if __name__=='__main__':main()
