import json,subprocess,sys
from pathlib import Path
import numpy as np
from possession.core import promote
R=Path('experiments/gap-augmentation');P=Path('data/diagnostics-review');C=Path('data/external/prepared')
def load(p):return json.loads(Path(p).read_text())
def main():
 aug=load(R/'augmentation-results.json');dec=load(R/'decoder-isolation.json');ids=sorted({r['match'] for r in aug});assert len(aug)==10
 checks=[]
 for m in ids:
  d=np.load(C/(m+'.npz'));ev=np.load(P/(m+'-targetlike.npz'))['x'];tr=np.load(P/(m+'-training-targetlike.npz'))['x'];assert not np.array_equal(ev[:,5],tr[:,5])
  for name,x in [('evaluation',ev),('training',tr)]:
   for a,b in d['blocks']:
    age=0
    for t in range(a,b):
     age=0 if x[t,5] else age+1
     assert abs(x[t,8]-age/25)<1e-10
     if not x[t,5] or t==a or not x[t-1,5]:assert np.isnan(x[t,3])
   checks.append({'match':m,'setting':name,'mask_gap_speed_consistent':True})
 test=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],capture_output=True,text=True);(R/'tests.txt').write_text(test.stdout+test.stderr);assert test.returncode==0
 (R/'mask-checks.json').write_text(json.dumps(checks,indent=2))
 def pair(rows):
  assert len(rows)==10
  return {m:tuple(np.mean([[r['spellF1'],r['macroF1']] for r in rows if r['match']==m],axis=0)) for m in ids}
 b=[r for r in dec if r['method']=='penalty8'];six=[r for r in dec if r['method']=='penalty16'];bp=pair(b)
 gates={}
 for name,rr in [('augmentation_penalty8',aug),('penalty16',six)]:
  ap=pair(rr);ds=[ap[m][0]-bp[m][0] for m in ids];dm=[ap[m][1]-bp[m][1] for m in ids];cs={m:next(r['spellF1'] for r in rr if r['match']==m and r['condition']=='targetlike')-next(r['spellF1'] for r in b if r['match']==m and r['condition']=='targetlike') for m in ids}
  gates[name]={'promoted':promote(bp,ap,True),'paired_spell_deltas':dict(zip(ids,ds)),'paired_macro_deltas':dict(zip(ids,dm)),'median_paired_spell_delta':float(np.median(ds)),'median_paired_macro_delta':float(np.median(dm)),'matches_improved':int(sum(v>0 for v in ds)),'primary_corrupted_spell_deltas':cs,'primary_median_delta':float(np.median(list(cs.values())))}
 (R/'gates.json').write_text(json.dumps(gates,indent=2))
 lines=['# Approved augmentation and prerequisite report','', 'Primary augmentation metric: target-like corrupted spellF1. Promotion gate unchanged: per-match arithmetic mean clean/corrupted spellF1; positive median paired gain, majority improve, median paired macroF1 delta >=-.01, tests pass. Frozen penalty8 parent for both isolated changes.','', '## Corruption fidelity','', '| Match | Target missing | Original corrupted missing | Target-like missing |','|---|---:|---:|---:|']
 for r in load(R/'fidelity.json'):lines.append(f"| {r['match']} | {r['target_observed_missing_fraction']:.4f} | {r['original_corrupted_missing_fraction']:.4f} | {r['targetlike_missing_fraction']:.4f} |")
 lines+=['','Evaluation masks were applied to raw ball positions before feature computation. Cached training/evaluation features pass mask/gap-age/speed consistency checks. Training seeds20271106+i; evaluation20261106+i; replacement20281106+i. Actual missing rates vary because long runs and half-boundary truncation create sampling variance; no post-hoc calibration on labels.','', 'Longer contiguous gaps can remove many flickering predicted spells while erasing more graded live frames. That can raise spellF1 while lowering macroF1: spells and frames are weighted differently. This is an evidence-supported mechanism, not an isolated causal experiment; missing fraction and run structure both changed.','', '## Decoder isolation and augmentation means','', '| Method | Condition | spellF1 | macroF1 |','|---|---|---:|---:|']
 for method in ['argmax','smooth50','penalty8','penalty16','augmentation_penalty8']:
  source=aug if method=='augmentation_penalty8' else dec
  for condition in ['clean','targetlike']:
   rr=[r for r in source if r['method']==method and r['condition']==condition];lines.append(f"| {method} | {condition} | {np.mean([r['spellF1'] for r in rr]):.6f} | {np.mean([r['macroF1'] for r in rr]):.6f} |")
 lines+=['','Smoothing50 uses the supplied centered H/A majority logic on CatBoost argmax codes, D contributing no H/A vote. It is not a three-class probability smoother. Nearest-player+decoder used near-hard .98/.01 emissions and is not evidence isolating decoder quality.','', '## Label conventions','', '| Match | Dead share | Mean possession spell seconds |','|---|---:|---:|']
 sem=load(R/'label-conventions.json')
 for r in sem['external']+[dict(match='Public window (semantics only)',**sem['public_window_semantics_only'])]:lines.append(f"| {r['match']} | {r['dead_share']:.4f} | {r['mean_possession_spell_seconds']:.4f} |")
 lines+=['','Documentation: external DFL/floodlight BallStatus0=Dead,1=Alive and BallPossession1=Home,2=Away (literature/idsse.md); target DATA.md public summary has17 maximal H/A spells, mean14.2s, with D denoting dead ball per EVALUATION.md. Both nominally use H/A/D, but exact ownership continuation through loose balls/flight is not established equivalent. External unknown ownership is excluded as X and breaks spells, which can shorten measured spells.','', 'Baseline macroF1 about .38 externally versus the previously supplied target scores about .67 is a warning of possible convention/domain mismatch, not proof. External clean balls are essentially always observed: nearest-player almost never emits D despite41–52% dead labels. Target ball absence about41% makes its missing=>D heuristic behave differently; short public sampling also differs. Do not relabel, tune mappings or claim transfer equivalence from this comparison. No new public performance scoring.','', '## Per-match augmentation against penalty8','', '| Match | Condition | Parent spellF1 | Aug spellF1 | Parent macroF1 | Aug macroF1 |','|---|---|---:|---:|---:|---:|']
 for r in aug:
  q=next(x for x in b if x['match']==r['match'] and x['condition']==r['condition']);lines.append(f"| {r['match']} | {r['condition']} | {q['spellF1']:.6f} | {r['spellF1']:.6f} | {q['macroF1']:.6f} | {r['macroF1']:.6f} |")
 lines+=['','## Gates','',json.dumps(gates,indent=2),'','23 existing tests pass plus ten cache consistency audits. Sealed matches untouched. No combined augmentation+penalty16 experiment, no new target prediction export. Stop after this report.']
 (R/'report.md').write_text('\n'.join(lines)+'\n');print(json.dumps(gates,indent=2));print('\n'.join(lines[22:38]))
if __name__=='__main__':main()
