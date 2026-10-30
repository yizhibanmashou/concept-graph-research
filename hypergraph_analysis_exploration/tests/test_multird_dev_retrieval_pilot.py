import unittest

from src.analysis.multird_dev_retrieval_pilot import sample_groups, score, words_from_results


class DevelopmentRetrievalTests(unittest.TestCase):
    def test_sampling_ignores_target_word(self):
        rows = [{'word': 'a', 'definitions': 'x'}, {'word': 'b', 'definitions': 'y'}]
        selected = sample_groups(rows, {'x'}, 1)
        rows[0]['word'] = 'changed'
        self.assertEqual(selected, sample_groups(rows, {'x'}, 1))

    def test_word_dedup_and_rank_metrics(self):
        ranked = words_from_results([{'lemmas': 'ONE/two'}, {'lemmas': 'two/three'}])
        self.assertEqual(ranked, ['one', 'two', 'three'])
        self.assertEqual(score([1, 2, None]), {'queries': 3, 'top1': 1 / 3,
                         'recall_at_10': 2 / 3, 'mrr_at_100': .5})


if __name__ == '__main__':
    unittest.main()
