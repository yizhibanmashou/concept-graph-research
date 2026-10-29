import unittest
import random

from src.analysis.dependency_projection_scc import _strong_components, analyze_projection


class DependencyProjectionSCCTests(unittest.TestCase):
    def test_candidate_projection_can_cycle_while_selected_witness_stays_acyclic(self):
        heads = {"seed", "a", "b"}
        clauses = [
            ("a", ("seed",)),
            ("a", ("b",)),
            ("b", ("a",)),
        ]
        basis = {"seed"}
        witnesses = {
            "seed": {"proof_depth": 0, "witness_clause": []},
            "a": {"proof_depth": 1, "witness_clause": ["seed"]},
            "b": {"proof_depth": 2, "witness_clause": ["a"]},
        }

        result = analyze_projection(heads, clauses, basis, witnesses)

        self.assertEqual(result["unique_projected_arc_count"], 3)
        self.assertEqual(result["cyclic_component_count"], 1)
        self.assertEqual(result["cyclic_component_size_distribution"]["max"], 2)
        self.assertTrue(result["selected_witness"]["strict_depth_increase_dependency_to_head"])
        self.assertEqual(result["selected_witness"]["raw_dependency_count"], 2)

    def test_counts_self_loops_and_duplicate_projected_arcs(self):
        heads = {"a", "b"}
        clauses = [
            ("a", ("b",)),
            ("a", ("b", "a")),
            ("b", ("a",)),
        ]
        result = analyze_projection(heads, clauses, heads, {})

        self.assertEqual(result["raw_dependency_literal_count"], 4)
        self.assertEqual(result["unique_projected_arc_count"], 3)
        self.assertEqual(result["repeated_projected_arc_count_across_alternative_clauses"], 1)
        self.assertEqual(result["self_loop_arc_count"], 1)
        self.assertEqual(result["cyclic_component_count"], 1)
        self.assertEqual(result["cyclic_component_size_distribution"]["max"], 2)

    def test_iterative_scc_matches_mutual_reachability_reference(self):
        for seed in range(12):
            rng = random.Random(seed)
            node_count = 7
            pairs = {
                (source, target)
                for source in range(node_count)
                for target in range(node_count)
                if rng.random() < 0.22
            }
            encoded = {source * node_count + target for source, target in pairs}
            component_by_node, _ = _strong_components(node_count, encoded)

            reachable = [{node} for node in range(node_count)]
            for source, target in pairs:
                reachable[source].add(target)
            for pivot in range(node_count):
                for source in range(node_count):
                    if pivot in reachable[source]:
                        reachable[source].update(reachable[pivot])
            actual = {
                frozenset(node for node in range(node_count)
                          if component_by_node[node] == component_by_node[root])
                for root in range(node_count)
            }
            expected = {
                frozenset(other for other in range(node_count)
                          if other in reachable[node] and node in reachable[other])
                for node in range(node_count)
            }
            self.assertEqual(actual, expected, f"seed={seed}")


if __name__ == "__main__":
    unittest.main()
