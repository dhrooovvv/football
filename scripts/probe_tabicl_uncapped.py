"""User-authorized CPU admission: observe resources without imposing caps."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
import sys,time,json,hashlib,subprocess
from pathlib import Path
R=Path('experiments/tabicl-uncapped-2026-11-08')
if '--worker' in sys.argv:
 import probe_tabicl
 probe_tabicl.R=R
 probe_tabicl.worker('actual')
else:
 import psutil
 meta=json.loads(Path('experiments/tabicl-2026-11-08/weight-source.json').read_text());assert hashlib.sha256(Path('data/tabicl/model.ckpt').read_bytes()).hexdigest()==meta['sha256'];(R/'weight-source.json').write_text(json.dumps(meta,indent=2))
 with (R/'actual.log').open('w') as log:
  start=time.monotonic();p=subprocess.Popen([sys.executable,__file__,'--worker'],stdout=log,stderr=subprocess.STDOUT);peak=0;minimum=psutil.virtual_memory().available;last=0
  while p.poll() is None:
   try:peak=max(peak,psutil.Process(p.pid).memory_info().rss)
   except psutil.NoSuchProcess:pass
   minimum=min(minimum,psutil.virtual_memory().available);elapsed=time.monotonic()-start
   if elapsed-last>=30:
    last=elapsed;print(json.dumps(dict(elapsed_seconds=elapsed,observed_peak_rss_bytes=peak,min_available_bytes=minimum)),flush=True)
   time.sleep(.25)
 result=dict(exit_code=p.returncode,reason=None if p.returncode==0 else 'worker error or OS termination; inspect log',wall_seconds=time.monotonic()-start,observed_peak_rss_bytes=peak,min_observed_system_available_bytes=minimum,passed=p.returncode==0,experiment_resource_caps=False)
 (R/'admission.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
