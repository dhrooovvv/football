import numpy as np
from .features import build_features
from .inputs import Tracking

def features(track,teams,blocks,pitch,fps=25):
    base=build_features(track,teams,blocks,pitch,fps)
    h=base['home_nearest_ball_m'];a=base['away_nearest_ball_m']
    xy=track.ball[:,:2]*pitch
    edge=np.minimum.reduce([xy[:,0],pitch[0]-xy[:,0],xy[:,1],pitch[1]-xy[:,1]])
    out={'home_distance':h,'away_distance':a,'distance_margin':a-h,'ball_speed':base['ball_displacement_speed_m_s'],'edge_distance':edge,'ball_observed':base['ball_visible'],'home_observed':np.isfinite(h).astype(float),'away_observed':np.isfinite(a).astype(float),'gap_age':base['ball_gap_seconds']}
    return np.column_stack(list(out.values())),list(out)

def corrupt(track,blocks,seed):
    rng=np.random.default_rng(seed);p=track.players.copy();b=track.ball.copy()
    for start,stop in blocks:
        for t in np.flatnonzero(rng.random(stop-start)<.005)+start:
            b[t:min(stop,t+int(rng.integers(25,101))),:]=np.nan
        for j in range(p.shape[1]):
            for t in np.flatnonzero(rng.random(stop-start)<.001)+start:
                p[t:min(stop,t+int(rng.integers(10,51))),j,:]=np.nan
    return Tracking(p,b)

def promote(before,after,tests_pass):
    ids=sorted(before)
    if ids!=sorted(after) or len(ids)!=5: raise ValueError('Five paired development matches required')
    d=np.array([after[i][0]-before[i][0] for i in ids]);m=np.array([after[i][1]-before[i][1] for i in ids])
    return bool(tests_pass and np.median(d)>0 and (d>0).sum()>len(ids)/2 and np.median(m)>=-.01-1e-12)

def mean_player_speed(track,blocks,pitch,fps=25):
    out=np.full(len(track.ball),np.nan)
    for a,b in blocks:
        xy=track.players[a:b,:,:2]*pitch
        good=np.isfinite(xy[1:]).all(axis=2)&np.isfinite(xy[:-1]).all(axis=2)
        speed=np.linalg.norm(np.diff(xy,axis=0),axis=2)*fps
        count=good.sum(axis=1)
        out[a+1:b]=np.divide(np.where(good,speed,0).sum(axis=1),count,out=np.full(len(count),np.nan),where=count>0)
    return out
