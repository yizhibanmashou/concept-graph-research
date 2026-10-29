import json
import copy
import tempfile
import unittest
from pathlib import Path

from src.logic.verified_reasoning_pipeline import main, route_pipeline_result, run_pipeline
from src.logic.datalog_checker import verify_certificate
from src.logic.source_record_verifier import AnnotationSourceBundleVerifier
from tests.test_annotation_to_datalog import annotation


class VerifiedReasoningPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _dev_rows(self):
        return [
            {"sense_id": f"dev-{index}", "split": "dev", "gold": "entailment",
             "example_id": f"dev-example-{index}", "claim_id": "c1",
             "premise_sha256": "a" * 64, "hypothesis_sha256": "b" * 64,
             "scores": {"entailment": .96, "neutral": .02, "contradiction": .02}}
            for index in range(80)
        ]

    def _test_prediction(self, record):
        claim = record["analysis"]["rule_claims"][0]
        return {
            "split": "test", "sense_id": record["sense"]["synset_id"],
            "gold": "entailment", "example_id": "test-example-1", "claim_id": claim["id"],
            "premise_sha256": record["source"]["input_sha256"],
            "hypothesis_sha256": claim["nli_hypothesis_sha256"],
            "scores": {"entailment": .98, "neutral": .01, "contradiction": .01},
        }

    def _source_only_problem(self, record):
        """A source_only problem whose ground facts carry full provenance."""
        gloss_hash = record["source"]["input_sha256"]
        sense_id = record["sense"]["synset_id"]
        annotation_id = record["annotation_id"]
        source_documents = [record["provenance"]["source_records"][0]["path"]]

        def source_fact(predicate, formula_node_id):
            return {
                "predicate": predicate, "arguments": ["robin"],
                "knowledge_partition": "source_assertion",
                "source_documents": source_documents,
                "source_sense_id": sense_id,
                "source_gloss_sha256": gloss_hash,
                "source_claim_refs": [{
                    "annotation_id": annotation_id, "claim_id": "c1",
                    "formula_node_id": formula_node_id,
                }],
            }

        return {
            "knowledge_scope": "source_only",
            "facts": [source_fact("BIRD", "n1"), source_fact("SMALL", "n2")],
            "query": {"predicate": f"wn_sense:{sense_id}", "arguments": ["robin"]},
        }

    def _typed_annotation_problem(self, record, target="robin"):
        record["schema_version"] = "0.5-draft"
        record["analysis"]["rule_claims"][0]["variable_sorts"] = {"?x": "Person"}
        return {
            "facts": [
                {"predicate": "BIRD", "arguments": [target]},
                {"predicate": "SMALL", "arguments": [target]},
            ],
            "query": {"predicate": f"wn_sense:{record['sense']['synset_id']}", "arguments": [target]},
            "type_system": {
                "schema_version": "datalog-type-system/1",
                "type_system_id": "synthetic-person-entity",
                "version": "1",
                "sorts": {"Entity": [], "Person": ["Entity"]},
                "predicate_signatures": {
                    "BIRD": ["Entity"], "SMALL": ["Entity"],
                    f"wn_sense:{record['sense']['synset_id']}": ["Entity"],
                },
                "constant_sorts": {target: ["Person" if target == "robin" else "Entity"]},
            },
        }

    def _build_source_bundle(self, record):
        """Create a self-consistent mini frozen bundle with one source payload."""
        import hashlib

        bundle = Path(self.temp_dir.name) / "source_bundle"
        for sub in ("graph", "indexes", "provenance", "sources"):
            (bundle / sub).mkdir(parents=True, exist_ok=True)
        gloss = record["sense"]["gloss"]
        sense_id = record["sense"]["synset_id"]

        payload_path = "sources/record.json"
        payload_bytes = json.dumps({"synset": {"raw_definition": gloss}}).encode("utf-8")
        (bundle / payload_path).write_bytes(payload_bytes)
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        record["provenance"]["source_records"] = [
            {"path": payload_path, "sha256": payload_hash}]

        def write_jsonl(rel, rows):
            (bundle / rel).write_text(
                "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

        write_jsonl("graph/hypergraph_rules.jsonl", [{}])
        write_jsonl("graph/coverage_witnesses.jsonl", [{}])
        write_jsonl("indexes/senses.jsonl", [
            {"identity": sense_id, "source_records": [{"path": payload_path}]}])
        (bundle / "provenance/hypergraph_source_contract.json").write_text(
            json.dumps({"contract_version": "test"}), encoding="utf-8")

        def sha(rel):
            return hashlib.sha256((bundle / rel).read_bytes()).hexdigest()

        (bundle / "manifest.json").write_text(json.dumps({
            "semantic_fingerprint_sha256": "fp-mini",
            "graph_sha256": sha("graph/hypergraph_rules.jsonl")}), encoding="utf-8")
        checksum_specs = [
            "graph/hypergraph_rules.jsonl",
            "graph/coverage_witnesses.jsonl",
            "indexes/senses.jsonl",
            "provenance/hypergraph_source_contract.json",
            payload_path,
        ]
        checksum_rows = []
        for rel in checksum_specs:
            data = (bundle / rel).read_bytes()
            checksum_rows.append({"path": rel, "sha256": hashlib.sha256(data).hexdigest(),
                                  "bytes": len(data)})
        write_jsonl("checksums.jsonl", checksum_rows)
        all_required = ["manifest.json", "checksums.jsonl"] + checksum_specs[:4]
        lock_path = bundle.parent / "mini_lock.json"
        lock_path.write_text(json.dumps({
            "lock_version": "oewn-frozen-bundle-integrity-lock/2",
            "bundle_semantic_fingerprint_sha256": "fp-mini",
            "files": {rel: sha(rel) for rel in all_required}}), encoding="utf-8")
        return bundle, lock_path

    def test_compiled_definition_rule_yields_replayable_query_certificate(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        problem = {
            "facts": [
                {"predicate": "BIRD", "arguments": ["robin"], "source_documents": ["fixture"]},
                {"predicate": "SMALL", "arguments": ["robin"], "source_documents": ["fixture"]},
            ],
            "query": {"predicate": "wn_sense:oewn-00000001-n", "arguments": ["robin"]},
        }
        result = run_pipeline([record], problem, annotation_sha256="a" * 64, problem_sha256="b" * 64)
        self.assertEqual(result["proof_result"]["status"], "entailed_in_positive_datalog")
        self.assertTrue(result["proof_result"]["certificate_valid"])
        self.assertTrue(verify_certificate(result["replay_program"], result["proof_result"]["certificate"]))
        self.assertEqual(result["compilation"]["compiled_rule_count"], 1)
        self.assertEqual(result["input_hashes"]["annotation_jsonl_sha256"], "a" * 64)

    def test_typed_pipeline_route_rejects_changed_type_table_after_proof(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        record["annotation"]["adjudication_status"] = "adjudicated"
        problem = self._typed_annotation_problem(record)
        result = run_pipeline([record], problem)
        self.assertEqual(result["type_validation"]["status"], "valid")
        self.assertTrue(result["proof_result"]["certificate_valid"])

        tampered = copy.deepcopy(result)
        tampered["replay_program"]["type_system"]["version"] = "2"
        routed = route_pipeline_result(
            tampered, [record], self._test_prediction(record), self._dev_rows(), minimum_precision=.9,
        )
        self.assertEqual(routed["route"], "abstain_missing_or_invalid_proof")
        self.assertFalse(routed["evidence_checks"]["proof_certificate_replayed"])
        self.assertTrue(routed["evidence_checks"]["program_rules_match_annotations"])

    def test_schema_06_sort_judgment_survives_typed_pipeline_and_certificate_replay(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        record["annotation"]["adjudication_status"] = "adjudicated"
        problem = self._typed_annotation_problem(record)
        claim = record["analysis"]["rule_claims"][0]
        record["schema_version"] = "0.6-draft"
        claim.pop("variable_sorts")
        claim["variable_sort_judgments"] = {
            "?x": {
                "status": "assigned",
                "sort": "Person",
                "basis": "lexical_semantics",
                "evidence_spans": [],
                "rationale": "Synthetic pipeline fixture only.",
            }
        }

        result = run_pipeline([record], problem)
        compiled_rule = result["replay_program"]["rules"][0]
        self.assertEqual(result["type_validation"]["status"], "valid")
        self.assertEqual(compiled_rule["variable_sorts"], {"?x": "Person"})
        self.assertEqual(compiled_rule["provenance"]["variable_sort_review_status"], "adjudicated")
        self.assertEqual(
            compiled_rule["provenance"]["variable_sort_judgments"],
            claim["variable_sort_judgments"],
        )
        self.assertTrue(result["proof_result"]["certificate_valid"])
        self.assertTrue(verify_certificate(result["replay_program"], result["proof_result"]["certificate"]))

    def test_typed_pipeline_countermodel_must_replay_before_nonentailment_route(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        record["annotation"]["adjudication_status"] = "adjudicated"
        problem = self._typed_annotation_problem(record, target="eagle")
        result = run_pipeline([record], problem)
        self.assertEqual(result["proof_result"]["status"], "not_entailed_in_least_herbrand_model")
        self.assertTrue(result["proof_result"]["countermodel_valid"])

        prediction = self._test_prediction(record)
        valid_route = route_pipeline_result(
            result, [record], prediction, self._dev_rows(), minimum_precision=.9,
        )
        self.assertEqual(valid_route["route"], "not_entailed_in_supplied_program")
        self.assertTrue(valid_route["evidence_checks"]["countermodel_replayed"])

        tampered = copy.deepcopy(result)
        tampered["proof_result"]["countermodel"]["type_system_sha256"] = "0" * 64
        rejected_route = route_pipeline_result(
            tampered, [record], prediction, self._dev_rows(), minimum_precision=.9,
        )
        self.assertEqual(rejected_route["route"], "abstain_missing_or_invalid_proof")
        self.assertFalse(rejected_route["evidence_checks"]["countermodel_replayed"])

    def test_low_confidence_rule_cannot_support_query(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        record["analysis"]["rule_claims"][0]["confidence"] = "low"
        problem = {
            "facts": [
                {"predicate": "BIRD", "arguments": ["robin"]},
                {"predicate": "SMALL", "arguments": ["robin"]},
            ],
            "query": {"predicate": "wn_sense:oewn-00000001-n", "arguments": ["robin"]},
        }
        result = run_pipeline([record], problem)
        self.assertEqual(result["proof_result"]["status"], "not_entailed_in_least_herbrand_model")
        self.assertEqual(result["compilation"]["compiled_rule_count"], 0)
        self.assertEqual(result["compilation"]["rejection_count"], 1)
        self.assertIn("does not establish", result["interpretation_limit"])

    def test_cli_writes_self_contained_replay_artifact(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        problem = {
            "facts": [
                {"predicate": "BIRD", "arguments": ["robin"]},
                {"predicate": "SMALL", "arguments": ["robin"]},
            ],
            "query": {"predicate": "wn_sense:oewn-00000001-n", "arguments": ["robin"]},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            annotations_path = root / "annotations.jsonl"
            problem_path = root / "problem.json"
            output_path = root / "result.json"
            annotations_path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            problem_path.write_text(json.dumps(problem), encoding="utf-8")
            self.assertEqual(main([str(annotations_path), str(problem_path), "--output", str(output_path)]), 0)
            artifact = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(artifact["proof_result"]["status"], "entailed_in_positive_datalog")
            self.assertTrue(verify_certificate(artifact["replay_program"], artifact["proof_result"]["certificate"]))

    def test_composed_route_replays_certificate_and_requires_adjudicated_claim(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        record["annotation"]["adjudication_status"] = "adjudicated"
        source_bundle, lock_path = self._build_source_bundle(record)
        result = run_pipeline([record], self._source_only_problem(record))
        source_verifier = AnnotationSourceBundleVerifier(
            source_bundle, integrity_lock=lock_path)
        dev = self._dev_rows()
        nli_prediction = self._test_prediction(record)
        routed = route_pipeline_result(
            result, [record], nli_prediction, dev, minimum_precision=.9,
            source_bundle_root=source_bundle, source_bundle_verifier=source_verifier,
        )
        self.assertEqual(routed["route"], "candidate_supported_by_proof_nli_and_review")
        self.assertTrue(routed["evidence_checks"]["proof_certificate_replayed"])
        self.assertTrue(routed["evidence_checks"]["all_used_rules_bound_to_adjudicated_supported_claims"])
        self.assertFalse(routed["evidence_checks"]["test_gold_label_used"])

        record["annotation"]["adjudication_status"] = "independent"
        unadjudicated = route_pipeline_result(
            result, [record], nli_prediction, dev, minimum_precision=.9,
        )
        self.assertEqual(unadjudicated["route"], "abstain_source_rule_not_semantically_audited")

    def test_composed_route_accepts_unlabeled_test_prediction(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        record["annotation"]["adjudication_status"] = "adjudicated"
        source_bundle, lock_path = self._build_source_bundle(record)
        result = run_pipeline([record], self._source_only_problem(record))
        source_verifier = AnnotationSourceBundleVerifier(
            source_bundle, integrity_lock=lock_path)
        prediction = self._test_prediction(record)
        prediction.pop("gold")

        routed = route_pipeline_result(
            result, [record], prediction, self._dev_rows(), minimum_precision=.9,
            source_bundle_root=source_bundle, source_bundle_verifier=source_verifier,
        )

        self.assertEqual(routed["route"], "candidate_supported_by_proof_nli_and_review")
        self.assertFalse(routed["evidence_checks"]["test_gold_label_used"])

    def test_composed_route_rejects_test_sense_leakage_without_gold(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        record["annotation"]["adjudication_status"] = "adjudicated"
        problem = {
            "facts": [{"predicate": "BIRD", "arguments": ["robin"]},
                      {"predicate": "SMALL", "arguments": ["robin"]}],
            "query": {"predicate": "wn_sense:oewn-00000001-n", "arguments": ["robin"]},
        }
        result = run_pipeline([record], problem)
        prediction = self._test_prediction(record)
        prediction.pop("gold")
        prediction["sense_id"] = self._dev_rows()[0]["sense_id"]

        with self.assertRaisesRegex(ValueError, "group leakage"):
            route_pipeline_result(result, [record], prediction, self._dev_rows(), minimum_precision=.9)

    def test_composed_route_rejects_example_id_reused_from_dev(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        record["annotation"]["adjudication_status"] = "adjudicated"
        problem = {
            "facts": [{"predicate": "BIRD", "arguments": ["robin"]},
                      {"predicate": "SMALL", "arguments": ["robin"]}],
            "query": {"predicate": "wn_sense:oewn-00000001-n", "arguments": ["robin"]},
        }
        result = run_pipeline([record], problem)
        dev = self._dev_rows()
        prediction = self._test_prediction(record)
        prediction.pop("gold")
        prediction["example_id"] = dev[0]["example_id"]

        with self.assertRaisesRegex(ValueError, "example_id leakage"):
            route_pipeline_result(result, [record], prediction, dev, minimum_precision=.9)

    def test_composed_route_rejects_tampered_certificate_even_if_nli_is_high(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        record["annotation"]["adjudication_status"] = "adjudicated"
        problem = {
            "facts": [{"predicate": "BIRD", "arguments": ["robin"]},
                      {"predicate": "SMALL", "arguments": ["robin"]}],
            "query": {"predicate": "wn_sense:oewn-00000001-n", "arguments": ["robin"]},
        }
        result = run_pipeline([record], problem)
        result = copy.deepcopy(result)
        result["proof_result"]["certificate"]["nodes"].pop()
        dev = self._dev_rows()
        routed = route_pipeline_result(
            result, [record], self._test_prediction(record), dev, minimum_precision=.9,
        )
        self.assertEqual(routed["route"], "abstain_missing_or_invalid_proof")
        self.assertFalse(routed["evidence_checks"]["proof_certificate_replayed"])

    def test_composed_route_rejects_annotation_changed_after_proof_compilation(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        record["annotation"]["adjudication_status"] = "adjudicated"
        problem = {
            "facts": [{"predicate": "BIRD", "arguments": ["robin"]},
                      {"predicate": "SMALL", "arguments": ["robin"]}],
            "query": {"predicate": "wn_sense:oewn-00000001-n", "arguments": ["robin"]},
        }
        result = run_pipeline([record], problem)
        changed = copy.deepcopy(record)
        # Keep gap-free subtree coverage so validation passes, but use span
        # boundaries different from the original [0,12] evidence so the
        # recompiled rule provenance no longer matches the certificate that
        # was produced from the original record.
        changed["analysis"]["rule_claims"][0]["evidence_spans"] = [
            {"start": 0, "end": 6}, {"start": 6, "end": 12}]
        dev = self._dev_rows()
        prediction = self._test_prediction(changed)
        routed = route_pipeline_result(result, [changed], prediction, dev, minimum_precision=.9)
        self.assertEqual(routed["route"], "abstain_missing_or_invalid_proof")
        self.assertTrue(routed["evidence_checks"]["proof_certificate_replayed"])
        self.assertFalse(routed["evidence_checks"]["program_rules_match_annotations"])

    def test_composed_route_abstains_when_nli_pair_does_not_match_proof_claim(self):
        record = annotation("and", "sufficient", "gloss_to_target")
        record["annotation"]["adjudication_status"] = "adjudicated"
        problem = {
            "facts": [{"predicate": "BIRD", "arguments": ["robin"]},
                      {"predicate": "SMALL", "arguments": ["robin"]}],
            "query": {"predicate": "wn_sense:oewn-00000001-n", "arguments": ["robin"]},
        }
        result = run_pipeline([record], problem)
        dev = self._dev_rows()

        wrong_hypothesis = self._test_prediction(record)
        wrong_hypothesis["hypothesis_sha256"] = "c" * 64
        routed = route_pipeline_result(result, [record], wrong_hypothesis, dev, minimum_precision=.9)
        self.assertEqual(routed["route"], "abstain_source_rule_not_semantically_audited")
        self.assertTrue(routed["evidence_checks"]["proof_certificate_replayed"])
        self.assertFalse(routed["evidence_checks"]["nli_text_pair_hashes_bound_to_proof_claim"])

        wrong_claim = self._test_prediction(record)
        wrong_claim["claim_id"] = "different-claim"
        routed = route_pipeline_result(result, [record], wrong_claim, dev, minimum_precision=.9)
        self.assertEqual(routed["route"], "abstain_source_rule_not_semantically_audited")
        self.assertFalse(routed["evidence_checks"]["nli_text_pair_hashes_bound_to_proof_claim"])


if __name__ == "__main__":
    unittest.main()
