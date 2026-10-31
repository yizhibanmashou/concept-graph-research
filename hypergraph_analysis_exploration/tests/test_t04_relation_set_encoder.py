import unittest

import torch

from src.analysis.t04_relation_aggregation import aggregate_relation_views
from src.analysis.t04_relation_set_encoder import (
    SharedRelationItemEncoder,
    encode_relation_item_views,
)


class T04RelationSetEncoderTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(19)
        self.node_vectors = {
            "head": torch.tensor([10.0, 1.0]),
            "a": torch.tensor([1.0, 0.0]),
            "b": torch.tensor([2.0, 1.0]),
            "c": torch.tensor([3.0, 2.0]),
            "d": torch.tensor([4.0, 3.0]),
        }
        self.left = aggregate_relation_views(
            self.node_vectors,
            "head",
            [["a", "b"], ["c", "d"]],
            include_relation_items=True,
        )["relation_items"]
        self.right = aggregate_relation_views(
            self.node_vectors,
            "head",
            [["a", "c"], ["b", "d"]],
            include_relation_items=True,
        )["relation_items"]
        self.encoder = SharedRelationItemEncoder(2, 4)

    def test_shared_nonlinear_encoder_separates_partition_collision(self):
        left = encode_relation_item_views(self.left, self.encoder)
        right = encode_relation_item_views(self.right, self.encoder)

        self.assertTrue(torch.equal(left["B"], right["B"]))
        self.assertFalse(torch.equal(left["C"], right["C"]))
        self.assertFalse(torch.equal(left["D"], right["D"]))
        self.assertEqual(tuple(left["D"].shape), (4,))

    def test_set_encoder_is_invariant_to_item_order(self):
        items = self.left["D"]
        forward = self.encoder(items)
        reverse = self.encoder(items.flip(0))
        torch.testing.assert_close(forward, reverse)

    def test_one_shared_parameter_set_receives_finite_gradients(self):
        encoded = encode_relation_item_views(self.left, self.encoder)
        loss = sum(value.square().sum() for value in encoded.values())
        loss.backward()

        params = list(self.encoder.parameters())
        self.assertGreater(sum(parameter.numel() for parameter in params), 0)
        self.assertTrue(all(parameter.grad is not None for parameter in params))
        self.assertTrue(all(torch.isfinite(parameter.grad).all() for parameter in params))

    def test_invalid_relation_items_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "rank-2"):
            self.encoder(torch.ones(3))
        with self.assertRaisesRegex(ValueError, "missing B/C/D"):
            encode_relation_item_views({"B": torch.ones(1, 2)}, self.encoder)


if __name__ == "__main__":
    unittest.main()
