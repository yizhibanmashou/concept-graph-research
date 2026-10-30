import unittest
from src.analysis.tiny_bert_context_target_audit import classify_target


class TargetOffsetTests(unittest.TestCase):
    def test_full_partial_none_and_missing(self):
        offsets = [(0, 2), (3, 5), (5, 7), (8, 9)]
        self.assertEqual(classify_target(offsets, 3, 7, 3), 'full')
        self.assertEqual(classify_target(offsets, 3, 7, 2), 'partial')
        self.assertEqual(classify_target(offsets, 3, 7, 1), 'none')
        self.assertEqual(classify_target(offsets, 10, 11, 3), 'unlocatable')


if __name__ == '__main__':
    unittest.main()
