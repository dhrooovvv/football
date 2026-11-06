"""Rejected candidate retained only to reproduce the recorded experiment."""
import numpy as np

def mean_player_speed(track,blocks,pitch,fps=25):
    out=np.full(len(track.ball),np.nan)
    for a,b in blocks:
        xy=track.players[a:b,:,:2]*pitch
        good=np.isfinite(xy[1:]).all(axis=2)&np.isfinite(xy[:-1]).all(axis=2)
        speed=np.linalg.norm(np.diff(xy,axis=0),axis=2)*fps
        count=good.sum(axis=1)
        out[a+1:b]=np.divide(np.where(good,speed,0).sum(axis=1),count,out=np.full(len(count),np.nan),where=count>0)
    return out
