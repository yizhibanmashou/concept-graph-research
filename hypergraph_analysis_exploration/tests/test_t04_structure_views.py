import unittest

from src.analysis.t04_structure_views import (
    build_aligned_relation_tensors,
    build_relation_views,
)


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

    def test_aligned_tensors_share_nodes_and_encode_three_distinct_views(self):
        tensors = build_aligned_relation_tensors("target", [["a", "b"], ["c"]])
        self.assertEqual(tensors["node_ids"], ("a", "b", "c", "target"))
        self.assertEqual(tensors["target_index"], 3)
        self.assertEqual(tensors["B"]["dependency_mask"], (True, True, True, False))
        self.assertEqual(tensors["C"]["adjacency_matrix"][0],
                         (False, True, False, True))
        self.assertEqual(tensors["D"]["incidence_matrix"], (
            (True, True, False, True),
            (False, False, True, True),
        ))

    def test_aligned_tensor_views_ignore_branch_and_node_order(self):
        first = build_aligned_relation_tensors("t", [["a", "b"], ["c"]])
        permuted = build_aligned_relation_tensors("t", [["c"], ["b", "a"]])
        self.assertEqual(first, permuted)

    def test_pairwise_tensor_can_erase_distinct_branch_partitions(self):
        one_branch = build_aligned_relation_tensors("t", [["a", "b", "c"]])
        split_branches = build_aligned_relation_tensors(
            "t", [["a", "b"], ["a", "c"], ["b", "c"]]
        )
        self.assertEqual(one_branch["node_ids"], split_branches["node_ids"])
        self.assertEqual(one_branch["B"], split_branches["B"])
        self.assertEqual(one_branch["C"], split_branches["C"])
        self.assertNotEqual(one_branch["D"], split_branches["D"])


if __name__ == "__main__":
    unittest.main()
