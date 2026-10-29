import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.source_clause_alignment_audit import _dnf_part_branches, audit_alignment


class SourceClauseAlignmentAuditTests(unittest.TestCase):
    def test_links_active_source_logic_and_wsd_sets_without_emitting_private_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle"
            (bundle / "graph").mkdir(parents=True)
            (bundle / "indexes").mkdir()
            source_relative = "sources/demo.json"
            source_path = bundle / source_relative
            source_path.parent.mkdir()
            source = {
                "definition": {
                    "parts": [{"part_id": "private-part-1"}, {"part_id": "private-part-2"}],
                    "logic": {"op": "AND", "args": [
                        {"op": "ATOM", "part_id": "private-part-1"},
                        {"op": "ATOM", "part_id": "private-part-2"},
                    ]},
                },
                "part_results": [
                    {"part_id": "private-part-1", "wsd": {"sentence_synset_ids": ["private-lit-1"]}},
                    {"part_id": "private-part-2", "wsd": {"sentence_synset_ids": ["private-lit-2"]}},
                ],
                "synset": {"raw_definition": "private gloss"},
            }
            source_bytes = json.dumps(source).encode("utf-8")
            source_path.write_bytes(source_bytes)
            rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
            rules_path.write_text(json.dumps({
                "head": "private-sense",
                "clauses": [["private-lit-1", "private-lit-2"]],
            }) + "\n", encoding="utf-8")
            rules_hash = hashlib.sha256(rules_path.read_bytes()).hexdigest()
            (bundle / "manifest.json").write_text(json.dumps({
                "graph_sha256": rules_hash,
                "semantic_fingerprint_sha256": "f" * 64,
            }), encoding="utf-8")
            (bundle / "indexes" / "senses.jsonl").write_text(json.dumps({
                "identity": "private-sense",
                "active_clause_sources": [{"clause_index": 0, "source_documents": [source_relative]}],
            }) + "\n", encoding="utf-8")
            frame_path = root / "frame.jsonl"
            frame_path.write_text(json.dumps({
                "sense_id": "private-sense",
                "panel": "random_stratified",
                "source_records": [{
                    "path": source_relative,
                    "sha256": hashlib.sha256(source_bytes).hexdigest(),
                }],
            }) + "\n", encoding="utf-8")

            report = audit_alignment(frame_path, bundle)
            serialized = json.dumps(report)
            for private_value in ("private-sense", "private gloss", "private-part", "private-lit", source_relative):
                self.assertNotIn(private_value, serialized)
            self.assertEqual(report["aggregates"]["source_records_hash_verified"], 1)
            self.assertEqual(report["aggregates"]["logic_leaf_ids_match_part_ids"], 1)
            self.assertEqual(report["aggregates"]["logic_branch_count_matches_attributed_clause_count"], 1)
            self.assertEqual(report["aggregates"]["mapped_wsd_branch_sets_exactly_match_attributed_graph_clauses"], 1)

    def test_dnf_parser_rejects_unsupported_or_explosive_structures(self):
        self.assertIsNone(_dnf_part_branches({"op": "NOT", "args": []}))
        node = {"op": "OR", "args": [
            {"part_id": "a"}, {"part_id": "b"}, {"part_id": "c"},
        ]}
        self.assertEqual(len(_dnf_part_branches(node)), 3)
        explosive = {"op": "AND", "args": [
            {"op": "OR", "args": [{"part_id": f"p{n}"} for n in range(22)]}
            for _ in range(4)
        ]}
        self.assertIsNone(_dnf_part_branches(explosive))

    def test_selected_source_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle"
            (bundle / "graph").mkdir(parents=True)
            (bundle / "indexes").mkdir()
            source = bundle / "source.json"
            source.write_text("{}", encoding="utf-8")
            rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
            rules_path.write_text(json.dumps({"head": "sense", "clauses": [["x"]]}) + "\n", encoding="utf-8")
            (bundle / "manifest.json").write_text(json.dumps({
                "graph_sha256": hashlib.sha256(rules_path.read_bytes()).hexdigest(),
            }), encoding="utf-8")
            (bundle / "indexes" / "senses.jsonl").write_text(json.dumps({
                "identity": "sense",
                "active_clause_sources": [{"clause_index": 0, "source_documents": ["source.json"]}],
            }) + "\n", encoding="utf-8")
            frame = root / "frame.jsonl"
            frame.write_text(json.dumps({
                "sense_id": "sense",
                "source_records": [{"path": "source.json", "sha256": "0" * 64}],
            }) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash"):
                audit_alignment(frame, bundle)


if __name__ == "__main__":
    unittest.main()
