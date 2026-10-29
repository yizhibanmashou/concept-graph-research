import unittest
from src.analysis.preposition_paired_review import prepare


def item(node_id, pos):
    return {'synset_id': node_id, 'lemmas': node_id, 'pos': pos, 'definition': node_id}


class PrepositionReviewTests(unittest.TestCase):
    def test_original_preserved_and_empty_and_collisions_exposed(self):
        nodes = {x: item(x, p) for x, p in [('h', 'n'), ('p', 'prep'), ('q', 'prep'), ('x', 'n')]}
        result = prepare(nodes, {'h': [['p', 'x'], ['q', 'x'], ['p']]}, ['h'], {'prep'})[0]
        self.assertEqual([x['synset_id'] for x in result['branches'][0]['original']], ['p', 'x'])
        self.assertEqual([x['synset_id'] for x in result['branches'][0]['deleted']], ['x'])
        self.assertEqual(result['nonempty_collapsed_excess'], 1)
        self.assertTrue(result['branches'][2]['newly_empty'])
        self.assertIsNone(result['branches'][0]['review']['source_fidelity'])

    def test_rejects_missing_duplicate_or_empty_source(self):
        nodes = {'h': item('h', 'n')}
        for rules, ids in [({'h': [[]]}, ['h']), ({'h': [['missing']]}, ['h']),
                           ({'h': [['h']]}, ['h', 'h'])]:
            with self.assertRaises(ValueError):
                prepare(nodes, rules, ids, {'prep'})
