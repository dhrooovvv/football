"""Synthetic contracts only. User executes these before the diagnostic."""
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path[:0] = [str(Path('experiments/tcn-diagnostic-2026-11-13').resolve()),
               str(Path('reference/more-than-a-hack-2027-main/evaluation').resolve())]
import possession_metrics as pm
from diagnostics import (analyze, gap_exposure, valid_runs, matched_pairs,
                         paired_changes, recommendation, CATEGORIES)


def probabilities(labels):
    out = np.full((len(labels), 3), .05)
    for i, label in enumerate(labels):
        out[i, 'HAD'.index(label)] = .9
    return out


class DiagnosticTests(unittest.TestCase):
    def evaluate(self, truth, pred, raw=None, missing=None, blocks=None):
        y, p = np.array(list(truth)), np.array(list(pred))
        return analyze(y, p, np.zeros(len(y), bool) if missing is None else missing,
                       probabilities(raw or truth.replace('X', 'D')),
                       blocks or [(0, len(y))], pm)

    def test_half_and_unknown_boundaries_preserve_spells(self):
        report, rows = self.evaluate('HHHHXHH', 'HHHHXHH', blocks=[(0, 2), (2, 7)])
        self.assertEqual(report['true_spells'], 3)
        self.assertEqual([r['identity'] for r in rows], [(0, 2, 0), (2, 4, 0), (5, 7, 0)])
        self.assertEqual(report['spellF1'], 1)

    def test_tie_matching_agrees_with_official(self):
        gt = [(0, 10, 0), (10, 20, 0)]
        pred = [(0, 20, 0)]
        overlaps = pm.spell_overlaps(gt, pred)
        self.assertEqual(matched_pairs(overlaps, .5), [(0, 0)])
        self.assertEqual(pm.matched_gt_flags(overlaps, 2, .5).tolist(), [True, False])

    def test_gap_uses_whole_burst_not_spell_intersection(self):
        y = 'D'*150 + 'H'*10 + 'D'*150
        missing = np.ones(len(y), bool)
        report, rows = self.evaluate(y, y, missing=missing)
        self.assertEqual(rows[0]['gap'], 'over_10s')
        self.assertEqual(rows[0]['duration'], 'up_to_2s')
        self.assertEqual(report['bins']['up_to_2s/over_10s']['n_gt'], 1)

    def test_gaps_clip_half_and_unknown(self):
        y = pm.label_codes(list('HHXHHHHH'))
        runs = valid_runs(y, [(0, 5), (5, 8)], pm)
        self.assertEqual(gap_exposure(np.ones(8, bool), runs).tolist(), [2, 2, 0, 2, 2, 3, 3, 3])

    def test_decoder_removed_evidence_is_distinct_from_absent(self):
        _, with_support = self.evaluate('DDHHDD', 'DDDDDD')
        _, absent = self.evaluate('DDHHDD', 'DDDDDD', raw='DDDDDD')
        self.assertTrue(with_support[0]['flags']['decoder_removed_support'])
        self.assertFalse(absent[0]['flags']['decoder_removed_support'])

    def test_fully_observed_long_spell_is_not_long_gap(self):
        _, rows = self.evaluate('H'*300, 'A'*300)
        self.assertEqual(rows[0]['gap'], 'fully_observed')
        self.assertTrue(rows[0]['flags']['observed_wrong_team'])
        self.assertFalse(rows[0]['flags']['long_gap_without_argmax_match'])

    def test_merge_fragment_and_boundary_flags_overlap(self):
        _, merged = self.evaluate('HHDDHH', 'HHHHHH')
        self.assertTrue(all(r['flags']['merged'] for r in merged))
        self.assertTrue(all(r['flags']['boundary_misalignment'] for r in merged))
        _, fragmented = self.evaluate('HHHHHH', 'HDHDHD')
        self.assertTrue(fragmented[0]['flags']['fragmented'])

    def test_clean_corrupt_same_truth_and_identity_guard(self):
        _, clean = self.evaluate('HHDD', 'HHDD')
        _, corrupt = self.evaluate('HHDD', 'DDDD')
        result = paired_changes(clean, corrupt)
        self.assertEqual(result['0.5']['counts']['lost_after_corruption'], 1)
        corrupt[0]['identity'] = (1, 3, 0)
        with self.assertRaises(ValueError):
            paired_changes(clean, corrupt)

    def test_empty_spells_and_invalid_probability(self):
        report, rows = self.evaluate('DDDD', 'DDDD')
        self.assertEqual(rows, [])
        self.assertEqual(report['missed_iou_05'], 0)
        with self.assertRaises(ValueError):
            analyze(np.array(list('HH')), np.array(list('HH')), np.zeros(2, bool),
                    np.ones((2, 3)), [(0, 2)], pm)

    def test_exclusive_partition_and_all_thresholds(self):
        report, _ = self.evaluate('HHDAAHH', 'AADDDDD')
        self.assertEqual(sum(report['exclusive_missed_counts'].values()), report['missed_iou_05'])
        self.assertEqual(set(report['per_iou']), {'0.3', '0.4', '0.5', '0.6', '0.7'})

    def test_recommendation_is_conditional_and_requires_consistency(self):
        cells = []
        for i in range(5):
            counts = {k: 0 for k in CATEGORIES}
            counts['decoder_removed_support'] = 10
            cells.append(dict(trial='b', condition='targetlike', match=str(i),
                              analysis={'exclusive_missed_counts': counts}))
        result = recommendation(cells)
        self.assertEqual(result['conditional_proposal'], 'narrowly scoped decoding intervention')
        self.assertFalse(result['experiment_authorized'])
        for cell in cells:
            cell['analysis']['exclusive_missed_counts']['observed_wrong_team'] = 10
        self.assertIsNone(recommendation(cells)['conditional_proposal'])


if __name__ == '__main__':
    unittest.main()
