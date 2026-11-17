"""One fixed graph-budget extension; archived 40k trial remains immutable."""
from contextlib import contextmanager
from datetime import datetime
import fcntl
import hashlib
from importlib.metadata import version
import json
import math
from pathlib import Path
import platform
import subprocess
from zoneinfo import ZoneInfo

import run_tcn_hybrid as old
from hybrid_contract import (require, sha, load, committed_bytes, registration as parent_registration,
    stage_signature, storage_guard as original_guard, check_date, check_storage)

ROOT = Path('experiments/graph-long-2026-11-15')
MODELS = Path('models/graph-long-2026-11-15')
TOTAL, EXTRA, WORKERS = 50000, 10000, 4
ALLOWANCE = 512*1024**2


def jobs():
    return [(m, s) for m in old.IDS for s in old.SEEDS]


def registration():
    check_date()
    locked = load(ROOT/'inputs.json')
    require(set(locked) == {'code','evidence'}, 'Unexpected longer-graph lock schema')
    for group, entries in locked.items():
        for name, digest in entries.items():
            p = Path(name)
            require(not p.is_absolute() and '..' not in p.parts, 'Unsafe locked path')
            require(sha(p) == digest, 'Changed graph extension input: '+name)
            if group == 'code': committed_bytes(p)
    committed_bytes(ROOT/'inputs.json')
    mandatory = {str(ROOT/n) for n in ('long_contract.py','long_training.py','protocol.md',
        'membership.json','tests/test_long.py')} | {'scripts/run_graph_long.py','docs/run-graph-long.md'}
    require(mandatory <= set(locked['code']), 'Incomplete extension source lock')
    membership = load(ROOT/'membership.json')
    require(membership == dict(development=list(old.IDS),
        folds={m:['idsse-'+n for n in old.IDS if n != m] for m in old.IDS},
        sealed_excluded=['J03WQQ','J03WR9'],target_excluded=True), 'Membership differs')
    env = load('experiments/tcn-winner-release-2026-11-12/environment-snapshot.json')
    require(platform.python_version() == env['python'] and platform.system() == env['system']
        and platform.machine() == env['machine'], 'Pinned platform differs')
    for package, expected in env['packages'].items():
        require(version(package) == expected, 'Pinned dependency differs: '+package)
    _, _, base = parent_registration(training=False)
    bound, original_signature = stage_signature('graph', base)
    require(not bound['temporal_selected'], 'Frozen graph must use Trial B parent')
    _, rows, _ = old.verify_completed('graph', original_signature, bound)
    signature = hashlib.sha256((sha(ROOT/'protocol.md')+sha(ROOT/'inputs.json')).encode()).hexdigest()
    return signature, original_signature, bound, rows


def used_bytes():
    # Historical accounting predates the recent audit and private package copies.
    # Include those in this reserved allowance to avoid escaping the total quota.
    roots = (ROOT, MODELS, Path('experiments/temporal-recovery-audit-2026-11-15'),
             *Path('.').glob('submission-package-*'))
    return sum(p.stat().st_size for root in roots if root.exists()
               for p in root.rglob('*') if p.is_file() and not p.is_symlink())


@contextmanager
def guard():
    require(used_bytes() < ALLOWANCE, 'Extension artifacts exceed512MiB; preserve files')
    with original_guard(reserve=ALLOWANCE):
        yield
        require(used_bytes() < ALLOWANCE, 'Extension artifacts exceed512MiB; preserve files')


def save(path, value):
    with guard():
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
        temp.replace(path)


def fit_path(m, s, fit='first'):
    return MODELS/m/str(s)/fit/'progress.pt'


def proof_path(m, s):
    return ROOT/'evaluation/fits'/f'{m}-{s}.json'


def projection(rate, remaining_pairs=10, final_total=TOTAL):
    require(math.isfinite(rate) and rate>0 and 0<=remaining_pairs<=10, 'Invalid projection')
    development = math.ceil(remaining_pairs/WORKERS)*2*EXTRA*rate
    # Reserve four fresh final fits in one four-worker wave, if this candidate wins.
    return 1.5*(development+final_total*rate)+1800


def admit():
    values = [load(old.proof_path('graph',m,s))['seconds']/80000 for m,s in jobs()]
    benchmark = load(old.R/'scheduling/benchmark.json')
    require(benchmark['completed'] and benchmark['selected_workers']==4, 'Four-job benchmark missing')
    rate = max(max(values), benchmark['timings']['4']['worst_seconds_per_update'])
    remaining_pairs = sum(not proof_path(m,s).exists() for m,s in jobs())
    seconds = projection(rate, remaining_pairs=remaining_pairs)
    now = datetime.now(ZoneInfo('Asia/Kolkata'))
    remaining = (datetime(2026,11,16,tzinfo=ZoneInfo('Asia/Kolkata'))-now).total_seconds()
    check_storage(reserve=ALLOWANCE)
    require(seconds < remaining, '50k comparison plus final-fitting reserve no longer fits before freeze')
    return dict(seconds_per_update=rate, projected_total_with_final_reserve_seconds=seconds,
        remaining_seconds=remaining, workers=WORKERS, cumulative_steps=TOTAL,
        extra_steps_per_fit=EXTRA, forecast_is_not_runtime_guarantee=True)


@contextmanager
def operation(name):
    with guard(): (ROOT/'locks').mkdir(parents=True,exist_ok=True)
    with (ROOT/'locks'/f'{name}.lock').open('a+') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
