"""User-run external-only raw trajectory adapter; arrays stay ignored."""
import json,sys,hashlib,subprocess
from pathlib import Path
import numpy as np
from possession.external import load_match
from possession.inputs import Tracking
from possession.core import features,corrupt
R=Path('experiments/tcn-2026-11-10');OUT=Path('data/tcn-prepared')
sys.path.insert(0,str(R.resolve()))
from tcn_candidate import SLOTS,WIDTH
IDS=('J03WMX','J03WN1','J03WOH','J03WOY','J03WPY')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def authority():
 from datetime import datetime,date
 from zoneinfo import ZoneInfo
 if datetime.now(ZoneInfo('Asia/Kolkata')).date()>=date(2026,11,16):raise RuntimeError('Research closed at start of November16 freeze day')
 for p in [R/'protocol.md',R/'locked-inputs.json']:
  assert subprocess.check_output(['git','show','HEAD:'+str(p)])==p.read_bytes(),'Registration changed'
 for p,h in json.loads((R/'locked-inputs.json').read_text()).items():assert sha(p)==h,p
 from importlib.metadata import version
 for name,v in json.loads((R/'environment.json').read_text()).items():assert version(name)==v,'Dependency version changed: '+name
 assert tuple(json.loads(Path('experiments/core-development/split.json').read_text())['development'])==IDS

def encode(track,teams,blocks,core):
 n,p,_=track.players.shape
 if p>SLOTS-1 or set(teams.tolist())!={0,1}:raise ValueError('Unsupported player/team mapping')
 xy=np.full((n,SLOTS,2),np.nan,np.float32);xy[:,:p]=track.players[:,:,:2];xy[:,-1]=track.ball[:,:2]
 seen=np.isfinite(xy).all(-1);vel=np.zeros_like(xy)
 for a,b in blocks:
  valid=seen[a+1:b]&seen[a:b-1];vel[a+1:b]=np.where(valid[:,:,None],np.diff(xy[a:b],axis=0)*25,0)
 obj=np.zeros((n,SLOTS,8),np.float32);obj[:,:,:2]=np.where(seen[:,:,None],(xy-.5)*2,0);obj[:,:,2:4]=np.clip(vel,-5,5);obj[:,:,4]=seen
 obj[:,:p,5]=teams==0;obj[:,:p,6]=teams==1;obj[:,-1,7]=1
 globalx=core.copy();globalx[:,:5]/=100;globalx[:,8]=np.minimum(globalx[:,8],60)/60;globalx=np.nan_to_num(globalx,nan=0).astype(np.float32)
 out=np.column_stack([obj.reshape(n,-1),globalx]);assert out.shape==(n,WIDTH) and np.isfinite(out).all();return out

def main():
 authority();assert not OUT.exists(),'Prepared outputs already exist; review rather than overwrite';OUT.mkdir()
 manifest={};raw=json.loads((R/'raw-paths.json').read_text())
 for i,m in enumerate(IDS):
  import xml.etree.ElementTree as ET
  for _,node in ET.iterparse(raw[m][1],events=('end',)):
   if node.tag=='FrameSet':
    if node.get('TeamId','').lower()!='ball' and node.get('GameSection') in ['firstHalf','secondHalf'] and not node.get('PersonId'):raise ValueError('Missing trajectory identity')
    node.clear()
  t,teams,bb,pitch,y=load_match(*raw[m]);d=np.load('data/external/prepared/'+m+'.npz');core,_=features(t,teams,bb,pitch)
  assert np.array_equal(y,d['y']) and np.array_equal(bb,d['blocks']) and np.allclose(core,d['x'],equal_nan=True,rtol=0,atol=0),'Clean alignment mismatch'
  # Identical pre-existing player corruption; raw ball missing mask from frozen target-like input.
  c=corrupt(t,bb,20261106+i);xc=np.load('data/diagnostics-review/'+m+'-targetlike.npz')['x'];ball=t.ball.copy();ball[xc[:,5]==0]=np.nan;c=Tracking(c.players,ball)
  cc,_=features(c,teams,bb,pitch);assert np.allclose(cc,xc,equal_nan=True,rtol=0,atol=0),'Corruption reconstruction mismatch'
  for name,tr,cx in [('clean',t,core),('targetlike',c,cc)]:
   f=OUT/(m+'-'+name+'.npz');np.savez_compressed(f,x=encode(tr,teams,bb,cx),y=y,blocks=bb);manifest[str(f)]=sha(f)
  print('Prepared',m,flush=True)
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('Preparation complete; no fitting')
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true',required=True);parser.parse_args();main()
