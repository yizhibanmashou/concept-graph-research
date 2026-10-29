import copy
import hashlib
import unittest

from src.logic.annotation_to_datalog import compile_annotations
from src.logic.annotation_validator import validate_record
from src.logic.datalog_checker import verify_certificate, verify_query


def annotation(formula_kind="and", relation="necessary", direction="target_to_gloss"):
    nodes = [
        {"id": "n1", "kind": "atom", "predicate": "BIRD", "arguments": [{"kind": "variable", "id": "?x"}], "span": {"start": 2, "end": 6}},
        {"id": "n2", "kind": "atom", "predicate": "SMALL", "arguments": [{"kind": "variable", "id": "?x"}], "span": {"start": 7, "end": 12}},
        {"id": "n3", "kind": formula_kind, "children": ["n1", "n2"], "span": {"start": 0, "end": 12}},
    ]
    return {
        "schema_version": "0.4-draft",
        "item_id": "oewn-2025-plus:oewn-00000001-n",
        "annotation_id": "oewn-2025-plus:oewn-00000001-n:rater-a:independent",
        "source": {
            "resource": "Open English WordNet 2025 Plus",
            "version": "2025-12-31",
            "record_id": "oewn-00000001-n",
            "input_sha256": hashlib.sha256("a bird small".encode("utf-8")).hexdigest(),
            "license": "CC BY 4.0",
        },
        "sense": {"synset_id": "oewn-00000001-n", "lemmas": ["small bird"], "pos": "n", "gloss": "a bird small"},
        "analysis": {
            "status": "annotated",
            "nodes": nodes,
            "root_node_ids": ["n3"],
            "rule_claims": [{
                "id": "c1", "relation": relation, "direction": direction,
                "formula_node_id": "n3", "evidence_spans": [{"start": 0, "end": 12}], "confidence": "high",
                "semantic_support": "supported",
                "inference_basis": ["lexical_or_paraphrastic"],
                "nli_hypothesis": "The concept is a bird and is small.",
                "nli_hypothesis_sha256": hashlib.sha256(
                    "The concept is a bird and is small.".encode("utf-8")
                ).hexdigest(),
            }],
            "horn_projection": {"status": "not_attempted", "rule_ids": [], "omissions": []},
        },
        "annotation": {"annotator_id": "rater-a", "adjudication_status": "independent", "notes": []},
        "split": "unassigned",
        "provenance": {"source_records": [{"path": "record.json", "sha256": "b" * 64}]},
    }


class AnnotationToDatalogTests(unittest.TestCase):
    def test_schema_05_variable_sorts_reach_typed_rule_and_replay(self):
        record = annotation()
        record["schema_version"] = "0.5-draft"
        record["analysis"]["rule_claims"][0]["variable_sorts"] = {"?x": "Entity"}
        self.assertEqual(validate_record(record), [])

        compiled = compile_annotations([record])
        self.assertEqual(compiled["compiler_version"], "annotation-to-positive-horn/6")
        self.assertTrue(all(rule["variable_sorts"] == {"?x": "Entity"} for rule in compiled["rules"]))
        program = {
            "facts": [{"predicate": "wn_sense:oewn-00000001-n", "arguments": ["robin"]}],
            "rules": compiled["rules"],
            "query": {"predicate": "BIRD", "arguments": ["robin"]},
            "type_system": {
                "schema_version": "datalog-type-system/1",
                "type_system_id": "toy-lexical-types",
                "version": "1",
                "sorts": {"Entity": []},
                "predicate_signatures": {
                    "BIRD": ["Entity"],
                    "SMALL": ["Entity"],
                    "wn_sense:oewn-00000001-n": ["Entity"],
                },
                "constant_sorts": {"robin": ["Entity"]},
            },
        }
        result = verify_query(program)
        self.assertEqual(result["status"], "entailed_in_positive_datalog")
        self.assertTrue(result["certificate_valid"])

    def test_schema_06_sort_judgment_provenance_reaches_rule_and_replays(self):
        record = annotation()
        record["schema_version"] = "0.6-draft"
        claim = record["analysis"]["rule_claims"][0]
        claim["variable_sort_judgments"] = {
            "?x": {
                "status": "assigned",
                "sort": "Entity",
                "basis": "gloss_span",
                "evidence_spans": [{"start": 2, "end": 6}],
                "rationale": "Synthetic example: the defined referent is an entity.",
            }
        }
        self.assertEqual(validate_record(record), [])

        compiled = compile_annotations([record])
        self.assertEqual(compiled["compiler_version"], "annotation-to-positive-horn/6")
        self.assertEqual(compiled["compiled_rule_count"], 2)
        for rule in compiled["rules"]:
            self.assertEqual(rule["variable_sorts"], {"?x": "Entity"})
            self.assertEqual(rule["provenance"]["variable_sort_judgments"], claim["variable_sort_judgments"])
            self.assertEqual(rule["provenance"]["variable_sort_review_status"], "independent")

        program = {
            "facts": [{"predicate": "wn_sense:oewn-00000001-n", "arguments": ["robin"]}],
            "rules": compiled["rules"],
            "query": {"predicate": "BIRD", "arguments": ["robin"]},
            "type_system": {
                "schema_version": "datalog-type-system/1",
                "type_system_id": "toy-lexical-types",
                "version": "1",
                "sorts": {"Entity": []},
                "predicate_signatures": {
                    "BIRD": ["Entity"],
                    "SMALL": ["Entity"],
                    "wn_sense:oewn-00000001-n": ["Entity"],
                },
                "constant_sorts": {"robin": ["Entity"]},
            },
        }
        result = verify_query(program)
        self.assertEqual(result["status"], "entailed_in_positive_datalog")
        self.assertTrue(result["certificate_valid"])
        certificate = copy.deepcopy(result["certificate"])
        proof_rule = next(node for node in certificate["nodes"] if node["kind"] == "rule")
        proof_rule["provenance"]["variable_sort_judgments"]["?x"]["basis"] = "reviewer_convention"
        self.assertFalse(verify_certificate(program, certificate))

    def test_schema_06_unresolved_sort_judgment_blocks_compilation(self):
        record = annotation()
        record["schema_version"] = "0.6-draft"
        record["analysis"]["rule_claims"][0]["variable_sort_judgments"] = {
            "?x": {
                "status": "unresolved",
                "sort": None,
                "basis": "unknown",
                "evidence_spans": [],
                "rationale": "The referent domain cannot be determined in this synthetic example.",
            }
        }
        self.assertEqual(validate_record(record), [])
        compiled = compile_annotations([record])
        self.assertEqual(compiled["compiled_rule_count"], 0)
        self.assertIn("sort judgment unresolved", compiled["rejections"][0]["reason"])

    def test_schema_06_requires_exact_variables_and_valid_type_evidence(self):
        record = annotation()
        record["schema_version"] = "0.6-draft"
        judgment = {
            "status": "assigned",
            "sort": "Entity",
            "basis": "gloss_span",
            "evidence_spans": [{"start": 2, "end": 6}],
            "rationale": "Synthetic example.",
        }
        claim = record["analysis"]["rule_claims"][0]
        claim["variable_sort_judgments"] = {"?x": judgment, "?extra": judgment}
        self.assertIn("declares unused variables", " ".join(validate_record(record)))
        claim["variable_sort_judgments"] = {"?x": {**judgment, "evidence_spans": [{"start": 4, "end": 99}]}}
        self.assertIn("gloss length", " ".join(validate_record(record)))
        claim["variable_sort_judgments"] = {"?x": {**judgment, "basis": "unknown"}}
        self.assertIn("cannot be 'unknown'", " ".join(validate_record(record)))
        claim["variable_sort_judgments"] = {"?x": judgment}
        claim["variable_sorts"] = {"?x": "Entity"}
        self.assertIn("superseded by variable_sort_judgments", " ".join(validate_record(record)))

    def test_schema_05_requires_exact_formula_variable_sort_map(self):
        record = annotation()
        record["schema_version"] = "0.5-draft"
        claim = record["analysis"]["rule_claims"][0]
        claim["variable_sorts"] = {}
        self.assertIn("missing variables", " ".join(validate_record(record)))
        claim["variable_sorts"] = {"?x": "Entity", "?unused": "Entity"}
        self.assertIn("declares unused variables", " ".join(validate_record(record)))

    def test_schema_05_keeps_the_gloss_grounded_inference_basis_gate(self):
        record = annotation()
        record["schema_version"] = "0.5-draft"
        claim = record["analysis"]["rule_claims"][0]
        claim["variable_sorts"] = {"?x": "Entity"}
        claim["inference_basis"] = ["external_world_knowledge"]
        compiled = compile_annotations([record])
        self.assertEqual(compiled["compiled_rule_count"], 0)
        self.assertIn("not gloss-grounded", compiled["rejections"][0]["reason"])

    def test_necessary_conjunction_compiles_target_to_each_conjunct(self):
        compiled = compile_annotations([annotation()])
        self.assertEqual(compiled["compiled_rule_count"], 2)
        self.assertEqual(compiled["rejection_count"], 0)
        self.assertEqual(
            {rule["head"]["predicate"] for rule in compiled["rules"]},
            {"BIRD", "SMALL"},
        )
        self.assertTrue(all(rule["body"][0]["predicate"] == "wn_sense:oewn-00000001-n"
                            for rule in compiled["rules"]))

    def test_sufficient_conjunction_compiles_all_conjuncts_to_target(self):
        compiled = compile_annotations([annotation("and", "sufficient", "gloss_to_target")])
        self.assertEqual(compiled["compiled_rule_count"], 1)
        rule = compiled["rules"][0]
        self.assertEqual(rule["head"]["predicate"], "wn_sense:oewn-00000001-n")
        self.assertEqual([atom["predicate"] for atom in rule["body"]], ["BIRD", "SMALL"])

    def test_synthetic_constraint_deletion_broadens_sufficient_rule(self):
        """A compiler regression check, not a test of semantic mutation detection."""
        complete = annotation("and", "sufficient", "gloss_to_target")
        deleted_constraint = copy.deepcopy(complete)
        deleted_constraint["analysis"]["nodes"] = [
            node for node in deleted_constraint["analysis"]["nodes"] if node["id"] == "n1"
        ]
        deleted_constraint["analysis"]["root_node_ids"] = ["n1"]
        deleted_constraint["analysis"]["rule_claims"][0]["formula_node_id"] = "n1"

        def query_result(record):
            rules = compile_annotations([record])["rules"]
            return verify_query({
                "facts": [{
                    "predicate": "BIRD",
                    "arguments": ["robin"],
                    "source_documents": ["oewn-2025-plus"],
                }],
                "rules": rules,
                "query": {
                    "predicate": "wn_sense:oewn-00000001-n",
                    "arguments": ["robin"],
                },
            })["status"]

        self.assertEqual(query_result(complete), "not_entailed_in_least_herbrand_model")
        self.assertEqual(query_result(deleted_constraint), "entailed_in_positive_datalog")

    def test_sufficient_or_compiles_to_separate_safe_horn_branches(self):
        compiled = compile_annotations([annotation("or", "sufficient", "gloss_to_target")])
        self.assertEqual(compiled["compiled_rule_count"], 2)
        program = {
            "facts": [{"predicate": "BIRD", "arguments": ["robin"], "source_documents": ["oewn-2025-plus"]}],
            "rules": compiled["rules"],
            "query": {"predicate": "wn_sense:oewn-00000001-n", "arguments": ["robin"]},
        }
        result = verify_query(program)
        self.assertEqual(result["status"], "entailed_in_positive_datalog")
        self.assertTrue(result["certificate_valid"])
        self.assertTrue(verify_certificate(program, result["certificate"]))
        proof_node = next(node for node in result["certificate"]["nodes"] if node["kind"] == "rule")
        self.assertEqual(proof_node["provenance"]["evidence_spans"], [{"start": 0, "end": 12}])
        self.assertEqual(proof_node["provenance"]["semantic_support"], "supported")
        self.assertEqual(proof_node["provenance"]["support_confidence"], "high")
        self.assertEqual(proof_node["provenance"]["source_records"][0]["sha256"], "b" * 64)
        tampered = copy.deepcopy(result["certificate"])
        next(node for node in tampered["nodes"] if node["kind"] == "rule")["provenance"]["sense_id"] = "wrong"
        self.assertFalse(verify_certificate(program, tampered))

    def test_necessary_disjunction_is_rejected_without_flattening(self):
        compiled = compile_annotations([annotation("or", "necessary", "target_to_gloss")])
        self.assertEqual(compiled["compiled_rule_count"], 0)
        self.assertIn("cannot be represented", compiled["rejections"][0]["reason"])

    def test_relation_direction_conflict_is_rejected(self):
        compiled = compile_annotations([annotation("and", "necessary", "gloss_to_target")])
        self.assertEqual(compiled["compiled_rule_count"], 0)
        self.assertIn("mismatch", compiled["rejections"][0]["reason"])

    def test_non_unary_atoms_are_rejected_with_explicit_reason(self):
        record = annotation()
        record["analysis"]["nodes"][0]["arguments"].append({"kind": "variable", "id": "?y"})
        reason = compile_annotations([record])["rejections"][0]["reason"]
        self.assertIn("unary", reason)

    def test_dnf_expansion_is_bounded_before_rule_emission(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        nodes = record["analysis"]["nodes"]
        disjunction_ids = []
        for index in range(7):
            atom_a = f"a{index}"
            atom_b = f"b{index}"
            or_id = f"or{index}"
            nodes.extend([
                {"id": atom_a, "kind": "atom", "predicate": f"P{index}A", "arguments": [{"kind": "variable", "id": "?x"}], "span": {"start": 0, "end": 1}},
                {"id": atom_b, "kind": "atom", "predicate": f"P{index}B", "arguments": [{"kind": "variable", "id": "?x"}], "span": {"start": 0, "end": 1}},
                {"id": or_id, "kind": "or", "children": [atom_a, atom_b], "span": {"start": 0, "end": 1}},
            ])
            disjunction_ids.append(or_id)
        nodes.append({"id": "root", "kind": "and", "children": disjunction_ids, "span": {"start": 0, "end": 1}})
        record["analysis"]["root_node_ids"] = ["root"]
        record["analysis"]["rule_claims"][0]["formula_node_id"] = "root"

        compiled = compile_annotations([record])
        self.assertEqual(compiled["compiled_rule_count"], 0)
        self.assertIn("64-branch safety limit", compiled["rejections"][0]["reason"])

    def test_non_definition_claims_are_not_promoted_to_rules(self):
        compiled = compile_annotations([annotation("and", "typical", "none")])
        self.assertEqual(compiled["compiled_rule_count"], 0)
        self.assertEqual(compiled["rejections"][0]["reason"], "claim relation 'typical' is not a definition rule")

    def test_low_confidence_claim_is_preserved_as_rejection_not_compiled(self):
        record = annotation()
        record["analysis"]["rule_claims"][0]["confidence"] = "low"
        compiled = compile_annotations([record])
        self.assertEqual(compiled["compiled_rule_count"], 0)
        self.assertEqual(compiled["rejection_count"], 1)
        self.assertIn("below compilation threshold 'medium'", compiled["rejections"][0]["reason"])
        self.assertEqual(compiled["minimum_compilation_confidence"], "medium")

    def test_only_explicitly_supported_claims_are_compiled(self):
        for status in ("not_supported", "uncertain", "unassessed"):
            with self.subTest(status=status):
                record = annotation()
                claim = record["analysis"]["rule_claims"][0]
                claim["semantic_support"] = status
                if status == "not_supported":
                    # Schema 0.4 requires a non-empty, status-compatible reason.
                    claim["support_reasons"] = ["content_not_licensed"]
                elif status == "uncertain":
                    claim["support_reasons"] = ["lexical_or_sense_ambiguity"]
                else:
                    # An unassessed claim must carry the matching inference basis.
                    claim["inference_basis"] = ["unassessed"]
                compiled = compile_annotations([record])
                self.assertEqual(compiled["compiled_rule_count"], 0)
                self.assertIn(f"semantic support is '{status}'", compiled["rejections"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
