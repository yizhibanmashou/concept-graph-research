import unittest
from src.analysis.preposition_stratified_controls import stratify


class StratifiedControlTests(unittest.TestCase):
    def test_changed_and_collision_and_empty_in_target_strata(self):
        nodes = {'h': {'source_root': 's', 'pos': 'n'}, 'j': {'source_root': 's', 'pos': 'v'}}
        rows = [{'head': 'h', 'clauses': [['p', 'x'], ['q', 'x']]},
                {'head': 'j', 'clauses': [['p']]}]
        result = stratify(rows, nodes, {'p', 'q'})
        data = {(x['head_pos'], x['branch_bin']): x for x in result}
        self.assertEqual(data['n', 'two']['collision_heads'], 1)
        self.assertEqual(data['v', 'one']['heads_with_new_empty'], 1)
        self.assertEqual(sum(x['changed_heads'] for x in result), 2)
