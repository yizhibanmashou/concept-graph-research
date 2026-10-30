import random
import unittest

from src.analysis.witness_reuse_pilot import simulate_lru
from src.analysis.witness_rewire_order_sensitivity import evaluate_orders


class OrderSensitivityTests(unittest.TestCase):
    def test_explicit_order_and_capacity_match_reference(self):
        graph = {'a': ('b',), 'b': ('c',), 'c': ()}
        roots = ['a', 'b', 'c']
        rows = evaluate_orders(graph, roots, (11, 23), 2, (0, 2))
        for row in rows:
            order = random.Random(row['order_seed']).sample(roots, len(roots))
            self.assertEqual(row['metrics'], [simulate_lru(graph, order, 2, c) for c in (0, 2)])

    def test_duplicate_roots_fail(self):
        with self.assertRaises(ValueError):
            evaluate_orders({'a': ()}, ['a', 'a'], (11,), 2, (0,))


if __name__ == '__main__':
    unittest.main()
