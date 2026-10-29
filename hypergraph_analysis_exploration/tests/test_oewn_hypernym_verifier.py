import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from src.analysis.oewn_hypernym_verifier import (
    audit_hypernym_acyclicity,
    load_hypernym_graph,
    verify_claim_batch,
    verify_extracted_taxonomy,
    verify_hypernym_claim,
)


class OewnHypernymVerifierTests(unittest.TestCase):
    def setUp(self):
        self.nodes = {
            "child": {"pos": "n", "source_file": "noun.test.json"},
            "middle": {"pos": "n", "source_file": "noun.test.json"},
            "ancestor": {"pos": "n", "source_file": "noun.test.json"},
            "other": {"pos": "n", "source_file": "noun.test.json"},
            "verb": {"pos": "v", "source_file": "verb.test.json"},
            "adj": {"pos": "a", "source_file": "adj.test.json"},
            "satellite": {"pos": "s", "source_file": "adj.test.json"},
        }
        self.parents = {
            "child": ("middle",),
            "middle": ("ancestor",),
            "ancestor": (),
            "other": (),
            "verb": (),
            "adj": (),
            "satellite": (),
        }

    def test_returns_direct_and_deterministic_shortest_transitive_proofs(self):
        direct = verify_hypernym_claim("child", "middle", self.nodes, self.parents)
        self.assertEqual(direct["status"], "direct_hypernym")
        self.assertEqual(len(direct["proof_path"]), 1)

        transitive = verify_hypernym_claim("child", "ancestor", self.nodes, self.parents)
        self.assertEqual(transitive["status"], "transitive_hypernym")
        self.assertEqual(transitive["proof_path"], [
            {"child_synset_id": "child", "hypernym_synset_id": "middle", "source_file": "noun.test.json"},
            {"child_synset_id": "middle", "hypernym_synset_id": "ancestor", "source_file": "noun.test.json"},
        ])

    def test_missing_reverse_and_resource_nonreachability_are_not_semantic_falsehood(self):
        missing = verify_hypernym_claim("child", "missing", self.nodes, self.parents)
        self.assertEqual(missing["status"], "unknown_missing_synset")

        reverse = verify_hypernym_claim("ancestor", "child", self.nodes, self.parents)
        self.assertEqual(reverse["status"], "not_in_hypernym_closure")
        self.assertEqual(reverse["reverse_path"][0]["child_synset_id"], "child")

        disconnected = verify_hypernym_claim("other", "child", self.nodes, self.parents)
        self.assertEqual(disconnected["status"], "not_in_hypernym_closure")
        self.assertIsNone(disconnected["reverse_path"])

    def test_self_and_cross_pos_claims_are_not_asserted_as_hypernym(self):
        self.assertEqual(
            verify_hypernym_claim("child", "child", self.nodes, self.parents)["status"],
            "not_a_proper_hypernym",
        )
        self.assertEqual(
            verify_hypernym_claim("child", "verb", self.nodes, self.parents)["status"],
            "unsupported_cross_pos",
        )

        # WordNet adjective satellites (s) belong to the adjective (a) family.
        self.assertEqual(
            verify_hypernym_claim("adj", "satellite", self.nodes, self.parents)["status"],
            "not_in_hypernym_closure",
        )

    def test_batch_rejects_duplicate_ids_and_uncontrolled_fields(self):
        claim = {"claim_id": "q1", "child_synset_id": "child", "ancestor_synset_id": "middle"}
        with self.assertRaisesRegex(ValueError, "duplicate claim_id"):
            verify_claim_batch([claim, dict(claim)], self.nodes, self.parents)
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            verify_claim_batch([{**claim, "gold": True}], self.nodes, self.parents)

    def test_graph_acyclicity_audit_reports_cycle_residual_without_claiming_exact_scc_size(self):
        acyclic = audit_hypernym_acyclicity(self.nodes, self.parents)
        self.assertTrue(acyclic["acyclic"])
        self.assertEqual(acyclic["unprocessed_node_count"], 0)

        cyclic_parents = {**self.parents, "ancestor": ("child",)}
        cyclic = audit_hypernym_acyclicity(self.nodes, cyclic_parents)
        self.assertFalse(cyclic["acyclic"])
        self.assertGreater(cyclic["unprocessed_node_count"], 0)

    def test_loader_and_archive_verification_reject_modified_or_broken_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release = root / "release"
            release.mkdir()
            records = {
                "child": {"partOfSpeech": "n", "hypernym": ["parent"]},
                "parent": {"partOfSpeech": "n", "hypernym": []},
            }
            payload = json.dumps(records, sort_keys=True).encode("utf-8")
            (release / "noun.test.json").write_bytes(payload)
            archive_path = root / "release.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("oewn/noun.test.json", payload)

            manifest = verify_extracted_taxonomy(release, archive_path)
            self.assertEqual(manifest["verified_file_count"], 1)
            nodes, parents = load_hypernym_graph(release)
            self.assertEqual(parents["child"], ("parent",))
            self.assertEqual(verify_hypernym_claim("child", "parent", nodes, parents)["status"], "direct_hypernym")

            (release / "noun.test.json").write_bytes(payload + b" ")
            with self.assertRaisesRegex(ValueError, "differs from pinned release archive"):
                verify_extracted_taxonomy(release, archive_path)

    def test_loader_fails_closed_on_missing_endpoints_and_cross_pos_edges(self):
        with tempfile.TemporaryDirectory() as directory:
            release = Path(directory)
            (release / "noun.test.json").write_text(json.dumps({
                "child": {"partOfSpeech": "n", "hypernym": ["missing"]},
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "is absent from release"):
                load_hypernym_graph(release)

            (release / "noun.test.json").write_text(json.dumps({
                "child": {"partOfSpeech": "n", "hypernym": ["verb"]},
                "verb": {"partOfSpeech": "v", "hypernym": []},
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cross-POS hypernym edge"):
                load_hypernym_graph(release)

            (release / "noun.test.json").write_text(json.dumps({
                "adjective": {"partOfSpeech": "a", "hypernym": ["satellite"]},
                "satellite": {"partOfSpeech": "s", "hypernym": []},
            }), encoding="utf-8")
            nodes, parents = load_hypernym_graph(release)
            self.assertEqual(parents["adjective"], ("satellite",))


if __name__ == "__main__":
    unittest.main()
