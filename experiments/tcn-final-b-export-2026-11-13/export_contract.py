"""Frozen-artifact delivery contracts; no training registration or model imports."""
from contextlib import contextmanager
from datetime import date, datetime
import fcntl
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import shutil
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path('experiments/tcn-final-b-export-2026-11-13')
FINAL = Path('experiments/tcn-final-b-2026-11-13')
WINNER = Path('experiments/tcn-winner-release-2026-11-12')
MISSED = Path('experiments/tcn-missed-2026-11-13')
MANIFEST = Path('models/tcn-final-b/manifest.json')
OUTPUT_ROOT = Path('data/competition/tcn-final-b-exports')
SEEDS = (20261106, 20261107)
KEYS = tuple('idsse-' + m for m in ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY'))
SCHEMA = 'final_five_trial_b_two_seed_original_motion_tcn_v1'
TARGET_ASSETS = ('data/competition/tactical/BAR-ATH_tactical_atd.txt',
                 'data/competition/tactical/BAR-ATH_tactical_atd.xml')
REFERENCE = 'reference/more-than-a-hack-2027-main/evaluation/possession_metrics.py'
MAX_BYTES, MIN_FREE, RESERVE = 2 * 1024 ** 3, 12 * 1024 ** 3, 64 * 1024 ** 2
ARTIFACT_ROOTS = (Path('data/tcn-missed'), Path('models/tcn-missed'), MISSED,
                  Path('data/tcn-final-b'), Path('models/tcn-final-b'), FINAL,
                  ROOT, OUTPUT_ROOT, Path('experiments/tcn-diagnostic-2026-11-13'),
                  Path('data/tcn-diagnostic'))
QUALIFICATION_ROOTS = (Path('data/tcn-final-b-clean-env'), Path('data/tcn-final-b-clean-clone'))
RUNTIME_CODE = ('scripts/export_tcn_final_b.py', str(ROOT / 'export_contract.py'),
    str(ROOT / 'protocol.md'), str(ROOT / 'tests/test_export.py'),
    'docs/run-tcn-final-b-export.md', str(FINAL / 'final_training.py'),
    'experiments/tcn-parallel-2026-11-12/parallel_model.py',
    'experiments/tcn-parallel-2026-11-12/parallel_training.py',
    'experiments/tcn-pretrain-2026-11-11/pretrain_model.py',
    'experiments/tcn-2026-11-10/tcn_candidate.py',
    'experiments/tcn-expanded-2026-11-10/expanded_data.py',
    'experiments/tcn-missed-2026-11-13/objectives.py',
    'experiments/tcn-rotation-2026-11-11/rotation.py', 'scripts/prepare_tcn.py',
    'src/possession/__init__.py', 'src/possession/core.py', 'src/possession/features.py',
    'src/possession/inputs.py', 'src/possession/decode.py', 'src/possession/external.py',
    'configs/competition.json', 'experiments/core-development/split.json',
    str(WINNER / 'environment-snapshot.json'), str(WINNER / 'environment-lock.txt'),
    str(WINNER / 'inputs.json'),
    str(FINAL / 'inputs.json'), str(FINAL / 'protocol.md'), str(FINAL / 'membership.json'),
    str(FINAL / 'final-fit-result-audit.json'), str(MISSED / 'reviewed-b.json'))


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 ** 2), b''):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def permitted_date(today=None):
    today = today or datetime.now(ZoneInfo('Asia/Kolkata')).date()
    require(today <= date(2026, 11, 17), 'Project action deadline has passed; preserve artifacts')


def safe_relative(name):
    path = Path(name)
    require(not path.is_absolute() and '..' not in path.parts, 'Unsafe registered path')
    return path


def committed(path):
    saved = subprocess.run(['git', 'show', 'HEAD:' + str(path)], capture_output=True)
    require(saved.returncode == 0 and hashlib.sha256(saved.stdout).hexdigest() == sha(path),
            'Delivery source is not committed unchanged: ' + str(path))


def final_signature():
    return hashlib.sha256((sha(FINAL / 'protocol.md') + sha(FINAL / 'inputs.json')).encode()).hexdigest()


def validate_manifest(value, signature, snapshot):
    require(value.get('schema') == SCHEMA and value.get('registration') == signature,
            'Wrong final ensemble identity')
    require(value.get('training_matches') == list(KEYS) and value.get('training_steps_per_member') == 40000,
            'Final membership or training budget changed')
    require(value.get('sampler') == 'short_mix'
            and value.get('loss') == 'cross_entropy_plus_0.1_segment_soft_iou'
            and value.get('class_order') == ['H', 'A', 'D']
            and value.get('scaler_policy') == 'zeros_ones_521', 'Final recipe changed')
    require(value.get('inference') == dict(rotation180_probability_weights=[.5, .5],
            seed_probability_weights=[.5, .5], switching_penalty=16), 'Inference recipe changed')
    require(value.get('environment') == snapshot and value.get('quality_evaluation_performed') is False
            and value.get('production_promoted') is False
            and value.get('private_export_completed') is False
            and value.get('target_accuracy') == 'unknown', 'Final provenance changed')
    require(value.get('source_lock_sha256') == sha(FINAL / 'inputs.json')
            and value.get('selection_review_sha256') == sha(MISSED / 'reviewed-b.json'),
            'Final source/review binding changed')
    require(set(value.get('members', {})) == {str(s) for s in SEEDS}, 'Exactly two members required')
    for seed in SEEDS:
        member = value['members'][str(seed)]
        base = Path('models/tcn-final-b') / str(seed)
        for key, suffix in (('model', 'first/progress.pt'), ('repeat_model', 'repeat/progress.pt'),
                            ('proof', 'proof.json')):
            require(member.get(key) == str(base / suffix), 'Unexpected final member path')
        for path_key, hash_key in (('model', 'sha256'), ('repeat_model', 'repeat_sha256'),
                                   ('proof', 'proof_sha256')):
            require(sha(member[path_key]) == member[hash_key], 'Member bytes changed')
        proof = load(member['proof'])
        require(proof.get('registration') == signature and proof.get('seed') == seed
                and proof.get('training_matches') == list(KEYS) and proof.get('steps') == 40000
                and proof.get('repeated_training_exact') is True
                and proof.get('checkpoint_state_reload_exact') is True,
                'Member repeat/reload proof differs')
        require(proof.get('checkpoint_hashes') == {member['model']: member['sha256'],
                member['repeat_model']: member['repeat_sha256']}, 'Checkpoint proof differs')
        log_path = safe_relative(proof['checks_path'])
        require(log_path.parent == FINAL / 'evaluation' and log_path.name.startswith('checks-')
                and sha(log_path) == proof['checks_sha256'], 'Final checks log differs')


def required_evidence(manifest):
    paths = {str(MANIFEST)}
    for member in manifest['members'].values():
        paths.update(member[k] for k in ('model', 'repeat_model', 'proof'))
        paths.add(load(member['proof'])['checks_path'])
    return paths


def registration():
    permitted_date()
    locked = load(ROOT / 'inputs.json')
    require(set(locked) == {'code', 'evidence', 'target_assets', 'reference'}, 'Wrong export lock schema')
    require(set(RUNTIME_CODE) <= set(locked['code']), 'Incomplete delivery source lock')
    require(set(locked['target_assets']) == set(TARGET_ASSETS)
            and set(locked['reference']) == {REFERENCE}, 'Unexpected target/reference input')
    previous = load(WINNER / 'inputs.json')
    require(locked['target_assets'] == previous['target_assets']
            and locked['reference'][REFERENCE] == previous['reference'][REFERENCE],
            'Target assets or official validator differ from previously frozen release')
    for group, paths in locked.items():
        require(isinstance(paths, dict), 'Lock entries must be path/hash objects')
        for name, digest in paths.items():
            path = safe_relative(name)
            require(sha(path) == digest, 'Registered export bytes differ: ' + name)
            if group == 'code':
                committed(path)
    committed(ROOT / 'inputs.json')
    value, snapshot = load(MANIFEST), load(WINNER / 'environment-snapshot.json')
    require(required_evidence(value) == set(locked['evidence']), 'Wrong final artifact evidence set')
    validate_manifest(value, final_signature(), snapshot)
    audit = load(FINAL / 'final-fit-result-audit.json')
    require(audit['manifest_sha256'] == sha(MANIFEST) and audit['fit_count'] == 4
            and audit['logged_contracts'] == 104, 'Audited final artifact differs')
    require(platform.python_version() == snapshot['python'] and platform.system() == snapshot['system']
            and platform.machine() == snapshot['machine'], 'Pinned Python/platform differs')
    for package, expected in snapshot['packages'].items():
        require(version(package) == expected, 'Dependency differs: ' + package)
    split = load('experiments/core-development/split.json')
    require(split['development'] == [key[6:] for key in KEYS]
            and set(split['sealed']) == {'J03WQQ', 'J03WR9'}, 'Frozen split changed')
    signature = hashlib.sha256((sha(ROOT / 'protocol.md') + sha(ROOT / 'inputs.json')).encode()).hexdigest()
    return value, signature, snapshot


def artifact_bytes():
    total, seen = 0, set()
    # The fresh clone links models/data to the original workspace. Include both
    # workspaces' artifact trees so it cannot evade the combined storage cap.
    model_root = Path('models/tcn-final-b').resolve()
    project_roots = {Path.cwd().resolve(), model_root.parents[1]}
    for project in project_roots:
        for relative in ARTIFACT_ROOTS:
            root = project / relative
            if not root.exists():
                continue
            for path in root.resolve().rglob('*'):
                require(not path.is_symlink(), 'Artifact tree contains a symlink')
                if path.is_file() and path.resolve() not in seen:
                    seen.add(path.resolve())
                    total += path.stat().st_size
    for project in project_roots:
        for relative in QUALIFICATION_ROOTS:
            root = project / relative
            if not root.exists():
                continue
            # venv interpreter links and clone shared inputs are references,
            # not duplicate bytes; rglob does not descend directory symlinks.
            for path in root.rglob('*'):
                if not path.is_symlink() and path.is_file() and path.resolve() not in seen:
                    seen.add(path.resolve())
                    total += path.stat().st_size
    return total


def check_storage(reserve=RESERVE):
    used, free = artifact_bytes(), shutil.disk_usage('.').free
    require(used + reserve <= MAX_BYTES, 'Combined artifact budget exceeds2GiB; preserve existing assets')
    require(free - reserve >= MIN_FREE, 'Free storage would fall below12GiB; pause without deleting assets')
    return dict(artifact_bytes=used, free_bytes=free)


@contextmanager
def write_guard():
    permitted_date()
    directory = Path('data/tcn-missed')
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'storage.lock').open('a+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        permitted_date()
        check_storage()
        yield
        check_storage(0)


def write_json(path, value):
    with write_guard():
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
        temporary.replace(path)


def validate_output(path):
    path = Path(path)
    require(path.parent == OUTPUT_ROOT and path.name in ('local', 'clean', 'clone'),
            'Use a fixed private final-B local, clean or clone output')
    require(not path.exists() and not path.is_symlink(), 'Output exists; preserve prior evidence')
    return path


@contextmanager
def operation_lock():
    directory = Path('data/tcn-final-b')
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'export.lock').open('a+') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError('Another final-B export is active') from error
        yield
