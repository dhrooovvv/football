"""Isolated preregistered CPU sequence candidate; not production."""
import numpy as np
import torch
from torch import nn
WINDOW=250
HALO=25
CORE=200
SEED=20261106

def configure():
 torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True);torch.backends.mkldnn.enabled=False

class GRU(nn.Module):
 def __init__(self):
  super().__init__();self.gru=nn.GRU(9,16,batch_first=True,bidirectional=True);self.head=nn.Linear(32,3)
 def forward(self,x):return self.head(self.gru(x)[0])

def fit_scaler(sets):
 x=np.concatenate([s['x'][s['y']!='X'] for s in sets]);mean=np.nanmean(x,axis=0);scale=np.nanstd(x,axis=0);mean=np.where(np.isfinite(mean),mean,0);scale=np.where(np.isfinite(scale)&(scale>0),scale,1);return mean,scale

def transform(x,scaler):
 mean,scale=scaler;return np.ascontiguousarray(np.nan_to_num(np.clip((x-mean)/scale,-10,10),nan=0).astype(np.float32))

def windows(sets):
 out=[]
 for j,s in enumerate(sets):
  for a,b in s['blocks']:
   valid=s['y'][a:b]!='X';e=np.diff(np.r_[False,valid,False].astype(int))
   for x,z in zip(np.where(e==1)[0],np.where(e==-1)[0]):
    if z-x>=WINDOW:out.append((j,int(a+x),int(z-x-WINDOW+1)))
 return out

def train(sets,steps=200):
 torch.manual_seed(SEED);rng=np.random.default_rng(SEED);scaler=fit_scaler(sets);x=[transform(s['x'],scaler) for s in sets];labels=[np.array([{'H':0,'A':1,'D':2,'X':-1}[c] for c in s['y']],np.int64) for s in sets];w=windows(sets);cum=np.cumsum([r[2] for r in w]);assert len(cum) and cum[-1]>0;model=GRU().cpu();opt=torch.optim.Adam(model.parameters(),lr=.001);losses=[];model.train()
 for step in range(steps):
  bx=[];by=[]
  for draw in rng.integers(0,int(cum[-1]),size=8):
   k=int(np.searchsorted(cum,draw,side='right'));j,a,n=w[k];start=a+int(draw-(cum[k-1] if k else 0));bx.append(x[j][start:start+WINDOW]);by.append(labels[j][start+HALO:start+HALO+CORE])
  opt.zero_grad(set_to_none=True);logits=model(torch.from_numpy(np.stack(bx)))[:,HALO:HALO+CORE];loss=nn.functional.cross_entropy(logits.reshape(-1,3),torch.from_numpy(np.stack(by)).reshape(-1));loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();losses.append(float(loss.detach()))
 model.eval();return model,scaler,losses

def predict(model,x,blocks,scaler,batch=1):
 x=transform(x,scaler);out=np.full((len(x),3),1/3,dtype=np.float64);seen=np.zeros(len(x),int);items=[]
 for a,b in blocks:
  for s in range(a,b,CORE):items.append((int(a),int(b),int(s),int(min(CORE,b-s))))
 with torch.no_grad():
  for k in range(0,len(items),batch):
   desc=items[k:k+batch];bx=np.stack([x[np.clip(np.arange(s-HALO,s+CORE+HALO),a,b-1)] for a,b,s,n in desc]);p=torch.softmax(model(torch.from_numpy(bx)),dim=-1).numpy().astype(np.float64)
   for j,(a,b,s,n) in enumerate(desc):out[s:s+n]=p[j,HALO:HALO+n];seen[s:s+n]+=1
 for a,b in blocks:assert (seen[a:b]==1).all()
 out/=out.sum(axis=1,keepdims=True);assert np.isfinite(out).all();return out

def blend(cat,seq):
 out=.75*np.asarray(cat,np.float64)+.25*np.asarray(seq,np.float64);return out/out.sum(axis=1,keepdims=True)
