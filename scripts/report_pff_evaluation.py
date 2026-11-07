"""Validate completed aggregate PFF evaluations and write an auditable report.

Reads only experiment manifests/aggregate results. Never reads raw assets, labels,
prediction arrays or model files. Refuses partial cohorts/results/cost records.
"""
import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fmt(value, digits=6):
    return 'undefined' if value is None else f'{value:.{digits}f}'


def subset_metrics(s):
    keys = ['TP_D', 'FP_D', 'FN_D', 'TN_D']
    require(all(isinstance(s[k], int) and s[k] >= 0 for k in keys), 'Invalid confusion counts')
    tp, fp, fn, tn = (s[k] for k in keys)
    require(tp + fp + fn + tn == s['frames'], 'Subset denominator mismatch')
    require(tp + fn == s['true_D'] and tn + fp == s['true_live'], 'Class-support mismatch')
    div = lambda n, d: n / d if d else None
    f1d, f1l = div(2 * tp, 2 * tp + fp + fn), div(2 * tn, 2 * tn + fp + fn)
    macro = (f1d + f1l) / 2 if s['true_D'] and s['true_live'] else None
    expected = {'D_precision': div(tp, tp + fp), 'D_recall': div(tp, tp + fn),
                'D_f1': f1d, 'live_f1': f1l, 'live_recall': div(tn, tn + fp),
                'predicted_D_share': div(tp + fp, s['frames'])}
    for k, v in expected.items():
        require((v is None and s[k] is None) or
                (v is not None and s[k] is not None and math.isclose(v, s[k], abs_tol=1e-10)),
                'Stored subset metric differs from counts: ' + k)
    return macro


def validate_rows(rows, expected_keys, key_function):
    keys = [key_function(r) for r in rows]
    require(len(keys) == len(set(keys)) and set(keys) == set(expected_keys),
            'Partial, duplicated or unexpected evaluation cells')
    for r in rows:
        require(all(isinstance(r[k], (int, float)) and math.isfinite(r[k]) and 0 <= r[k] <= 1
                    for k in ['spellF1', 'macroF1', 'known_label_fraction']), 'Invalid metric range')
        require(r['known_frames'] > 0, 'No known-label evaluation support')
        s = r['subsets']
        require(set(s) == {'natural_missing', 'newly_masked', 'all_missing', 'observed'},
                'Missing diagnostic subset')
        for v in s.values():
            subset_metrics(v)
        require(s['all_missing']['frames'] + s['observed']['frames'] == r['known_frames'],
                'Observed/missing denominator mismatch')
        require(s['natural_missing']['frames'] + s['newly_masked']['frames'] == s['all_missing']['frames'],
                'Natural/newly missing union mismatch')
        require(r['condition'] != 'clean' or s['newly_masked']['frames'] == 0,
                'Clean condition has newly masked frames')


def build_report(root):
    split = read(Path('experiments/pff-intake/split.json'))
    admission_path = Path('experiments/pff-admission/admission.json')
    admission = read(admission_path)
    expected_all = set(split['pff_additional_training']) | set(split['pff_transfer_holdout'])
    require(len(admission) == 64 and {r['match'] for r in admission} == expected_all,
            'Admission matrix must contain each of the 64 fixed matches once')
    require(len({r['match'] for r in admission}) == len(admission), 'Duplicate admission match')
    cohort, lock = read(root / 'cohort.json'), read(root / 'cohort-lock.json')
    require(cohort == lock, 'Cohort differs from pre-fit lock')
    require(cohort['admission_sha256'] == hashlib.sha256(admission_path.read_bytes()).hexdigest(),
            'Admission hash differs from locked cohort')
    passed = {r['match'] for r in admission if r['status'] == 'pass'}
    train = [m for m in split['pff_additional_training'] if m in passed]
    held = [m for m in split['pff_transfer_holdout'] if m in passed]
    require(cohort['training'] == train and cohort['transfer_holdout'] == held,
            'Cohort is not the fixed split intersected with strict passes')
    require(len(train) >= 2 and len(held) >= 2 and not set(train) & set(held), 'Insufficient/disjoint cohort')
    ids = split['idsse_development']
    require(len(ids) == 5 and not set(ids) & set(split['idsse_sealed_excluded_from_all_training']),
            'IDSSE cohort contract failed')
    a, b = read(root / 'train-more-results.json'), read(root / 'transfer-results.json')
    conditions = ['clean', 'targetlike']
    validate_rows(a, {(m, arm, c) for m in ids for arm in ['parent', 'expanded'] for c in conditions},
                  lambda r: (r['match'], r['arm'], r['condition']))
    forward, reverse = 'IDSSE5_to_PFF_holdout', 'PFF_training_to_IDSSE5'
    validate_rows(b, {(m, forward, c) for m in held for c in conditions} |
                  {(m, reverse, c) for m in ids for c in conditions},
                  lambda r: (r['match'], r['direction'], r['condition']))
    require(all(r['provider'] == 'idsse' and r['inference_blocks'] == 'label_valid_runs_legacy' for r in a),
            'A provider/segmentation contract failed')
    require(all(r['inference_blocks'] == 'halves_only' and
                r['provider'] == ('pff' if r['direction'] == forward else 'idsse') for r in b),
            'Transfer provider/segmentation contract failed')
    costs = read(root / 'cost.json')
    require(len(costs) == 11, 'Cost records incomplete: expected 10 paired fits plus reverse fit')
    require({(x.get('match'), x['arm']) for x in costs} ==
            {(m, arm) for m in ids for arm in ['parent', 'expanded']} | {(None, 'reverse_PFF_only')},
            'Missing or duplicated cost arm')
    require(all(x['training_rows'] > 0 and x['seconds'] >= 0 for x in costs), 'Invalid fit cost')
    gate = read(root / 'gate.json')
    cells = {(r['match'], r['arm'], r['condition']): r for r in a}
    delta = {k: {} for k in ['paired_spell_deltas', 'paired_macro_deltas', 'primary_deltas']}
    for m in ids:
        for metric, key in [('spellF1', 'paired_spell_deltas'), ('macroF1', 'paired_macro_deltas')]:
            delta[key][m] = statistics.mean(cells[m, 'expanded', c][metric] - cells[m, 'parent', c][metric]
                                           for c in conditions)
        delta['primary_deltas'][m] = (cells[m, 'expanded', 'targetlike']['spellF1'] -
                                      cells[m, 'parent', 'targetlike']['spellF1'])
    for key, values in delta.items():
        require(set(gate[key]) == set(ids) and all(math.isclose(values[m], gate[key][m], abs_tol=1e-10)
                                                   for m in ids), 'Gate delta mismatch: ' + key)
    med_s = statistics.median(delta['paired_spell_deltas'].values())
    med_f = statistics.median(delta['paired_macro_deltas'].values())
    med_c = statistics.median(delta['primary_deltas'].values())
    wins = sum(v > 0 for v in delta['paired_spell_deltas'].values())
    base = bool(gate['tests_pass'] and med_s > 0 and wins >= 3 and med_f >= -.01 - 1e-12)
    require(gate['existing_gate'] == base and gate['promoted'] == (base and med_c >= .01)
            and gate['matches_improved'] == wins and math.isclose(gate['median_primary_delta'], med_c, abs_tol=1e-10),
            'Stored gate decision disagrees with complete paired results')

    lines = ['# PFF data evaluations — completed aggregate report', '',
             'This report validates completeness and recomputes the A decision from aggregate files. '
             'No target/public labels, raw observations, prediction arrays or sealed assets are read.', '',
             '## Admission and fixed populations', '',
             f'Attempted 64 matches; {len(passed)} pass; {64-len(passed)} excluded. '
             f'Admitted training: {len(train)} of fixed 48; transfer: {len(held)} of fixed 16. '
             'No replacement by performance. Admission SHA-256: `' + cohort['admission_sha256'] + '`.', '',
             '| Match | Status | Known labels / frames | Natural missing / known | Corrupted missing / known |',
             '|---|---|---:|---:|---:|']
    for r in sorted(admission, key=lambda z: z['match']):
        if r['status'] != 'pass':
            lines.append(f"| {r['match']} | excluded; see admission.json | — | — | — |")
            continue
        n = r['known_labels']
        lines.append(f"| {r['match']} | pass | {n}/{r['frames']} | {r['natural_missing_graded']}/{n} | {r['corrupted_missing_graded']}/{n} |")
    lines += ['', '## A — train-more paired comparison', '',
              'Both arms retain legacy label-valid-run decoder resets for comparability. '
              'Fresh parent uses the other four IDSSE matches; expanded adds only admitted PFF training matches.', '',
              '| Match | Setting | Parent spellF1 | Expanded spellF1 | Parent macroF1 | Expanded macroF1 |',
              '|---|---|---:|---:|---:|---:|']
    for m in ids:
        for c in conditions:
            p, e = cells[m, 'parent', c], cells[m, 'expanded', c]
            lines.append(f"| {m} | {c} | {fmt(p['spellF1'])} | {fmt(e['spellF1'])} | {fmt(p['macroF1'])} | {fmt(e['macroF1'])} |")
    lines += ['', '| Match | Paired spell delta | Paired macro delta | Corrupted spell delta |',
              '|---|---:|---:|---:|']
    for m in ids:
        lines.append('| ' + m + ' | ' + ' | '.join(fmt(delta[k][m]) for k in delta) + ' |')
    decision = 'PASS' if gate['promoted'] else 'REJECT'
    lines += ['', f'**A gate: {decision}.** Paired median spell delta {fmt(med_s)}; '
              f'{wins}/5 improve; median macro delta {fmt(med_f)}; primary corrupted median delta {fmt(med_c)} '
              '(minimum +.01). Tests: ' + str(gate['tests_pass']) + '. '
              'A passing gate is eligibility, not deployment: clean deterministic reproduction is still required.', '',
              '## B — descriptive transfer risk, never selection', '',
              '| Direction | Match | Setting | spellF1 | macroF1 | Known frames | Known fraction |',
              '|---|---|---|---:|---:|---:|---:|']
    for r in sorted(b, key=lambda z: (z['direction'], z['match'], z['condition'])):
        lines.append(f"| {r['direction']} | {r['match']} | {r['condition']} | {fmt(r['spellF1'])} | {fmt(r['macroF1'])} | {r['known_frames']} | {fmt(r['known_label_fraction'])} |")
    lines += ['', '## Equal-match variation', '',
              'SD is sample SD across matches; not a confidence interval. Do not pool providers or treat A/B block policies as identical.', '',
              '| Evaluation / arm | Setting | N | Mean spellF1 | Median | SD | Min–max | Mean macroF1 | Macro SD | Known fraction range |',
              '|---|---|---:|---:|---:|---:|---|---:|---:|---|']
    groups = [(f'A/{arm}', [r for r in a if r['arm'] == arm]) for arm in ['parent', 'expanded']]
    groups += [(f'B/{d}', [r for r in b if r['direction'] == d]) for d in [forward, reverse]]
    for name, rr in groups:
        for c in conditions:
            z = [r for r in rr if r['condition'] == c]
            ss, ff, kk = ([r[k] for r in z] for k in ['spellF1', 'macroF1', 'known_label_fraction'])
            lines.append(f'| {name} | {c} | {len(z)} | {fmt(statistics.mean(ss))} | {fmt(statistics.median(ss))} | {fmt(statistics.stdev(ss))} | {fmt(min(ss))}–{fmt(max(ss))} | {fmt(statistics.mean(ff))} | {fmt(statistics.stdev(ff))} | {fmt(min(kk))}–{fmt(max(kk))} |')
    lines += ['', '## Per-match missing-ball dead/live diagnostics', '',
              'D is positive; live collapses H/A. Counts use known-label unique 25 Hz frames. '
              'Natural missing is adapter missingness before masks; newly masked excludes naturally missing. '
              'All-missing is their union. Clean PFF is not fully observed. '
              'Binary macroF1 is undefined if either true class has no support; rates with zero denominator are undefined.', '',
              '| Evaluation | Match | Setting | Subset | N | True D/live | TP/FP/FN/TN (D+) | D precision/recall/F1 | Live recall | Binary macroF1 | Predicted D share |',
              '|---|---|---|---|---:|---|---|---|---:|---:|---:|']
    for r in a + b:
        name = 'A/' + r['arm'] if 'arm' in r else 'B/' + r['direction']
        for sub in ['natural_missing', 'newly_masked', 'all_missing', 'observed']:
            s = r['subsets'][sub]
            count = '/'.join(str(s[k]) for k in ['TP_D', 'FP_D', 'FN_D', 'TN_D'])
            rates = '/'.join(fmt(s[k], 4) for k in ['D_precision', 'D_recall', 'D_f1'])
            lines.append(f"| {name} | {r['match']} | {r['condition']} | {sub} | {s['frames']} | {s['true_D']}/{s['true_live']} | {count} | {rates} | {fmt(s['live_recall'],4)} | {fmt(subset_metrics(s),4)} | {fmt(s['predicted_D_share'],4)} |")
    lines += ['', '## Fit cost', '', '| Match | Arm | Training rows | Seconds |', '|---|---|---:|---:|']
    for r in costs:
        lines.append(f"| {r.get('match','all')} | {r['arm']} | {r['training_rows']} | {r['seconds']:.3f} |")
    lines += ['', f"Total recorded fit seconds: {sum(r['seconds'] for r in costs):.3f}. Forward transfer reuses the frozen IDSSE model; fit totals exclude preparation, inference and prior model cost.", '',
              '## Limitations and interpretation', '',
              '- Input is raw VISIBLE-only PFF observations. Smoothed PFF coordinates are excluded because provider smoothing uses events/carrier information; including them would risk teacher-conditioned feature leakage.',
              '- A uses annotation-supported X-gap resets inherited from the parent. B decodes halves only and lets the scorer mask X. Their top-line difference is not an isolated causal estimate of provider shift.',
              '- Conservative unknown/duplicate handling changes the evaluable population. Coverage and missingness denominators are published; high annotation presence alone does not prove convention agreement.',
              '- PFF is broadcast-derived and naturally missing; IDSSE tactical data, provider labels, class shares and visible subsets differ. More data volume/provider mixture and noise vary together. A gain would not prove that label count alone caused it.',
              '- Five IDSSE matches have historical reuse. A passed gate is not an unbiased generalization guarantee. Fold SD is descriptive. B is risk evidence only: no setting, cleanup, calibration or promotion may depend on it.',
              '- Both sealed IDSSE matches remain excluded; target-match accuracy is unknown. No public-window score is used. No new model combination or rescue search is authorized by this report.', '',
              'Sources: completed admission/cohort/lock, train-more-results.json, transfer-results.json, gate.json, cost.json and their preregistered protocols. All raw assets and arrays remain local.']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('experiments/pff-evaluation'))
    args = parser.parse_args()
    text = build_report(args.root)  # Refuse partial data before opening output.
    temporary = args.root / 'report.md.tmp'
    temporary.write_text(text)
    temporary.replace(args.root / 'report.md')
    print('Validated completed aggregate evaluations and wrote', args.root / 'report.md')


if __name__ == '__main__':
    main()
