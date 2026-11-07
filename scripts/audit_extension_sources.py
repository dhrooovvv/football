"""Download documentation/schema only; no competition data or sealed data."""
from pathlib import Path
import urllib.request,json,hashlib
R=Path('experiments/extension-2026-11-07');D=Path('data/extension-audit');D.mkdir(exist_ok=True)
def fetch(url,name):
 try:
  data=urllib.request.urlopen(url,timeout=45).read();(D/name).write_bytes(data);return data
 except Exception as e:print(name,type(e).__name__);return None
for repo in ['SkillCorner/opendata','PySport/kloppy','metrica-sports/sample-data']:
 tree=fetch('https://api.github.com/repos/'+repo+'/git/trees/HEAD?recursive=1',repo.split('/')[0]+'-tree.json')
 if tree:
  a=json.loads(tree);paths=[x['path'] for x in a.get('tree',[]) if x['type']=='blob'];print(repo,a.get('sha'))
  for p in paths:
   if repo.startswith('Skill') and (('matches/' in p and p.endswith('_match.json')) or 'phases' in p or p in ['LICENSE','README.md']): print(p)
   if repo.startswith('PySport') and 'pff' in p and ('deserial' in p or 'tracking' in p):print(p)
for url,name in [('https://raw.githubusercontent.com/SkillCorner/opendata/master/README.md','skillcorner-readme.md'),('https://raw.githubusercontent.com/SkillCorner/opendata/master/LICENSE','skillcorner-license.txt'),('https://raw.githubusercontent.com/metrica-sports/sample-data/master/README.md','metrica-readme.md'),('https://api.figshare.com/v2/articles/28196177','idsse-manifest.json')]:fetch(url,name)
