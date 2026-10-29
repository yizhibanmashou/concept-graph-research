"""Audit aggregate GCIDE source-payload links to frozen graph clauses/witnesses.

The output contains counts and fingerprints only. It never serializes glosses,
sense identities, source paths, rule text, or arbitrary source labels.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.audit_gcide_source_evidence import GCIDE_LABEL, SOURCE_FAMILY, _normalized_source_label
from src.analysis.audit_source_release_metadata import (
    DEFAULT_MAX_SOURCE_BYTES,
    _load_checksums,
    _safe_payload_path,
    _sha256_bytes,
    _sha256_file,
)
from src.analysis.frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK, verify_frozen_bundle_integrity
from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root

DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase127" / "gcide_graph_lineage.json"
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _contains_string_hash(value: Any, target_hash: str) -> bool:
    if isinstance(value, str):
        return hashlib.sha256(value.encode("utf-8")).hexdigest() == target_hash
    if isinstance(value, dict):
        return any(_contains_string_hash(child, target_hash) for child in value.values())
    if isinstance(value, list):
        return any(_contains_string_hash(child, target_hash) for child in value)
    return False


def audit_gcide_graph_lineage(
    bundle: Path,
    *,
    maximum_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> dict[str, Any]:
    bundle = bundle.resolve()
    integrity = verify_frozen_bundle_integrity(bundle)
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity lock did not pass")

    index_path = bundle / "indexes" / "senses.jsonl"
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    hyperedges_path = bundle / "graph" / "hyperedges.jsonl"
    witnesses_path = bundle / "graph" / "coverage_witnesses.jsonl"
    for required in (index_path, rules_path, hyperedges_path, witnesses_path):
        if not required.is_file():
            raise ValueError("required frozen index or graph file is missing")

    checksums, checksums_sha256 = _load_checksums(bundle)
    target_paths: set[str] = set()
    with index_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            source_records = row.get("source_records") if isinstance(row, dict) else None
            if not isinstance(source_records, list):
                continue
            for metadata in source_records:
                relative = metadata.get("path") if isinstance(metadata, dict) else None
                if isinstance(relative, str) and relative.startswith(SOURCE_FAMILY):
                    target_paths.add(relative)

    payload_sequence = __import__("hashlib").sha256()
    payload_bytes = 0
    gcide_payloads: dict[str, dict[str, Any]] = {}
    exception_paths: set[str] = set()
    exception_evidence_objects = 0
    evidence_objects = 0
    for relative in sorted(target_paths):
        payload_path = _safe_payload_path(bundle, relative, maximum_source_bytes)
        raw = payload_path.read_bytes()
        digest = _sha256_bytes(raw)
        expected = checksums.get(relative)
        if (
            not isinstance(expected, dict)
            or expected.get("sha256") != digest
            or type(expected.get("bytes")) is not int
            or expected["bytes"] != len(raw)
        ):
            raise ValueError("target source payload differs from frozen checksum sidecar")
        payload_sequence.update(len(raw).to_bytes(8, "big"))
        payload_sequence.update(bytes.fromhex(digest))
        payload_bytes += len(raw)
        payload = json.loads(raw.decode("utf-8"))
        source_record = payload.get("source_record") if isinstance(payload, dict) else None
        provenance = source_record.get("alternative_definition_provenance") if isinstance(source_record, dict) else None
        evidence = provenance.get("source_evidence") if isinstance(provenance, dict) else None
        if not isinstance(evidence, list):
            continue
        gcide_count = sum(
            1 for item in evidence
            if isinstance(item, dict) and _normalized_source_label(item.get("source")) == GCIDE_LABEL
        )
        if gcide_count:
            evidence_objects += gcide_count
            synset = payload.get("synset") if isinstance(payload.get("synset"), dict) else {}
            raw_definition = synset.get("raw_definition")
            raw_definition_hash = hashlib.sha256(raw_definition.encode("utf-8")).hexdigest() if isinstance(raw_definition, str) else None
            for item in evidence:
                if not isinstance(item, dict) or _normalized_source_label(item.get("source")) != GCIDE_LABEL:
                    continue
                value = item.get("definition_text_sha256")
                if not isinstance(value, str) or HASH_RE.fullmatch(value) is None:
                    raise ValueError("GCIDE evidence has an invalid definition_text_sha256")
                value = value.casefold()
                if value != raw_definition_hash and not _contains_string_hash(payload, value):
                    exception_evidence_objects += 1
                    exception_paths.add(relative)
            gcide_payloads[relative] = {
                "synset_id": payload.get("synset_id"),
                "sense_id": payload.get("sense_id"),
            }

    rows_by_path: dict[str, dict[str, Any]] = {}
    path_reference_counts: Counter[str] = Counter()
    with index_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            source_records = row.get("source_records") if isinstance(row, dict) else None
            if not isinstance(source_records, list):
                continue
            for metadata in source_records:
                relative = metadata.get("path") if isinstance(metadata, dict) else None
                if relative in gcide_payloads:
                    path_reference_counts[relative] += 1
                    rows_by_path[relative] = row

    candidate_heads = {item.get("synset_id") for item in gcide_payloads.values() if isinstance(item.get("synset_id"), str)}
    rules_by_head: dict[str, dict[str, Any]] = {}
    with rules_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            if not isinstance(row, dict):
                raise ValueError("hypergraph rule record is malformed")
            head = row.get("head")
            if head in candidate_heads:
                if head in rules_by_head:
                    raise ValueError("candidate graph head is duplicated")
                rules_by_head[head] = row

    hyperedges: dict[tuple[str, int], list[Any]] = {}
    with hyperedges_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            if not isinstance(row, dict):
                raise ValueError("hyperedge record is malformed")
            head, clause_index, dependencies = row.get("head"), row.get("clause_index"), row.get("dependencies")
            if head in candidate_heads and isinstance(head, str) and type(clause_index) is int and isinstance(dependencies, list):
                key = (head, clause_index)
                if key in hyperedges:
                    raise ValueError("duplicate candidate hyperedge head/clause index")
                hyperedges[key] = dependencies

    witnesses_by_head: dict[str, dict[str, Any]] = {}
    with witnesses_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            head = row.get("head") if isinstance(row, dict) else None
            if head in candidate_heads:
                if head in witnesses_by_head:
                    raise ValueError("candidate selected-witness head is duplicated")
                witnesses_by_head[head] = row

    payload_outcomes: Counter[str] = Counter()
    path_level_active_rows = 0
    path_level_selected_rows = 0
    exception_paths_selected = 0
    exception_paths_nonselected_only = 0
    exception_paths_absent = 0
    unique_head_state: dict[str, dict[str, bool]] = {}
    for relative, payload_info in gcide_payloads.items():
        row = rows_by_path.get(relative)
        if row is None or path_reference_counts[relative] != 1:
            raise ValueError("GCIDE source payload is missing or duplicated in the sense index")
        identity = row.get("identity")
        payload_outcomes["payload_synset_id_equals_index_identity"] += int(payload_info["synset_id"] == identity)
        payload_outcomes["payload_sense_id_equals_index_identity"] += int(payload_info["sense_id"] == identity)
        head = payload_info.get("synset_id")
        rule = rules_by_head.get(head) if isinstance(head, str) else None
        witness = witnesses_by_head.get(head) if isinstance(head, str) else None
        clauses = rule.get("clauses", []) if isinstance(rule, dict) else []
        witness_clause = witness.get("witness_clause") if isinstance(witness, dict) else None
        selected_indices = [i for i, clause in enumerate(clauses) if clause == witness_clause] if isinstance(witness_clause, list) else []
        active_entries = row.get("active_clause_sources", [])
        active_entries = [entry for entry in active_entries if isinstance(entry, dict)] if isinstance(active_entries, list) else []
        path_active_entries = [entry for entry in active_entries if relative in (entry.get("source_documents") or [])]
        path_selected_entries = [entry for entry in path_active_entries if entry.get("clause_index") in selected_indices]
        path_nonselected_entries = [entry for entry in path_active_entries if entry.get("clause_index") not in selected_indices]
        path_level_active_rows += len(path_active_entries)
        path_level_selected_rows += len(path_selected_entries)
        if path_selected_entries:
            payload_outcomes["gcide_payloads_in_selected_witness_documents"] += 1
            if relative in exception_paths:
                exception_paths_selected += 1
        elif path_nonselected_entries:
            payload_outcomes["gcide_payloads_in_nonselected_active_documents_only"] += 1
            if relative in exception_paths:
                exception_paths_nonselected_only += 1
        else:
            payload_outcomes["gcide_payloads_absent_from_all_active_clause_documents"] += 1
            if relative in exception_paths:
                exception_paths_absent += 1

        if isinstance(head, str) and head not in unique_head_state:
            is_seed = witness.get("is_seed") is True if isinstance(witness, dict) else False
            hyperedge_match = any(
                hyperedges.get((head, i)) == clauses[i]
                for i in selected_indices
                if isinstance(clauses, list) and i < len(clauses)
            )
            if isinstance(witness, dict) and not is_seed and not (selected_indices and hyperedge_match):
                raise ValueError("non-seed selected witness does not match a rule clause and hyperedge")
            unique_head_state[head] = {
                "rule_found": rule is not None,
                "witness_found": witness is not None,
                "is_seed_witness": is_seed,
                "selected_clause_matches_rule": bool(selected_indices),
                "selected_clause_matches_hyperedge": hyperedge_match,
            }

    if any(value != len(gcide_payloads) for value in (
        payload_outcomes["payload_synset_id_equals_index_identity"],
        payload_outcomes["payload_sense_id_equals_index_identity"],
    )):
        raise ValueError("GCIDE payload identity differs from its sense-index identity")

    head_counts = Counter()
    for state in unique_head_state.values():
        head_counts["candidate_graph_heads"] += 1
        head_counts["graph_rules_found"] += int(state["rule_found"])
        head_counts["selected_witnesses_found"] += int(state["witness_found"])
        head_counts["seed_witness_heads"] += int(state["is_seed_witness"])
        head_counts["nonseed_witness_heads"] += int(state["witness_found"] and not state["is_seed_witness"])
        head_counts["selected_witness_clauses_matching_rules"] += int(state["selected_clause_matches_rule"])
        head_counts["selected_witness_clauses_matching_hyperedges"] += int(state["selected_clause_matches_hyperedge"])

    return {
        "schema_version": "gcide-graph-lineage/1",
        "scope": "gcide_labeled_alternative_definition_source_payloads_to_frozen_graph_source_documents",
        "inputs": {
            "bundle_manifest_sha256": _sha256_file(bundle / "manifest.json"),
            "bundle_integrity_lock_sha256": _sha256_file(DEFAULT_INTEGRITY_LOCK),
            "checksums_sidecar_sha256": checksums_sha256,
            "sense_index_sha256": _sha256_file(index_path),
            "target_payload_sequence_sha256": payload_sequence.hexdigest(),
            "target_payload_count": len(target_paths),
            "target_payload_bytes": payload_bytes,
            "rules_sha256": _sha256_file(rules_path),
            "hyperedges_sha256": _sha256_file(hyperedges_path),
            "witnesses_sha256": _sha256_file(witnesses_path),
            "gcide_payload_count": len(gcide_payloads),
            "gcide_evidence_object_count": evidence_objects,
            "evidence_objects_with_hash_absent_from_same_payload_strings_and_not_equal_to_raw_definition": exception_evidence_objects,
        },
        "counts": {
            **dict(sorted(payload_outcomes.items())),
            **dict(sorted(head_counts.items())),
            "gcide_payloads_referenced_once_by_sense_index": sum(path_reference_counts[p] == 1 for p in gcide_payloads),
            "gcide_payloads_with_active_clause_source_link": sum(
                payload_outcomes[key] for key in ("gcide_payloads_in_selected_witness_documents", "gcide_payloads_in_nonselected_active_documents_only")
            ),
            "gcide_payload_source_rows_in_active_clauses": path_level_active_rows,
            "gcide_payload_source_rows_in_selected_witness_clauses": path_level_selected_rows,
            "gcide_payloads_in_selected_witness_documents": payload_outcomes["gcide_payloads_in_selected_witness_documents"],
            "gcide_payloads_in_nonselected_active_documents_only": payload_outcomes["gcide_payloads_in_nonselected_active_documents_only"],
            "gcide_payloads_absent_from_all_active_clause_documents": payload_outcomes["gcide_payloads_absent_from_all_active_clause_documents"],
            "exception_payloads": len(exception_paths),
            "exception_payloads_in_selected_witness_documents": exception_paths_selected,
            "exception_payloads_in_nonselected_active_documents_only": exception_paths_nonselected_only,
            "exception_payloads_absent_from_all_active_clause_documents": exception_paths_absent,
        },
        "interpretation_limit": (
            "This is path-level structural lineage from source-indexed GCIDE-labeled payloads to active-clause source documents and selected witness clauses. "
            "It does not prove the marked text semantically supports a rule, identify exclusive subsource rights, establish ILI/sense equivalence across resources, or clear redistribution."
        ),
        "raw_text_id_paths_and_rule_text_emitted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, default=configured_bundle_root())
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--maximum-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error("output exists; pass --force to replace it")
    try:
        report = audit_gcide_graph_lineage(args.bundle_root, maximum_source_bytes=args.maximum_source_bytes)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        print(json.dumps({"schema_version": "gcide-graph-lineage/1", "valid": False}, indent=2))
        return 1
    report["implementation_sha256"] = _sha256_file(Path(__file__).resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"schema_version": report["schema_version"], "counts": report["counts"], "output_sha256": _sha256_file(output)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
