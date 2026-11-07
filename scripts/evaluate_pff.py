"""Preregistered A then B; no target/sealed labels or transfer-based selection."""
import sys,json,time,subprocess,hashlib
from pathlib import Path
import numpy as np
from catboost import CatBoostClassifier
from possession.config import PARAMS
from possession.decode import decode
from possession.core import promote
from review_frozen import pm,blocks_valid
R=Path('experiments/pff-evaluation');MODELS=Path('models/pff-evaluation');MODELS.mkdir(exist_ok=True);PFF=Path('data/pff/features');IDSSE=Path('data/external/prepared');DIAG=Path('data/diagnostics-review')
def save(name,x):(R/name).write_text(json.dumps(x,indent=2))
def missing(y,p,mask):
 v=(y!='X')&mask;g=y[v]=='D';q=p[v]=='D';tp=int((g&q).sum());fp=int((~g&q).sum());fn=int((g&~q).sum());tn=int((~g&~q).sum());ratio=lambda a,b:a/b if b else None
 return {'frames':int(v.sum()),'true_D':int(g.sum()),'true_live':int((~g).sum()),'TP_D':tp,'FP_D':fp,'FN_D':fn,'TN_D':tn,'D_f1':ratio(2*tp,2*tp+fp+fn),'live_f1':ratio(2*tn,2*tn+fp+fn),'D_precision':ratio(tp,tp+fp),'D_recall':ratio(tp,tp+fn),'live_recall':ratio(tn,tn+fp),'predicted_D_share':ratio(tp+fp,len(g))}
def measure(model,m,provider,condition,legacy=False):
 path=(PFF if provider=='pff' else IDSSE)/(m+'.npz');d=np.load(path);y=d['y'];bb=d['blocks'].tolist();x=d['x'] if condition=='clean' else d['xc'] if provider=='pff' else np.load(DIAG/(m+'-targetlike.npz'))['x'];natural=d['natural_missing'] if provider=='pff' else d['x'][:,5]==0;probs=model.predict_proba(x,thread_count=1)[:,[list(model.classes_).index(c) for c in ['H','A','D']]];pred=decode(probs,(1-np.eye(3))*16,blocks_valid(y,bb) if legacy else bb);g=pm.label_codes(y);p=pm.label_codes(pred)
 for _,end in sorted(bb[:-1],reverse=True):g=np.insert(g,int(end),pm.X);p=np.insert(p,int(end),pm.X)
 r=pm.evaluate(g,p,bootstrap_n=0);allmiss=x[:,5]==0
 return {'match':m,'provider':provider,'condition':condition,'spellF1':r['spell_f1_mean'],'macroF1':r['macro_f1'],'known_label_fraction':float((y!='X').mean()),'known_frames':int((y!='X').sum()),'subsets':{n:missing(y,pred,v) for n,v in [('natural_missing',natural),('newly_masked',allmiss&~natural),('all_missing',allmiss),('observed',~allmiss)]},'inference_blocks':'label_valid_runs_legacy' if legacy else 'halves_only'}
def samples(ids,provider):
 xs=[];ys=[]
 for m in ids:
  d=np.load((PFF if provider=='pff' else IDSSE)/(m+'.npz'));y=d['y'];idx=np.arange(0,len(y),5);idx=idx[y[idx]!='X'];xs.append(d['x'][idx]);ys.append(y[idx])
 return np.concatenate(xs),np.concatenate(ys)
def fit(name,x,y):
 start=time.monotonic();model=CatBoostClassifier(**PARAMS);model.fit(x,y);model.save_model(str(MODELS/(name+'.cbm')));return model,time.monotonic()-start

def main():
 split=json.loads(Path('experiments/pff-intake/split.json').read_text());ad=json.loads(Path('experiments/pff-admission/admission.json').read_text());assert len(ad)==64;passed={r['match'] for r in ad if r['status']=='pass'};train=[m for m in split['pff_additional_training'] if m in passed];held=[m for m in split['pff_transfer_holdout'] if m in passed];assert len(train)>=2 and len(held)>=2;ids=split['idsse_development'];cohort={'training':train,'transfer_holdout':held,'excluded':[r for r in ad if r['status']!='pass'],'admission_sha256':hashlib.sha256(Path('experiments/pff-admission/admission.json').read_bytes()).hexdigest()};save('cohort.json',cohort)
 # Cohort committed by caller before this process starts: not inferred from model scores.
 assert Path('experiments/pff-evaluation/cohort-lock.json').exists();assert json.loads(Path('experiments/pff-evaluation/cohort-lock.json').read_text())==cohort
 px,py=samples(train,'pff');rows=[];times=[]
 for m in ids:
  ix,iy=samples([k for k in ids if k!=m],'idsse')
  for arm,x,y in [('parent',ix,iy),('expanded',np.concatenate([ix,px]),np.concatenate([iy,py]))]:
   model,secs=fit(m+'-'+arm,x,y);times.append({'match':m,'arm':arm,'training_rows':len(y),'seconds':secs})
   for condition in ['clean','targetlike']:rows.append({'arm':arm,**measure(model,m,'idsse',condition,True)})
   save('train-more-results.json',rows);save('cost.json',times);print('A',m,arm,flush=True)
 pair=lambda rr:{m:tuple(np.mean([[r['spellF1'],r['macroF1']] for r in rr if r['match']==m],axis=0)) for m in ids};b=pair([r for r in rows if r['arm']=='parent']);a=pair([r for r in rows if r['arm']=='expanded']);ds={m:a[m][0]-b[m][0] for m in ids};dm={m:a[m][1]-b[m][1] for m in ids};cor={m:next(r['spellF1'] for r in rows if r['match']==m and r['condition']=='targetlike' and r['arm']=='expanded')-next(r['spellF1'] for r in rows if r['match']==m and r['condition']=='targetlike' and r['arm']=='parent') for m in ids};test=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-q'],capture_output=True,text=True);(R/'tests.txt').write_text(test.stdout+test.stderr);base=promote(b,a,test.returncode==0);primary=float(np.median(list(cor.values())));gate={'promoted':base and primary>=.01,'existing_gate':base,'median_primary_delta':primary,'paired_spell_deltas':ds,'paired_macro_deltas':dm,'primary_deltas':cor,'matches_improved':int(sum(v>0 for v in ds.values())),'tests_pass':test.returncode==0};save('gate.json',gate);print('A decision',json.dumps(gate),flush=True)
 # Freeze A decision before transfer; never use B to choose settings.
 transfer=[];forward=CatBoostClassifier();forward.load_model('models/core-final.cbm')
 for m in held:
  for condition in ['clean','targetlike']:transfer.append({'direction':'IDSSE5_to_PFF_holdout',**measure(forward,m,'pff',condition)})
  save('transfer-results.json',transfer);print('B forward',m,flush=True)
 reverse,secs=fit('PFF_only_reverse',px,py);times.append({'arm':'reverse_PFF_only','training_rows':len(py),'seconds':secs});save('cost.json',times)
 for m in ids:
  for condition in ['clean','targetlike']:transfer.append({'direction':'PFF_training_to_IDSSE5',**measure(reverse,m,'idsse',condition)})
  save('transfer-results.json',transfer);print('B reverse',m,flush=True)
 print('Both evaluations complete',flush=True)
if __name__=='__main__':main()
