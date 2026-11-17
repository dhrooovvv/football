"""User-run fixed extra-training control and masked-geometry pretraining comparison."""
import argparse
from contextlib import contextmanager
from datetime import date, datetime
import fcntl
import hashlib
from importlib.metadata import version
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

PROJECT = Path(__file__).resolve().parents[1]
R = Path('experiments/tcn-pretrain-2026-11-11')
DATA = Path('data/tcn-pretrain')
MODELS = Path('models/tcn-pretrain/evaluation')
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
SETTINGS = ('clean', 'targetlike')
STAGE_STEPS = 20000
TOTAL_STEPS = 2 * STAGE_STEPS


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b''):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def check_date():
    require(datetime.now(ZoneInfo('Asia/Kolkata')).date() < date(2026, 11, 16),
            'Research closes at the start of November16; preserve partial evidence.')


def expected_membership():
    split = json.loads(Path('experiments/core-development/split.json').read_text())
    cohort = json.loads(Path('experiments/pff-evaluation/cohort.json').read_text())
    require(tuple(split['development']) == IDS and len(cohort['training']) == 48,
            'Original development/PFF training split changed')
    require(not set(cohort['training']) & set(cohort['transfer_holdout']), 'PFF holdout overlap')
    return dict(development=list(IDS),
                supervised_folds={m: ['idsse-'+n for n in IDS if n != m] for m in IDS},
                geometry_folds={m: ['idsse-'+n for n in IDS if n != m]
                                + ['pff-'+n for n in cohort['training']] for m in IDS},
                pff_training=cohort['training'], sealed_excluded=split['sealed'],
                pff_transfer_holdout_excluded=cohort['transfer_holdout'], target_excluded=True,
                held_out_even_unlabelled_excluded=True, final_fit_enabled=False)


def registration():
    check_date()
    for path in (R/'protocol.md', R/'inputs.json', R/'membership.json'):
        saved = subprocess.run(['git','show','HEAD:'+str(path)], capture_output=True)
        require(saved.returncode == 0 and saved.stdout == path.read_bytes(),
                'Registration must be committed: '+str(path))
    locked = json.loads((R/'inputs.json').read_text())
    require(set(locked) == {'code','data','prepared_manifests'}, 'Unexpected lock schema')
    mandatory = ['scripts/run_tcn_pretrain.py', str(R/'protocol.md'), str(R/'membership.json'),
                 str(R/'requirements.txt'), str(R/'pretrain_model.py'), str(R/'pretrain_training.py'),
                 str(R/'pretrain_data.py'), str(R/'tests/test_pretrain_model.py'),
                 'experiments/tcn-2026-11-10/tcn_candidate.py',
                 'experiments/tcn-rotation-2026-11-11/rotation.py',
                 'experiments/core-development/split.json','experiments/pff-evaluation/cohort.json']
    require(all(name in locked['code'] for name in mandatory), 'Incomplete source registration')
    for group, items in locked.items():
        for name, digest in items.items():
            require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Unsafe source path')
            require(sha(name) == digest, 'Registered file changed: '+name)
            if group == 'code':
                tracked = subprocess.run(['git','ls-files','--error-unmatch','--',name], capture_output=True).returncode == 0
                if tracked or name in mandatory:
                    saved = subprocess.run(['git','show','HEAD:'+name], capture_output=True)
                    require(saved.returncode == 0 and hashlib.sha256(saved.stdout).hexdigest() == digest,
                            'Source differs from git: '+name)
    membership = json.loads((R/'membership.json').read_text())
    require(membership == expected_membership(), 'Membership differs from approved splits')
    keys = ['idsse-'+m for m in IDS] + ['pff-'+m for m in membership['pff_training']]
    require(set(locked['prepared_manifests']) == {f'data/tcn-expanded/{k}/manifest.json' for k in keys},
            'Exactly53eligible compact manifests required')
    required = ['experiments/tcn-rotation-2026-11-11/results.json']
    for match in IDS:
        for setting in SETTINGS:
            required += [f'data/tcn-prepared/{match}-{setting}.npz',
                         f'data/tcn-rotation/{match}-{setting}-first.csv']
    require(all(name in locked['data'] for name in required), 'Frozen evaluation reference missing')
    for package, expected in json.loads(Path('experiments/tcn-2026-11-10/environment.json').read_text()).items():
        require(version(package) == expected, 'Dependency version differs: '+package)
    signature = hashlib.sha256((sha(R/'protocol.md')+sha(R/'inputs.json')).encode()).hexdigest()
    return locked, membership, signature


def verify_frozen_inputs(locked):
    for items in locked.values():
        for name, digest in items.items():
            require(sha(name) == digest, 'Registered file changed during execution: '+name)
    expected = {'objects.npy','roles.npy','core.npy','gap_ball.npy','gap_core.npy','labels.npy','metadata.json'}
    for name in locked['prepared_manifests']:
        manifest = json.loads(Path(name).read_text())
        require(set(manifest) == {'files'} and set(manifest['files']) == expected,
                'Unexpected compact members: '+name)
        for member, digest in manifest['files'].items():
            require(sha(Path(name).parent/member) == digest, 'Compact member changed: '+member)


@contextmanager
def operation_lock():
    DATA.mkdir(parents=True, exist_ok=True); handles=[]
    try:
        for directory in (Path('data/tcn-expanded'), DATA):
            handle=(directory/'operation.lock').open('a+'); handles.append(handle)
            try: fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError('Another compact-data or pretraining operation is active') from error
        yield
    finally:
        for handle in reversed(handles): handle.close()


def run_checks():
    env=os.environ.copy()
    env['PYTHONPATH']=os.pathsep.join([str(PROJECT/'src'),str(PROJECT/'scripts'),env.get('PYTHONPATH','')])
    with (R/'checks.txt').open('w') as log:
        for suite in ('tests','experiments/tcn-2026-11-10/tests','experiments/tcn-gap-2026-11-10/tests',
                      'experiments/tcn-rotation-2026-11-11/tests',str(R/'tests')):
            log.write('\n'+suite+'\n');log.flush()
            result=subprocess.run([sys.executable,'-m','unittest','discover','-s',suite,'-v'],
                                  stdout=log,stderr=subprocess.STDOUT,env=env)
            require(result.returncode == 0, 'User-run contracts failed; preserve checks.txt')
    print('Integrated user-run checks passed.',flush=True)


def checkpoint_paths(arm, match):
    return [MODELS/arm/match/repeat/'progress.pt' for repeat in ('first','repeat')]


def verify_fold(arm, match, signature, architecture, parent_name, membership):
    path=R/'evaluation'/arm/(match+'.json')
    if not path.exists(): return None
    record=json.loads(path.read_text())
    require(record['registration']==signature and record['architecture']==architecture
            and record['arm']==arm and record['parent']==parent_name, 'Cached fold identity differs')
    expected_supervised=membership['supervised_folds'][match]
    expected_geometry=membership['geometry_folds'][match] if arm=='pretrain' else []
    require(record['training_matches']==expected_supervised and record['geometry_matches']==expected_geometry,
            'Cached fold membership differs')
    require(record['training_steps']==TOTAL_STEPS and record['repeated_training_exact'], 'Cached budget/repeat proof missing')
    durations=record['training_stage_seconds']
    require(set(durations)=={'first','repeat'} and all(set(v)=={'stage1','stage2'}
            and all(isinstance(n,(int,float)) and math.isfinite(n) and n>=0 for n in v.values())
            for v in durations.values()),'Cached stage timings invalid')
    coverage=record['coverage']
    require(set(coverage)=={'stage1','stage2'},'Invalid stage coverage')
    for stage in ('stage1','stage2'):
        expected=expected_geometry if arm=='pretrain' and stage=='stage1' else expected_supervised
        require(set(coverage[stage])==set(expected) and all(isinstance(v,int) and v>0 for v in coverage[stage].values())
                and sum(coverage[stage].values())==STAGE_STEPS*8, 'Cached sampling coverage differs')
    views=record['supervised_views']
    require(set(views)=={'stage1','stage2'},'Invalid supervised-view stages')
    for stage in ('stage1','stage2'):
        expected_draws=0 if arm=='pretrain' and stage=='stage1' else STAGE_STEPS*8
        require(set(views[stage])=={'clean','gap'} and all(isinstance(v,int) and v>=0 for v in views[stage].values())
                and sum(views[stage].values())==expected_draws,'Cached supervised views differ')
    loss=json.loads((R/'evaluation'/arm/(match+'-losses.json')).read_text())
    require(loss['not_validation_loss'] and len(loss['minibatch_losses'])==TOTAL_STEPS
            and all(math.isfinite(v) for v in loss['minibatch_losses'])
            and hashlib.sha256(json.dumps(loss['minibatch_losses']).encode()).hexdigest()==record['training_loss_sha256'],
            'Cached loss evidence differs')
    require(record['target_counts']['stage2']==0 and (record['target_counts']['stage1']>0 if arm=='pretrain'
            else record['target_counts']['stage1']==0),'Cached reconstruction targets differ')
    require(set(record['checkpoint_hashes'])=={str(p) for p in checkpoint_paths(arm,match)},'Checkpoint references differ')
    for name,digest in record['checkpoint_hashes'].items(): require(sha(name)==digest,'Checkpoint changed')
    rows=record['rows']
    require(len(rows)==2 and {(v['match'],v['condition']) for v in rows}=={(match,s) for s in SETTINGS},'Incomplete fold cells')
    for row in rows:
        require(row['reload_probabilities_equal'] and row['csv_bytes_equal_reload_batch4'],'Inference proof missing')
        require(len(row['csv_paths'])==3 and len(set(row['csv_paths']))==3,'Repeat CSV paths missing')
        for name in row['csv_paths']: require(sha(name)==row['csv_sha256'],'Prediction CSV changed')
        require(sha(row['parent_csv_path'])==row['parent_csv_sha256'],'Parent CSV changed')
        for variant in ('parent','candidate'):
            for metric in ('spellF1','macroF1'):
                value=row[variant][metric]
                require(isinstance(value,(int,float)) and math.isfinite(value) and 0<=value<=1,'Invalid saved metric')
    return record


def calculate_gate(rows,np,promote):
    require(len(rows)==10 and {(v['match'],v['condition']) for v in rows}=={(m,s) for m in IDS for s in SETTINGS},
            'Exactly ten unique match-condition cells required')
    def paired(arm):
        return {m:tuple(float(np.mean([v[arm][metric] for v in rows if v['match']==m]))
                        for metric in ('spellF1','macroF1')) for m in IDS}
    before,after=paired('parent'),paired('candidate')
    primary={v['match']:v['candidate']['spellF1']-v['parent']['spellF1'] for v in rows if v['condition']=='targetlike'}
    median=float(np.median(list(primary.values())));existing=promote(before,after,True)
    return dict(quality_eligible=bool(existing and median>=.01),existing_gate=existing,
                primary_median_delta=median,primary_deltas=primary,
                paired_spell_deltas={m:after[m][0]-before[m][0] for m in IDS},
                paired_macro_deltas={m:after[m][1]-before[m][1] for m in IDS},
                matches_improved=sum(after[m][0]>before[m][0] for m in IDS),
                contract_checks_passed=True,repeated_training_exact=True,csv_repeatability_cases=10,
                clean_environment_verified=False,production_changed=False,sealed_opened=False,pff_holdout_opened=False)


def rotation_parent():
    rows=json.loads(Path('experiments/tcn-rotation-2026-11-11/results.json').read_text())
    require(len(rows)==10,'Rotation archive incomplete')
    return {(v['match'],v['condition']):dict(score=v,csv=f"data/tcn-rotation/{v['match']}-{v['condition']}-first.csv") for v in rows}


def arm_parent(rows):
    return {(v['match'],v['condition']):dict(score=v['candidate'],csv=v['csv_paths'][0]) for v in rows}


def evaluate_arm(arm,parent_name,parents,rotation,control,membership,signature,supervised,np,torch,
                 model_code,train_fit,confirm_repeat,GeometryCase,eligible_starts,score,missing,decode,
                 export_labels,promote,rotate180,average_views,locked):
    directory=R/'evaluation'/arm;directory.mkdir(parents=True,exist_ok=True)
    private=DATA/'predictions'/arm;private.mkdir(parents=True,exist_ok=True)
    scaler=np.zeros(model_code.WIDTH),np.ones(model_code.WIDTH);all_rows=[]
    for match in IDS:
        check_date()
        completed=verify_fold(arm,match,signature,model_code.ARCHITECTURE,parent_name,membership)
        if completed is not None:
            all_rows.extend(completed['rows']);print('Reused validated fold',arm,match,flush=True);continue
        started=time.monotonic()
        training=[case for case in supervised if case.key in membership['supervised_folds'][match]]
        require([v.key for v in training]==membership['supervised_folds'][match],'Supervised fold order differs')
        geometry=[GeometryCase(Path('data/tcn-expanded')/key) for key in membership['geometry_folds'][match]] if arm=='pretrain' else []
        require([v.key for v in geometry]==(membership['geometry_folds'][match] if arm=='pretrain' else []),
                'Geometry fold membership differs')
        geometry_counts={v.key:len(eligible_starts(v)) for v in geometry}
        require(all(n>0 for n in geometry_counts.values()),'Geometry match lacks eligible masked-observed targets')
        fits=MODELS/arm/match
        first,losses,coverage=train_fit(training,geometry,fits/'first',signature,arm=arm,held_out=match,
                                      stage_steps=STAGE_STEPS,allowed_pff=membership['pff_training'])
        check_date()
        second,repeat_losses,repeat_coverage=train_fit(training,geometry,fits/'repeat',signature,arm=arm,held_out=match,
                                                      stage_steps=STAGE_STEPS,allowed_pff=membership['pff_training'])
        confirm_repeat(first,second,losses,repeat_losses,coverage,repeat_coverage)
        saved=torch.load(fits/'first/progress.pt',map_location='cpu',weights_only=True)
        repeat_saved=torch.load(fits/'repeat/progress.pt',map_location='cpu',weights_only=True)
        require(saved['target_counts']==repeat_saved['target_counts'],'Repeated target counts differ')
        require(saved['supervised_views']==repeat_saved['supervised_views'],'Repeated supervised view counts differ')
        require(saved['step']==TOTAL_STEPS and saved['identity']['total_steps']==TOTAL_STEPS
                and saved['identity']['supervised_matches']==membership['supervised_folds'][match]
                and saved['identity']['geometry_matches']==([v.key for v in geometry]),
                'Checkpoint budget or membership differs')
        loaded=model_code.TCN().cpu().eval();loaded.load_state_dict(saved['state'],strict=True)
        held_case=next(c for c in supervised if c.key=='idsse-'+match);rows=[]
        for setting in SETTINGS:
            with np.load(f'data/tcn-prepared/{match}-{setting}.npz',allow_pickle=False) as case:
                x,labels,blocks=case['x'],case['y'],case['blocks'].tolist()
            require(x.shape==(len(labels),model_code.WIDTH) and blocks==held_case.blocks,'Held-out dimensions/halves differ')
            codes=np.array([{'H':0,'A':1,'D':2,'X':-1}[str(v)] for v in labels],np.int8)
            require(np.array_equal(codes,held_case.labels),'Held-out labels differ')
            parent_ref=parents[match,setting];parent=np.loadtxt(parent_ref['csv'],delimiter=',',skiprows=1,usecols=1,dtype=str)
            require(len(parent)==len(labels) and set(np.unique(parent))<=set('HADX'),'Parent CSV malformed')
            parent_score=score(labels,parent,blocks)
            for metric in ('spellF1','macroF1'):
                require(abs(parent_score[metric]-parent_ref['score'][metric])<=1e-12,'Parent metric does not reproduce')
            rotated=rotate180(x)
            p=model_code.predict(first,x,blocks,scaler);q=model_code.predict(first,rotated,blocks,scaler)
            pr=model_code.predict(loaded,x,blocks,scaler);qr=model_code.predict(loaded,rotated,blocks,scaler)
            require(np.array_equal(p,pr) and np.array_equal(q,qr),'Both-view reload probabilities differ')
            pb=average_views(model_code.predict(first,x,blocks,scaler,batch=4),model_code.predict(first,rotated,blocks,scaler,batch=4))
            probabilities=[average_views(p,q),average_views(pr,qr),pb]
            predictions=[decode(v,(1-np.eye(3))*16,blocks) for v in probabilities]
            paths=[private/f'{match}-{setting}-{tag}.csv' for tag in ('first','reload','batch4')]
            for path,pred in zip(paths,predictions):export_labels(path,pred,len(labels))
            digests=[sha(path) for path in paths];require(len(set(digests))==1,'Decoded CSV bytes differ')
            candidate=score(labels,predictions[0],blocks)
            rows.append(dict(match=match,condition=setting,parent=parent_score,candidate=candidate,
                             rotation_reference=rotation[match,setting]['score'],
                             control_reference=control[match,setting]['score'] if control is not None else None,
                             parent_missing_ball=missing(labels,parent,x[:,-4]==0),
                             candidate_missing_ball=missing(labels,predictions[0],x[:,-4]==0),
                             parent_csv_path=parent_ref['csv'],parent_csv_sha256=sha(parent_ref['csv']),
                             csv_paths=[str(p) for p in paths],csv_sha256=digests[0],
                             reload_probabilities_equal=True,csv_bytes_equal_reload_batch4=True))
        record=dict(registration=signature,architecture=model_code.ARCHITECTURE,arm=arm,parent=parent_name,
                    training_matches=[v.key for v in training],geometry_matches=[v.key for v in geometry],
                    geometry_eligible_starts=geometry_counts,training_steps=TOTAL_STEPS,stage_steps=STAGE_STEPS,
                    repeated_training_exact=True,coverage=coverage,target_counts=saved['target_counts'],supervised_views=saved['supervised_views'],
                    training_stage_seconds={'first':saved['stage_seconds'],'repeat':repeat_saved['stage_seconds']},
                    training_loss_sha256=hashlib.sha256(json.dumps(losses).encode()).hexdigest(),
                    checkpoint_hashes={str(p):sha(p) for p in checkpoint_paths(arm,match)},rows=rows,
                    seconds=time.monotonic()-started)
        write_json(directory/(match+'-losses.json'),dict(minibatch_losses=losses,not_validation_loss=True,
                   stage1_objective='masked_ball_XY_MSE' if arm=='pretrain' else 'possession_crossentropy',
                   stage2_objective='possession_crossentropy'))
        write_json(directory/(match+'.json'),record);all_rows.extend(rows)
        print('Completed',arm,match,flush=True)
        # Drop52mapping bundles before constructing the next fold's geometry.
        del geometry,first,second,loaded,saved,repeat_saved
    require(all_rows==[v for m in IDS for v in verify_fold(arm,m,signature,model_code.ARCHITECTURE,parent_name,membership)['rows']],
            'Aggregate/cached fold rows differ')
    verify_frozen_inputs(locked)
    gate=calculate_gate(all_rows,np,promote)
    write_json(directory/'results.json',all_rows);write_json(directory/'gate.json',gate)
    require(calculate_gate(json.loads((directory/'results.json').read_text()),np,promote)==gate,'Saved gate differs')
    report=f'# {arm} comparison against {parent_name}\n\n|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|\n|---|---|---:|---:|---:|---:|\n'
    for row in all_rows:
        a,b=row['parent'],row['candidate'];report+=f"|{row['match']}|{row['condition']}|{a['spellF1']:.6f}|{b['spellF1']:.6f}|{a['macroF1']:.6f}|{b['macroF1']:.6f}|\n"
    (directory/'report.md').write_text(report+'\n```json\n'+json.dumps(gate,indent=2)+'\n```\n')
    with Path('ball.md').open('a') as journal:
        journal.write('\nFixed pretraining-route '+arm+' comparison recorded against '+parent_name+'; production unchanged. '+json.dumps(gate)+'\n')
    return all_rows,gate


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',action='store_true',required=True);parser.parse_args()
    os.chdir(PROJECT);locked,membership,signature=registration()
    with operation_lock():
        run_checks();verify_frozen_inputs(locked)
        sys.path[:0]=[str(PROJECT/'src'),str(PROJECT/'scripts'),str(PROJECT/R),
                      str(PROJECT/'experiments/tcn-expanded-2026-11-10'),str(PROJECT/'experiments/tcn-rotation-2026-11-11')]
        import numpy as np
        import torch
        import pretrain_model as model_code
        from pretrain_training import train_fit,confirm_repeat
        from pretrain_data import GeometryCase,eligible_starts
        from expanded_data import CompactCase
        from possession.core import promote
        from possession.decode import decode
        from possession.inputs import export_labels
        from rotation import rotate180,average_views
        from review_frozen import score
        from evaluate_pff import missing
        model_code.configure()
        supervised=[CompactCase(Path('data/tcn-expanded')/('idsse-'+m)) for m in IDS]
        require([v.key for v in supervised]==['idsse-'+m for m in IDS],'Supervised cases differ')
        rotation=rotation_parent()
        args=(membership,signature,supervised,np,torch,model_code,train_fit,confirm_repeat,GeometryCase,
              eligible_starts,score,missing,decode,export_labels,promote,rotate180,average_views,locked)
        control_rows,control_gate=evaluate_arm('control','rotation20k',rotation,rotation,None,*args)
        control=arm_parent(control_rows)
        parent_name='control40k_reset' if control_gate['quality_eligible'] else 'rotation20k'
        parent=control if control_gate['quality_eligible'] else rotation
        pretrain_rows,pretrain_gate=evaluate_arm('pretrain',parent_name,parent,rotation,control,*args)
        retained='pretrain20k_finetune20k' if pretrain_gate['quality_eligible'] else parent_name
        cost={arm:sum(json.loads((R/'evaluation'/arm/(m+'.json')).read_text())['seconds'] for m in IDS)
              for arm in ('control','pretrain')}
        training_cost={arm:{repeat:{stage:sum(json.loads((R/'evaluation'/arm/(m+'.json')).read_text())['training_stage_seconds'][repeat][stage]
                         for m in IDS) for stage in ('stage1','stage2')} for repeat in ('first','repeat')}
                         for arm in ('control','pretrain')}
        write_json(R/'cost.json',dict(fold_stage_seconds=cost,training_stage_seconds=training_cost,total_updates_per_fit=TOTAL_STEPS,
                   maximum_fit_pipelines=20,updates_matched=True,exact_compute_matched=False,
                   note='Walltime includes repeated fits and inference; pretext/supervised update costs differ.'))
        contrasts={}
        for reference in ('rotation_reference','control_reference'):
            contrast_rows=[dict(match=row['match'],condition=row['condition'],
                                parent=row[reference],candidate=row['candidate']) for row in pretrain_rows]
            contrasts[reference]=calculate_gate(contrast_rows,np,promote)
        write_json(R/'diagnostic-contrasts.json',dict(not_alternate_selection=True,comparisons=contrasts))
        summary='# Fixed pretraining route: final development decision\n\n'
        summary+='Retained recipe: '+retained+'. Production unchanged; target accuracy unknown.\n\n'
        summary+='|Arm|Setting|Mean spellF1|Mean macroF1|\n|---|---|---:|---:|\n'
        for label,group in [('rotation20k',[value['score'] | dict(condition=key[1]) for key,value in rotation.items()]),
                            ('control40k_reset',[row['candidate'] | dict(condition=row['condition']) for row in control_rows]),
                            ('pretrain20k_finetune20k',[row['candidate'] | dict(condition=row['condition']) for row in pretrain_rows])]:
            for setting in SETTINGS:
                selected=[row for row in group if row['condition']==setting]
                summary+=f"|{label}|{setting}|{np.mean([row['spellF1'] for row in selected]):.6f}|{np.mean([row['macroF1'] for row in selected]):.6f}|\n"
        summary+='\nControl gate and actual-parent pretraining gate are the sequential decisions. diagnostic-contrasts.json preserves both comparisons without selecting an alternate parent after results. Full per-match metrics/errors/missing-ball quality are in each arm evaluation folder. Costs are update-matched, not exact compute-matched.\n'
        (R/'report.md').write_text(summary)
        write_json(R/'decision.json',dict(retained_development_candidate=retained,
                   control_quality_eligible=control_gate['quality_eligible'],pretrain_quality_eligible=pretrain_gate['quality_eligible'],
                   pretrain_parent=parent_name,production_changed=False,automatic_followup=False,
                   clean_environment_verified=False,target_accuracy='unknown'))
        print('Comparison complete. Retained development recipe:',retained,flush=True)


if __name__=='__main__':
    try:main()
    except (Exception,KeyboardInterrupt) as error:
        os.chdir(PROJECT)
        write_json(R/'last-failure.json',dict(error_type=type(error).__name__,message=str(error),production_changed=False))
        with Path('ball.md').open('a') as journal:
            journal.write('\nFixed pretraining route stopped; preserve failure record and checkpoints for review.\n')
        raise
