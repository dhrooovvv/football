import json,hashlib
from pathlib import Path
import numpy as np
from possession.core import promote
R=Path('experiments/gru-2026-11-08')
def main():
 load=lambda p:json.loads(Path(p).read_text());rows=load(R/'results.json');parent=load(R/'parent.json');g=load(R/'gate.json');det=load(R/'determinism.json');cost=load(R/'cost.json');ids=load('experiments/core-development/split.json')['development'];assert len(rows)==len(parent)==len(det)==10;assert len(cost)==5
 for path,value in load(R/'snapshot.json')['source_hashes'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==value,'Source drift'
 pair=lambda rr:{m:tuple(np.mean([[r['spellF1'],r['macroF1']] for r in rr if r['match']==m],axis=0)) for m in ids};a=pair(rows);b=pair(parent);assert g['existing_gate']==promote(b,a,True);assert not g['promoted'];assert all(d['repeated_training_equal'] and d['reload_probabilities_equal'] and d['csv_bytes_equal_reload_batch4'] for d in det)
 legacy=[r for r in load('experiments/gap-augmentation/decoder-isolation.json') if r['method']=='penalty16'];differences=[]
 for p in parent:
  q=next(q for q in legacy if q['match']==p['match'] and q['condition']==p['condition']);differences.append({'match':p['match'],'condition':p['condition'],'spell_delta':p['spellF1']-q['spellF1'],'macro_delta':p['macroF1']-q['macroF1']})
 (R/'parent-block-comparison.json').write_text(json.dumps(differences,indent=2));lines=['# Optional CPU GRU blend — rejected, November8','', 'One preregistered candidate only: scratch1layerbidirectionalhidden16,200Adamsteps,batch8,250framewindows/200retainedlossframes,9fold-standardizedfeatures,cleanIDSSE4training, fixed75%CatBoost/25%GRU andViterbi16. No PFF/target/public/sealeddata used. Noaugmentation/calibration/search. CatBoost unchanged, GRUadditionalcompute explicitly bounded.','', '**Reject:**1/5pairedmatches improve; median corruptedspell delta-.007520 fails+.01minimum and existingpairedgate fails. No rescuedblend/window/budget. Productionunchanged.','', '| Match | Setting | Parent spellF1 | Blend spellF1 | Parent macroF1 | Blend macroF1 |','|---|---|---:|---:|---:|---:|']
 for r in rows:
  p=next(p for p in parent if p['match']==r['match'] and p['condition']==r['condition']);lines.append(f"| {r['match']} | {r['condition']} | {p['spellF1']:.6f} | {r['spellF1']:.6f} | {p['macroF1']:.6f} | {r['macroF1']:.6f} |")
 lines+=['','| Arm | Setting | Mean spellF1 | Mean macroF1 | Fold spellF1 SD |','|---|---|---:|---:|---:|']
 for arm,rr in [('parent',parent),('GRUblend',rows)]:
  for condition in ['clean','targetlike']:
   z=[r for r in rr if r['condition']==condition];lines.append(f"| {arm} | {condition} | {np.mean([r['spellF1'] for r in z]):.6f} | {np.mean([r['macroF1'] for r in z]):.6f} | {np.std([r['spellF1'] for r in z],ddof=1):.6f} |")
 lines+=['','## Determinism and parent comparability','','All5folds repeated full200step training with identical state tensors/scaler/losssequence. All10heldoutcases: exact reloadprobabilities and decodedCSVbytes equal atfixedbatch1 andbatch4. These are version/platform-specific results, not crosshardwareguarantees.1000 candidate updates plus 1000 independent repeat-verification updates = 2000 total; eachbatch8×250inputframes, losscentral200. Trainingtime cost.json records ONLYinitialtraining time, excludes repeatverification and inference. Modelserializationbyteequality notclaimed.','',f"Maximum parent half-block versus historical label-supported score difference: spell{max(abs(x['spell_delta']) for x in differences):.12g},macro{max(abs(x['macro_delta']) for x in differences):.12g}. No label-derived reset used for this experiment.",'','## Missing-ball quality','','| Match | Setting | Arm | Missing frames | Live recall | D precision | D recall | Predicted D share |','|---|---|---|---:|---:|---:|---:|---:|']
 def fmt(x):return 'undefined' if x is None else f'{x:.6f}'
 for arm,rr in [('parent',parent),('GRUblend',rows)]:
  for r in rr:
   m=r['missing_ball'];lines.append(f"| {r['match']} | {r['condition']} | {arm} | {m['frames']} | {fmt(m['live_recall'])} | {fmt(m['D_precision'])} | {fmt(m['D_recall'])} | {fmt(m['predicted_D_share'])} |")
 lines+=['','## Limits','','10swindow is shorter than median10.72sgaps and much shorter than p90~33.8s; some interiorscannotseeobservedendpoints. Bidirectionalwindows use localfutureobservations offline. Clean-onlytraining leaves missing masks/gapageOOD. This failure is evidence against this fixedsmallbudgetcandidate, not allGRUs or sequence modelling. No new temporal feature,augmentation or largercontexttriedafterresults. Five developmentmatches have historicalreuse; no unbiased generalization claim. Torchisolatedresearchdependency, notproductionrequirement.','', 'Gate:','```json',json.dumps(g,indent=2),'```']
 (R/'report.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines[18:27]))
if __name__=='__main__':main()
