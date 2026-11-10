"""User-run training-segment diagnostic, never development-selection evidence."""
import json,sys,time,subprocess
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0,str(Path('experiments/tcn-2026-11-10').resolve()))
from tcn_candidate import TCN,configure,predict,SEED,WINDOW,HALO,CORE,WIDTH
from prepare_tcn import authority,sha
from review_frozen import score
from possession.decode import decode
R=Path('experiments/tcn-learning-check-2026-11-10')
POINTS=(0,200,1000,2000)
def diagnostic_metrics(model,x,y):
 p=predict(model,x,[(0,len(x))],(0,1));labels=np.array(['H','A','D']);raw=labels[p.argmax(1)];dec=decode(p,(1-np.eye(3))*16,[(0,len(x))]);codes=np.array([{'H':0,'A':1,'D':2}[c] for c in y]);ce=float(-np.log(np.maximum(p[np.arange(len(y)),codes],1e-12)).mean())
 return {'training_segment_only':True,'cross_entropy_full_segment':ce,'argmax_accuracy':float((raw==y).mean()),'argmax':score(y,raw,[(0,len(x))]),'decoder16':score(y,dec,[(0,len(x))]),'true_shares':{c:float((y==c).mean()) for c in labels},'argmax_shares':{c:float((raw==c).mean()) for c in labels},'decoded_shares':{c:float((dec==c).mean()) for c in labels},'class_recalls':{c:float((raw[y==c]==c).mean()) if (y==c).any() else None for c in labels}}
def main():
 authority()
 for f in [R/'protocol.md',R/'locked-inputs.json']:
  assert subprocess.check_output(['git','show','HEAD:'+str(f)])==f.read_bytes()
 for f,h in json.loads((R/'locked-inputs.json').read_text()).items():assert sha(f)==h,f
 assert not (R/'results.json').exists() and not (R/'failure.json').exists(),'Previous diagnostic requires review'
 configure();torch.manual_seed(SEED);rng=np.random.default_rng(SEED)
 with np.load('data/tcn-prepared/J03WMX-clean.npz') as d:
  a,b=d['blocks'][0];end=min(int(b),int(a)+10000);x=np.ascontiguousarray(d['x'][int(a):end],dtype=np.float32);y=d['y'][int(a):end].copy()
 assert len(x)==10000 and x.shape[1]==WIDTH and np.isfinite(x).all(),'Segment contract'
 assert set(y.tolist())=={'H','A','D'} and all((y==c).sum()>=50 for c in ['H','A','D']),'Fixed segment lacks diagnostic class support; do not replace it'
 model=TCN().cpu();opt=torch.optim.Adam(model.parameters(),lr=.001);codes=np.array([{'H':0,'A':1,'D':2}[c] for c in y],np.int64);rows=[];losses=[];start=time.monotonic()
 for step in range(2001):
  if step in POINTS:
   model.eval();r={'step':step,'elapsed_seconds':time.monotonic()-start,**diagnostic_metrics(model,x,y)};rows.append(r);(R/'results.json').write_text(json.dumps(rows,indent=2));print('Checkpoint',step,'training accuracy',r['argmax_accuracy'],'full-segment CE',r['cross_entropy_full_segment'],flush=True)
  if step==2000:break
  model.train();starts=rng.integers(0,len(x)-WINDOW+1,size=8);bx=np.stack([x[s:s+WINDOW] for s in starts]);by=np.stack([codes[s+HALO:s+HALO+CORE] for s in starts]);opt.zero_grad(set_to_none=True);z=model(torch.from_numpy(bx))[:,HALO:HALO+CORE];loss=torch.nn.functional.cross_entropy(z.reshape(-1,3),torch.from_numpy(by).reshape(-1));assert torch.isfinite(loss),'Nonfinite training loss';loss.backward();assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters()),'Nonfinite gradient';torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();losses.append(float(loss.detach()))
 final=rows[-1];passed=final['argmax_accuracy']>=.95 and final['cross_entropy_full_segment']<=.15 and all(v>=.9 for v in final['class_recalls'].values())
 verdict={'training_overfit_diagnostic_pass':bool(passed),'promotion_evidence':False,'production_changed':False,'no_generalization_claim':True,'fixed_budget_steps':2000,'runtime_seconds':time.monotonic()-start};(R/'verdict.json').write_text(json.dumps(verdict,indent=2));(R/'minibatch-losses.json').write_text(json.dumps(losses));print(json.dumps(verdict),flush=True)
 with Path('ball.md').open('a') as f:f.write('\nUser-runTCNtraining-onlydiagnostic completed: '+json.dumps(verdict)+'; checkpoint metrics are training fit only.\n')
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true',required=True);p.parse_args()
 try:main()
 except Exception as e:
  if not (R/'failure.json').exists():(R/'failure.json').write_text(json.dumps({'type':type(e).__name__,'message':str(e),'production_changed':False},indent=2))
  raise
