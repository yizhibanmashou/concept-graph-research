import copy
import hashlib
import json
import unittest

from src.logic.datalog_checker import verify_certificate, verify_countermodel, verify_query


def toy_program(query_argument="fido"):
    return {
        "facts": [{"predicate": "dog", "arguments": ["fido"],
                   "source_documents": ["sources/dog-1.json"]}],
        "rules": [{"id": "r-dog-animal",
                   "head": {"predicate": "animal", "arguments": ["?x"]},
                   "body": [{"predicate": "dog", "arguments": ["?x"]}],
                   "provenance": {"sense_id": "dog-1", "source_documents": ["sources/dog-1.json"]}}],
        "query": {"predicate": "animal", "arguments": [query_argument]},
    }


def typed_program(query_predicate="animal", query_argument="fido"):
    return {
        "facts": [
            {"predicate": "dog", "arguments": ["fido"]},
            {"predicate": "dog", "arguments": ["eagle"]},
        ],
        "rules": [
            {"id": "r-dog-animal", "head": {"predicate": "animal", "arguments": ["?x"]},
             "body": [{"predicate": "dog", "arguments": ["?x"]}], "variable_sorts": {"?x": "Person"}},
            {"id": "r-person-qualified", "head": {"predicate": "qualified", "arguments": ["?x"]},
             "body": [{"predicate": "person_only", "arguments": ["?x"]}],
             "variable_sorts": {"?x": "Person"}},
        ],
        "query": {"predicate": query_predicate, "arguments": [query_argument]},
        "type_system": {
            "schema_version": "datalog-type-system/1",
            "type_system_id": "synthetic-person-entity",
            "version": "1",
            "sorts": {"Entity": [], "Person": ["Entity"]},
            "predicate_signatures": {
                "dog": ["Entity"], "animal": ["Entity"],
                "person_only": ["Person"], "qualified": ["Person"],
            },
            "constant_sorts": {"fido": ["Person"], "eagle": ["Entity"]},
        },
    }


def rehash_countermodel(countermodel):
    canonical = json.dumps(
        countermodel["interpretation"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    countermodel["interpretation_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class DatalogCheckerTests(unittest.TestCase):
    def test_typed_variable_domain_accepts_subsort_and_excludes_parent_only_constant(self):
        positive = typed_program()
        result = verify_query(positive)
        self.assertEqual(result["status"], "entailed_in_positive_datalog")
        self.assertTrue(result["certificate_valid"])

        parent_only = typed_program(query_argument="eagle")
        result = verify_query(parent_only)
        self.assertEqual(result["status"], "not_entailed_in_least_herbrand_model")
        self.assertTrue(result["countermodel_valid"])

    def test_typed_certificate_requires_matching_type_table_hash(self):
        program = typed_program()
        certificate = verify_query(program)["certificate"]
        self.assertTrue(verify_certificate(program, certificate))

        missing_hash = copy.deepcopy(certificate)
        del missing_hash["type_system_sha256"]
        self.assertFalse(verify_certificate(program, missing_hash))

        changed_type_table = copy.deepcopy(program)
        changed_type_table["type_system"]["version"] = "2"
        self.assertFalse(verify_certificate(changed_type_table, certificate))

    def test_typed_countermodel_rejects_hash_mismatch_and_wrong_sort_atom(self):
        program = typed_program(query_argument="eagle")
        countermodel = verify_query(program)["countermodel"]
        self.assertTrue(verify_countermodel(program, countermodel))

        changed_hash = copy.deepcopy(countermodel)
        changed_hash["type_system_sha256"] = "0" * 64
        self.assertFalse(verify_countermodel(program, changed_hash))

        wrong_sort = copy.deepcopy(countermodel)
        wrong_sort["interpretation"].append(
            {"predicate": "person_only", "arguments": ["eagle"]}
        )
        wrong_sort["interpretation"].sort(
            key=lambda atom: (atom["predicate"], tuple(atom["arguments"]))
        )
        rehash_countermodel(wrong_sort)
        self.assertFalse(verify_countermodel(program, wrong_sort))

    def test_hypernym_candidate_gets_replayable_proof(self):
        program = toy_program()
        result = verify_query(program)
        self.assertEqual(result["status"], "entailed_in_positive_datalog")
        self.assertTrue(result["certificate_valid"])
        self.assertTrue(verify_certificate(program, result["certificate"]))

    def test_absent_candidate_has_least_model_counterexample(self):
        program = toy_program("rover")
        result = verify_query(program)
        self.assertEqual(result["status"], "not_entailed_in_least_herbrand_model")
        self.assertTrue(result["countermodel"]["query_absent"])
        self.assertTrue(result["countermodel_valid"])
        self.assertTrue(verify_countermodel(program, result["countermodel"]))

    def test_countermodel_verifier_rejects_rule_violation_and_query_inclusion(self):
        program = toy_program("rover")
        countermodel = verify_query(program)["countermodel"]
        missing_rule_head = copy.deepcopy(countermodel)
        missing_rule_head["interpretation"] = [
            atom for atom in missing_rule_head["interpretation"]
            if atom["predicate"] != "animal"
        ]
        canonical = json.dumps(
            missing_rule_head["interpretation"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        missing_rule_head["interpretation_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.assertFalse(verify_countermodel(program, missing_rule_head))

        query_included = copy.deepcopy(countermodel)
        query_included["interpretation"].append(program["query"])
        query_included["interpretation"].sort(key=lambda atom: (atom["predicate"], tuple(atom["arguments"])))
        canonical = json.dumps(
            query_included["interpretation"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        query_included["interpretation_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.assertFalse(verify_countermodel(program, query_included))

    def test_tampered_provenance_invalidates_certificate(self):
        program = toy_program()
        cert = verify_query(program)["certificate"]
        tampered = copy.deepcopy(cert)
        rule_node = next(node for node in tampered["nodes"] if node["kind"] == "rule")
        rule_node["provenance"] = {"sense_id": "wrong-sense"}
        self.assertFalse(verify_certificate(program, tampered))

    def test_unreachable_node_invalidates_certificate(self):
        program = toy_program()
        tampered = copy.deepcopy(verify_query(program)["certificate"])
        tampered["nodes"].append({
            "node_id": '["cat",["felix"]]',
            "atom": {"predicate": "cat", "arguments": ["felix"]},
            "kind": "fact",
            "source_documents": [],
        })
        self.assertFalse(verify_certificate(program, tampered))

    def test_unsafe_rule_rejected(self):
        program = toy_program()
        program["rules"][0]["head"]["arguments"] = ["?unbound"]
        with self.assertRaisesRegex(ValueError, "unsafe head variable"):
            verify_query(program)

    def test_inconsistent_predicate_arity_rejected(self):
        program = toy_program()
        program["facts"].append({"predicate": "dog", "arguments": ["fido", "extra"]})
        with self.assertRaisesRegex(ValueError, "inconsistent arity"):
            verify_query(program)


if __name__ == "__main__":
    unittest.main()
