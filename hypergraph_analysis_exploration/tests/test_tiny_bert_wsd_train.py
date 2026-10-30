import unittest
from src.analysis.tiny_bert_wsd_train import batchify_rows, validate


class TinyBertTrainTests(unittest.TestCase):
    def test_four_conditions_have_equal_candidates_and_valid_labels(self):
        row = {'sample_id': 'id', 'label': 1, 'inputs': {v: [[1, 0], [2, 0]] for v in 'ABCD'}}
        self.assertEqual(validate([row], 2), {'id'})
        row['inputs']['D'].append([3, 0])
        with self.assertRaises(ValueError):
            validate([row], 2)

    def test_duplicate_samples_are_rejected(self):
        row = {'sample_id': 'id', 'label': 0, 'inputs': {v: [[1, 0], [2, 0]] for v in 'ABCD'}}
        with self.assertRaises(ValueError):
            validate([row, row], 2)

    def test_batchify_rows_accepts_archived_rows_without_candidate_manifest(self):
        row = {'label': 1, 'inputs': {v: [[1, 0], [2, 0]] for v in 'ABCD'}}
        inputs, labels = batchify_rows([row], 'A', 2)
        self.assertEqual(inputs, [[[1, 0], [2, 0]]])
        self.assertEqual(labels, [1])

    def test_batchify_rows_preserves_unscorable_new_schema_targets(self):
        row = {'label': -1, 'candidate_ids': ['a', 'b'], 'scorable_candidate_ids': ['a'],
               'inputs': {v: [[1, 0]] for v in 'ABCD'}}
        inputs, labels = batchify_rows([row], 'D', 2)
        self.assertEqual(inputs, [[[1, 0]]])
        self.assertEqual(labels, [None])

    def test_batchify_rows_rejects_candidate_count_mismatch(self):
        row = {'label': 0, 'scorable_candidate_ids': ['a', 'b'],
               'inputs': {v: [[1, 0]] for v in 'ABCD'}}
        with self.assertRaisesRegex(ValueError, 'unexpected candidate shape'):
            batchify_rows([row], 'A', 2)
