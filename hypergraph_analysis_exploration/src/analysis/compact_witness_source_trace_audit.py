"""Compare source trace links for selected and compact minimum-depth witnesses.

The default mode checks index metadata only. Optional payload verification
rehashes linked files and checks their synset identity, but does not assess
whether source text semantically supports a clause.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK, verify_frozen_bundle_integrity
from src.analysis.frozen_hypergraph_audit import DEFAULT_BUNDLE, PROJECT_ROOT, jsonl, load_graph, validate_witnesses
from src.analysis.full_source_payload_census import (
    DEFAULT_MAX_SOURCE_BYTES,
    _load_checksums,
    _read_source,
    _safe_source_path,
)
from src.analysis.minimum_witness_audit import minimum_depth_clauses_by_head, minimum_derivation_depths
from src.analysis.witness_tree_expansion_audit import minimum_tree_witness_rows


DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase198" / "compact_witness_source_trace_current.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clause_source_documents(index_row: dict[str, Any], clause_index: int) -> set[str]:
    documents: set[str] = set()
    entries = index_row.get("active_clause_sources")
    if not isinstance(entries, list):
        return documents
    for entry in entries:
        if not isinstance(entry, dict) or type(entry.get("clause_index")) is not int:
            continue
        if entry["clause_index"] != clause_index:
            continue
        values = entry.get("source_documents")
        if isinstance(values, list):
            documents.update(value for value in values if isinstance(value, str) and value)
    return documents


def _profile_choice(
    witness: dict[str, Any],
    index_row: dict[str, Any],
    rules: dict[str, list[list[str]]],
    checksums: dict[str, dict[str, Any]],
    document_ref_counts: Counter[str],
    document_heads: dict[str, set[str]],
) -> dict[str, int]:
    if witness["is_seed"]:
        return {"rule_count": 0, "rules_with_source_links": 0, "rules_without_source_links": 0,
                "source_document_links": 0, "source_documents_missing_index_metadata": 0,
                "source_documents_missing_checksum_metadata": 0}
    body = witness["witness_clause"]
    matching = [i for i, clause in enumerate(rules[witness["head"]]) if sorted(clause) == sorted(body)]
    if not matching:
        raise ValueError("witness clause is absent from graph rules")
    documents = _clause_source_documents(index_row, matching[0])
    source_rows = index_row.get("source_records")
    source_paths = {
        row.get("path") for row in source_rows
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    } if isinstance(source_rows, list) else set()
    missing_index = len(documents - source_paths)
    missing_checksum = 0
    for document in documents:
        checksum = checksums.get(document)
        if (not isinstance(checksum, dict)
                or not isinstance(checksum.get("sha256"), str)
                or type(checksum.get("bytes")) is not int):
            missing_checksum += 1
        document_ref_counts[document] += 1
        document_heads.setdefault(document, set()).add(witness["head"])
    return {
        "rule_count": 1,
        "rules_with_source_links": int(bool(documents)),
        "rules_without_source_links": int(not documents),
        "source_document_links": len(documents),
        "source_documents_missing_index_metadata": missing_index,
        "source_documents_missing_checksum_metadata": missing_checksum,
    }


def _summarize_profile(counts: Counter[str], docs: Counter[str]) -> dict[str, Any]:
    return {
        **dict(sorted(counts.items())),
        "distinct_source_documents": len(docs),
        "source_documents_reused_by_multiple_rules": sum(value > 1 for value in docs.values()),
        "max_rules_per_source_document": max(docs.values(), default=0),
    }


def build_report(
    bundle: Path = DEFAULT_BUNDLE,
    integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
    *,
    verify_payloads: bool = False,
    maximum_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> dict[str, Any]:
    if not isinstance(maximum_source_bytes, int) or isinstance(maximum_source_bytes, bool) or maximum_source_bytes < 1:
        raise ValueError("maximum_source_bytes must be a positive integer")
    bundle = bundle.resolve()
    integrity = verify_frozen_bundle_integrity(bundle, integrity_lock.resolve())
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity verification failed")
    rules, clauses, _ = load_graph(bundle)
    heads = set(rules)
    basis_path = bundle / "graph" / "selected_basis_atoms.txt"
    basis = {line.strip() for line in basis_path.read_text(encoding="utf-8").splitlines() if line.strip()}
    witness_path = bundle / "graph" / "coverage_witnesses.jsonl"
    selected_check = validate_witnesses(heads, basis, rules, list(jsonl(witness_path)))
    if not selected_check["all_valid"]:
        raise ValueError("selected witness certificate failed validation")
    depths = minimum_derivation_depths(heads, clauses, basis)
    clauses_by_head = minimum_depth_clauses_by_head(heads, clauses, depths, basis)
    compact_rows, _ = minimum_tree_witness_rows(heads, basis, depths, clauses_by_head)
    compact_check = validate_witnesses(heads, basis, rules, compact_rows)
    if not compact_check["all_valid"]:
        raise ValueError("compact minimum-depth witness certificate failed validation")

    selected = selected_check["witness_by_head"]
    compact = compact_check["witness_by_head"]
    if any(selected[head]["proof_depth"] != depths[head] for head in heads - basis):
        raise ValueError("selected witness is not minimum-depth for every nonbasis head")
    changed_clauses = sum(
        sorted(selected[head]["witness_clause"]) != sorted(compact[head]["witness_clause"])
        for head in heads - basis
    )

    checksums, checksums_hash = _load_checksums(bundle)
    index_path = bundle / "indexes" / "senses.jsonl"
    selected_counts: Counter[str] = Counter()
    compact_counts: Counter[str] = Counter()
    selected_docs: Counter[str] = Counter()
    compact_docs: Counter[str] = Counter()
    selected_doc_heads: dict[str, set[str]] = {}
    compact_doc_heads: dict[str, set[str]] = {}
    seen: set[str] = set()
    with index_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict) or not isinstance(row.get("identity"), str):
                raise ValueError(f"malformed sense index row {line_number}")
            head = row["identity"]
            if head not in heads or head in seen:
                raise ValueError("sense index has an unknown or duplicate graph identity")
            seen.add(head)
            selected_result = _profile_choice(
                selected[head], row, rules, checksums, selected_docs, selected_doc_heads
            )
            compact_result = _profile_choice(
                compact[head], row, rules, checksums, compact_docs, compact_doc_heads
            )
            selected_counts.update(selected_result)
            compact_counts.update(compact_result)
    if seen != heads:
        raise ValueError("sense index and graph head sets differ")

    payload_audit: dict[str, Any] = {
        "requested": verify_payloads,
        "distinct_source_documents_read": 0,
        "distinct_source_documents_verified": 0,
        "payload_bytes_read": 0,
        "checksum_mismatch_count": None,
        "selected_document_head_pair_count": sum(map(len, selected_doc_heads.values())),
        "selected_document_head_identity_mismatch_count": None,
        "selected_source_documents_verified": None,
        "compact_document_head_pair_count": sum(map(len, compact_doc_heads.values())),
        "compact_document_head_identity_mismatch_count": None,
        "compact_source_documents_verified": None,
    }
    if verify_payloads:
        mismatch_count = 0
        identity_mismatch_selected = 0
        identity_mismatch_compact = 0
        verified_payloads: dict[str, str | None] = {}
        payload_bytes = 0
        for document in sorted(set(selected_doc_heads) | set(compact_doc_heads)):
            checksum = checksums.get(document)
            if not isinstance(checksum, dict):
                mismatch_count += 1
                continue
            expected_hash = checksum.get("sha256")
            expected_bytes = checksum.get("bytes")
            if not isinstance(expected_hash, str) or type(expected_bytes) is not int:
                mismatch_count += 1
                continue
            source_path = _safe_source_path(bundle, document, maximum_source_bytes)
            raw, source = _read_source(source_path)
            payload_bytes += len(raw)
            observed_hash = hashlib.sha256(raw).hexdigest()
            if observed_hash != expected_hash or len(raw) != expected_bytes:
                mismatch_count += 1
                continue
            synset = source.get("synset") if isinstance(source.get("synset"), dict) else {}
            source_identity = source.get("synset_id") or source.get("sense_id") or synset.get("synset_id")
            verified_payloads[document] = source_identity
            if any(source_identity != head for head in selected_doc_heads.get(document, set())):
                identity_mismatch_selected += sum(
                    source_identity != head for head in selected_doc_heads.get(document, set())
                )
            if any(source_identity != head for head in compact_doc_heads.get(document, set())):
                identity_mismatch_compact += sum(
                    source_identity != head for head in compact_doc_heads.get(document, set())
                )
        payload_audit.update({
            "distinct_source_documents_read": len(set(selected_doc_heads) | set(compact_doc_heads)),
            "distinct_source_documents_verified": len(verified_payloads),
            "payload_bytes_read": payload_bytes,
            "checksum_mismatch_count": mismatch_count,
            "selected_document_head_identity_mismatch_count": identity_mismatch_selected,
            "selected_source_documents_verified": sum(document in verified_payloads for document in selected_doc_heads),
            "compact_document_head_identity_mismatch_count": identity_mismatch_compact,
            "compact_source_documents_verified": sum(document in verified_payloads for document in compact_doc_heads),
        })
    payloads_all_verified = (
        verify_payloads
        and payload_audit["checksum_mismatch_count"] == 0
        and payload_audit["distinct_source_documents_verified"] == payload_audit["distinct_source_documents_read"]
    )
    payload_audit["selected_source_payload_integrity_valid"] = bool(
        payloads_all_verified and payload_audit["selected_document_head_identity_mismatch_count"] == 0
    )
    payload_audit["compact_source_payload_integrity_valid"] = bool(
        payloads_all_verified and payload_audit["compact_document_head_identity_mismatch_count"] == 0
    )

    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    return {
        "audit_version": "compact-witness-source-trace/1",
        "bundle_integrity_valid": True,
        "selected_witness_certificate_valid": selected_check["all_valid"],
        "compact_minimum_depth_witness_certificate_valid": compact_check["all_valid"],
        "selected_witnesses_minimum_depth": True,
        "graph_rules_sha256": _sha256(rules_path),
        "selected_witnesses_sha256": _sha256(witness_path),
        "sense_index_sha256": _sha256(index_path),
        "checksums_index_sha256": checksums_hash,
        "graph_head_count": len(heads),
        "basis_count": len(basis),
        "nonbasis_rule_count": len(heads - basis),
        "changed_clause_choice_count": changed_clauses,
        "selected_witness_source_trace": _summarize_profile(selected_counts, selected_docs),
        "compact_witness_source_trace": _summarize_profile(compact_counts, compact_docs),
        "payload_verification": payload_audit,
        "payload_hashes_verified": bool(payloads_all_verified),
        "identities_or_paths_emitted": False,
        "raw_text_emitted": False,
        "interpretation_limit": "This verifies clause-to-index-source-document links, source_records metadata coverage, and checksum-sidecar entry presence only. It does not rehash payload bytes or judge gloss-span semantic support, WSD correctness, clause meaning, licensing, or runtime efficiency.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-payloads", action="store_true",
                        help="read every linked source payload and verify checksum plus synset identity")
    parser.add_argument("--max-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project")
    if output.exists():
        parser.error(f"output exists; choose a new path: {output}")
    try:
        report = build_report(
            args.bundle,
            args.integrity_lock,
            verify_payloads=args.verify_payloads,
            maximum_source_bytes=args.max_source_bytes,
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with output.open("xb") as stream:
        stream.write(payload)
    print(json.dumps({
        "output": str(output.relative_to(PROJECT_ROOT)),
        "output_sha256": hashlib.sha256(payload).hexdigest(),
        "changed_clause_choice_count": report["changed_clause_choice_count"],
        "selected_rules_with_source_links": report["selected_witness_source_trace"]["rules_with_source_links"],
        "compact_rules_with_source_links": report["compact_witness_source_trace"]["rules_with_source_links"],
        "payload_verification": report["payload_verification"],
    }, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
