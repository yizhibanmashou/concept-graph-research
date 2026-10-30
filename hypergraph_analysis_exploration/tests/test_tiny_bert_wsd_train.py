import unittest
from src.analysis.tiny_bert_wsd_train import validate


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
