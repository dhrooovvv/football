"""Rebuild development training inputs from original external XML, no target labels."""
import json
from pathlib import Path
import numpy as np
from possession.external import load_match
from possession.core import features

def main():
 out=Path('data/reproduction/prepared');out.mkdir(parents=True,exist_ok=True)
 for m in json.loads(Path('experiments/core-development/split.json').read_text())['development']:
  t,tm,bb,pp,y=load_match(next(Path('data/external').glob('*matchinformation*'+m+'.xml')),next(Path('data/external').glob('*positions*'+m+'.xml')));x,names=features(t,tm,bb,pp);old=np.load(Path('data/external/prepared')/(m+'.npz'));assert np.allclose(x,old['x'],equal_nan=True,atol=0,rtol=0);assert np.array_equal(y,old['y']);np.savez_compressed(out/(m+'.npz'),x=x,y=y,blocks=bb,names=names);print('Clean rebuilt',m,flush=True)
if __name__=='__main__':main()
