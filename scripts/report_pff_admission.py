import json,hashlib
import numpy as np
from pathlib import Path
R=Path('experiments/pff-admission')
def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  while b:=f.read(8*1024**2):h.update(b)
 return h.hexdigest()
def main():
 for item in json.loads(Path('experiments/pff-intake/release-manifest.json').read_text()):
  if item['path'].startswith(('Tracking Data/','Metadata/','Rosters/')):assert digest(Path('data/pff/release')/item['path'])==item['sha256'],'Release file drift'
 snapshot=json.loads((R/'snapshot.json').read_text())
 for path,expected in snapshot.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected, 'Preparation source drift'
 rows=json.loads((R/'admission.json').read_text());assert len(rows)==64 and len({r['match'] for r in rows})==64;split=json.loads(Path('experiments/pff-intake/split.json').read_text());passed={r['match'] for r in rows if r['status']=='pass'}
 for m in passed:
  assert digest(Path('data/pff/features')/(m+'.npz'))==next(r['feature_sha256'] for r in rows if r['match']==m),'Feature cache drift'
  d=np.load(Path('data/pff/features')/(m+'.npz'));assert d['x'].shape==d['xc'].shape==(len(d['y']),9);assert not np.isinf(d['x']).any() and not np.isinf(d['xc']).any();assert np.isin(d['y'],['H','A','D','X']).all()
 cohort={'training':[m for m in split['pff_additional_training'] if m in passed],'transfer_holdout':[m for m in split['pff_transfer_holdout'] if m in passed],'excluded':[r for r in rows if r['status']!='pass'],'admission_sha256':hashlib.sha256((R/'admission.json').read_bytes()).hexdigest()};Path('experiments/pff-evaluation/cohort-lock.json').write_text(json.dumps(cohort,indent=2))
 lines=['# PFF full admission report','', 'Raw VISIBLE-only homePlayers/awayPlayers/balls. No smoothed/event-carrier-conditioned observation fields. CLK/VID and unsupported native-time gaps clear state/owner until fresh supported annotation. Missing ball does not remove valid labels. Standard halves only; full source/protocol/split fingerprints in snapshot.json. All matches attempted with no score-based cleanup or replacement.','','| Match | Status | Frames25Hz | Known fraction | Naturally missing graded | Synthetic-condition missing graded | Natural missing H | Natural missing A | Natural missing D |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
 for r in rows:
  if r['status']!='pass':lines.append(f"| {r['match']} | FAIL: {r['reason']} | | | | | | | |");continue
  t=r['label_by_natural_observation'];lines.append(f"| {r['match']} | pass | {r['frames']} | {r['known_fraction']:.6f} | {r['natural_missing_graded']} | {r['corrupted_missing_graded']} | {t['H']['missing']} | {t['A']['missing']} | {t['D']['missing']} |")
 good=[r for r in rows if r['status']=='pass'];totals={z:{v:sum(r['label_by_natural_observation'][z][v] for r in good) for v in ['visible','missing']} for z in ['H','A','D','X']};summary={'release_and_feature_hashes_verified':True,'attempted':64,'passed':len(good),'failed':64-len(good),'training_admitted':len(cohort['training']),'transfer_admitted':len(cohort['transfer_holdout']),'label_by_natural_observation':totals,'preparation_script_sha256':hashlib.sha256(Path('scripts/prepare_pff_admission.py').read_bytes()).hexdigest(),'inference_label_cleanup_chosen_by_score':False};(R/'summary.json').write_text(json.dumps(summary,indent=2));lines+=['','Aggregate label-by-observation support:','```json',json.dumps(summary,indent=2),'```','','Conflicts are separate finite-coordinate vs presence/missing disagreements, including within-list repeats, in admission.json. Conservative disagreement masks are not proof of source error. PFFteacherlabels remain provider-event conventions, not verified equivalence to IDSSE/target. Positive admission proves tested contracts, not transfer quality. No models fitted before this report/cohort lock.'];(R/'report.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
