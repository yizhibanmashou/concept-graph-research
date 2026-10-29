"""Run reviewed gloss rules through the compiler and proof-certificate checker.

This pipeline does not parse glosses or establish that annotations are
semantically faithful. It makes the existing human-review -> Horn compilation
-> finite positive Datalog proof path reproducible as one operation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.logic.annotation_to_datalog import compile_annotations
from src.logic.annotation_validator import load_jsonl, validate_dataset
from src.logic.datalog_checker import (
    FACT_KNOWLEDGE_PARTITIONS,
    verify_certificate,
    verify_countermodel,
    verify_query,
)
from src.logic.nli_gate import SHA256_RE, route_candidate, select_certified_entailment_threshold
from src.logic.source_record_verifier import (
    AnnotationSourceBundleVerifier,
    verify_annotation_records,
)


PIPELINE_VERSION = "reviewed-gloss-proof-pipeline/13"


def _formula_subtree_node_ids(formula_node_id: str, nodes: dict[str, dict[str, Any]]) -> set[str]:
    """Return node IDs reachable from a claim's formula root."""
    result: set[str] = set()
    pending = [formula_node_id]
    while pending:
        node_id = pending.pop()
        if node_id in result or node_id not in nodes:
            continue
        result.add(node_id)
        node = nodes[node_id]
        kind = node.get("kind")
        if kind in {"and", "or"} and isinstance(node.get("children"), list):
            pending.extend(child for child in node["children"] if isinstance(child, str))
        elif kind in {"not", "forall", "exists"} and isinstance(node.get("child"), str):
            pending.append(node["child"])
        elif kind == "implies":
            pending.extend(child for child in (node.get("antecedent"), node.get("consequent"))
                           if isinstance(child, str))
    return result


def _canonical_json_sha256(value: Any, label: str) -> str:
    """Hash a JSON-compatible value independent of whitespace and key order."""
    try:
        payload = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must contain only finite JSON-compatible values") from exc
    return hashlib.sha256(payload).hexdigest()


def _same_sha256(left: Any, right: Any) -> bool:
    """Compare validated hexadecimal digests independent of letter case."""
    return (isinstance(left, str) and isinstance(right, str)
            and SHA256_RE.fullmatch(left) is not None
            and SHA256_RE.fullmatch(right) is not None
            and left.lower() == right.lower())


def _type_validation_report(program: dict[str, Any]) -> dict[str, Any]:
    """Recompute the optional typed-program check for an auditable route report."""
    if "type_system" not in program:
        return {"status": "not_requested", "valid": None, "errors": []}
    from src.logic.typed_program_validator import validate_typed_program

    report = validate_typed_program(program)
    return {**report, "status": "valid" if report.get("valid") is True else "invalid"}


def run_pipeline(records: list[dict[str, Any]], problem: dict[str, Any], *,
                 annotation_sha256: str | None = None,
                 problem_sha256: str | None = None) -> dict[str, Any]:
    """Compile reviewed records and verify one query against supplied facts."""
    if not isinstance(problem, dict):
        raise ValueError("problem must be a JSON object")
    for label, digest in (("annotation_sha256", annotation_sha256), ("problem_sha256", problem_sha256)):
        if digest is not None and (not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)):
            raise ValueError(f"{label} must be a 64-character hexadecimal SHA-256 value")
    facts = problem.get("facts")
    query = problem.get("query")
    if not isinstance(facts, list):
        raise ValueError("problem.facts must be a list")
    if not isinstance(query, dict):
        raise ValueError("problem.query must be an atom object")

    knowledge_scope = problem.get("knowledge_scope", "all_inputs")
    if not isinstance(knowledge_scope, str) or knowledge_scope not in {"all_inputs", "source_only"}:
        raise ValueError("problem.knowledge_scope must be all_inputs or source_only")
    partition_counts: Counter[str] = Counter()
    for index, fact in enumerate(facts):
        if not isinstance(fact, dict):
            raise ValueError(f"problem.facts[{index}] must be an object")
        partition = fact.get("knowledge_partition", "unclassified")
        if not isinstance(partition, str) or partition not in FACT_KNOWLEDGE_PARTITIONS | {"unclassified"}:
            raise ValueError(f"problem.facts[{index}].knowledge_partition is invalid")
        partition_counts[partition] += 1
    if knowledge_scope == "source_only":
        if partition_counts["unclassified"]:
            raise ValueError("source_only knowledge scope requires an explicit knowledge_partition on every fact")
        applied_facts = []
        for index, fact in enumerate(facts):
            if fact["knowledge_partition"] != "source_assertion":
                continue
            source_documents = fact.get("source_documents")
            if not isinstance(source_documents, list) or not source_documents or any(
                not isinstance(source, str) or not source.strip() for source in source_documents
            ):
                raise ValueError(
                    f"source_only problem.facts[{index}] needs non-empty source_documents"
                )
            source_sense_id = fact.get("source_sense_id")
            source_gloss_sha256 = fact.get("source_gloss_sha256")
            if not isinstance(source_sense_id, str) or not source_sense_id.strip():
                raise ValueError(
                    f"source_only problem.facts[{index}] needs a non-empty source_sense_id"
                )
            if not isinstance(source_gloss_sha256, str) or not SHA256_RE.fullmatch(source_gloss_sha256):
                raise ValueError(
                    f"source_only problem.facts[{index}] needs a valid source_gloss_sha256"
                )
            source_claim_refs = fact.get("source_claim_refs")
            if not isinstance(source_claim_refs, list) or not source_claim_refs or any(
                not isinstance(ref, dict)
                or any(not isinstance(ref.get(field), str) or not ref[field].strip()
                       for field in ("annotation_id", "claim_id", "formula_node_id"))
                for ref in source_claim_refs
            ):
                raise ValueError(
                    f"source_only problem.facts[{index}] needs source_claim_refs to reviewed gloss atom nodes"
                )
            applied_facts.append(fact)
    else:
        applied_facts = facts

    compiled = compile_annotations(records)
    annotation_content_sha256 = _canonical_json_sha256(records, "records")
    problem_content_sha256 = _canonical_json_sha256(problem, "problem")
    program = {"facts": applied_facts, "rules": compiled["rules"], "query": query}
    if "type_system" in problem:
        program["type_system"] = problem["type_system"]
    type_validation = _type_validation_report(program)
    try:
        proof_result = verify_query(program)
    except ValueError as exc:
        proof_result = {
            "status": "unknown",
            "query": query,
            "reason_code": (
                "invalid_typed_program"
                if type_validation.get("status") == "invalid"
                else "invalid_or_unsupported_datalog_program"
            ),
            "detail": str(exc),
        }
    if proof_result.get("certificate") and not proof_result.get("certificate_valid"):
        raise RuntimeError("proof certificate failed independent replay")

    return {
        "pipeline_version": PIPELINE_VERSION,
        "input_hashes": {
            "annotation_jsonl_sha256": annotation_sha256,
            "problem_json_sha256": problem_sha256,
            "annotation_records_canonical_json_sha256": annotation_content_sha256,
            "problem_canonical_json_sha256": problem_content_sha256,
        },
        "compilation": {
            "compiler_version": compiled["compiler_version"],
            "minimum_compilation_confidence": compiled["minimum_compilation_confidence"],
            "compiled_rule_count": compiled["compiled_rule_count"],
            "rejection_count": compiled["rejection_count"],
            "rejections": compiled["rejections"],
        },
        "proof_result": proof_result,
        "type_validation": type_validation,
        "replay_program": program,
        "fact_scope": {
            "policy": knowledge_scope,
            "input_fact_counts_by_partition": dict(sorted(partition_counts.items())),
            "applied_fact_count": len(applied_facts),
            "excluded_fact_count": len(facts) - len(applied_facts),
            "definition_rules_partition": "adjudicated_annotation_rules",
        },
        "interpretation_limit": (
            "A valid certificate proves the query from the facts retained by the declared knowledge_scope "
            "and compiled rules only. In source_only mode, only explicitly tagged source_assertion facts "
            "are retained, and caller-declared sense/gloss bindings are checked against the test input. "
            "Each used source fact must now cite an adjudicated supported gloss atom with the same predicate, "
            "sense, and gloss hash; its arguments must match that atom's variables/constants and the declared "
            "target-variable binding must equal the query target. "
            "Source paths and human semantic judgments are still not independently verified against external files. "
            "It does not establish that the human annotations faithfully express the gloss, "
            "that the gloss entails the rule, or that non-entailment means false in an open world."
        ),
    }


def route_pipeline_result(
    result: dict[str, Any],
    records: list[dict[str, Any]],
    nli_prediction: dict[str, Any],
    dev_rows: list[dict[str, Any]],
    minimum_precision: float = 0.9,
    precision_confidence_level: float = 0.95,
    source_bundle_root: Path | None = None,
    source_bundle_verifier: AnnotationSourceBundleVerifier | None = None,
) -> dict[str, Any]:
    """Route only after replaying the proof and binding used rules to adjudication.

    ``route_candidate`` remains a low-level policy helper that accepts booleans.
    This wrapper derives those booleans from the actual pipeline certificate,
    replay program, and canonical adjudicated annotation records. For repeated
    routing, callers can reuse ``source_bundle_verifier`` so immutable bundle
    metadata is indexed once while cited payload bytes are checked per result.
    """
    if not isinstance(result, dict):
        raise ValueError("pipeline result must be an object")
    annotation_errors = validate_dataset(records)
    if annotation_errors:
        raise ValueError("annotation evidence is invalid: " + "; ".join(annotation_errors[:5]))
    if (not isinstance(nli_prediction, dict) or nli_prediction.get("split") != "test"
            or not isinstance(nli_prediction.get("sense_id"), str)
            or not nli_prediction["sense_id"]
            or not isinstance(nli_prediction.get("example_id"), str)
            or not nli_prediction["example_id"]
            or not isinstance(nli_prediction.get("claim_id"), str)
            or not nli_prediction["claim_id"]):
        raise ValueError("routing requires a test prediction with sense_id, example_id, and claim_id")
    if not isinstance(dev_rows, list) or any(
        not isinstance(row, dict)
        or not all(isinstance(row.get(field), str) and row[field] for field in ("example_id", "claim_id"))
        or not isinstance(row.get("sense_id"), str) or not row["sense_id"]
        or not isinstance(row.get("premise_sha256"), str)
        or not isinstance(row.get("hypothesis_sha256"), str)
        for row in dev_rows
    ):
        raise ValueError("composed routing requires example/claim IDs and premise/hypothesis hashes on every dev row")
    if not all(
        isinstance(nli_prediction.get(field), str) and SHA256_RE.fullmatch(nli_prediction[field])
        for field in ("premise_sha256", "hypothesis_sha256")
    ):
        raise ValueError("composed routing requires valid premise and hypothesis SHA-256 values on the test prediction")
    if "group_id" in nli_prediction and (
        not isinstance(nli_prediction["group_id"], str) or not nli_prediction["group_id"]
    ):
        raise ValueError("test prediction group_id must be a non-empty string when supplied")
    uses_group_id = any("group_id" in row for row in dev_rows) or "group_id" in nli_prediction
    group_field = "group_id" if uses_group_id else "sense_id"
    if uses_group_id and (
        any("group_id" not in row for row in dev_rows) or "group_id" not in nli_prediction
    ):
        raise ValueError("If group_id is used, it must be present on every dev row and the test prediction")
    if any(not isinstance(row.get(group_field), str) or not row[group_field].strip()
           for row in dev_rows):
        raise ValueError(f"composed routing requires a non-empty {group_field} on every dev row")
    if not isinstance(nli_prediction.get(group_field), str) or not nli_prediction[group_field].strip():
        raise ValueError(f"composed routing requires a non-empty {group_field} on the test prediction")
    dev_groups = {row[group_field] for row in dev_rows}
    if nli_prediction[group_field] in dev_groups:
        raise ValueError("Development/test group leakage detected")
    if nli_prediction["example_id"] in {row["example_id"] for row in dev_rows}:
        raise ValueError("Development/test example_id leakage detected")
    # The certified selector requires one explicit group_id per calibration
    # row. For compatibility callers without group IDs, use sense_id as the
    # conservative isolation unit; strict exports already carry group_id.
    calibration_rows = (
        dev_rows if uses_group_id
        else [{**row, "group_id": row["sense_id"]} for row in dev_rows]
    )
    # Online routing must not require a test gold label. Calibrate only on
    # labeled dev rows, then route the unlabeled test prediction.
    threshold_selection = select_certified_entailment_threshold(
        calibration_rows, minimum_precision, precision_confidence_level
    )
    threshold_selection["grouping_policy"] = (
        "explicit_group_id" if uses_group_id else "sense_id_as_group_id_compatibility_fallback"
    )
    threshold_selection["development_rows_sha256_scope"] = (
        "calibration rows after group-key normalization"
    )
    proof_result = result.get("proof_result")
    program = result.get("replay_program")
    typed_program_validation = (
        _type_validation_report(program) if isinstance(program, dict)
        else {"status": "unavailable", "valid": False, "errors": ["replay program is not an object"]}
    )
    certificate = proof_result.get("certificate") if isinstance(proof_result, dict) else None
    program_query = program.get("query") if isinstance(program, dict) else None
    proof_query = proof_result.get("query") if isinstance(proof_result, dict) else None
    if (not isinstance(program_query, dict)
            or program_query.get("predicate") != f"wn_sense:{nli_prediction['sense_id']}"
            or proof_query != program_query):
        raise ValueError("test prediction sense_id must match the pipeline query")

    expected_rules = compile_annotations(records)["rules"]
    try:
        program_rules = program.get("rules") if isinstance(program, dict) else None
        certificate_replayed = (
            isinstance(proof_result, dict)
            and proof_result.get("status") == "entailed_in_positive_datalog"
            and isinstance(certificate, dict)
            and isinstance(program, dict)
            and verify_certificate(program, certificate)
        )
    except (KeyError, TypeError, ValueError):
        certificate_replayed = False
    countermodel = proof_result.get("countermodel") if isinstance(proof_result, dict) else None
    try:
        countermodel_replayed = (
            isinstance(proof_result, dict)
            and proof_result.get("status") == "not_entailed_in_least_herbrand_model"
            and isinstance(countermodel, dict)
            and isinstance(program, dict)
            and verify_countermodel(program, countermodel)
        )
    except (KeyError, TypeError, ValueError):
        countermodel_replayed = False
    program_rules_match_annotations = isinstance(program_rules, list) and program_rules == expected_rules
    proof_valid = certificate_replayed and program_rules_match_annotations

    records_by_annotation = {record["annotation_id"]: record for record in records}
    rules_by_id = {
        rule.get("id"): rule
        for rule in program.get("rules", [])
        if isinstance(rule, dict) and isinstance(rule.get("id"), str)
    } if isinstance(program, dict) and isinstance(program.get("rules"), list) else {}
    used_rule_ids = {
        node.get("rule_id")
        for node in certificate.get("nodes", [])
        if isinstance(node, dict) and node.get("kind") == "rule"
    } if isinstance(certificate, dict) and isinstance(certificate.get("nodes"), list) else set()

    fact_nodes = [
        node for node in certificate.get("nodes", [])
        if isinstance(node, dict) and node.get("kind") == "fact"
    ] if isinstance(certificate, dict) and isinstance(certificate.get("nodes"), list) else []
    source_annotation_ids = {
        reference.get("annotation_id")
        for node in fact_nodes
        for reference in (node.get("source_claim_refs") if isinstance(node.get("source_claim_refs"), list) else [])
        if isinstance(reference, dict) and isinstance(reference.get("annotation_id"), str)
    }
    source_annotation_ids.update(
        rule.get("provenance", {}).get("annotation_id")
        for rule_id in used_rule_ids
        for rule in [rules_by_id.get(rule_id)]
        if isinstance(rule, dict)
        and isinstance(rule.get("provenance"), dict)
        and isinstance(rule["provenance"].get("annotation_id"), str)
    )
    source_records_for_proof = [
        records_by_annotation[annotation_id]
        for annotation_id in sorted(source_annotation_ids)
        if annotation_id in records_by_annotation
    ]
    source_payload_verification: dict[str, Any] = {
        "integrity_pass": False,
        "failure_counts": {"source_bundle_root_not_supplied": 1},
    }
    verifier_root = source_bundle_verifier.bundle if source_bundle_verifier is not None else None
    root_conflict = (
        source_bundle_root is not None
        and verifier_root is not None
        and source_bundle_root.resolve() != verifier_root
    )
    if root_conflict:
        source_payload_verification = {
            "integrity_pass": False,
            "failure_counts": {"source_bundle_root_verifier_mismatch": 1},
        }
    elif (source_bundle_verifier is not None or source_bundle_root is not None) and source_records_for_proof:
        try:
            source_payload_verification = verify_annotation_records(
                source_records_for_proof,
                verifier_root or source_bundle_root,
                verifier=source_bundle_verifier,
            )
        except (OSError, ValueError, json.JSONDecodeError):
            source_payload_verification = {
                "integrity_pass": False,
                "failure_counts": {"source_bundle_verification_error": 1},
            }
    elif source_bundle_verifier is not None or source_bundle_root is not None:
        source_payload_verification = {
            "integrity_pass": False,
            "failure_counts": {"no_proof_referenced_annotation_records": 1},
        }
    proof_facts_source_only = bool(fact_nodes) and all(
        node.get("knowledge_partitions") == ["source_assertion"]
        and isinstance(node.get("source_documents"), list)
        and bool(node["source_documents"])
        and all(isinstance(source, str) and source.strip() for source in node["source_documents"])
        for node in fact_nodes
    )
    proof_facts_bound_to_test_source = bool(fact_nodes) and all(
        isinstance(node.get("source_bindings"), list)
        and any(
            isinstance(binding, dict)
            and binding.get("sense_id") == nli_prediction["sense_id"]
            and binding.get("gloss_sha256") == nli_prediction["premise_sha256"].lower()
            and isinstance(binding.get("source_documents"), list)
            and bool(binding["source_documents"])
            and all(isinstance(source, str) and source.strip() for source in binding["source_documents"])
            and set(binding["source_documents"]) <= set(node.get("source_documents", []))
            for binding in node["source_bindings"]
        )
        for node in fact_nodes
    )
    proof_facts_bound_to_reviewed_atoms = bool(fact_nodes) and all(
        _fact_node_has_reviewed_atom_support(
            node, records_by_annotation, program_query, nli_prediction
        )
        for node in fact_nodes
    )
    used_rules_bound_to_test_source = bool(used_rule_ids)
    all_used_rules_reviewed = bool(used_rule_ids)
    nli_claim_matches_proof = False
    for rule_id in used_rule_ids:
        rule = rules_by_id.get(rule_id)
        provenance = rule.get("provenance") if isinstance(rule, dict) else None
        if not isinstance(provenance, dict):
            all_used_rules_reviewed = False
            used_rules_bound_to_test_source = False
            continue
        record = records_by_annotation.get(provenance.get("annotation_id"))
        if not isinstance(record, dict):
            all_used_rules_reviewed = False
            used_rules_bound_to_test_source = False
            continue
        annotation = record.get("annotation") if isinstance(record.get("annotation"), dict) else {}
        source = record.get("source") if isinstance(record.get("source"), dict) else {}
        sense = record.get("sense") if isinstance(record.get("sense"), dict) else {}
        analysis = record.get("analysis") if isinstance(record.get("analysis"), dict) else {}
        claims = analysis.get("rule_claims") if isinstance(analysis.get("rule_claims"), list) else []
        rule_source_matches_test = (
            sense.get("synset_id") == nli_prediction["sense_id"]
            and _same_sha256(source.get("input_sha256"), nli_prediction["premise_sha256"])
        )
        if not rule_source_matches_test:
            used_rules_bound_to_test_source = False
        claim = next((item for item in claims
                      if isinstance(item, dict) and item.get("id") == provenance.get("claim_id")), None)
        source_records = record.get("provenance", {}).get("source_records", [])
        claim_matches = (
            isinstance(claim, dict)
            and claim.get("semantic_support") == "supported"
            and claim.get("confidence") in {"medium", "high"}
            and claim.get("inference_basis") == provenance.get("inference_basis")
            and isinstance(claim.get("inference_basis"), list)
            and bool(claim["inference_basis"])
            and set(claim["inference_basis"]) <= {
                "lexical_or_paraphrastic", "compositional_or_logical",
            }
            and claim.get("relation") == provenance.get("relation")
            and claim.get("direction") == provenance.get("direction")
            and claim.get("evidence_spans") == provenance.get("evidence_spans")
            and sense.get("synset_id") == provenance.get("sense_id")
            and _same_sha256(source.get("input_sha256"), provenance.get("source_gloss_sha256"))
            and source_records == provenance.get("source_records")
            and annotation.get("adjudication_status") == "adjudicated"
        )
        if (
            claim_matches
            and rule_source_matches_test
            and provenance.get("claim_id") == nli_prediction["claim_id"]
            and provenance.get("sense_id") == nli_prediction["sense_id"]
            and _same_sha256(source.get("input_sha256"), nli_prediction["premise_sha256"])
            and _same_sha256(claim.get("nli_hypothesis_sha256"), nli_prediction["hypothesis_sha256"])
        ):
            nli_claim_matches_proof = True
        if not claim_matches:
            all_used_rules_reviewed = False
    source_semantics_reviewed = (
        proof_valid
        and proof_facts_source_only
        and proof_facts_bound_to_test_source
        and proof_facts_bound_to_reviewed_atoms
        and all_used_rules_reviewed
        and used_rules_bound_to_test_source
        and nli_claim_matches_proof
        and source_payload_verification.get("integrity_pass") is True
    )

    routed = route_candidate(
        nli_prediction.get("scores"),
        threshold_selection,
        proof_certificate_valid=proof_valid,
        source_semantics_reviewed=source_semantics_reviewed,
    )
    if (isinstance(proof_result, dict)
            and proof_result.get("status") == "unknown"
            and routed.get("route") == "abstain_missing_or_invalid_proof"):
        routed["route"] = "abstain_unknown_proof_result"
    elif (countermodel_replayed
          and routed.get("route") == "abstain_missing_or_invalid_proof"):
        routed["route"] = "not_entailed_in_supplied_program"
    return {
        **routed,
        "evidence_checks": {
            "test_prediction_split": nli_prediction["split"],
            "test_prediction_sense_matches_query": True,
            "threshold_selected_from_group_disjoint_dev_rows": True,
            "test_gold_label_used": False,
            "proof_status": proof_result.get("status") if isinstance(proof_result, dict) else None,
            "proof_status_reason": proof_result.get("reason_code") if isinstance(proof_result, dict) else None,
            "proof_certificate_replayed": certificate_replayed,
            "countermodel_replayed": countermodel_replayed,
            "typed_program_validation": typed_program_validation,
            "program_rules_match_annotations": program_rules_match_annotations,
            "used_rule_count": len(used_rule_ids),
            "proof_fact_partitions": sorted({
                partition if isinstance(partition, str) else "invalid_partition"
                for node in fact_nodes
                for partition in (
                    node.get("knowledge_partitions")
                    if isinstance(node.get("knowledge_partitions"), list)
                    else ["unclassified"]
                )
            }),
            "all_used_rules_bound_to_adjudicated_supported_claims": all_used_rules_reviewed,
            "source_semantics_gate_passed": source_semantics_reviewed,
            "all_used_rules_bound_to_test_sense_and_gloss": used_rules_bound_to_test_source,
            "all_used_facts_explicitly_tagged_as_source_assertions": proof_facts_source_only,
            "all_used_facts_bound_to_test_sense_and_gloss": proof_facts_bound_to_test_source,
            "all_used_facts_bound_to_adjudicated_gloss_atoms": proof_facts_bound_to_reviewed_atoms,
            "nli_text_pair_hashes_bound_to_proof_claim": nli_claim_matches_proof,
            "source_payloads_independently_verified": source_payload_verification.get("integrity_pass") is True,
            "source_payload_verification": source_payload_verification,
            "development_threshold_selection": threshold_selection,
        },
        "interpretation_limit": (
            "This route binds NLI to a replayed certificate and matching adjudicated annotation records. "
            "The source semantics gate also requires a matching source_bundle_root or reusable source bundle verifier "
            "and a passing byte/hash/index/gloss-field "
            "verification for every annotation record cited by the proof. "
            "It still does not independently establish that the adjudication is correct, that supplied facts are true, "
            "or that NLI calibration transfers beyond the supplied test distribution."
        ),
    }


def route_pipeline_result_from_export(
    result: dict[str, Any],
    records: list[dict[str, Any]],
    target_example_id: str,
    prediction_export_dir: Path,
    expected_export_manifest_sha256: str,
    minimum_precision: float = 0.9,
    precision_confidence_level: float = 0.95,
    source_bundle_root: Path | None = None,
    source_bundle_verifier: AnnotationSourceBundleVerifier | None = None,
) -> dict[str, Any]:
    """Route one test item only from a pinned, hash-verified NLI export.

    The export manifest binds one model identity to both split files. The
    caller must pin the manifest digest independently before routing.
    """
    if not isinstance(target_example_id, str) or not target_example_id:
        raise ValueError("target_example_id must be a non-empty string")
    if (not isinstance(expected_export_manifest_sha256, str)
            or not SHA256_RE.fullmatch(expected_export_manifest_sha256)):
        raise ValueError("expected_export_manifest_sha256 must be a 64-character SHA-256")
    export_dir = Path(prediction_export_dir)
    manifest_path = export_dir / "export_manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    if not _same_sha256(manifest_sha256, expected_export_manifest_sha256):
        raise ValueError("NLI export manifest does not match its externally pinned SHA-256")
    try:
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid NLI export manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "claim-review-nli-export/0.2":
        raise ValueError("unsupported NLI export manifest schema")
    model = manifest.get("model")
    if (not isinstance(model, dict)
            or not isinstance(model.get("id"), str) or not model["id"].strip()
            or not isinstance(model.get("revision"), str) or not model["revision"].strip()):
        raise ValueError("NLI export manifest requires a non-empty model id and immutable revision")
    for field in ("sidecar_sha256", "candidate_manifest_sha256", "model_scores_sha256"):
        if not isinstance(manifest.get(field), str) or not SHA256_RE.fullmatch(manifest[field]):
            raise ValueError(f"NLI export manifest has an invalid {field}")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict) or set(outputs) != {"dev", "test"}:
        raise ValueError("NLI export manifest must bind exactly dev and test prediction files")

    loaded: dict[str, list[dict[str, Any]]] = {}
    for split in ("dev", "test"):
        spec = outputs[split]
        if not isinstance(spec, dict):
            raise ValueError(f"NLI export manifest {split} output must be an object")
        relative_path = spec.get("path")
        if (not isinstance(relative_path, str) or not relative_path
                or Path(relative_path).name != relative_path or relative_path in {".", ".."}):
            raise ValueError(f"NLI export manifest {split} path must be a plain filename")
        expected_rows, expected_sha256 = spec.get("rows"), spec.get("sha256")
        if (isinstance(expected_rows, bool) or not isinstance(expected_rows, int) or expected_rows < 1
                or not isinstance(expected_sha256, str) or not SHA256_RE.fullmatch(expected_sha256)):
            raise ValueError(f"NLI export manifest {split} output has invalid row count or SHA-256")
        output_path = export_dir / relative_path
        if not _same_sha256(hashlib.sha256(output_path.read_bytes()).hexdigest(), expected_sha256):
            raise ValueError(f"NLI export {split} prediction file does not match its manifest SHA-256")
        try:
            rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid NLI export {split} JSONL: {exc}") from exc
        if len(rows) != expected_rows:
            raise ValueError(f"NLI export {split} row count does not match its manifest")
        for index, row in enumerate(rows, start=1):
            if (not isinstance(row, dict) or row.get("split") != split
                    or row.get("model_id") != model["id"]
                    or row.get("model_revision") != model["revision"]):
                raise ValueError(f"NLI export {split} row {index} has a mismatched split or model identity")
        loaded[split] = rows

    matches = [row for row in loaded["test"] if row.get("example_id") == target_example_id]
    if len(matches) != 1:
        raise ValueError("target_example_id must identify exactly one row in the exported test split")
    # Gold labels are kept in the exported file for offline scoring. Remove the
    # target's label before online routing to preserve the no-test-gold contract.
    prediction = {key: value for key, value in matches[0].items() if key != "gold"}
    routed = route_pipeline_result(
        result, records, prediction, loaded["dev"],
        minimum_precision, precision_confidence_level, source_bundle_root, source_bundle_verifier,
    )
    checks = routed.get("evidence_checks")
    if isinstance(checks, dict):
        checks["nli_model_identity_bound_to_pinned_export"] = True
        checks["nli_export_manifest_sha256"] = manifest_sha256
        checks["nli_model_id"] = model["id"]
        checks["nli_model_revision"] = model["revision"]
        checks["test_gold_label_used"] = False
    routed["prediction_export"] = {
        "manifest_sha256": manifest_sha256,
        "development_predictions_sha256": outputs["dev"]["sha256"],
        "test_predictions_sha256": outputs["test"]["sha256"],
    }
    return routed


def route_pipeline_batch_from_export(
    items: list[dict[str, Any]],
    records: list[dict[str, Any]],
    prediction_export_dir: Path,
    expected_export_manifest_sha256: str,
    minimum_precision: float = 0.9,
    precision_confidence_level: float = 0.95,
    source_bundle_root: Path | None = None,
    source_bundle_verifier: AnnotationSourceBundleVerifier | None = None,
) -> dict[str, Any]:
    """Route a batch of precomputed pipeline results against one pinned export.

    Each item is ``{"example_id": str, "pipeline_result": dict}``. Routing
    remains fail-fast: a malformed item or failed integrity gate aborts the
    batch instead of returning a partial result that could be mistaken for a
    complete evaluation. The reusable source-bundle verifier is shared across
    items; the strict export entry point continues to verify the pinned files
    for each item.
    """
    if not isinstance(items, list) or not items:
        raise ValueError("items must be a non-empty list")
    seen_example_ids: set[str] = set()
    normalized_items: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"batch item {index} must be an object")
        example_id = item.get("example_id")
        pipeline_result = item.get("pipeline_result")
        if not isinstance(example_id, str) or not example_id.strip():
            raise ValueError(f"batch item {index} requires a non-empty example_id")
        if example_id in seen_example_ids:
            raise ValueError(f"duplicate batch example_id: {example_id!r}")
        if not isinstance(pipeline_result, dict):
            raise ValueError(f"batch item {index} requires a pipeline_result object")
        seen_example_ids.add(example_id)
        normalized_items.append({"example_id": example_id, "pipeline_result": pipeline_result})

    results = []
    for item in normalized_items:
        routed = route_pipeline_result_from_export(
            item["pipeline_result"], records, item["example_id"],
            prediction_export_dir, expected_export_manifest_sha256,
            minimum_precision, precision_confidence_level,
            source_bundle_root, source_bundle_verifier,
        )
        results.append({"example_id": item["example_id"], "route": routed})

    export_metadata = results[0]["route"].get("prediction_export", {})
    if any(result["route"].get("prediction_export") != export_metadata for result in results[1:]):
        raise RuntimeError("batch routes unexpectedly resolved to different prediction exports")
    return {
        "schema_version": "reviewed-gloss-proof-batch-route/1",
        "pipeline_version": PIPELINE_VERSION,
        "batch_input_sha256": _canonical_json_sha256(normalized_items, "batch items"),
        "annotation_records_sha256": _canonical_json_sha256(records, "annotation records"),
        "prediction_export": export_metadata,
        "item_count": len(results),
        "routes": results,
        "interpretation_limit": (
            "Each route retains the strict single-item proof, source, and NLI checks. "
            "Batch completion does not establish annotation correctness, NLI semantic validity, "
            "or performance beyond the supplied examples."
        ),
    }


def _fact_node_has_reviewed_atom_support(
    node: dict[str, Any],
    records_by_annotation: dict[str, dict[str, Any]],
    query: dict[str, Any],
    nli_prediction: dict[str, Any],
) -> bool:
    """Match a ground source fact to a reviewed gloss atom and its target binding."""
    atom = node.get("atom")
    fact_arguments = atom.get("arguments") if isinstance(atom, dict) else None
    query_arguments = query.get("arguments") if isinstance(query, dict) else None
    references = node.get("source_claim_refs")
    source_documents = node.get("source_documents")
    if (not isinstance(atom, dict) or not isinstance(atom.get("predicate"), str)
            or not isinstance(fact_arguments, list)
            or any(not isinstance(value, str) or not value or value.startswith("?")
                   for value in fact_arguments)
            or not isinstance(query_arguments, list) or len(query_arguments) != 1
            or not isinstance(query_arguments[0], str) or not query_arguments[0]
            or not isinstance(references, list) or not references):
        return False
    if (not isinstance(source_documents, list) or not source_documents
            or any(not isinstance(path, str) or not path.strip() for path in source_documents)):
        return False
    fact_source_paths = set(source_documents)
    referenced_source_paths: set[str] = set()
    for reference in references:
        if not isinstance(reference, dict):
            return False
        record = records_by_annotation.get(reference.get("annotation_id"))
        if not isinstance(record, dict):
            return False
        record_provenance = record.get("provenance") if isinstance(record.get("provenance"), dict) else {}
        source_records = record_provenance.get("source_records")
        if not isinstance(source_records, list) or not source_records:
            return False
        record_source_paths = {
            item["path"] for item in source_records
            if isinstance(item, dict) and isinstance(item.get("path"), str) and item["path"].strip()
        }
        if not record_source_paths or not (fact_source_paths & record_source_paths):
            return False
        referenced_source_paths.update(record_source_paths)
        annotation = record.get("annotation") if isinstance(record.get("annotation"), dict) else {}
        source = record.get("source") if isinstance(record.get("source"), dict) else {}
        sense = record.get("sense") if isinstance(record.get("sense"), dict) else {}
        analysis = record.get("analysis") if isinstance(record.get("analysis"), dict) else {}
        nodes_list = analysis.get("nodes") if isinstance(analysis.get("nodes"), list) else []
        nodes = {item.get("id"): item for item in nodes_list if isinstance(item, dict)
                 and isinstance(item.get("id"), str)}
        claims = analysis.get("rule_claims") if isinstance(analysis.get("rule_claims"), list) else []
        claim = next((item for item in claims if isinstance(item, dict)
                      and item.get("id") == reference.get("claim_id")), None)
        formula_node_id = reference.get("formula_node_id")
        formula_atom = nodes.get(formula_node_id)
        formula_arguments = formula_atom.get("arguments") if isinstance(formula_atom, dict) else None
        claim_formula_ids = (
            _formula_subtree_node_ids(claim.get("formula_node_id"), nodes)
            if isinstance(claim, dict) and isinstance(claim.get("formula_node_id"), str)
            else set()
        )
        claim_formula_kinds = {nodes[node_id].get("kind") for node_id in claim_formula_ids}
        allowed_formula_kinds = (
            {"atom", "and"}
            if isinstance(claim, dict) and claim.get("relation") == "necessary"
            else {"atom", "and", "or"}
        )
        expected_direction = {
            "necessary": "target_to_gloss",
            "sufficient": "gloss_to_target",
            "biconditional": "both",
        }
        bindings = node.get("source_bindings") if isinstance(node.get("source_bindings"), list) else []
        binding_matches_record = any(
            isinstance(binding, dict)
            and binding.get("sense_id") == sense.get("synset_id")
            and binding.get("gloss_sha256") == source.get("input_sha256", "").lower()
            for binding in bindings
        )
        if (annotation.get("adjudication_status") != "adjudicated"
                or sense.get("synset_id") != query.get("predicate", "").removeprefix("wn_sense:")
                or source.get("input_sha256", "").lower() != nli_prediction.get("premise_sha256", "").lower()
                or not binding_matches_record
                or not isinstance(claim, dict)
                or claim.get("semantic_support") != "supported"
                or claim.get("confidence") not in {"medium", "high"}
                or claim.get("relation") not in expected_direction
                or claim.get("direction") != expected_direction.get(claim.get("relation"))
                or not isinstance(claim.get("inference_basis"), list)
                or not claim["inference_basis"]
                or not set(claim["inference_basis"]) <= {
                    "lexical_or_paraphrastic", "compositional_or_logical",
                }
                or formula_node_id not in claim_formula_ids
                or not claim_formula_kinds
                or not claim_formula_kinds <= allowed_formula_kinds
                or not isinstance(formula_atom, dict)
                or formula_atom.get("kind") != "atom"
                or formula_atom.get("predicate") != atom["predicate"]
                or not isinstance(formula_arguments, list)
                or len(formula_arguments) != len(fact_arguments)):
            return False
        variable_bindings: dict[str, str] = {}
        for formula_term, fact_term in zip(formula_arguments, fact_arguments):
            if not isinstance(formula_term, dict) or formula_term.get("kind") not in {"variable", "constant"}:
                return False
            identifier = formula_term.get("id")
            if not isinstance(identifier, str) or not identifier:
                return False
            if formula_term["kind"] == "constant":
                if identifier.startswith("?") or identifier != fact_term:
                    return False
                continue
            if not identifier.startswith("?"):
                return False
            previous = variable_bindings.setdefault(identifier, fact_term)
            if previous != fact_term:
                return False
        if record.get("schema_version") == "0.7-draft":
            target_variable = claim.get("target_variable")
        else:
            # The legacy compiler only permits unary atoms over one shared
            # variable, so its target can be recovered from this source atom.
            target_variable = (
                formula_arguments[0].get("id")
                if len(formula_arguments) == 1
                and isinstance(formula_arguments[0], dict)
                and formula_arguments[0].get("kind") == "variable"
                else None
            )
        if (not isinstance(target_variable, str)
                or variable_bindings.get(target_variable) != query_arguments[0]):
            return False
    return fact_source_paths <= referenced_source_paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotations", type=Path, help="validated canonical annotation JSONL")
    parser.add_argument("problem", type=Path, help="JSON object with ground facts and one ground query")
    parser.add_argument("--output", type=Path, required=True, help="self-contained result and replay program JSON")
    parser.add_argument("--force", action="store_true", help="replace an existing result")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        records, _, parse_errors = load_jsonl(args.annotations)
        if parse_errors:
            raise ValueError("invalid annotation JSONL: " + "; ".join(parse_errors[:5]))
        problem_bytes = args.problem.read_bytes()
        problem = json.loads(problem_bytes.decode("utf-8"))
        result = run_pipeline(
            records,
            problem,
            annotation_sha256=hashlib.sha256(args.annotations.read_bytes()).hexdigest(),
            problem_sha256=hashlib.sha256(problem_bytes).hexdigest(),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Proof status: {result['proof_result']['status']}")
    print(f"Compiled rules: {result['compilation']['compiled_rule_count']}; rejected claims: {result['compilation']['rejection_count']}")
    print(f"Replayable result: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
