import unittest

from src.analysis.audit_t04_train_graph_inventory import summarize_train_inventory


class T04TrainGraphInventoryTests(unittest.TestCase):
    def test_uses_only_candidate_ids_and_reports_shared_graph_inventory(self):
        rows = [
            {"candidate_ids": ["target", "target", "missing"], "label": "must not be read"},
        ]
        report = summarize_train_inventory(
            rows,
            {"target": "target gloss", "a": "a gloss", "b": "b gloss"},
            {"target": [["a", "b"]]},
        )
        self.assertEqual(report["split"], "train_only")
        self.assertEqual(report["candidate_occurrences"], 3)
        self.assertEqual(report["unique_candidates"], 2)
        self.assertEqual(report["complete_graph_candidates"], 1)
        self.assertEqual(report["failure_categories"], {"target_node_missing": 1})
        self.assertNotIn("label", report)
        self.assertEqual(report["complete_candidate_graph_sizes"]["branches"]["median"], 1)

    def test_rejects_malformed_candidate_inventory_without_leaking_values(self):
        with self.assertRaisesRegex(ValueError, "candidate IDs"):
            summarize_train_inventory([{"candidate_ids": ["ok", ""]}], {}, {})

    def test_retains_empty_and_malformed_branch_as_failure_denominator(self):
        report = summarize_train_inventory(
            [{"candidate_ids": ["bad"]}],
            {"bad": "definition"},
            {"bad": [["a"], []]},
        )
        self.assertEqual(report["unique_candidates"], 1)
        self.assertEqual(report["failed_unique_candidates"], 1)
        self.assertEqual(report["failure_categories"], {"invalid_or_empty_branch": 1})

    def test_retains_missing_dependency_gloss_as_failure(self):
        report = summarize_train_inventory(
            [{"candidate_ids": ["head"]}],
            {"head": "definition", "dep": "   "},
            {"head": [["dep"]]},
        )
        self.assertEqual(report["failure_categories"], {"dependency_gloss_missing": 1})


if __name__ == "__main__":
    unittest.main()
