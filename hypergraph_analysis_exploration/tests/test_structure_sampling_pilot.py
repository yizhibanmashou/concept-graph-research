import unittest

from src.analysis.structure_sampling_pilot import summarize


class StructureSamplingPilotTests(unittest.TestCase):
    def test_strata_and_deterministic_sampling(self):
        positions = {'a': 'n', 'b': 'prep', 'c': 'v'}
        rules = [
            {'head': 'h1', 'clauses': [['a']]},
            {'head': 'h2', 'clauses': [['a', 'b'], ['c']]},
            {'head': 'h3', 'clauses': [['a'], ['c']]},
        ]
        result = summarize(rules, positions, sample_size=1, seed=17)
        self.assertEqual(result['counts'], {'multi/joint/prep': 1,
                                           'multi/singleton/no_prep': 1,
                                           'single/singleton/no_prep': 1})
        self.assertEqual(result, summarize(rules, positions, sample_size=1, seed=17))
        self.assertEqual(result['sample_ids']['multi/joint/prep'], ['h2'])

    def test_rejects_missing_dependency_and_duplicate_head(self):
        with self.assertRaisesRegex(ValueError, 'missing'):
            summarize([{'head': 'h', 'clauses': [['missing']]}], {})
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            summarize([{'head': 'h', 'clauses': [['a']]},
                       {'head': 'h', 'clauses': [['a']]}], {'a': 'n'})

    def test_rejects_empty_clause_instead_of_calling_it_singleton(self):
        with self.assertRaisesRegex(ValueError, 'empty clause'):
            summarize([{'head': 'h', 'clauses': [[]]}], {})

    def test_reservoir_is_bounded_and_repeatable(self):
        rules = [{'head': str(i), 'clauses': [['a']]} for i in range(20)]
        result = summarize(rules, {'a': 'n'}, sample_size=3, seed=17)
        self.assertEqual(result['counts']['single/singleton/no_prep'], 20)
        self.assertEqual(len(result['sample_ids']['single/singleton/no_prep']), 3)
        self.assertEqual(result, summarize(rules, {'a': 'n'}, sample_size=3, seed=17))


if __name__ == '__main__':
    unittest.main()
