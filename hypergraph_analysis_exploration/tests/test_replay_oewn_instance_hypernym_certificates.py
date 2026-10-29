from copy import deepcopy
import json
import tempfile
import unittest
from pathlib import Path
import zipfile

from src.analysis.oewn_instance_hypernym_verifier import verify_claim_batch
from src.analysis.replay_oewn_instance_hypernym_certificates import (
    _load_graph_independently,
    _verify_archive_bytes_independently,
    verify_report,
)


class OewnInstanceHypernymCertificateReplayTests(unittest.TestCase):
    def setUp(self):
        self.nodes = {
            "instance": {"pos": "n", "source_file": "noun.test.json"},
            "class": {"pos": "n", "source_file": "noun.test.json"},
            "superclass": {"pos": "n", "source_file": "noun.test.json"},
            "unrelated": {"pos": "n", "source_file": "noun.test.json"},
        }
        self.instance_parents = {"instance": ("class",), "class": (), "superclass": (), "unrelated": ()}
        self.class_parents = {"instance": (), "class": ("superclass",), "superclass": (), "unrelated": ()}
        self.claims = [
            {"claim_id": "direct", "instance_synset_id": "instance", "class_synset_id": "class"},
            {"claim_id": "lifted", "instance_synset_id": "instance", "class_synset_id": "superclass"},
            {"claim_id": "negative", "instance_synset_id": "instance", "class_synset_id": "unrelated"},
        ]
        self.manifest = {"release_name": "fixture", "archive_sha256": "a" * 64}
        self.claims_hash = "b" * 64
        batch = verify_claim_batch(self.claims, self.nodes, self.instance_parents, self.class_parents)
        self.report = {
            "verifier_version": "oewn-instance-hypernym-verifier/1",
            "inputs": {
                **self.manifest,
                "claims_sha256": self.claims_hash,
                "synset_count": len(self.nodes),
                "direct_instance_hypernym_edge_count": 1,
                "direct_class_hypernym_edge_count": 1,
            },
            **batch,
        }

    def replay(self, report=None, claims=None):
        return verify_report(
            self.report if report is None else report,
            self.claims if claims is None else claims,
            self.manifest,
            self.nodes,
            self.instance_parents,
            self.class_parents,
            self.claims_hash,
        )

    def test_valid_direct_lifted_and_nonreachability_results_replay(self):
        result = self.replay()
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["replayed_positive_certificates"], 2)
        self.assertEqual(result["status_counts"], {
            "direct_instance_membership": 1,
            "lifted_instance_class_membership": 1,
            "not_in_instance_class_closure": 1,
        })

    def test_rejects_path_relation_endpoint_source_and_rule_tampering(self):
        mutations = [
            lambda r: r["results"][1]["proof_path"][1].update(relation="instance_hypernym"),
            lambda r: r["results"][1]["proof_path"][1].update(parent_synset_id="unrelated"),
            lambda r: r["results"][1]["proof_path"][1].update(source_file="wrong.json"),
            lambda r: r["results"][1]["logical_proof"]["rules"][1]["body"].clear(),
            lambda r: r["results"][1]["logical_proof"]["steps"][-1].update(premises=["fact-instance-0"]),
        ]
        for mutate in mutations:
            altered = deepcopy(self.report)
            mutate(altered)
            replay = self.replay(altered)
            self.assertFalse(replay["valid"])
            self.assertTrue(replay["errors"])

    def test_rejects_fingerprint_status_and_false_nonreachability_tampering(self):
        altered_hash = deepcopy(self.report)
        altered_hash["inputs"]["claims_sha256"] = "c" * 64
        self.assertFalse(self.replay(altered_hash)["valid"])

        altered_counts = deepcopy(self.report)
        altered_counts["status_counts"]["not_in_instance_class_closure"] = 0
        self.assertFalse(self.replay(altered_counts)["valid"])

        false_negative = deepcopy(self.report)
        changed_claims = deepcopy(self.claims)
        changed_claims[2]["class_synset_id"] = "superclass"
        false_negative["results"][2]["class_synset_id"] = "superclass"
        result = self.replay(false_negative, changed_claims)
        self.assertFalse(result["valid"])
        self.assertTrue(any("claims non-reachability" in error for error in result["errors"]))

    def test_replay_graph_loader_independently_reads_and_checks_relation_families(self):
        with tempfile.TemporaryDirectory() as directory:
            release = Path(directory)
            records = {
                "instance": {"partOfSpeech": "n", "instance_hypernym": ["class"]},
                "class": {"partOfSpeech": "n", "hypernym": ["superclass"]},
                "superclass": {"partOfSpeech": "n"},
            }
            (release / "noun.test.json").write_text(json.dumps(records), encoding="utf-8")
            nodes, instance_parents, class_parents = _load_graph_independently(release)
            self.assertEqual(instance_parents["instance"], ("class",))
            self.assertEqual(class_parents["instance"], ())
            self.assertEqual(class_parents["class"], ("superclass",))

            (release / "noun.test.json").write_text(json.dumps({
                "instance": {"partOfSpeech": "n", "instance_hypernym": ["missing"]},
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "instance_hypernym endpoint.*absent"):
                _load_graph_independently(release)

    def test_replay_archive_manifest_is_independent_and_detects_changed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release = root / "release"
            release.mkdir()
            payload = json.dumps({"n1": {"partOfSpeech": "n"}}).encode("utf-8")
            extracted = release / "noun.test.json"
            extracted.write_bytes(payload)
            archive_path = root / "release.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("oewn/noun.test.json", payload)
            manifest = _verify_archive_bytes_independently(release, archive_path)
            self.assertEqual(manifest["verified_file_count"], 1)
            extracted.write_bytes(payload + b" ")
            with self.assertRaisesRegex(ValueError, "differs from pinned release archive"):
                _verify_archive_bytes_independently(release, archive_path)


if __name__ == "__main__":
    unittest.main()
