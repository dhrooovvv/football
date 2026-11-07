import sys,json,time,hashlib,subprocess,io
from pathlib import Path
import numpy as np
import torch
from possession.decode import decode
from possession.core import promote
from possession.inputs import export_labels
from review_frozen import score
from evaluate_pff import missing
R=Path('experiments/gru-2026-11-08');sys.path.insert(0,str(R.resolve()));from gru_candidate import configure,train,predict,GRU,blend
M=Path('models/gru-candidate');M.mkdir(exist_ok=True);OUT=Path('data/gru-candidate');OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 configure();ids=json.loads(Path('experiments/core-development/split.json').read_text())['development'];sets={m:np.load(Path('data/external/prepared')/(m+'.npz')) for m in ids};rows=[];parent=[];det=[];cost=[]
 for m,d in sets.items():
  fits=[sets[k] for k in ids if k!=m];start=time.monotonic();model,scaler,loss=train(fits);secs=time.monotonic()-start;path=M/(m+'.pt');torch.save({'state':model.state_dict(),'mean':scaler[0].tolist(),'scale':scaler[1].tolist()},path);loaded=torch.load(path,map_location='cpu',weights_only=True);reload=GRU().cpu();reload.load_state_dict(loaded['state']);reload.eval();reload_scaler=(np.array(loaded['mean']),np.array(loaded['scale']));again,sc2,loss2=train(fits);same=all(torch.equal(v,again.state_dict()[k]) for k,v in model.state_dict().items());same=same and np.array_equal(scaler,sc2) and loss==loss2;assert same,'Repeat training nondeterministic';bb=d['blocks'].tolist()
  cost.append({'match':m,'steps':200,'batch':8,'input_window':250,'retained_loss_frames':200,'initial_training_seconds':secs,'initial_loss':loss[0],'final_loss':loss[-1]})
  for condition,x in [('clean',d['x']),('targetlike',np.load(Path('data/diagnostics-review')/(m+'-targetlike.npz'))['x'])]:
   cat=np.load(Path('data/diagnostics-review')/(m+'-'+condition+'-probs.npz'))['p'];seq=predict(model,x,bb,scaler);seq_reload=predict(reload,x,bb,reload_scaler);assert np.array_equal(seq,seq_reload),'Reload probabilities differ';p=blend(cat,seq);pred=decode(p,(1-np.eye(3))*16,bb);base=decode(cat,(1-np.eye(3))*16,bb);pred_reload=decode(blend(cat,seq_reload),(1-np.eye(3))*16,bb);batch_pred=decode(blend(cat,predict(model,x,bb,scaler,batch=4)),(1-np.eye(3))*16,bb);paths=[OUT/(m+'-'+condition+'-'+tag+'.csv') for tag in ['first','reload','batch4']]
   for f,y in zip(paths,[pred,pred_reload,batch_pred]):export_labels(f,y,len(y))
   csvsame=len({sha(f) for f in paths})==1;assert csvsame,'CSV batch/reload mismatch';det.append({'match':m,'condition':condition,'repeated_training_equal':same,'reload_probabilities_equal':True,'csv_bytes_equal_reload_batch4':csvsame,'csv_sha256':sha(paths[0])});rows.append({'match':m,'condition':condition,**score(d['y'],pred,bb),'missing_ball':missing(d['y'],pred,x[:,5]==0)});parent.append({'match':m,'condition':condition,**score(d['y'],base,bb),'missing_ball':missing(d['y'],base,x[:,5]==0)})
  for name,value in [('results.json',rows),('parent.json',parent),('determinism.json',det),('cost.json',cost)]: (R/name).write_text(json.dumps(value,indent=2))
  print('Completed',m,flush=True)
 pair=lambda rr:{m:tuple(np.mean([[r['spellF1'],r['macroF1']] for r in rr if r['match']==m],axis=0)) for m in ids};a=pair(rows);b=pair(parent);ds={m:a[m][0]-b[m][0] for m in ids};dm={m:a[m][1]-b[m][1] for m in ids};co={m:next(r['spellF1'] for r in rows if r['match']==m and r['condition']=='targetlike')-next(r['spellF1'] for r in parent if r['match']==m and r['condition']=='targetlike') for m in ids};tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-q'],capture_output=True,text=True);(R/'production-tests.txt').write_text(tests.stdout+tests.stderr);base=promote(b,a,tests.returncode==0);delta=float(np.median(list(co.values())));gate={'promoted':base and delta>=.01 and all(r['csv_bytes_equal_reload_batch4'] for r in det),'existing_gate':base,'primary_median_delta':delta,'paired_spell_deltas':ds,'paired_macro_deltas':dm,'primary_deltas':co,'matches_improved':int(sum(v>0 for v in ds.values())),'tests_pass':tests.returncode==0,'determinism_pass':True};(R/'gate.json').write_text(json.dumps(gate,indent=2));print(json.dumps(gate),flush=True)
if __name__=='__main__':main()
