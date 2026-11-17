"""Synthetic operational speed check, no match quality evidence."""
import argparse,subprocess,sys,json,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--threads',type=int);a=p.parse_args()
if a.threads:
 import torch
 sys.path.insert(0,str(Path('experiments/tcn-interaction-2026-11-10').resolve()))
 from interaction_model import TCN
 torch.set_num_threads(a.threads);torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True);torch.backends.mkldnn.enabled=False
 def run():
  torch.manual_seed(7);m=TCN();x=torch.randn(8,250,521);y=torch.randint(0,3,(8,200));opt=torch.optim.Adam(m.parameters(),lr=.001);start=time.monotonic()
  for _ in range(50):
   opt.zero_grad();z=m(x)[:,25:225];loss=torch.nn.functional.cross_entropy(z.reshape(-1,3),y.reshape(-1));loss.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),1);opt.step()
  return time.monotonic()-start,{k:v.detach().clone() for k,v in m.state_dict().items()}
 t,s=run();t2,s2=run();print(json.dumps({'threads':a.threads,'seconds':[t,t2],'within_mode_weights_exact':all(torch.equal(v,s2[k]) for k,v in s.items()),'synthetic_only':True}))
else:
 r=[json.loads(subprocess.check_output([sys.executable,__file__,'--threads',str(n)],text=True)) for n in [1,11]];Path('experiments/tcn-cores-2026-11-10/results.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
