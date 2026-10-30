import unittest
from src.analysis.tiny_bert_wsd_data import (candidate_ids_for_surface, choose_candidates,
                                             encode_target_centered_context, select)


class TinyBertDataTests(unittest.TestCase):
    def test_candidate_selection_does_not_accept_gold(self):
        ids = ['a', 'b', 'c', 'd', 'e']
        self.assertEqual(choose_candidates('example', ids), choose_candidates('example', list(reversed(ids))))
        self.assertEqual(len(choose_candidates('example', ids)), 4)

    def test_stable_sample_does_not_use_label(self):
        rows = [{'sample_id': 'b', 'doc': 'd', 'sentence': 1, 'token': 1, 'gold': 'x'},
                {'sample_id': 'a', 'doc': 'd', 'sentence': 1, 'token': 2, 'gold': 'y'}]
        self.assertEqual(select(rows, 1)[0]['sample_id'], 'a')
        rows[1]['gold'] = 'changed'
        self.assertEqual(select(rows, 1)[0]['sample_id'], 'a')

    def test_candidate_inventory_unions_all_gold_independent_morphology_analyses(self):
        index = {
            ('year', 'n'): {'sense-year': {}},
            ('years', 'n'): {'sense-years': {}},
            ('other', 'n'): {'sense-other': {}},
        }
        calls = []

        def all_morphy(surface, pos):
            calls.append((surface, pos))
            return ['years', 'year', 'years']

        candidates = candidate_ids_for_surface('Years', 'n', index, all_morphy)
        self.assertEqual(candidates, {'sense-year', 'sense-years'})
        self.assertEqual(calls, [('years', 'n')])

    def test_candidate_inventory_falls_back_to_normalized_surface(self):
        index = {('at the same time', 'r'): {'sense-1': {}}}
        candidates = candidate_ids_for_surface('At_the_same_Time', 'r', index, lambda _surface, _pos: [])
        self.assertEqual(candidates, {'sense-1'})

    def test_centered_context_brackets_actual_occurrence_and_respects_budget(self):
        words = ['left'] * 20 + ['pivot'] + ['right'] * 20

        def encode(text):
            return [1, 2] if text == 'target: pivot context:' else [3]

        ids, window = encode_target_centered_context(words, 20, 'pivot', encode, 90, 91, maximum=12)
        self.assertEqual(len(ids), 12)
        self.assertEqual(ids[window['target_piece_start'] - 1], 90)
        self.assertEqual(ids[window['target_piece_start']], 3)
        self.assertEqual(ids[window['target_piece_end']], 91)
        self.assertTrue(window['sentence_truncated'])

    def test_centered_context_rejects_mismatched_xml_position(self):
        with self.assertRaisesRegex(ValueError, 'does not match'):
            encode_target_centered_context(['first', 'second'], 0, 'second', lambda _text: [1], 90, 91)
