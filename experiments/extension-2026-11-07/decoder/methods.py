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

def learn_hazards(label_arrays,cap=250):
 lengths=[[] for _ in range(3)]
 for y,blocks in label_arrays:
  for a,b in blocks:
   part=y[a:b];e=np.r_[0,np.flatnonzero(part[1:]!=part[:-1])+1,len(part)]
   for s,t in zip(e[:-1],e[1:]):
    if part[s] in LABELS:lengths[list(LABELS).index(part[s])].append(t-s)
 h=np.empty((3,cap))
 for c,ls in enumerate(lengths):
  ls=np.array(ls)
  for j in range(1,cap+1):
   exposure=int((ls>=j).sum()) if j<cap else int(np.maximum(ls-cap+1,0).sum());ends=int((ls==j).sum()) if j<cap else int((ls>=cap).sum());h[c,j-1]=(ends+1)/(exposure+2)
 return h

def duration_decode(p,blocks,h,cost=16):
 cap=h.shape[1];stay=np.log1p(-h);leave=np.log(h);out=np.full(len(p),'X');diag=np.eye(3,dtype=bool)
 for a,b in blocks:
  log=np.log(np.maximum(p[a:b],1e-12));v=np.full((3,cap),-np.inf);v[:,0]=log[0];newback=np.zeros((b-a,3),np.int16);tailback=np.zeros((b-a,3),bool)
  for t in range(1,b-a):
   exits=v+leave;ages=exits.argmax(axis=1);best=exits[np.arange(3),ages];q=best[:,None]-np.full((3,3),cost);q[diag]=-np.inf;source=q.argmax(axis=0);nv=np.full_like(v,-np.inf);nv[:,0]=q[source,np.arange(3)];newback[t]=source*cap+ages[source]
   nv[:,1:]=v[:,:-1]+stay[:,:-1];tail=v[:,-1]+stay[:,-1];tailback[t]=tail>nv[:,-1];nv[:,-1]=np.maximum(nv[:,-1],tail);nv+=log[t,:,None];nv-=nv.max();v=nv
  code=int(v.argmax());state,age=divmod(code,cap)
  for t in range(b-a-1,-1,-1):
   out[a+t]=LABELS[state]
   if age==0:state,age=divmod(int(newback[t,state]),cap)
   elif age==cap-1 and tailback[t,state]:pass
   else:age-=1
 return out
