import numpy as np
LABELS=np.array(['H','A','D'])
def variable_decode(p,blocks,ages=None,live_cost=None):
 out=np.full(len(p),'X')
 for a,b in blocks:
  log=np.log(np.maximum(p[a:b],1e-12));v=log[0].copy();back=np.zeros((b-a,3),np.int8)
  for t in range(1,b-a):
   cost=(1-np.eye(3))*16
   if ages is not None:cost*=1+min(ages[a+t]/2,1)
   if live_cost is not None:cost[0,1]=cost[1,0]=live_cost
   q=v[:,None]-cost;back[t]=q.argmax(axis=0);v=q[back[t],np.arange(3)]+log[t];v-=v.max()
  state=v.argmax()
  for t in range(b-a-1,-1,-1):out[a+t]=LABELS[state];state=back[t,state]
 return out
