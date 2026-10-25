import sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import main

class Checks(unittest.TestCase):
    def test_negation(self): self.assertEqual(main.sentiment('not helpful'),'negative')
    def test_identical_experiment(self):
        delta,ci,p=main.experiment(np.array([0,1]*100),np.array([0,1]*100)); self.assertEqual(delta,0); self.assertEqual(p,1); self.assertLess(ci[0],0)

if __name__=="__main__": unittest.main()
