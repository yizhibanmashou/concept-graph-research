import copy
import unittest

from src.analysis.preposition_relation_records import transform_record, validate_source_record


def fixture_record():
    return {
        "schema_version": "t02-relation-v0",
        "item_id": "fixture-1",
        "target_id": "fixture-target",
        "transform_version": "fixture-transform",
        "source_version": {
            "nodes_sha256": "a" * 64,
            "rules_sha256": "b" * 64,
            "input_sha256": "c" * 64,
        },
        "source_branches": [{
            "branch_id": "branch-1",
            "premise_occurrence_ids": ["agent", "prep-to", "recipient", "prep-without", "condition"],
        }],
        "occurrences": [
            {"occurrence_id": "agent", "branch_id": "branch-1", "branch_position": 0,
             "node_id": "concept-agent", "pos": "noun", "source_locator": {"pointer": "/p/0"}},
            {"occurrence_id": "prep-to", "branch_id": "branch-1", "branch_position": 1,
             "node_id": "to-1", "pos": "prep", "source_locator": {"pointer": "/p/1"}},
            {"occurrence_id": "recipient", "branch_id": "branch-1", "branch_position": 2,
             "node_id": "concept-recipient", "pos": "noun", "source_locator": {"pointer": "/p/2"}},
            {"occurrence_id": "prep-without", "branch_id": "branch-1", "branch_position": 3,
             "node_id": "without-1", "pos": "prep", "source_locator": {"pointer": "/p/3"}},
            {"occurrence_id": "condition", "branch_id": "branch-1", "branch_position": 4,
             "node_id": "concept-condition", "pos": "noun", "source_locator": {"pointer": "/p/4"}},
        ],
    }


def supported_to_relation():
    return [{
        "relation_id": "relation-to",
        "branch_id": "branch-1",
        "source_occurrence_ids": ["prep-to"],
        "category": "direction_path",
        "predicate": "fixture-directed-relation",
        "arguments": [
            {"role": "source", "occurrence_ref": "agent"},
            {"role": "goal", "occurrence_ref": "recipient"},
        ],
        "polarity": "positive",
        "negation_scope": "unknown",
        "evidence_refs": [{"locator": "fixture-evidence-1"}],
        "status": "supported",
        "unresolved_reason": None,
    }]


class PrepositionRelationRecordTests(unittest.TestCase):
    def test_four_conditions_preserve_occurrences_and_never_guess_unmapped_preps(self):
        record = fixture_record()
        relations = supported_to_relation()
        before = copy.deepcopy(record)
        result = transform_record(record, relations)

        self.assertEqual(record, before, "transform must not mutate the input record")
        self.assertEqual(list(result["conditions"]), ["source", "prep_delete", "boundary_preserve", "typed_relation"])
        source = result["conditions"]["source"]["branches"][0]
        deleted = result["conditions"]["prep_delete"]["branches"][0]
        boundary = result["conditions"]["boundary_preserve"]["branches"][0]
        typed = result["conditions"]["typed_relation"]["branches"][0]
        self.assertEqual(source["premise_occurrence_ids"], ["agent", "prep-to", "recipient", "prep-without", "condition"])
        self.assertEqual(deleted["premise_occurrence_ids"], ["agent", "recipient", "condition"])
        self.assertEqual(deleted["removed_occurrence_ids"], ["prep-to", "prep-without"])
        self.assertEqual(boundary["premise_occurrence_ids"], source["premise_occurrence_ids"])
        self.assertEqual(typed["premise_occurrence_ids"], ["agent", "recipient", "prep-without", "condition"])
        self.assertEqual(typed["relations"][0]["source_occurrence_ids"], ["prep-to"])
        unresolved = next(row for row in typed["relations"] if row["status"] == "unresolved")
        self.assertEqual(unresolved["source_occurrence_ids"], ["prep-without"])
        self.assertIsNone(unresolved["predicate"])
        self.assertTrue(unresolved["unresolved_reason"])

    def test_branch_order_and_occurrence_identity_are_validated(self):
        record = fixture_record()
        record["source_branches"][0]["premise_occurrence_ids"][0:2] = ["prep-to", "agent"]
        with self.assertRaisesRegex(ValueError, "order must be contiguous"):
            validate_source_record(record)

    def test_empty_source_branch_is_rejected_but_deletion_can_create_one(self):
        record = fixture_record()
        record["source_branches"][0]["premise_occurrence_ids"] = []
        record["occurrences"] = []
        with self.assertRaisesRegex(ValueError, "source premises cannot be empty"):
            validate_source_record(record)

        record = fixture_record()
        record["source_branches"][0]["premise_occurrence_ids"] = ["prep-to", "prep-without"]
        record["occurrences"] = [row for row in record["occurrences"] if row["occurrence_id"] in {"prep-to", "prep-without"}]
        for position, occurrence in enumerate(record["occurrences"]):
            occurrence["branch_position"] = position
        transformed = transform_record(record)
        deleted = transformed["conditions"]["prep_delete"]["branches"][0]
        self.assertEqual(deleted["premise_occurrence_ids"], [])
        self.assertTrue(deleted["empty_after_transform"])

    def test_non_string_source_occurrence_reference_is_rejected(self):
        record = fixture_record()
        record["source_branches"][0]["premise_occurrence_ids"][0] = None
        with self.assertRaisesRegex(ValueError, "occurrence references must be non-empty strings"):
            validate_source_record(record)

    def test_supported_relation_requires_evidence_and_same_branch_arguments(self):
        record = fixture_record()
        relation = supported_to_relation()[0]
        relation["evidence_refs"] = []
        with self.assertRaisesRegex(ValueError, "needs evidence_refs"):
            transform_record(record, [relation])

    def test_unresolved_relation_cannot_assert_predicate(self):
        record = fixture_record()
        relation = {
            "relation_id": "unresolved-to", "branch_id": "branch-1",
            "source_occurrence_ids": ["prep-to"], "category": "unresolved",
            "predicate": "must-not-be-asserted", "arguments": [], "polarity": "unknown",
            "negation_scope": "unknown", "evidence_refs": [], "status": "unresolved",
            "unresolved_reason": "role-ambiguous",
        }
        with self.assertRaisesRegex(ValueError, "cannot assert a predicate"):
            transform_record(record, [relation])


if __name__ == "__main__":
    unittest.main()
