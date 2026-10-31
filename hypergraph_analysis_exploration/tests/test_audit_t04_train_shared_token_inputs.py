import unittest

from src.analysis.audit_t04_train_shared_token_inputs import summarize_shared_token_inputs


class T04TrainSharedTokenInputTests(unittest.TestCase):
    def test_equalizes_text_inventory_and_reports_structure_separately(self):
        rows = [{"candidate_ids": ["head", "head"], "label": "must not be read"}]
        nodes = {"head": "target gloss", "a": "alpha", "b": "beta"}
        rules = {"head": [["a", "b"], ["a"]]}

        report = summarize_shared_token_inputs(
            rows, nodes, rules,
            lambda text: [len(piece) for piece in text.split()],
        )

        self.assertEqual(report["candidate_occurrences"], 2)
        self.assertEqual(report["unique_candidates"], 1)
        self.assertEqual(report["valid_shared_token_candidates"], 1)
        self.assertEqual(report["shared_text_token_hashes"]["conditions_equal_for_all_valid_candidates"], 1)
        self.assertEqual(report["structure_sizes_per_candidate"]["branches"]["max"], 2)
        self.assertEqual(report["structure_sizes_per_candidate"]["pairwise_edges"]["max"], 3)
        self.assertEqual(
            report["token_piece_counts_without_special_tokens_or_truncation"][
                "longest_single_gloss_per_candidate"
            ]["max"],
            2,
        )
        self.assertNotIn("label", report)

    def test_missing_graph_data_stays_in_failure_denominator(self):
        report = summarize_shared_token_inputs(
            [{"candidate_ids": ["head", "missing"]}],
            {"head": "target gloss", "dep": "dependency"},
            {"head": [["dep"]]},
            lambda text: text.split(),
        )
        self.assertEqual(report["unique_candidates"], 2)
        self.assertEqual(report["failed_unique_candidates"], 1)
        self.assertEqual(report["failure_categories"], {"target_node_missing": 1})

    def test_rejects_empty_candidate_ids(self):
        with self.assertRaisesRegex(ValueError, "candidate IDs"):
            summarize_shared_token_inputs(
                [{"candidate_ids": [""]}], {}, {}, lambda text: text.split()
            )


if __name__ == "__main__":
    unittest.main()
