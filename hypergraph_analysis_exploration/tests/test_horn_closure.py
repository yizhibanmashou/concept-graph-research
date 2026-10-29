import unittest

from src.analysis.frozen_hypergraph_audit import basis_sensitivity, closure


class HornClosureTests(unittest.TestCase):
    def setUp(self):
        # h has two alternative clauses: (a AND b) OR c; z depends on h.
        self.heads = {"h", "z", "a", "b", "c"}
        self.clauses = [
            ("h", ("a", "b")),
            ("h", ("c",)),
            ("z", ("h",)),
        ]

    def test_partial_conjunct_does_not_derive_head(self):
        self.assertEqual(closure(self.heads, self.clauses, {"a"}), {"a"})

    def test_one_complete_or_branch_derives_head_and_downstream(self):
        self.assertEqual(closure(self.heads, self.clauses, {"a", "b"}), {"a", "b", "h", "z"})
        self.assertEqual(closure(self.heads, self.clauses, {"c"}), {"c", "h", "z"})

    def test_flattening_branches_would_be_unsound(self):
        # A naïve projected rule h <- a,b,c would miss valid OR branches;
        # treating any edge as sufficient would incorrectly derive h from a.
        self.assertNotIn("h", closure(self.heads, self.clauses, {"a"}))
        self.assertIn("h", closure(self.heads, self.clauses, {"c"}))

    def test_basis_sensitivity_respects_alternative_clauses(self):
        heads = {"a", "b", "x", "y"}
        clauses = [("a", ("b",)), ("x", ("a",)), ("x", ("b",)), ("y", ("x",))]
        witnesses = {
            "a": {"witness_clause": []},
            "b": {"witness_clause": []},
            "x": {"witness_clause": ["a"]},
            "y": {"witness_clause": ["x"]},
        }
        rows = basis_sensitivity(heads, clauses, {"a", "b"}, witnesses)
        by_seed = {row["basis_atom"]: row for row in rows}
        self.assertEqual(by_seed["a"]["exact_and_or_closure_loss_count"], 0)
        self.assertEqual(by_seed["a"]["selected_witness_descendant_count"], 2)
        self.assertEqual(by_seed["a"]["witness_minus_exact_loss_count"], 2)
        self.assertTrue(by_seed["a"]["removed_basis_atom_rederived"])


if __name__ == "__main__":
    unittest.main()
