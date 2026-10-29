import unittest
from src.analysis.witness_reuse_pilot import measure, simulate_lru


class WitnessReusePilotTests(unittest.TestCase):
    def test_diamond_and_shared_root_count_depth_sensitive_keys(self):
        graph = {'r': ('a', 'b'), 'a': ('c',), 'b': ('c',), 'c': ()}
        result = measure(graph, ['r', 'a'], 2)
        self.assertEqual(result['unfolded_node_visits'], 7)
        self.assertEqual(result['per_root_unique_node_depth_keys'], 6)
        self.assertEqual(result['across_root_unique_node_depth_keys'], 6)

    def test_zero_depth_counts_only_roots(self):
        self.assertEqual(measure({'r': ('a',), 'a': ()}, ['r'], 0)['unfolded_node_visits'], 1)

    def test_lru_capacity_zero_matches_unfolded_visits(self):
        graph = {'r': ('a', 'b'), 'a': ('c',), 'b': ('c',), 'c': ()}
        result = simulate_lru(graph, ['r'], 2, 0)
        self.assertEqual(result['computed_states'], 5)
        self.assertEqual(result['cache_hits'], 0)

    def test_sufficient_lru_capacity_reuses_repeated_root(self):
        graph = {'r': ('a', 'b'), 'a': ('c',), 'b': ('c',), 'c': ()}
        result = simulate_lru(graph, ['r', 'r'], 2, 4)
        self.assertEqual(result['computed_states'], 4)
        self.assertEqual(result['cache_hits'], 2)

    def test_measure_emits_deterministic_order_sensitivities(self):
        result = measure({'r': ('a',), 'a': ()}, ['r', 'a'], 1)
        orders = result['lru_cache_capacity_sensitivity']['root_orders']
        self.assertEqual(set(orders), {'listed', 'reverse', 'shuffle_seed_17'})
        self.assertEqual([row['capacity'] for row in orders['listed']], [0, 16, 64, 256, 1024, 4096, 16384, None])


if __name__ == '__main__': unittest.main()
