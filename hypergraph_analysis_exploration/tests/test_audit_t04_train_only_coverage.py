import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.audit_t04_train_only_coverage import audit


class T04TrainOnlyCoverageAuditTests(unittest.TestCase):
    def test_reports_mapping_and_budget_counts_without_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            train_path = root / "train.json"
            metadata_path = root / "metadata.json"
            nodes_path = root / "nodes.tsv"
            rules_path = root / "rules.jsonl"
            rows = [{
                "sample_id": "opaque-sample",
                "candidate_ids": ["a", "b"],
                "scorable_candidate_ids": ["a", "b"],
                "candidates": [
                    {"candidate_id": "a", "status": "ready"},
                    {"candidate_id": "b", "status": "ready"},
                ],
                "gold_candidate_id": "a",
                "label": 0,
                "inputs": {
                    condition: [[101, 1, 2, 102, 7, 102], [101, 1, 2, 102, 8, 102]]
                    for condition in "ABCD"
                },
            }]
            train_path.write_text(json.dumps(rows), encoding="utf-8")
            metadata_path.write_text(json.dumps({
                "joint_budget": 6,
                "target_marker_ids": {"start": 1, "end": 2},
                "counts": {"train": {
                    "gold_not_encodable": 0,
                    "gold_invalid_gold": 0,
                    "gold_no_exact_key": 0,
                    "gold_target_absent_from_graph": 0,
                    "sentence_window_truncated": 0,
                }},
            }), encoding="utf-8")
            with nodes_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=["synset_id", "definition"], delimiter="\t")
                writer.writeheader()
                writer.writerows([
                    {"synset_id": "a", "definition": "alpha"},
                    {"synset_id": "b", "definition": "beta"},
                    {"synset_id": "x", "definition": "dependency"},
                ])
            rules_path.write_text(
                '{"head":"a","clauses":[["x"]]}\n'
                '{"head":"b","clauses":[["x"]]}\n',
                encoding="utf-8",
            )

            result = audit(train_path, metadata_path, nodes_path, rules_path)

        self.assertEqual(result["scorable_gold_rows"], 1)
        self.assertEqual(result["candidate_encoding_failures"], 0)
        self.assertEqual(result["graph_candidate_coverage"], 2)
        self.assertEqual(result["A_input_context_piece_distribution"]["min"], 2)
        self.assertEqual(result["A_candidate_piece_distribution"]["min"], 1)
        self.assertEqual(result["target_marker_pair_counts"], {"(1, 1)": 1})


if __name__ == "__main__":
    unittest.main()
