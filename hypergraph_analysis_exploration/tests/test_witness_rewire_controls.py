import unittest
from collections import Counter

from src.analysis.witness_rewire_controls import rewire


class RewireTests(unittest.TestCase):
    def test_degree_invariants_and_reproducibility(self):
        graph = {'a': ('b', 'c'), 'b': ('a', 'd'), 'c': ('a',), 'd': ('b',), 'e': ('e',)}
        changed, audit = rewire(graph, 101, 100)
        self.assertEqual((changed, audit), rewire(graph, 101, 100))
        self.assertGreater(audit['accepted'], 0)
        self.assertEqual({k: len(v) for k, v in graph.items()}, {k: len(v) for k, v in changed.items()})
        self.assertEqual(Counter(x for v in graph.values() for x in v), Counter(x for v in changed.values() for x in v))
        self.assertEqual(changed['e'], ('e',))
        self.assertTrue(all(len(v) == len(set(v)) for v in changed.values()))
        self.assertFalse(any(k in v for k, v in changed.items() if k != 'e'))

    def test_invalid_graph_is_rejected(self):
        with self.assertRaises(ValueError):
            rewire({'a': ('missing',)}, 1)
        with self.assertRaises(ValueError):
            rewire({'a': ('a', 'a')}, 1)

    def test_group_preservation_per_source(self):
        graph = {'a': ('b', 'c'), 'b': ('a', 'd'), 'c': ('a',), 'd': ('b',), 'e': ('e',)}
        groups = {'a': 'x', 'b': 'x', 'c': 'y', 'd': 'y', 'e': 'x'}
        changed, _ = rewire(graph, 101, 100, groups=groups)
        for head in graph:
            self.assertEqual(Counter(groups[x] for x in graph[head]), Counter(groups[x] for x in changed[head]))
        with self.assertRaises(ValueError):
            rewire(graph, 101, groups={'a': 'x'})


if __name__ == '__main__':
    unittest.main()
