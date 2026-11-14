"""Immutable diagnostic registration and bounded writes; no training entrypoint."""
from contextlib import contextmanager
import fcntl
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

R = Path('experiments/tcn-diagnostic-2026-11-13')
DATA = Path('data/tcn-diagnostic')
ARTIFACT_ROOTS = tuple(map(Path, (
    'data/tcn-missed', 'models/tcn-missed', 'experiments/tcn-missed-2026-11-13',
    'data/tcn-final-b', 'models/tcn-final-b', 'experiments/tcn-final-b-2026-11-13',
    'experiments/tcn-final-b-export-2026-11-13', 'data/competition/tcn-final-b-exports',
    str(R), str(DATA))))
QUALIFICATION_ROOTS = tuple(map(Path, ('data/tcn-final-b-clean-env',
                                       'data/tcn-final-b-clean-clone')))


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8*1024**2), b''):
            digest.update(chunk)
    return digest.hexdigest()


def check_storage(reserve=64*1024**2):
    used = 0
    for root in ARTIFACT_ROOTS:
        require(not root.is_symlink(), 'Symlink artifact root rejected')
        if root.exists():
            for path in root.rglob('*'):
                require(not path.is_symlink(), 'Symlink artifact rejected')
                if path.is_file():
                    used += path.stat().st_size
    # Qualification clone intentionally shares private assets by symlink; count
    # its regular files and environment once, never traverse those shared links.
    for root in QUALIFICATION_ROOTS:
        require(not root.is_symlink(), 'Qualification root must not be a symlink')
        if root.exists():
            used += sum(path.stat().st_size for path in root.rglob('*')
                        if not path.is_symlink() and path.is_file())
    require(used+reserve <= 2*1024**3, 'Combined artifacts exceed 2GiB; no deletion performed')
    require(shutil.disk_usage('.').free-reserve >= 12*1024**3,
            'Free space would fall below 12GiB; no deletion performed')


@contextmanager
def storage_guard():
    from contract import check_date
    check_date()
    with Path('data/tcn-missed/storage.lock').open('a+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        check_date(); check_storage()
        yield
        check_storage(0)


def save(path, value):
    with storage_guard():
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
        temporary.replace(path)


def registration():
    from contract import registration as parent_registration, committed_bytes
    _, _, parent_signature = parent_registration()
    locked = json.loads((R/'inputs.json').read_text())
    require(set(locked) == {'code', 'evidence'}, 'Diagnostic lock schema differs')
    mandatory = {str(R/name) for name in ('diagnostics.py', 'diagnostic_contract.py', 'protocol.md',
        'tests/test_diagnostics.py', 'tests/test_runner.py')}
    mandatory.update(('scripts/diagnose_tcn_possessions.py', 'docs/run-tcn-diagnostic.md'))
    require(mandatory <= set(locked['code']), 'Diagnostic source locks incomplete')
    base = Path('experiments/tcn-missed-2026-11-13')
    evidence = {str(base/('reviewed-'+trial+'.json')) for trial in ('a', 'b')}
    for trial in ('a', 'b'):
        evidence.update(str(base/'evaluation'/trial/name) for name in ('results.json', 'completion.json', 'gate-v2.json'))
        evidence.update(str(base/'evaluation'/trial/'fits'/f'{match}-{seed}.json')
            for match in ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
            for seed in (20261106, 20261107))
    require(evidence <= set(locked['evidence']), 'Diagnostic completed-evidence locks incomplete')
    for group in locked.values():
        for name, digest in group.items():
            path = Path(name)
            require(not path.is_absolute() and '..' not in path.parts, 'Unsafe registered path')
            require(sha(path) == digest, 'Diagnostic registered file changed: '+name)
    for name in (*locked['code'], str(R/'inputs.json')):
        committed_bytes(name)
    signature = hashlib.sha256((sha(R/'inputs.json')+sha(R/'protocol.md')+parent_signature).encode()).hexdigest()
    return signature, parent_signature


@contextmanager
def operation_lock():
    DATA.mkdir(parents=True, exist_ok=True)
    with (DATA/'operation.lock').open('a+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with Path('data/tcn-expanded/operation.lock').open('a+') as data:
            fcntl.flock(data, fcntl.LOCK_SH | fcntl.LOCK_NB)
            yield
