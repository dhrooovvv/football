"""External cached-parent diagnostics only; no model fitting or target access."""
import json,hashlib,subprocess
from pathlib import Path
import numpy as np
from review_frozen import score
from possession.decode import decode
R=Path('experiments/control-context-2026-11-09')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 for p in [R/'audit-protocol.md',R/'audit-inputs.json']:
  assert subprocess.check_output(['git','show','HEAD:'+str(p)])==p.read_bytes()
 for p,h in json.loads((R/'audit-inputs.json').read_text()).items():assert sha(p)==h,p
 assert not (R/'audit.json').exists(),'Never overwrite completed audit'
 ids=json.loads(Path('experiments/core-development/split.json').read_text())['development'];rows=[]
 for m in ids:
  with np.load('data/external/prepared/'+m+'.npz') as d:y=d['y'];bb=d['blocks'].tolist();clean=d['x']
  for c in ['clean','targetlike']:
   x=clean if c=='clean' else np.load('data/diagnostics-review/'+m+'-targetlike.npz')['x']
   p=np.load('data/diagnostics-review/'+m+'-'+c+'-probs.npz')['p'];pred=decode(p,(1-np.eye(3))*16,bb)
   age=np.zeros(len(y),int)
   for a,b in bb:
    for i in range(a,b):age[i]=0 if x[i,5]>0 else (age[i-1] if i>a else 0)+1
   slices={}
   for name,mask in [('observed',age==0),('gap_0_1s',(age>0)&(age<=25)),('gap_1_3s',(age>25)&(age<=75)),('gap_3_10s',(age>75)&(age<=250)),('gap_over10s',age>250)]:
    v=mask&(y!='X');dl=v&((y=='D')!=(pred=='D'));wt=v&(y!='D')&(pred!='D')&(y!=pred);live=v&(y!='D')
    slices[name]={'frames':int(v.sum()),'dead_live_wrong':int(dl.sum()),'wrong_team':int(wt.sum()),'true_live':int(live.sum()),'pred_live_on_true_live':int((live&(pred!='D')).sum())}
   rows.append({'match':m,'condition':c,**score(y,pred,bb),'slices':slices})
 (R/'audit.json').write_text(json.dumps(rows,indent=2));print('Completed10 frozen diagnostic cases; no fitting')
if __name__=='__main__':main()
