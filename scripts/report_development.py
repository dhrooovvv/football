import json,csv,subprocess,sys
from pathlib import Path
import numpy as np
from possession.core import promote
root=Path('experiments/core-development')
def paired(rows):
 return {m:(float(np.mean([r['spell_f1_mean'] for r in rows if r['match']==m])),float(np.mean([r['macro_f1'] for r in rows if r['match']==m]))) for m in sorted({r['match'] for r in rows})}
def report(tag,before=None):
 rows=json.loads((root/tag/'results.json').read_text())
 if len(rows)!=10 or len({(r['match'],r['condition']) for r in rows})!=10: raise ValueError('Incomplete five-match comparison')
 lines=['| Match | Condition | spellF1 | macroF1 | Missed@.5 | Spurious@.5 | Short recall@.5 | Dead/live errors |','|---|---|---:|---:|---:|---:|---:|---:|']
 for r in rows:
  s=r['spell_f1']['0.5'];e=r['errors'];short=e['short_spell_recall_iou_05']
  lines.append(f"| {r['match']} | {r['condition']} | {r['spell_f1_mean']:.6f} | {r['macro_f1']:.6f} | {s['n_missed']} | {s['n_spurious']} | {short if short is not None else 'N/A'} | {e['dead_live_wrong_frames']} |")
 if before:
  b=paired(json.loads((root/before/'results.json').read_text()));a=paired(rows)
  check=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-q'],capture_output=True,text=True)
  (root/tag/'test-output.txt').write_text(check.stdout+check.stderr)
  result={'tests_passed':check.returncode==0,'promoted':promote(b,a,check.returncode==0),'paired_spell_deltas':{m:a[m][0]-b[m][0] for m in a},'paired_macro_deltas':{m:a[m][1]-b[m][1] for m in a}}
  (root/tag/'gate.json').write_text(json.dumps(result,indent=2));lines.append('\nGate: '+json.dumps(result))
 text='\n'.join(lines)+'\n';(root/tag/'summary.md').write_text(text);print(text)
if __name__=='__main__':
 import sys
 report(*sys.argv[1:])
