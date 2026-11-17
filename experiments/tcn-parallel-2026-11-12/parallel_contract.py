"""Registration and aggregate gates for two fixed external-only comparisons."""
from datetime import date, datetime
import hashlib
from importlib.metadata import version
import json
import math
from pathlib import Path
import platform
import statistics
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path('experiments/tcn-parallel-2026-11-12')
PARENT = Path('experiments/tcn-pretrain-2026-11-11')
IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
SETTINGS = ('clean', 'targetlike')
ARMS = ('attention', 'ensemble')


def require(ok, message):
    if not ok:
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


def check_date():
    require(datetime.now(ZoneInfo('Asia/Kolkata')).date() < date(2026, 11, 16),
            'Research is frozen at the start of November16; preserve partial evidence')


def expected_membership():
    split = json.loads(Path('experiments/core-development/split.json').read_text())
    require(split['development'] == list(IDS)
            and set(split['sealed']) == {'J03WQQ', 'J03WR9'}, 'Original split changed')
    return dict(development=list(IDS),
                supervised_folds={m: ['idsse-' + n for n in IDS if n != m] for m in IDS},
                sealed_excluded=split['sealed'], target_excluded=True, pff_excluded=True,
                held_out_excluded=True, final_fit_enabled=False)


def verify_hashes(locked):
    for group in locked.values():
        for name, digest in group.items():
            require(not Path(name).is_absolute() and '..' not in Path(name).parts,
                    'Unsafe registered path')
            require(sha(name) == digest, 'Registered file changed: ' + name)


def registration():
    check_date()
    locked = json.loads((ROOT / 'inputs.json').read_text())
    require(set(locked) == {'code', 'reference', 'data', 'prepared_manifests', 'parent_evidence'},
            'Unexpected registration schema')
    mandatory = ['scripts/run_tcn_parallel.py', str(ROOT / 'protocol.md'),
                 str(ROOT / 'membership.json'), str(ROOT / 'requirements.txt'),
                 str(ROOT / 'parallel_contract.py'), str(ROOT / 'parallel_model.py'),
                 str(ROOT / 'parallel_training.py'), str(ROOT / 'tests/test_parallel_contract.py'),
                 str(ROOT / 'tests/test_parallel_model.py'), str(ROOT / 'tests/test_parallel_training.py'),
                 'docs/run-tcn-parallel.md', 'configs/competition.json',
                 'experiments/core-development/split.json',
                 'experiments/tcn-winner-release-2026-11-12/environment-snapshot.json',
                 'experiments/tcn-2026-11-10/tcn_candidate.py',
                 'experiments/tcn-pretrain-2026-11-11/pretrain_model.py',
                 'experiments/tcn-expanded-2026-11-10/expanded_data.py',
                 'experiments/tcn-rotation-2026-11-11/rotation.py',
                 'experiments/tcn-winner-slot-audit-2026-11-12/winner_contract.py',
                 'scripts/review_frozen.py', 'scripts/evaluate_pff.py']
    missing = [name for name in mandatory if name not in locked['code']]
    require(not missing, 'Missing committed source fingerprints: ' + ', '.join(missing))
    require(not set(locked['code']) & set(locked['reference']), 'Reference/code categories overlap')
    require('reference/more-than-a-hack-2027-main/evaluation/possession_metrics.py'
            in locked['reference'], 'Unchanged official scorer must be pinned')
    require(set(locked['data']) == {f'data/tcn-prepared/{m}-{c}.npz'
                                   for m in IDS for c in SETTINGS}, 'Frozen ten evaluation cases required')
    require(set(locked['prepared_manifests']) == {
        f'data/tcn-expanded/idsse-{m}/manifest.json' for m in IDS}, 'Exactly five training compacts required')
    parents = [str(PARENT / name) for name in ('protocol.md', 'inputs.json', 'membership.json',
               'evaluation/control/results.json', 'evaluation/control/gate.json')]
    for match in IDS:
        parents.append(str(PARENT / 'evaluation/control' / (match + '.json')))
        parents += [f'models/tcn-pretrain/evaluation/control/{match}/{fit}/progress.pt'
                    for fit in ('first', 'repeat')]
        parents += [f'data/tcn-pretrain/predictions/control/{match}-{c}-{tag}.csv'
                    for c in SETTINGS for tag in ('first', 'reload', 'batch4')]
    missing = [name for name in parents if name not in locked['parent_evidence']]
    require(not missing, 'Missing frozen parent evidence: ' + ', '.join(missing))
    verify_hashes(locked)
    for name in [str(ROOT / 'inputs.json'), *locked['code']]:
        saved = subprocess.run(['git', 'show', 'HEAD:' + name], capture_output=True)
        require(saved.returncode == 0 and hashlib.sha256(saved.stdout).hexdigest() == sha(name),
                'Registration/source must match committed bytes: ' + name)
    membership = json.loads((ROOT / 'membership.json').read_text())
    require(membership == expected_membership(), 'Registered membership differs')
    environment = json.loads(Path('experiments/tcn-winner-release-2026-11-12/environment-snapshot.json').read_text())
    require(platform.python_version() == environment['python']
            and platform.machine() == environment['machine']
            and platform.system() == environment['system'], 'Python/platform differs')
    for package, expected in environment['packages'].items():
        require(version(package) == expected, 'Dependency version differs: ' + package)
    for name in locked['prepared_manifests']:
        manifest = json.loads(Path(name).read_text())
        require(set(manifest) == {'files'} and set(manifest['files']) == {
            'objects.npy', 'roles.npy', 'core.npy', 'gap_ball.npy', 'gap_core.npy',
            'labels.npy', 'metadata.json'}, 'Unexpected compact members')
        for member, digest in manifest['files'].items():
            require(sha(Path(name).parent / member) == digest, 'Compact member changed')
    parent_gate = json.loads((PARENT / 'evaluation/control/gate.json').read_text())
    require(parent_gate['quality_eligible'] is True and parent_gate['repeated_training_exact'] is True,
            'Frozen parent eligibility/repeat proof differs')
    signature = hashlib.sha256((sha(ROOT / 'protocol.md') + sha(ROOT / 'inputs.json')).encode()).hexdigest()
    return locked, membership, signature


def cell_index(rows):
    index = {(v['match'], v['condition']): v for v in rows}
    require(len(rows) == 10 and set(index) == {(m, c) for m in IDS for c in SETTINGS},
            'Exactly ten unique match/condition cells required')
    for row in rows:
        for metric in ('spellF1', 'macroF1'):
            value = row[metric]
            require(isinstance(value, (int, float)) and math.isfinite(value) and 0 <= value <= 1,
                    'Invalid aggregate metric')
    return index


def gate(before, after, contracts=True, repeats=True):
    old, new = cell_index(before), cell_index(after)
    def paired_delta(match, metric):
        return ((new[match, 'clean'][metric] + new[match, 'targetlike'][metric]) / 2
                - (old[match, 'clean'][metric] + old[match, 'targetlike'][metric]) / 2)
    spell = {m: paired_delta(m, 'spellF1') for m in IDS}
    macro = {m: paired_delta(m, 'macroF1') for m in IDS}
    primary = {m: new[m, 'targetlike']['spellF1'] - old[m, 'targetlike']['spellF1'] for m in IDS}
    median_spell, median_macro = statistics.median(spell.values()), statistics.median(macro.values())
    median_primary = statistics.median(primary.values())
    wins = sum(value > 0 for value in spell.values())
    existing = median_spell > 0 and wins >= 3 and median_macro >= -.01 - 1e-12
    return dict(quality_eligible=bool(existing and median_primary >= .01 and contracts and repeats),
                existing_gate=existing, primary_median_delta=median_primary,
                paired_median_spell_delta=median_spell, paired_median_macro_delta=median_macro,
                matches_improved=wins, primary_deltas=primary, paired_spell_deltas=spell,
                paired_macro_deltas=macro, contracts_passed=bool(contracts), repeated_training_exact=bool(repeats),
                production_changed=False, sealed_opened=False, target_accuracy='unknown')


def ordered_decision(parent, attention, ensemble):
    attention_gate = gate(parent, attention)
    selected = 'attention' if attention_gate['quality_eligible'] else 'parent'
    ensemble_parent = attention if selected == 'attention' else parent
    ensemble_gate = gate(ensemble_parent, ensemble)
    if ensemble_gate['quality_eligible']:
        selected = 'ensemble'
    return dict(order=['attention', 'ensemble'], attention_vs_parent=attention_gate,
                ensemble_compared_against='attention' if attention_gate['quality_eligible'] else 'parent',
                ensemble_vs_current_best=ensemble_gate, selected_development_candidate=selected,
                combined_attention_ensemble_tested=False, production_changed=False,
                automatic_followup=False, target_accuracy='unknown')
