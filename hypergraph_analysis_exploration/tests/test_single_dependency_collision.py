import unittest
from src.analysis.single_dependency_collision import analyze


class SingleDependencyCollisionTests(unittest.TestCase):
    def test_single_deletion_collision_empty_and_duplicate_branches(self):
        pos = {'p': 'prep', 'x': 'n', 'q': 'n'}
        rows = [{'head': 'h', 'clauses': [['x', 'p'], ['x'], ['x'], ['q', 'p']]}]
        result = analyze(rows, pos)
        items = {node['id']: node for node in result['nodes']}
        self.assertEqual(result['totals']['distinct_nonempty_branches'], 3)
        self.assertEqual(items['p']['collision_heads'], 1)
        self.assertEqual(result['posthoc_strict_containment']['heads_by_min_size_difference'], {1: 1})
        self.assertEqual(items['x']['empty_heads'], 1)
        self.assertEqual(result['groups']['prep']['node_head_uses'], 1)
        self.assertEqual(result['groups']['other']['collision_node_head_pairs'], 0)

    def test_two_node_deletion_is_not_single_node_collision(self):
        result = analyze([{'head': 'h', 'clauses': [['a', 'b', 'x'], ['x']]}],
                         {'a': 'prep', 'b': 'prep', 'x': 'n'})
        self.assertEqual(sum(g['collision_node_head_pairs'] for g in result['groups'].values()), 0)
        projection = result['posthoc_all_prep_projection']
        self.assertEqual(projection['affected_heads'], 1)
        self.assertEqual(projection['heads_by_min_symmetric_difference'], {2: 1})
        self.assertEqual(result['posthoc_strict_containment']['heads_by_min_size_difference'], {2: 1})

    def test_invalid_source_rejected(self):
        for clauses in ([[]], [['absent']], []):
            with self.assertRaises(ValueError):
                analyze([{'head': 'h', 'clauses': clauses}], {})
