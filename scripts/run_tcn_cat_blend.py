"""One fixed probability ensemble; external development only, no training."""
import json,sys,subprocess,time
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0,str(Path('experiments/tcn-2026-11-10').resolve()))
from tcn_candidate import TCN,configure,predict
from prepare_tcn import authority,sha,IDS
from possession.decode import decode
from possession.inputs import export_labels
from possession.core import promote
from review_frozen import score
R=Path('experiments/tcn-cat-blend-2026-11-10');OUT=Path('data/tcn-cat-blend')
def main():
 authority()
 for f in [R/'protocol.md',R/'locked-inputs.json']:assert subprocess.check_output(['git','show','HEAD:'+str(f)])==f.read_bytes()
 for f,h in json.loads((R/'locked-inputs.json').read_text()).items():assert sha(f)==h,f
 assert not (R/'complementarity.json').exists(),'Never overwrite/resume without review'
 configure();comp=[]
 for m in IDS:
  for c in ['clean','targetlike']:
   d=np.load('data/tcn-prepared/'+m+'-'+c+'.npz');y=d['y'];bb=d['blocks'].tolist();cat=np.load('data/diagnostics-review/'+m+'-'+c+'-probs.npz')['p'];base=decode(cat,(1-np.eye(3))*16,bb);tcn=np.loadtxt('data/tcn-long/'+m+'-'+c+'-first.csv',delimiter=',',skiprows=1,usecols=1,dtype=str);v=y!='X';wrong=v&(tcn!=y)
   comp.append({'match':m,'condition':c,'graded_frames':int(v.sum()),'tcn_wrong':int(wrong.sum()),'cat_correct_tcn_wrong':int((wrong&(base==y)).sum()),'tcn_correct_cat_wrong':int((v&(tcn==y)&(base!=y)).sum())})
 (R/'complementarity.json').write_text(json.dumps(comp,indent=2));supported=sum(any(x['match']==m and x['cat_correct_tcn_wrong']>0 for x in comp) for m in IDS)>=3
 if not supported:(R/'gate.json').write_text(json.dumps({'status':'SKIPPED_NO_COMPLEMENTARY_EVIDENCE','production_changed':False}));return
 OUT.mkdir(exist_ok=True);rows=[];parents=[];det=[];cost=[]
 for m in IDS:
  start=time.monotonic();ck=torch.load('models/tcn-long/'+m+'.pt',map_location='cpu',weights_only=True);model=TCN().eval();model.load_state_dict(ck['state']);sc=(np.array(ck['mean']),np.array(ck['scale']))
  for c in ['clean','targetlike']:
   d=np.load('data/tcn-prepared/'+m+'-'+c+'.npz');x=d['x'];y=d['y'];bb=d['blocks'].tolist();seq=predict(model,x,bb,sc);base=decode(seq,(1-np.eye(3))*16,bb);old=np.loadtxt('data/tcn-long/'+m+'-'+c+'-first.csv',delimiter=',',skiprows=1,usecols=1,dtype=str);assert np.array_equal(base,old),'Parent reconstruction differs'
   cat=np.load('data/diagnostics-review/'+m+'-'+c+'-probs.npz')['p'];mix=.5*seq+.5*cat;mix/=mix.sum(1,keepdims=True);pred=decode(mix,(1-np.eye(3))*16,bb);again=decode(mix.copy(),(1-np.eye(3))*16,bb);paths=[OUT/(m+'-'+c+'-'+tag+'.csv') for tag in ['first','repeat']]
   for path,p in zip(paths,[pred,again]):export_labels(path,p,len(y))
   assert sha(paths[0])==sha(paths[1]);det.append({'match':m,'condition':c,'csv_repeat_equal':True,'parent_reconstructed_exact':True,'sha256':sha(paths[0])});rows.append({'match':m,'condition':c,**score(y,pred,bb)});parents.append({'match':m,'condition':c,**score(y,base,bb)})
  cost.append({'match':m,'seconds':time.monotonic()-start})
  for name,obj in [('results.json',rows),('parent.json',parents),('determinism.json',det),('cost.json',cost)]: (R/name).write_text(json.dumps(obj,indent=2))
  print('Completed',m,flush=True)
 tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-q'],capture_output=True,text=True);(R/'tests.txt').write_text(tests.stdout+tests.stderr)
 pair=lambda rr:{m:tuple(np.mean([[r['spellF1'],r['macroF1']] for r in rr if r['match']==m],axis=0)) for m in IDS}
 a,b=pair(rows),pair(parents);co={m:next(r['spellF1'] for r in rows if r['match']==m and r['condition']=='targetlike')-next(r['spellF1'] for r in parents if r['match']==m and r['condition']=='targetlike') for m in IDS};primary=float(np.median(list(co.values())));gate={'quality_eligible':bool(promote(b,a,tests.returncode==0) and primary>=.01),'primary_median_delta':primary,'primary_deltas':co,'paired_spell_deltas':{m:float(a[m][0]-b[m][0]) for m in IDS},'paired_macro_deltas':{m:float(a[m][1]-b[m][1]) for m in IDS},'matches_improved':sum(a[m][0]>b[m][0] for m in IDS),'tests_passed':tests.returncode==0,'production_changed':False,'clean_environment_verified':False}
 gate['matches_improved']=int(gate['matches_improved']);(R/'gate.json').write_text(json.dumps(gate,indent=2));print(json.dumps(gate),flush=True)
 report='# Fixed50/50blend vs20kTCN\n\n|Match|Setting|TCN spell|Blend spell|TCN macro|Blend macro|\n|---|---|---:|---:|---:|---:|\n'
 for a,b in zip(parents,rows):report+=f"|{a['match']}|{a['condition']}|{a['spellF1']:.6f}|{b['spellF1']:.6f}|{a['macroF1']:.6f}|{b['macroF1']:.6f}|\n"
 (R/'report.md').write_text(report+'\n```json\n'+json.dumps(gate,indent=2)+'\n```\n')
if __name__=='__main__':main()
