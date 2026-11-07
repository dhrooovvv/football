import argparse,json,sys,hashlib
from pathlib import Path
import numpy as np
from catboost import CatBoostClassifier
from possession.external import load_match
from possession.core import features,corrupt
from possession.decode import decode
from possession.diagnostics import summarize
sys.path.insert(0,str(Path('reference/more-than-a-hack-2027-main/evaluation').resolve()))
import possession_metrics as metrics
from possession.config import PARAMS,CACHE,ROOT,DATA


def prepare(extra=False):
    if extra:
        sys.path.insert(0,str(ROOT.resolve()))
        from rejected_mean_speed import mean_player_speed
    CACHE.mkdir(exist_ok=True)
    split=json.loads((ROOT/'split.json').read_text())
    for i,m in enumerate(split['development']):
        path=CACHE/(m+'.npz')
        if path.exists() and not extra: continue
        if not list(DATA.glob('*positions*'+m+'.xml')): continue
        t,teams,blocks,pitch,y=load_match(next(DATA.glob('*matchinformation*'+m+'.xml')),next(DATA.glob('*positions*'+m+'.xml')))
        corrupted=corrupt(t,blocks,20261106+i)
        if extra:
            np.savez_compressed(CACHE/(m+'-speed.npz'),x=mean_player_speed(t,blocks,pitch),xc=mean_player_speed(corrupted,blocks,pitch))
            print('Prepared speed',m,flush=True);continue
        x,names=features(t,teams,blocks,pitch);xc,_=features(corrupted,teams,blocks,pitch)
        np.savez_compressed(path,x=x,xc=xc,y=y,blocks=blocks,names=names)
        print('Prepared',m,flush=True)

def run(penalty=2,tag='core',extra=False,team_penalty=None):
    ids=json.loads((ROOT/'split.json').read_text())['development'];sets={m:np.load(CACHE/(m+'.npz')) for m in ids}
    if extra:
        for m,d in list(sets.items()):
            speed=np.load(CACHE/(m+'-speed.npz'));sets[m]={k:d[k] for k in d.files}
            for k in ['x','xc']: sets[m][k]=np.column_stack([d[k],speed[k]])
    out=ROOT/tag;out.mkdir(exist_ok=True);models=Path('models/core-speed' if extra else 'models/core');models.mkdir(parents=True,exist_ok=True)
    rows=[]
    for m in ids:
        modelpath=models/(m+'.cbm');model=CatBoostClassifier(**PARAMS)
        if modelpath.exists(): model.load_model(modelpath)
        else:
            xs=[];ys=[]
            for other,d in sets.items():
                if other==m: continue
                idx=np.arange(0,len(d['y']),5);idx=idx[d['y'][idx]!='X'];xs.append(d['x'][idx]);ys.append(d['y'][idx])
            model.fit(np.concatenate(xs),np.concatenate(ys));model.save_model(modelpath)
        d=sets[m]
        for condition,key in [('clean','x'),('corrupted','xc')]:
            probs=model.predict_proba(d[key])[:,[list(model.classes_).index(c) for c in ['H','A','D']]]
            # Reset decoding at each half and every unsupported-label gap.
            blocks=[]
            for a,b in d['blocks']:
                valid=d['y'][a:b]!='X';edges=np.diff(np.r_[False,valid,False].astype(int));blocks += [(int(a+s),int(a+e)) for s,e in zip(np.where(edges==1)[0],np.where(edges==-1)[0])]
            cost=(np.ones((3,3))-np.eye(3))*penalty
            if team_penalty is not None: cost[0,1]=cost[1,0]=team_penalty
            pred=decode(probs,cost,blocks)
            gt=metrics.label_codes(d['y']);pc=metrics.label_codes(pred)
            # Separate halves with X to prevent evaluation joining equal states.
            for _,end in d['blocks'][:-1]:
                gt=np.insert(gt,int(end),metrics.X);pc=np.insert(pc,int(end),metrics.X)
            r=metrics.evaluate(gt,pc,bootstrap_n=0)
            np.savez_compressed(CACHE/(m+'-'+condition+'-'+tag+'-pred.npz'),probabilities=probs,pred=pred)
            row={'match':m,'condition':condition,**r,'errors':summarize(gt,pc,metrics)};rows.append(row)
            print(m,condition,'spell',r['spell_f1_mean'],'macro',r['macro_f1'],flush=True)
            (out/'results.json').write_text(json.dumps(rows,indent=2))
    (out/'configuration.json').write_text(json.dumps({'catboost':PARAMS,'penalty':penalty,'mean_player_speed':extra,'team_penalty':team_penalty},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--extra',action='store_true');p.add_argument('--penalty',type=float,default=2);p.add_argument('--tag',default='core');p.add_argument('--team-penalty',type=float);a=p.parse_args()
    if a.prepare: prepare(a.extra)
    else: run(a.penalty,a.tag,a.extra,a.team_penalty)
