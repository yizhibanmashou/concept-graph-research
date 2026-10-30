import unittest
from collections import Counter
from src.analysis.semcor_dev_pilot import build_index, mapped_target, norm, observed_key, pos_class, ranked_gloss, ranked_mfs


class SemcorDevPilotTests(unittest.TestCase):
    def test_adjective_candidates_and_strict_mapping(self):
        rows = [{'synset_id': 'oewn-a', 'lemmas': 'good', 'pos': 'a', 'definition': 'pleasant'},
                {'synset_id': 'oewn-b', 'lemmas': 'good', 'pos': 's', 'definition': 'healthy'}]
        index = build_index(rows)
        self.assertEqual(set(index['good', 'a']), {'oewn-a', 'oewn-b'})
        self.assertEqual(pos_class('s'), 'a')
        self.assertEqual(norm('Ice_Cream'), 'ice cream')
        self.assertEqual(mapped_target('key', {'key': {'a'}}, {r['synset_id']: r for r in rows}), ('oewn-a', None))

    def test_baselines_deterministic_and_no_gold_input(self):
        rows = {'x': {'synset_id': 'x', 'lemmas': 'bank', 'definition': 'money'},
                'y': {'synset_id': 'y', 'lemmas': 'bank', 'definition': 'river'}}
        self.assertEqual(ranked_mfs(rows, Counter({'y': 2})), 'y')
        self.assertEqual(ranked_mfs(rows, Counter()), 'x')
        self.assertEqual(ranked_gloss(rows, 'the river flows'), 'y')
        self.assertEqual(ranked_gloss(rows, 'unmatched'), 'x')

    def test_target_is_derived_from_surface_and_observed_pos(self):
        morph = lambda surface, pos: 'run' if surface == 'running' and pos == 'v' else None
        self.assertEqual(observed_key('running', 'VBG', morph), ('run', 'v'))
        self.assertEqual(observed_key('Unknown_Name', 'NNP', morph), ('unknown name', 'n'))
        self.assertIsNone(observed_key('and', 'CC', morph))
