import unittest
from src.analysis.sense_packing_order_audit import audit, chosen
from src.analysis.sense_representation_pilot import build


class PackingOrderTests(unittest.TestCase):
    def test_selected_identity_is_independent_of_branch_order(self):
        item = build('h', 'head', [['x', 'y'], ['z']], {'x': 'a', 'y': 'b', 'z': 'c'})
        self.assertEqual(chosen(item, {'selected_indices': [0]}), [('x', 'y')])
        item['D']['branches'][0].reverse()
        self.assertEqual(chosen(item, {'selected_indices': [0]}), [('x', 'y')])

    def test_deterministic_and_missing_seeds_rejected(self):
        item = build('h', 'head', [['x'], ['y']], {'x': 'a', 'y': 'b'})
        first = audit([item], list, 1000, [0, 1])
        self.assertEqual(first, audit([item], list, 1000, [0, 1]))
        self.assertEqual(first['count_changed_targets'], 0)
        self.assertEqual(first['identity_changed_targets'], 0)
        with self.assertRaises(ValueError):
            audit([item], list, 100, [])
