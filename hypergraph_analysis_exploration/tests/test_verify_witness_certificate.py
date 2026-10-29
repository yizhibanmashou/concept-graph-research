import copy
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.verify_witness_certificate import (
    CLAIM_TYPE,
    verify_witness_certificate,
)


class VerifyWitnessCertificateTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.bundle = Path(self.temp_dir.name) / "bundle"
        (self.bundle / "graph").mkdir(parents=True)
        (self.bundle / "indexes").mkdir()
        (self.bundle / "manifest.json").write_text(
            json.dumps({"semantic_fingerprint_sha256": "fingerprint-1"}), encoding="utf-8")
        self._write_jsonl("graph/hypergraph_rules.jsonl", [
            {"head": "a", "clauses": []},
            {"head": "b", "clauses": []},
            {"head": "h", "clauses": [["a", "b"], ["b"]]},
            {"head": "z", "clauses": [["h"]]},
        ])
        self._write_jsonl("graph/coverage_witnesses.jsonl", [
            {"head": "a", "is_seed": True, "proof_depth": 0, "witness_clause": []},
            {"head": "b", "is_seed": True, "proof_depth": 0, "witness_clause": []},
            {"head": "h", "is_seed": False, "proof_depth": 1, "witness_clause": ["a", "b"]},
            {"head": "z", "is_seed": False, "proof_depth": 2, "witness_clause": ["h"]},
        ])
        self._write_jsonl("indexes/senses.jsonl", [
            {"identity": "h", "active_clause_sources": [
                {"clause_index": 0, "source_documents": ["src/h.json"]},
                {"clause_index": 1, "source_documents": ["src/h-alt.json"]},
            ]},
            {"identity": "z", "active_clause_sources": [
                {"clause_index": 0, "source_documents": ["src/z.json"]},
            ]},
        ])
        self.certificate = {
            "claim_type": CLAIM_TYPE,
            "graph_semantic_fingerprint_sha256": "fingerprint-1",
            "target": "z",
            "node_count": 4,
            "edge_count": 3,
            "topological_order": ["a", "b", "h", "z"],
            "nodes": [
                {"id": "a", "proof_depth": 0, "is_seed": True,
                 "witness_clause_index": None, "witness_clause": [], "source_documents": []},
                {"id": "b", "proof_depth": 0, "is_seed": True,
                 "witness_clause_index": None, "witness_clause": [], "source_documents": []},
                {"id": "h", "proof_depth": 1, "is_seed": False,
                 "witness_clause_index": 0, "witness_clause": ["a", "b"],
                 "source_documents": ["src/h.json"]},
                {"id": "z", "proof_depth": 2, "is_seed": False,
                 "witness_clause_index": 0, "witness_clause": ["h"],
                 "source_documents": ["src/z.json"]},
            ],
            "edges": [
                {"from": "a", "to": "h"},
                {"from": "b", "to": "h"},
                {"from": "h", "to": "z"},
            ],
        }
        self._finalize_integrity()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_jsonl(self, relative, rows):
        path = self.bundle / relative
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    def _finalize_integrity(self):
        """Write provenance/checksums and a lock matching this synthetic bundle."""
        import hashlib

        bundle = self.bundle
        (bundle / "provenance").mkdir(exist_ok=True)
        contract = bundle / "provenance" / "hypergraph_source_contract.json"
        if not contract.exists():
            contract.write_text(json.dumps({"contract_version": "test"}), encoding="utf-8")
        manifest_path = bundle / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["graph_sha256"] = hashlib.sha256(
            (bundle / "graph/hypergraph_rules.jsonl").read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        checksum_targets = [
            "graph/hypergraph_rules.jsonl",
            "graph/coverage_witnesses.jsonl",
            "indexes/senses.jsonl",
            "provenance/hypergraph_source_contract.json",
        ]
        checksum_rows = [
            {"path": rel,
             "sha256": hashlib.sha256((bundle / rel).read_bytes()).hexdigest()}
            for rel in checksum_targets
        ]
        (bundle / "checksums.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in checksum_rows), encoding="utf-8")
        all_required = [
            "manifest.json", "checksums.jsonl",
            "graph/hypergraph_rules.jsonl", "graph/coverage_witnesses.jsonl",
            "indexes/senses.jsonl", "provenance/hypergraph_source_contract.json",
        ]
        lock = {
            "lock_version": "oewn-frozen-bundle-integrity-lock/2",
            "bundle_semantic_fingerprint_sha256":
                manifest.get("semantic_fingerprint_sha256"),
            "files": {
                rel: hashlib.sha256((bundle / rel).read_bytes()).hexdigest()
                for rel in all_required
            },
        }
        self.integrity_lock = bundle.parent / "test_integrity_lock.json"
        self.integrity_lock.write_text(json.dumps(lock), encoding="utf-8")

    def test_accepts_exact_source_linked_witness_dag(self):
        result = verify_witness_certificate(self.certificate, self.bundle, self.integrity_lock)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["node_count"], 4)
        self.assertEqual(result["edge_count"], 3)

    def test_rejects_tampering_across_graph_structure_and_provenance(self):
        mutations = {
            "fingerprint": lambda cert: cert.update(graph_semantic_fingerprint_sha256="wrong"),
            "selected_clause": lambda cert: cert["nodes"][2].update(witness_clause=["b"]),
            "source_reference": lambda cert: cert["nodes"][2].update(source_documents=["other.json"]),
            "edge": lambda cert: cert["edges"].pop(),
            "depth": lambda cert: cert["nodes"][3].update(proof_depth=9),
            "topological_order": lambda cert: cert.update(topological_order=["h", "a", "b", "z"]),
            "unreachable_node": lambda cert: cert["nodes"].append(copy.deepcopy(cert["nodes"][0])),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                tampered = copy.deepcopy(self.certificate)
                mutate(tampered)
                self.assertFalse(verify_witness_certificate(tampered, self.bundle, self.integrity_lock)["valid"])

    def test_rejects_certificate_from_different_bundle_version(self):
        (self.bundle / "manifest.json").write_text(
            json.dumps({"semantic_fingerprint_sha256": "fingerprint-2"}), encoding="utf-8")
        # Rebuild the matching lock/checksums for fingerprint-2 so integrity
        # passes and the certificate fingerprint mismatch is what is reported.
        self._finalize_integrity()
        result = verify_witness_certificate(
            self.certificate, self.bundle, self.integrity_lock)
        self.assertFalse(result["valid"])
        self.assertIn("certificate graph fingerprint does not match the bundle", result["errors"])


if __name__ == "__main__":
    unittest.main()
