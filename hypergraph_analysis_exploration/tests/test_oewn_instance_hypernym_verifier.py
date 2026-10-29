import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.oewn_instance_hypernym_verifier import (
    load_instance_graph,
    verify_claim_batch,
    verify_instance_claim,
)


class OewnInstanceHypernymVerifierTests(unittest.TestCase):
    def setUp(self):
        self.nodes = {
            "instance": {"pos": "n", "source_file": "noun.test.json"},
            "class": {"pos": "n", "source_file": "noun.test.json"},
            "superclass": {"pos": "n", "source_file": "noun.test.json"},
            "unrelated": {"pos": "n", "source_file": "noun.test.json"},
            "verb": {"pos": "v", "source_file": "verb.test.json"},
        }
        self.instance_parents = {"instance": ("class",), "class": (), "superclass": (), "unrelated": (), "verb": ()}
        self.class_parents = {"instance": (), "class": ("superclass",), "superclass": (), "unrelated": (), "verb": ()}

    def test_direct_and_lifted_instance_membership_use_distinct_predicates_and_rules(self):
        direct = verify_instance_claim("instance", "class", self.nodes, self.instance_parents, self.class_parents)
        self.assertEqual(direct["status"], "direct_instance_membership")
        self.assertEqual([edge["relation"] for edge in direct["proof_path"]], ["instance_hypernym"])
        self.assertEqual(direct["logical_proof"]["root_step_id"], "derive-instance-of-class")

        lifted = verify_instance_claim("instance", "superclass", self.nodes,
                                       self.instance_parents, self.class_parents)
        self.assertEqual(lifted["status"], "lifted_instance_class_membership")
        self.assertEqual([edge["relation"] for edge in lifted["proof_path"]], ["instance_hypernym", "hypernym"])
        self.assertEqual(lifted["logical_proof"]["steps"][-1]["rule_id"],
                         "oewn_instance_of_class_hypernym_lifting/1")
        self.assertEqual(lifted["logical_proof"]["steps"][-1]["atom"], {
            "predicate": "oewn_instance_of_class", "arguments": ["instance", "superclass"]
        })

    def test_resource_nonreachability_missing_self_and_cross_pos_are_scoped(self):
        self.assertEqual(verify_instance_claim("instance", "unrelated", self.nodes,
                                               self.instance_parents, self.class_parents)["status"],
                         "not_in_instance_class_closure")
        self.assertEqual(verify_instance_claim("instance", "absent", self.nodes,
                                               self.instance_parents, self.class_parents)["status"],
                         "unknown_missing_synset")
        self.assertEqual(verify_instance_claim("instance", "instance", self.nodes,
                                               self.instance_parents, self.class_parents)["status"],
                         "not_a_proper_instance_class_pair")
        self.assertEqual(verify_instance_claim("instance", "verb", self.nodes,
                                               self.instance_parents, self.class_parents)["status"],
                         "unsupported_cross_pos")

    def test_batch_rejects_duplicate_ids_and_unknown_fields(self):
        claim = {"claim_id": "q1", "instance_synset_id": "instance", "class_synset_id": "class"}
        with self.assertRaisesRegex(ValueError, "duplicate claim_id"):
            verify_claim_batch([claim, dict(claim)], self.nodes, self.instance_parents, self.class_parents)
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            verify_claim_batch([{**claim, "gold": True}], self.nodes, self.instance_parents, self.class_parents)

    def test_loader_keeps_relation_families_separate_and_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            release = Path(directory)
            (release / "noun.test.json").write_text(json.dumps({
                "instance": {"partOfSpeech": "n", "instance_hypernym": ["class"]},
                "class": {"partOfSpeech": "n", "hypernym": ["superclass"]},
                "superclass": {"partOfSpeech": "n"},
            }), encoding="utf-8")
            nodes, instance_parents, class_parents = load_instance_graph(release)
            self.assertEqual(instance_parents["instance"], ("class",))
            self.assertEqual(class_parents["instance"], ())
            self.assertEqual(class_parents["class"], ("superclass",))

            (release / "noun.test.json").write_text(json.dumps({
                "instance": {"partOfSpeech": "n", "instance_hypernym": ["missing"]},
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "instance_hypernym endpoint.*absent"):
                load_instance_graph(release)


if __name__ == "__main__":
    unittest.main()
