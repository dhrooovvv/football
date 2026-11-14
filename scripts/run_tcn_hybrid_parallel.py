"""User-run scheduling-only extension for the registered graph hybrid."""
import argparse
from contextlib import contextmanager
from datetime import datetime
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT/'scripts'),str(PROJECT/'experiments/tcn-hybrid-2026-11-14')]
import run_tcn_hybrid as old
from hybrid_contract import (registration as parent_registration, require, sha, load, save,
    stage_signature, check_date, operation_lock, storage_guard, artifact_projection)
R = Path('experiments/tcn-hybrid-2026-11-14/scheduling')
DATA = Path('data/tcn-hybrid/scheduling')
MODELS = Path('models/tcn-hybrid/scheduling')
PROBE_STEPS = 64


def jobs():
    return [(match, seed) for match in old.IDS for seed in old.SEEDS]


def registration():
    _, _, base = parent_registration()
    locked = load(R/'inputs.json')
    for group, entries in locked.items():
        for path, digest in entries.items():
            require(sha(path) == digest, 'Scheduling fingerprint differs: '+path)
            if group == 'code':
                committed = subprocess.run(['git','show','HEAD:'+path],capture_output=True,check=True).stdout
                require(hashlib.sha256(committed).hexdigest() == digest, 'Scheduling source is uncommitted')
    committed = subprocess.run(['git','show','HEAD:'+str(R/'inputs.json')],capture_output=True,check=True).stdout
    require(committed == (R/'inputs.json').read_bytes(), 'Scheduling lock is uncommitted')
    bound, signature = stage_signature('graph', base)
    require(not bound['temporal_selected'], 'This scheduling amendment is for rejected-temporal/B graph parent')
    old.validated_review('temporal', base)
    pre = load(old.R/'preflight/graph/report.json')
    require(pre['completed'] and pre['signature'] == signature and pre['binding'] == bound, 'Graph preflight differs')
    require(sha(pre['checks_path']) == pre['checks_sha256'], 'Graph correctness log changed')
    for path, digest in pre['caches'].items():
        require(sha(path) == digest, 'Parent cache changed')
    extension = hashlib.sha256((sha(R/'protocol.md')+sha(R/'inputs.json')).encode()).hexdigest()
    return base, bound, signature, extension, pre


@contextmanager
def task_lock(match, seed, fit='paired'):
    DATA.mkdir(parents=True,exist_ok=True)
    with (DATA/f'{match}-{seed}-{fit}.lock').open('a+') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def checks():
    path=R/'checks.txt'
    require(not path.exists(), 'Scheduling checks already exist; preserve earlier benchmark')
    with storage_guard():
        with path.open('w') as stream:
            result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(R/'tests'),'-v'],
                                  stdout=stream,stderr=subprocess.STDOUT)
    require(result.returncode == 0, 'Scheduling contracts failed; preserve checks.txt')
    return path


def schedule(tasks, workers, mode, mode_name='full'):
    pending=list(tasks); active=[]; started=time.monotonic(); peak_rss=0
    try:
        while pending or active:
            check_date()
            while pending and len(active)<workers:
                match,seed=pending.pop(0)
                command=[sys.executable,'scripts/run_tcn_hybrid_parallel.py','--task',mode,
                         '--match',match,'--seed',str(seed),'--mode-name',mode_name]
                with storage_guard():
                    directory=R/'logs';directory.mkdir(parents=True,exist_ok=True)
                    path=directory/f'{mode}-{mode_name}-{match}-{seed}-{time.time_ns()}.txt'
                    stream=path.open('w')
                child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT)
                active.append((child,stream,path))
            for item in list(active):
                child,stream,path=item
                if child.poll() is not None:
                    stream.close();active.remove(item)
                    require(child.returncode == 0,'Scheduling worker failed; preserve '+str(path))
            if active:
                measured=subprocess.run(['ps','-o','rss=','-p',','.join(str(child.pid) for child,_,_ in active)],
                                        capture_output=True,text=True)
                if measured.returncode==0:
                    peak_rss=max(peak_rss,sum(int(v) for v in measured.stdout.split())*1024)
                time.sleep(.25)
    finally:
        for child,stream,_ in active:
            if child.poll() is None:child.terminate()
            child.wait();stream.close()
    return dict(wall_seconds=time.monotonic()-started,sampled_peak_sum_worker_rss_bytes=peak_rss)


def probe_path(mode, match, seed):
    return MODELS/'benchmark'/mode/match/str(seed)/'progress.pt'


def task(mode, match, seed, mode_name):
    _,bound,signature,extension,pre=registration()
    if mode=='final':
        final_task(match,seed,extension)
        return
    require((match,seed) in jobs(), 'Unregistered fold/seed')
    with task_lock(match,seed,mode_name):
        d=old.dependencies();training=d['hybrid_training'];torch=d['torch']
        cases=old.prepare_cases('graph',match,signature,bound,d)
        if mode=='probe':
            path=probe_path(mode_name,match,seed)
            require(not path.exists(), 'Probe already exists; preserve benchmark evidence')
            started=time.monotonic()
            training.train_fit(cases,path.parent,signature,'graph',seed,match,storage_guard,
                               steps=PROBE_STEPS,probe=True)
            elapsed=time.monotonic()-started
            rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            save(path.with_suffix('.json'),dict(extension=extension,match=match,seed=seed,seconds=elapsed,
                peak_rss_bytes=int(rss if sys.platform=='darwin' else rss*1024),sha256=sha(path)))
            return
        require(mode=='fit','Unknown task')
        if old.verify_fit('graph',match,seed,signature):return
        started=time.monotonic()
        for fit in ('first','repeat'):
            training.train_fit(cases,old.fit_path('graph',match,seed,fit).parent,signature,
                               'graph',seed,match,storage_guard)
        values=[torch.load(old.fit_path('graph',match,seed,fit),weights_only=True,map_location='cpu')
                for fit in ('first','repeat')]
        identity=training.expected_identity(signature,'graph',seed,match)
        for value in values:training.validate_saved(value,identity)
        training.confirm_repeat(*values)
        value=values[0]
        proof=dict(stage='graph',seed=seed,held_out=match,signature=signature,binding=bound,
            training_matches=identity['training_matches'],steps=40000,exact_repeat=True,
            checks_path=pre['checks_path'],checks_sha256=pre['checks_sha256'],
            checkpoint_hashes={str(old.fit_path('graph',match,seed,fit)):sha(old.fit_path('graph',match,seed,fit))
                               for fit in ('first','repeat')},seconds=time.monotonic()-started,
            training_loss_sha256=hashlib.sha256(json.dumps(value['losses']).encode()).hexdigest(),
            component_loss_sha256=hashlib.sha256(json.dumps(value['component_losses']).encode()).hexdigest(),
            coverage=value['coverage'],supervised_views=value['supervised_views'],exposure=value['exposure'],
            scheduling_extension=extension)
        save(old.proof_path('graph',match,seed),proof)
        old.verify_fit('graph',match,seed,signature)


def projected_seconds(seconds_per_fit, workers, evaluation_seconds):
    require(workers in (2,4) and math.isfinite(seconds_per_fit) and seconds_per_fit>0 and math.isfinite(evaluation_seconds) and evaluation_seconds>=0,'Invalid throughput inputs')
    # Ten paired jobs each contain two fits. Four final fits run independently.
    waves=math.ceil(10/workers)
    return 1.5*(waves*2*seconds_per_fit+math.ceil(4/workers)*seconds_per_fit+evaluation_seconds)


def benchmark(base,bound,signature,extension,pre):
    require(not (R/'benchmark.json').exists(), 'Completed benchmark already exists; preserve it')
    log=checks();timings={};proofs={}
    for count in (2,4):
        name=str(count)
        measured=schedule(jobs(),count,'probe',name)
        wall=measured['wall_seconds']
        records=[load(probe_path(name,m,s).with_suffix('.json')) for m,s in jobs()]
        timings[name]=dict(wall_seconds=wall,sampled_peak_sum_worker_rss_bytes=measured['sampled_peak_sum_worker_rss_bytes'],worst_seconds_per_update=max(r['seconds']/PROBE_STEPS for r in records),
                           measured_peak_worker_rss_bytes=max(r['peak_rss_bytes'] for r in records),
                           estimated_sum_worker_rss_bytes=sum(sorted((r['peak_rss_bytes'] for r in records),reverse=True)[:count]))
        for m,s in jobs():
            path=probe_path(name,m,s);record=load(path.with_suffix('.json'))
            require(record['extension']==extension and sha(path)==record['sha256'],'Probe identity changed')
            proofs[str(path)]=sha(path)
    d=old.dependencies();torch=d['torch'];training=d['hybrid_training']
    for m,s in jobs():
        values=[torch.load(probe_path(str(n),m,s),weights_only=True,map_location='cpu') for n in (2,4)]
        expected=training.expected_identity(signature,'graph',s,m,steps=PROBE_STEPS,probe=True)
        for value in values:training.validate_saved(value,expected)
        training.confirm_repeat(*values)
        # Existing one-process preflight supplies a serial reference for seed20261106.
        if s==old.SEEDS[0]:
            originals=list((old.MODELS/'graph/preflight'/m).rglob('progress.pt'))
            require(len(originals)==1,'Serial probe reference is ambiguous')
            reference=torch.load(originals[0],weights_only=True,map_location='cpu')
            training.validate_saved(reference,expected);training.confirm_repeat(reference,values[0])
    m,s=jobs()[0]
    with d['np'].load(f'data/tcn-prepared/{m}-clean.npz',allow_pickle=False) as case:
        x=case['x'];blocks=case['blocks'].tolist()
    p,_=old.cache_paths('graph',m,m,'clean','evaluation')
    parent=d['np'].load(p,mmap_mode='r',allow_pickle=False)
    start,stop=blocks[0];support=[(start,min(stop,start+16384))]
    digests=[]
    for count,batch in ((2,1),(4,1),(4,4)):
        value=torch.load(probe_path(str(count),m,s),weights_only=True,map_location='cpu')
        model=d['hybrid_model'].GraphRefiner().eval();model.load_state_dict(value['state'])
        probabilities=d['hybrid_model'].predict(model,x,parent,support,batch=batch)
        labels=d['decode'](probabilities,(1-d['np'].eye(3))*16,support)
        digests.append(old.csv_digest(labels))
    require(len(set(digests))==1,'Scheduling/batch decoded CSV bytes differ')
    # Compare complete benchmark wall times, including subprocess/import overhead.
    selected=min((2,4),key=lambda n:(timings[str(n)]['wall_seconds'],n))
    speed=timings[str(selected)]['worst_seconds_per_update']
    estimate=projected_seconds(speed*40000,selected,pre['preparation_and_probe_seconds']*3)
    from zoneinfo import ZoneInfo
    remaining=(datetime(2026,11,16,tzinfo=ZoneInfo('Asia/Kolkata'))-datetime.now(ZoneInfo('Asia/Kolkata'))).total_seconds()
    result=dict(completed=True,remaining_seconds=remaining,projected_to_finish=estimate<remaining,extension=extension,stage_signature=signature,timings=timings,
        selected_workers=selected,exact_states_losses_rng_equal=True,serial_reference_equal=True,
        csv_hashes=digests,checks_path=str(log),checks_sha256=sha(log),probe_checkpoints=proofs,
        projected_seconds=estimate,final_fit_scheduling='four_independent_first_repeat_fits',quality_scores_used=False)
    save(R/'benchmark.json',result)
    print('Benchmark complete. Selected workers:',selected,'projected total hours:',estimate/3600,flush=True)


def run(base,bound,signature,extension,pre):
    record=load(R/'benchmark.json')
    require(record['completed'] and record['extension']==extension and record['stage_signature']==signature
            and record['exact_states_losses_rng_equal'] and record['serial_reference_equal'], 'Benchmark differs')
    require(sha(record['checks_path'])==record['checks_sha256'],'Scheduling checks changed')
    for path,digest in record['probe_checkpoints'].items():require(sha(path)==digest,'Benchmark probe changed')
    count=record['selected_workers'];speed=record['timings'][str(count)]['worst_seconds_per_update']
    seconds=projected_seconds(speed*40000,count,pre['preparation_and_probe_seconds']*3)
    from datetime import date
    from zoneinfo import ZoneInfo
    remaining=(datetime(2026,11,16,tzinfo=ZoneInfo('Asia/Kolkata'))-datetime.now(ZoneInfo('Asia/Kolkata'))).total_seconds()
    require(seconds<remaining,'Measured scheduling projection exceeds remaining freeze budget')
    require(artifact_projection(pre['evaluation_frames'],1)['within_budget'],'Projected artifacts exceed storage budget')
    tasks=[(m,s) for m,s in jobs() if not old.verify_fit('graph',m,s,signature)]
    schedule(tasks,count,'fit')
    old.evaluate('graph',signature,bound)
    parent_registration();old.verify_completed('graph',signature,bound)
    save(R/'run-completion.json',dict(extension=extension,workers=count,completed=True,
         graph_completion_sha256=sha(old.R/'evaluation/graph/completion.json')))
    print('Graph comparison complete. Stop and report done for review.',flush=True)



def final_task(match,seed,extension):
    import release_tcn_hybrid as release
    require(match in ('final-first','final-repeat') and seed in old.SEEDS,'Invalid final task')
    _,_,base=parent_registration()
    identity,signature=release.release_identity('graph',base)
    require(identity['stages']==['graph'],'Parallel final mode requires the accepted graph-only correction')
    fit=match.split('-')[1]
    with task_lock(match,seed,fit):
        d=release.dependencies()
        cases=[release.cached_final_parent(d['CompactCase'](Path('data/tcn-expanded')/('idsse-'+m)),
                    'graph',[],{},d,signature) for m in old.IDS]
        d['hybrid_training'].train_fit(cases,release.checkpoint_paths('graph',seed)[0 if fit=='first' else 1].parent,
                    signature,'graph',seed,None,storage_guard,purpose='final')


def fit_final(base,extension,pre):
    import release_tcn_hybrid as release
    record=load(R/'benchmark.json')
    require(record['extension']==extension and record['completed'],'Scheduling benchmark differs')
    count=record['selected_workers'];speed=record['timings'][str(count)]['worst_seconds_per_update']
    from zoneinfo import ZoneInfo
    remaining=(datetime(2026,11,16,tzinfo=ZoneInfo('Asia/Kolkata'))-datetime.now(ZoneInfo('Asia/Kolkata'))).total_seconds()
    estimate=1.5*(math.ceil(4/count)*40000*speed+pre['preparation_and_probe_seconds']*3)
    require(estimate<remaining,'Parallel final fits exceed remaining freeze budget')
    identity,signature=release.release_identity('graph',base)
    require(identity['stages']==['graph'],'Only an accepted graph-only branch can use this final mode')
    check=release.checks();d=release.dependencies()
    for m in old.IDS:
        release.cached_final_parent(d['CompactCase'](Path('data/tcn-expanded')/('idsse-'+m)),
                    'graph',[],{},d,signature)
    schedule([(f'final-{fit}',seed) for seed in old.SEEDS for fit in ('first','repeat')],count,'final')
    members={}
    for seed in old.SEEDS:
        paths=release.checkpoint_paths('graph',seed)
        values=[d['torch'].load(p,map_location='cpu',weights_only=True) for p in paths]
        expected=d['hybrid_training'].expected_identity(signature,'graph',seed,None,purpose='final')
        for value in values:d['hybrid_training'].validate_saved(value,expected)
        d['hybrid_training'].confirm_repeat(*values)
        proof=release.MODELS/'graph'/str(seed)/'proof.json'
        save(proof,dict(signature=signature,stage='graph',seed=seed,steps=40000,
            training_matches=identity['training_matches'],exact_repeat=True,
            checks_path=str(check),checks_sha256=sha(check),
            checkpoint_hashes={str(p):sha(p) for p in paths},scheduling_extension=extension))
        members[str(seed)]=dict(proof=str(proof),proof_sha256=sha(proof))
    save(release.MODELS/'manifest-graph.json',dict(identity=identity,signature=signature,
        stage_signatures={'graph':signature},members={'graph':members},
        source_inputs_sha256=sha(old.R/'inputs.json'),base_manifest_sha256=sha('models/tcn-final-b/manifest.json'),
        quality_evaluation_performed=False,production_promoted=False,target_accuracy='unknown',
        scheduling_extension=extension))
    release.validate_manifest(release.MODELS/'manifest-graph.json',base,d)
    print('Parallel final branch fitting complete. Stop for review before export.',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    actions=parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--benchmark',action='store_true')
    actions.add_argument('--run',action='store_true')
    actions.add_argument('--fit-final',action='store_true')
    actions.add_argument('--task',choices=('probe','fit','final'),help=argparse.SUPPRESS)
    parser.add_argument('--match',choices=(*old.IDS,'final-first','final-repeat'),help=argparse.SUPPRESS)
    parser.add_argument('--seed',type=int,choices=old.SEEDS,help=argparse.SUPPRESS)
    parser.add_argument('--mode-name',default='full',help=argparse.SUPPRESS)
    args=parser.parse_args();os.chdir(PROJECT)
    base,bound,signature,extension,pre=registration()
    if args.task:
        task(args.task,args.match,args.seed,args.mode_name);return
    with operation_lock('graph'):
        if args.benchmark:benchmark(base,bound,signature,extension,pre)
        elif args.fit_final:
            import release_tcn_hybrid as release
            with release.operation():
                fit_final(base,extension,pre)
        else:run(base,bound,signature,extension,pre)


if __name__=='__main__':
    main()
