"""Aggregate-only spell diagnostics. Labels never determine a deployed prediction."""
from collections import Counter
import numpy as np

DURATION_BINS = ('up_to_2s', '2_to_10s', 'over_10s')
GAP_BINS = ('fully_observed', 'up_to_2s', '2_to_10s', 'over_10s')
CATEGORIES = ('decoder_removed_support', 'long_gap_without_argmax_match',
              'observed_wrong_team', 'dead_live_confusion', 'merged',
              'fragmented', 'boundary_misalignment', 'other')


def duration_bin(frames):
    return 'up_to_2s' if frames <= 50 else '2_to_10s' if frames <= 250 else 'over_10s'


def valid_runs(y, blocks, official):
    """Retain original frame coordinates, splitting at BOTH halves and X."""
    result = []
    end = 0
    for start, stop in blocks:
        if not end <= start < stop <= len(y):
            raise ValueError('Blocks must be ordered, disjoint and inside labels')
        result.extend((int(start + a), int(start + b))
                      for a, b in official.valid_runs(y[start:stop]))
        end = stop
    outside = np.ones(len(y), bool)
    for a, b in blocks:
        outside[a:b] = False
    if np.any(y[outside] != official.X):
        raise ValueError('Graded labels outside registered blocks')
    return result


def gap_exposure(missing, runs):
    """Every missing frame gets its full valid-run-clipped burst length."""
    lengths = np.zeros(len(missing), dtype=np.int64)
    for start, stop in runs:
        edges = np.diff(np.r_[False, missing[start:stop], False].astype(np.int8))
        for a, b in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)):
            lengths[start+a:start+b] = b-a
    return lengths


def matched_pairs(overlaps, threshold):
    used_g, used_p, pairs = set(), set(), []
    for iou, g, p in overlaps:
        if iou < threshold:
            break
        if g not in used_g and p not in used_p:
            used_g.add(g); used_p.add(p); pairs.append((g, p))
    return pairs


def quantiles(values):
    return np.quantile(values, [0, .1, .5, .9, 1]).tolist() if len(values) else []


def analyze(y, prediction, missing, probabilities, blocks, official):
    y = official.label_codes(y)
    pred = official.label_codes(prediction)
    missing = np.asarray(missing, bool)
    probabilities = np.asarray(probabilities)
    if pred.shape != y.shape or missing.shape != y.shape or probabilities.shape != (len(y), 3):
        raise ValueError('Diagnostic arrays have different shapes')
    if not np.isfinite(probabilities).all() or np.any(probabilities < 0) or not np.allclose(
            probabilities.sum(1), 1, atol=1e-8, rtol=0):
        raise ValueError('Invalid probabilities')
    runs = valid_runs(y, blocks, official)
    truth = official.possession_spells(y, runs)
    guesses = official.possession_spells(pred, runs)
    argmax = probabilities.argmax(1).astype(np.int8)
    raw_spells = official.possession_spells(argmax, runs)
    overlaps = official.spell_overlaps(truth, guesses)
    raw_overlaps = official.spell_overlaps(truth, raw_spells)
    scores = official.spell_scores(y, pred, runs)
    gap_lengths = gap_exposure(missing, runs)
    members = [set() for _ in truth]
    for _, i, j in overlaps:
        members[i].add(j)
    reverse = [set() for _ in guesses]
    for i, js in enumerate(members):
        for j in js:
            reverse[j].add(i)
    records = []
    matched = {str(t): official.matched_gt_flags(overlaps, len(truth), t)
               for t in official.SPELL_IOUS}
    raw_matched = {str(t): official.matched_gt_flags(raw_overlaps, len(truth), t)
                   for t in official.SPELL_IOUS}
    for i, (a, b, team) in enumerate(truth):
        maximum = int(gap_lengths[a:b].max())
        gap = duration_bin(maximum) if maximum else 'fully_observed'
        majority_wrong = int(np.sum(pred[a:b] == 1-team)) > (b-a)/2
        dead = bool(np.any(pred[a:b] == official.D))
        flags = dict(decoder_removed_support=bool(raw_matched['0.5'][i] and not matched['0.5'][i]),
                     long_gap_without_argmax_match=bool(maximum > 250 and not raw_matched['0.5'][i]),
                     observed_wrong_team=bool(not maximum and majority_wrong),
                     dead_live_confusion=dead,
                     merged=any(len(reverse[j]) >= 2 for j in members[i]),
                     fragmented=len(members[i]) >= 2,
                     boundary_misalignment=bool(members[i] and not matched['0.5'][i]))
        # Multi-label associations. This priority partitions misses only for ranking;
        # it must not be presented as a causal attribution or recoverable score.
        missed = not bool(matched['0.5'][i])
        exclusive = next((k for k in CATEGORIES[:-1] if flags[k]), 'other') if missed else None
        records.append(dict(identity=(int(a), int(b), int(team)), duration=duration_bin(b-a), gap=gap,
                            matched={k: bool(v[i]) for k, v in matched.items()},
                            argmax_matched={k: bool(v[i]) for k, v in raw_matched.items()},
                            flags=flags, exclusive=exclusive,
                            correct_argmax_fraction=float(np.mean(argmax[a:b] == team)),
                            mean_correct_team_probability=float(probabilities[a:b, team].mean())))
    bins = {}
    for duration in DURATION_BINS:
        for gap in GAP_BINS:
            selected = [r for r in records if r['duration'] == duration and r['gap'] == gap]
            bins[duration + '/' + gap] = dict(n_gt=len(selected), per_iou={
                str(t): dict(n_matched=sum(r['matched'][str(t)] for r in selected),
                             n_missed=sum(not r['matched'][str(t)] for r in selected),
                             recall=(sum(r['matched'][str(t)] for r in selected)/len(selected)
                                     if selected else None)) for t in official.SPELL_IOUS})
    misses = [r for r in records if not r['matched']['0.5']]
    pair_counts = {a + '+' + b: sum(r['flags'][a] and r['flags'][b] for r in misses)
                   for n, a in enumerate(CATEGORIES[:-1]) for b in CATEGORIES[n+1:-1]}
    pairs = matched_pairs(overlaps, .5)
    if len(pairs) != int(matched['0.5'].sum()):
        raise ValueError('Pair matcher disagrees with unchanged official matcher')
    start_shifts = [guesses[j][0]-truth[i][0] for i, j in pairs]
    stop_shifts = [guesses[j][1]-truth[i][1] for i, j in pairs]
    graded = y != official.X
    groups = {'all': graded, 'ball_missing': graded & missing, 'ball_observed': graded & ~missing}
    frame_errors = {}
    for name, mask in groups.items():
        cm = official.confusion(y[mask], pred[mask])
        frame_errors[name] = dict(frames=int(mask.sum()),
            wrong_team=int(np.sum(mask & (y < 2) & (pred < 2) & (y != pred))),
            dead_live=int(np.sum(mask & ((y == official.D) != (pred == official.D)))),
            predicted_X=int(np.sum(mask & (pred == official.X))),
            alive_dead_f1=official.alive_dead_f1(official.scored_confusion(cm)))
    report = dict(spellF1=scores['mean_f1'], per_iou={str(k): v for k, v in scores['per_iou'].items()},
                  true_spells=len(truth), predicted_spells=len(guesses), bins=bins,
                  missed_iou_05=len(misses), multi_label_missed_counts={k: sum(r['flags'][k] for r in misses)
                      for k in CATEGORIES[:-1]}, category_pair_overlaps=pair_counts,
                  exclusive_missed_counts={k: sum(r['exclusive'] == k for r in misses) for k in CATEGORIES},
                  boundary_shifts_frames=dict(matched_at_iou_05=len(pairs),
                      start_quantiles=quantiles(start_shifts), stop_quantiles=quantiles(stop_shifts)),
                  frame_errors=frame_errors,
                  probability_evidence={name: dict(spells=len(group),
                      mean_correct_team_probability=(float(np.mean([r['mean_correct_team_probability'] for r in group])) if group else None),
                      mean_correct_argmax_fraction=(float(np.mean([r['correct_argmax_fraction'] for r in group])) if group else None))
                      for name, group in (('matched_iou_05', [r for r in records if r['matched']['0.5']]),
                                          ('missed_iou_05', misses))},
                  evidence_by_iou={str(t): dict(
                      argmax_matched_decoded_missed=sum(r['argmax_matched'][str(t)] and not r['matched'][str(t)] for r in records),
                      decoded_matched_argmax_missed=sum(r['matched'][str(t)] and not r['argmax_matched'][str(t)] for r in records),
                      both_missed=sum(not r['matched'][str(t)] and not r['argmax_matched'][str(t)] for r in records))
                      for t in official.SPELL_IOUS})
    return report, records


def paired_changes(clean, corrupted):
    if [r['identity'] for r in clean] != [r['identity'] for r in corrupted]:
        raise ValueError('Clean/corrupted ground-truth spell identities differ')
    result = {}
    for t in ('0.3', '0.4', '0.5', '0.6', '0.7'):
        counts = Counter({key: 0 for key in ('retained', 'lost_after_corruption',
                                              'gained_after_corruption', 'missed_in_both')})
        lost_groups = Counter()
        for old, new in zip(clean, corrupted):
            a, b = old['matched'][t], new['matched'][t]
            counts['retained' if a and b else 'lost_after_corruption' if a else
                   'gained_after_corruption' if b else 'missed_in_both'] += 1
            if a and not b:
                lost_groups[new['duration'] + '/' + new['gap']] += 1
        result[t] = dict(counts=dict(counts), lost_duration_gap=dict(lost_groups))
    return result


def recommendation(cells):
    """Predeclared conservative ranking, no candidate or decoder selection."""
    names = CATEGORIES[:3]
    per_match = {r['match']: r['analysis']['exclusive_missed_counts'] for r in cells
                 if r['trial'] == 'b' and r['condition'] == 'targetlike'}
    totals = {k: sum(v[k] for v in per_match.values()) for k in CATEGORIES}
    ranking = sorted(totals, key=lambda k: (-totals[k], CATEGORIES.index(k)))
    winner = ranking[0]
    consistency = sum(v[winner] > 0 and v[winner] == max(v.values()) for v in per_match.values())
    unique = len(ranking) == 1 or totals[winner] > totals[ranking[1]]
    directions = dict(decoder_removed_support='narrowly scoped decoding intervention',
        long_gap_without_argmax_match='temporal context spanning long gaps',
        observed_wrong_team='local player-ball control relationships')
    proposal = directions[winner] if winner in names and unique and consistency >= 3 else None
    return dict(ranking=[dict(category=k, affected_spells=totals[k]) for k in ranking],
                per_match=per_match, leading_category_matches=consistency,
                conditional_proposal=proposal, experiment_authorized=False,
                interpretation='Priority-partitioned associations, not causal effects or recoverable spellF1. '
                'No proposal if the leader is tied, unsupported in three matches, or outside the registered branches. '
                'Stopped tracks need explicit reopening; any proposal needs review and a new protocol.')
