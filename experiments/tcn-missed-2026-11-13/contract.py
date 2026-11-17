"""Versioned positive-gain gate, immutable registration and bounded local writes.

Imports perform no model, scoring, data-array or runtime-test execution.
"""
from contextlib import contextmanager
from datetime import date, datetime
import fcntl
import hashlib
import json
import math
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import threading
from zoneinfo import ZoneInfo

ROOT = R = Path('experiments/tcn-missed-2026-11-13')
LEGACY = Path('experiments/tcn-parallel-2026-11-12')
BASELINE_RESULTS = LEGACY / 'evaluation/ensemble/results.json'
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
SETTINGS = ('clean', 'targetlike')
GATE_VERSION = 'positive_median_v2'
ARTIFACT_ROOTS = (Path('data/tcn-missed'), Path('models/tcn-missed'), ROOT)
MAX_BYTES = 2 * 1024 ** 3
MIN_FREE_BYTES = 12 * 1024 ** 3
RESERVE_BYTES = 64 * 1024 ** 2
_STORAGE = threading.local()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 ** 2), b''):
            result.update(block)
    return result.hexdigest()


def check_date():
    require(datetime.now(ZoneInfo('Asia/Kolkata')).date() < date(2026, 11, 16),
            'Research frozen at the start of November16; preserve partial evidence')


def artifact_bytes():
    total = 0
    for root in ARTIFACT_ROOTS:
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
            'New-trial artifacts would exceed2GiB; preserve evidence, no automatic deletion')
    require(free - reserve >= MIN_FREE_BYTES,
            'Free disk would fall below12GiB; pause without deleting assets')
    return dict(artifact_bytes=used, free_bytes=free)


@contextmanager
def storage_guard():
    """Serialize new writes across jobs; reserve64MiB for one atomic operation.

    The post-write check also catches an unexpectedly oversized operation. All
    writers use this guard; checkpoint reservation is larger than their model
    and optimizer states. Nested calls in one thread reuse the same lock.
    """
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
def operation_lock(trial):
    require(trial in ('a', 'b'), 'Only the two authorized trials are allowed')
    check_date()
    directory = Path('data/tcn-missed') / trial
    directory.mkdir(parents=True, exist_ok=True)
    handles = []
    try:
        for path, mode in ((Path('data/tcn-expanded/operation.lock'), fcntl.LOCK_SH),
                           (directory / 'operation.lock', fcntl.LOCK_EX)):
            handle = path.open('a+')
            handles.append(handle)
            try:
                fcntl.flock(handle, mode | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError('Conflicting data writer or duplicate trial operation') from error
        yield
    finally:
        for handle in reversed(handles):
            handle.close()


def cell_index(rows):
    require(isinstance(rows, list), 'Metrics must be a list of ten aggregate cells')
    index = {(row['match'], row['condition']): row for row in rows}
    require(len(rows) == 10 and set(index) == {(m, c) for m in IDS for c in SETTINGS},
            'Exactly ten unique development match/condition cells required')
    for row in rows:
        for key in ('spellF1', 'macroF1'):
            value = row[key]
            require(type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1,
                    'Invalid metric: ' + key)
    return index


def gate_v2(before, after, contracts=True, repeats=True):
    """Only the primary minimum changes from v1: strictly positive, not >=.01."""
    require(type(contracts) is bool and type(repeats) is bool, 'Proof flags must be boolean')
    old, new = cell_index(before), cell_index(after)
    def paired(match, metric):
        return ((new[match, 'clean'][metric] + new[match, 'targetlike'][metric]) / 2
                - (old[match, 'clean'][metric] + old[match, 'targetlike'][metric]) / 2)
    spell = {m: paired(m, 'spellF1') for m in IDS}
    macro = {m: paired(m, 'macroF1') for m in IDS}
    primary = {m: new[m, 'targetlike']['spellF1'] - old[m, 'targetlike']['spellF1'] for m in IDS}
    median_spell = statistics.median(spell.values())
    median_macro = statistics.median(macro.values())
    median_primary = statistics.median(primary.values())
    wins = sum(delta > 0 for delta in spell.values())
    existing = median_spell > 0 and wins >= 3 and median_macro >= -.01 - 1e-12
    return dict(gate_version=GATE_VERSION,
                quality_eligible=bool(existing and median_primary > 0 and contracts and repeats),
                existing_gate=existing, primary_median_delta=median_primary,
                paired_median_spell_delta=median_spell, paired_median_macro_delta=median_macro,
                matches_improved=wins, primary_deltas=primary, paired_spell_deltas=spell,
                paired_macro_deltas=macro, contracts_passed=contracts, repeated_training_exact=repeats,
                production_changed=False, sealed_opened=False, target_accuracy='unknown')


def committed_bytes(path):
    path = Path(path)
    require(not path.is_absolute() and '..' not in path.parts, 'Unsafe committed path')
    saved = subprocess.run(['git', 'show', 'HEAD:' + str(path)], capture_output=True)
    require(saved.returncode == 0 and hashlib.sha256(saved.stdout).hexdigest() == sha(path),
            'Source or review must match committed bytes: ' + str(path))


def registration():
    check_date()
    sys.path.insert(0, str(LEGACY.resolve()))
    from parallel_contract import registration as old_registration
    _, membership, _ = old_registration()
    locked = json.loads((R / 'inputs.json').read_text())
    require(set(locked) == {'code', 'evidence'}, 'Unexpected missed-trials lock schema')
    mandatory = {str(R / name) for name in ('contract.py', 'training.py', 'objectives.py',
                 'protocol.md', 'policy-v2.json', 'membership.json', 'requirements.txt', 'tests/test_contract.py',
                 'tests/test_training_objectives.py')}
    mandatory.update(('scripts/run_tcn_missed.py', 'docs/run-tcn-missed.md'))
    require(mandatory <= set(locked['code']),
            'Missing committed new source locks: ' + ', '.join(sorted(mandatory - set(locked['code']))))
    require(str(BASELINE_RESULTS) in locked['evidence'], 'Baseline result must be fingerprinted')
    for group in locked.values():
        require(isinstance(group, dict), 'Lock groups must be path/hash objects')
        for name, digest in group.items():
            path = Path(name)
            require(not path.is_absolute() and '..' not in path.parts, 'Unsafe registered path')
            require(sha(path) == digest, 'Registered file changed: ' + name)
    for name in (str(R / 'inputs.json'), *locked['code']):
        committed_bytes(name)
    require(json.loads((R / 'membership.json').read_text()) == membership, 'New membership differs')
    policy = json.loads((R / 'policy-v2.json').read_text())
    rows = json.loads(BASELINE_RESULTS.read_text())
    before = [dict(match=r['match'], condition=r['condition'], **r['parent']) for r in rows]
    after = [dict(match=r['match'], condition=r['condition'], **r['candidate']) for r in rows]
    require(policy['ensemble_gate_v2'] == gate_v2(before, after)
            and policy['retrospective'] is True and policy['production_changed'] is False,
            'Policy amendment differs from new gate or changes production')
    signature = hashlib.sha256((sha(R / 'protocol.md') + sha(R / 'inputs.json')).encode()).hexdigest()
    return locked, membership, signature


def _completed_a(signature):
    directory = R / 'evaluation/a'
    completion_path = directory / 'completion.json'
    completion = json.loads(completion_path.read_text())
    results_path = directory / 'results.json'
    require(completion.get('completed') is True and completion.get('registration') == signature
            and completion.get('contracts_passed') is True
            and completion.get('repeated_training_exact') is True
            and completion.get('results_sha256') == sha(results_path),
            'Trial A lacks bound completion/repeat/contracts evidence')
    rows = json.loads(results_path.read_text())
    baseline = {(r['match'], r['condition']): r['candidate']
                for r in json.loads(BASELINE_RESULTS.read_text())}
    require(len(rows) == 10 and len(baseline) == 10, 'Incomplete A/baseline result set')
    for row in rows:
        require(row['parent'] == baseline.get((row['match'], row['condition'])),
                'Trial A must compare against the registered two-seed ensemble')
    before = [dict(match=r['match'], condition=r['condition'], **r['parent']) for r in rows]
    after = [dict(match=r['match'], condition=r['condition'], **r['candidate']) for r in rows]
    return completion_path, results_path, gate_v2(before, after)


def expected_review_a(signature):
    """Create only after runner verifies every fold/model/CSV proof independently."""
    completion_path, results_path, gate = _completed_a(signature)
    accepted = gate['quality_eligible']
    return dict(registration=signature, reviewed=True, accepted=accepted,
                sampler='short_mix' if accepted else 'uniform',
                parent_trial='a' if accepted else 'baseline',
                parent_results_sha256=sha(results_path if accepted else BASELINE_RESULTS),
                a_completion_sha256=sha(completion_path))


def binding(trial, signature):
    require(trial in ('a', 'b'), 'Only trials a and b authorized')
    if trial == 'a':
        return dict(sampler='short_mix', parent_trial='baseline',
                    parent_results_sha256=sha(BASELINE_RESULTS))
    path = R / 'reviewed-a.json'
    require(path.exists(), 'Trial B blocked until Trial A is reviewed and its decision committed')
    record = json.loads(path.read_text())
    require(record == expected_review_a(signature), 'Reviewed Trial A decision is stale or differs from gate')
    committed_bytes(path)
    return dict(sampler=record['sampler'], parent_trial=record['parent_trial'],
                parent_results_sha256=record['parent_results_sha256'], reviewed_a_sha256=sha(path))
