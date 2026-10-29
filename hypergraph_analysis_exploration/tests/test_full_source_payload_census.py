import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.full_source_payload_census import audit_payloads


class FullSourcePayloadCensusTests(unittest.TestCase):
    def test_reads_active_payload_and_emits_only_aggregate_structure(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            (bundle / "graph").mkdir(parents=True)
            (bundle / "indexes").mkdir()
            (bundle / "sources").mkdir()
            rule_path = bundle / "graph" / "hypergraph_rules.jsonl"
            rule_path.write_text(json.dumps({
                "head": "private-sense",
                "clauses": [["private-literal-a", "private-literal-b"]],
            }) + "\n", encoding="utf-8")
            graph_hash = hashlib.sha256(rule_path.read_bytes()).hexdigest()
            payload = {
                "definition": {
                    "definition": "private effective gloss",
                    "parts": [{"part_id": "p1"}, {"part_id": "p2"}],
                    "logic": {"op": "AND", "args": [
                        {"part_id": "p1"}, {"part_id": "p2"},
                    ]},
                },
                "synset": {"raw_definition": "private raw gloss"},
                "part_results": [
                    {"part_id": "p1", "wsd": {"sentence_synset_ids": ["private-literal-a"]}},
                    {"part_id": "p2", "wsd": {"sentence_synset_ids": ["private-literal-b"]}},
                ],
            }
            source_path = bundle / "sources" / "source.json"
            source_path.write_text(json.dumps(payload), encoding="utf-8")
            source_bytes = source_path.read_bytes()
            (bundle / "checksums.jsonl").write_text(json.dumps({
                "path": "sources/source.json",
                "bytes": len(source_bytes),
                "sha256": hashlib.sha256(source_bytes).hexdigest(),
            }) + "\n", encoding="utf-8")
            (bundle / "manifest.json").write_text(json.dumps({
                "sense_count": 1,
                "graph_sha256": graph_hash,
            }), encoding="utf-8")
            (bundle / "indexes" / "senses.jsonl").write_text(json.dumps({
                "identity": "private-sense",
                "source_records": [{"path": "sources/source.json"}],
                "active_clause_sources": [{
                    "clause_index": 0,
                    "source_documents": ["sources/source.json"],
                }],
            }) + "\n", encoding="utf-8")

            report = audit_payloads(bundle, progress_every=0)

            self.assertEqual(report["counts"]["active_source_payloads_read"], 1)
            self.assertTrue(report["counts"]["all_active_payloads_match_frozen_checksums"])
            self.assertEqual(report["counts"]["logic_trees_parsed"], 1)
            self.assertEqual(report["counts"]["logic_leaf_sets_match_parts"], 1)
            self.assertEqual(report["counts"]["branch_count_matches_attributed_clause_count"], 1)
            self.assertEqual(report["counts"]["wsd_branch_id_multisets_match_graph_literal_ids"], 1)
            self.assertEqual(report["counts"]["graph_clause_wsd_relation_exact_branch_match"], 1)
            self.assertEqual(report["counts"]["payloads_with_raw_effective_text_difference"], 1)
            serialized = json.dumps(report)
            for private in (
                "private-sense", "private-literal", "private raw gloss",
                "private effective gloss", "sources/source.json",
            ):
                self.assertNotIn(private, serialized)

            payload["part_results"] = payload["part_results"][:1]
            source_path.write_text(json.dumps(payload), encoding="utf-8")
            source_bytes = source_path.read_bytes()
            (bundle / "checksums.jsonl").write_text(json.dumps({
                "path": "sources/source.json",
                "bytes": len(source_bytes),
                "sha256": hashlib.sha256(source_bytes).hexdigest(),
            }) + "\n", encoding="utf-8")
            incomplete = audit_payloads(bundle, progress_every=0)
            self.assertEqual(incomplete["counts"]["logic_trees_with_complete_part_wsd_ids"], 0)
            self.assertNotIn("wsd_branch_id_multisets_match_graph_literal_ids", incomplete["counts"])
            self.assertNotIn("graph_clauses_subset_of_a_wsd_branch_union", incomplete["counts"])
            (bundle / "checksums.jsonl").write_text(json.dumps({
                "path": "sources/source.json",
                "bytes": len(source_bytes),
                "sha256": "0" * 64,
            }) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "does not match its frozen checksums"):
                audit_payloads(bundle, progress_every=0)

    def test_aggregates_directional_clause_to_wsd_branch_set_relations(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            (bundle / "graph").mkdir(parents=True)
            (bundle / "indexes").mkdir()
            (bundle / "sources").mkdir()
            clauses = [["alpha"], ["alpha", "extra"], ["alpha", "missing"], ["private-disjoint"]]
            rule_path = bundle / "graph" / "hypergraph_rules.jsonl"
            rule_path.write_text(json.dumps({"head": "private-sense", "clauses": clauses}) + "\n", encoding="utf-8")
            graph_hash = hashlib.sha256(rule_path.read_bytes()).hexdigest()
            payload = {
                "definition": {
                    "definition": "private gloss",
                    "parts": [{"part_id": "p1"}, {"part_id": "p2"}],
                    "logic": {"op": "OR", "args": [{"part_id": "p1"}, {"part_id": "p2"}]},
                },
                "synset": {"raw_definition": "private gloss"},
                "part_results": [
                    {"part_id": "p1", "wsd": {"sentence_synset_ids": ["alpha", "extra"]}},
                    {"part_id": "p2", "wsd": {"sentence_synset_ids": ["beta"]}},
                ],
            }
            source_path = bundle / "sources" / "source.json"
            source_path.write_text(json.dumps(payload), encoding="utf-8")
            source_bytes = source_path.read_bytes()
            (bundle / "checksums.jsonl").write_text(json.dumps({
                "path": "sources/source.json",
                "bytes": len(source_bytes),
                "sha256": hashlib.sha256(source_bytes).hexdigest(),
            }) + "\n", encoding="utf-8")
            (bundle / "manifest.json").write_text(json.dumps({"sense_count": 1, "graph_sha256": graph_hash}), encoding="utf-8")
            (bundle / "indexes" / "senses.jsonl").write_text(json.dumps({
                "identity": "private-sense",
                "source_records": [{"path": "sources/source.json"}],
                "active_clause_sources": [
                    {"clause_index": index, "source_documents": ["sources/source.json"]}
                    for index in range(len(clauses))
                ],
            }) + "\n", encoding="utf-8")

            report = audit_payloads(bundle, progress_every=0)
            counts = report["counts"]
            self.assertEqual(counts["graph_clause_wsd_relation_proper_subset_of_branch"], 1)
            self.assertEqual(counts["graph_clause_wsd_relation_exact_branch_match"], 1)
            self.assertEqual(counts["graph_clause_wsd_relation_partial_overlap_only"], 1)
            self.assertEqual(counts["graph_clause_wsd_relation_disjoint_from_all_branches"], 1)
            self.assertEqual(counts.get("graph_clause_wsd_comparison_skipped_incomplete", 0), 0)
            self.assertNotIn("private-disjoint", json.dumps(report))

    def test_rejects_unsafe_source_path(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            (bundle / "graph").mkdir(parents=True)
            (bundle / "indexes").mkdir()
            rule_path = bundle / "graph" / "hypergraph_rules.jsonl"
            rule_path.write_text(json.dumps({"head": "s", "clauses": [["x"]]}) + "\n", encoding="utf-8")
            (bundle / "manifest.json").write_text(json.dumps({
                "sense_count": 1,
                "graph_sha256": hashlib.sha256(rule_path.read_bytes()).hexdigest(),
            }), encoding="utf-8")
            (bundle / "checksums.jsonl").write_text("", encoding="utf-8")
            (bundle / "indexes" / "senses.jsonl").write_text(json.dumps({
                "identity": "s",
                "source_records": [{"path": "../escape.json"}],
                "active_clause_sources": [{"clause_index": 0, "source_documents": ["../escape.json"]}],
            }) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsafe relative path"):
                audit_payloads(bundle, progress_every=0)


if __name__ == "__main__":
    unittest.main()
