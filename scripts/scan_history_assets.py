"""Full reachable Git history asset scan; report path/commit only, never contents."""
import subprocess,json,re
from pathlib import Path
run=lambda *a:subprocess.check_output(['git',*a])
commits=run('rev-list','--all').decode().split();cache={};hits=set()
for commit in commits:
 for line in run('ls-tree','-r','-z',commit).split(b'\0'):
  if not line:continue
  meta,path=line.split(b'\t',1);mode,kind,oid=meta.split();path=path.decode();key=oid.decode()
  if key not in cache:
   data=run('cat-file','blob',key)
   binary=data.startswith((b'\x93NUMPY',b'PK\x03\x04',b'PAR1')) or b'ftyp' in data[:20]
   framecsv=bool(re.match(rb'frame,label\r?\n(?:0,[HADX]\r?\n)',data))
   raw=bool(re.search(rb'(?m)^\d+:(?:NaN|[-0-9.]+),[^\n]+:',data))
   cache[key]=binary or framecsv or raw
  suspicious=bool(re.search(r'\.(mp4|mov|npz|npy|parquet|zip|cbm|bz2|gz)$',path,re.I)) or bool(re.search(r'(^|/)(BAR-ATH[^/]*\.(xml|txt|csv)|candidate(?:-repeat)?\.csv)$',path,re.I)) or cache[key]
  if suspicious:hits.add((path,commit))
R=Path('experiments/extension-2026-11-07');report={'scope':'all commits reachable from all local refs; every unique blob read locally; filename/binary/raw-ATD/frame-CSV signatures; no contents reported','commits_scanned':len(commits),'unique_blobs_scanned':len(cache),'findings':[{'path':p,'commit':c} for p,c in sorted(hits)],'limitations':'Signature scan is not proof against arbitrary transformed/embedded derivatives; ordinary narrative aggregates/configuration are intentionally allowed.'};(R/'history-leak-scan.json').write_text(json.dumps(report,indent=2));print('History scan complete. Findings:',len(hits))
