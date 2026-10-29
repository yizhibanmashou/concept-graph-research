import unittest
from src.analysis.reverse_dictionary_pilot import GlossIndex


class ReverseDictionaryTests(unittest.TestCase):
    def test_ranks_gloss_terms_without_target_labels(self):
        rows = [dict(synset_id='a', lemmas='cat', definition='small furry animal'),
                dict(synset_id='b', lemmas='table', definition='flat wooden furniture')]
        index = GlossIndex(rows)
        self.assertEqual(index.search('furry animal')[0]['id'], 'a')
        self.assertEqual(index.search('unknown'), [])

    def test_duplicate_id_is_rejected(self):
        row = dict(synset_id='a', lemmas='x', definition='thing')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            GlossIndex([row, row])


if __name__ == '__main__': unittest.main()
