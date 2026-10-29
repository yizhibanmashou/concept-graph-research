import unittest
from backend.reasoning import closure, rank_alternatives


class ReasoningTests(unittest.TestCase):
    def setUp(self):
        self.rules = {'target': [['a','b'],['c']], 'c':[['d']], 'cycle_a':[['cycle_b']], 'cycle_b':[['cycle_a']], 'missing_head':[['absent']]}

    def test_and_requires_every_prerequisite(self):
        self.assertNotIn('target', closure(self.rules, {'a'}))
        self.assertIn('target', closure(self.rules, {'a','b'}))

    def test_alternative_and_multistep(self):
        result=closure(self.rules, {'d'})
        self.assertIn('c',result)
        self.assertIn('target',result)
        self.assertEqual(result['target'],2)

    def test_cycle_is_not_bootstrapped(self):
        self.assertNotIn('cycle_a',closure(self.rules,set()))
        self.assertIn('cycle_b',closure(self.rules,{'cycle_a'}))

    def test_missing_and_duplicate_dependencies(self):
        self.assertNotIn('missing_head',closure(self.rules,set()))
        self.assertIn('x',closure({'x':[['a','a']]},{'a'}))

    def test_ranking_and_increment(self):
        costs=closure(self.rules,{'d'})
        ranked=rank_alternatives(self.rules['target'],costs)
        self.assertEqual(ranked[0]['index'],1)
        self.assertTrue(ranked[0]['complete'])
        before=set(closure(self.rules,{'a'}))
        after=set(closure(self.rules,{'a','b'}))
        self.assertEqual(after-before,{'b','target'})

if __name__ == '__main__': unittest.main()
