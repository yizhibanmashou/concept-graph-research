import unittest
from src.analysis.sense_budget_packing import pack
from src.analysis.sense_representation_pilot import build


class SenseBudgetPackingTests(unittest.TestCase):
    def test_accepts_only_whole_branches_and_respects_all_budgets(self):
        item = build('h', 'head', [['x'], ['y', 'z']], {'x': 'a', 'y': 'b', 'z': 'c'})
        encode = lambda text: list(text)
        complete = pack(item, encode, 1000)
        self.assertEqual((complete['status'], complete['selected_branches']), ('all', 2))
        base_over = pack(item, encode, 1)
        self.assertEqual(base_over['status'], 'base_over_budget')
        for budget in range(60, 300):
            result = pack(item, encode, budget)
            if result['status'] != 'base_over_budget':
                self.assertLessEqual(max(result['tokens'].values()), budget)
                self.assertIn(result['selected_branches'], range(3))

    def test_missing_or_empty_branches_rejected(self):
        item = build('h', 'head', [['x']], {'x': 'a'})
        item['D']['branches'] = [[]]
        with self.assertRaises(ValueError):
            pack(item, lambda text: list(text), 100)
