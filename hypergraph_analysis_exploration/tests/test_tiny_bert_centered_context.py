import unittest
from src.analysis.tiny_bert_centered_context import centered_window, replace_context


class CenteredContextTests(unittest.TestCase):
    def test_center_retains_target_at_both_ends(self):
        for target in ([0], [19], [10, 11]):
            result = centered_window([80, 81], list(range(20)), target, 8)
            self.assertEqual(result[:2], [80, 81])
            self.assertTrue(all(i in result[2:] for i in target))
        with self.assertRaises(ValueError):
            centered_window([1] * 8, [2], [0], 8)

    def test_every_target_span_fits_when_budget_allows(self):
        for length in range(1, 21):
            for start in range(length):
                for end in range(start + 1, min(length, start + 5) + 1):
                    target = list(range(start, end))
                    result = centered_window([1000, 1001], list(range(length)), target, 7)
                    self.assertLessEqual(len(result), 7)
                    self.assertTrue(all(i in result[2:] for i in target))

    def test_candidate_and_label_preserved(self):
        sequence = [101, 5, 6, 102, 7, 8, 102, 0, 0]
        row = {'sample_id': 's', 'label': 0, 'inputs': {v: [sequence] for v in 'ABCD'}}
        result = replace_context(row, [5, 6], [9, 10], 9)
        self.assertEqual(result['label'], 0)
        self.assertEqual(result['inputs']['D'][0], [101, 9, 10, 102, 7, 8, 102, 0, 0])
        with self.assertRaises(ValueError):
            replace_context(row, [5], [9], 9)


if __name__ == '__main__':
    unittest.main()
