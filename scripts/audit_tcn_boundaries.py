"""Cached external error audit, no learning or new model inference."""
import json,subprocess
from pathlib import Path
import numpy as np
from review_frozen import score,pm
from prepare_tcn import sha,IDS
from possession.decode import decode
R=Path('experiments/tcn-boundary-audit-2026-11-10')
def main():
 for f in [R/'protocol.md',R/'locked-inputs.json']:assert subprocess.check_output(['git','show','HEAD:'+str(f)])==f.read_bytes()
 for f,h in json.loads((R/'locked-inputs.json').read_text()).items():assert sha(f)==h,f
 assert not (R/'results.json').exists()
 rows=[]
 for m in IDS:
  for condition in ['clean','targetlike']:
   d=np.load('data/tcn-prepared/'+m+'-'+condition+'.npz');y=d['y'];blocks=d['blocks'].tolist();observed=d['x'][:,-4]>0;g=pm.label_codes(y)
   for tag,root in [('tcn','data/tcn-long'),('blend','data/tcn-cat-blend'),('gap_blend','data/tcn-gap'),('catboost',None)]:
    p=decode(np.load('data/diagnostics-review/'+m+'-'+condition+'-probs.npz')['p'],(1-np.eye(3))*16,blocks) if root is None else np.loadtxt(root+'/'+m+'-'+condition+'-first.csv',delimiter=',',skiprows=1,usecols=1,dtype=str)
    q=pm.label_codes(p);age=np.zeros(len(y),int);near=np.zeros(len(y),bool)
    for a,b in blocks:
     for i in range(a,b):age[i]=0 if observed[i] else (age[i-1] if i>a else 0)+1
     for i in np.flatnonzero(y[a+1:b]!=y[a:b-1])+a+1:near[max(a,i-25):min(b,i+26)]=True
    slices={}
    for name,v in [('observed',observed),('missing',~observed),('missing_over1s',age>25),('near_gt_boundary',near),('interior',~near)]:
     v=v&(y!='X');dl=v&((y=='D')!=(p=='D'));wt=v&(y!='D')&(p!='D')&(y!=p);slices[name]={'frames':int(v.sum()),'wrong_team':int(wt.sum()),'dead_live_wrong':int(dl.sum()),'true_live':int((v&(y!='D')).sum()),'live_recovered':int((v&(y!='D')&(p!='D')).sum())}
    # Half-separated official scores provide full spell and matched-boundary diagnostics.
    r=score(y,p,blocks);sp=[];predsp=[];flags=[]
    for a,b in blocks:
     gy=g[a:b];py=q[a:b];runs=pm.valid_runs(gy);gs=pm.possession_spells(gy,runs);ps=pm.possession_spells(py,runs);sp+=gs;predsp+=ps;flags.extend(pm.matched_gt_flags(pm.spell_overlaps(gs,ps),len(gs),.5).tolist())
    lengths=np.array([b-a for a,b,_ in sp]);flags=np.array(flags,bool);short=lengths<=50
    rows.append({'match':m,'condition':condition,'model':tag,**r,'slices':slices,'true_possession_count':len(sp),'predicted_possession_count':len(predsp),'short_true':int(short.sum()),'short_matched':int(flags[short].sum()),'long_true':int((~short).sum()),'long_matched':int(flags[~short].sum())})
 (R/'results.json').write_text(json.dumps(rows,indent=2));print('Audited40cached cases; no training/model inference')
if __name__=='__main__':main()
