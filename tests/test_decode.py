import itertools
import unittest
import numpy as np
from possession.decode import decode

COST = np.ones((3, 3)) - np.eye(3)


def emissions(states):
    p = np.full((len(states), 3), .01)
    p[np.arange(len(states)), states] = .98
    return p


class ConfirmatoryContracts(unittest.TestCase):
    def fixtures(self):
        return [np.array([[.9,.05,.05],[.9,.05,.05],[.45,.50,.05],[.9,.05,.05],[.9,.05,.05]]),
                emissions([0]*5+[1]*2+[0]*5), emissions([0]*5+[2]*5+[1]*5)]

    def test_ambiguous_flicker(self):
        self.assertEqual(decode(self.fixtures()[0], COST).tolist(), ['H']*5)

    def test_short_supported_possession(self):
        self.assertEqual(decode(self.fixtures()[1], COST).tolist(), ['H']*5+['A']*2+['H']*5)

    def test_stoppage_and_restart(self):
        self.assertEqual(decode(self.fixtures()[2], COST).tolist(), ['H']*5+['D']*5+['A']*5)

    def test_half_isolation(self):
        p = np.full((10,3), 1/3)
        original = decode(p, COST, [(0,5),(5,10)])
        p[:5] = emissions([1]*5)
        np.testing.assert_array_equal(original[5:],decode(p,COST,[(0,5),(5,10)])[5:])

    def test_repeatability_and_team_swap(self):
        for p in self.fixtures():
            a=decode(p,COST)
            np.testing.assert_array_equal(a,decode(p,COST))
            expected=np.array([{'H':'A','A':'H','D':'D'}[x] for x in a])
            np.testing.assert_array_equal(expected,decode(p[:,[1,0,2]],COST[np.ix_([1,0,2],[1,0,2])]))

    def test_invalid_emissions(self):
        for p in [[[-.1,.6,.5]],[[.1,.1,.1]],[[np.nan,.5,.5]],[[np.inf,0,0]],[.2,.3,.5],[[.5,.5]]]:
            with self.subTest(p=p),self.assertRaises(ValueError):decode(p,COST)


class ExploratoryContracts(unittest.TestCase):
    def test_small_sequence_against_exhaustive_oracle(self):
        rng=np.random.default_rng(17)
        for _ in range(10):
            p=rng.dirichlet(np.ones(3),size=5)
            cost=rng.uniform(0,2,size=(3,3))
            def score(path):
                return sum(np.log(p[t,k]) for t,k in enumerate(path))-sum(cost[a,b] for a,b in zip(path,path[1:]))
            best=max(itertools.product(range(3),repeat=5),key=score)
            self.assertEqual(decode(p,cost).tolist(),np.array(['H','A','D'])[list(best)].tolist())

    def test_uncovered_frames_and_invalid_blocks(self):
        p=emissions([0]*5)
        self.assertEqual(decode(p,COST,[(1,4)]).tolist(),['X','H','H','H','X'])
        for blocks in [[(0,3),(2,5)],[(0,6)],[(2,2)],[(0.,3)]]:
            with self.assertRaises(ValueError):decode(p,COST,blocks)

    def test_empty_zero_and_bad_cost(self):
        self.assertEqual(decode(np.empty((0,3)),COST).tolist(),[])
        self.assertEqual(decode([[1,0,0]],COST).tolist(),['H'])
        for cost in [np.ones((2,3)),np.full((3,3),np.nan),-np.ones((3,3))]:
            with self.assertRaises(ValueError):decode([[1,0,0]],cost)
