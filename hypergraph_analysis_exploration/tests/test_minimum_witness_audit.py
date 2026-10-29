import random
import unittest
from itertools import product

from src.analysis.frozen_hypergraph_audit import validate_witnesses
from src.analysis.minimum_witness_audit import (
    _witness_rows,
    minimum_depth_clauses_by_head,
    minimum_derivation_depths,
)
from src.analysis.minimum_witness_basis_support import (
    global_minimum_basis_support_masks,
    local_minimum_basis_support_masks,
)
from src.analysis.global_minimum_witness_basis_support import stratified_support_impact


def relaxation_reference(heads, clauses, basis):
    """Independent repeated relaxation for small test hypergraphs."""
    depths = {node: 0 for node in basis}
    changed = True
    while changed:
        changed = False
        for head, body in clauses:
            if head in basis or any(node not in depths for node in body):
                continue
            candidate = 1 + max((depths[node] for node in body), default=0)
            if head not in depths or candidate < depths[head]:
                depths[head] = candidate
                changed = True
    if set(depths) != heads:
        raise ValueError("unreachable head in reference")
    return depths


class MinimumWitnessAuditTests(unittest.TestCase):
    def test_grounded_cycles_do_not_self_bootstrap_and_minimum_witness_replays(self):
        heads = {"seed", "a", "b", "c"}
        basis = {"seed"}
        clauses = [
            ("a", ("seed",)),
            ("a", ("b",)),
            ("b", ("a",)),
            ("c", ("a", "b")),
        ]

        depths = minimum_derivation_depths(heads, clauses, basis)

        self.assertEqual(depths, {"seed": 0, "a": 1, "b": 2, "c": 3})
        rules = {head: [tuple(body) for rule_head, body in clauses if rule_head == head]
                 for head in heads}
        minimizing = minimum_depth_clauses_by_head(heads, clauses, depths, basis)
        rows = _witness_rows(heads, basis, depths, minimizing)
        self.assertEqual(minimizing["a"], [("seed",)])
        result = validate_witnesses(heads, basis, rules, rows)
        self.assertTrue(result["all_valid"])

    def test_unreachable_cycle_is_not_treated_as_grounded(self):
        heads = {"seed", "a", "b"}
        clauses = [("a", ("b",)), ("b", ("a",))]
        with self.assertRaisesRegex(ValueError, "no grounded derivation"):
            minimum_derivation_depths(heads, clauses, {"seed"})

    def test_priority_queue_matches_independent_relaxation_on_random_graphs(self):
        for seed in range(16):
            rng = random.Random(seed)
            heads = {f"n{node}" for node in range(7)}
            basis = {"n0"}
            clauses = [(f"n{node}", (f"n{node - 1}",)) for node in range(1, 7)]
            for head in sorted(heads - basis):
                for _ in range(rng.randrange(3)):
                    candidates = sorted(heads - {head})
                    width = rng.randint(1, min(3, len(candidates)))
                    body = tuple(sorted(rng.sample(candidates, width)))
                    clauses.append((head, body))

            actual = minimum_derivation_depths(heads, clauses, basis)
            expected = relaxation_reference(heads, clauses, basis)
            self.assertEqual(actual, expected, f"seed={seed}")

    def test_basis_support_envelope_preserves_or_and_structure(self):
        heads = {"a", "b", "x", "both", "either", "root"}
        basis = {"a", "b"}
        clauses = [
            ("x", ("a",)),
            ("x", ("b",)),
            ("both", ("a", "b")),
            ("either", ("a",)),
            ("either", ("b",)),
            ("root", ("x", "both")),
        ]
        depths = minimum_derivation_depths(heads, clauses, basis)
        minimizing = minimum_depth_clauses_by_head(heads, clauses, depths, basis)

        possible, certain = local_minimum_basis_support_masks(
            heads, basis, depths, minimizing
        )

        bit_a = 1 << sorted(basis).index("a")
        bit_b = 1 << sorted(basis).index("b")
        self.assertEqual(possible["x"], bit_a | bit_b)
        self.assertEqual(certain["x"], 0)
        self.assertEqual(possible["both"], bit_a | bit_b)
        self.assertEqual(certain["both"], bit_a | bit_b)
        self.assertEqual(possible["either"], bit_a | bit_b)
        self.assertEqual(certain["either"], 0)
        self.assertEqual(possible["root"], bit_a | bit_b)
        self.assertEqual(certain["root"], bit_a | bit_b)

    def test_empty_alternative_removes_certain_basis_support(self):
        heads = {"seed", "node"}
        basis = {"seed"}
        clauses = [("node", ("seed",)), ("node", ())]
        depths = minimum_derivation_depths(heads, clauses, basis)
        minimizing = minimum_depth_clauses_by_head(heads, clauses, depths, basis)

        possible, certain = local_minimum_basis_support_masks(
            heads, basis, depths, minimizing
        )

        self.assertEqual(possible["node"], 1)
        self.assertEqual(certain["node"], 0)

    def test_support_masks_match_exhaustive_local_minimum_witnesses(self):
        for seed in range(20):
            rng = random.Random(seed)
            basis = {"n0", "n1"}
            heads = {f"n{index}" for index in range(6)}
            clauses = []
            for index in range(2, 6):
                head = f"n{index}"
                candidates = [f"n{prior}" for prior in range(index)]
                clauses.append((head, (rng.choice(candidates),)))
                for _ in range(rng.randrange(3)):
                    width = rng.randint(1, min(3, len(candidates)))
                    body = tuple(sorted(rng.sample(candidates, width)))
                    clauses.append((head, body))

            depths = minimum_derivation_depths(heads, clauses, basis)
            minimizing = minimum_depth_clauses_by_head(heads, clauses, depths, basis)
            possible, certain = local_minimum_basis_support_masks(
                heads, basis, depths, minimizing
            )

            family = {
                node: [1 << sorted(basis).index(node)]
                for node in basis
            }
            for head in sorted(heads - basis, key=lambda node: (depths[node], node)):
                supports = set()
                for body in minimizing[head]:
                    dependency_families = [family[dependency] for dependency in body]
                    combinations = product(*dependency_families) if body else [()]
                    for combination in combinations:
                        support_mask = 0
                        for mask in combination:
                            support_mask |= mask
                        supports.add(support_mask)
                family[head] = sorted(supports)

            for head in heads:
                exhaustive_possible = 0
                for mask in family[head]:
                    exhaustive_possible |= mask
                exhaustive_certain = family[head][0]
                for mask in family[head][1:]:
                    exhaustive_certain &= mask
                self.assertEqual(possible[head], exhaustive_possible, f"seed={seed}, head={head}")
                self.assertEqual(certain[head], exhaustive_certain, f"seed={seed}, head={head}")

    def test_global_minimum_support_includes_slack_subproofs(self):
        heads = {"p", "q", "x", "a", "y", "b", "root"}
        basis = {"p", "q"}
        clauses = [
            ("x", ("q",)),
            ("a", ("p",)),
            ("a", ("x",)),
            ("y", ("q",)),
            ("b", ("y",)),
            ("root", ("a", "b")),
        ]
        depths = minimum_derivation_depths(heads, clauses, basis)
        local_clauses = minimum_depth_clauses_by_head(heads, clauses, depths, basis)
        local_possible, local_certain = local_minimum_basis_support_masks(
            heads, basis, depths, local_clauses
        )
        global_possible, global_certain, states = global_minimum_basis_support_masks(
            heads, basis, depths, clauses
        )

        bit_p = 1 << sorted(basis).index("p")
        bit_q = 1 << sorted(basis).index("q")
        self.assertEqual(depths["root"], 3)
        self.assertEqual(local_certain["root"], bit_p | bit_q)
        self.assertEqual(global_possible["root"], bit_p | bit_q)
        self.assertEqual(global_certain["root"], bit_q)
        self.assertGreater(states, len(heads))
        clauses_by_head = {head: [] for head in heads}
        for head, body in clauses:
            clauses_by_head[head].append(body)
        strata = stratified_support_impact(
            heads, depths, clauses_by_head, local_possible, local_certain,
            global_possible, global_certain,
        )
        for rows in strata.values():
            self.assertEqual(sum(row["head_count"] for row in rows), len(heads))
            self.assertEqual(
                sum(row["possible_pairs_added"] for row in rows),
                sum((global_possible[node] & ~local_possible[node]).bit_count() for node in heads),
            )

    def test_global_support_keeps_basis_leaf_and_rule_as_alternatives(self):
        heads = {"p", "q", "x", "root"}
        basis = {"p", "q"}
        clauses = [("p", ("q",)), ("x", ("q",)), ("root", ("p", "x"))]
        depths = minimum_derivation_depths(heads, clauses, basis)
        possible, certain, _ = global_minimum_basis_support_masks(
            heads, basis, depths, clauses
        )
        bit_p = 1 << sorted(basis).index("p")
        bit_q = 1 << sorted(basis).index("q")
        self.assertEqual(possible["p"], bit_p)
        self.assertEqual(certain["p"], bit_p)
        self.assertEqual(possible["root"], bit_p | bit_q)
        self.assertEqual(certain["root"], bit_q)

    def test_global_support_masks_match_bounded_proof_enumeration(self):
        for seed in range(12):
            rng = random.Random(100 + seed)
            basis = {"n0", "n1"}
            heads = {f"n{index}" for index in range(6)}
            clauses = []
            for index in range(2, 6):
                head = f"n{index}"
                candidates = [f"n{prior}" for prior in range(index)]
                clauses.append((head, (rng.choice(candidates),)))
                for _ in range(rng.randrange(3)):
                    width = rng.randint(1, min(3, len(candidates)))
                    body = tuple(sorted(rng.sample(candidates, width)))
                    clauses.append((head, body))

            depths = minimum_derivation_depths(heads, clauses, basis)
            possible, certain, _ = global_minimum_basis_support_masks(
                heads, basis, depths, clauses
            )
            basis_bits = {node: 1 << index for index, node in enumerate(sorted(basis))}
            by_head = {head: [] for head in heads}
            for head, body in clauses:
                by_head[head].append(body)

            from functools import lru_cache

            @lru_cache(maxsize=None)
            def enumerate_supports(head, budget):
                supports = []
                if head in basis:
                    supports.append(basis_bits[head])
                if budget >= 1:
                    for body in by_head[head]:
                        if any(depths[dep] > budget - 1 for dep in body):
                            continue
                        dep_families = [enumerate_supports(dep, budget - 1) for dep in body]
                        combinations = product(*dep_families) if body else [()]
                        for combination in combinations:
                            mask = 0
                            for dep_mask in combination:
                                mask |= dep_mask
                            supports.append(mask)
                return tuple(supports)

            for head in heads:
                family = enumerate_supports(head, depths[head])
                self.assertTrue(family, f"seed={seed}, head={head}")
                expected_possible = 0
                for mask in family:
                    expected_possible |= mask
                expected_certain = family[0]
                for mask in family[1:]:
                    expected_certain &= mask
                self.assertEqual(possible[head], expected_possible, f"seed={seed}, head={head}")
                self.assertEqual(certain[head], expected_certain, f"seed={seed}, head={head}")


if __name__ == "__main__":
    unittest.main()
