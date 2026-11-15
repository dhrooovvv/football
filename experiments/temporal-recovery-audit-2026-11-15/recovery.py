"""Exploratory spell-level separability; never returns deployed predictions."""
import numpy as np

SIGNALS = ('parent_team_margin', 'temporal_team_margin', 'member_agreement')


def auc(positive, negative):
    """Mann–Whitney probability, ties worth one half; no threshold fitting."""
    if not positive or not negative:
        return None
    ordered = np.sort(np.asarray(negative, dtype=np.float64))
    p = np.asarray(positive, dtype=np.float64)
    below = np.searchsorted(ordered, p, side='left')
    equal = np.searchsorted(ordered, p, side='right') - below
    return float(np.sum(below + .5 * equal) / (len(p) * len(ordered)))


def summarize(records):
    groups = sorted({r['category'] for r in records})
    result = {'counts': {g: sum(r['category'] == g for r in records) for g in groups}}
    result['signals'] = {}
    for signal in SIGNALS:
        good = [r[signal] for r in records if r['category'] == 'recovered']
        bad = [r[signal] for r in records if r['category'] == 'introduced_spurious']
        result['signals'][signal] = dict(
            recovered_vs_introduced_spurious_auc=auc(good, bad),
            recovered_n=len(good), introduced_spurious_n=len(bad),
            recovered_quantiles=np.quantile(good, [0, .25, .5, .75, 1]).tolist() if good else [],
            introduced_spurious_quantiles=np.quantile(bad, [0, .25, .5, .75, 1]).tolist() if bad else [])
    return result


def spell_records(y, before, after, parent, temporal, members, missing, blocks, official, diagnostic):
    """Full original spells, split at halves and unknown supervision, official greedy IoU .5."""
    y, before, after = map(official.label_codes, (y, before, after))
    if parent.shape != (len(y), 3) or temporal.shape != parent.shape or len(members) != 2:
        raise ValueError('Wrong frozen two-member probability schema')
    runs = diagnostic.valid_runs(y, blocks, official)
    truth = official.possession_spells(y, runs)
    old = official.possession_spells(before, runs)
    new = official.possession_spells(after, runs)
    old_pairs = diagnostic.matched_pairs(official.spell_overlaps(truth, old), .5)
    new_pairs = diagnostic.matched_pairs(official.spell_overlaps(truth, new), .5)
    old_hit = {i for i, _ in old_pairs}
    new_truth = {j: i for i, j in new_pairs}
    preserved = {j for _, j in diagnostic.matched_pairs(official.spell_overlaps(old, new), .5)}
    gaps = diagnostic.gap_exposure(np.asarray(missing, bool), runs)
    records = []
    for j, (a, b, team) in enumerate(new):
        if j in new_truth:
            category = 'preserved_true' if new_truth[j] in old_hit else 'recovered'
        else:
            category = 'persistent_spurious' if j in preserved else 'introduced_spurious'
        others = [i for i in range(3) if i != team]
        records.append(dict(start=int(a), stop=int(b), team=int(team), category=category,
            frames=int(b-a), missing_fraction=float(np.mean(missing[a:b])),
            maximum_gap_frames=int(gaps[a:b].max()),
            parent_team_margin=float(np.mean(parent[a:b, team]-parent[a:b][:, others].max(1))),
            temporal_team_margin=float(np.mean(temporal[a:b, team]-temporal[a:b][:, others].max(1))),
            member_agreement=float(np.mean(np.logical_and(
                members[0][a:b].argmax(1) == team, members[1][a:b].argmax(1) == team)))))
    return records


def loss_summary(values):
    """Report each fixed stage separately; stage two deliberately resets RNG/Adam."""
    values = np.asarray(values, dtype=np.float64)
    if values.shape != (40000,) or not np.isfinite(values).all():
        raise ValueError('Expected exactly 40000 finite saved training losses')
    result = []
    for start in (0, 20000):
        part = values[start:start+20000]
        means = [float(part[i:i+1000].mean()) for i in range(0, 20000, 1000)]
        result.append(dict(start_update=start, stop_update=start+20000,
            thousand_update_means=means, first_1000_mean=means[0], last_1000_mean=means[-1],
            late_5000_change=float(part[-5000:].mean()-part[-10000:-5000].mean())))
    return result
