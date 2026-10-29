"""Validate draft pair-level annotations for instance-to-class relation review.

This structural validator binds two sense records, their separate gloss spans,
and two distinct judgments. It does not decide relation truth or gloss support.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "wordnet-instance-relation-annotation/0.2-draft"
POS_VALUES = {"n", "v", "a", "s", "r"}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
CONFIDENCE_VALUES = {"high", "medium", "low"}
RELATION_LABELS = {"yes", "no", "uncertain", "cannot_determine"}
RELATION_BASES = {
    "gloss_only", "lexical_or_paraphrastic", "external_world_knowledge",
    "insufficient_context", "unclear",
}
GLOSS_SUPPORT_VALUES = {"supported", "not_supported", "uncertain", "unassessed"}
INFERENCE_BASIS_VALUES = {
    "lexical_or_paraphrastic", "compositional_or_logical",
    "external_world_knowledge", "pragmatic_or_conversational",
    "figurative_or_metaphorical", "unclear", "unassessed",
}
SUPPORT_REASON_VALUES = {
    "content_not_licensed", "claim_overstates_or_omits_qualifier",
    "direction_mismatch", "operator_or_scope_mismatch", "source_conflict",
    "lexical_or_sense_ambiguity", "scope_or_reference_ambiguity",
    "insufficient_context", "other",
}
NOT_SUPPORTED_REASONS = {
    "content_not_licensed", "claim_overstates_or_omits_qualifier",
    "direction_mismatch", "operator_or_scope_mismatch", "source_conflict", "other",
}
UNCERTAIN_REASONS = {
    "lexical_or_sense_ambiguity", "scope_or_reference_ambiguity",
    "insufficient_context", "other",
}
ADJUDICATION_STATUSES = {"independent", "adjudicated", "unresolved"}
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _choice(value: Any, choices: set[str]) -> bool:
    return isinstance(value, str) and value in choices


def _sha256_matches(value: Any, text: str) -> bool:
    return (isinstance(value, str) and SHA256_RE.fullmatch(value) is not None
            and value.lower() == hashlib.sha256(text.encode("utf-8")).hexdigest())


def _object(value: Any, keys: set[str], where: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{where} must be an object")
        return {}
    missing = keys - set(value)
    extra = set(value) - keys
    if missing:
        errors.append(f"{where} is missing fields: {sorted(missing)}")
    if extra:
        errors.append(f"{where} has unsupported fields: {sorted(extra)}")
    return value


def _sense(value: Any, side: str, errors: list[str]) -> dict[str, Any]:
    where = f"{side}_sense"
    sense = _object(value, {"synset_id", "lemmas", "pos", "gloss", "gloss_sha256"}, where, errors)
    if not _nonempty(sense.get("synset_id")):
        errors.append(f"{where}.synset_id must be a non-empty string")
    lemmas = sense.get("lemmas")
    valid_lemmas = isinstance(lemmas, list) and bool(lemmas) and all(_nonempty(x) for x in lemmas)
    if valid_lemmas and len(lemmas) != len(set(lemmas)):
        valid_lemmas = False
    if not valid_lemmas:
        errors.append(f"{where}.lemmas must be a non-empty list of unique non-empty strings")
    if not _choice(sense.get("pos"), POS_VALUES):
        errors.append(f"{where}.pos must be one of {sorted(POS_VALUES)}")
    gloss = sense.get("gloss")
    if not _nonempty(gloss):
        errors.append(f"{where}.gloss must be a non-empty string")
        gloss = ""
    if not _sha256_matches(sense.get("gloss_sha256"), gloss):
        errors.append(f"{where}.gloss_sha256 must match the UTF-8 SHA-256 of its own gloss")
    return sense


def _spans(value: Any, gloss: str, where: str, errors: list[str]) -> list[dict[str, int]]:
    if not isinstance(value, list):
        errors.append(f"{where} must be a list")
        return []
    spans: list[dict[str, int]] = []
    for index, span in enumerate(value):
        label = f"{where}[{index}]"
        if not isinstance(span, dict) or set(span) != {"start", "end"}:
            errors.append(f"{label} must contain exactly integer start and end")
            continue
        start, end = span.get("start"), span.get("end")
        if type(start) is not int or type(end) is not int:
            errors.append(f"{label} start and end must be integers")
        elif start < 0 or end <= start or end > len(gloss):
            errors.append(f"{label} must satisfy 0 <= start < end <= gloss length ({len(gloss)} code points)")
        else:
            spans.append({"start": start, "end": end})
    return spans


def _pair_spans(value: Any, instance_gloss: str, class_gloss: str,
                where: str, errors: list[str]) -> tuple[list[dict[str, int]], list[dict[str, int]]]:
    obj = _object(value, {"instance_gloss", "class_gloss"}, where, errors)
    return (
        _spans(obj.get("instance_gloss"), instance_gloss, f"{where}.instance_gloss", errors),
        _spans(obj.get("class_gloss"), class_gloss, f"{where}.class_gloss", errors),
    )


def validate_record(record: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    required = {"schema_version", "item_id", "annotation_id", "source", "instance_sense",
                "class_sense", "relation_claim", "judgments", "annotation"}
    _object(record, required, "record", errors)
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION!r}")
    for field in ("item_id", "annotation_id"):
        if not _nonempty(record.get(field)):
            errors.append(f"{field} must be a non-empty string")

    source = _object(record.get("source"),
                     {"resource", "version", "license", "archive_sha256"}, "source", errors)
    for field in ("resource", "version", "license"):
        if not _nonempty(source.get(field)):
            errors.append(f"source.{field} must be a non-empty string")
    if not isinstance(source.get("archive_sha256"), str) or not SHA256_RE.fullmatch(source["archive_sha256"]):
        errors.append("source.archive_sha256 must be a 64-character hexadecimal SHA-256")

    instance = _sense(record.get("instance_sense"), "instance", errors)
    class_sense = _sense(record.get("class_sense"), "class", errors)
    if instance.get("synset_id") == class_sense.get("synset_id") and _nonempty(instance.get("synset_id")):
        errors.append("instance_sense.synset_id and class_sense.synset_id must differ")
    instance_gloss = instance.get("gloss") if isinstance(instance.get("gloss"), str) else ""
    class_gloss = class_sense.get("gloss") if isinstance(class_sense.get("gloss"), str) else ""

    claim = _object(record.get("relation_claim"), {"predicate", "direction"}, "relation_claim", errors)
    if claim.get("predicate") != "instance_of":
        errors.append("relation_claim.predicate must be 'instance_of'")
    if claim.get("direction") != "instance_to_class":
        errors.append("relation_claim.direction must be 'instance_to_class'")

    judgments = _object(record.get("judgments"), {"sense_relation", "gloss_support"}, "judgments", errors)
    relation = _object(judgments.get("sense_relation"),
                       {"label", "basis", "evidence_spans", "rationale", "confidence"},
                       "judgments.sense_relation", errors)
    if not _choice(relation.get("label"), RELATION_LABELS):
        errors.append(f"judgments.sense_relation.label must be one of {sorted(RELATION_LABELS)}")
    relation_basis = relation.get("basis")
    valid_relation_basis = (isinstance(relation_basis, list) and bool(relation_basis)
                            and all(_choice(item, RELATION_BASES) for item in relation_basis))
    if valid_relation_basis and len(relation_basis) != len(set(relation_basis)):
        valid_relation_basis = False
    if not valid_relation_basis:
        errors.append(f"judgments.sense_relation.basis must be a non-empty unique list from {sorted(RELATION_BASES)}")
    relation_evidence = _pair_spans(
        relation.get("evidence_spans"), instance_gloss, class_gloss,
        "judgments.sense_relation.evidence_spans", errors,
    )
    if (isinstance(relation_basis, list) and "gloss_only" in relation_basis
            and not all(relation_evidence)):
        errors.append("gloss_only sense_relation requires at least one span in each source gloss")
    if not _choice(relation.get("confidence"), CONFIDENCE_VALUES):
        errors.append(f"judgments.sense_relation.confidence must be one of {sorted(CONFIDENCE_VALUES)}")
    if not _nonempty(relation.get("rationale")):
        errors.append("judgments.sense_relation.rationale must be a non-empty string")

    support = _object(judgments.get("gloss_support"),
                      {"status", "inference_basis", "support_reasons", "evidence_spans",
                       "rationale", "confidence"},
                      "judgments.gloss_support", errors)
    status = support.get("status")
    if not _choice(status, GLOSS_SUPPORT_VALUES):
        errors.append(f"judgments.gloss_support.status must be one of {sorted(GLOSS_SUPPORT_VALUES)}")
    basis = support.get("inference_basis")
    valid_basis = isinstance(basis, list) and bool(basis) and all(
        _choice(item, INFERENCE_BASIS_VALUES) for item in basis
    )
    if valid_basis and len(basis) != len(set(basis)):
        valid_basis = False
    if not valid_basis:
        errors.append("judgments.gloss_support.inference_basis must be a non-empty unique list of valid basis codes")
    reasons = support.get("support_reasons")
    if not isinstance(reasons, list) or any(not _choice(item, SUPPORT_REASON_VALUES) for item in reasons):
        errors.append("judgments.gloss_support.support_reasons must be a list of valid reason codes")
        reasons = []
    elif len(reasons) != len(set(reasons)):
        errors.append("judgments.gloss_support.support_reasons must not contain duplicates")
    evidence = _pair_spans(support.get("evidence_spans"), instance_gloss, class_gloss,
                           "judgments.gloss_support.evidence_spans", errors)
    if status == "supported":
        if not all(evidence):
            errors.append("supported gloss_support requires at least one span in each source gloss")
        if isinstance(basis, list) and any(not _choice(item, {"lexical_or_paraphrastic", "compositional_or_logical"})
                                           for item in basis):
            errors.append("supported gloss_support basis must be gloss-grounded lexical/compositional only")
        if reasons:
            errors.append("supported gloss_support must have an empty support_reasons list")
    elif _choice(status, {"not_supported", "uncertain"}):
        if not reasons:
            errors.append(f"{status} gloss_support requires at least one support reason")
        allowed = NOT_SUPPORTED_REASONS if status == "not_supported" else UNCERTAIN_REASONS
        if any(reason not in allowed for reason in reasons):
            errors.append(f"{status} gloss_support contains a reason code not allowed for that status")
    elif status == "unassessed":
        if basis != ["unassessed"]:
            errors.append("unassessed gloss_support must use inference_basis ['unassessed']")
        if reasons or any(evidence):
            errors.append("unassessed gloss_support must not contain reasons or evidence spans")
    if not _choice(support.get("confidence"), CONFIDENCE_VALUES):
        errors.append(f"judgments.gloss_support.confidence must be one of {sorted(CONFIDENCE_VALUES)}")
    if not _nonempty(support.get("rationale")):
        errors.append("judgments.gloss_support.rationale must be a non-empty string")

    annotation = _object(record.get("annotation"),
                         {"annotator_id", "adjudication_status", "notes"}, "annotation", errors)
    if not _nonempty(annotation.get("annotator_id")):
        errors.append("annotation.annotator_id must be a non-empty string")
    if not _choice(annotation.get("adjudication_status"), ADJUDICATION_STATUSES):
        errors.append(f"annotation.adjudication_status must be one of {sorted(ADJUDICATION_STATUSES)}")
    notes = annotation.get("notes")
    if not isinstance(notes, list) or any(not isinstance(note, str) for note in notes):
        errors.append("annotation.notes must be a list of strings")
    return errors


def validate_dataset(records: list[Any], line_numbers: list[int] | None = None) -> list[str]:
    errors: list[str] = []
    if line_numbers is None:
        line_numbers = list(range(1, len(records) + 1))
    seen_annotation_ids: set[str] = set()
    seen_item_annotators: set[tuple[str, str]] = set()
    item_source_pair: dict[str, tuple[str, str, str]] = {}
    for index, record in enumerate(records):
        line = line_numbers[index] if index < len(line_numbers) else index + 1
        for message in validate_record(record):
            errors.append(f"line {line}: {message}")
        if not isinstance(record, dict):
            continue
        annotation_id = record.get("annotation_id")
        if isinstance(annotation_id, str):
            if annotation_id in seen_annotation_ids:
                errors.append(f"line {line}: duplicate annotation_id {annotation_id!r}")
            seen_annotation_ids.add(annotation_id)
        item_id = record.get("item_id")
        annotation = record.get("annotation")
        annotator = annotation.get("annotator_id") if isinstance(annotation, dict) else None
        if isinstance(item_id, str) and isinstance(annotator, str):
            pair_key = (item_id, annotator)
            if pair_key in seen_item_annotators:
                errors.append(f"line {line}: duplicate annotation for item_id/annotator_id {pair_key!r}")
            seen_item_annotators.add(pair_key)
        instance = record.get("instance_sense")
        class_sense = record.get("class_sense")
        source = record.get("source")
        if (isinstance(item_id, str) and isinstance(instance, dict) and isinstance(class_sense, dict)
                and isinstance(source, dict)):
            identity = (
                instance.get("synset_id"), class_sense.get("synset_id"),
                source.get("resource"), source.get("version"), source.get("license"),
                source.get("archive_sha256"),
            )
            previous = item_source_pair.get(item_id)
            if previous is not None and previous != identity:
                errors.append(f"line {line}: item_id {item_id!r} is bound to inconsistent sense pair/source release")
            item_source_pair[item_id] = identity
    return errors


def load_jsonl(path: Path) -> tuple[list[Any], list[int], list[str]]:
    records: list[Any] = []
    line_numbers: list[int] = []
    errors: list[str] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
                line_numbers.append(line_number)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON ({exc.msg})")
    return records, line_numbers, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path, help="pair annotation JSONL")
    args = parser.parse_args(argv)
    try:
        records, line_numbers, parse_errors = load_jsonl(args.jsonl)
    except OSError as exc:
        parser.error(str(exc))
    errors = parse_errors + validate_dataset(records, line_numbers)
    if errors:
        print(f"Invalid pair annotations: {len(errors)} error(s)")
        for error in errors[:25]:
            print(f"- {error}")
        return 1
    print(f"Valid pair annotations: {len(records)} records; schema={SCHEMA_VERSION}")
    print("Structural validation only; no relation truth or gloss-support semantics were evaluated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
