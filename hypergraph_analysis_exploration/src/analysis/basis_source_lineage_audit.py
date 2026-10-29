"""Audit identity and payload lineage for the frozen graph's selected basis."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.analysis.frozen_bundle_integrity import (
    DEFAULT_INTEGRITY_LOCK,
    verify_frozen_bundle_integrity,
)
from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_BUNDLE = configured_bundle_root()
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase229" / "basis_source_lineage_audit.json"
SCHEMA_VERSION = "basis-source-lineage-audit/1"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _payload_identity(payload: dict[str, Any]) -> str | None:
    synset = payload.get("synset")
    synset = synset if isinstance(synset, dict) else {}
    value = payload.get("synset_id") or payload.get("sense_id") or synset.get("synset_id")
    return value if isinstance(value, str) else None


def build_report(
    bundle: Path = DEFAULT_BUNDLE,
    integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
) -> dict[str, Any]:
    bundle = bundle.resolve()
    integrity = verify_frozen_bundle_integrity(bundle, integrity_lock)
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity lock did not pass")

    graph_dir = bundle / "graph"
    basis_path = graph_dir / "selected_basis_atoms.txt"
    nodes_path = graph_dir / "nodes.tsv"
    index_path = bundle / "indexes" / "senses.jsonl"
    checksums_path = bundle / "checksums.jsonl"
    required_paths = (basis_path, nodes_path, index_path, checksums_path)
    if not all(path.is_file() for path in required_paths):
        raise ValueError("bundle lacks a required basis lineage input")

    basis_rows = [line.strip() for line in basis_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    basis = set(basis_rows)
    if len(basis) != len(basis_rows):
        raise ValueError("selected_basis_atoms.txt contains duplicate IDs")

    nodes: dict[str, dict[str, str]] = {}
    with nodes_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        required_columns = {"synset_id", "lemmas", "pos", "definition", "source_root", "is_basis"}
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError("nodes.tsv lacks required basis metadata columns")
        for row in reader:
            identity = row.get("synset_id", "")
            if identity in basis:
                if identity in nodes:
                    raise ValueError("nodes.tsv contains duplicate basis identity")
                nodes[identity] = row
    if set(nodes) != basis or any(row.get("is_basis", "").casefold() != "true" for row in nodes.values()):
        raise ValueError("basis file and nodes.tsv do not agree exactly")

    checksum_rows: dict[str, dict[str, Any]] = {}
    with checksums_path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            record = json.loads(line)
            path = record.get("path")
            if not isinstance(path, str) or not path:
                raise ValueError(f"checksum row {line_number} has no path")
            if path in checksum_rows:
                raise ValueError(f"duplicate checksum path at row {line_number}")
            checksum_rows[path] = record

    index_rows: dict[str, dict[str, Any]] = {}
    total_index_rows = 0
    total_index_clause_count = 0
    active_clause_source_entry_count = 0
    active_clause_source_document_link_count = 0
    clauses_without_active_source_row = 0
    duplicate_clause_source_indices = 0
    out_of_range_clause_source_indices = 0
    clause_entries_without_source_documents = 0
    clause_sources_missing_same_head_source_record = 0
    clause_source_document_count_distribution: Counter[int] = Counter()
    with index_path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            total_index_rows += 1
            record = json.loads(line)
            identity = record.get("identity")
            clause_count = record.get("graph_clause_count")
            if not isinstance(clause_count, int) or clause_count < 0:
                raise ValueError(f"invalid graph_clause_count in sense-index row {line_number}")
            total_index_clause_count += clause_count
            record_paths = {
                item.get("path")
                for item in record.get("source_records", [])
                if isinstance(item, dict) and isinstance(item.get("path"), str)
            }
            source_rows = record.get("active_clause_sources")
            if not isinstance(source_rows, list):
                raise ValueError(f"malformed active_clause_sources in sense-index row {line_number}")
            valid_indices: set[int] = set()
            for source_row in source_rows:
                active_clause_source_entry_count += 1
                if not isinstance(source_row, dict):
                    raise ValueError(f"malformed active clause source row {line_number}")
                clause_index = source_row.get("clause_index")
                if not isinstance(clause_index, int) or clause_index < 0 or clause_index >= clause_count:
                    out_of_range_clause_source_indices += 1
                elif clause_index in valid_indices:
                    duplicate_clause_source_indices += 1
                else:
                    valid_indices.add(clause_index)
                documents = source_row.get("source_documents")
                if not isinstance(documents, list):
                    raise ValueError(f"malformed source_documents in sense-index row {line_number}")
                active_clause_source_document_link_count += len(documents)
                clause_source_document_count_distribution[len(documents)] += 1
                if not documents:
                    clause_entries_without_source_documents += 1
                if any(not isinstance(path, str) or path not in record_paths for path in documents):
                    clause_sources_missing_same_head_source_record += 1
            clauses_without_active_source_row += clause_count - len(valid_indices)
            if identity in basis:
                if identity in index_rows:
                    raise ValueError(f"duplicate basis identity in sense index at row {line_number}")
                index_rows[identity] = record
    if set(index_rows) != basis:
        raise ValueError("sense index does not contain every basis identity exactly once")

    node_index_pos_matches = 0
    node_index_lemma_matches = 0
    node_index_definition_matches = 0
    source_record_counts: Counter[int] = Counter()
    source_paths_by_identity: dict[str, set[str]] = {}
    source_pairs: set[tuple[str, str]] = set()
    active_pairs: set[tuple[str, str]] = set()
    active_paths_subset_count = 0
    active_path_count = 0
    for identity, record in index_rows.items():
        node = nodes[identity]
        node_index_pos_matches += node.get("pos") == record.get("pos")
        node_index_lemma_matches += node.get("lemmas") == record.get("lemmas")
        node_index_definition_matches += node.get("definition") == record.get("snapshot_definition")
        records = record.get("source_records")
        if not isinstance(records, list):
            raise ValueError(f"basis sense-index row has malformed source_records: {identity}")
        source_record_counts[len(records)] += 1
        paths = {item.get("path") for item in records if isinstance(item, dict) and item.get("path")}
        source_paths_by_identity[identity] = paths
        source_pairs.update((identity, path) for path in paths)
        active_paths = {
            path
            for clause_source in record.get("active_clause_sources", [])
            if isinstance(clause_source, dict)
            for path in clause_source.get("source_documents", [])
            if isinstance(path, str)
        }
        active_path_count += len(active_paths)
        active_pairs.update((identity, path) for path in active_paths)
        active_paths_subset_count += active_paths <= paths

    shared_paths: dict[str, set[str]] = defaultdict(set)
    for identity, path in source_pairs:
        shared_paths[path].add(identity)

    payload_length_matches = 0
    payload_sha256_matches = 0
    payload_identity_matches = 0
    sidecar_path_matches = 0
    payload_files_exist = 0
    payload_paths_within_bundle = 0
    payload_digest_rows: list[tuple[str, str]] = []
    for identity, relative_path in sorted(source_pairs):
        sidecar = checksum_rows.get(relative_path)
        if sidecar is None:
            continue
        sidecar_path_matches += 1
        payload_path = (bundle / relative_path).resolve()
        if payload_path.is_relative_to(bundle):
            payload_paths_within_bundle += 1
        else:
            raise ValueError("source payload path escapes the frozen bundle")
        if not payload_path.is_file():
            continue
        payload_files_exist += 1
        raw = payload_path.read_bytes()
        if len(raw) == sidecar.get("bytes"):
            payload_length_matches += 1
        digest = _sha256_bytes(raw)
        if digest == sidecar.get("sha256"):
            payload_sha256_matches += 1
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"basis source payload is invalid JSON: {relative_path}") from exc
        record_identity = next(
            item.get("identity")
            for item in index_rows[identity]["source_records"]
            if item.get("path") == relative_path
        )
        if record_identity == identity and _payload_identity(payload) == identity:
            payload_identity_matches += 1
        payload_digest_rows.append((relative_path, digest))

    if not (
        payload_length_matches == payload_sha256_matches == payload_identity_matches == len(source_pairs)
        and sidecar_path_matches == payload_files_exist == payload_paths_within_bundle == len(source_pairs)
    ):
        raise ValueError("one or more basis source payloads failed linkage, size, hash, or identity checks")

    # Establish whether basis source documents are linked as clause evidence for other senses.
    basis_paths = {path for _, path in source_pairs}
    active_owners: dict[str, set[str]] = defaultdict(set)
    with index_path.open(encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            owner = record.get("identity")
            for clause_source in record.get("active_clause_sources", []):
                if isinstance(clause_source, dict):
                    for path in clause_source.get("source_documents", []):
                        if path in basis_paths:
                            active_owners[path].add(owner)

    bundle_manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    payload_digest_rows.sort()
    payload_digest_digest = _sha256_bytes(
        "".join(f"{path}\t{digest}\n" for path, digest in payload_digest_rows).encode("utf-8")
    )
    source_root_counts = Counter(row.get("source_root") or "other_or_missing" for row in nodes.values())
    return {
        "schema_version": SCHEMA_VERSION,
        "claim_type": "basis_identity_and_source_payload_lineage_not_semantic_support",
        "inputs": {
            "bundle_root": str(bundle),
            "bundle_semantic_fingerprint_sha256": bundle_manifest.get("semantic_fingerprint_sha256"),
            "basis_file_sha256": _sha256_bytes(basis_path.read_bytes()),
            "nodes_file_sha256": _sha256_bytes(nodes_path.read_bytes()),
            "sense_index_sha256": _sha256_bytes(index_path.read_bytes()),
            "checksums_sha256": _sha256_bytes(checksums_path.read_bytes()),
            "frozen_bundle_integrity_valid": True,
        },
        "counts": {
            "basis_atoms": len(basis),
            "basis_nodes_matched": len(nodes),
            "basis_sense_index_rows_matched": len(index_rows),
            "sense_index_total_rows": total_index_rows,
            "sense_index_graph_clause_count_sum": total_index_clause_count,
            "active_clause_source_index_rows": active_clause_source_entry_count,
            "active_clause_source_document_links": active_clause_source_document_link_count,
            "clauses_missing_active_source_index_rows": clauses_without_active_source_row,
            "active_clause_source_document_count_distribution": dict(
                sorted(clause_source_document_count_distribution.items())
            ),
            "active_clause_entries_without_source_documents": clause_entries_without_source_documents,
            "active_clause_entries_with_documents_missing_same_head_source_record": clause_sources_missing_same_head_source_record,
            "duplicate_clause_source_indices": duplicate_clause_source_indices,
            "out_of_range_clause_source_indices": out_of_range_clause_source_indices,
            "basis_source_record_path_associations": len(source_pairs),
            "basis_distinct_source_payloads": len(basis_paths),
            "basis_seeds_with_source_records": len(source_paths_by_identity),
            "source_record_count_distribution": dict(sorted(source_record_counts.items())),
            "basis_source_paths_shared_across_basis_seeds": sum(len(owners) > 1 for owners in shared_paths.values()),
            "active_clause_source_associations_for_basis_heads": len(active_pairs),
            "active_source_paths_subset_of_each_basis_sense_source_records": active_paths_subset_count,
            "basis_source_paths_linked_to_clause_evidence_anywhere": sum(path in active_owners for path in basis_paths),
            "basis_source_paths_linked_to_clause_evidence_for_multiple_index_rows": sum(
                len(active_owners[path]) > 1 for path in basis_paths
            ),
            "source_roots": dict(sorted(source_root_counts.items())),
        },
        "checks": {
            "basis_ids_match_nodes_one_to_one": set(nodes) == basis,
            "basis_ids_match_sense_index_one_to_one": set(index_rows) == basis,
            "all_graph_clauses_have_exactly_one_active_source_index_row": (
                total_index_clause_count == active_clause_source_entry_count
                and clauses_without_active_source_row == 0
                and duplicate_clause_source_indices == 0
                and out_of_range_clause_source_indices == 0
            ),
            "all_active_clause_documents_link_to_same_head_source_records": (
                clause_sources_missing_same_head_source_record == 0
            ),
            "node_index_pos_exact_matches": node_index_pos_matches,
            "node_index_lemmas_exact_matches": node_index_lemma_matches,
            "node_index_definition_exact_matches": node_index_definition_matches,
            "source_paths_found_in_checksum_sidecar": sidecar_path_matches,
            "source_payload_files_exist": payload_files_exist,
            "source_payload_sizes_match_sidecar": payload_length_matches,
            "source_payload_sha256_match_sidecar": payload_sha256_matches,
            "source_payload_identity_matches_basis_identity": payload_identity_matches,
            "source_identity_digest": payload_digest_digest,
        },
        "interpretation_limits": [
            "Identity, source path, payload hash, and sense identity linkage do not establish that a gloss semantically supports a Horn rule.",
            "Removing a basis seed is not equivalent to deleting its source payloads or all clauses linked to those payloads.",
            "No source-deletion closure was computed; a source-document intervention unit remains undefined.",
            "The audit does not assess license clearance or public-release eligibility.",
        ],
    }


def _write_json(path: Path, report: dict[str, Any], force: bool) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to(PROJECT_ROOT):
        raise ValueError("output must remain inside the project directory")
    if resolved.exists() and not force:
        raise ValueError("output already exists; choose another path or pass --force")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = build_report(args.bundle, args.integrity_lock)
        _write_json(args.output, report, args.force)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    counts = report["counts"]
    checks = report["checks"]
    print(
        "Audited basis source lineage: "
        f"{counts['basis_atoms']} basis atoms, "
        f"{checks['source_payload_sha256_match_sidecar']} payloads hash-verified"
    )
    print(f"Wrote aggregate-only report: {args.output.resolve().relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
