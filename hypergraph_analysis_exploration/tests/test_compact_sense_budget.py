import unittest
from src.analysis.compact_sense_budget import pack, representations
from src.analysis.sense_representation_pilot import build


class CompactBudgetTests(unittest.TestCase):
    def test_aliases_preserve_shared_dependencies_and_branch_membership(self):
        item = build('target', 'gloss', [['x', 'y'], ['z']], {'x': 'one', 'y': 'two', 'z': 'three'})
        reps, aliases = representations(item, item['D']['branches'])
        self.assertEqual(reps['B']['deps'], reps['C']['deps'])
        self.assertEqual(reps['B']['deps'], reps['D']['deps'])
        self.assertEqual(reps['D']['branches'], [[aliases['x'], aliases['y']], [aliases['z']]])
        self.assertEqual(reps['C']['edges'], [aliases[x] for x in sorted(aliases)])

    def test_budget_and_missing_dependency(self):
        item = build('h', 'head', [['x'], ['y']], {'x': 'a', 'y': 'b'})
        self.assertEqual(pack(item, list, 1000)['status'], 'all')
        self.assertEqual(pack(item, list, 1)['status'], 'base_over_budget')
        item['D']['branches'].append(['missing'])
        with self.assertRaises(ValueError):
            pack(item, list, 1000)
