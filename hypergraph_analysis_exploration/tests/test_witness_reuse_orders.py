import unittest
from src.analysis.witness_reuse_orders import compare


class ReuseOrdersTests(unittest.TestCase):
    def test_paired_orders_and_zero_capacity(self):
        graph = {'r': ('a',), 's': ('a',), 'a': ()}
        result = compare(graph, ['r', 's'], 1, [0, 3], [11, 17])
        self.assertEqual(result, compare(graph, ['r', 's'], 1, [0, 3], [11, 17]))
        self.assertEqual(len(result['rows']), 4)
        self.assertEqual([row['computed_states'] for row in result['rows'] if row['capacity'] == 0], [4, 4])
        self.assertTrue(all(row['computed_states'] <= 4 for row in result['rows']))

    def test_rejects_duplicate_roots_or_seeds(self):
        for roots, seeds in [(['a', 'a'], [1]), (['a'], [1, 1])]:
            with self.assertRaises(ValueError):
                compare({'a': ()}, roots, 0, [0], seeds)
