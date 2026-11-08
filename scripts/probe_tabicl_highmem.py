"""Authorized single higher-memory admission. No quality scoring."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[k]='1'
import sys,time,json,hashlib,subprocess
from pathlib import Path
R=Path(sys.argv[sys.argv.index('--output')+1]) if '--output' in sys.argv else Path('experiments/tabicl-highmem-2026-11-08')
if '--worker' in sys.argv:
 import probe_tabicl
 probe_tabicl.R=R
 probe_tabicl.worker('actual')
else:
 import psutil
 meta=json.loads(Path('experiments/tabicl-2026-11-08/weight-source.json').read_text())
 assert hashlib.sha256(Path('data/tabicl/model.ckpt').read_bytes()).hexdigest()==meta['sha256']
 (R/'weight-source.json').write_text(json.dumps(meta,indent=2))
 with (R/'actual.log').open('w') as log:
  start=time.monotonic();p=subprocess.Popen([sys.executable,__file__,'--worker','--output',str(R)],stdout=log,stderr=subprocess.STDOUT);peak=0;minavailable=psutil.virtual_memory().available;reason=None
  while p.poll() is None:
   try:peak=max(peak,psutil.Process(p.pid).memory_info().rss)
   except psutil.NoSuchProcess:pass
   available=psutil.virtual_memory().available;minavailable=min(minavailable,available)
   if time.monotonic()-start>300:reason='300 second cap'
   if peak>10*1024**3:reason='10 GiB process RSS cap'
   if available<3*1024**3:reason='3 GiB system available-memory floor'
   if reason:p.terminate();p.wait(timeout=10);break
   time.sleep(.25)
 result=dict(exit_code=p.returncode,reason=reason,wall_seconds=time.monotonic()-start,observed_peak_rss_bytes=peak,min_observed_system_available_bytes=minavailable,passed=p.returncode==0 and reason is None)
 (R/'admission.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
