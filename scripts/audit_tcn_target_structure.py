"""User-run label-free target/external geometry qualification; no model or scoring."""
import argparse
from datetime import date, datetime
import fcntl
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

PROJECT=Path(__file__).resolve().parents[1]
ROOT=Path('experiments/tcn-target-structure-2026-11-12')
OUT=Path('data/competition/tcn-target-structure')
IDS=('J03WMX','J03WN1','J03WOH','J03WOY','J03WPY')
TARGET=('data/competition/tactical/BAR-ATH_tactical_atd.txt',
        'data/competition/tactical/BAR-ATH_tactical_atd.xml')
DIAGNOSTIC=Path('experiments/tcn-winner-slot-audit-2026-11-12')
ENVIRONMENT=Path('experiments/tcn-winner-release-2026-11-12/environment-snapshot.json')
ACTIVE_OUTPUT=False


def require(ok,message):
    if not ok:raise RuntimeError(message)


def sha(path):
    result=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024**2),b''):result.update(block)
    return result.hexdigest()


def write_json(path,value):
    temporary=Path(path).with_suffix('.tmp')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    temporary.replace(path)


def check_date():
    require(datetime.now(ZoneInfo('Asia/Kolkata')).date()<date(2026,11,16),
            'Input qualification closes at the start of November16')


def registration():
    check_date()
    lock=json.loads((ROOT/'inputs.json').read_text())
    require(set(lock)=={'code','data','evidence'},'Unexpected structure registration')
    mandatory=['scripts/audit_tcn_target_structure.py',str(ROOT/'protocol.md'),str(ROOT/'structure.py'),
               str(ROOT/'tests/test_structure.py'),str(ROOT/'requirements.txt'),
               str(ROOT/'external-pitch-scales.json'),'docs/run-tcn-target-structure.md',
               'src/possession/inputs.py','scripts/prepare_tcn.py','configs/competition.json',
               'experiments/core-development/split.json',str(ENVIRONMENT)]
    require(all(path in lock['code'] for path in mandatory),'Incomplete source registration')
    scales=json.loads((ROOT/'external-pitch-scales.json').read_text())
    require(set(scales)==set(IDS),'Exactly five external pitch scales required')
    geometry={f'data/tcn-expanded/idsse-{match}/{member}' for match in IDS
              for member in ('objects.npy','roles.npy','metadata.json')}
    metadata={scales[match]['metadata_path'] for match in IDS}
    require(set(lock['data'])==set(TARGET)|geometry|metadata,'Unexpected geometry input set')
    evidence={str(DIAGNOSTIC/name) for name in ('decision.json','inputs.json','results.json','controls.json','determinism.json')}
    require(set(lock['evidence'])==evidence,'Current-winner stress evidence not pinned')
    for match in IDS:
        item=scales[match]
        require(set(item)=={'pitch_metres','metadata_path','metadata_sha256'}
                and lock['data'][item['metadata_path']]==item['metadata_sha256'],
                'External physical pitch provenance differs')
    for group,files in lock.items():
        for name,digest in files.items():
            require(not Path(name).is_absolute() and '..' not in Path(name).parts,'Unsafe registered path')
            require(sha(name)==digest,'Registered file bytes changed: '+name)
            if group=='code':
                saved=subprocess.run(['git','show','HEAD:'+name],capture_output=True)
                require(saved.returncode==0 and hashlib.sha256(saved.stdout).hexdigest()==digest,
                        'Structure source must be committed: '+name)
    saved=subprocess.run(['git','show','HEAD:'+str(ROOT/'inputs.json')],capture_output=True)
    require(saved.returncode==0 and saved.stdout==(ROOT/'inputs.json').read_bytes(),
            'Commit the input registration before execution')
    split=json.loads(Path('experiments/core-development/split.json').read_text())
    require(split['development']==list(IDS) and set(split['sealed'])=={'J03WQQ','J03WR9'},'Protected split changed')
    environment=json.loads(ENVIRONMENT.read_text())
    require(platform.python_version()==environment['python'] and platform.system()==environment['system']
            and platform.machine()==environment['machine'],'Registered Python/platform differs')
    require(version('numpy')==environment['packages']['numpy'],'Numpy version differs')
    decision=json.loads((DIAGNOSTIC/'decision.json').read_text())
    require(decision['completed'] and decision['winner']=='control40k_reset_rotation_penalty16'
            and decision['parent_reproduced'] and decision['repeatability_passed']
            and decision['static_controls_within_tolerance'] and decision['diagnostic_only']
            and not decision['quality_selection_performed'],'Reviewed stress source differs')
    for field,name in (('inputs_sha256','inputs.json'),('results_sha256','results.json'),
                       ('controls_sha256','controls.json'),('determinism_sha256','determinism.json')):
        require(decision[field]==sha(DIAGNOSTIC/name),'Stress evidence differs from completed decision')
    return lock,scales,environment


def contracts():
    with (ROOT/'checks.txt').open('w') as log:
        process=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-v'],
                               stdout=log,stderr=subprocess.STDOUT)
    require(process.returncode==0,'Synthetic structure contracts failed; retain checks.txt')


def target_case(summarize,np):
    from possession.inputs import load_atd,load_teams
    config=json.loads(Path('configs/competition.json').read_text())
    source=config['sources']['tactical'];blocks=config['tactical_half_open_blocks']
    require(config['game']=='BAR-ATH' and config['fps']==25 and config['pitch_metres']==[105.3,68.]
            and config['home_team']=='Barcelona' and config['away_team']=='Atletic Club'
            and source==dict(frames=199319,slots=46)
            and blocks==[[11185,90652],[110808,190198]],'Frozen target contract differs')
    # The original strict parser reads locally. Its errors contain no raw rows.
    track=load_atd(TARGET[0],source['frames'],source['slots'])
    teams=load_teams(TARGET[1],source['slots'],config['home_team'],config['away_team'])
    def read(start,stop):
        raw=np.asarray(track.players[start:stop,:,:2],dtype=np.float32)
        seen=np.isfinite(raw).all(-1)
        # Match the stored external representation's centeredfloat32 quantization.
        centered=np.where(seen[:,:,None],(raw-np.float32(.5))*np.float32(2.),0)
        return (centered+np.float32(1.))*np.float32(.5),seen
    result=summarize(source['frames'],teams,blocks,config['pitch_metres'],read)
    del track
    return result


def external_case(match,scale,summarize,np):
    directory=Path('data/tcn-expanded')/('idsse-'+match)
    metadata=json.loads((directory/'metadata.json').read_text())
    require(metadata['provider']=='idsse' and metadata['key']=='idsse-'+match and metadata['match']==match,
            'External geometry membership differs')
    objects=np.load(directory/'objects.npy',mmap_mode='r',allow_pickle=False)
    roles=np.load(directory/'roles.npy',allow_pickle=False)
    require(objects.shape==(metadata['frames'],64,5) and objects.dtype==np.float32
            and roles.shape==(64,3) and np.isin(roles,[0,1]).all()
            and (roles.sum(1)<=1).all() and np.array_equal(roles[-1],[0,0,1])
            and not roles[:-1,2].any(),'External geometry/role schema differs')
    slots=np.flatnonzero(roles[:63,:2].sum(1)==1)
    teams=np.argmax(roles[slots,:2],axis=1).astype(np.int8)
    def read(start,stop):
        values=objects[start:stop,slots]
        require(np.isfinite(values).all() and np.isin(values[:,:,4],[0,1]).all(),
                'Invalid external observation values')
        # Invert the stored centered encoding; float32 roundoff is disclosed.
        xy=(values[:,:,:2]+np.float32(1.))*np.float32(.5)
        return xy,values[:,:,4]==1
    result=summarize(metadata['frames'],teams,metadata['blocks'],scale['pitch_metres'],read)
    del objects,roles
    return result


def report(rows):
    text='# Label-free input structure comparison\n\n'
    text+='Descriptive geometry only. No model, labels, scoring, identity estimates or repair. Physical pitch scales are provider-specific.\n\n'
    text+='|Case|Team|Allocated slots|Visible slot count mean|Same-slot step mean(m)|Nearest mean for same pairs(m)|Clipping proxy share|Exact-close frame share|\n'
    text+='|---|---|---:|---:|---:|---:|---:|---:|\n'
    def number(value):return 'NA' if value is None else f'{value:.6f}'
    for case,value in rows.items():
        for team,item in value['teams'].items():
            text+=f"|{case}|{team}|{item['allocated_player_slots']}|{number(item['visible_slot_count']['mean'])}|{number(item['adjacent_observed_same_slot_displacement']['mean_m'])}|{number(item['nearest_previous_set_for_same_slot_observed_pairs']['mean_m'])}|{number(item['encoder_velocity_clipping_proxy']['any_component_exceeds_abs5_fraction'])}|{number(item['same_team_close_position_proxies']['thresholds'][0]['frame_fraction'])}|\n"
    text+='\nFull aggregate quantile intervals, fixed bins, appearance/disappearance/run lengths, same-pair nearest contrast and close-pair thresholds are in summaries.json. All half-edge run fragments are retained and marked censored; initial appearance and half-end disappearance are not counted as observed transitions.\n\n'
    text+='Nearest set distances are directed many-to-one proxies, not person matching or identity truth. Close positions can be real teammates in proximity or quantization, so no duplicate-track rate is inferred; visible slots are not verified unique players. Allocated team slot capacities differ between providers; pooled missing-run distributions include inactive/replacement slots. Both sources use centeredfloat32 encoding and reconstruct normalizedXY from it; this adds rounding relative to the original encoder velocity calculation. Clipping is the rederived abs(normalizedXYdiff*25)>5 proxy, not an exact audit of pre-rounded source velocities. Zero clipping does not establish continuity: this threshold permits0.2 normalized pitch-axis units per25Hz step. Quantiles use fixed0.01m histogram intervals; >=200m is an open upper tail. No cutoff is a release-quality or identity-switch threshold; target accuracy remains unknown.\n'
    return text


def main():
    global ACTIVE_OUTPUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true',required=True);parser.parse_args()
    os.chdir(PROJECT);lock,scales,environment=registration()
    handle=(OUT.parent/'tcn-target-structure.operation.lock').open('a+')
    try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError as error:raise RuntimeError('A structure diagnostic is already active') from error
    require(not OUT.exists(),'Existing attempt; preserve it for review')
    contracts()
    sys.path[:0]=[str(PROJECT/'src'),str(PROJECT/ROOT)]
    import numpy as np
    from structure import summarize
    OUT.mkdir()
    ACTIVE_OUTPUT=True
    started=time.monotonic()
    commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    write_json(OUT/'started.json',dict(git_commit=commit,inputs_sha256=sha(ROOT/'inputs.json'),
        timestamp=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),label_free=True,
        model_executed=False,scoring_executed=False,training_executed=False))
    rows={};timings={}
    for case in ('target',*IDS):
        check_date();case_start=time.monotonic()
        rows[case]=target_case(summarize,np) if case=='target' else external_case(case,scales[case],summarize,np)
        timings[case]=time.monotonic()-case_start
        write_json(OUT/'summaries.json',rows)
        print('Completed aggregate geometry case',case,flush=True)
    for files in lock.values():
        for name,digest in files.items():require(sha(name)==digest,'Input bytes changed during diagnostic')
    require(set(rows)=={'target',*IDS},'Incomplete structure comparison')
    (OUT/'report.md').write_text(report(rows))
    write_json(OUT/'provenance.json',dict(completed=True,label_free=True,git_commit=commit,
        inputs_sha256=sha(ROOT/'inputs.json'),protocol_sha256=sha(ROOT/'protocol.md'),
        stress_decision_sha256=sha(DIAGNOSTIC/'decision.json'),summary_sha256=sha(OUT/'summaries.json'),
        source_hashes=lock,environment_python=environment['python'],numpy=version('numpy'),
        chunk_frames=256,case_count=6,synthetic_contracts_pass=True,
        model_executed=False,scoring_executed=False,training_executed=False,
        public_labels_read=False,protected_matches_read=False,quality_selection_performed=False,
        identity_switch_rate_estimated=False,production_changed=False,target_accuracy='unknown',
        case_seconds=timings,total_seconds=time.monotonic()-started))
    print('Structure comparison complete. Review private aggregate report before release.',flush=True)


if __name__=='__main__':
    try:main()
    except Exception as error:
        os.chdir(PROJECT)
        # Error messages are fixed contracts; no asset values or rows are included.
        destination=OUT/'last-failure.json' if ACTIVE_OUTPUT else ROOT/'last-failure.json'
        message=str(error) if isinstance(error,RuntimeError) else 'Local geometry reader or aggregation failed; retain evidence for source review.'
        write_json(destination,dict(error_type=type(error).__name__,message=message,
                                   production_changed=False))
        raise RuntimeError('Structure diagnostic failed; retain the attempt and review its failure record.') from None
