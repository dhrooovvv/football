"""SameTCNtraining, one independent clean/ball-gap window view intervention."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('experiments/tcn-2026-11-10').resolve()))
from tcn_candidate import *
def train(sets,steps=200):
 torch.manual_seed(SEED);rng=np.random.default_rng(SEED);view_rng=np.random.default_rng(SEED+424242);scaler=fit_scaler(sets);x=[transform(s['x'],scaler) for s in sets];aug=[transform(s['aug'],scaler) for s in sets];labels=[np.array([{'H':0,'A':1,'D':2,'X':-1}[c] for c in s['y']],np.int64) for s in sets];w=windows(sets);cum=np.cumsum([r[2] for r in w]);assert len(cum) and cum[-1]>0;model=TCN().cpu();opt=torch.optim.Adam(model.parameters(),lr=.001);losses=[];model.train()
 for step in range(steps):
  bx=[];by=[]
  for draw in rng.integers(0,int(cum[-1]),size=8):
   k=int(np.searchsorted(cum,draw,side='right'));j,a,n=w[k];start=a+int(draw-(cum[k-1] if k else 0));bx.append((aug[j] if view_rng.random()<.5 else x[j])[start:start+WINDOW]);by.append(labels[j][start+HALO:start+HALO+CORE])
  opt.zero_grad(set_to_none=True);logits=model(torch.from_numpy(np.stack(bx)))[:,HALO:HALO+CORE];loss=nn.functional.cross_entropy(logits.reshape(-1,3),torch.from_numpy(np.stack(by)).reshape(-1));loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();losses.append(float(loss.detach()))
 model.eval();return model,scaler,losses
