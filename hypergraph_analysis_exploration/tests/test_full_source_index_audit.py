import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.full_source_index_audit import _ensure_project_output, audit_index


class FullSourceIndexAuditTests(unittest.TestCase):
    def test_aggregates_index_without_emitting_ids_text_or_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            (bundle / "indexes").mkdir(parents=True)
            (bundle / "manifest.json").write_text(json.dumps({
                "sense_count": 2,
                "source_record_files": 3,
                "graph_sha256": "a" * 64,
                "semantic_fingerprint_sha256": "b" * 64,
            }), encoding="utf-8")
            rows = [
                {
                    "identity": "private-sense-a",
                    "pos": "n",
                    "graph_clause_count": 2,
                    "is_basis": False,
                    "canonical_replay_exact": True,
                    "source_records": [{
                        "status": "success",
                        "parts": 2,
                        "has_decomposition": True,
                        "has_argumentation": False,
                        "has_wsd": True,
                        "raw_definition": "private raw gloss",
                        "effective_definition": "private changed gloss",
                        "path": "sources/private.json",
                    }],
                    "active_clause_sources": [
                        {"clause_index": 0, "source_documents": ["sources/private.json"]},
                        {"clause_index": 1, "source_documents": ["sources/private.json"]},
                    ],
                },
                {
                    "identity": "private-sense-b",
                    "pos": "x",
                    "graph_clause_count": 1,
                    "is_basis": True,
                    "canonical_replay_exact": False,
                    "source_records": [
                        {"status": "unrecognized-status", "parts": 2},
                        {"status": "success", "parts": None},
                    ],
                    "active_clause_sources": [],
                },
            ]
            (bundle / "indexes" / "senses.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )

            report = audit_index(bundle)
            serialized = json.dumps(report)
            for private_value in ("private-sense", "private raw gloss", "private changed gloss", "sources/private.json"):
                self.assertNotIn(private_value, serialized)
            self.assertEqual(report["senses_scanned"], 2)
            self.assertEqual(report["source_records_scanned"], 3)
            self.assertEqual(report["count_checks"]["source_record_count_matches_manifest"], True)
            self.assertEqual(report["parts_vs_graph_clause_count"], {
                "equal": 1, "parts_missing_or_invalid": 1, "parts_more": 1,
            })
            self.assertEqual(report["source_records_where_raw_and_effective_definitions_differ"], 1)
            self.assertEqual(report["active_clause_source_pairs"], 2)
            self.assertEqual(report["active_clause_source_unique_pairs"], 2)
            self.assertEqual(report["active_clause_source_duplicate_pairs"], 0)
            self.assertEqual(report["active_source_records"], 1)
            self.assertEqual(report["active_clause_source_missing_records"], 0)
            self.assertEqual(report["active_source_records_parts_vs_attributed_clauses"], {"equal": 1})
            self.assertEqual(report["graph_clauses_with_source_lineage"], 2)
            self.assertEqual(report["graph_clauses_without_source_lineage"], 1)
            self.assertEqual(report["senses_with_all_graph_clauses_sourced"], 1)

    def test_counts_duplicate_clause_source_pairs_and_missing_source_lineage(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            (bundle / "indexes").mkdir(parents=True)
            (bundle / "manifest.json").write_text(json.dumps({
                "sense_count": 1,
                "source_record_files": 1,
            }), encoding="utf-8")
            row = {
                "identity": "private-sense",
                "pos": "n",
                "graph_clause_count": 1,
                "source_records": [],
                "active_clause_sources": [
                    {"clause_index": 0, "source_documents": ["missing.json", "missing.json"]}
                ],
            }
            (bundle / "indexes" / "senses.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
            report = audit_index(bundle)
            self.assertEqual(report["active_clause_source_pairs"], 2)
            self.assertEqual(report["active_clause_source_unique_pairs"], 1)
            self.assertEqual(report["active_clause_source_duplicate_pairs"], 1)
            self.assertEqual(report["active_clause_source_missing_records"], 1)
            self.assertEqual(report["graph_clauses_with_source_lineage"], 1)

    def test_rejects_report_outside_project(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "inside the project"):
                _ensure_project_output(Path(directory) / "report.json")


if __name__ == "__main__":
    unittest.main()
