import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.logic.instance_relation_annotation_validator import (
    SCHEMA_VERSION,
    load_jsonl,
    main,
    validate_dataset,
    validate_record,
)


def pair_record(annotation_id="ann-a", annotator_id="a"):
    instance_gloss = "a named person"
    class_gloss = "a human being"
    instance_start, instance_end = 2, 14
    class_start, class_end = 2, 7
    return {
        "schema_version": SCHEMA_VERSION,
        "item_id": "oewn-v:instance-id->class-id",
        "annotation_id": annotation_id,
        "source": {
            "resource": "synthetic WordNet-like resource",
            "version": "fixture-v1",
            "license": "synthetic-only",
            "archive_sha256": "a" * 64,
        },
        "instance_sense": {
            "synset_id": "instance-id", "lemmas": ["Example"], "pos": "n",
            "gloss": instance_gloss,
            "gloss_sha256": hashlib.sha256(instance_gloss.encode("utf-8")).hexdigest(),
        },
        "class_sense": {
            "synset_id": "class-id", "lemmas": ["person"], "pos": "n",
            "gloss": class_gloss,
            "gloss_sha256": hashlib.sha256(class_gloss.encode("utf-8")).hexdigest(),
        },
        "relation_claim": {"predicate": "instance_of", "direction": "instance_to_class"},
        "judgments": {
            "sense_relation": {
                "label": "yes", "basis": ["gloss_only"],
                "rationale": "Synthetic fixture: both glosses describe the same category relation.",
                "evidence_spans": {
                    "instance_gloss": [{"start": instance_start, "end": instance_end}],
                    "class_gloss": [{"start": class_start, "end": class_end}],
                },
                "confidence": "medium",
            },
            "gloss_support": {
                "status": "supported", "inference_basis": ["lexical_or_paraphrastic"],
                "rationale": "Synthetic fixture: the two glosses jointly license the ordered claim.",
                "support_reasons": [],
                "evidence_spans": {
                    "instance_gloss": [{"start": instance_start, "end": instance_end}],
                    "class_gloss": [{"start": class_start, "end": class_end}],
                },
                "confidence": "medium",
            },
        },
        "annotation": {"annotator_id": annotator_id, "adjudication_status": "independent", "notes": []},
    }


class InstanceRelationAnnotationValidatorTests(unittest.TestCase):
    def test_synthetic_example_fixture_is_valid(self):
        fixture_path = Path(__file__).parent / "fixtures" / "instance_relation_annotation_0_2_synthetic.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertEqual(validate_record(fixture), [])

    def test_accepts_pair_schema_with_separate_gloss_hashes_and_span_spaces(self):
        self.assertEqual(validate_record(pair_record()), [])

    def test_detects_independent_gloss_hash_and_span_coordinate_errors(self):
        record = pair_record()
        record["class_sense"]["gloss_sha256"] = "b" * 64
        record["judgments"]["gloss_support"]["evidence_spans"]["instance_gloss"][0] = {
            "start": 0, "end": 1000
        }
        errors = " ".join(validate_record(record))
        self.assertIn("class_sense.gloss_sha256", errors)
        self.assertIn("instance_gloss[0] must satisfy", errors)

    def test_gloss_only_relation_judgment_requires_both_gloss_spans(self):
        record = pair_record()
        record["judgments"]["sense_relation"]["evidence_spans"]["class_gloss"] = []
        errors = " ".join(validate_record(record))
        self.assertIn("gloss_only sense_relation requires", errors)

    def test_each_judgment_requires_its_own_rationale(self):
        record = pair_record()
        del record["judgments"]["sense_relation"]["rationale"]
        del record["judgments"]["gloss_support"]["rationale"]
        errors = " ".join(validate_record(record))
        self.assertIn("sense_relation.rationale", errors)
        self.assertIn("gloss_support.rationale", errors)

    def test_support_labels_have_status_specific_reason_basis_and_span_rules(self):
        not_supported = pair_record()
        support = not_supported["judgments"]["gloss_support"]
        support["status"] = "not_supported"
        support["inference_basis"] = ["external_world_knowledge"]
        support["support_reasons"] = ["content_not_licensed"]
        self.assertEqual(validate_record(not_supported), [])

        missing_reason = copy.deepcopy(not_supported)
        missing_reason["judgments"]["gloss_support"]["support_reasons"] = []
        self.assertIn("requires at least one support reason",
                      " ".join(validate_record(missing_reason)))

        unassessed = pair_record()
        unassessed_support = unassessed["judgments"]["gloss_support"]
        unassessed_support.update({
            "status": "unassessed", "inference_basis": ["unassessed"],
            "support_reasons": [],
            "evidence_spans": {"instance_gloss": [], "class_gloss": []},
        })
        self.assertEqual(validate_record(unassessed), [])

        one_sided = pair_record()
        one_sided["judgments"]["gloss_support"]["evidence_spans"]["class_gloss"] = []
        self.assertIn("at least one span in each source gloss",
                      " ".join(validate_record(one_sided)))

    def test_dataset_rejects_duplicate_annotator_item_and_pair_source_drift(self):
        first = pair_record()
        duplicate = copy.deepcopy(first)
        duplicate["annotation_id"] = "ann-b"
        errors = " ".join(validate_dataset([first, duplicate]))
        self.assertIn("duplicate annotation for item_id/annotator_id", errors)

        second_annotator = copy.deepcopy(first)
        second_annotator["annotation_id"] = "ann-b"
        second_annotator["annotation"]["annotator_id"] = "b"
        second_annotator["class_sense"]["synset_id"] = "different-class"
        drift_errors = " ".join(validate_dataset([first, second_annotator]))
        self.assertIn("bound to inconsistent sense pair/source release", drift_errors)

        release_drift = copy.deepcopy(first)
        release_drift["annotation_id"] = "ann-b"
        release_drift["annotation"]["annotator_id"] = "b"
        release_drift["source"]["version"] = "fixture-v2"
        self.assertIn("bound to inconsistent sense pair/source release",
                      " ".join(validate_dataset([first, release_drift])))

    def test_dataset_allows_two_independent_annotators_for_same_pair(self):
        first = pair_record()
        second = pair_record(annotation_id="ann-b", annotator_id="b")
        self.assertEqual(validate_dataset([first, second]), [])

    def test_malformed_unhashable_enum_values_fail_closed_without_crashing(self):
        record = pair_record()
        record["instance_sense"]["pos"] = []
        record["judgments"]["sense_relation"]["label"] = {}
        record["judgments"]["sense_relation"]["basis"] = [[]]
        record["judgments"]["gloss_support"]["status"] = []
        record["judgments"]["gloss_support"]["inference_basis"] = [[]]
        record["judgments"]["gloss_support"]["support_reasons"] = [[]]
        errors = validate_record(record)
        self.assertGreaterEqual(len(errors), 6)

    def test_jsonl_cli_reports_valid_records_without_echoing_source_text(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pair_annotations.jsonl"
            path.write_text(json.dumps(pair_record(), ensure_ascii=False) + "\n", encoding="utf-8")
            records, lines, parse_errors = load_jsonl(path)
            self.assertEqual(lines, [1])
            self.assertEqual(parse_errors, [])
            self.assertEqual(validate_dataset(records, lines), [])
            self.assertEqual(main([str(path)]), 0)


if __name__ == "__main__":
    unittest.main()
