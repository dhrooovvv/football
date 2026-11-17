"""Immutable provenance and bounded writes for an identical-recipe final B fit.

No model imports or array/checkpoint deserialization occur in this module.
"""
from contextlib import contextmanager
import fcntl
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import threading

R = Path('experiments/tcn-final-b-2026-11-13')
MODELS = Path('models/tcn-final-b')
DATA = Path('data/tcn-final-b')
MISSED = Path('experiments/tcn-missed-2026-11-13')
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
KEYS = tuple('idsse-' + match for match in IDS)
SEEDS = (20261106, 20261107)
MAX_BYTES = 2 * 1024 ** 3
MIN_FREE_BYTES = 12 * 1024 ** 3
RESERVE_BYTES = 64 * 1024 ** 2
_STORAGE = threading.local()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 ** 2), b''):
            digest.update(block)
    return digest.hexdigest()


@lru_cache(maxsize=1)
def _missed():
    # A distinct module name avoids accidentally selecting another contract.py
    # already loaded by a runner or test suite.
    spec = importlib.util.spec_from_file_location('final_b_missed_contract', MISSED / 'contract.py')
    require(spec is not None and spec.loader is not None, 'Missing registered missed-trial contract')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_date():
    _missed().check_date()


def artifact_roots():
    # Do not mutate the old module's globals: its historical runtime is frozen.
    return tuple(_missed().ARTIFACT_ROOTS) + (DATA, MODELS, R)


def artifact_bytes():
    total = 0
    roots = artifact_roots()
    require(len(set(roots)) == len(roots), 'Duplicate artifact roots')
    for root in roots:
        if not root.exists():
            continue
        require(not root.is_symlink(), 'Artifact root must not be a symlink')
        for path in root.rglob('*'):
            require(not path.is_symlink(), 'Artifact paths must not be symlinks')
            if path.is_file():
                total += path.stat().st_size
    return total


def check_storage(reserve=RESERVE_BYTES):
    used = artifact_bytes()
    free = shutil.disk_usage('.').free
    require(used + reserve <= MAX_BYTES,
            'Combined missed-trial/final-B artifacts would exceed2GiB; preserve existing assets')
    require(free - reserve >= MIN_FREE_BYTES,
            'Free storage would fall below12GiB; pause without deleting existing assets')
    return dict(artifact_bytes=used, free_bytes=free)


@contextmanager
def storage_guard():
    """Use the same global lock as both completed missed-possession trials."""
    check_date()
    if getattr(_STORAGE, 'active', False):
        yield
        return
    directory = Path('data/tcn-missed')
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'storage.lock').open('a+') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        check_date()
        check_storage()
        _STORAGE.active = True
        try:
            yield
            check_storage(0)
        finally:
            _STORAGE.active = False


def write_json(path, value):
    with storage_guard():
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
        temporary.replace(path)


@contextmanager
def operation_lock(seed=None):
    """Coordinator locks only master; each worker locks only its own seed.

    Both also hold the existing shared compact-data reader lock. This permits
    two seed workers under one coordinator without recursively locking master.
    """
    require(seed is None or type(seed) is int and seed in SEEDS, 'Unregistered final-fit seed')
    check_date()
    DATA.mkdir(parents=True, exist_ok=True)
    handles = []
    try:
        own = DATA / ('operation.lock' if seed is None else f'seed-{seed}.lock')
        for path, mode in ((Path('data/tcn-expanded/operation.lock'), fcntl.LOCK_SH),
                           (own, fcntl.LOCK_EX)):
            handle = path.open('a+')
            handles.append(handle)
            try:
                fcntl.flock(handle, mode | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError('Conflicting compact writer or duplicate final-B operation') from error
        yield
    finally:
        for handle in reversed(handles):
            handle.close()


def committed_bytes(path):
    path = Path(path)
    require(not path.is_absolute() and '..' not in path.parts, 'Unsafe committed path')
    saved = subprocess.run(['git', 'show', 'HEAD:' + str(path)], capture_output=True)
    require(saved.returncode == 0 and hashlib.sha256(saved.stdout).hexdigest() == sha(path),
            'Final-B source/review differs from committed bytes: ' + str(path))


def _load(path):
    return json.loads(Path(path).read_text())


def validate_b_evidence(missed_signature):
    """Verify the accepted B decision by metadata, aggregate arithmetic and bytes."""
    old = _missed()
    bound = old.binding('b', missed_signature)
    trial_signature = hashlib.sha256((missed_signature + json.dumps(bound, sort_keys=True)).encode()).hexdigest()
    directory = MISSED / 'evaluation/b'
    completion_path, results_path, gate_path = (directory / name for name in
                                               ('completion.json', 'results.json', 'gate-v2.json'))
    review_path = MISSED / 'reviewed-b.json'
    committed_bytes(MISSED / 'reviewed-a.json')
    committed_bytes(review_path)
    completion, rows, review = _load(completion_path), _load(results_path), _load(review_path)
    require(completion.get('completed') is True and completion.get('trial') == 'b'
            and completion.get('registration') == missed_signature
            and completion.get('trial_signature') == trial_signature
            and completion.get('binding') == bound and completion.get('case_count') == 10
            and completion.get('contracts_passed') is True
            and completion.get('repeated_training_exact') is True
            and completion.get('production_changed') is False,
            'Final B requires complete, bound development evidence')
    require(completion['results_sha256'] == sha(results_path)
            and completion['gate_sha256'] == sha(gate_path), 'B result/gate fingerprints changed')
    parent_path = (MISSED / 'evaluation/a/results.json' if bound['parent_trial'] == 'a'
                   else old.BASELINE_RESULTS)
    require(sha(parent_path) == bound['parent_results_sha256'], 'B parent binding changed')
    parent = {(row['match'], row['condition']): row for row in _load(parent_path)}
    require(len(rows) == len(parent) == 10, 'Incomplete development cells')
    require({(r['match'], r['condition']) for r in rows} == {(m, c) for m in IDS for c in ('clean', 'targetlike')},
            'B development cells differ from the frozen split')
    evidence = {str(path) for path in (completion_path, results_path, gate_path, review_path,
                MISSED / 'reviewed-a.json', parent_path)}
    expected_proofs = {str(directory / 'fits' / f'{m}-{seed}.json') for m in IDS for seed in SEEDS}
    require(set(completion['fit_proofs']) == expected_proofs, 'B fit proof set differs')
    for name, digest in completion['fit_proofs'].items():
        require(sha(name) == digest, 'B fit proof changed: ' + name)
        proof = _load(name)
        match, seed = proof['match'], proof['seed']
        require(match in IDS and type(seed) is int and seed in SEEDS and proof['trial'] == 'b'
                and proof['trial_signature'] == trial_signature and proof['sampler'] == bound['sampler']
                and proof['training_steps'] == 40000 and proof['exact_repeat'] is True
                and proof['training_matches'] == ['idsse-' + m for m in IDS if m != match],
                'B fit proof identity/budget differs')
        require(name == str(directory / 'fits' / f'{match}-{seed}.json'), 'B proof path identity differs')
        require(sha(proof['checks_path']) == proof['checks_sha256'], 'B contracts log changed')
        expected_models = {f'models/tcn-missed/b/{match}/{seed}/{fit}/progress.pt' for fit in ('first', 'repeat')}
        require(set(proof['checkpoint_hashes']) == expected_models, 'B checkpoint path set differs')
        evidence.update((name, proof['checks_path']))
        for model_path, model_digest in proof['checkpoint_hashes'].items():
            require(sha(model_path) == model_digest, 'B checkpoint bytes changed')
            evidence.add(model_path)
    for row in rows:
        old_row = parent[row['match'], row['condition']]
        require(row['parent'] == old_row['candidate'], 'B parent metrics changed')
        require(row.get('reload_probabilities_equal_both_views') is True
                and row.get('csv_bytes_equal_reload_batch4') is True, 'Missing B inference equality proof')
        expected_csvs = [f'data/tcn-missed/b/predictions/{row["match"]}-{row["condition"]}-{tag}.csv'
                         for tag in ('first', 'reload', 'batch4')]
        require(row['csv_paths'] == expected_csvs, 'B prediction paths differ')
        for path in row['csv_paths']:
            require(sha(path) == row['csv_sha256'], 'B prediction changed')
            evidence.add(path)
        require(sha(row['parent_reconstruction_path']) == row['parent_csv_sha256']
                == old_row['csv_sha256'], 'B parent reconstruction changed')
        evidence.add(row['parent_reconstruction_path'])
    before = [dict(match=r['match'], condition=r['condition'], **r['parent']) for r in rows]
    after = [dict(match=r['match'], condition=r['condition'], **r['candidate']) for r in rows]
    gate = old.gate_v2(before, after)
    require(gate == _load(gate_path) and gate['quality_eligible'] is True, 'B no longer passes registered gate')
    require(review.get('reviewed') is True and review.get('accepted_under_registered_gate') is True
            and review.get('selected_trial') == 'b' and review.get('sampler') == bound['sampler']
            and review.get('loss') == 'cross_entropy_plus_0.1_segment_soft_iou'
            and review.get('results_sha256') == sha(results_path)
            and review.get('production_changed') is False
            and review.get('authorized_experiment_round_complete') is True,
            'Final fit requires committed accepted B review, without production promotion')
    return evidence


def registration():
    check_date()
    old = _missed()
    _, membership, missed_signature = old.registration()
    require(membership['development'] == list(IDS) and membership['final_fit_enabled'] is False,
            'Original split metadata changed')
    required_evidence = validate_b_evidence(missed_signature)
    locked = _load(R / 'inputs.json')
    require(set(locked) == {'code', 'evidence'}, 'Unexpected final-B source lock schema')
    mandatory = {str(R / name) for name in ('release_contract.py', 'final_training.py', 'protocol.md',
                 'membership.json', 'tests/test_release_contract.py', 'tests/test_final_training.py')}
    mandatory.update(('scripts/fit_tcn_final_b.py', 'docs/run-tcn-final-b.md'))
    require(mandatory <= set(locked['code']),
            'Missing final-B source locks: ' + ', '.join(sorted(mandatory - set(locked['code']))))
    require(required_evidence <= set(locked['evidence']),
            'Missing B evidence fingerprints: ' + ', '.join(sorted(required_evidence - set(locked['evidence']))))
    for group in locked.values():
        require(isinstance(group, dict), 'Final-B lock groups must be path/hash objects')
        for name, digest in group.items():
            path = Path(name)
            require(not path.is_absolute() and '..' not in path.parts, 'Unsafe final-B registered path')
            require(sha(path) == digest, 'Registered final-B source/evidence changed: ' + name)
    for name in (str(R / 'inputs.json'), *locked['code']):
        committed_bytes(name)
    final_membership = _load(R / 'membership.json')
    require(final_membership.get('training_matches') == list(KEYS)
            and set(final_membership.get('sealed_excluded', [])) == {'J03WQQ', 'J03WR9'}
            and final_membership.get('target_excluded') is True
            and final_membership.get('pff_excluded') is True,
            'Final fit must use exactly the five IDSSE development matches')
    signature = hashlib.sha256((sha(R / 'protocol.md') + sha(R / 'inputs.json')).encode()).hexdigest()
    return locked, signature
