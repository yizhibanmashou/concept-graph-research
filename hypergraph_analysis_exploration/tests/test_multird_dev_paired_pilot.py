import unittest

from src.analysis.multird_dev_paired_pilot import select_pairs


class PairTests(unittest.TestCase):
    def test_pairs_match_word_and_require_both_groups(self):
        rows = [{'word': 'Word', 'definitions': 'match'}, {'word': 'word', 'definitions': 'different'},
                {'word': 'other', 'definitions': 'match'}]
        pairs, eligible = select_pairs(rows, {'match'})
        self.assertEqual(eligible, 1)
        self.assertEqual(pairs[0][1:], ('word', 0, 1))
        self.assertEqual(select_pairs(rows, {'match'}), (pairs, eligible))

    def test_no_valid_pairs(self):
        with self.assertRaises(ValueError):
            select_pairs([{'word': 'a', 'definitions': 'only'}], {'only'})


if __name__ == '__main__':
    unittest.main()
