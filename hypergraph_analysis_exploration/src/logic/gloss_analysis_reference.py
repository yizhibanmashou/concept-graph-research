"""Validate adjudicated alternative analyses for WordNet gloss annotations.

The reference sidecar keeps whole analyses separate from semantic OR nodes in
the annotation AST. Annotation hashes use canonical JSON bytes, not JSONL line
bytes, so the same record has one identity independent of whitespace/order.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from src.logic.annotation_validator import ANALYSIS_STATUSES, load_jsonl, validate_dataset


SCHEMA_VERSION = "gloss-analysis-reference/0.2"
ADJUDICATION_STATUSES = {"complete", "unresolved"}
UNRESOLVED_REASON_CODES = {
    "annotator_disagreement", "semantic_ambiguity", "scope_or_reference_ambiguity",
    "insufficient_evidence", "other",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REFERENCE_FIELDS = {
    "schema_version", "item_id", "source_gloss_sha256", "adjudication_status",
    "adjudicator_id", "accepted_alternatives", "unresolved_candidates", "notes",
}
ALTERNATIVE_FIELDS = {
    "alternative_id", "annotation_record_sha256", "analysis_status",
    "root_node_ids", "rule_claim_ids", "rationale",
}
UNRESOLVED_FIELDS = {
    "candidate_id", "annotation_record_sha256", "reason_code", "rationale",
}
SOURCE_IDENTITY_FIELDS = ("resource", "version", "record_id", "license", "input_sha256")
SENSE_IDENTITY_FIELDS = ("synset_id", "lemmas", "pos", "gloss")


def canonical_annotation_record_sha256(record: dict[str, Any]) -> str:
    """Hash one annotation record's canonical JSON representation."""
    payload = json.dumps(
        record, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def annotation_source_sense_identity(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return the immutable source/sense fields that define an annotation item."""
    source = record.get("source", {})
    sense = record.get("sense", {})
    return {
        "source": {key: source.get(key) for key in SOURCE_IDENTITY_FIELDS},
        "sense": {key: sense.get(key) for key in SENSE_IDENTITY_FIELDS},
    }


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _strict_fields(value: Any, expected: set[str], label: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return False
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    if missing:
        errors.append(f"{label} missing fields: {missing}")
    if extra:
        errors.append(f"{label} has unsupported fields: {extra}")
    return not missing and not extra


def _validated_record_index(
    annotation_records: list[dict[str, Any]], line_numbers: list[int] | None = None
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors = validate_dataset(annotation_records, line_numbers)
    by_hash: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(annotation_records, start=1):
        try:
            digest = canonical_annotation_record_sha256(record)
        except (TypeError, ValueError) as exc:
            errors.append(f"annotation record {index}: cannot canonicalize JSON: {exc}")
            continue
        if digest in by_hash:
            errors.append(f"annotation record {index}: duplicate canonical record hash {digest}")
        else:
            by_hash[digest] = record
    return by_hash, errors


def validate_reference_record(
    reference: Any, annotation_records_by_hash: dict[str, dict[str, Any]], where: str = "reference"
) -> list[str]:
    errors: list[str] = []
    if not _strict_fields(reference, REFERENCE_FIELDS, where, errors):
        return errors
    if reference.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{where}.schema_version must be {SCHEMA_VERSION!r}")
    if not _nonempty(reference.get("item_id")):
        errors.append(f"{where}.item_id must be a non-empty string")
    if not _sha256(reference.get("source_gloss_sha256")):
        errors.append(f"{where}.source_gloss_sha256 must be a lowercase SHA-256")
    if not isinstance(reference.get("adjudication_status"), str) or reference.get("adjudication_status") not in ADJUDICATION_STATUSES:
        errors.append(f"{where}.adjudication_status must be one of {sorted(ADJUDICATION_STATUSES)}")
    if not _nonempty(reference.get("adjudicator_id")):
        errors.append(f"{where}.adjudicator_id must be a non-empty pseudonymous identifier")
    if not isinstance(reference.get("notes"), list) or any(not isinstance(note, str) for note in reference["notes"]):
        errors.append(f"{where}.notes must be a list of strings")

    accepted = reference.get("accepted_alternatives")
    if not isinstance(accepted, list):
        errors.append(f"{where}.accepted_alternatives must be a list")
        accepted = []
    unresolved = reference.get("unresolved_candidates")
    if not isinstance(unresolved, list):
        errors.append(f"{where}.unresolved_candidates must be a list")
        unresolved = []
    if reference.get("adjudication_status") == "complete" and not accepted:
        errors.append(f"{where}: complete adjudication requires at least one accepted alternative")
    if reference.get("adjudication_status") == "complete" and unresolved:
        errors.append(
            f"{where}: complete adjudication cannot retain unresolved candidates; "
            "mark the item unresolved until all candidate analyses are adjudicated"
        )
    if reference.get("adjudication_status") == "unresolved" and (accepted or not unresolved):
        errors.append(f"{where}: unresolved adjudication requires candidates and no accepted alternatives")

    seen_alternative_ids: set[str] = set()
    seen_candidate_ids: set[str] = set()
    source_hash = reference.get("source_gloss_sha256")
    item_id = reference.get("item_id")
    adjudicator_id = reference.get("adjudicator_id")
    linked_identity: dict[str, dict[str, Any]] | None = None

    def check_record_link(digest: Any, label: str) -> dict[str, Any] | None:
        nonlocal linked_identity
        if not _sha256(digest):
            errors.append(f"{label}.annotation_record_sha256 must be a lowercase SHA-256")
            return None
        record = annotation_records_by_hash.get(digest)
        if record is None:
            errors.append(f"{label} references an annotation record absent from the supplied record set")
            return None
        source = record.get("source", {})
        sense = record.get("sense", {})
        annotation = record.get("annotation", {})
        analysis = record.get("analysis", {})
        if not all(isinstance(value, dict) for value in (source, sense, annotation, analysis)):
            errors.append(f"{label} annotation record has malformed source/sense/annotation/analysis objects")
            return record
        if record.get("item_id") != item_id:
            errors.append(f"{label} item_id does not match its annotation record")
        if source.get("input_sha256") != source_hash:
            errors.append(f"{label} gloss hash does not match its annotation record")
        if isinstance(sense.get("gloss"), str):
            expected = hashlib.sha256(sense["gloss"].encode("utf-8")).hexdigest()
            if expected != source_hash:
                errors.append(f"{where}.source_gloss_sha256 does not match the exact raw gloss")
        current_identity = annotation_source_sense_identity(record)
        if linked_identity is None:
            linked_identity = current_identity
        elif current_identity != linked_identity:
            errors.append(
                f"{label} source/sense identity differs from other annotation records linked to item_id {item_id!r}"
            )
        return record

    for index, alternative in enumerate(accepted):
        label = f"{where}.accepted_alternatives[{index}]"
        if not _strict_fields(alternative, ALTERNATIVE_FIELDS, label, errors):
            continue
        alternative_id = alternative.get("alternative_id")
        if not _nonempty(alternative_id):
            errors.append(f"{label}.alternative_id must be a non-empty string")
        elif alternative_id in seen_alternative_ids:
            errors.append(f"{label}.alternative_id is duplicated")
        else:
            seen_alternative_ids.add(alternative_id)
        analysis_status = alternative.get("analysis_status")
        if not isinstance(analysis_status, str) or analysis_status not in ANALYSIS_STATUSES:
            errors.append(f"{label}.analysis_status must be one of {sorted(ANALYSIS_STATUSES)}")
        if not _nonempty(alternative.get("rationale")):
            errors.append(f"{label}.rationale must explain why the full analysis is admissible")
        record = check_record_link(alternative.get("annotation_record_sha256"), label)
        if record is None:
            continue
        if annotation.get("adjudication_status") != "adjudicated":
            errors.append(f"{label} must reference an annotation record marked adjudicated")
        if annotation.get("annotator_id") != adjudicator_id:
            errors.append(f"{label} annotator_id must match the sidecar adjudicator_id")
        if analysis.get("status") != analysis_status:
            errors.append(f"{label}.analysis_status does not match the referenced annotation record")
        root_ids = alternative.get("root_node_ids")
        if not isinstance(root_ids, list) or any(not _nonempty(node_id) for node_id in root_ids):
            errors.append(f"{label}.root_node_ids must be a list of node IDs")
            root_ids = []
        if len(root_ids) != len(set(root_ids)):
            errors.append(f"{label}.root_node_ids must not contain duplicates")
        record_root_ids = analysis.get("root_node_ids", [])
        if not isinstance(record_root_ids, list) or any(not isinstance(node_id, str) for node_id in record_root_ids):
            errors.append(f"{label} referenced analysis has malformed root_node_ids")
            record_root_ids = []
        if set(root_ids) != set(record_root_ids):
            errors.append(f"{label}.root_node_ids must preserve the full referenced analysis roots")
        claim_ids = alternative.get("rule_claim_ids")
        if not isinstance(claim_ids, list) or any(not _nonempty(claim_id) for claim_id in claim_ids):
            errors.append(f"{label}.rule_claim_ids must be a list of claim IDs")
            claim_ids = []
        if len(claim_ids) != len(set(claim_ids)):
            errors.append(f"{label}.rule_claim_ids must not contain duplicates")
        claims = analysis.get("rule_claims", [])
        if not isinstance(claims, list):
            errors.append(f"{label} referenced analysis has malformed rule_claims")
            claims = []
        claims_by_id = {claim.get("id"): claim for claim in claims if isinstance(claim, dict)}
        missing_claim_ids = sorted(set(claim_ids) - claims_by_id.keys())
        if missing_claim_ids:
            errors.append(f"{label}.rule_claim_ids not found in referenced record: {missing_claim_ids}")
        for claim_id in set(claim_ids) & claims_by_id.keys():
            if claims_by_id[claim_id].get("semantic_support") != "supported":
                errors.append(f"{label} includes claim {claim_id!r} not adjudicated as supported")
        if analysis_status == "annotated" and not root_ids:
            errors.append(f"{label}: annotated alternative must include at least one root")

    for index, candidate in enumerate(unresolved):
        label = f"{where}.unresolved_candidates[{index}]"
        if not _strict_fields(candidate, UNRESOLVED_FIELDS, label, errors):
            continue
        candidate_id = candidate.get("candidate_id")
        if not _nonempty(candidate_id):
            errors.append(f"{label}.candidate_id must be a non-empty string")
        elif candidate_id in seen_candidate_ids:
            errors.append(f"{label}.candidate_id is duplicated")
        else:
            seen_candidate_ids.add(candidate_id)
        if not isinstance(candidate.get("reason_code"), str) or candidate.get("reason_code") not in UNRESOLVED_REASON_CODES:
            errors.append(f"{label}.reason_code must be one of {sorted(UNRESOLVED_REASON_CODES)}")
        if not _nonempty(candidate.get("rationale")):
            errors.append(f"{label}.rationale must be non-empty")
        check_record_link(candidate.get("annotation_record_sha256"), label)

    return errors


def validate_reference_dataset(
    references: list[dict[str, Any]], annotation_records: list[dict[str, Any]],
    reference_line_numbers: list[int] | None = None, annotation_line_numbers: list[int] | None = None,
) -> list[str]:
    by_hash, errors = _validated_record_index(annotation_records, annotation_line_numbers)
    seen_items: set[str] = set()
    for index, reference in enumerate(references, start=1):
        line = reference_line_numbers[index - 1] if reference_line_numbers else index
        where = f"reference line {line}"
        errors.extend(validate_reference_record(reference, by_hash, where))
        if isinstance(reference, dict):
            item_id = reference.get("item_id")
            if isinstance(item_id, str):
                if item_id in seen_items:
                    errors.append(f"{where}: duplicate sidecar for item_id {item_id!r}")
                seen_items.add(item_id)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("references", type=Path, help=f"{SCHEMA_VERSION} JSONL")
    parser.add_argument("annotation_records", type=Path, help="adjudicated annotation JSONL records referenced by sidecars")
    args = parser.parse_args(argv)
    try:
        references, reference_lines, reference_errors = load_jsonl(args.references)
        records, record_lines, record_errors = load_jsonl(args.annotation_records)
        if reference_errors or record_errors:
            raise ValueError("invalid JSONL: " + "; ".join((reference_errors + record_errors)[:8]))
        errors = validate_reference_dataset(references, records, reference_lines, record_lines)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    if errors:
        print("Gloss analysis reference validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Valid {SCHEMA_VERSION} sidecars: {len(references)} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
