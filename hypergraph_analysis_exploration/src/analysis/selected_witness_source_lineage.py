"""Verify source-file lineage and checksums for every selected-witness clause.

This audits traceability from the frozen witness clause through the sense index
to active source payloads. It does not judge whether a payload semantically
supports a graph literal or whether a rule is true of the represented concept.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.full_source_payload_census import (
    DEFAULT_MAX_SOURCE_BYTES,
    _load_checksums,
    _read_source,
    _safe_source_path,
)
from src.analysis.frozen_hypergraph_audit import (
    DEFAULT_BUNDLE,
    PROJECT_ROOT,
    jsonl,
    load_graph,
    validate_witnesses,
)
from src.analysis.frozen_bundle_integrity import (
    DEFAULT_INTEGRITY_LOCK,
    verify_frozen_bundle_integrity,
)
from src.analysis.minimum_witness_audit import distribution_summary


DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase19" / "selected_witness_source_lineage.json"


def audit_selected_witness_sources(
    bundle: Path,
    *,
    maximum_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
    integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
) -> dict[str, Any]:
    if not isinstance(maximum_source_bytes, int) or isinstance(maximum_source_bytes, bool) or maximum_source_bytes < 1:
        raise ValueError("maximum_source_bytes must be a positive integer")
    bundle = bundle.resolve()
    bundle_integrity = verify_frozen_bundle_integrity(bundle, integrity_lock)
    if not bundle_integrity["valid"]:
        raise ValueError(
            "frozen bundle integrity lock failed: "
            + ", ".join(bundle_integrity["errors"])
        )
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    index_path = bundle / "indexes" / "senses.jsonl"
    witness_path = bundle / "graph" / "coverage_witnesses.jsonl"
    basis_path = bundle / "graph" / "selected_basis_atoms.txt"
    graph_hash = hashlib.sha256(rules_path.read_bytes()).hexdigest()
    index_hash = hashlib.sha256(index_path.read_bytes()).hexdigest()
    witness_hash = hashlib.sha256(witness_path.read_bytes()).hexdigest()
    basis_bytes = basis_path.read_bytes()
    basis_hash = hashlib.sha256(basis_bytes).hexdigest()
    if manifest.get("graph_sha256") and graph_hash != manifest["graph_sha256"]:
        raise ValueError("graph rules SHA-256 does not match bundle manifest")

    rules, _, _ = load_graph(bundle)
    heads = set(rules)
    basis = {
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt")
        .read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    witness_rows = list(jsonl(witness_path))
    witness_check = validate_witnesses(heads, basis, rules, witness_rows)
    if not witness_check["all_valid"]:
        raise ValueError("selected witness graph failed structural validation")
    witness_by_head = witness_check["witness_by_head"]
    checksums, checksums_hash = _load_checksums(bundle)
    basis_checksum = checksums.get("graph/selected_basis_atoms.txt")
    basis_matches_checksums = (
        isinstance(basis_checksum, dict)
        and basis_checksum.get("sha256") == basis_hash
        and basis_checksum.get("bytes") == len(basis_bytes)
    )
    if not basis_matches_checksums:
        raise ValueError("selected basis file does not match bundle checksums")

    selected_rule_count = seed_count = missing_lineage = missing_source_metadata = 0
    selected_source_links = source_bytes = 0
    source_doc_ref_counts: Counter[str] = Counter()
    source_docs_per_rule: list[int] = []
    witness_depth_source_links: dict[str, int] = Counter()
    payload_hash_mismatches = payload_identity_mismatches = 0
    verified_payloads: dict[str, tuple[int, str]] = {}

    with index_path.open("r", encoding="utf-8") as stream:
        indexed_heads: set[str] = set()
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict) or not isinstance(row.get("identity"), str):
                raise ValueError(f"malformed sense index record at line {line_number}")
            head = row["identity"]
            if head not in heads:
                raise ValueError("sense index contains a head absent from graph rules")
            if head in indexed_heads:
                raise ValueError("sense index contains a duplicate identity")
            indexed_heads.add(head)
            witness = witness_by_head[head]
            if witness["is_seed"]:
                seed_count += 1
                continue

            body = witness["witness_clause"]
            matching = [index for index, clause in enumerate(rules[head])
                        if sorted(clause) == sorted(body)]
            if not matching:
                raise ValueError("selected witness clause is absent from graph rules")
            selected_clause_index = matching[0]
            selected_rule_count += 1
            source_rows = row.get("source_records")
            source_paths = {
                source.get("path")
                for source in source_rows
                if isinstance(source, dict) and isinstance(source.get("path"), str)
            } if isinstance(source_rows, list) else set()
            entries = row.get("active_clause_sources")
            docs: set[str] = set()
            if not isinstance(entries, list):
                entries = []
            for entry in entries:
                if not isinstance(entry, dict) or entry.get("clause_index") != selected_clause_index:
                    continue
                values = entry.get("source_documents")
                if isinstance(values, list):
                    docs.update(value for value in values if isinstance(value, str) and value)
            if not docs:
                missing_lineage += 1
            if docs - source_paths:
                missing_source_metadata += len(docs - source_paths)

            source_docs_per_rule.append(len(docs))
            depth = witness["proof_depth"]
            depth_bucket = "1-5" if depth <= 5 else "6-25" if depth <= 25 else "26-100" if depth <= 100 else "101-300" if depth <= 300 else "301+"
            witness_depth_source_links[depth_bucket] += len(docs)
            for relative in sorted(docs):
                source_doc_ref_counts[relative] += 1
                selected_source_links += 1
                checksum_row = checksums.get(relative)
                if (not isinstance(checksum_row, dict)
                        or not isinstance(checksum_row.get("sha256"), str)
                        or type(checksum_row.get("bytes")) is not int):
                    payload_hash_mismatches += 1
                    continue
                cached = verified_payloads.get(relative)
                if cached is None:
                    source_path = _safe_source_path(bundle, relative, maximum_source_bytes)
                    raw, source = _read_source(source_path)
                    observed_hash = hashlib.sha256(raw).hexdigest()
                    if observed_hash != checksum_row["sha256"] or len(raw) != checksum_row["bytes"]:
                        payload_hash_mismatches += 1
                        continue
                    synset = source.get("synset") if isinstance(source.get("synset"), dict) else {}
                    source_identity = source.get("synset_id") or source.get("sense_id") or synset.get("synset_id")
                    cached = (len(raw), source_identity)
                    verified_payloads[relative] = cached
                    source_bytes += len(raw)
                source_identity = cached[1]
                if source_identity != head:
                    payload_identity_mismatches += 1

    if indexed_heads != heads:
        raise ValueError("sense index and graph head sets differ")
    if payload_hash_mismatches:
        raise ValueError("one or more selected witness source payloads failed checksum verification")

    source_fanout = list(source_doc_ref_counts.values())
    implementation_files = (
        "src/analysis/selected_witness_source_lineage.py",
        "src/analysis/frozen_bundle_integrity.py",
        "src/analysis/frozen_hypergraph_audit.py",
        "src/analysis/full_source_payload_census.py",
        "src/analysis/minimum_witness_audit.py",
    )
    implementation_hashes = {
        relative: hashlib.sha256((PROJECT_ROOT / relative).read_bytes()).hexdigest()
        for relative in implementation_files
    }
    return {
        "audit_version": "selected-witness-source-lineage/2",
        "input_sha256": {
            "manifest": bundle_integrity["observed_sha256"]["manifest.json"],
            "graph_rules": graph_hash,
            "sense_index": index_hash,
            "selected_witnesses": witness_hash,
            "checksums_index": checksums_hash,
            "selected_basis_atoms": basis_hash,
            "integrity_lock": hashlib.sha256(integrity_lock.read_bytes()).hexdigest(),
        },
        "implementation": {
            "schema": "selected-witness-source-lineage-implementation/1",
            "sha256": implementation_hashes,
            "python_version": sys.version,
            "platform": platform.platform(),
        },
        "bundle_integrity": {
            "valid": bundle_integrity["valid"],
            "observed_sha256": bundle_integrity["observed_sha256"],
            "selected_basis_matches_checksums": basis_matches_checksums,
        },
        "counts": {
            "graph_head_count": len(heads),
            "basis_seed_count": seed_count,
            "selected_rule_count": selected_rule_count,
            "selected_rules_with_source_links": selected_rule_count - missing_lineage,
            "selected_rules_without_source_links": missing_lineage,
            "source_document_links_for_selected_rules": selected_source_links,
            "distinct_source_documents_for_selected_rules": len(source_doc_ref_counts),
            "source_documents_linked_to_multiple_selected_rules": sum(count > 1 for count in source_fanout),
            "source_document_links_missing_index_source_metadata": missing_source_metadata,
            "selected_source_payload_bytes_verified": source_bytes,
            "distinct_selected_source_payloads_verified": len(verified_payloads),
            "selected_source_payload_identity_mismatches": payload_identity_mismatches,
            "selected_source_payload_checksum_mismatches": payload_hash_mismatches,
        },
        "distribution": {
            "source_documents_per_selected_rule": distribution_summary(source_docs_per_rule),
            "selected_rules_per_source_document": distribution_summary(source_fanout),
            "source_document_links_by_witness_depth": dict(sorted(witness_depth_source_links.items())),
        },
        "validation": {
            "frozen_bundle_integrity_lock_valid": bundle_integrity["valid"],
            "selected_basis_matches_checksums": basis_matches_checksums,
            "selected_witness_graph_valid": witness_check["all_valid"],
            "all_selected_rules_have_source_links": missing_lineage == 0,
            "all_source_links_resolve_to_index_source_records": missing_source_metadata == 0,
            "all_selected_source_payloads_match_checksums": payload_hash_mismatches == 0,
            "all_selected_source_payloads_match_witness_head_identity": payload_identity_mismatches == 0,
        },
        "raw_text_emitted": False,
        "identities_or_paths_emitted": False,
        "interpretation_limit": "This verifies structural source-document lineage, file checksum, and source-record/head identity for selected witness clauses. It does not verify source-span support, WSD correctness, rule direction, gloss entailment, or license clearance.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--max-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project directory")
    if args.max_source_bytes < 1:
        parser.error("--max-source-bytes must be positive")
    if output.exists() and not args.force:
        parser.error(f"output exists; pass --force to replace: {output}")
    try:
        report = audit_selected_witness_sources(
            args.bundle,
            maximum_source_bytes=args.max_source_bytes,
            integrity_lock=args.integrity_lock.resolve(),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "Verified source lineage for "
        f"{report['counts']['selected_rule_count']} selected witness clauses; "
        f"wrote aggregate-only report to {output.relative_to(PROJECT_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
