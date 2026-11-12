"""Fixed release contracts; standard-library only until user invokes execution."""
from datetime import date, datetime
from importlib.metadata import version
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from zoneinfo import ZoneInfo

PROJECT = Path(__file__).resolve().parents[2]
ROOT = Path('experiments/tcn-winner-release-2026-11-12')
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
KEYS = tuple('idsse-' + match for match in IDS)
SCHEMA = 'final_IDSSE5_control40k_reset_v1'
MODELS = Path('models/tcn-winner-release')
TARGET_ASSETS = ('data/competition/tactical/BAR-ATH_tactical_atd.txt',
                 'data/competition/tactical/BAR-ATH_tactical_atd.xml')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 ** 2), b''):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def permitted_date(training=False):
    today = datetime.now(ZoneInfo('Asia/Kolkata')).date()
    require(today < date(2026, 11, 16) if training else today <= date(2026, 11, 17),
            'Training is frozen or the project action deadline has passed')


def check_membership(cases):
    require(tuple(case.key for case in cases) == KEYS,
            'Final fit requires exactly the ordered five approved IDSSE matches')
    require(all(case.provider == 'idsse' for case in cases), 'Unexpected training provider')


def expected_identity(signature, diagnostic):
    return dict(kind=SCHEMA, registration=signature, training_matches=list(KEYS),
                geometry_matches=[], total_steps=40000, stage_steps=20000, seed=20261106,
                view_seed=20261106 + 424242, window=250, halo=25, core=200, batch=8,
                optimizer='Adam', learning_rate=.001, gradient_clip=1.,
                supervised_gap_probability=.5,
                stage_boundary='reset_Adam_and_supervised_RNG_in_both_arms',
                architecture='original_motion_tcn_geometric_pretraining_head_v1',
                schema='original_encoded521_core9_observed_masked_ballXY_v1',
                slot_diagnostic=diagnostic)


def registration(training=False):
    permitted_date(training)
    for name in ('protocol.md', 'inputs.json'):
        path = ROOT / name
        saved = subprocess.run(['git', 'show', 'HEAD:' + str(path)], capture_output=True)
        require(saved.returncode == 0 and saved.stdout == path.read_bytes(),
                'Release registration must be committed: ' + str(path))
    locked = json.loads((ROOT / 'inputs.json').read_text())
    require(set(locked) == {'code', 'parent_evidence', 'prepared_manifests', 'target_assets', 'reference'},
            'Unexpected release lock schema')
    mandatory = ('scripts/fit_tcn_winner.py', 'scripts/export_tcn_winner.py',
                 str(ROOT / 'protocol.md'), str(ROOT / 'release_contract.py'),
                 str(ROOT / 'winner_training.py'), str(ROOT / 'requirements.txt'),
                 str(ROOT / 'environment-lock.txt'), str(ROOT / 'environment-snapshot.json'),
                 str(ROOT / 'dependency-license-metadata.json'),
                 str(ROOT / 'tests/test_winner_release.py'),
                 'experiments/tcn-pretrain-2026-11-11/pretrain_model.py',
                 'experiments/tcn-2026-11-10/tcn_candidate.py',
                 'experiments/tcn-expanded-2026-11-10/expanded_data.py',
                 'experiments/tcn-rotation-2026-11-11/rotation.py',
                 'scripts/prepare_tcn.py', 'src/possession/core.py', 'src/possession/features.py',
                 'src/possession/inputs.py', 'src/possession/decode.py',
                 'configs/competition.json', 'experiments/core-development/split.json')
    require(all(name in locked['code'] for name in mandatory), 'Incomplete release source lock')
    parent_root = 'experiments/tcn-pretrain-2026-11-11/'
    require(all(parent_root + name in locked['parent_evidence'] for name in (
        'evaluation/control/gate.json', 'evaluation/control/results.json',
        'inputs.json', 'membership.json', 'result-audit.json')),
        'Archived winning parent evidence is not fully pinned')
    require('reference/more-than-a-hack-2027-main/evaluation/possession_metrics.py'
            in locked['reference'], 'Official unchanged validator is not pinned')
    require(set(locked['prepared_manifests']) == {
        f'data/tcn-expanded/{key}/manifest.json' for key in KEYS}, 'Exactly five compact manifests required')
    require(set(locked['target_assets']) == set(TARGET_ASSETS), 'Unexpected target asset set')
    groups = ('code', 'parent_evidence', 'prepared_manifests') if training else ('code', 'target_assets', 'reference')
    for group in groups:
        for name, digest in locked[group].items():
            path = Path(name)
            require(not path.is_absolute() and '..' not in path.parts, 'Unsafe registered path')
            require(sha(path) == digest, 'Registered release file changed: ' + name)
            if group == 'code':
                saved = subprocess.run(['git', 'show', 'HEAD:' + name], capture_output=True)
                require(saved.returncode == 0 and hashlib.sha256(saved.stdout).hexdigest() == digest,
                        'Release source differs from committed version: ' + name)
    split = json.loads(Path('experiments/core-development/split.json').read_text())
    require(tuple(split['development']) == IDS and set(split['sealed']) == {'J03WQQ', 'J03WR9'},
            'Original approved split changed')
    snapshot = json.loads((ROOT / 'environment-snapshot.json').read_text())
    require(platform.python_version() == snapshot['python'] and platform.system() == snapshot['system']
            and platform.machine() == snapshot['machine'], 'Pinned Python/platform differs')
    environment = snapshot['packages']
    for package, expected in environment.items():
        require(version(package) == expected, 'Dependency version differs: ' + package)
    signature = hashlib.sha256((sha(ROOT / 'protocol.md') + sha(ROOT / 'inputs.json')).encode()).hexdigest()
    if training:
        gate = json.loads(Path('experiments/tcn-pretrain-2026-11-11/evaluation/control/gate.json').read_text())
        require(gate['quality_eligible'] is True and gate['repeated_training_exact'] is True,
                'Archived winning control has no passing eligibility proof')
        for name in locked['prepared_manifests']:
            manifest = json.loads(Path(name).read_text())
            require(set(manifest) == {'files'} and set(manifest['files']) == {
                'objects.npy', 'roles.npy', 'core.npy', 'gap_ball.npy', 'gap_core.npy',
                'labels.npy', 'metadata.json'}, 'Unexpected compact members')
            for member, digest in manifest['files'].items():
                require(sha(Path(name).parent / member) == digest, 'Compact training member changed')
    return locked, signature, environment


def reviewed_diagnostic(path, acknowledged):
    require(acknowledged, 'Review the completed slot diagnostic before explicitly acknowledging its risk')
    path = Path(path)
    # This evidence is diagnostic, never a stress-metric promotion threshold.
    record = json.loads(path.read_text())
    require(record.get('diagnostic_only') is True and record.get('completed') is True,
            'Current-winner slot diagnostic is incomplete')
    require(record.get('winner') == 'control40k_reset_rotation_penalty16',
            'Slot diagnostic belongs to a different model')
    require(record.get('parent_reproduced') is True and record.get('repeatability_passed') is True,
            'Slot diagnostic parent/repeatability evidence failed')
    require(isinstance(record.get('registration'), str) and len(record['registration']) == 64,
            'Slot diagnostic registration is missing')
    require(record.get('static_controls_within_tolerance') is True,
            'Slot diagnostic controls need bug/transfer review before final fitting')
    diagnostic_root = Path('experiments/tcn-winner-slot-audit-2026-11-12')
    require(path == diagnostic_root / 'decision.json', 'Use the registered current-winner diagnostic')
    require(record.get('repeatability_cases') == 40 and record.get('parent_reconstruction_cases') == 10
            and record.get('tests_pass') is True and record.get('quality_selection_performed') is False
            and record.get('model_promoted') is False and record.get('production_changed') is False,
            'Slot diagnostic completion/control evidence differs')
    for name in ('protocol.md', 'inputs.json'):
        source = diagnostic_root / name
        saved = subprocess.run(['git', 'show', 'HEAD:' + str(source)], capture_output=True)
        require(saved.returncode == 0 and saved.stdout == source.read_bytes(),
                'Slot diagnostic source registration is not committed')
    expected = hashlib.sha256((sha(diagnostic_root / 'protocol.md')
                               + sha(diagnostic_root / 'inputs.json')).encode()).hexdigest()
    require(record['registration'] == expected, 'Slot diagnostic registration signature differs')
    for name in ('results', 'controls', 'determinism', 'inputs'):
        require(sha(diagnostic_root / (name + '.json')) == record.get(name + '_sha256'),
                'Slot diagnostic evidence changed: ' + name)
    return dict(path=str(path), sha256=sha(path), human_review_acknowledged=True,
                registration=record['registration'])
