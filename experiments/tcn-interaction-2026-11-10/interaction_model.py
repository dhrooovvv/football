"""One representation change: masked player-ball relativeXY before object encoding."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('experiments/tcn-2026-11-10').resolve()))
from tcn_candidate import TCN as ParentTCN,SLOTS,CHANNELS
import torch
from torch import nn

def relations(o):
 mask=o[:,:,:,4]*o[:,:,-1:,4];mask=mask.clone();mask[:,:,-1]=0
 relative=(o[:,:,:,:2]-o[:,:,-1:,:2])*mask.unsqueeze(-1)
 return torch.cat([relative,mask.unsqueeze(-1)],dim=-1)

class TCN(ParentTCN):
 def __init__(self):
  super().__init__();self.object=nn.Conv1d(8,8,3,padding=1)
 def forward(self,x):
  b,t,_=x.shape;o=x[:,:,:SLOTS*CHANNELS].reshape(b,t,SLOTS,CHANNELS);v=torch.cat([o[:,:,:,:5],relations(o)],dim=-1)
  h=torch.relu(self.object(v.permute(0,2,3,1).reshape(b*SLOTS,8,t))).reshape(b,SLOTS,8,t).permute(0,3,1,2)
  pools=[]
  for k in [5,6,7]:
   mask=o[:,:,:,k]*o[:,:,:,4];pools.append((h*mask.unsqueeze(-1)).sum(2)/mask.sum(2).clamp_min(1).unsqueeze(-1))
  return self.layers(torch.cat(pools+[x[:,:,-9:]],dim=-1).transpose(1,2)).transpose(1,2)
