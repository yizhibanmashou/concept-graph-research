import unittest

from src.analysis.t04_structure_views import build_relation_views


class T04StructureViewsTests(unittest.TestCase):
    def test_flat_dependencies_pairwise_projection_and_hyperedges(self):
        views = build_relation_views("target", [["a", "b"], ["c"]])
        self.assertEqual(views["node_ids"], ("a", "b", "c", "target"))
        self.assertEqual(views["B"]["dependencies"], ("a", "b", "c"))
        self.assertEqual(views["C"]["pairwise_edges"], (
            ("a", "b"), ("a", "target"), ("b", "target"), ("c", "target")
        ))
        self.assertEqual(views["D"]["branches"], (
            ("a", "b", "target"), ("c", "target")
        ))

    def test_branch_and_node_order_do_not_change_views(self):
        first = build_relation_views("t", [["a", "b"], ["c", "d"]])
        permuted = build_relation_views("t", [["d", "c"], ["b", "a"]])
        self.assertEqual(first, permuted)

    def test_flat_B_discards_branch_partition(self):
        first = build_relation_views("t", [["a", "b"], ["c", "d"]])
        second = build_relation_views("t", [["a", "c"], ["b", "d"]])
        self.assertEqual(first["B"], second["B"])

    def test_pairwise_C_can_match_distinct_D_hypergraphs(self):
        one_hyperedge = build_relation_views("t", [["a", "b", "c"]])
        triangle_hyperedges = build_relation_views(
            "t", [["a", "b"], ["a", "c"], ["b", "c"]]
        )
        self.assertEqual(one_hyperedge["B"], triangle_hyperedges["B"])
        self.assertEqual(one_hyperedge["C"], triangle_hyperedges["C"])
        self.assertNotEqual(one_hyperedge["D"], triangle_hyperedges["D"])

    def test_rejects_empty_source_branch(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            build_relation_views("t", [["a"], []])


if __name__ == "__main__":
    unittest.main()
