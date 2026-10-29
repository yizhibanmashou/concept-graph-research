import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.logic.annotation_validator import load_jsonl, main, validate_dataset, validate_record


def toy_record(annotation_id="oewn:v1:test.n.01:ann-a:pass1", split="train"):
    return {
        "schema_version": "0.2-draft",
        "item_id": "oewn:v1:test.n.01",
        "annotation_id": annotation_id,
        "source": {
            "resource": "Open English WordNet",
            "version": "v1",
            "record_id": "test.n.01",
            "input_sha256": hashlib.sha256("a sample gloss".encode("utf-8")).hexdigest(),
            "license": "to-be-verified",
        },
        "sense": {
            "synset_id": "test.n.01",
            "lemmas": ["test"],
            "pos": "n",
            "gloss": "a sample gloss",
        },
        "analysis": {
            "status": "annotated",
            "nodes": [
                {"id": "n1", "kind": "atom", "predicate": "SAMPLE", "arguments": [{"kind": "variable", "id": "?x"}], "span": {"start": 2, "end": 14}},
                {"id": "n2", "kind": "atom", "predicate": "TEST", "arguments": [{"kind": "variable", "id": "?x"}], "span": {"start": 2, "end": 14}},
                {"id": "n3", "kind": "and", "children": ["n1", "n2"], "span": {"start": 0, "end": 14}},
            ],
            "root_node_ids": ["n3"],
            "rule_claims": [
                {"id": "claim-1", "relation": "necessary", "direction": "target_to_gloss", "formula_node_id": "n3", "evidence_spans": [{"start": 0, "end": 14}], "confidence": "medium", "semantic_support": "supported"}
            ],
            "horn_projection": {"status": "projectable", "rule_ids": ["rule-1"], "omissions": []},
        },
        "annotation": {"annotator_id": "ann-a", "adjudication_status": "independent", "notes": []},
        "split": split,
    }


class AnnotationValidatorTests(unittest.TestCase):
    def test_valid_record_passes(self):
        self.assertEqual(validate_record(toy_record()), [])

    def test_gloss_tampering_is_detected_by_source_hash(self):
        record = toy_record()
        record["sense"]["gloss"] = "a changed sample gloss"
        self.assertIn("source.input_sha256 does not match", " ".join(validate_record(record)))

    def test_explicit_underspecified_abstention_can_omit_an_ast(self):
        record = toy_record()
        record["analysis"] = {
            "status": "underspecified",
            "nodes": [],
            "root_node_ids": [],
            "rule_claims": [],
            "horn_projection": {"status": "unsupported", "rule_ids": [], "omissions": ["no stable parse"]},
        }
        self.assertEqual(validate_record(record), [])

    def test_annotated_record_still_requires_a_root(self):
        record = toy_record()
        record["analysis"]["root_node_ids"] = []
        self.assertIn("root_node_ids must not be empty", " ".join(validate_record(record)))

    def test_malformed_enum_values_do_not_crash_validator(self):
        record = toy_record()
        record["sense"]["pos"] = []
        record["analysis"]["nodes"][0]["kind"] = []
        record["analysis"]["rule_claims"][0]["relation"] = {}
        self.assertTrue(validate_record(record))

    def test_unicode_codepoint_offsets_are_checked(self):
        record = toy_record()
        record["sense"]["gloss"] = "猫"
        self.assertIn("analysis.nodes[0].span", " ".join(validate_record(record)))

    def test_dangling_ast_reference_is_rejected(self):
        record = toy_record()
        record["analysis"]["nodes"][2]["children"].append("missing")
        self.assertIn("missing child missing", " ".join(validate_record(record)))

    def test_ast_cycle_is_rejected(self):
        record = toy_record()
        record["analysis"]["nodes"][2]["children"] = ["n1", "n2"]
        record["analysis"]["nodes"][0] = {"id": "n1", "kind": "not", "child": "n3", "span": {"start": 2, "end": 14}}
        self.assertIn("AST contains a cycle", " ".join(validate_record(record)))

    def test_quantifier_binds_variable_lexically_in_its_child(self):
        record = toy_record()
        record["analysis"]["nodes"][0]["arguments"][0]["id"] = "?y"
        record["analysis"]["nodes"].append({
            "id": "n4", "kind": "forall", "binder": {"kind": "variable", "id": "?y"},
            "child": "n1", "span": {"start": 2, "end": 14},
        })
        record["analysis"]["root_node_ids"] = ["n4"]
        record["analysis"]["rule_claims"][0]["formula_node_id"] = "n4"
        self.assertEqual(validate_record(record), [])

    def test_variable_and_binder_ids_must_use_question_mark_prefix(self):
        record = toy_record()
        record["analysis"]["nodes"][0]["arguments"][0]["id"] = "x"
        record["analysis"]["nodes"].append({
            "id": "n4", "kind": "exists", "binder": {"kind": "variable", "id": "y"},
            "child": "n1", "span": {"start": 2, "end": 14},
        })
        record["analysis"]["root_node_ids"] = ["n4"]
        errors = " ".join(validate_record(record))
        self.assertIn("variable ID like '?x'", errors)
        self.assertIn("binder.id must be a variable ID", errors)

    def test_nested_quantifiers_must_alpha_rename_shadowed_binders(self):
        record = toy_record()
        record["analysis"]["nodes"].extend([
            {"id": "n4", "kind": "exists", "binder": {"kind": "variable", "id": "?x"},
             "child": "n1", "span": {"start": 2, "end": 14}},
            {"id": "n5", "kind": "forall", "binder": {"kind": "variable", "id": "?x"},
             "child": "n4", "span": {"start": 2, "end": 14}},
        ])
        record["analysis"]["root_node_ids"] = ["n5"]
        errors = " ".join(validate_record(record))
        self.assertIn("shadows an enclosing binder '?x'", errors)

    def test_shared_ast_node_cannot_change_meaning_across_quantifier_scopes(self):
        record = toy_record()
        record["analysis"]["nodes"].extend([
            {"id": "n4", "kind": "exists", "binder": {"kind": "variable", "id": "?x"},
             "child": "n1", "span": {"start": 2, "end": 14}},
            {"id": "n5", "kind": "and", "children": ["n4", "n1"],
             "span": {"start": 0, "end": 14}},
        ])
        record["analysis"]["root_node_ids"] = ["n5"]
        errors = " ".join(validate_record(record))
        self.assertIn("shared under different quantifier scopes", errors)

    def test_rule_claim_must_link_evidence_and_formula(self):
        record = toy_record()
        claim = record["analysis"]["rule_claims"][0]
        claim["formula_node_id"] = "missing"
        claim["evidence_spans"] = []
        errors = " ".join(validate_record(record))
        self.assertIn("formula_node_id", errors)
        self.assertIn("evidence_spans", errors)

    def test_rule_claim_requires_semantic_support_adjudication(self):
        record = toy_record()
        del record["analysis"]["rule_claims"][0]["semantic_support"]
        self.assertIn("semantic_support", " ".join(validate_record(record)))

    def test_optional_nli_hypothesis_hash_must_match_claim_text(self):
        record = toy_record()
        claim = record["analysis"]["rule_claims"][0]
        claim["nli_hypothesis"] = "The concept is a sample and is a test."
        claim["nli_hypothesis_sha256"] = hashlib.sha256(b"wrong text").hexdigest()
        self.assertIn("nli_hypothesis_sha256 does not match", " ".join(validate_record(record)))

    def test_split_leakage_by_lemma_is_rejected(self):
        first = toy_record("annotation-1", "train")
        second = copy.deepcopy(first)
        second["annotation_id"] = "annotation-2"
        second["sense"]["synset_id"] = "another-synset"
        second["split"] = "test"
        errors = " ".join(validate_dataset([first, second]))
        self.assertIn("lemma 'test' appears in both train and test", errors)

    def test_split_errors_keep_original_jsonl_line_numbers(self):
        first = toy_record("annotation-1", "train")
        second = copy.deepcopy(first)
        second["annotation_id"] = "annotation-2"
        second["split"] = "test"
        errors = " ".join(validate_dataset([first, second], [2, 7]))
        self.assertIn("line 7:", errors)

    def test_jsonl_cli_accepts_valid_record_and_preserves_line_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "annotations.jsonl"
            path.write_text("\n{bad json}\n" + json.dumps(toy_record()) + "\n", encoding="utf-8")
            records, line_numbers, parse_errors = load_jsonl(path)
            self.assertEqual(line_numbers, [3])
            self.assertIn("line 2: invalid JSON", parse_errors[0])
            self.assertEqual(validate_dataset(records, line_numbers), [])

            valid_path = Path(directory) / "valid.jsonl"
            valid_path.write_text(json.dumps(toy_record()) + "\n", encoding="utf-8")
            self.assertEqual(main([str(valid_path)]), 0)

    def test_same_item_can_have_two_annotators_in_same_split(self):
        first = toy_record("annotation-1", "dev")
        second = copy.deepcopy(first)
        second["annotation_id"] = "annotation-2"
        second["annotation"]["annotator_id"] = "ann-b"
        self.assertEqual(validate_dataset([first, second]), [])


if __name__ == "__main__":
    unittest.main()
