from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.flattening_ablation import build_report
from src.analysis.frozen_hypergraph_audit import closure


class FlatteningAblationTests(unittest.TestCase):
    def test_existential_arcs_overgenerate_and_conjunctive_union_undergenerates(self):
        heads = {"basis_b", "basis_d", "target"}
        rules = {
            "basis_b": [],
            "basis_d": [],
            "target": [("basis_b", "missing_c"), ("basis_d",)],
        }
        clauses = [(head, body) for head, bodies in rules.items() for body in bodies]
        relaxed_clauses = [(head, (dep,)) for head, body in clauses for dep in body]
        strict_clauses = [
            (head, tuple(sorted({dep for body in bodies for dep in body})))
            for head, bodies in rules.items()
        ]
        existential_seeds = {"basis_b"}
        canonical_without_alternative = closure(heads, clauses, existential_seeds)
        self.assertNotIn("target", canonical_without_alternative)
        self.assertIn("target", closure(heads, relaxed_clauses, existential_seeds))

        conjunctive_seeds = {"basis_d"}
        canonical_with_alternative = closure(heads, clauses, conjunctive_seeds)
        self.assertIn("target", canonical_with_alternative)
        self.assertNotIn("target", closure(heads, strict_clauses, conjunctive_seeds))

    def test_build_report_uses_declared_or_of_and_semantics(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp)
            (bundle / "graph").mkdir()
            (bundle / "graph" / "hypergraph_rules.jsonl").write_text(
                '{"head":"b","clauses":[]}\n'
                '{"head":"c","clauses":[["b"]]}\n'
                '{"head":"h_relaxed","clauses":[["b","c"]]}\n'
                '{"head":"h_cycle","clauses":[["b"],["x"]]}\n'
                '{"head":"x","clauses":[["h_cycle"]]}\n',
                encoding="utf-8",
            )
            (bundle / "graph" / "selected_basis_atoms.txt").write_text("b\n", encoding="utf-8")
            result = build_report(bundle)
        self.assertEqual(result["canonical_and_or_closure"]["derived_count"], 5)
        self.assertEqual(
            result["flattening_comparisons"]["simple_arc_existential_relaxation"]["overgenerated_count"], 0
        )
        self.assertEqual(
            result["flattening_comparisons"]["simple_arc_conjunctive_union"]["undergenerated_count"], 2
        )
        self.assertEqual(result["derivation_depth_information_loss"]["heads_with_strictly_shorter_simple_arc_depth"], 1)


if __name__ == "__main__":
    unittest.main()
