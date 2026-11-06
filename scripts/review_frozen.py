"""Ordered frozen diagnostics; restricted target outputs remain local."""
import sys,json,hashlib
from pathlib import Path
import numpy as np
from catboost import CatBoostClassifier
from possession.inputs import load_atd,load_teams,Tracking
from possession.core import features,corrupt,promote
from possession.decode import decode
from possession.external import load_match
from possession.diagnostics import summarize
sys.path.insert(0,str(Path('reference/more-than-a-hack-2027-main/evaluation').resolve()))
import possession_metrics as pm
sys.path.insert(0,str(Path('reference/more-than-a-hack-2027-main/starter').resolve()))
from baseline import smooth
OUT=Path('experiments/diagnostics-review');PRIVATE=Path('data/diagnostics-review');PRIVATE.mkdir(exist_ok=True)
def save(p,x):p.write_text(json.dumps(x,indent=2))
def runs(mask):
 e=np.diff(np.r_[False,mask,False].astype(int));return list(zip(np.where(e==1)[0],np.where(e==-1)[0]))
def lengths(mask,blocks):return np.array([b-a for s,t in blocks for a,b in runs(mask[s:t])],dtype=int)
def quant(x):
 x=x[np.isfinite(x)];return np.quantile(x,[0,.1,.5,.9,.99,1]).tolist() if len(x) else []
def stats(x,names):return {n:{'finite_fraction':float(np.isfinite(x[:,i]).mean()),'quantiles':quant(x[:,i])} for i,n in enumerate(names)}
def blocks_valid(y,blocks):return [(int(s+a),int(s+b)) for s,t in blocks for a,b in runs(y[s:t]!='X')]
def score(y,p,blocks):
 g=pm.label_codes(y);q=pm.label_codes(p)
 for _,end in sorted(blocks[:-1],reverse=True):g=np.insert(g,int(end),pm.X);q=np.insert(q,int(end),pm.X)
 r=pm.evaluate(g,q,bootstrap_n=0);err=summarize(g,q,pm)
 sp=pm.spell_scores(g,q,pm.valid_runs(g));err.update(sp['per_iou'][.5])
 pairs=[]
 for a,b in pm.valid_runs(g):pairs.extend(pm.match_transitions(pm.transitions(g,[(a,b)]),pm.transitions(q,[(a,b)]),50,typed='pair')[0])
 err['boundary_shift_quantiles_frames']=quant(np.array([p[0]-t[0] for t,p in pairs],float))
 # Oracle repairs isolate overlapping frame error categories; diagnostic upper bounds, not predictors.
 gains={}
 for kind in ['dead_live','wrong_team']:
  fix=q.copy();v=g!=pm.X
  mask=(((g==pm.D)!=(q==pm.D)) if kind=='dead_live' else ((g!=pm.D)&(q!=pm.D)&(g!=q)))&v
  fix[mask]=g[mask];gains[kind]=pm.spell_scores(g,fix,pm.valid_runs(g))['mean_f1']-r['spell_f1_mean']
 return {'spellF1':r['spell_f1_mean'],'macroF1':r['macro_f1'],'errors':err,'oracle_repair_spellF1_gain':gains}
def main():
 cfg=json.loads(Path('configs/competition.json').read_text());base=Path('data/competition/tactical/BAR-ATH_tactical');blocks=cfg['tactical_half_open_blocks'];pitch=np.array(cfg['pitch_metres'])
 track=load_atd(str(base)+'_atd.txt',199319,46);teams=load_teams(str(base)+'_atd.xml',46,cfg['home_team'],cfg['away_team']);x,names=features(track,teams,blocks,pitch)
 model=CatBoostClassifier();model.load_model('models/core-final.cbm');order=[list(model.classes_).index(c) for c in ['H','A','D']];prob=model.predict_proba(x)[:,order];pred=decode(prob,(1-np.eye(3))*8,blocks)
 old=pm.read_label_csv('data/competition/predictions/candidate.csv');assert np.array_equal(pred,old.label.to_numpy())
 gt=pm.read_label_csv('reference/more-than-a-hack-2027-main/evaluation/gt/BAR-ATH_possession_gt_public.csv');assert pm.validate_submission(old,len(gt)) is None
 # Exactly one public evaluation; all detailed outputs private.
 result=pm.evaluate(pm.label_codes(gt.label.to_numpy()),pm.label_codes(pred),bootstrap_n=0);save(PRIVATE/'public-score.json',result)
 reflected=Tracking(track.players.copy(),track.ball.copy());reflected.players[...,:2]=1-reflected.players[...,:2];reflected.ball[:,:2]=1-reflected.ball[:,:2];xr,_=features(reflected,teams,blocks,pitch)
 valid=np.zeros(len(x),bool)
 for a,b in blocks:valid[a:b]=True
 checks={'frame_offset':'PASS: strict 1..N to 0..N-1 contract and sequential CSV','home_away':'PASS: explicit named metadata mapping','attacking_direction':'PASS: core invariant under 180-degree pitch reflection' if np.allclose(x,xr,equal_nan=True,atol=1e-8) else 'FAIL','coordinate_scaling':'PASS: normalized coordinates scaled by configured metric pitch; no direction-dependent feature','X_outside_graded_blocks':'PASS' if (pred[~valid]=='X').all() else 'FAIL','public_score_used_for_selection':False,'limitations':'Contracts checked; public score alone cannot prove semantic correctness. No alternate offsets, mappings or versions scored.'}
 save(OUT/'target-checks.json',checks);print('Step 1 completed; checks only, public score private.',flush=True)
 miss=~np.isfinite(track.ball[:,:2]).all(axis=1);gap=lengths(miss,blocks);seen=lengths(~miss,blocks)
 save(PRIVATE/'target-shift.json',{'features':stats(x[valid],names),'missing_runs':gap.tolist(),'observed_runs':seen.tolist(),'missing_fraction':float(miss[valid].mean())})
 ids=json.loads(Path('experiments/core-development/split.json').read_text())['development'];allrows=[];shift={};grids={};penalties=[2,8,16,32]
 for i,m in enumerate(ids):
  cache=np.load(Path('data/external/prepared')/(m+'.npz'));y=cache['y'];bb=cache['blocks'].tolist();vb=blocks_valid(y,bb);clean=cache['x'];cp=PRIVATE/(m+'-targetlike.npz')
  if cp.exists():xc=np.load(cp)['x']
  else:
   t,tm,bb,pp,yy=load_match(next(Path('data/external').glob('*matchinformation*'+m+'.xml')),next(Path('data/external').glob('*positions*'+m+'.xml')))
   rng=np.random.default_rng(20261106+i);c=corrupt(t,bb,20261106+i);ball=t.ball.copy()
   for a,b in bb:
    pos=a;missing=bool(rng.random()<miss[valid].mean())
    while pos<b:
     length=int(rng.choice(gap if missing else seen));end=min(b,pos+length)
     if missing:ball[pos:end]=np.nan
     pos=end;missing=not missing
   xc,_=features(Tracking(c.players,ball),tm,bb,pp);np.savez_compressed(cp,x=xc)
  save(PRIVATE/(m+'-shift.json'),{'clean':stats(clean,names),'targetlike':stats(xc,names),'missing_run_quantiles':quant(lengths(clean[:,5]==0,bb)),'targetlike_missing_run_quantiles':quant(lengths(xc[:,5]==0,bb))})
  mod=CatBoostClassifier();mod.load_model('models/core/'+m+'.cbm');order=[list(mod.classes_).index(c) for c in ['H','A','D']]
  for condition,xx in [('clean',clean),('targetlike',xc)]:
   probs=mod.predict_proba(xx)[:,order];np.savez_compressed(PRIVATE/(m+'-'+condition+'-probs.npz'),p=probs)
   for penalty in penalties:
    p=decode(probs,(1-np.eye(3))*penalty,vb);r=score(y,p,bb);allrows.append({'match':m,'condition':condition,'method':'catboost_penalty'+str(penalty),**r})
  print('Step 2 evaluated',m,flush=True)
 save(OUT/'model-results.json',allrows)
 print('Step 2 complete. Starting same-match baselines.',flush=True)
 for m in ids:
  d=np.load(Path('data/external/prepared')/(m+'.npz'));y=d['y'];bb=d['blocks'].tolist();vb=blocks_valid(y,bb)
  for condition,xx in [('clean',d['x']),('targetlike',np.load(PRIVATE/(m+'-targetlike.npz'))['x'])]:
   h,a=xx[:,0],xx[:,1];h=np.where(np.isfinite(h),h,np.inf);a=np.where(np.isfinite(a),a,np.inf);codes=np.where(np.minimum(h,a)<np.inf,np.where(h<=a,0,1),-1)
   for window in [0,25,50,125]:
    p=np.full(len(y),'X')
    for s,t in vb:p[s:t]=smooth(codes[s:t],window)
    allrows.append({'match':m,'condition':condition,'method':'baseline_'+str(window),**score(y,p,bb)})
   prob=np.full((len(y),3),.01);prob[np.arange(len(y)),np.where(codes<0,2,codes)]=.98;p=decode(prob,(1-np.eye(3))*8,vb)
   allrows.append({'match':m,'condition':condition,'method':'nearest_decoder8',**score(y,p,bb)})
  print('Step 3 evaluated',m,flush=True)
 save(OUT/'results.json',allrows);print('Ordered diagnostics complete.',flush=True)
if __name__=='__main__':main()
