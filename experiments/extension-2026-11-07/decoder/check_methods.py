import itertools,numpy as np
from methods import variable_decode,duration_decode
rng=np.random.default_rng(8);p=rng.dirichlet([1,1,1],size=5);h=rng.uniform(.01,.4,size=(3,3));labels=['H','A','D']
def val(s):
 z=sum(np.log(p[t,c]) for t,c in enumerate(s));age=0
 for t in range(1,len(s)):
  if s[t]==s[t-1]:z+=np.log1p(-h[s[t-1],min(age,2)]);age=min(age+1,2)
  else:z+=np.log(h[s[t-1],min(age,2)])-16;age=0
 return z
q=duration_decode(p,[(0,5)],h);s=tuple(labels.index(c) for c in q);assert abs(val(s)-max(val(t) for t in itertools.product(range(3),repeat=5)))<1e-10
q=variable_decode(p,[(0,5)],live_cost=8);s=tuple(labels.index(c) for c in q)
def asym(s):return sum(np.log(p[t,c]) for t,c in enumerate(s))-sum((8 if max(s[t],s[t-1])<2 else 16) for t in range(1,5) if s[t]!=s[t-1])
assert abs(asym(s)-max(asym(t) for t in itertools.product(range(3),repeat=5)))<1e-10
print('Asymmetric and semi-Markov exhaustive contracts passed.')
