"""Preregistered CPU-only admission; no quality scoring or target inputs."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[k]='1'
import sys,json,time,hashlib,subprocess,urllib.request
from pathlib import Path
R=Path('experiments/tabicl-2026-11-08');D=Path('data/tabicl');D.mkdir(exist_ok=True)
def worker(kind):
 import numpy as np,torch
 from tabicl import TabICLClassifier
 from possession.decode import decode
 from possession.inputs import export_labels
 from importlib.metadata import distributions
 torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True);torch.backends.mkldnn.enabled=False
 np.random.seed(20261106);torch.manual_seed(20261106)
 if kind!='actual':
  n=int(kind);rng=np.random.default_rng(20261106);x=rng.normal(size=(n,9));y=np.array(['H','A','D'])[np.arange(n)%3];q=rng.normal(size=(64,9));x[::13,0]=np.nan;q[::7,0]=np.nan
 else:
  ids=json.loads(Path('experiments/core-development/split.json').read_text())['development'];xs=[];ys=[]
  for m in ids[1:]:
   d=np.load(Path('data/external/prepared')/(m+'.npz'));idx=np.arange(0,len(d['y']),5);idx=idx[d['y'][idx]!='X'];xs.append(d['x'][idx]);ys.append(d['y'][idx])
  x=np.concatenate(xs);y=np.concatenate(ys);q=np.load(Path('data/external/prepared')/(ids[0]+'.npz'))['x'][:64]
 params=dict(n_estimators=1,softmax_temperature=1.,random_state=20261106,n_jobs=1,device='cpu',use_amp=False,use_fa3=False,offload_mode=False,kv_cache=False,model_path=str(D/'model.ckpt'),allow_auto_download=False)
 results=[];hashes=[];start=time.monotonic()
 for rep in range(2):
  model=TabICLClassifier(**params);model.fit(x,y);p=model.predict_proba(q)[:,[list(model.classes_).index(c) for c in ['H','A','D']]]
  assert np.isfinite(p).all() and np.allclose(p.sum(1),1)
  results.append(p);pred=decode(p,(1-np.eye(3))*16,[(0,len(p))]);f=D/(kind+'-'+str(rep)+'.csv');export_labels(f,pred,len(pred));hashes.append(hashlib.sha256(f.read_bytes()).hexdigest())
 same=np.array_equal(*results);csvsame=len(set(hashes))==1
 out=dict(probe=kind,context_rows=len(x),query_rows=len(q),seconds=time.monotonic()-start,probabilities_equal=same,csv_equal=csvsame,csv_sha256=hashes[0],params=params,classes_order='H,A,D',dependencies={d.metadata['Name']:d.version for d in distributions() if d.metadata['Name'] in ['tabicl','torch','numpy','scikit-learn','scipy','einops','huggingface_hub']})
 (R/(kind+'.json')).write_text(json.dumps(out,indent=2));assert same and csvsame,'Determinism admission failed'
 print(json.dumps(out),flush=True)
def main():
 import psutil
 meta=json.loads((R/'weight-source.json').read_text());weight=D/'model.ckpt'
 if not weight.exists(): urllib.request.urlretrieve('https://huggingface.co/'+meta['repo']+'/resolve/'+meta['revision']+'/'+meta['filename'],weight)
 meta['sha256']=hashlib.sha256(weight.read_bytes()).hexdigest();meta['bytes']=weight.stat().st_size;(R/'weight-source.json').write_text(json.dumps(meta,indent=2))
 reports=[]
 for kind in ['1000','10000','actual']:
  log=(R/(kind+'.log')).open('w');start=time.monotonic();p=subprocess.Popen([sys.executable,__file__,'--worker',kind],stdout=log,stderr=subprocess.STDOUT);peak=0;reason=None
  while p.poll() is None:
   try: peak=max(peak,psutil.Process(p.pid).memory_info().rss)
   except psutil.NoSuchProcess: pass
   if time.monotonic()-start>300:reason='300 second resource cap'
   if peak>6*1024**3:reason='6 GiB resident-memory cap'
   if reason: p.terminate();p.wait(timeout=10);break
   time.sleep(.25)
  log.close();reports.append(dict(probe=kind,exit_code=p.returncode,reason=reason,wall_seconds=time.monotonic()-start,peak_rss_bytes=peak));(R/'admission.json').write_text(json.dumps(reports,indent=2));print(reports[-1],flush=True)
  if p.returncode!=0 or reason:break
if __name__=='__main__':
 if len(sys.argv)>1:worker(sys.argv[2])
 else:main()
