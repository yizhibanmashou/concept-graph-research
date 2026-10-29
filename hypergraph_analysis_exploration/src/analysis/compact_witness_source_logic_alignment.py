"""Compare source logic/WSD branches for clauses changed by compact witnesses.

This aggregate audit checks source-index linkage, payload bytes, and structural
overlap between graph clauses and source-part WSD synset-ID unions. It is not a
semantic-support or entailment judgment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
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
from src.analysis.source_clause_alignment_audit import _dnf_part_branches
from src.analysis.witness_tree_expansion_audit import minimum_tree_witness_rows


DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase200" / "compact_witness_source_logic_alignment.json"
STRATEGIES = ("selected", "compact")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _choice_clause_index(head: str, witness: dict[str, Any], rules: dict[str, list[list[str]]]) -> int:
    body = witness["witness_clause"]
    matches = [index for index, clause in enumerate(rules[head]) if sorted(clause) == sorted(body)]
    if not matches:
        raise ValueError("witness clause is absent from graph rules")
    return matches[0]


def _choice_documents(index_row: dict[str, Any], clause_index: int) -> set[str]:
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


def _mapped_wsd_branches(source: dict[str, Any], branches: list[frozenset[str]]) -> list[frozenset[str]]:
    results = source.get("part_results")
    result_by_part = {
        result.get("part_id"): result
        for result in results
        if isinstance(result, dict) and isinstance(result.get("part_id"), str)
    } if isinstance(results, list) else {}
    mapped_branches: list[frozenset[str]] = []
    for branch in branches:
        mapped: set[str] = set()
        for part_id in branch:
            result = result_by_part.get(part_id, {})
            wsd = result.get("wsd") if isinstance(result, dict) else None
            ids = wsd.get("sentence_synset_ids") if isinstance(wsd, dict) else None
            if isinstance(ids, list):
                mapped.update(value for value in ids if isinstance(value, str))
        mapped_branches.append(frozenset(mapped))
    return mapped_branches


def build_report(
    bundle: Path = DEFAULT_BUNDLE,
    integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
    *,
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
    changed_heads = {
        head for head in heads - basis
        if sorted(selected[head]["witness_clause"]) != sorted(compact[head]["witness_clause"])
    }

    source_index = bundle / "indexes" / "senses.jsonl"
    checksums, checksum_index_hash = _load_checksums(bundle)
    # doc -> (strategy, head, clause-body) associations; payloads are read once.
    associations: dict[str, list[tuple[str, str, frozenset[str]]]] = defaultdict(list)
    document_sets = {strategy: set() for strategy in STRATEGIES}
    seen: set[str] = set()
    missing_index_metadata = Counter()
    missing_checksum_metadata = Counter()
    with source_index.open("r", encoding="utf-8") as stream:
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
            if head not in changed_heads:
                continue
            source_rows = row.get("source_records")
            source_paths = {
                item.get("path") for item in source_rows
                if isinstance(item, dict) and isinstance(item.get("path"), str)
            } if isinstance(source_rows, list) else set()
            for strategy, witness_map in (("selected", selected), ("compact", compact)):
                clause_index = _choice_clause_index(head, witness_map[head], rules)
                clause_body = frozenset(witness_map[head]["witness_clause"])
                documents = _choice_documents(row, clause_index)
                if not documents:
                    raise ValueError("changed witness clause has no active source-document link")
                for document in documents:
                    if document not in source_paths:
                        missing_index_metadata[strategy] += 1
                    checksum = checksums.get(document)
                    if (not isinstance(checksum, dict)
                            or not isinstance(checksum.get("sha256"), str)
                            or type(checksum.get("bytes")) is not int):
                        missing_checksum_metadata[strategy] += 1
                    document_sets[strategy].add(document)
                    associations[document].append((strategy, head, clause_body))
    if seen != heads:
        raise ValueError("sense index and graph head sets differ")

    stats = {strategy: Counter() for strategy in STRATEGIES}
    exact_documents = {strategy: set() for strategy in STRATEGIES}
    subset_documents = {strategy: set() for strategy in STRATEGIES}
    verified_documents = {strategy: set() for strategy in STRATEGIES}
    alignment_by_head = {
        strategy: defaultdict(lambda: {"exact": False, "subset": False})
        for strategy in STRATEGIES
    }
    payload_checksum_mismatches = Counter()
    payload_identity_mismatches = Counter()
    payload_bytes = 0
    for document in sorted(associations):
        checksum = checksums.get(document)
        if not isinstance(checksum, dict):
            for strategy, _, _ in associations[document]:
                payload_checksum_mismatches[strategy] += 1
            continue
        expected_hash = checksum.get("sha256")
        expected_bytes = checksum.get("bytes")
        if not isinstance(expected_hash, str) or type(expected_bytes) is not int:
            for strategy, _, _ in associations[document]:
                payload_checksum_mismatches[strategy] += 1
            continue
        source_path = _safe_source_path(bundle, document, maximum_source_bytes)
        raw, source = _read_source(source_path)
        payload_bytes += len(raw)
        observed_hash = hashlib.sha256(raw).hexdigest()
        if observed_hash != expected_hash or len(raw) != expected_bytes:
            for strategy, _, _ in associations[document]:
                payload_checksum_mismatches[strategy] += 1
            continue
        synset = source.get("synset") if isinstance(source.get("synset"), dict) else {}
        source_identity = source.get("synset_id") or source.get("sense_id") or synset.get("synset_id")
        branches = _dnf_part_branches((source.get("definition") or {}).get("logic")
                                      if isinstance(source.get("definition"), dict) else None)
        mapped = _mapped_wsd_branches(source, branches) if branches is not None else []
        for strategy, head, body in associations[document]:
            stats[strategy]["source_document_head_clause_associations"] += 1
            if source_identity == head:
                verified_documents[strategy].add(document)
            else:
                payload_identity_mismatches[strategy] += 1
            if branches is None:
                stats[strategy]["logic_trees_unparsed_or_over_branch_limit"] += 1
                continue
            stats[strategy]["source_logic_branches"] += len(branches)
            if any(body == branch for branch in mapped):
                stats[strategy]["clauses_exactly_match_a_wsd_branch_union"] += 1
                exact_documents[strategy].add(document)
                alignment_by_head[strategy][head]["exact"] = True
            if any(body <= branch for branch in mapped):
                stats[strategy]["clauses_are_subset_of_a_wsd_branch_union"] += 1
                subset_documents[strategy].add(document)
                alignment_by_head[strategy][head]["subset"] = True

    paired_head_counts: dict[str, dict[str, int]] = {}
    for metric in ("exact", "subset"):
        selected_flags = alignment_by_head["selected"]
        compact_flags = alignment_by_head["compact"]
        selected_only = sum(
            bool(selected_flags[head][metric]) and not bool(compact_flags[head][metric])
            for head in changed_heads
        )
        compact_only = sum(
            bool(compact_flags[head][metric]) and not bool(selected_flags[head][metric])
            for head in changed_heads
        )
        both = sum(
            bool(selected_flags[head][metric]) and bool(compact_flags[head][metric])
            for head in changed_heads
        )
        paired_head_counts[metric] = {
            "selected_only": selected_only,
            "compact_only": compact_only,
            "both": both,
            "neither": len(changed_heads) - selected_only - compact_only - both,
            "paired_heads": len(changed_heads),
        }

    summaries: dict[str, Any] = {}
    for strategy in STRATEGIES:
        # Count at clause/document granularity; multiple changed clause links to one document remain distinct.
        strategy_associations = [item for items in associations.values() for item in items if item[0] == strategy]
        association_count = len(strategy_associations)
        summaries[strategy] = {
            "changed_heads": len(changed_heads),
            "changed_clause_source_associations": association_count,
            "distinct_source_documents": len(document_sets[strategy]),
            "source_documents_with_verified_payload_identity": len(verified_documents[strategy]),
            "payload_checksum_mismatches": payload_checksum_mismatches[strategy],
            "payload_identity_mismatch_associations": payload_identity_mismatches[strategy],
            "source_documents_with_exact_wsd_branch_union": len(exact_documents[strategy]),
            "source_documents_with_subset_wsd_branch_union": len(subset_documents[strategy]),
            **dict(sorted(stats[strategy].items())),
            "source_links_missing_head_metadata": missing_index_metadata[strategy],
            "source_links_missing_checksum_metadata": missing_checksum_metadata[strategy],
        }
    return {
        "audit_version": "compact-witness-source-logic-alignment/1",
        "bundle_integrity_valid": True,
        "selected_witness_certificate_valid": selected_check["all_valid"],
        "compact_minimum_depth_witness_certificate_valid": compact_check["all_valid"],
        "selected_witnesses_minimum_depth": all(selected[head]["proof_depth"] == depths[head] for head in heads - basis),
        "graph_rules_sha256": _sha256(bundle / "graph" / "hypergraph_rules.jsonl"),
        "selected_witnesses_sha256": _sha256(witness_path),
        "sense_index_sha256": _sha256(source_index),
        "checksums_index_sha256": checksum_index_hash,
        "changed_clause_choice_count": len(changed_heads),
        "changed_choice_source_logic_wsd_alignment": summaries,
        "paired_head_alignment_counts": paired_head_counts,
        "payload_bytes_read": payload_bytes,
        "identities_or_paths_emitted": False,
        "raw_text_emitted": False,
        "interpretation_limit": "Exact/subset overlap compares source part-ID logic branches to automatic WSD synset-ID unions only. It does not establish gloss-span semantic support, correct WSD, rule soundness, direction, or licensing.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--max-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must be inside the project")
    if output.exists():
        parser.error(f"output exists; choose a new path: {output}")
    try:
        report = build_report(args.bundle, args.integrity_lock,
                              maximum_source_bytes=args.max_source_bytes)
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
        "selected_exact_wsd_branch_document_count": report["changed_choice_source_logic_wsd_alignment"]["selected"]["source_documents_with_exact_wsd_branch_union"],
        "compact_exact_wsd_branch_document_count": report["changed_choice_source_logic_wsd_alignment"]["compact"]["source_documents_with_exact_wsd_branch_union"],
        "payload_bytes_read": report["payload_bytes_read"],
    }, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
