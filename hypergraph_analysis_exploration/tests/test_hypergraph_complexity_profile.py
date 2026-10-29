import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.hypergraph_complexity_profile import build_profile, depth_bin


class HypergraphComplexityProfileTests(unittest.TestCase):
    def test_depth_bins_cover_boundaries(self):
        self.assertEqual(depth_bin(0), "0")
        self.assertEqual(depth_bin(5), "1-5")
        self.assertEqual(depth_bin(6), "6-25")
        self.assertEqual(depth_bin(300), "101-300")
        self.assertEqual(depth_bin(301), "301+")

    def test_profile_reports_structural_depth_and_rule_alternatives(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir)
            graph_dir = bundle / "graph"
            graph_dir.mkdir()
            rules = [
                {"head": "seed", "clauses": []},
                {"head": "a", "clauses": [["seed"], ["seed", "seed2"]]},
                {"head": "b", "clauses": [["a", "seed"]]},
                {"head": "seed2", "clauses": []},
            ]
            witnesses = [
                {"head": "seed", "is_seed": True, "proof_depth": 0, "witness_clause": []},
                {"head": "seed2", "is_seed": True, "proof_depth": 0, "witness_clause": []},
                {"head": "a", "is_seed": False, "proof_depth": 1, "witness_clause": ["seed"]},
                {"head": "b", "is_seed": False, "proof_depth": 2, "witness_clause": ["a", "seed"]},
            ]
            (graph_dir / "hypergraph_rules.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rules), encoding="utf-8"
            )
            (graph_dir / "selected_basis_atoms.txt").write_text("seed\nseed2\n", encoding="utf-8")
            (graph_dir / "coverage_witnesses.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in witnesses), encoding="utf-8"
            )

            report = build_profile(bundle)

        self.assertTrue(report["witness_certificate_validation"]["all_valid"])
        self.assertEqual(report["graph_size"]["head_count"], 4)
        self.assertEqual(report["heads_with_multiple_alternative_clauses"], 1)
        self.assertEqual(report["depth_strata"]["1-5"]["head_count"], 2)
        self.assertEqual(report["depth_strata"]["1-5"]["heads_with_multiple_alternatives"], 1)
        self.assertEqual(report["depth_strata"]["1-5"]["selected_witness_and_width"]["median"], 1.5)
        selected = report["selected_witness_dag"]
        self.assertEqual(selected["edge_count"], 3)
        self.assertEqual(selected["dependency_parent_count_including_zero_use_heads"]["max"], 2)
        self.assertEqual(selected["basis_atoms_used_as_dependencies"], 1)
        self.assertEqual(selected["basis_atoms_unused_as_dependencies"], 1)
        self.assertEqual(
            selected["depth_strata_by_dependency_node"]["0"]["dependency_parent_count"]["max"], 2
        )


if __name__ == "__main__":
    unittest.main()
