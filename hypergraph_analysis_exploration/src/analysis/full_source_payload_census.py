"""Scan active frozen source payloads and compare logic branches to graph clauses.

This is an aggregate-only structural census. It verifies payload readability and
compares part/logic/WSD identifiers with attributed graph clauses; it does not
judge natural-language entailment or source-rule faithfulness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from src.analysis.frozen_hypergraph_audit import DEFAULT_BUNDLE, load_graph
from src.analysis.source_clause_alignment_audit import _dnf_part_branches
from src.analysis.project_paths import PROJECT_ROOT


DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase15" / "full_source_payload_census.json"
MAX_INDEX_BYTES = 256 * 1024 * 1024
MAX_INDEX_LINE_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_SOURCE_BYTES = 16 * 1024 * 1024


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_source_path(bundle: Path, relative: Any, maximum_bytes: int) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("active source record has a missing path")
    posix = PurePosixPath(relative)
    if posix.is_absolute() or ".." in posix.parts:
        raise ValueError("active source record has an unsafe relative path")
    path = bundle.joinpath(*posix.parts).resolve()
    if not path.is_relative_to(bundle) or not path.is_file():
        raise ValueError("active source file is missing or resolves outside the frozen bundle")
    if path.stat().st_size > maximum_bytes:
        raise ValueError("active source file exceeds the configured per-file byte limit")
    return path


def _read_source(path: Path) -> tuple[bytes, dict[str, Any]]:
    raw = path.read_bytes()
    try:
        source = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("an active source payload is not valid UTF-8 JSON") from exc
    if not isinstance(source, dict):
        raise ValueError("an active source payload must be a JSON object")
    return raw, source


def _load_checksums(bundle: Path) -> tuple[dict[str, dict[str, Any]], str]:
    path = bundle / "checksums.jsonl"
    if not path.is_file():
        raise ValueError("frozen bundle checksums.jsonl is missing")
    checksums: dict[str, dict[str, Any]] = {}
    with path.open("rb") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            if len(raw_line) > MAX_INDEX_LINE_BYTES:
                raise ValueError(f"checksums.jsonl line {line_number} exceeds the 8 MiB safety limit")
            if not raw_line.strip():
                continue
            try:
                row = json.loads(raw_line)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid checksums.jsonl record at line {line_number}") from exc
            relative = row.get("path") if isinstance(row, dict) else None
            if not isinstance(relative, str) or not relative:
                raise ValueError(f"checksums.jsonl record {line_number} has no path")
            if relative in checksums:
                raise ValueError("checksums.jsonl contains duplicate paths")
            checksums[relative] = row
    return checksums, _sha256_file(path)


def audit_payloads(bundle: Path, *, maximum_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
                   progress_every: int = 5000) -> dict[str, Any]:
    bundle = bundle.resolve()
    if not isinstance(maximum_source_bytes, int) or isinstance(maximum_source_bytes, bool) or maximum_source_bytes < 1:
        raise ValueError("maximum_source_bytes must be a positive integer")
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    index_path = bundle / "indexes" / "senses.jsonl"
    if not index_path.is_file() or index_path.stat().st_size > MAX_INDEX_BYTES:
        raise ValueError("sense index is missing or exceeds the 256 MiB safety limit")

    rules, _, _ = load_graph(bundle)
    graph_path = bundle / "graph" / "hypergraph_rules.jsonl"
    graph_sha256 = _sha256_file(graph_path)
    if manifest.get("graph_sha256") and graph_sha256 != manifest["graph_sha256"]:
        raise ValueError("graph rules SHA-256 does not match bundle manifest")
    checksums, checksums_sha256 = _load_checksums(bundle)

    counts: Counter[str] = Counter()
    logic_ops: Counter[str] = Counter()
    per_source_digest = hashlib.sha256()
    payload_bytes = 0
    total_senses = 0
    payloads_processed = 0
    malformed_active_entries = 0

    with index_path.open("rb") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            if not raw_line.strip():
                continue
            if len(raw_line) > MAX_INDEX_LINE_BYTES:
                raise ValueError(f"sense index line {line_number} exceeds the 8 MiB safety limit")
            try:
                row = json.loads(raw_line)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid sense-index JSON at line {line_number}") from exc
            if not isinstance(row, dict) or not isinstance(row.get("identity"), str):
                raise ValueError(f"malformed sense-index record at line {line_number}")
            identity = row["identity"]
            if identity not in rules:
                raise ValueError("sense index contains an identity absent from graph rules")
            total_senses += 1
            clauses = rules[identity]

            active_by_path: dict[str, set[int]] = defaultdict(set)
            for entry in row.get("active_clause_sources", []):
                if not isinstance(entry, dict) or type(entry.get("clause_index")) is not int:
                    malformed_active_entries += 1
                    continue
                clause_index = entry["clause_index"]
                documents = entry.get("source_documents")
                if clause_index < 0 or clause_index >= len(clauses) or not isinstance(documents, list) or not documents:
                    malformed_active_entries += 1
                    continue
                for document in documents:
                    if not isinstance(document, str) or not document:
                        malformed_active_entries += 1
                        continue
                    active_by_path[document].add(clause_index)

            source_rows = row.get("source_records")
            if not isinstance(source_rows, list):
                raise ValueError("sense-index source_records field is malformed")
            for source_meta in source_rows:
                if not isinstance(source_meta, dict):
                    counts["malformed_source_metadata_records"] += 1
                    continue
                relative = source_meta.get("path")
                if not isinstance(relative, str) or relative not in active_by_path:
                    continue
                indexes = sorted(active_by_path[relative])
                source_path = _safe_source_path(bundle, relative, maximum_source_bytes)
                raw, source = _read_source(source_path)
                checksum_row = checksums.get(relative)
                expected_sha256 = checksum_row.get("sha256") if isinstance(checksum_row, dict) else None
                expected_bytes = checksum_row.get("bytes") if isinstance(checksum_row, dict) else None
                observed_sha256 = hashlib.sha256(raw).hexdigest()
                if (not isinstance(expected_sha256, str) or len(expected_sha256) != 64
                        or type(expected_bytes) is not int
                        or expected_sha256 != observed_sha256 or expected_bytes != len(raw)):
                    raise ValueError("active source payload does not match its frozen checksums.jsonl entry")
                counts["active_source_payload_checksum_matches"] += 1
                payloads_processed += 1
                payload_bytes += len(raw)
                file_digest = bytes.fromhex(observed_sha256)
                per_source_digest.update(len(raw).to_bytes(8, "big"))
                per_source_digest.update(file_digest)
                definition = source.get("definition") if isinstance(source.get("definition"), dict) else {}
                synset = source.get("synset") if isinstance(source.get("synset"), dict) else {}
                parts = definition.get("parts")
                parts = parts if isinstance(parts, list) else []
                part_ids = [part.get("part_id") for part in parts
                            if isinstance(part, dict) and isinstance(part.get("part_id"), str)]
                unique_parts = len(part_ids) == len(parts) and len(set(part_ids)) == len(part_ids)
                counts["source_payloads_with_unique_part_ids"] += int(unique_parts)
                counts["source_parts"] += len(parts)

                logic = definition.get("logic")
                logic_ops[logic.get("op", "missing_or_invalid") if isinstance(logic, dict) else "missing_or_invalid"] += 1
                branches = _dnf_part_branches(logic)
                graph_clauses = [frozenset(clauses[index]) for index in indexes]
                counts["active_source_clause_links"] += len(indexes)
                counts["active_source_payloads"] += 1
                if branches is None:
                    counts["logic_trees_unparsed_or_exceeding_expansion_limit"] += 1
                    continue
                counts["logic_trees_parsed"] += 1
                leaves = set().union(*branches) if branches else set()
                if unique_parts and leaves == set(part_ids):
                    counts["logic_leaf_sets_match_parts"] += 1
                if len(branches) == len(indexes):
                    counts["branch_count_matches_attributed_clause_count"] += 1
                else:
                    counts["branch_count_differs_from_attributed_clause_count"] += 1
                if Counter(branches) == Counter(graph_clauses):
                    counts["part_id_branch_multisets_match_graph_literal_ids"] += 1

                part_results = source.get("part_results")
                result_by_part = {
                    result.get("part_id"): result
                    for result in part_results
                    if isinstance(result, dict) and isinstance(result.get("part_id"), str)
                } if isinstance(part_results, list) else {}
                mapped_branches: list[frozenset[str]] = []
                wsd_complete = True
                for branch in branches:
                    mapped: set[str] = set()
                    for part_id in branch:
                        result = result_by_part.get(part_id)
                        wsd = result.get("wsd") if isinstance(result, dict) else None
                        ids = wsd.get("sentence_synset_ids") if isinstance(wsd, dict) else None
                        if not isinstance(ids, list) or not ids or any(not isinstance(value, str) for value in ids):
                            wsd_complete = False
                        elif isinstance(ids, list):
                            mapped.update(ids)
                    mapped_branches.append(frozenset(mapped))
                counts["logic_trees_with_complete_part_wsd_ids"] += int(wsd_complete)
                if wsd_complete and Counter(mapped_branches) == Counter(graph_clauses):
                    counts["wsd_branch_id_multisets_match_graph_literal_ids"] += 1
                if wsd_complete:
                    for graph_clause in graph_clauses:
                        exact = any(graph_clause == branch for branch in mapped_branches)
                        subset = any(graph_clause < branch for branch in mapped_branches)
                        overlap = any(graph_clause & branch for branch in mapped_branches)
                        if exact:
                            relation = "exact_branch_match"
                        elif subset:
                            relation = "proper_subset_of_branch"
                        elif overlap:
                            relation = "partial_overlap_only"
                        else:
                            relation = "disjoint_from_all_branches"
                        counts[f"graph_clause_wsd_relation_{relation}"] += 1
                        if any(graph_clause <= branch for branch in mapped_branches):
                            counts["graph_clauses_subset_of_a_wsd_branch_union"] += 1
                        if any(graph_clause == branch for branch in mapped_branches):
                            counts["graph_clauses_equal_a_wsd_branch_union"] += 1
                else:
                    counts["graph_clause_wsd_comparison_skipped_incomplete"] += len(graph_clauses)

                raw_definition = synset.get("raw_definition")
                effective_definition = definition.get("definition")
                if isinstance(raw_definition, str) and isinstance(effective_definition, str):
                    counts["payloads_with_raw_effective_text_comparison"] += 1
                    counts["payloads_with_raw_effective_text_difference"] += int(raw_definition != effective_definition)

            if progress_every > 0 and total_senses % progress_every == 0:
                print(f"Scanned {total_senses} senses; read {payloads_processed} active source payloads", flush=True)

    expected_senses = manifest.get("sense_count")
    return {
        "audit_version": "full-active-source-payload-structure/1",
        "graph_rules_sha256": graph_sha256,
        "sense_index_sha256": _sha256_file(index_path),
        "checksums_index_sha256": checksums_sha256,
        "payload_sequence_sha256": per_source_digest.hexdigest(),
        "counts": {
            "sense_index_records": total_senses,
            "manifest_expected_senses": expected_senses,
            "sense_count_matches_manifest": total_senses == expected_senses if isinstance(expected_senses, int) else None,
            "active_source_payloads_read": payloads_processed,
            "active_source_payloads_checksum_matched": counts["active_source_payload_checksum_matches"],
            "all_active_payloads_match_frozen_checksums": (
                counts["active_source_payload_checksum_matches"] == payloads_processed
            ),
            "active_source_payload_total_bytes": payload_bytes,
            "active_clause_source_entries_malformed": malformed_active_entries,
            **dict(sorted(counts.items())),
        },
        "logic_operator_counts": dict(sorted(logic_ops.items())),
        "raw_text_emitted": False,
        "identities_or_paths_emitted": False,
        "scope": "all active source payloads referenced by the full frozen sense index; only hashes, byte totals and aggregate structural counts are emitted",
        "interpretation_limit": (
            "Part IDs, AND/OR branch IDs, WSD synset-ID sets and graph literal-ID sets are structural traces only. "
            "Their equality, subset relation, or mismatch does not establish source-span support, correct sense disambiguation, "
            "gloss fidelity, entailment, or rule soundness."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--max-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error(f"output exists; pass --force to replace: {output}")
    try:
        report = audit_payloads(args.bundle, maximum_source_bytes=args.max_source_bytes)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Read {report['counts']['active_source_payloads_read']} active source payloads")
    print(f"Wrote aggregate-only report: {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
