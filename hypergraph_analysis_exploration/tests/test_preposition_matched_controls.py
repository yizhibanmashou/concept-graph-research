import unittest
from collections import Counter
from src.analysis.preposition_matched_controls import effects, match


class MatchedControlsTests(unittest.TestCase):
    def test_matching_is_deterministic_and_equal_by_frequency(self):
        usage = Counter({'p1': 1, 'p2': 2, 'p3': 5, 'x': 1, 'y': 2, 'z': 2})
        pos = {'p1': 'prep', 'p2': 'prep', 'p3': 'prep', 'x': 'n', 'y': 'v', 'z': 'n'}
        selected, controls = match(usage, pos, 17, [100, 101])
        self.assertEqual((selected, controls), match(usage, pos, 17, [100, 101]))
        self.assertEqual(selected, {'p1', 'p2'})
        for control in controls:
            self.assertEqual(sorted(usage[x] for x in control), [1, 2])
            self.assertFalse(control & selected)

    def test_projection_counts_empty_and_nonempty_collision_separately(self):
        rows = [{'head': 'h', 'clauses': [['p', 'x'], ['q', 'x'], ['p']]}]
        result = effects(rows, {'p', 'q'})
        self.assertEqual(result['new_empty_branches'], 1)
        self.assertEqual(result['heads_with_new_empty'], 1)
        self.assertEqual(result['collision_heads'], 1)
        self.assertEqual(result['collision_excess'], 1)
        with self.assertRaises(ValueError):
            effects([{'head': 'h', 'clauses': [[]]}], {'p'})
