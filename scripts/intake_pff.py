"""PFF release inventory, source hashes and schema-only audit; never train or score."""
import json,hashlib,bz2,zipfile
from pathlib import Path
R=Path('experiments/pff-intake');DATA=Path('data/pff/release')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while b:=f.read(8*1024**2):h.update(b)
 return h.hexdigest()
def main():
 manifest=[]
 for p in sorted(DATA.rglob('*')):
  if p.is_file():manifest.append({'path':str(p.relative_to(DATA)),'bytes':p.stat().st_size,'sha256':sha(p)})
 files={p.name.split('.')[0]:p for p in (DATA/'Tracking Data').glob('*.bz2')};meta={p.stem:p for p in (DATA/'Metadata').glob('*.json')};rosters={p.stem:p for p in (DATA/'Rosters').glob('*.json')};assert len(files)==64 and set(files)==set(meta)==set(rosters)
 schema=[];rates=[]
 for mid,p in sorted(files.items()):
  m=json.loads(meta[mid].read_text());assert isinstance(m,list) and len(m)==1;m=m[0];assert str(m['id'])==mid
  with bz2.open(p,'rt') as f:record=json.loads(next(f))
  framekeys=sorted(record);eventkeys=sorted((record.get('game_event') or {}).keys());pitch=m['stadium']['pitches'][0];fps=float(m['fps']);assert fps>0 and pitch['length']>0 and pitch['width']>0
  schema.append({'match':mid,'fps':fps,'pitch_m':[pitch['length'],pitch['width']],'frame_fields':framekeys,'first_record_event_fields':eventkeys,'metadata_roster_tracking_present':True});rates.append(fps)
 ids=sorted(files,key=lambda m:hashlib.sha256(('pff2022-split-20261107:'+m).encode()).hexdigest());split={'seed':20261107,'method':'ascending SHA256(pff2022-split-20261107:+matchID),first48train,last16transfer','pff_additional_training':ids[:48],'pff_transfer_holdout':ids[48:],'idsse_development':['J03WMX','J03WN1','J03WOH','J03WOY','J03WPY'],'idsse_sealed_excluded_from_all_training':['J03WQQ','J03WR9'],'performance_used_to_choose_split':False,'eligibility':'prospective; admission requires full state coverage/adapter validation before any modelling'}
 (R/'release-manifest.json').write_text(json.dumps(manifest,indent=2));(R/'split.json').write_text(json.dumps(split,indent=2));(R/'schema-audit.json').write_text(json.dumps(schema,indent=2));record={'archive_sha256':sha(Path('/Users/dhruv/Downloads/Archive 2.zip')),'delivered_release_files':len(manifest),'tracking_matches':64,'matching_metadata':64,'matching_rosters':64,'native_fps_values':sorted(set(rates)),'manifest_sha256':sha(R/'release-manifest.json'),'split_sha256':sha(R/'split.json'),'training_executed':False,'full_state_coverage_validated':False};(R/'intake.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
if __name__=='__main__':main()
