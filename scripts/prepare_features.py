"""Materialise main-model feature inputs locally, requiring explicit team metadata."""
import argparse
import json
from pathlib import Path
import numpy as np
from possession.inputs import load_atd, load_teams
from possession.features import build_features


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path('data/competition'))
    parser.add_argument('--config',type=Path,default=Path('configs/competition.json'))
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    base=args.root/'tactical/BAR-ATH_tactical'
    meta=Path(str(base)+'_atd.xml')
    if not meta.exists():
        raise SystemExit('Required input missing: BAR-ATH_tactical_atd.xml. No features written.')
    spec=config['sources']['tactical']
    teams=load_teams(meta,spec['slots'],config['home_team'],config['away_team'])
    track=load_atd(Path(str(base)+'_atd.txt'),spec['frames'],spec['slots'])
    features=build_features(track,teams,config['tactical_half_open_blocks'],config['pitch_metres'],config['fps'])
    output=args.root/'derived'
    output.mkdir(exist_ok=True)
    np.savez_compressed(output/'tactical_features.npz',**features)
    (output/'features.json').write_text(json.dumps({'feature_names':list(features),'scope':'label-free tracking features; automatic tag hints kept separate','configuration':config},indent=2))
    print('Feature inputs saved locally. No model fitted and no predictions generated.')

if __name__=='__main__': main()
