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

SLOTS=64
CHANNELS=8
WIDTH=SLOTS*CHANNELS+9
class TCN(nn.Module):
 def __init__(self):
  super().__init__();self.object=nn.Conv1d(5,8,3,padding=1)
  self.layers=nn.Sequential(nn.Conv1d(33,32,3,padding=1),nn.ReLU(),nn.Conv1d(32,32,3,padding=2,dilation=2),nn.ReLU(),nn.Conv1d(32,32,3,padding=4,dilation=4),nn.ReLU(),nn.Conv1d(32,3,1))
 def forward(self,x):
  b,t,_=x.shape;o=x[:,:,:SLOTS*CHANNELS].reshape(b,t,SLOTS,CHANNELS)
  h=torch.relu(self.object(o[:,:,:,:5].permute(0,2,3,1).reshape(b*SLOTS,5,t))).reshape(b,SLOTS,8,t).permute(0,3,1,2)
  pools=[]
  for k in [5,6,7]:
   mask=o[:,:,:,k]*o[:,:,:,4];pools.append((h*mask.unsqueeze(-1)).sum(2)/mask.sum(2).clamp_min(1).unsqueeze(-1))
  z=torch.cat(pools+[x[:,:,-9:]],dim=-1)
  return self.layers(z.transpose(1,2)).transpose(1,2)

def fit_scaler(sets):return np.zeros(WIDTH),np.ones(WIDTH)
def transform(x,scaler):
 assert x.shape[1]==WIDTH and np.isfinite(x).all()
 return np.ascontiguousarray(x,dtype=np.float32)

def windows(sets):
 out=[]
 for j,s in enumerate(sets):
  for a,b in s['blocks']:
   valid=s['y'][a:b]!='X';e=np.diff(np.r_[False,valid,False].astype(int))
   for x,z in zip(np.where(e==1)[0],np.where(e==-1)[0]):
    if z-x>=WINDOW:out.append((j,int(a+x),int(z-x-WINDOW+1)))
 return out

def train(sets,steps=200):
 torch.manual_seed(SEED);rng=np.random.default_rng(SEED);scaler=fit_scaler(sets);x=[transform(s['x'],scaler) for s in sets];labels=[np.array([{'H':0,'A':1,'D':2,'X':-1}[c] for c in s['y']],np.int64) for s in sets];w=windows(sets);cum=np.cumsum([r[2] for r in w]);assert len(cum) and cum[-1]>0;model=TCN().cpu();opt=torch.optim.Adam(model.parameters(),lr=.001);losses=[];model.train()
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
