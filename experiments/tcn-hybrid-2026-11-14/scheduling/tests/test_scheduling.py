"""User-run pure scheduling contracts. No real models or data are opened."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path('scripts').resolve()))
import run_tcn_hybrid_parallel as parallel

class SchedulingTests(unittest.TestCase):
    def test_ten_unique_fold_seed_tasks(self):
        tasks=parallel.jobs()
        self.assertEqual(len(tasks),10)
        self.assertEqual(len(set(tasks)),10)
        self.assertNotIn('J03WQQ',{m for m,_ in tasks})
    def test_projection_counts_whole_job_waves(self):
        self.assertEqual(parallel.projected_seconds(100,4,20),1.5*(3*2*100+100+20))
        self.assertEqual(parallel.projected_seconds(100,2,20),1.5*(5*2*100+2*100+20))
    def test_invalid_projection_rejected(self):
        for args in [(100,11,0),(0,4,0),(100,4,-1)]:
            with self.assertRaises(RuntimeError):parallel.projected_seconds(*args)
    def test_probe_and_full_outputs_separate(self):
        probe=parallel.probe_path('4','J03WMX',20261106)
        full=parallel.old.fit_path('graph','J03WMX',20261106)
        self.assertNotEqual(probe,full)
        self.assertIn('benchmark',probe.parts)

if __name__=='__main__':unittest.main()
