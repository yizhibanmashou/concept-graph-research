import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.annotation_source_audit import audit_sources


class AnnotationSourceAuditTests(unittest.TestCase):
    def test_aggregates_fields_without_emitting_gloss_and_checks_source_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle"
            source = bundle / "sources" / "Synset" / "fixture" / "sense.json"
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps({
                "pipeline": "fixture-pipeline",
                "status": "success",
                "synset": {"raw_definition": "original gloss", "lemmas": ["fixture"]},
                "definition": {
                    "definition": "effective gloss",
                    "parts": [{"part_id": "p1"}],
                    "logic": {"op": "OR", "args": []},
                },
            }), encoding="utf-8")
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            (bundle / "manifest.json").write_text(json.dumps({
                "graph_version": "fixture-graph",
                "semantic_fingerprint_sha256": "f" * 64,
            }), encoding="utf-8")
            frame = root / "frame.jsonl"
            frame.write_text(json.dumps({
                "sense_id": "fixture-sense",
                "panel": "random_stratified",
                "structural_features": {"clause_count": 2},
                "source_records": [{"path": "sources/Synset/fixture/sense.json", "sha256": source_hash}],
            }) + "\n", encoding="utf-8")

            report = audit_sources(frame, bundle)
            self.assertEqual(report["source_file_hashes_verified"], 1)
            self.assertEqual(report["aggregates"]["definition_logic_operator_counts"], {"OR": 1})
            self.assertEqual(report["aggregates"]["part_count_matches_graph_clause_count"], 0)
            self.assertEqual(report["aggregates"]["raw_effective_text_differs"], 1)
            self.assertFalse(report["raw_text_emitted"])

    def test_source_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle"
            source = bundle / "sources" / "Synset" / "fixture" / "sense.json"
            source.parent.mkdir(parents=True)
            source.write_text("{}", encoding="utf-8")
            (bundle / "manifest.json").write_text("{}", encoding="utf-8")
            frame = root / "frame.jsonl"
            frame.write_text(json.dumps({
                "sense_id": "fixture-sense",
                "source_records": [{"path": "sources/Synset/fixture/sense.json", "sha256": "0" * 64}],
            }) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                audit_sources(frame, bundle)


if __name__ == "__main__":
    unittest.main()
