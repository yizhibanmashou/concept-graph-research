import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.selected_witness_source_lineage import audit_selected_witness_sources
from src.analysis.frozen_bundle_integrity import REQUIRED_FILES


class SelectedWitnessSourceLineageTests(unittest.TestCase):
    def _make_bundle(self, root: Path, *, link_source=True, tamper_checksum=False):
        bundle = root / "bundle"
        (bundle / "graph").mkdir(parents=True)
        (bundle / "indexes").mkdir()
        (bundle / "sources").mkdir()
        rules = [
            {"head": "seed", "clauses": []},
            {"head": "h", "clauses": [["seed"]]},
        ]
        rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
        rules_path.write_text("".join(json.dumps(row) + "\n" for row in rules), encoding="utf-8")
        (bundle / "graph" / "coverage_witnesses.jsonl").write_text("".join(
            json.dumps(row) + "\n" for row in [
                {"head": "seed", "is_seed": True, "proof_depth": 0, "witness_clause": []},
                {"head": "h", "is_seed": False, "proof_depth": 1, "witness_clause": ["seed"]},
            ]
        ), encoding="utf-8")
        (bundle / "graph" / "selected_basis_atoms.txt").write_text("seed\n", encoding="utf-8")
        source_path = bundle / "sources" / "h.json"
        raw_source = json.dumps({"synset": {"synset_id": "h"}}).encode("utf-8")
        source_path.write_bytes(raw_source)
        index_rows = [
            {"identity": "seed", "source_records": [], "active_clause_sources": []},
            {
                "identity": "h",
                "source_records": [{"path": "sources/h.json"}],
                "active_clause_sources": ([
                    {"clause_index": 0, "source_documents": ["sources/h.json"]}
                ] if link_source else []),
            },
        ]
        (bundle / "indexes" / "senses.jsonl").write_text("".join(
            json.dumps(row) + "\n" for row in index_rows
        ), encoding="utf-8")
        rules_sha = hashlib.sha256(rules_path.read_bytes()).hexdigest()
        (bundle / "manifest.json").write_text(json.dumps({"graph_sha256": rules_sha, "semantic_fingerprint_sha256": "synthetic"}), encoding="utf-8")
        source_sha = hashlib.sha256(raw_source).hexdigest()
        if tamper_checksum:
            source_sha = "0" * 64
        provenance = bundle / "provenance"
        provenance.mkdir()
        (provenance / "hypergraph_source_contract.json").write_text('{}', encoding="utf-8")
        checksum_paths = list(REQUIRED_FILES[2:]) + ["graph/selected_basis_atoms.txt"]
        checksum_rows = [{"path": name, "sha256": hashlib.sha256((bundle / name).read_bytes()).hexdigest(),
                          "bytes": (bundle / name).stat().st_size} for name in checksum_paths]
        checksum_rows.append({"path": "sources/h.json", "sha256": source_sha, "bytes": len(raw_source)})
        (bundle / "checksums.jsonl").write_text(''.join(json.dumps(row) + '\n' for row in checksum_rows), encoding="utf-8")
        lock = {"lock_version": "oewn-frozen-bundle-integrity-lock/2",
                "bundle_semantic_fingerprint_sha256": "synthetic",
                "files": {name: hashlib.sha256((bundle / name).read_bytes()).hexdigest() for name in REQUIRED_FILES}}
        self.integrity_lock = root / "synthetic_lock.json"
        self.integrity_lock.write_text(json.dumps(lock), encoding="utf-8")
        return bundle

    def test_validates_selected_clause_lineage_payload_hash_and_head_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = self._make_bundle(Path(directory))
            report = audit_selected_witness_sources(bundle, integrity_lock=self.integrity_lock)
        counts = report["counts"]
        self.assertEqual(counts["graph_head_count"], 2)
        self.assertEqual(counts["selected_rule_count"], 1)
        self.assertEqual(counts["selected_rules_with_source_links"], 1)
        self.assertEqual(counts["distinct_selected_source_payloads_verified"], 1)
        self.assertTrue(all(report["validation"].values()))
        serialized = json.dumps(report)
        for private_value in ('"seed"', "sources/h.json", '"h"'):
            self.assertNotIn(private_value, serialized)

    def test_reports_selected_witness_clause_without_source_lineage(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = self._make_bundle(Path(directory), link_source=False)
            report = audit_selected_witness_sources(bundle, integrity_lock=self.integrity_lock)
        self.assertEqual(report["counts"]["selected_rules_without_source_links"], 1)
        self.assertFalse(report["validation"]["all_selected_rules_have_source_links"])

    def test_fails_closed_when_selected_source_hash_does_not_match_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = self._make_bundle(Path(directory), tamper_checksum=True)
            with self.assertRaisesRegex(ValueError, "checksum verification"):
                audit_selected_witness_sources(bundle, integrity_lock=self.integrity_lock)


if __name__ == "__main__":
    unittest.main()
