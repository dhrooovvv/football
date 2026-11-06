import json,sys,subprocess
from pathlib import Path
import numpy as np
from catboost import CatBoostClassifier
from possession.decode import decode
from possession.core import features,promote
from possession.inputs import load_atd,load_teams
from review_frozen import score,blocks_valid,pm
R=Path('experiments/combined16');P=Path('data/diagnostics-review');C=Path('data/external/prepared')
def main():
 ids=json.loads(Path('experiments/core-development/split.json').read_text())['development'];parents=[r for r in json.loads(Path('experiments/gap-augmentation/decoder-isolation.json').read_text()) if r['method']=='penalty16'];rows=[]
 for m in ids:
  d=np.load(C/(m+'.npz'));model=CatBoostClassifier();model.load_model('models/gap-augmentation/'+m+'.cbm');order=[list(model.classes_).index(c) for c in ['H','A','D']]
  for condition,x in [('clean',d['x']),('targetlike',np.load(P/(m+'-targetlike.npz'))['x'])]:
   prob=model.predict_proba(x)[:,order];pred=decode(prob,(1-np.eye(3))*16,blocks_valid(d['y'],d['blocks']));rows.append({'match':m,'condition':condition,'method':'augmentation16',**score(d['y'],pred,d['blocks'].tolist())})
  print('Combined evaluated',m,flush=True)
 (R/'results.json').write_text(json.dumps(rows,indent=2))
 tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],capture_output=True,text=True);(R/'tests.txt').write_text(tests.stdout+tests.stderr)
 def pair(rr):return {m:tuple(np.mean([[r['spellF1'],r['macroF1']] for r in rr if r['match']==m],axis=0)) for m in ids}
 b=pair(parents);a=pair(rows);ds={m:a[m][0]-b[m][0] for m in ids};dm={m:a[m][1]-b[m][1] for m in ids};primary={m:next(r['spellF1'] for r in rows if r['match']==m and r['condition']=='targetlike')-next(r['spellF1'] for r in parents if r['match']==m and r['condition']=='targetlike') for m in ids}
 gate={'promoted':promote(b,a,tests.returncode==0),'paired_spell_deltas':ds,'paired_macro_deltas':dm,'median_spell_delta':float(np.median(list(ds.values()))),'median_macro_delta':float(np.median(list(dm.values()))),'matches_improved':int(sum(v>0 for v in ds.values())),'primary_corrupted_spell_deltas':primary,'primary_median_delta':float(np.median(list(primary.values()))),'tests_passed':tests.returncode==0};(R/'gate.json').write_text(json.dumps(gate,indent=2))
 print('Combined gate',json.dumps(gate),flush=True)
 # Frozen promoted pipeline before this round; no public labels loaded.
 cfg=json.loads(Path('configs/competition.json').read_text());base=Path('data/competition/tactical/BAR-ATH_tactical');t=load_atd(str(base)+'_atd.txt',199319,46);tm=load_teams(str(base)+'_atd.xml',46,cfg['home_team'],cfg['away_team']);x,_=features(t,tm,cfg['tactical_half_open_blocks'],cfg['pitch_metres']);model=CatBoostClassifier();model.load_model('models/core-final.cbm');order=[list(model.classes_).index(c) for c in ['H','A','D']];pred=decode(model.predict_proba(x)[:,order],(1-np.eye(3))*16,cfg['tactical_half_open_blocks']);valid=pred!='X';sp=[];segments=[]
 for start,end in cfg['tactical_half_open_blocks']:
  part=pred[start:end];edges=np.r_[0,np.flatnonzero(part[1:]!=part[:-1])+1,len(part)]
  for a,b in zip(edges[:-1],edges[1:]):
   segments.append(int(b-a))
   if part[a] in ['H','A']:sp.append(int(b-a))
 target={'pipeline':'frozen unaugmented core-final model, penalty16 (promoted before round; not tuned on aggregates)','graded_frames':int(valid.sum()),'shares':{c:float((pred[valid]==c).mean()) for c in ['H','A','D']},'possession_spell_count':len(sp),'mean_possession_spell_seconds':float(np.mean(sp)/25),'all_state_segment_count':len(segments),'mean_all_state_segment_seconds':float(np.mean(segments)/25)}
 # External summaries directly from caches; no public labels.
 ext=[]
 for m in ids:
  d=np.load(C/(m+'.npz'));y=d['y'];v=y!='X';sp=[]
  for start,end in d['blocks']:
   sp+=pm.possession_spells(pm.label_codes(y),[(int(a),int(b)) for a,b in blocks_valid(y,[(start,end)])])
  ext.append({'match':m,'shares':{c:float((y[v]==c).mean()) for c in ['H','A','D']},'possession_spell_count':len(sp),'mean_possession_spell_seconds':float(np.mean([b-a for a,b,_ in sp])/25)})
 (R/'target-aggregate.json').write_text(json.dumps({'target':target,'external_ground_truth':ext},indent=2));print('Label-free aggregate diagnostic complete.',flush=True)
if __name__=='__main__':main()
