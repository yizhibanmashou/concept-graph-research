import unittest

from src.analysis.preposition_sampling_frame_audit import classify_target


class PrepositionSamplingFrameAuditTests(unittest.TestCase):
    def test_new_empty_is_separate(self):
        self.assertEqual(classify_target([['prep-1'], ['noun-1']],
                                         {'prep-1': 'prep', 'noun-1': 'n'}),
                         'new_empty')

    def test_nonempty_pair_collision(self):
        self.assertEqual(classify_target([['prep-1', 'noun-1'], ['noun-1']],
                                         {'prep-1': 'prep', 'noun-1': 'n'}),
                         'new_collision')

    def test_empty_and_collision_are_both_counted(self):
        clauses = [['prep-1'], ['prep-2', 'noun-1'], ['noun-1']]
        positions = {'prep-1': 'prep', 'prep-2': 'prep', 'noun-1': 'n'}
        self.assertEqual(classify_target(clauses, positions), 'empty_and_collision')

    def test_ordinary_occurrence_removal_without_topology_collision(self):
        self.assertEqual(classify_target([['prep-1', 'noun-1'], ['noun-2']],
                                         {'prep-1': 'prep', 'noun-1': 'n', 'noun-2': 'n'}),
                         'other_affected')

    def test_unaffected_target(self):
        self.assertEqual(classify_target([['noun-1'], ['noun-2']],
                                         {'noun-1': 'n', 'noun-2': 'n'}),
                         'unaffected')


if __name__ == '__main__':
    unittest.main()
