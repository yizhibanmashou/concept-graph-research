import unittest

import torch

from src.analysis.t04_relation_aggregation import aggregate_relation_views


class T04RelationAggregationTests(unittest.TestCase):
    def setUp(self):
        self.vectors = {
            "head": torch.tensor([10.0, 1.0]),
            "a": torch.tensor([1.0, 0.0]),
            "b": torch.tensor([2.0, 1.0]),
            "c": torch.tensor([3.0, 2.0]),
            "d": torch.tensor([4.0, 3.0]),
        }

    def test_node_and_branch_order_do_not_change_pooled_views(self):
        left = aggregate_relation_views(
            self.vectors, "head", [["a", "b", "c"], ["a", "d"]]
        )
        right = aggregate_relation_views(
            dict(reversed(list(self.vectors.items()))), "head", [["d", "a"], ["c", "b", "a"]]
        )
        for condition in "ABCD":
            self.assertTrue(torch.equal(left[condition], right[condition]))

    def test_pairwise_projection_collision_with_single_vs_four_branches(self):
        one_branch = aggregate_relation_views(
            self.vectors, "head", [["a", "b", "c", "d"]]
        )
        four_branches = aggregate_relation_views(
            self.vectors,
            "head",
            [["a", "b", "c"], ["a", "b", "d"], ["a", "c", "d"], ["b", "c", "d"]],
        )

        self.assertEqual(one_branch["dependency_ids"], four_branches["dependency_ids"])
        self.assertEqual(one_branch["pair_ids"], four_branches["pair_ids"])
        self.assertTrue(torch.equal(one_branch["B"], four_branches["B"]))
        self.assertTrue(torch.equal(one_branch["C"], four_branches["C"]))
        self.assertFalse(torch.equal(one_branch["D"], four_branches["D"]))

    def test_b_c_d_means_collapse_distinct_equal_size_partitions(self):
        left = aggregate_relation_views(
            self.vectors, "head", [["a", "b"], ["c", "d"]],
            include_relation_items=True,
        )
        right = aggregate_relation_views(
            self.vectors, "head", [["a", "c"], ["b", "d"]],
            include_relation_items=True,
        )

        self.assertNotEqual(left["canonical_branches"], right["canonical_branches"])
        self.assertEqual(left["dependency_ids"], right["dependency_ids"])
        self.assertNotEqual(left["pair_ids"], right["pair_ids"])
        self.assertTrue(torch.equal(left["B"], right["B"]))
        self.assertTrue(torch.equal(left["C"], right["C"]))
        self.assertTrue(torch.equal(left["D"], right["D"]))
        self.assertTrue(torch.equal(left["relation_items"]["B"], right["relation_items"]["B"]))
        self.assertFalse(torch.equal(left["relation_items"]["C"], right["relation_items"]["C"]))
        self.assertFalse(torch.equal(left["relation_items"]["D"], right["relation_items"]["D"]))

    def test_outputs_have_shared_width_and_a_has_zero_relation_channel(self):
        result = aggregate_relation_views(self.vectors, "head", [["a", "b"]])
        for condition in "ABCD":
            self.assertEqual(tuple(result[condition].shape), (4,))
        self.assertTrue(torch.equal(result["A"][2:], torch.zeros(2)))

    def test_weighted_matrix_matches_direct_b_c_d_means_and_keeps_gradients(self):
        vectors = {key: value.clone().requires_grad_() for key, value in self.vectors.items()}
        branches = [["a", "b", "c"], ["a", "d"]]
        result = aggregate_relation_views(vectors, "head", branches)
        target = vectors["head"]
        b_expected = torch.stack([vectors[key] for key in ("a", "b", "c", "d")]).mean(0)
        pair_ids = result["pair_ids"]
        c_expected = torch.stack([
            (vectors[left] + vectors[right]) / 2 for left, right in pair_ids
        ]).mean(0)
        d_expected = torch.stack([
            torch.stack([target, *(vectors[key] for key in branch)]).mean(0)
            for branch in (["a", "b", "c"], ["a", "d"])
        ]).mean(0)
        self.assertTrue(torch.allclose(result["B"][2:], b_expected))
        self.assertTrue(torch.allclose(result["C"][2:], c_expected))
        self.assertTrue(torch.allclose(result["D"][2:], d_expected))
        sum(result[key].sum() for key in "ABCD").backward()
        self.assertTrue(all(value.grad is not None for value in vectors.values()))

    def test_invalid_or_missing_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            aggregate_relation_views(self.vectors, "head", [[]])
        with self.assertRaisesRegex(ValueError, "missing node"):
            aggregate_relation_views({"head": torch.ones(2)}, "head", [["a"]])


if __name__ == "__main__":
    unittest.main()
