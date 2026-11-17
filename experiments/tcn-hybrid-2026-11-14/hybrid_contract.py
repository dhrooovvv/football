"""Frozen lineage, sequential review decisions and bounded hybrid artifacts."""
from contextlib import contextmanager
from datetime import date, datetime
import fcntl
from functools import lru_cache
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import threading
from zoneinfo import ZoneInfo

R = Path('experiments/tcn-hybrid-2026-11-14')
DATA = Path('data/tcn-hybrid')
MODELS = Path('models/tcn-hybrid')
MISSED = Path('experiments/tcn-missed-2026-11-13')
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
SEEDS = (20261106, 20261107)
STAGES = ('temporal', 'graph')
SETTINGS = ('clean', 'targetlike')
MAX_BYTES, MIN_FREE, RESERVE = 2 * 1024 ** 3, 12 * 1024 ** 3, 64 * 1024 ** 2
ARTIFACT_ROOTS = tuple(map(Path, ('data/tcn-missed', 'models/tcn-missed', str(MISSED),
    'data/tcn-final-b', 'models/tcn-final-b', 'experiments/tcn-final-b-2026-11-13',
    'experiments/tcn-final-b-export-2026-11-13', 'data/competition/tcn-final-b-exports',
    'experiments/tcn-diagnostic-2026-11-13', 'data/tcn-diagnostic', str(R), str(DATA), str(MODELS),
    'data/competition/tcn-hybrid-exports')))
QUALIFICATION_ROOTS = tuple(map(Path, ('data/tcn-final-b-clean-env', 'data/tcn-final-b-clean-clone',
    'data/tcn-hybrid-clean-env', 'data/tcn-hybrid-clean-clone')))
_STORAGE = threading.local()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 ** 2), b''):
            digest.update(chunk)
    return digest.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def check_date(training=True):
    today = datetime.now(ZoneInfo('Asia/Kolkata')).date()
    require(today < date(2026, 11, 16) if training else today <= date(2026, 11, 17),
            'Research frozen' if training else 'Project action deadline passed')


def committed_bytes(path):
    path = Path(path)
    require(not path.is_absolute() and '..' not in path.parts, 'Unsafe committed path')
    saved = subprocess.run(['git', 'show', 'HEAD:' + str(path)], capture_output=True)
    require(saved.returncode == 0 and hashlib.sha256(saved.stdout).hexdigest() == sha(path),
            'Source/review is not committed unchanged: ' + str(path))


@lru_cache(maxsize=1)
def old_contract():
    spec = importlib.util.spec_from_file_location('hybrid_missed_contract', MISSED / 'contract.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def missed_signature():
    return hashlib.sha256((sha(MISSED / 'protocol.md') + sha(MISSED / 'inputs.json')).encode()).hexdigest()


def verify_lock(path, committed_groups=('code',)):
    groups = load(path)
    for group, entries in groups.items():
        require(isinstance(entries, dict), 'Fingerprint groups must be objects')
        for name, digest in entries.items():
            candidate = Path(name)
            require(not candidate.is_absolute() and '..' not in candidate.parts, 'Unsafe fingerprint path')
            require(sha(candidate) == digest, 'Registered bytes differ: ' + name)
            if group in committed_groups:
                committed_bytes(candidate)
    committed_bytes(path)
    return groups


def registration(training=True):
    """Delivery verifies byte locks without calling historical research guards."""
    check_date(training)
    if training:
        old_contract().registration()
    else:
        verify_lock(MISSED / 'inputs.json')
        verify_lock(Path('experiments/tcn-parallel-2026-11-12/inputs.json'))
    locked = verify_lock(R / 'inputs.json')
    require(set(locked) == {'code', 'evidence'}, 'Unexpected hybrid source lock schema')
    mandatory = {str(R / name) for name in ('hybrid_contract.py', 'hybrid_model.py', 'hybrid_data.py',
        'hybrid_training.py', 'protocol.md', 'membership.json', 'requirements.txt',
        'tests/test_model.py', 'tests/test_training.py', 'tests/test_contract.py', 'tests/test_runner.py')}
    mandatory.update(('scripts/run_tcn_hybrid.py', 'docs/run-tcn-hybrid.md'))
    require(mandatory <= set(locked['code']), 'Hybrid source fingerprints incomplete')
    membership = load(R / 'membership.json')
    expected = {m: ['idsse-' + n for n in IDS if n != m] for m in IDS}
    require(membership['development'] == list(IDS) and membership['supervised_folds'] == expected
            and set(membership['sealed_excluded']) == {'J03WQQ', 'J03WR9'}
            and membership['target_excluded'] is True, 'Hybrid split differs')
    signature = hashlib.sha256((sha(R / 'protocol.md') + sha(R / 'inputs.json')).encode()).hexdigest()
    return locked, membership, signature


def gate_v2(before, after, contracts=True, repeats=True):
    return old_contract().gate_v2(before, after, contracts, repeats)


def validated_review(stage, base_signature, require_committed=True):
    # Resolve lazily because the runner itself imports this contract.
    from run_tcn_hybrid import validated_review as verify
    return verify(stage, base_signature, require_committed)


def stage_binding(stage, signature):
    require(stage in STAGES, 'Unregistered hybrid stage')
    value = dict(stage=stage, registration=signature, parent='trial_b',
                 parent_results_sha256=sha(MISSED / 'evaluation/b/results.json'),
                 parent_review_sha256=sha(MISSED / 'reviewed-b.json'), temporal_selected=False)
    if stage == 'graph':
        path = R / 'reviewed-temporal.json'
        require(path.is_file(), 'Graph waits for committed temporal review')
        committed_bytes(path)
        review = load(path)
        require(review['stage'] == 'temporal' and review['registration'] == signature
                and review['review_completed'] is True, 'Temporal review identity differs')
        for key, name in (('completion_sha256', 'completion.json'), ('results_sha256', 'results.json'),
                          ('gate_sha256', 'gate-v2.json')):
            require(review[key] == sha(R / 'evaluation/temporal' / name), 'Temporal review evidence differs')
        gate = load(R / 'evaluation/temporal/gate-v2.json')
        require(review['accepted'] is gate['quality_eligible'], 'Temporal review disagrees with gate')
        value['review_sha256'] = sha(path)
        value['temporal_selected'] = review['accepted']
        if review['accepted']:
            value.update(parent='temporal', parent_results_sha256=review['results_sha256'],
                         temporal_checkpoints=review['checkpoint_hashes'])
            for name, digest in review['checkpoint_hashes'].items():
                require(sha(name) == digest, 'Retained temporal weights changed')
    return value


def stage_signature(stage, signature):
    bound = stage_binding(stage, signature)
    digest = hashlib.sha256((signature + json.dumps(bound, sort_keys=True)).encode()).hexdigest()
    return bound, digest


def artifact_bytes():
    total, seen = 0, set()
    project_roots = {Path.cwd().resolve(), Path('models/tcn-final-b').resolve().parents[1]}
    for project in project_roots:
        for relative in ARTIFACT_ROOTS:
            root = project / relative
            if root.exists():
                for path in root.resolve().rglob('*'):
                    require(not path.is_symlink(), 'Artifact tree contains a symlink')
                    if path.is_file() and path.resolve() not in seen:
                        seen.add(path.resolve()); total += path.stat().st_size
        for relative in QUALIFICATION_ROOTS:
            root = project / relative
            if root.exists():
                for path in root.rglob('*'):
                    if not path.is_symlink() and path.is_file() and path.resolve() not in seen:
                        seen.add(path.resolve()); total += path.stat().st_size
    return total


def check_storage(reserve=RESERVE):
    used, free = artifact_bytes(), shutil.disk_usage('.').free
    require(used + reserve <= MAX_BYTES, 'Combined artifacts would exceed2GiB; preserve existing assets')
    require(free - reserve >= MIN_FREE, 'Free space would fall below12GiB; preserve existing assets')
    return dict(artifact_bytes=used, free_bytes=free)


@contextmanager
def storage_guard(training=True, reserve=RESERVE):
    check_date(training)
    if getattr(_STORAGE, 'active', False):
        yield
        return
    directory = Path('data/tcn-missed')
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'storage.lock').open('a+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        check_date(training); check_storage(reserve)
        _STORAGE.active = True
        try:
            yield
            check_storage(0)
        finally:
            _STORAGE.active = False


def save(path, value, training=True):
    with storage_guard(training):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
        temporary.replace(path)


@contextmanager
def operation_lock(stage, seed=None):
    require(stage in STAGES and (seed is None or seed in SEEDS), 'Invalid stage/seed lock')
    check_date()
    directory = DATA / stage
    directory.mkdir(parents=True, exist_ok=True)
    handles = []
    try:
        name = 'operation.lock' if seed is None else f'seed-{seed}.lock'
        for path, mode in ((Path('data/tcn-expanded/operation.lock'), fcntl.LOCK_SH),
                           (directory / name, fcntl.LOCK_EX)):
            handle = path.open('a+'); handles.append(handle)
            try:
                fcntl.flock(handle, mode | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError('Conflicting writer or duplicate hybrid operation') from error
        yield
    finally:
        for handle in reversed(handles):
            handle.close()


def deadline_projection(seconds_per_update, evaluation_seconds, workers, included_branches=1, now=None):
    require(workers in (1, 2) and included_branches in (1, 2), 'Invalid projection shape')
    require(math.isfinite(seconds_per_update) and seconds_per_update > 0
            and math.isfinite(evaluation_seconds) and evaluation_seconds >= 0, 'Invalid timing measurement')
    now = now or datetime.now(ZoneInfo('Asia/Kolkata'))
    require(now.tzinfo is not None, 'Timezone required for projection')
    deadline = datetime(2026, 11, 16, tzinfo=ZoneInfo('Asia/Kolkata'))
    #20 development fits plus4 final fits for each branch selected in the final stack.
    raw = seconds_per_update * 40000 * (20 / workers + 4 * included_branches) + evaluation_seconds
    estimate = 1.5 * raw
    remaining = (deadline - now).total_seconds()
    return dict(remaining_seconds=remaining, projected_seconds=estimate, safety_factor=1.5,
                projected_to_finish=estimate < remaining, workers=workers,
                included_final_branches=included_branches, estimate_not_guarantee=True)


def artifact_projection(evaluation_frames, included_branches=1):
    require(type(evaluation_frames) is int and evaluation_frames > 0
            and included_branches in (1, 2), 'Invalid artifact projection')
    measured = check_storage(0)
    #Each small model/optimizer plus four40k scalar histories fits comfortably
    #inside8MiB. Three CSV passes use at most12bytes per serialized frame.
    additional = (20 + 4 * included_branches) * 8 * 1024 ** 2
    additional += evaluation_frames * 3 * 12 + 16 * 1024 ** 2
    return dict(measured_artifact_bytes=measured['artifact_bytes'],
                projected_additional_bytes=additional,
                projected_total_bytes=measured['artifact_bytes'] + additional,
                projected_free_bytes=measured['free_bytes'] - additional,
                within_budget=(measured['artifact_bytes'] + additional <= MAX_BYTES
                               and measured['free_bytes'] - additional >= MIN_FREE),
                checkpoint_bound_bytes_per_fit=8 * 1024 ** 2,
                estimate_not_guarantee=True)
