import unittest
from src.analysis.wsd_pilot import candidates


class WsdPilotTests(unittest.TestCase):
    def test_exact_lemma_and_pos_select_all_matching_senses(self):
        rows = [dict(synset_id='a', lemmas='bank / banking company', pos='n'),
                dict(synset_id='b', lemmas='bank', pos='v'),
                dict(synset_id='c', lemmas='riverbank', pos='n')]
        self.assertEqual([r['synset_id'] for r in candidates(rows, 'BANK', 'n')], ['a'])


if __name__ == '__main__': unittest.main()
