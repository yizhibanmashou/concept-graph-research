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
        self.assertEqual(reps['C']['edges'], [[aliases['x'], aliases['y']]])

    def test_pairwise_projection_keeps_edges_but_loses_branch_partition(self):
        inventory = {'a': 'A', 'b': 'B', 'c': 'C'}
        one_hyperedge = build('target', 'gloss', [['a', 'b', 'c']], inventory)
        three_pairwise_branches = build('target', 'gloss', [['a', 'b'], ['a', 'c'], ['b', 'c']], inventory)

        one_reps, one_aliases = representations(one_hyperedge, one_hyperedge['D']['branches'])
        pair_reps, pair_aliases = representations(three_pairwise_branches, three_pairwise_branches['D']['branches'])

        self.assertEqual(one_reps['C']['edges'], pair_reps['C']['edges'])
        self.assertNotEqual(one_reps['D']['branches'], pair_reps['D']['branches'])
        self.assertEqual(one_reps['C']['edges'], [
            [one_aliases['a'], one_aliases['b']],
            [one_aliases['a'], one_aliases['c']],
            [one_aliases['b'], one_aliases['c']],
        ])
        self.assertEqual(one_reps['C']['edges'], [
            [pair_aliases['a'], pair_aliases['b']],
            [pair_aliases['a'], pair_aliases['c']],
            [pair_aliases['b'], pair_aliases['c']],
        ])

    def test_pairwise_projection_is_a_simple_graph(self):
        item = build('target', 'gloss', [['a', 'b'], ['a', 'b', 'c']],
                     {'a': 'A', 'b': 'B', 'c': 'C'})
        reps, aliases = representations(item, item['D']['branches'])
        self.assertEqual(reps['C']['edges'], [
            [aliases['a'], aliases['b']],
            [aliases['a'], aliases['c']],
            [aliases['b'], aliases['c']],
        ])

    def test_budget_and_missing_dependency(self):
        item = build('h', 'head', [['x'], ['y']], {'x': 'a', 'y': 'b'})
        self.assertEqual(pack(item, list, 1000)['status'], 'all')
        self.assertEqual(pack(item, list, 1)['status'], 'base_over_budget')
        item['D']['branches'].append(['missing'])
        with self.assertRaises(ValueError):
            pack(item, list, 1000)
