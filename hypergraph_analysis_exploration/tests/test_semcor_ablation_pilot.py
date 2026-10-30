import json
import unittest
from src.analysis.semcor_ablation_pilot import make_texts


class SemcorAblationTests(unittest.TestCase):
    def test_same_dependencies_and_complete_branch_under_budget(self):
        row = {'synset_id': 'h', 'definition': 'target'}
        texts, status = make_texts(row, [['x'], ['y', 'z']], {'x': 'one', 'y': 'two', 'z': 'three'}, list, 1000)
        self.assertEqual(status, 'all')
        values = {key: json.loads(text) for key, text in texts.items()}
        self.assertEqual(values['B']['dependencies'], values['C']['dependencies'])
        self.assertEqual(values['B']['dependencies'], values['D']['dependencies'])
        self.assertEqual(values['D']['branches'], [['x'], ['y', 'z']])

    def test_base_over_budget_excludes_all_conditions(self):
        row = {'synset_id': 'h', 'definition': 'target'}
        texts, status = make_texts(row, [['x']], {'x': 'one'}, list, 1)
        self.assertIsNone(texts)
        self.assertEqual(status, 'base_over_budget')
