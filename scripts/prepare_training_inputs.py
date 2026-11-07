"""Prepare clean development training inputs from external XML in a fresh clone."""
import argparse,json
from pathlib import Path
import numpy as np
from possession.external import load_match
from possession.core import features

def main():
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=Path('data/external'));p.add_argument('--output',type=Path,default=Path('data/external/prepared'));a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 for m in json.loads(Path('experiments/core-development/split.json').read_text())['development']:
  t,tm,bb,pp,y=load_match(next(a.data.glob('*matchinformation*'+m+'.xml')),next(a.data.glob('*positions*'+m+'.xml')));x,names=features(t,tm,bb,pp);np.savez_compressed(a.output/(m+'.npz'),x=x,y=y,blocks=bb,names=names);print('Prepared development match',m,flush=True)
if __name__=='__main__':main()
