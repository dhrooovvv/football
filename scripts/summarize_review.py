import json
from pathlib import Path
import numpy as np
from possession.core import promote
R=Path('experiments/diagnostics-review')
def main():
 rows=json.loads((R/'results.json').read_text());methods=sorted({r['method'] for r in rows});ids=sorted({r['match'] for r in rows})
 def pair(method):return {m:tuple(np.mean([[r['spellF1'],r['macroF1']] for r in rows if r['method']==method and r['match']==m],axis=0)) for m in ids}
 base=pair('catboost_penalty8');gates={}
 for method in methods:
  if not method.startswith('catboost'):continue
  after=pair(method);ds=[after[m][0]-base[m][0] for m in ids];dm=[after[m][1]-base[m][1] for m in ids]
  gates[method]={'passes_gate':promote(base,after,True),'median_spell_delta':float(np.median(ds)),'median_macro_delta':float(np.median(dm)),'matches_improved':int(sum(x>0 for x in ds))}
 (R/'grid-gates.json').write_text(json.dumps(gates,indent=2))
 lines=['# Frozen diagnostic development results','', 'All figures are external development evidence. Target rows, distributions and public score remain local. Clean/target-like mean is the paired gate input. Frozen production remains penalty8 pending review.','', '| Method | Condition | Mean spellF1 | Mean macroF1 |','|---|---|---:|---:|']
 for method in methods:
  for condition in ['clean','targetlike']:
   subset=[r for r in rows if r['method']==method and r['condition']==condition];lines.append(f"| {method} | {condition} | {np.mean([r['spellF1'] for r in subset]):.6f} | {np.mean([r['macroF1'] for r in subset]):.6f} |")
 lines+=['','## Frozen penalty8 per-match taxonomy','','Boundary quantiles: min/p10/median/p90/p99/max in frames; only typed boundaries matched within 2 seconds. Missed/spurious use IoU .5. Oracle gains are overlapping diagnostic repair upper bounds, not additive causal attribution or selectable predictions.','','| Match | Condition | spellF1 | macroF1 | Missed | Spurious | Short recall | Dead/live wrong frames | Boundary quantiles | Oracle dead/live gain | Oracle wrong-team gain |','|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|']
 for r in rows:
  if r['method']!='catboost_penalty8':continue
  e=r['errors'];o=r['oracle_repair_spellF1_gain'];lines.append(f"| {r['match']} | {r['condition']} | {r['spellF1']:.6f} | {r['macroF1']:.6f} | {e['n_missed']} | {e['n_spurious']} | {e['short_spell_recall_iou_05']:.4f} | {e['dead_live_wrong_frames']} | {e['boundary_shift_quantiles_frames']} | {o['dead_live']:.6f} | {o['wrong_team']:.6f} |")
 (R/'summary.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps(gates,indent=2))
 print('\n'.join(lines[:24]))
if __name__=='__main__':main()
