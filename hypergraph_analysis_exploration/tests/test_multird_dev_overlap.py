import unittest

from src.analysis.multird_dev_overlap import audit, normalize


class DevelopmentOverlapTests(unittest.TestCase):
    def test_only_matching_gloss_and_target_count_as_aligned(self):
        nodes = [{'definition': '  A  Example ', 'lemmas': 'one/TWO'},
                 {'definition': 'something else', 'lemmas': 'three'}]
        rows = [{'word': 'two', 'definitions': 'a example'},
                {'word': 'three', 'definitions': 'a example'},
                {'word': 'four', 'definitions': 'absent'}]
        self.assertEqual(audit(rows, nodes), {'records': 3, 'unique_words': 3, 'eligible_records': 3,
            'empty_words': 0, 'empty_definitions': 0,
            'exact_definition_records': 2, 'exact_definition_unique_words': 2,
            'exact_definition_and_lemma_records': 1, 'exact_definition_and_lemma_unique_words': 1})
        self.assertEqual(normalize('  Ä\tWORD  '), 'ä word')

    def test_empty_inputs_are_counted_but_ineligible(self):
        result = audit([{'word': ' ', 'definitions': 'x'}, {'word': 'w', 'definitions': ' '}], [])
        self.assertEqual((result['empty_words'], result['empty_definitions'], result['eligible_records']), (1, 1, 0))


if __name__ == '__main__':
    unittest.main()
