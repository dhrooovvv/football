import concurrent.futures,hashlib,json,urllib.request
from pathlib import Path
root=Path('data/external'); root.mkdir(parents=True,exist_ok=True)
split=json.loads(Path('experiments/core-development/split.json').read_text())
manifest=json.loads(urllib.request.urlopen('https://api.figshare.com/v2/articles/28196177').read())
files=[f for f in manifest['files'] if any('DFL-MAT-'+m+'.xml' in f['name'] for m in split['development']) and ('positions_raw' in f['name'] or 'matchinformation' in f['name'])]
def fetch(f):
 p=root/f['name']
 if not p.exists():
  temp=p.with_suffix('.partial')
  urllib.request.urlretrieve(f['download_url'],temp)
  if temp.stat().st_size!=f['size']: raise ValueError('size mismatch')
  temp.rename(p)
 h=hashlib.md5()
 with p.open('rb') as s:
  while b:=s.read(8*1024**2): h.update(b)
 if h.hexdigest()!=f['computed_md5']: raise ValueError('checksum mismatch')
 return {'name':f['name'],'md5':h.hexdigest(),'url':f['download_url']}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 results=list(pool.map(fetch,files))
(root/'manifest.json').write_text(json.dumps(results,indent=2))
print('Downloaded and verified development files only:',len(results))
