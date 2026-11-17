"""User-run 40k-to-50k graph continuation over the frozen Trial-B TCN."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
PROJECT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(PROJECT/'scripts'),str(PROJECT/'experiments/graph-long-2026-11-15'),
             str(PROJECT/'experiments/tcn-hybrid-2026-11-14')]
import run_tcn_hybrid as old
from long_contract import (ROOT, WORKERS, TOTAL, MODELS, registration, guard, save,
    require, sha, load, jobs, fit_path, proof_path, operation, admit, check_date)


def verify_proof(match,seed,signature):
    path=proof_path(match,seed)
    if not path.exists():return None
    proof=load(path)
    require(proof['signature']==signature and proof['match']==match and proof['seed']==seed
        and proof['steps']==TOTAL and proof['exact_repeat'] is True
        and proof['training_matches']==['idsse-'+m for m in old.IDS if m!=match], 'Long fit proof differs')
    expected={str(fit_path(match,seed,f)):sha(fit_path(match,seed,f)) for f in ('first','repeat')}
    require(proof['checkpoint_hashes']==expected and sha(proof['checks_path'])==proof['checks_sha256'],
            'Long fit checkpoint/checks changed')
    sources={str(old.fit_path('graph',match,seed,f)):sha(old.fit_path('graph',match,seed,f)) for f in ('first','repeat')}
    require(proof['source_checkpoints']==sources, 'Warm-start lineage differs')
    return proof


def checks(signature):
    status=ROOT/'checks-status.json'
    if status.exists():
        value=load(status)
        require(value['signature']==signature and value['passed']
            and sha(value['path'])==value['sha256'], 'Checks status changed')
        return Path(value['path'])
    path=ROOT/f'checks-{time.time_ns()}.txt'
    with guard():
        with path.open('w') as stream:
            env=os.environ.copy()
            env['PYTHONPATH']='src:scripts:experiments/tcn-hybrid-2026-11-14:experiments/graph-long-2026-11-15'
            for folder in (old.R/'tests',ROOT/'tests'):
                outcome=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(folder),'-v'],
                    stdout=stream,stderr=subprocess.STDOUT,env=env)
                require(outcome.returncode==0,'Long-graph checks failed; preserve '+str(path))
    save(status,dict(signature=signature,passed=True,path=str(path),sha256=sha(path)))
    return path


def worker(match,seed,signature,original_signature,bound,checks_path):
    with operation(f'{match}-{seed}'):
        if verify_proof(match,seed,signature):return
        d=old.dependencies()
        import long_training as training
        cases=old.prepare_cases('graph',match,original_signature,bound,d)
        identity=d['hybrid_training'].expected_identity(original_signature,'graph',seed,match)
        start=time.monotonic()
        for fit in ('first','repeat'):
            training.train_fit(cases,fit_path(match,seed,fit).parent,signature,'graph',seed,match,guard,
                warm_start=old.fit_path('graph',match,seed,fit), source_identity=identity)
        values=[d['torch'].load(fit_path(match,seed,f),map_location='cpu',weights_only=True) for f in ('first','repeat')]
        expected=training.expected_identity(signature,'graph',seed,match)
        for v in values:training.validate_saved(v,expected)
        training.confirm_repeat(*values)
        save(proof_path(match,seed),dict(signature=signature,match=match,seed=seed,steps=TOTAL,
            exact_repeat=True,training_matches=expected['training_matches'],
            source_checkpoints={str(old.fit_path('graph',match,seed,f)):sha(old.fit_path('graph',match,seed,f)) for f in ('first','repeat')},
            checkpoint_hashes={str(fit_path(match,seed,f)):sha(fit_path(match,seed,f)) for f in ('first','repeat')},
            checks_path=str(checks_path),checks_sha256=sha(checks_path),continuation_seconds=time.monotonic()-start,
            loss_sha256=hashlib.sha256(json.dumps(values[0]['losses']).encode()).hexdigest()))


def schedule(tasks,checks_path):
    pending=list(tasks);active=[];start=time.monotonic()
    try:
        while pending or active:
            check_date()
            while pending and len(active)<WORKERS:
                match,seed=pending.pop(0)
                with guard():
                    (ROOT/'logs').mkdir(parents=True,exist_ok=True)
                    path=ROOT/'logs'/f'{match}-{seed}-{time.time_ns()}.txt';stream=path.open('w')
                command=[sys.executable,'scripts/run_graph_long.py','--worker','--match',match,
                    '--seed',str(seed),'--checks-path',str(checks_path)]
                child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT)
                active.append((child,stream,path))
                print('Started graph continuation',match,seed,'log:',path,flush=True)
            for item in list(active):
                child,stream,path=item
                if child.poll() is not None:
                    stream.close();active.remove(item)
                    require(child.returncode==0,'Graph continuation worker failed; preserve '+str(path))
            if active:time.sleep(.25)
    finally:
        for child,stream,_ in active:
            if child.poll() is None:child.terminate()
            child.wait();stream.close()
    return time.monotonic()-start


def model(match,seed,signature,d,training):
    require(verify_proof(match,seed,signature),'Missing exact-fit proof')
    saved=d['torch'].load(fit_path(match,seed),map_location='cpu',weights_only=True)
    training.validate_saved(saved,training.expected_identity(signature,'graph',seed,match))
    value=d['hybrid_model'].GraphRefiner().cpu().eval();value.load_state_dict(saved['state'],strict=True)
    return value


def evaluate(signature,original_signature,bound,archives):
    d=old.dependencies();np=d['np']
    import long_training as training
    prior={(r['match'],r['condition']):r for r in archives}
    rows=[];paired=[]
    for match in old.IDS:
        check_date()
        unit=ROOT/'evaluation'/f'{match}.json'
        if unit.exists():
            value=load(unit);content={k:v for k,v in value.items() if k!='content_sha256'}
            require(value['signature']==signature and value['match']==match
                and hashlib.sha256(json.dumps(content,sort_keys=True).encode()).hexdigest()==value['content_sha256'],
                'Cached evaluation differs')
            for row in value['rows']:
                require(sha(row['csv_path'])==row['csv_sha256'],'Cached CSV changed')
            rows.extend(value['rows']);paired.append(value['paired']);continue
        members=[model(match,s,signature,d,training) for s in old.SEEDS]
        reloads=[model(match,s,signature,d,training) for s in old.SEEDS]
        records={};local=[];previous=None
        for condition in old.SETTINGS:
            check_date()
            with np.load(f'data/tcn-prepared/{match}-{condition}.npz',allow_pickle=False) as case:
                x,y,blocks=case['x'],case['y'],case['blocks'].tolist()
            if previous is not None:require(np.array_equal(y,previous[0]) and blocks==previous[1],'Corruption changed labels')
            previous=(y.copy(),blocks)
            path,metadata=old.cache_paths('graph',match,match,condition,'evaluation')
            meta=load(metadata)
            expected=dict(signature=original_signature,binding=bound,stage='graph',held_out=match,
                case=match,role='evaluation',view=condition,source_sha256=sha(f'data/tcn-prepared/{match}-{condition}.npz'),
                training_matches=['idsse-'+m for m in old.IDS if m!=match])
            require(meta['identity']==expected and sha(path)==meta['sha256'],'OOF Trial B cache differs')
            parent=np.load(path,mmap_mode='r',allow_pickle=False)
            parent_pred=d['decode'](parent,(1-np.eye(3))*16,blocks)
            archived=prior[match,condition]
            require(old.csv_digest(parent_pred)==archived['parent_csv_sha256']
                and d['metrics'](y,parent_pred,blocks,d['score'],d['official'],np)==archived['parent'],
                'Selected Trial B no longer reproduces')
            p,parts=old.ensemble_prediction(members,x,parent,blocks,d,return_members=True)
            repeated,reparts=old.ensemble_prediction(reloads,x,parent,blocks,d,return_members=True)
            batch4=old.ensemble_prediction(members,x,parent,blocks,d,batch=4)
            require(np.array_equal(p,repeated) and all(np.array_equal(a,b) for a,b in zip(parts,reparts)),
                    'Reloaded probabilities differ')
            predictions=[d['decode'](value,(1-np.eye(3))*16,blocks) for value in (p,repeated,batch4)]
            require(len({old.csv_digest(v) for v in predictions})==1,'CSV bytes differ by reload/batch')
            csv_path=MODELS/'predictions'/f'{match}-{condition}.csv'
            with guard():
                csv_path.parent.mkdir(parents=True,exist_ok=True)
                d['export_labels'](csv_path,predictions[0],len(y))
            require(sha(csv_path)==old.csv_digest(predictions[0]),'Written CSV bytes differ')
            measured=d['metrics'](y,predictions[0],blocks,d['score'],d['official'],np)
            analysis,records[condition]=d['analyze'](y,predictions[0],x[:,-4]==0,p,blocks,d['official'])
            require(analysis['per_iou']==measured['spell_per_iou'],'Diagnostic/scorer disagreement')
            local.append(dict(match=match,condition=condition,parent=archived['parent'],
                original_graph_40k=archived['candidate'],candidate=measured,analysis=analysis,
                candidate_missing_ball=d['missing'](y,predictions[0],x[:,-4]==0),
                parent_missing_ball=d['missing'](y,parent_pred,x[:,-4]==0),
                csv_path=str(csv_path),csv_sha256=sha(csv_path),reload_probabilities_equal=True,
                csv_bytes_equal_reload_batch4=True))
            print('Evaluated graph50k',match,condition,flush=True)
        pair=dict(match=match,per_iou=d['paired_changes'](records['clean'],records['targetlike']))
        value=dict(signature=signature,match=match,rows=local,paired=pair)
        value['content_sha256']=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
        save(unit,value);rows.extend(local);paired.append(pair)
    from hybrid_contract import gate_v2
    before=[dict(match=r['match'],condition=r['condition'],**r['parent']) for r in rows]
    after=[dict(match=r['match'],condition=r['condition'],**r['candidate']) for r in rows]
    gate=gate_v2(before,after)
    save(ROOT/'evaluation/results.json',rows);save(ROOT/'evaluation/gate-v2.json',gate)
    save(ROOT/'evaluation/paired-corruption.json',paired)
    report='# Graph continuation: frozen TCN + 50k graph\n\n'
    report+='|Match|Setting|TCN spellF1|Graph40k|Graph50k|TCN macroF1|Graph50k macroF1|\n|---|---|---:|---:|---:|---:|---:|\n'
    for r in rows:
        report+=(f"|{r['match']}|{r['condition']}|{r['parent']['spellF1']:.6f}|{r['original_graph_40k']['spellF1']:.6f}|"
            f"{r['candidate']['spellF1']:.6f}|{r['parent']['macroF1']:.6f}|{r['candidate']['macroF1']:.6f}|\n")
    report+='\nGate against retained Trial B:\n\n'+json.dumps(gate,indent=2)+'\n\nNo automatic promotion. Target accuracy unknown.\n'
    with guard():(ROOT/'evaluation/report.md').write_text(report)
    registration()
    save(ROOT/'evaluation/completion.json',dict(signature=signature,completed=True,gate=gate,
        results_sha256=sha(ROOT/'evaluation/results.json'),report_sha256=sha(ROOT/'evaluation/report.md'),
        fit_proofs={str(proof_path(m,s)):sha(proof_path(m,s)) for m,s in jobs()},
        production_changed=False,sealed_opened=False,target_accuracy='unknown'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    actions=parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--run',action='store_true');actions.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    parser.add_argument('--match',choices=old.IDS,help=argparse.SUPPRESS)
    parser.add_argument('--seed',type=int,choices=old.SEEDS,help=argparse.SUPPRESS)
    parser.add_argument('--checks-path',type=Path,help=argparse.SUPPRESS)
    args=parser.parse_args();os.chdir(PROJECT)
    signature,original_signature,bound,rows=registration()
    if args.worker:
        require((args.match,args.seed) in jobs() and args.checks_path is not None,'Invalid internal task')
        require(load(ROOT/'checks-status.json')==dict(signature=signature,passed=True,
            path=str(args.checks_path),sha256=sha(args.checks_path)),'Worker checks binding differs')
        worker(args.match,args.seed,signature,original_signature,bound,args.checks_path);return
    with operation('coordinator'):
        require(not (ROOT/'evaluation/completion.json').exists(),'Completed comparison exists; review it')
        forecast=admit();save(ROOT/'admission.json',dict(signature=signature,**forecast))
        log=checks(signature)
        todo=[(m,s) for m,s in jobs() if not verify_proof(m,s,signature)]
        elapsed=schedule(todo,log)
        evaluate(signature,original_signature,bound,rows)
        save(ROOT/'run-completion.json',dict(signature=signature,completed=True,workers=WORKERS,
            continuation_wall_seconds=elapsed,completion_sha256=sha(ROOT/'evaluation/completion.json')))
        print('Graph50k comparison complete. Stop and report done for review; no final fit/export started.',flush=True)


if __name__=='__main__':
    try:main()
    except (Exception,KeyboardInterrupt) as error:
        os.chdir(PROJECT)
        try:save(ROOT/'failures'/f'{time.time_ns()}.json',dict(type=type(error).__name__,message=str(error)))
        except Exception:print('Preserve terminal output; failure evidence could not be saved.',file=sys.stderr)
        raise
