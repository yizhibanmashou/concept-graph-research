import unittest

from src.analysis.oewn_hypernym_verifier import verify_claim_batch
from src.analysis.verify_oewn_hypernym_certificates import verify_report


class OewnHypernymCertificateReplayTests(unittest.TestCase):
    def setUp(self):
        self.nodes = {
            "child": {"pos": "n", "source_file": "noun.test.json"},
            "middle": {"pos": "n", "source_file": "noun.test.json"},
            "ancestor": {"pos": "n", "source_file": "noun.test.json"},
            "other": {"pos": "n", "source_file": "noun.test.json"},
            "descendant": {"pos": "n", "source_file": "noun.test.json"},
        }
        self.parents = {
            "child": ("middle", "ancestor"),
            "middle": ("ancestor",),
            "ancestor": (),
            "other": (),
            "descendant": ("child",),
        }
        self.claims = [
            {"claim_id": "direct", "child_synset_id": "child", "ancestor_synset_id": "middle"},
            {"claim_id": "transitive", "child_synset_id": "descendant", "ancestor_synset_id": "ancestor"},
            {"claim_id": "unreachable", "child_synset_id": "other", "ancestor_synset_id": "child"},
        ]
        self.manifest = {
            "release_name": "Open English WordNet 2025 Plus",
            "release_date": "2025-12-31",
            "archive_sha256": "a" * 64,
            "verified_file_count": 1,
            "verified_file_set_sha256": "b" * 64,
        }

    def make_report(self):
        batch = verify_claim_batch(self.claims, self.nodes, self.parents)
        return {
            "verifier_version": "oewn-hypernym-closure-verifier/2",
            "inputs": {
                **self.manifest,
                "claims_sha256": "c" * 64,
                "synset_count": len(self.nodes),
                "direct_hypernym_edge_count": sum(map(len, self.parents.values())),
            },
            "claim_count": batch["claim_count"],
            "status_counts": batch["status_counts"],
            "taxonomy_graph_audit": {"acyclic": True, "unprocessed_node_count": 0},
            "results": batch["results"],
        }

    def replay(self, report):
        return verify_report(report, self.claims, self.manifest, self.nodes, self.parents, "c" * 64)

    def test_accepts_replayed_direct_transitive_and_resource_negative_results(self):
        result = self.replay(self.make_report())
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["replayed_positive_paths"], 2)

    def test_rejects_tampered_edge_endpoints_and_source_file(self):
        report = self.make_report()
        report["results"][0]["proof_path"][0]["hypernym_synset_id"] = "other"
        report["results"][1]["proof_path"][0]["source_file"] = "noun.wrong.json"
        result = self.replay(report)
        self.assertFalse(result["valid"])
        errors = " ".join(result["errors"])
        self.assertIn("not a direct hypernym edge", errors)
        self.assertIn("source_file does not match", errors)

    def test_rejects_tampered_horn_rule_premises_and_nonpositive_proof_material(self):
        report = self.make_report()
        transitive = report["results"][1]
        application = next(step for step in transitive["logical_proof"]["steps"]
                           if step["kind"] == "rule_application")
        application["premises"] = ["fact-0", "fact-0"]
        report["results"][2]["logical_proof"] = {"forged": True}
        result = self.replay(report)
        errors = " ".join(result["errors"])
        self.assertIn("proof steps do not exactly follow", errors)
        self.assertIn("negative result must not contain positive proof material", errors)

    def test_rejects_non_shortest_but_valid_path(self):
        report = self.make_report()
        transitive = report["results"][1]
        transitive["proof_path"] = [
            {"child_synset_id": "descendant", "hypernym_synset_id": "child", "source_file": "noun.test.json"},
            {"child_synset_id": "child", "hypernym_synset_id": "middle", "source_file": "noun.test.json"},
            {"child_synset_id": "middle", "hypernym_synset_id": "ancestor", "source_file": "noun.test.json"},
        ]
        result = self.replay(report)
        self.assertFalse(result["valid"])
        self.assertIn("proof_path is not shortest", " ".join(result["errors"]))

    def test_rejects_false_resource_nonreachability_and_fingerprint_mismatch(self):
        report = self.make_report()
        false_negative_claims = [dict(claim) for claim in self.claims]
        false_negative_claims[2]["child_synset_id"] = "child"
        false_negative_claims[2]["ancestor_synset_id"] = "ancestor"
        false_negative_claims[2]["claim_id"] = "unreachable"
        report["results"][2]["child_synset_id"] = "child"
        report["results"][2]["ancestor_synset_id"] = "ancestor"
        result = verify_report(report, false_negative_claims, self.manifest, self.nodes, self.parents, "c" * 64)
        self.assertFalse(result["valid"])
        self.assertIn("claims non-reachability but a path exists", " ".join(result["errors"]))

        report = self.make_report()
        report["inputs"]["archive_sha256"] = "d" * 64
        self.assertIn("does not match the verified OEWN release", " ".join(self.replay(report)["errors"]))

    def test_rejects_mismatched_claim_file_and_status_aggregate(self):
        report = self.make_report()
        report["status_counts"] = {"direct_hypernym": 3}
        result = verify_report(report, self.claims, self.manifest, self.nodes, self.parents, "d" * 64)
        errors = " ".join(result["errors"])
        self.assertIn("claims_sha256", errors)
        self.assertIn("status_counts", errors)

    def test_rejects_tampered_graph_acyclicity_summary(self):
        report = self.make_report()
        report["taxonomy_graph_audit"]["acyclic"] = False
        self.assertIn("taxonomy_graph_audit", " ".join(self.replay(report)["errors"]))


if __name__ == "__main__":
    unittest.main()
