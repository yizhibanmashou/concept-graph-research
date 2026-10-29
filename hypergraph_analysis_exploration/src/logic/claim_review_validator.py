"""Validate claim-review JSONL sidecars before NLI evaluation export.

This checks record structure, byte-exact text hashes, evidence span bounds,
annotation-state consistency, and split/group hygiene. It does not validate
the semantic correctness of any human judgment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "claim-review-record/0.1"
SPLITS = {"train", "dev", "test", "unassigned"}
NLI_STATUSES = {"adjudicated", "uncertain", "unassessed"}
NLI_LABELS = {"entailment", "neutral", "contradiction"}
SUPPORT = {"supported", "not_supported", "uncertain", "unassessed"}
BASES = {
    "lexical_or_paraphrastic", "compositional_or_logical",
    "external_world_knowledge", "pragmatic_or_conversational",
    "figurative_or_metaphorical", "unclear", "unassessed",
}
REASONS = {
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
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TOP_LEVEL_KEYS = {
    "schema_version", "candidate_id", "candidate_set_version", "group_id", "split",
    "source", "premise", "premise_sha256", "hypothesis", "hypothesis_sha256",
    "direction", "relation", "formula_sha256", "nli_relation_status",
    "nli_relation_gold", "semantic_support", "inference_basis", "support_reasons",
    "evidence_spans", "annotation",
}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _hash_matches(value: Any, expected_text: str) -> bool:
    return (isinstance(value, str) and SHA256_RE.fullmatch(value) is not None
            and value == hashlib.sha256(expected_text.encode("utf-8")).hexdigest())


def validate_record(row: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(row, dict):
        return ["record must be a JSON object"]
    extra = set(row) - TOP_LEVEL_KEYS
    if extra:
        errors.append(f"unexpected top-level fields: {sorted(extra)}")
    missing = {"schema_version", "candidate_id", "candidate_set_version", "group_id", "split",
               "source", "premise", "premise_sha256", "hypothesis", "hypothesis_sha256",
               "direction", "nli_relation_status", "semantic_support", "inference_basis",
               "evidence_spans", "annotation"} - set(row)
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")

    for key in ("candidate_id", "candidate_set_version", "group_id"):
        if not _nonempty(row.get(key)):
            errors.append(f"{key} must be a non-empty string")
    if row.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    if not isinstance(row.get("split"), str) or row["split"] not in SPLITS:
        errors.append(f"split must be one of {sorted(SPLITS)}")

    source = row.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
        source = {}
    elif set(source) - {"resource", "release", "sense_id", "pos", "gloss_sha256"}:
        errors.append(f"source has unexpected fields: {sorted(set(source) - {'resource', 'release', 'sense_id', 'pos', 'gloss_sha256'})}")
    for key in ("resource", "release", "sense_id"):
        if not _nonempty(source.get(key)):
            errors.append(f"source.{key} must be a non-empty string")
    if not isinstance(source.get("pos"), str) or source["pos"] not in {"n", "v", "a", "r"}:
        errors.append("source.pos must be one of ['a', 'n', 'r', 'v']")

    premise, hypothesis = row.get("premise"), row.get("hypothesis")
    if not _nonempty(premise):
        errors.append("premise must be a non-empty string")
    if not _nonempty(hypothesis):
        errors.append("hypothesis must be a non-empty string")
    if isinstance(premise, str):
        if not _hash_matches(row.get("premise_sha256"), premise):
            errors.append("premise_sha256 does not match UTF-8 SHA-256 of premise")
        if not _hash_matches(source.get("gloss_sha256"), premise):
            errors.append("source.gloss_sha256 does not match UTF-8 SHA-256 of premise")
    if isinstance(hypothesis, str) and not _hash_matches(row.get("hypothesis_sha256"), hypothesis):
        errors.append("hypothesis_sha256 does not match UTF-8 SHA-256 of hypothesis")

    if not isinstance(row.get("direction"), str) or row["direction"] not in {"target_to_gloss", "gloss_to_target", "both", "none"}:
        errors.append("direction must be target_to_gloss|gloss_to_target|both|none")
    if "relation" in row and (not isinstance(row["relation"], str) or row["relation"] not in {"necessary", "sufficient", "biconditional", "typical", "example", "other"}):
        errors.append("relation has an unsupported value")
    if "formula_sha256" in row and not (isinstance(row["formula_sha256"], str) and SHA256_RE.fullmatch(row["formula_sha256"])):
        errors.append("formula_sha256 must be a lowercase 64-character SHA-256")

    nli_status = row.get("nli_relation_status")
    if not isinstance(nli_status, str) or nli_status not in NLI_STATUSES:
        errors.append(f"nli_relation_status must be one of {sorted(NLI_STATUSES)}")
    nli_gold = row.get("nli_relation_gold")
    if nli_status == "adjudicated":
        if not isinstance(nli_gold, str) or nli_gold not in NLI_LABELS:
            errors.append(f"adjudicated nli_relation_status requires nli_relation_gold in {sorted(NLI_LABELS)}")
    elif "nli_relation_gold" in row:
        errors.append("nli_relation_gold is forbidden unless nli_relation_status is adjudicated")

    support = row.get("semantic_support")
    if not isinstance(support, str) or support not in SUPPORT:
        errors.append(f"semantic_support must be one of {sorted(SUPPORT)}")
    basis = row.get("inference_basis")
    if (not isinstance(basis, list) or not basis
            or any(not isinstance(value, str) or value not in BASES for value in basis)):
        errors.append(f"inference_basis must be a non-empty list from {sorted(BASES)}")
    elif len(set(basis)) != len(basis):
        errors.append("inference_basis must not contain duplicates")
    elif "unclear" in basis and len(basis) != 1:
        errors.append("inference_basis='unclear' must be the only value when present")
    elif "unassessed" in basis and (len(basis) != 1 or support != "unassessed"):
        errors.append("inference_basis='unassessed' must be alone and semantic_support must be unassessed")
    elif support == "unassessed" and basis != ["unassessed"]:
        errors.append("semantic_support=unassessed requires inference_basis=['unassessed']")

    reasons = row.get("support_reasons", [])
    if not isinstance(reasons, list) or any(not isinstance(reason, str) or reason not in REASONS for reason in reasons):
        errors.append(f"support_reasons must be a list of values from {sorted(REASONS)}")
    elif len(set(reasons)) != len(reasons):
        errors.append("support_reasons must not contain duplicates")
    elif isinstance(support, str) and support in {"not_supported", "uncertain"}:
        allowed = NOT_SUPPORTED_REASONS if support == "not_supported" else UNCERTAIN_REASONS
        if not reasons or any(reason not in allowed for reason in reasons):
            errors.append(f"support_reasons must be non-empty and compatible with semantic_support={support!r}")
    elif reasons and isinstance(support, str):
        errors.append(f"support_reasons must be empty when semantic_support={support!r}")

    spans = row.get("evidence_spans")
    if not isinstance(spans, list):
        errors.append("evidence_spans must be a list")
    else:
        for index, span in enumerate(spans):
            if not isinstance(span, dict):
                errors.append(f"evidence_spans[{index}] must be an object")
                continue
            if set(span) - {"start", "end"} or not {"start", "end"} <= set(span):
                errors.append(f"evidence_spans[{index}] must contain only start and end")
            start, end = span.get("start"), span.get("end")
            if (type(start) is not int or type(end) is not int
                    or not isinstance(premise, str)
                    or start < 0 or end <= start or end > len(premise)):
                length = len(premise) if isinstance(premise, str) else "unknown"
                errors.append(f"evidence_spans[{index}] must satisfy 0 <= start < end <= premise length ({length} code points)")

    annotation = row.get("annotation")
    if not isinstance(annotation, dict):
        errors.append("annotation must be an object")
    else:
        if set(annotation) - {"annotator_id", "adjudication_status", "notes"}:
            errors.append(f"annotation has unexpected fields: {sorted(set(annotation) - {'annotator_id', 'adjudication_status', 'notes'})}")
        if not {"annotator_id", "adjudication_status", "notes"} <= set(annotation):
            errors.append("annotation must include annotator_id, adjudication_status, and notes")
        for key in ("annotator_id", "adjudication_status"):
            if not _nonempty(annotation.get(key)):
                errors.append(f"annotation.{key} must be a non-empty string")
        if (not isinstance(annotation.get("adjudication_status"), str)
                or annotation["adjudication_status"] not in {"independent", "adjudicated", "unresolved"}):
            errors.append("annotation.adjudication_status must be independent|adjudicated|unresolved")
        if not isinstance(annotation.get("notes"), list) or any(not isinstance(note, str) for note in annotation.get("notes", [])):
            errors.append("annotation.notes must be a list of strings")
    return errors


def validate_dataset(rows: list[Any], line_numbers: list[int] | None = None) -> list[str]:
    errors: list[str] = []
    if not rows:
        errors.append("sidecar must contain at least one record")
    if line_numbers is not None and len(line_numbers) != len(rows):
        raise ValueError("line_numbers must align one-to-one with rows")
    candidate_ids: set[str] = set()
    group_splits: dict[str, str] = {}
    sense_splits: dict[str, str] = {}
    for index, row in enumerate(rows):
        line = line_numbers[index] if line_numbers is not None else index + 1
        errors.extend(f"line {line}: {error}" for error in validate_record(row))
        if not isinstance(row, dict):
            continue
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            if candidate_id in candidate_ids:
                errors.append(f"line {line}: duplicate candidate_id {candidate_id!r}")
            candidate_ids.add(candidate_id)
        split = row.get("split")
        if not isinstance(split, str) or split not in {"train", "dev", "test"}:
            continue
        group_id = row.get("group_id")
        if isinstance(group_id, str):
            previous = group_splits.setdefault(group_id, split)
            if previous != split:
                errors.append(f"line {line}: group_id {group_id!r} appears in both {previous} and {split} splits")
        source = row.get("source")
        sense_id = source.get("sense_id") if isinstance(source, dict) else None
        if isinstance(sense_id, str):
            previous = sense_splits.setdefault(sense_id, split)
            if previous != split:
                errors.append(f"line {line}: sense_id {sense_id!r} appears in both {previous} and {split} splits")
    return errors


def validate_against_candidate_manifest(rows: list[Any], manifest: Any) -> list[str]:
    """Require an exact one-to-one match with the frozen text-free candidate set."""
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["candidate manifest must be a JSON object"]
    expected_top = {"schema_version", "candidate_set_version", "candidate_count", "candidates"}
    if set(manifest) != expected_top:
        errors.append("candidate manifest must contain exactly schema_version, candidate_set_version, candidate_count, candidates")
    schema_version = manifest.get("schema_version")
    if (not isinstance(schema_version, str)
            or schema_version not in {"claim-review-candidate-manifest/0.1", "claim-review-candidate-manifest/0.2"}):
        errors.append("unsupported candidate manifest schema_version")
    version = manifest.get("candidate_set_version")
    if not _nonempty(version):
        errors.append("candidate manifest candidate_set_version must be a non-empty string")
    candidates = manifest.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return errors + ["candidate manifest candidates must be a non-empty array"]
    if type(manifest.get("candidate_count")) is not int or manifest["candidate_count"] != len(candidates):
        errors.append("candidate_count does not match manifest candidates length")

    manifest_by_id: dict[str, dict[str, Any]] = {}
    candidate_keys = {
        "candidate_id", "group_id", "split", "source", "direction",
        "premise_sha256", "hypothesis_sha256",
    }
    candidate_optional = {"relation", "formula_sha256"}
    if schema_version == "claim-review-candidate-manifest/0.2":
        candidate_optional.add("composition")
    source_keys = {"resource", "release", "sense_id", "pos"}
    group_splits: dict[str, str] = {}
    sense_splits: dict[str, str] = {}
    premise_splits: dict[str, str] = {}
    for index, candidate in enumerate(candidates):
        where = f"manifest candidate {index}"
        if (not isinstance(candidate, dict) or not candidate_keys <= set(candidate)
                or set(candidate) - candidate_keys - candidate_optional):
            errors.append(f"{where} contains missing or unsupported fields for manifest schema {schema_version!r}")
            continue
        candidate_id = candidate.get("candidate_id")
        if not _nonempty(candidate_id):
            errors.append(f"{where} candidate_id must be a non-empty string")
            continue
        source = candidate.get("source")
        if not isinstance(source, dict) or set(source) != source_keys:
            errors.append(f"{where} source must contain exactly resource, release, sense_id, and pos")
            continue
        if candidate_id in manifest_by_id:
            errors.append(f"duplicate candidate_id in manifest: {candidate_id!r}")
            continue
        if "relation" in candidate and (not isinstance(candidate["relation"], str)
                or candidate["relation"] not in {"necessary", "sufficient", "biconditional", "typical", "example", "other"}):
            errors.append(f"{where} has an invalid relation")
        if "formula_sha256" in candidate and not (
                isinstance(candidate["formula_sha256"], str)
                and SHA256_RE.fullmatch(candidate["formula_sha256"])):
            errors.append(f"{where} has an invalid formula_sha256")
        composition = candidate.get("composition")
        if "composition" in candidate:
            composition_errors = _validate_composition(composition)
            errors.extend(f"{where}: {error}" for error in composition_errors)
            if "formula_sha256" not in candidate:
                errors.append(f"{where} composed candidates require formula_sha256")
        if isinstance(candidate.get("split"), str) and candidate["split"] in {"train", "dev", "test"}:
            for dimension, value, table in (
                    ("group_id", candidate.get("group_id"), group_splits),
                    ("sense_id", source.get("sense_id"), sense_splits),
                    ("exact premise_sha256", candidate.get("premise_sha256"), premise_splits)):
                if isinstance(value, str):
                    previous = table.setdefault(value, candidate["split"])
                    if previous != candidate["split"]:
                        errors.append(f"{where} {dimension} leaks across train/dev/test splits")
        manifest_by_id[candidate_id] = candidate

    composition_edges: dict[str, list[str]] = {}
    for candidate_id, candidate in manifest_by_id.items():
        composition = candidate.get("composition")
        if not isinstance(composition, dict) or not isinstance(composition.get("components"), list):
            continue
        children = []
        for component in composition["components"]:
            if not isinstance(component, dict) or not isinstance(component.get("candidate_id"), str):
                continue
            child_id = component["candidate_id"]
            child = manifest_by_id.get(child_id)
            if child is None:
                errors.append(f"candidate {candidate_id!r} references unknown component {child_id!r}")
                continue
            if (child.get("group_id") != candidate.get("group_id")
                    or child.get("split") != candidate.get("split")
                    or child.get("source") != candidate.get("source")
                    or child.get("premise_sha256") != candidate.get("premise_sha256")):
                errors.append(f"candidate {candidate_id!r} component {child_id!r} differs in group/split/source/premise")
            children.append(child_id)
        composition_edges[candidate_id] = children

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(candidate_id: str) -> None:
        if candidate_id in visiting:
            errors.append(f"composition dependency cycle includes candidate_id {candidate_id!r}")
            return
        if candidate_id in visited:
            return
        visiting.add(candidate_id)
        for child_id in composition_edges.get(candidate_id, []):
            visit(child_id)
        visiting.remove(candidate_id)
        visited.add(candidate_id)

    for candidate_id in composition_edges:
        visit(candidate_id)

    if version != next((row.get("candidate_set_version") for row in rows if isinstance(row, dict)), None):
        errors.append("candidate_set_version differs between sidecar and manifest")
    sidecar_by_id = {
        row.get("candidate_id"): row for row in rows
        if isinstance(row, dict) and isinstance(row.get("candidate_id"), str)
    }
    if len(sidecar_by_id) != len(rows):
        errors.append("sidecar contains invalid or duplicate candidate IDs")
    if set(sidecar_by_id) != set(manifest_by_id):
        missing = len(set(manifest_by_id) - set(sidecar_by_id))
        extra = len(set(sidecar_by_id) - set(manifest_by_id))
        errors.append(f"sidecar/manifest candidate set mismatch (missing={missing}, extra={extra})")
    compare_fields = (
        "candidate_id", "group_id", "split", "direction", "premise_sha256",
        "hypothesis_sha256", "relation", "formula_sha256",
    )
    for candidate_id in set(sidecar_by_id) & set(manifest_by_id):
        row = sidecar_by_id[candidate_id]
        frozen = manifest_by_id[candidate_id]
        mismatches = [field for field in compare_fields if row.get(field) != frozen.get(field)]
        if row.get("candidate_set_version") != version:
            mismatches.append("candidate_set_version")
        side_source = row.get("source")
        frozen_source = frozen.get("source")
        if not isinstance(side_source, dict) or not isinstance(frozen_source, dict):
            mismatches.append("source")
        elif any(side_source.get(field) != frozen_source.get(field) for field in source_keys):
            mismatches.append("source")
        if mismatches:
            errors.append(f"candidate {candidate_id!r} differs from frozen manifest fields: {sorted(set(mismatches))}")
    return errors


def _validate_composition(value: Any) -> list[str]:
    errors = []
    if (not isinstance(value, dict) or set(value) != {"operator", "components"}
            or not isinstance(value.get("operator"), str)
            or value["operator"] not in {"and", "or"}
            or not isinstance(value.get("components"), list)
            or len(value["components"]) < 2):
        return ["composition must contain operator=and|or and at least two components"]
    ids = []
    for index, component in enumerate(value["components"]):
        if (not isinstance(component, dict) or set(component) != {"candidate_id", "negated"}
                or not _nonempty(component.get("candidate_id"))
                or type(component.get("negated")) is not bool):
            errors.append(f"composition.components[{index}] must contain candidate_id and boolean negated")
            continue
        ids.append(component["candidate_id"])
    if len(ids) != len(set(ids)):
        errors.append("composition component candidate_ids must be unique")
    return errors


def load_jsonl(path: Path) -> tuple[list[Any], list[int], list[str]]:
    rows: list[Any] = []
    lines: list[int] = []
    errors: list[str] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
                lines.append(line_no)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_no}: invalid JSON: {exc.msg}")
    return rows, lines, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sidecar", type=Path, help="claim-review JSONL")
    parser.add_argument("--candidate-manifest", type=Path,
                        help="text-free, gold-free frozen candidate manifest")
    parser.add_argument("--candidate-manifest-sha256",
                        help="expected manifest file hash recorded in the external preregistration/lock")
    args = parser.parse_args(argv)
    try:
        rows, lines, errors = load_jsonl(args.sidecar)
    except OSError as exc:
        print(f"cannot read {args.sidecar}: {exc}", file=sys.stderr)
        return 2
    errors.extend(validate_dataset(rows, lines))
    if bool(args.candidate_manifest) != bool(args.candidate_manifest_sha256):
        errors.append("--candidate-manifest and --candidate-manifest-sha256 must be supplied together")
    elif args.candidate_manifest:
        try:
            raw = args.candidate_manifest.read_bytes()
            actual_hash = hashlib.sha256(raw).hexdigest()
            if actual_hash != args.candidate_manifest_sha256:
                errors.append("candidate manifest file SHA-256 does not match the externally pinned value")
            manifest = json.loads(raw.decode("utf-8"))
            errors.extend(validate_against_candidate_manifest(rows, manifest))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read candidate manifest: {exc}")
    if errors:
        print("Claim-review validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Valid claim-review JSONL: {len(rows)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
