import sys,json,itertools,subprocess
from pathlib import Path
import numpy as np
from possession.decode import decode
from possession.core import promote
from review_frozen import score,blocks_valid
R=Path('experiments/extension-2026-11-07/decoder');sys.path.insert(0,str(R.resolve()));from methods import variable_decode,learn_hazards,duration_decode

def main():
 method=sys.argv[1];ids=json.loads(Path('experiments/core-development/split.json').read_text())['development'];parents=[r for r in json.loads(Path('experiments/gap-augmentation/decoder-isolation.json').read_text()) if r['method']=='penalty16'];rows=[]
 # Exhaustive optimization contract for variable costs, including initial state.
 rng=np.random.default_rng(13);p=rng.dirichlet([1,1,1],size=5);age=np.arange(5)/2;pred=variable_decode(p,[(0,5)],ages=age);seq=tuple(['H','A','D'].index(c) for c in pred)
 def value(s):return sum(np.log(p[t,c]) for t,c in enumerate(s))-sum(16*(1+min(age[t]/2,1)) for t in range(1,5) if s[t]!=s[t-1])
 assert abs(value(seq)-max(value(s) for s in itertools.product(range(3),repeat=5)))<1e-10
 assert np.array_equal(variable_decode(p,[(0,5)]),decode(p,(1-np.eye(3))*16,[(0,5)]))
 for m in ids:
  if method=='duration':
   training=[]
   for other in ids:
    if other!=m:
     tr=np.load(Path('data/external/prepared')/(other+'.npz'));training.append((tr['y'],tr['blocks']))
   hazard=learn_hazards(training)
  d=np.load(Path('data/external/prepared')/(m+'.npz'));bb=d['blocks'].tolist();vb=blocks_valid(d['y'],bb)
  for condition,key in [('clean','x'),('targetlike','xc')]:
   x=d['x'] if condition=='clean' else np.load(Path('data/diagnostics-review')/(m+'-targetlike.npz'))['x'];p=np.load(Path('data/diagnostics-review')/(m+'-'+condition+'-probs.npz'))['p'];pred=(duration_decode(p,vb,hazard) if method=='duration' else variable_decode(p,vb,ages=x[:,8] if method=='gap' else None,live_cost=8 if method=='asymmetric' else None));rows.append({'match':m,'condition':condition,**score(d['y'],pred,bb)})
  print(method,m,flush=True)
  (R/(method+'-results.json')).write_text(json.dumps(rows,indent=2))
 pair=lambda rr:{m:tuple(np.mean([[r['spellF1'],r['macroF1']] for r in rr if r['match']==m],axis=0)) for m in ids};a=pair(rows);b=pair(parents);ds={m:a[m][0]-b[m][0] for m in ids};dm={m:a[m][1]-b[m][1] for m in ids};cor={m:next(r['spellF1'] for r in rows if r['match']==m and r['condition']=='targetlike')-next(r['spellF1'] for r in parents if r['match']==m and r['condition']=='targetlike') for m in ids};test=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-q'],capture_output=True,text=True);(R/(method+'-tests.txt')).write_text(test.stdout+test.stderr);base=promote(b,a,test.returncode==0);primary=float(np.median(list(cor.values())));gate={'promoted':base and primary>=.01,'existing_gate':base,'median_primary_delta':primary,'paired_spell_deltas':ds,'paired_macro_deltas':dm,'primary_deltas':cor,'matches_improved':int(sum(x>0 for x in ds.values())),'tests_passed':test.returncode==0,'exhaustive_contract':True};(R/(method+'-gate.json')).write_text(json.dumps(gate,indent=2));print(json.dumps(gate))
if __name__=='__main__':main()
