import unittest

from src.analysis.frozen_hypergraph_audit import validate_witnesses


class WitnessValidationTests(unittest.TestCase):
    def setUp(self):
        self.heads = {"a", "b", "h", "z"}
        self.basis = {"a", "b"}
        self.rules = {
            "h": [("a", "b")],
            "z": [("h",)],
        }
        self.rows = [
            {"head": "a", "is_seed": True, "proof_depth": 0, "witness_clause": []},
            {"head": "b", "is_seed": True, "proof_depth": 0, "witness_clause": []},
            {"head": "h", "is_seed": False, "proof_depth": 1, "witness_clause": ["a", "b"]},
            {"head": "z", "is_seed": False, "proof_depth": 2, "witness_clause": ["h"]},
        ]

    def test_accepts_complete_exact_depth_witness_dag(self):
        result = validate_witnesses(self.heads, self.basis, self.rules, self.rows)
        self.assertTrue(result["all_valid"])
        self.assertEqual(result["missing_head_count"], 0)
        self.assertEqual(result["wrong_depth_count"], 0)

    def test_rejects_seed_mismatch_and_noncanonical_depth(self):
        rows = [dict(row) for row in self.rows]
        rows[0]["is_seed"] = False
        rows[3]["proof_depth"] = 3
        result = validate_witnesses(self.heads, self.basis, self.rules, rows)
        self.assertFalse(result["all_valid"])
        self.assertEqual(result["seed_flag_mismatch_count"], 1)
        self.assertEqual(result["wrong_depth_count"], 1)

    def test_rejects_missing_duplicate_and_unexpected_records(self):
        rows = [row for row in self.rows if row["head"] != "b"]
        rows.extend([
            dict(self.rows[0]),
            {"head": "extra", "is_seed": True, "proof_depth": 0, "witness_clause": []},
        ])
        result = validate_witnesses(self.heads, self.basis, self.rules, rows)
        self.assertFalse(result["all_valid"])
        self.assertEqual(result["missing_head_count"], 1)
        self.assertEqual(result["duplicate_head_count"], 1)
        self.assertEqual(result["unexpected_head_count"], 1)

    def test_rejects_duplicate_literals_and_non_boolean_seed_marker(self):
        rows = [dict(row) for row in self.rows]
        rows[2]["witness_clause"] = ["a", "a", "b"]
        rows[3]["is_seed"] = 0
        result = validate_witnesses(self.heads, self.basis, self.rules, rows)
        self.assertFalse(result["all_valid"])
        self.assertEqual(result["seed_flag_mismatch_count"], 1)
        self.assertGreater(result["invalid_head_count"], 0)


if __name__ == "__main__":
    unittest.main()
