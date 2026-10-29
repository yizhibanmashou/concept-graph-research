"""Audit source-index coverage across all minimum-depth clause alternatives.

This is an aggregate structural/provenance audit. It does not read source
payloads or establish that a gloss semantically supports a clause.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.frozen_bundle_integrity import (
    DEFAULT_INTEGRITY_LOCK,
    verify_frozen_bundle_integrity,
)
from src.analysis.frozen_hypergraph_audit import (
    DEFAULT_BUNDLE,
    PROJECT_ROOT,
    jsonl,
    load_graph,
    validate_witnesses,
)
from src.analysis.minimum_witness_audit import (
    minimum_depth_clauses_by_head,
    minimum_derivation_depths,
)
from src.analysis.full_source_payload_census import (
    DEFAULT_MAX_SOURCE_BYTES,
    _read_source,
    _safe_source_path,
)
from src.analysis.witness_tree_expansion_audit import minimum_tree_witness_rows


DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase215" / "minimum_depth_alternative_source_audit.json"
DEFAULT_SOURCE_MAP_OUTPUT = PROJECT_ROOT / "outputs" / "phase216" / "minimum_depth_alternative_source_map.jsonl"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _distribution(values: list[int]) -> dict[str, int | float | None]:
    if not values:
        return {"count": 0, "min": None, "median": None, "p90": None, "max": None}
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "min": ordered[0],
        "median": statistics.median(ordered),
        "p90": ordered[int(0.9 * (len(ordered) - 1))],
        "max": ordered[-1],
    }


def _clause_documents(index_row: dict[str, Any]) -> dict[int, set[str]]:
    result: dict[int, set[str]] = {}
    entries = index_row.get("active_clause_sources")
    if not isinstance(entries, list):
        return result
    for entry in entries:
        if not isinstance(entry, dict) or type(entry.get("clause_index")) is not int:
            continue
        clause_index = entry["clause_index"]
        documents = entry.get("source_documents")
        if not isinstance(documents, list):
            continue
        result.setdefault(clause_index, set()).update(
            document for document in documents
            if isinstance(document, str) and document
        )
    return result


def _source_paths(index_row: dict[str, Any]) -> set[str]:
    rows = index_row.get("source_records")
    if not isinstance(rows, list):
        return set()
    return {
        row["path"] for row in rows
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }


def _checksum_paths(checksums: dict[str, Any]) -> set[str]:
    return {
        path for path, row in checksums.items()
        if isinstance(path, str) and isinstance(row, dict)
        and isinstance(row.get("sha256"), str) and type(row.get("bytes")) is int
    }


def build_report(
    bundle: Path = DEFAULT_BUNDLE,
    integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
    *,
    verify_new_payloads: bool = False,
    maximum_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
    source_map_output: Path | None = None,
) -> dict[str, Any]:
    if not isinstance(maximum_source_bytes, int) or isinstance(maximum_source_bytes, bool) or maximum_source_bytes < 1:
        raise ValueError("maximum_source_bytes must be a positive integer")
    bundle = bundle.resolve()
    integrity_lock = integrity_lock.resolve()
    integrity = verify_frozen_bundle_integrity(bundle, integrity_lock)
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity verification failed")

    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    witness_path = bundle / "graph" / "coverage_witnesses.jsonl"
    index_path = bundle / "indexes" / "senses.jsonl"
    checksum_path = bundle / "checksums.jsonl"
    rules, clauses, literal_count = load_graph(bundle)
    heads = set(rules)
    basis = {
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt")
        .read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    selected_check = validate_witnesses(heads, basis, rules, list(jsonl(witness_path)))
    if not selected_check.get("all_valid"):
        raise ValueError("selected witness certificate failed structural validation")

    depths = minimum_derivation_depths(heads, clauses, basis)
    alternatives = minimum_depth_clauses_by_head(heads, clauses, depths, basis)
    compact_rows, _ = minimum_tree_witness_rows(heads, basis, depths, alternatives)
    compact_by_head = {row["head"]: row for row in compact_rows}
    selected = selected_check["witness_by_head"]
    selected_min_depth = all(
        selected[head]["proof_depth"] == depths[head]
        for head in heads - basis
    )
    if not selected_min_depth:
        raise ValueError("selected witness is not minimum-depth for every nonbasis head")

    clause_indices: dict[str, dict[tuple[str, ...], int]] = {}
    for head, bodies in rules.items():
        indexed: dict[tuple[str, ...], int] = {}
        for index, body in enumerate(bodies):
            key = tuple(body)
            if key in indexed:
                raise ValueError("duplicate canonical body within a graph head")
            indexed[key] = index
        clause_indices[head] = indexed

    try:
        checksums = {
            row["path"]: row for row in jsonl(checksum_path)
            if isinstance(row, dict) and isinstance(row.get("path"), str)
        }
    except (KeyError, TypeError) as exc:
        raise ValueError("malformed checksum sidecar") from exc
    valid_checksum_paths = _checksum_paths(checksums)

    head_count = 0
    alternative_clause_total = 0
    alternative_counts: list[int] = []
    minimum_depths: list[int] = []
    clauses_with_links = 0
    clauses_without_links = 0
    clause_source_document_links = 0
    clause_source_documents_missing_index_metadata = 0
    clause_source_documents_missing_checksum_metadata = 0
    heads_with_multiple_minimum_clauses = 0
    heads_with_additional_source_documents_beyond_canonical = 0
    extra_source_documents_beyond_canonical = 0
    heads_with_additional_source_documents_beyond_selected = 0
    extra_source_documents_beyond_selected = 0
    canonical_clause_document_counts: list[int] = []
    selected_clause_document_counts: list[int] = []
    all_alternative_union_document_counts: list[int] = []
    selected_clause_differs_from_canonical = 0
    union_documents: set[str] = set()
    source_map_rows: list[dict[str, Any]] | None = [] if source_map_output is not None else None
    alternative_documents_by_head: dict[str, set[str]] = {}
    baseline_documents_by_head: dict[str, set[str]] = {}
    seen_heads: set[str] = set()

    with index_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict) or not isinstance(row.get("identity"), str):
                raise ValueError(f"malformed sense index row {line_number}")
            head = row["identity"]
            if head not in heads or head in seen_heads:
                raise ValueError("sense index has an unknown or duplicate graph identity")
            seen_heads.add(head)
            if head in basis:
                continue

            bodies = alternatives[head]
            head_count += 1
            alternative_clause_total += len(bodies)
            alternative_counts.append(len(bodies))
            minimum_depths.append(depths[head])
            if len(bodies) > 1:
                heads_with_multiple_minimum_clauses += 1

            docs_by_clause = _clause_documents(row)
            source_paths = _source_paths(row)
            all_docs: set[str] = set()
            for body in bodies:
                clause_index = clause_indices[head].get(tuple(body))
                if clause_index is None:
                    raise ValueError("minimum-depth clause is absent from graph rule inventory")
                documents = docs_by_clause.get(clause_index, set())
                clause_source_document_links += len(documents)
                if documents:
                    clauses_with_links += 1
                else:
                    clauses_without_links += 1
                clause_source_documents_missing_index_metadata += len(documents - source_paths)
                clause_source_documents_missing_checksum_metadata += len(documents - valid_checksum_paths)
                all_docs.update(documents)
                union_documents.update(documents)
                if source_map_rows is not None:
                    for document in sorted(documents):
                        checksum = checksums.get(document)
                        if not isinstance(checksum, dict):
                            raise ValueError("source map document lacks checksum metadata")
                        source_map_rows.append({
                            "head_key_sha256": hashlib.sha256(head.encode("utf-8")).hexdigest(),
                            "clause_index": clause_index,
                            "body_key_sha256": hashlib.sha256(
                                json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                            ).hexdigest(),
                            "body_literal_count": len(body),
                            "source_document_key_sha256": hashlib.sha256(document.encode("utf-8")).hexdigest(),
                            "source_payload_sha256": checksum["sha256"],
                            "source_payload_bytes": checksum["bytes"],
                        })

            canonical_body = min(bodies)
            canonical_index = clause_indices[head][tuple(canonical_body)]
            canonical_docs = docs_by_clause.get(canonical_index, set())
            canonical_clause_document_counts.append(len(canonical_docs))
            all_alternative_union_document_counts.append(len(all_docs))
            additional_docs = all_docs - canonical_docs
            if additional_docs:
                heads_with_additional_source_documents_beyond_canonical += 1
                extra_source_documents_beyond_canonical += len(additional_docs)

            selected_body = tuple(sorted(selected[head]["witness_clause"]))
            if selected_body != canonical_body:
                selected_clause_differs_from_canonical += 1
            selected_index = clause_indices[head].get(selected_body)
            if selected_index is None:
                raise ValueError("selected witness clause is absent from graph rule inventory")
            selected_docs = docs_by_clause.get(selected_index, set())
            selected_clause_document_counts.append(len(selected_docs))
            selected_additional_docs = all_docs - selected_docs
            if selected_additional_docs:
                heads_with_additional_source_documents_beyond_selected += 1
                extra_source_documents_beyond_selected += len(selected_additional_docs)

            compact_body = tuple(sorted(compact_by_head[head]["witness_clause"]))
            compact_index = clause_indices[head].get(compact_body)
            if compact_index is None:
                raise ValueError("compact minimum-depth clause is absent from graph rule inventory")
            compact_docs = docs_by_clause.get(compact_index, set())
            alternative_documents_by_head[head] = all_docs
            baseline_documents_by_head[head] = selected_docs | compact_docs

    if seen_heads != heads:
        raise ValueError("sense index and graph head sets differ")
    if head_count != len(heads - basis) or clauses_with_links + clauses_without_links != alternative_clause_total:
        raise ValueError("minimum-depth alternative accounting did not reconcile")

    source_map_info: dict[str, Any] = {"requested": source_map_rows is not None}
    if source_map_rows is not None:
        source_map_rows.sort(key=lambda row: (
            row["head_key_sha256"], row["clause_index"], row["source_document_key_sha256"]
        ))
        source_map_output = source_map_output.resolve()
        source_map_output.parent.mkdir(parents=True, exist_ok=True)
        with source_map_output.open("w", encoding="utf-8", newline="\n") as stream:
            for row in source_map_rows:
                stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        source_map_info.update({
            "path": source_map_output.as_posix(),
            "row_count": len(source_map_rows),
            "sha256": _sha256(source_map_output),
            "raw_paths_or_identities_emitted": False,
            "identifiers_are_hashed_not_anonymized": True,
        })

    source_union_checksum_complete = union_documents <= valid_checksum_paths
    payload_verification: dict[str, Any] = {
        "requested": verify_new_payloads,
        "baseline_source": "Phase199 selected-plus-compact witness payload and identity audit",
        "baseline_reused": False,
        "baseline_document_head_pair_count": 0,
        "new_minimum_depth_document_head_pair_count": 0,
        "new_distinct_source_documents": 0,
        "new_payload_bytes_read": 0,
        "checksum_mismatch_count": None,
        "identity_mismatch_count": None,
        "all_minimum_depth_alternative_source_pairs_verified": False,
    }
    if verify_new_payloads:
        audit_path = PROJECT_ROOT / "sources" / "compact_witness_source_trace_audit_2026-10-08_phase199.json"
        previous_output_path = PROJECT_ROOT / "outputs" / "phase199" / "compact_witness_source_trace_verified.json"
        prior = json.loads(audit_path.read_text(encoding="utf-8"))
        prior_output_bytes = previous_output_path.read_bytes()
        expected_prior_implementations = prior.get("implementation_sha256")
        if not isinstance(expected_prior_implementations, dict):
            raise ValueError("Phase199 machine record lacks implementation hashes")
        for relative, expected_hash in expected_prior_implementations.items():
            source_path = PROJECT_ROOT / relative
            if not source_path.is_file() or _sha256(source_path) != expected_hash:
                raise ValueError("Phase199 implementation source has changed")
        baseline_inputs = {
            "input_bundle_manifest_sha256": _sha256(bundle / "manifest.json"),
            "input_graph_rules_sha256": _sha256(rules_path),
            "input_selected_witnesses_sha256": _sha256(witness_path),
            "input_selected_basis_atoms_sha256": _sha256(bundle / "graph" / "selected_basis_atoms.txt"),
            "input_sense_index_sha256": _sha256(index_path),
            "input_checksums_index_sha256": _sha256(checksum_path),
            "integrity_lock_sha256": _sha256(integrity_lock),
        }
        if any(prior.get(key) != value for key, value in baseline_inputs.items()):
            raise ValueError("Phase199 payload baseline does not match current frozen inputs")
        if hashlib.sha256(prior_output_bytes).hexdigest() != prior.get("output_sha256"):
            raise ValueError("Phase199 payload output does not match its recorded SHA-256")
        prior_output = json.loads(prior_output_bytes.decode("utf-8"))
        if not (
            prior.get("selected_source_payload_integrity_valid") is True
            and prior.get("compact_source_payload_integrity_valid") is True
            and prior.get("checksum_mismatch_count") == 0
            and prior.get("selected_document_head_identity_mismatch_count") == 0
            and prior.get("compact_document_head_identity_mismatch_count") == 0
            and prior_output.get("payload_hashes_verified") is True
        ):
            raise ValueError("Phase199 payload baseline is not fully valid")

        baseline_pairs = {
            (document, head)
            for head, documents in baseline_documents_by_head.items()
            for document in documents
        }
        alternative_pairs = {
            (document, head)
            for head, documents in alternative_documents_by_head.items()
            for document in documents
        }
        new_pairs = alternative_pairs - baseline_pairs
        new_documents_by_head: dict[str, set[str]] = {}
        for document, head in new_pairs:
            new_documents_by_head.setdefault(document, set()).add(head)

        checksum_mismatches = 0
        identity_mismatches = 0
        bytes_read = 0
        for document, expected_heads in new_documents_by_head.items():
            checksum = checksums.get(document)
            if not isinstance(checksum, dict):
                checksum_mismatches += 1
                continue
            expected_hash = checksum.get("sha256")
            expected_bytes = checksum.get("bytes")
            if not isinstance(expected_hash, str) or type(expected_bytes) is not int:
                checksum_mismatches += 1
                continue
            raw, source = _read_source(_safe_source_path(bundle, document, maximum_source_bytes))
            bytes_read += len(raw)
            if hashlib.sha256(raw).hexdigest() != expected_hash or len(raw) != expected_bytes:
                checksum_mismatches += 1
                continue
            synset = source.get("synset") if isinstance(source.get("synset"), dict) else {}
            identity = source.get("synset_id") or source.get("sense_id") or synset.get("synset_id")
            identity_mismatches += sum(identity != head for head in expected_heads)
        payload_verification = {
            "requested": True,
            "baseline_source": "Phase199 selected-plus-compact witness payload and identity audit",
            "baseline_reused": True,
            "baseline_document_head_pair_count": len(baseline_pairs),
            "new_minimum_depth_document_head_pair_count": len(new_pairs),
            "new_distinct_source_documents": len(new_documents_by_head),
            "new_payload_bytes_read": bytes_read,
            "checksum_mismatch_count": checksum_mismatches,
            "identity_mismatch_count": identity_mismatches,
            "all_minimum_depth_alternative_source_pairs_verified": (
                checksum_mismatches == 0 and identity_mismatches == 0
            ),
        }
    return {
        "schema_version": "minimum-depth-alternative-source-audit/1",
        "scope": "minimum_depth_clause_source_index_metadata_only",
        "bundle_integrity_valid": True,
        "selected_witness_all_valid": True,
        "selected_witness_all_minimum_depth": selected_min_depth,
        "payloads_read_this_run": payload_verification["new_distinct_source_documents"],
        "payload_bytes_read_this_run": payload_verification["new_payload_bytes_read"],
        "source_gloss_semantically_reviewed": False,
        "source_map": source_map_info,
        "semantic_support_assessed": False,
        "graph_counts": {
            "heads": len(heads),
            "basis_atoms": len(basis),
            "clauses": len(clauses),
            "dependency_literals": literal_count,
        },
        "minimum_depth_clause_alternatives": {
            "nonbasis_heads": head_count,
            "alternative_clause_count": alternative_clause_total,
            "alternatives_per_head": _distribution(alternative_counts),
            "minimum_depth": _distribution(minimum_depths),
            "heads_with_multiple_minimum_clauses": heads_with_multiple_minimum_clauses,
            "clauses_with_source_links": clauses_with_links,
            "clauses_without_source_links": clauses_without_links,
            "source_document_links_across_alternatives": clause_source_document_links,
            "source_documents_missing_head_source_records_metadata": clause_source_documents_missing_index_metadata,
            "source_documents_missing_checksum_metadata": clause_source_documents_missing_checksum_metadata,
            "distinct_source_documents_across_all_minimum_depth_alternatives": len(union_documents),
            "all_alternative_union_has_checksum_metadata": source_union_checksum_complete,
        },
        "payload_verification": payload_verification,
        "single_clause_selection_coverage": {
            "canonical_tie_break": "lexicographically_smallest_minimum_depth_clause",
            "canonical_source_documents_per_head": _distribution(canonical_clause_document_counts),
            "all_minimum_depth_alternative_union_documents_per_head": _distribution(all_alternative_union_document_counts),
            "heads_where_alternatives_add_documents_beyond_canonical_choice": heads_with_additional_source_documents_beyond_canonical,
            "alternative_union_documents_omitted_by_canonical_choice_total": extra_source_documents_beyond_canonical,
            "heads_where_alternatives_add_documents_beyond_current_selected_choice": heads_with_additional_source_documents_beyond_selected,
            "alternative_union_documents_omitted_by_current_selected_choice_total": extra_source_documents_beyond_selected,
            "current_selected_clause_differs_from_canonical_minimum_depth_clause": selected_clause_differs_from_canonical,
            "current_selected_source_documents_per_head": _distribution(selected_clause_document_counts),
        },
        "input_sha256": {
            "integrity_lock": _sha256(integrity_lock),
            "manifest": _sha256(bundle / "manifest.json"),
            "hypergraph_rules": _sha256(rules_path),
            "coverage_witnesses": _sha256(witness_path),
            "sense_index": _sha256(index_path),
            "checksums_sidecar": _sha256(checksum_path),
            "analysis_source": _sha256(Path(__file__).resolve()),
        },
        "limitations": [
            "Source links, source-record metadata, and checksum metadata are structural provenance only.",
            (
                "Source payload JSON was read only for incremental checksum/identity verification; "
                "the Phase199 selected/compact baseline was reused after input and implementation hash checks."
                if verify_new_payloads else
                "No source payload bytes were read or rehashed in this metadata-only run."
            ),
            "No gloss-span support, rule correctness, license clearance, or downstream effect was evaluated.",
            "Alternative source-document union size is not a semantic-quality measure.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-new-payloads", action="store_true",
                        help="verify alternative source associations absent from the Phase199 selected/compact baseline")
    parser.add_argument("--max-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--source-map-output", type=Path,
                        help="write deterministic per-clause source associations without raw paths or sense IDs")
    args = parser.parse_args(argv)
    try:
        result = build_report(
            args.bundle, args.integrity_lock,
            verify_new_payloads=args.verify_new_payloads,
            maximum_source_bytes=args.max_source_bytes,
            source_map_output=args.source_map_output,
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "schema_version": "minimum-depth-alternative-source-audit/1",
            "integrity_valid": False,
            "error_type": type(exc).__name__,
        }, ensure_ascii=False, indent=2))
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": args.output.as_posix(),
        "bundle_integrity_valid": result["bundle_integrity_valid"],
        "nonbasis_heads": result["minimum_depth_clause_alternatives"]["nonbasis_heads"],
        "minimum_depth_clause_alternatives": result["minimum_depth_clause_alternatives"]["alternative_clause_count"],
        "heads_with_multiple_minimum_clauses": result["minimum_depth_clause_alternatives"]["heads_with_multiple_minimum_clauses"],
        "heads_where_alternatives_add_source_documents": result["single_clause_selection_coverage"]["heads_where_alternatives_add_documents_beyond_canonical_choice"],
        "payload_verification": result["payload_verification"],
        "source_map": result["source_map"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
