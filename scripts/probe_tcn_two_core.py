"""Label-free operational CSV check with trained parent weights lifted to interaction shape."""
import sys,json,time,subprocess,hashlib
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0,str(Path('experiments/tcn-interaction-2026-11-10').resolve()))
from interaction_model import TCN
from interaction_training import predict
from possession.decode import decode
from possession.inputs import export_labels
R=Path('experiments/tcn-cores-2026-11-10');OUT=Path('data/tcn-core-probe')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 for p in [R/'inference-protocol.md',R/'inference-inputs.json']:assert subprocess.check_output(['git','show','HEAD:'+str(p)])==p.read_bytes()
 for p,h in json.loads((R/'inference-inputs.json').read_text()).items():assert sha(p)==h,p
 torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True);torch.backends.mkldnn.enabled=False;OUT.mkdir(exist_ok=True)
 ck=torch.load('models/tcn-gap/J03WMX.pt',map_location='cpu',weights_only=True);state=ck['state'];w=state['object.weight'];state['object.weight']=torch.cat([w,torch.zeros((8,3,3))],dim=1);model=TCN().eval();model.load_state_dict(state)
 with np.load('data/tcn-prepared/J03WMX-clean.npz') as d:x=d['x'][:16384].copy()
 cat=np.load('data/diagnostics-review/J03WMX-clean-probs.npz')['p'][:16384];rows=[];first=None
 for n in [1,2]:
  torch.set_num_threads(n);t=time.monotonic();p=predict(model,x,[(0,len(x))],(0,1));q=predict(model,x,[(0,len(x))],(0,1));assert np.array_equal(p,q),'Within-mode prediction differs';mix=.5*p+.5*cat;mix/=mix.sum(1,keepdims=True);y=decode(mix,(1-np.eye(3))*16,[(0,len(x))]);f=OUT/(str(n)+'.csv');export_labels(f,y,len(y));rows.append({'threads':n,'seconds_two_predictions':time.monotonic()-t,'within_mode_probabilities_exact':True,'csv_sha256':sha(f),'max_probability_delta_vs_one_thread':0. if first is None else float(np.abs(p-first).max())});first=p if first is None else first
 out={'cases':rows,'cross_thread_csv_equal':rows[0]['csv_sha256']==rows[1]['csv_sha256'],'trained_parent_lifted_zero_extra_weights':True,'actual_candidate_weights_tested':False,'no_quality_scores':True};(R/'inference-results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':main()
