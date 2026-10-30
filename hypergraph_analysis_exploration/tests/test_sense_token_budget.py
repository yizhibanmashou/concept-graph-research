import unittest
from src.analysis.sense_token_budget import lengths


class TokenBudgetTests(unittest.TestCase):
    def test_uses_the_same_encoder_and_counts_over_budget(self):
        item = {key: {'target': 'h', 'value': 'x' * n}
                for key, n in [('A', 1), ('B', 2), ('C', 3), ('D', 4)]}
        result = lengths([item], lambda text: list(text), [26, 28])
        expected = {key: result['items'][0]['tokens'][key] for key in 'ABCD'}
        self.assertLess(expected['A'], expected['D'])
        for key in 'ABCD':
            self.assertEqual(result['summary'][key]['over_budget']['26'], int(expected[key] > 26))

    def test_empty_or_invalid_budget_rejected(self):
        with self.assertRaises(ValueError):
            lengths([], lambda x: x, [128])
        with self.assertRaises(ValueError):
            lengths([{}], lambda x: x, [0])
