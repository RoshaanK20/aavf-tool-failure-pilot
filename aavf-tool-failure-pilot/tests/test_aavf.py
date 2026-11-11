import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from aavf_sim import Scenario, execute, run

def scenario(write_fault='none', stock_fault='none', price_fault='none', delta=-4):
    return Scenario(99, 40, 120, delta, stock_fault, price_fault, write_fault)

class ExperimentTests(unittest.TestCase):
    def test_clean_all_pass(self):
        for name in ('no_check', 'retry', 'verify_all', 'adaptive'):
            result = execute(scenario(), name)
            self.assertEqual(result.success, 1, (name,result))
    def test_naive_retry_duplicate_on_lost_ack(self):
        r = execute(scenario(write_fault='timeout_post'), 'retry')
        self.assertEqual(r.duplicate_write, 1)
        self.assertEqual(r.state_correct, 0)
    def test_verify_before_retry_prevents_duplicate(self):
        for name in ('verify_all', 'adaptive'):
            r = execute(scenario(write_fault='timeout_post'), name)
            self.assertEqual(r.duplicate_write, 0)
            self.assertEqual(r.state_correct, 1)
    def test_silent_drop_missed_by_no_check(self):
        self.assertEqual(execute(scenario(write_fault='silent_drop'), 'no_check').state_correct, 0)
    def test_adaptive_recovers_high_risk_silent_drop(self):
        self.assertEqual(execute(scenario(write_fault='silent_drop'), 'adaptive').state_correct, 1)
    def test_plausible_corruption_remains_limitation(self):
        self.assertEqual(execute(scenario(stock_fault='corrupt'), 'adaptive').report_correct, 0)
        self.assertEqual(execute(scenario(stock_fault='corrupt'), 'verify_all').report_correct, 1)
    def test_reproducible(self):
        _, a = run(30, seed=77)
        _, b = run(30, seed=77)
        self.assertEqual(a, b)

if __name__ == '__main__': unittest.main()
