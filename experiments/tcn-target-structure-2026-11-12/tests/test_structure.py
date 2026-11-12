"""User-run synthetic geometry contracts; no match assets or models."""
import json
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from structure import summarize


class Structure(unittest.TestCase):
    def make(self, frames=8):
        xy=np.zeros((frames,4,2),np.float32)
        xy[:,:,0]=np.array([.125,.875,.25,.75],np.float32)
        xy[:,:,1]=.5
        return xy,np.ones((frames,4),bool),np.array([0,0,1,1])

    def run_case(self,xy,seen,teams,blocks=None,chunk=3):
        return summarize(len(xy),teams,blocks or [[0,len(xy)]],[100.,50.],
                         lambda a,b:(xy[a:b],seen[a:b]),chunk_size=chunk)

    def test_stable_geometry_and_chunk_invariance(self):
        args=self.make();a=self.run_case(*args,chunk=1);b=self.run_case(*args,chunk=3)
        self.assertEqual(a,b)
        for team in a['teams'].values():
            self.assertEqual(team['adjacent_observed_same_slot_displacement']['count'],14)
            self.assertEqual(team['adjacent_observed_same_slot_displacement']['max_m'],0.)
            self.assertEqual(team['encoder_velocity_clipping_proxy']['any_component_exceeds_abs5_fraction'],0.)
            self.assertEqual(team['observation_runs']['visible_runs']['count'],2)

    def test_permutation_changes_slot_motion_but_not_set_geometry(self):
        xy,seen,teams=self.make()
        xy[1::2,:2]=xy[1::2,1::-1].copy()
        result=self.run_case(xy,seen,teams)['teams']['H']
        self.assertEqual(result['adjacent_observed_same_slot_displacement']['mean_m'],75.)
        self.assertEqual(result['directed_nearest_same_team_previous_set']['mean_m'],0.)
        self.assertEqual(result['encoder_velocity_clipping_proxy']['any_component_exceeds_abs5_fraction'],1.)

    def test_gaps_and_half_boundaries_never_create_motion_pairs(self):
        xy,seen,teams=self.make(6)
        seen[1:3,0]=False;xy[1:3,0]=np.nan
        xy[3:,:,0]+=np.float32(.5)
        result=self.run_case(xy,seen,teams,[[0,3],[3,6]],chunk=2)
        home=result['teams']['H'];away=result['teams']['A']
        self.assertEqual(home['adjacent_observed_same_slot_displacement']['count'],6)
        self.assertEqual(away['adjacent_observed_same_slot_displacement']['count'],8)
        self.assertEqual(home['adjacent_observed_same_slot_displacement']['max_m'],0.)
        self.assertEqual(home['observation_runs']['disappearances_after_observed_presence'],1)
        # Reappearance at a new half is censored, not an observed transition.
        self.assertEqual(home['observation_runs']['appearances_after_observed_absence'],0)
        self.assertEqual(home['observation_runs']['missing_runs']['max_seconds'],2/25)

    def test_duplicate_and_close_pairs_are_descriptive_counts(self):
        xy,seen,teams=self.make();xy[:,:2]=xy[:,0:1]
        seen[0,1]=False
        result=self.run_case(xy,seen,teams)['teams']['H']
        proxies=result['same_team_close_position_proxies']
        self.assertEqual(proxies['visible_unordered_pair_count'],7)
        self.assertEqual(proxies['thresholds'][0]['pair_count'],7)
        self.assertEqual(proxies['thresholds'][0]['frame_fraction'],7/8)
        self.assertEqual(result['visible_slot_count']['frequency'],{'0':0,'1':1,'2':7})

    def test_output_has_no_rows_identifiers_or_geometry_sequences(self):
        result=self.run_case(*self.make())
        self.assertEqual(set(result),{'active_frames','fps','real_half_count','pitch_metres','teams'})
        text=json.dumps(result,allow_nan=False)
        for forbidden in ('coordinates','slot_ids','frame_ids','trajectory','samples','labels'):
            self.assertNotIn(forbidden,text)
        for team in result['teams'].values():
            self.assertLessEqual(len(team['visible_slot_count']['frequency']),65)
            for metric in ('adjacent_observed_same_slot_displacement','directed_nearest_same_team_previous_set'):
                self.assertEqual(len(team[metric]['quantile_intervals_m']),4)

    def test_strict_visibility_and_block_contract(self):
        xy,seen,teams=self.make()
        with self.assertRaises(ValueError):self.run_case(xy.astype(np.float64),seen,teams)
        with self.assertRaises(ValueError):self.run_case(xy,seen.astype(np.int8),teams)
        with self.assertRaises(ValueError):self.run_case(xy,seen,teams,[[0,5],[4,8]])
        xy[0,0]=np.nan
        with self.assertRaises(ValueError):self.run_case(xy,seen,teams)


if __name__=='__main__':unittest.main()
