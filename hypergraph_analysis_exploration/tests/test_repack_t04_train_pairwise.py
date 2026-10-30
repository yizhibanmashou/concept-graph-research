import unittest

from src.analysis.repack_t04_train_pairwise import rebuild_rows
from src.analysis.tiny_bert_wsd_train import conditions_for_run, should_evaluate


class RepackT04TrainPairwiseTests(unittest.TestCase):
    def test_rebuilds_all_conditions_without_changing_train_labels_or_context(self):
        row = {'sample_id': 's1', 'candidate_ids': ['a', 'b'],
               'scorable_candidate_ids': ['a', 'b'], 'label': 1,
               'inputs': {key: [[101, 11, 102, 3, 102, 0, 0, 0],
                                [101, 11, 102, 4, 102, 0, 0, 0]] for key in 'ABCD'}}
        def prepare(candidate_id):
            return {key: [ord(key)] for key in 'ABCD'}

        output, stats = rebuild_rows([row], prepare, joint_budget=8)
        self.assertEqual(output[0]['label'], 1)
        self.assertEqual(output[0]['candidate_ids'], ['a', 'b'])
        self.assertEqual(output[0]['inputs']['C'][0], [101, 11, 102, ord('C'), 102, 0, 0, 0])
        self.assertEqual(stats['scorable_targets'], 1)
        self.assertEqual(stats['candidate_instances'], 2)

    def test_rejects_nonshared_train_context(self):
        row = {'sample_id': 's1', 'candidate_ids': ['a'], 'label': 0,
               'inputs': {key: [[101, 11, 102, 3, 102, 0]] for key in 'ABCD'}}
        row['inputs']['D'][0][1] = 12
        with self.assertRaisesRegex(ValueError, 'share one train context'):
            rebuild_rows([row], lambda _: {key: [5] for key in 'ABCD'}, joint_budget=6)

    def test_train_only_keeps_all_conditions_and_skips_evaluation(self):
        self.assertEqual(conditions_for_run(smoke=False), tuple('ABCD'))
        self.assertFalse(should_evaluate(smoke=False, train_only=True))
        self.assertTrue(should_evaluate(smoke=False, train_only=False))


if __name__ == '__main__':
    unittest.main()
