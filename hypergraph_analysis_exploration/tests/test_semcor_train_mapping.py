import unittest
from src.analysis.semcor_train_mapping import adjective_relaxed_recovery, classify, partition


class SemcorMappingTests(unittest.TestCase):
    def test_partition_is_reproducible_disjoint_and_complete(self):
        ids = [f'doc{i}' for i in range(20)]
        result = partition(ids)
        self.assertEqual(result, partition(list(reversed(ids))))
        self.assertEqual([len(result[k]) for k in ('train', 'dev', 'test')], [14, 3, 3])
        self.assertEqual(len(set().union(*map(set, result.values()))), 20)
        with self.assertRaises(ValueError):
            partition(['x', 'x'])

    def test_mapping_categories_and_strict_candidate_check(self):
        nodes = {'a': {'lemmas': 'ice cream / dessert', 'pos': 'n'}}
        self.assertEqual(classify('x', 'x', 'n', {}, nodes), 'no_exact_key')
        self.assertEqual(classify('x', 'x', 'n', {'x': {'a', 'b'}}, nodes), 'multiple_oewn_targets')
        self.assertEqual(classify('x', 'x', 'n', {'x': {'b'}}, nodes), 'target_absent_from_graph')
        self.assertEqual(classify('x', 'other', 'n', {'x': {'a'}}, nodes), 'target_not_in_strict_lemma_pos_candidates')
        self.assertEqual(classify('X', 'ice_cream', 'n', {'x': {'a'}}, nodes), 'strict_candidate_covered')
        prefixed = {'oewn-00000001-n': {'lemmas': 'dog', 'pos': 'n'}}
        self.assertEqual(classify('x', 'dog', 'n', {'x': {'00000001-n'}}, prefixed), 'strict_candidate_covered')
        adj = {'oewn-00000002-s': {'lemmas': 'good', 'pos': 'a'}}
        self.assertEqual(classify('x', 'good', 's', {'x': {'00000002-s'}}, adj), 'target_not_in_strict_lemma_pos_candidates')
        self.assertTrue(adjective_relaxed_recovery('x', 'good', 's', {'x': {'00000002-s'}}, adj))
        self.assertFalse(adjective_relaxed_recovery('x', 'bad', 's', {'x': {'00000002-s'}}, adj))
