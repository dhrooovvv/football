"""Preregistered ball-independent trailing 2.5s whole-pitch bundle."""
import numpy as np
NAMES=['rolling_mean_player_speed','rolling_slow_share','rolling_home_compactness','rolling_away_compactness','rolling_longitudinal_centroid_separation']
WINDOW=63

def whole_pitch(track,teams,blocks,pitch,fps=25):
 xy=track.players[...,:2]*np.asarray(pitch);valid=np.isfinite(xy).all(axis=2);speed=np.full(valid.shape,np.nan)
 for a,b in blocks:
  ok=valid[a+1:b]&valid[a:b-1];v=np.linalg.norm(xy[a+1:b]-xy[a:b-1],axis=2)*fps;speed[a+1:b]=np.where(ok,v,np.nan)
 def mean(x,axis):
  n=np.isfinite(x).sum(axis=axis);s=np.where(np.isfinite(x),x,0).sum(axis=axis);return np.divide(s,n,out=np.full(s.shape,np.nan),where=n>0)
 cols=[mean(speed,1),mean(np.where(np.isfinite(speed),(speed<1).astype(float),np.nan),1)];centers=[]
 for side in [0,1]:
  points=xy[:,np.asarray(teams)==side];good=np.isfinite(points).all(axis=2);points=np.where(good[...,None],points,np.nan);center=mean(points,1);centers.append(center)
  radius=np.sqrt(mean(np.sum((points-center[:,None])**2,axis=2),1));radius[good.sum(axis=1)<2]=np.nan;cols.append(radius)
 cols.append(np.abs(centers[1][:,0]-centers[0][:,0]));raw=np.column_stack(cols);out=np.full_like(raw,np.nan)
 for a,b in blocks:
  z=raw[a:b];finite=np.isfinite(z);s=np.vstack([np.zeros(5),np.cumsum(np.where(finite,z,0),axis=0)]);n=np.vstack([np.zeros(5),np.cumsum(finite,axis=0)]);hi=np.arange(1,len(z)+1);lo=np.maximum(0,hi-WINDOW);count=n[hi]-n[lo];out[a:b]=np.divide(s[hi]-s[lo],count,out=np.full_like(z,np.nan),where=count>0)
 return out
