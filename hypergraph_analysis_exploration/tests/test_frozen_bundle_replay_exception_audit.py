import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.audit_frozen_bundle_replay_exceptions import audit_replay_exceptions


class FrozenBundleReplayExceptionAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.bundle = Path(self.temp_dir.name)
        for relative in ("reports", "indexes", "graph"):
            (self.bundle / relative).mkdir()
        manifest = {
            "semantic_fingerprint_sha256": "semantic-1",
            "canonical_replay_exact_heads": 1,
            "sense_count": 2,
            "head_count": 2,
        }
        replay = {
            "semantic_fingerprint_sha256": "semantic-1",
            "canonical_replay_exact_heads": 1,
            "heads": 2,
            "graph_slice_selection_heads": [{
                "head": "exception",
                "missing_from_canonical_replay": [["base", "extra"]],
                "extra_in_canonical_replay": [["base"]],
                "all_graph_clauses_have_direct_source_dnf_evidence": True,
                "policy": "preserve authoritative graph clause",
            }],
        }
        (self.bundle / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (self.bundle / "reports" / "source_replay.json").write_text(json.dumps(replay), encoding="utf-8")
        self._write_jsonl("indexes/senses.jsonl", [
            {"identity": "base", "canonical_replay_exact": True, "graph_clause_count": 0},
            {"identity": "exception", "canonical_replay_exact": False, "graph_clause_count": 1,
             "pos": "r"},
        ])
        self._write_jsonl("graph/hypergraph_rules.jsonl", [
            {"head": "base", "clauses": []},
            {"head": "exception", "clauses": [["base", "extra"]]},
        ])
        self._write_jsonl("graph/coverage_witnesses.jsonl", [
            {"head": "base", "is_seed": True, "proof_depth": 0, "witness_clause": []},
            {"head": "exception", "is_seed": False, "proof_depth": 1,
             "witness_clause": ["base", "extra"]},
        ])

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_jsonl(self, relative, rows):
        path = self.bundle / relative
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    def test_reports_single_declared_exception_and_selected_witness(self):
        report = audit_replay_exceptions(self.bundle)
        self.assertEqual(report["canonical_replay_exact_counts"], {"true": 1, "false": 1,
                                                                   "missing_or_invalid": 0})
        self.assertEqual(report["exception_count"], 1)
        exception = report["exceptions"][0]
        self.assertEqual(exception["selected_witness_clause"], ["base", "extra"])
        self.assertTrue(exception["all_graph_clauses_have_direct_source_dnf_evidence"])
        self.assertFalse(report["source_payloads_opened"])

    def test_rejects_fingerprint_or_exception_index_disagreement(self):
        replay_path = self.bundle / "reports" / "source_replay.json"
        replay = json.loads(replay_path.read_text(encoding="utf-8"))
        replay["semantic_fingerprint_sha256"] = "other"
        replay_path.write_text(json.dumps(replay), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            audit_replay_exceptions(self.bundle)

        replay["semantic_fingerprint_sha256"] = "semantic-1"
        replay_path.write_text(json.dumps(replay), encoding="utf-8")
        index_path = self.bundle / "indexes" / "senses.jsonl"
        rows = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines()]
        rows[1]["canonical_replay_exact"] = True
        self._write_jsonl("indexes/senses.jsonl", rows)
        with self.assertRaisesRegex(ValueError, "canonical replay exact count"):
            audit_replay_exceptions(self.bundle)


if __name__ == "__main__":
    unittest.main()
