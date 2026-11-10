"""User-run preparation of training-only independent raw ball gaps."""
import json,subprocess,sys
from pathlib import Path
import numpy as np
from prepare_tcn import authority as original_authority,sha,encode,IDS
from possession.external import load_match
from possession.inputs import Tracking
from possession.core import features
R=Path('experiments/tcn-gap-2026-11-10');OUT=Path('data/tcn-gap-prepared')
def authority():
 original_authority()
 for f in [R/'protocol.md',R/'locked-inputs.json']:assert subprocess.check_output(['git','show','HEAD:'+str(f)])==f.read_bytes()
 for f,h in json.loads((R/'locked-inputs.json').read_text()).items():assert sha(f)==h,f

def mask_ball(ball,blocks,gaps,observed,fraction,seed):
 rng=np.random.default_rng(seed);b=ball.copy()
 assert len(gaps) and len(observed) and min(gaps)>0 and min(observed)>0
 for a,z in blocks:
  pos=int(a);missing=bool(rng.random()<fraction)
  while pos<z:
   end=min(int(z),pos+int(rng.choice(gaps if missing else observed)))
   if missing:b[pos:end]=np.nan
   pos=end;missing=not missing
 return b

def main():
 authority();assert not OUT.exists(),'No preparation overwrite';OUT.mkdir();raw=json.loads(Path('experiments/tcn-2026-11-10/raw-paths.json').read_text());target=json.loads(Path('data/diagnostics-review/target-shift.json').read_text());manifest={};fidelity=[]
 for i,m in enumerate(IDS):
  t,tm,bb,pitch,y=load_match(*raw[m]);seed=20261206+i;ball=mask_ball(t.ball,bb,target['missing_runs'],target['observed_runs'],target['missing_fraction'],seed);core,_=features(Tracking(t.players,ball),tm,bb,pitch);clean,_=features(t,tm,bb,pitch);old=np.load('data/external/prepared/'+m+'.npz');assert np.array_equal(y,old['y']) and np.array_equal(bb,old['blocks']) and np.allclose(clean,old['x'],equal_nan=True,atol=0,rtol=0)
  # Ball gaps alter ball-dependent features only; players remain clean and labels unchanged.
  x=encode(Tracking(t.players,ball),tm,bb,core);p=OUT/(m+'.npz');np.savez_compressed(p,x=x,y=y,blocks=bb);manifest[str(p)]=sha(p);fidelity.append({'match':m,'seed':seed,'training_view_missing_fraction':float((core[:,5]==0).mean()),'target_observed_missing_fraction':target['missing_fraction'],'labels_changed':False});print('Prepared independent training view',m,flush=True)
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));(R/'training-corruption-fidelity.json').write_text(json.dumps(fidelity,indent=2));print('Training-view preparation complete; no fitting')
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',required=True,action='store_true');p.parse_args();main()
