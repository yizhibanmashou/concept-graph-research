"""Profile aggregate source-decomposition metadata in a frozen WordNet index.

This is a structural coverage audit, not a semantic validation. Raw identities,
definitions, lemmas, and source paths are read only as needed for aggregation
and are never emitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:  # Direct script execution and package/module execution are both supported.
    from .project_paths import PROJECT_ROOT, configured_bundle_root
except ImportError:
    from project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_BUNDLE = configured_bundle_root()
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase8" / "full_source_index_audit.json"
MAX_INDEX_BYTES = 256 * 1024 * 1024
MAX_LINE_BYTES = 8 * 1024 * 1024
VALID_POS = {"n", "v", "a", "r"}
VALID_STATUS = {"success", "partial", "failed", "error"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bucket(value: Any, allowed: set[str]) -> str:
    return value if isinstance(value, str) and value in allowed else "other_or_missing"


def audit_index(bundle: Path) -> dict[str, Any]:
    bundle = bundle.resolve()
    manifest_path = bundle / "manifest.json"
    index_path = bundle / "indexes" / "senses.jsonl"
    if not manifest_path.is_file() or not index_path.is_file():
        raise ValueError("bundle must contain manifest.json and indexes/senses.jsonl")
    if index_path.stat().st_size > MAX_INDEX_BYTES:
        raise ValueError("sense index exceeds the configured 256 MiB safety limit")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("bundle manifest is invalid JSON") from exc

    pos_counts: Counter[str] = Counter()
    basis_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    source_count_per_sense: Counter[int] = Counter()
    part_count_distribution: Counter[str] = Counter()
    part_vs_clause: Counter[str] = Counter()
    feature_counts: Counter[str] = Counter()
    canonical_counts: Counter[str] = Counter()
    clause_count_distribution: Counter[str] = Counter()
    active_clause_count_per_source: Counter[int] = Counter()
    active_parts_vs_clauses: Counter[str] = Counter()
    unique_identities: set[str] = set()
    sense_count = source_record_count = 0
    senses_with_any_parts = senses_with_all_parts = 0
    source_records_with_parts = source_records_matching_parts = 0
    active_clause_source_entries = active_clause_source_pairs = 0
    active_clause_source_unique_pairs = active_clause_source_duplicate_pairs = 0
    active_clause_source_missing_records = malformed_active_clause_sources = 0
    active_source_records = active_clauses = graph_clauses = 0
    graph_clauses_without_source_lineage = senses_with_all_clauses_sourced = 0
    records_with_text_difference = records_with_text_comparison = 0
    malformed_records = 0

    try:
        with index_path.open("rb") as stream:
            for line_number, raw_line in enumerate(stream, start=1):
                if len(raw_line) > MAX_LINE_BYTES:
                    raise ValueError(f"sense index line {line_number} exceeds the 8 MiB safety limit")
                if not raw_line.strip():
                    continue
                try:
                    row = json.loads(raw_line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError(f"sense index has invalid JSON at line {line_number}") from exc
                if not isinstance(row, dict):
                    raise ValueError(f"sense index line {line_number} is not an object")
                sense_count += 1
                identity = row.get("identity")
                if not isinstance(identity, str) or not identity or identity in unique_identities:
                    malformed_records += 1
                else:
                    unique_identities.add(identity)
                pos_counts[_bucket(row.get("pos"), VALID_POS)] += 1
                clause_count = row.get("graph_clause_count")
                if not isinstance(clause_count, int) or isinstance(clause_count, bool) or clause_count < 0:
                    malformed_records += 1
                    clause_count = None
                clause_count_distribution[str(clause_count) if clause_count is not None else "invalid"] += 1
                if clause_count is not None:
                    graph_clauses += clause_count
                canonical = row.get("canonical_replay_exact")
                canonical_counts[str(canonical).lower() if isinstance(canonical, bool) else "missing_or_invalid"] += 1
                basis = row.get("is_basis")
                basis_counts[str(basis).lower() if isinstance(basis, bool) else "missing_or_invalid"] += 1

                source_rows = row.get("source_records")
                if not isinstance(source_rows, list):
                    malformed_records += 1
                    source_rows = []
                source_rows_by_path: dict[str, dict[str, Any]] = {}
                source_count_per_sense[len(source_rows)] += 1
                if source_rows:
                    all_parts = True
                    any_parts = False
                else:
                    all_parts = any_parts = False
                for source in source_rows:
                    source_record_count += 1
                    if not isinstance(source, dict):
                        malformed_records += 1
                        status_counts["other_or_missing"] += 1
                        all_parts = False
                        continue
                    source_path = source.get("path")
                    if isinstance(source_path, str) and source_path:
                        if source_path in source_rows_by_path:
                            malformed_records += 1
                        source_rows_by_path[source_path] = source
                    status_counts[_bucket(source.get("status"), VALID_STATUS)] += 1
                    for field in ("has_decomposition", "has_argumentation", "has_wsd"):
                        value = source.get(field)
                        feature_counts[f"{field}_{str(value).lower() if isinstance(value, bool) else 'missing_or_invalid'}"] += 1
                    parts = source.get("parts")
                    if isinstance(parts, int) and not isinstance(parts, bool) and parts >= 0:
                        any_parts = True
                        source_records_with_parts += 1
                        part_count = parts
                        part_count_distribution[str(part_count)] += 1
                        if clause_count is not None and part_count == clause_count:
                            source_records_matching_parts += 1
                            part_vs_clause["equal"] += 1
                        elif clause_count is None:
                            part_vs_clause["clause_count_invalid"] += 1
                        elif part_count < clause_count:
                            part_vs_clause["parts_fewer"] += 1
                        else:
                            part_vs_clause["parts_more"] += 1
                    elif isinstance(parts, list):
                        any_parts = True
                        source_records_with_parts += 1
                        part_count = len(parts)
                        part_count_distribution[str(part_count)] += 1
                        if clause_count is not None and part_count == clause_count:
                            source_records_matching_parts += 1
                            part_vs_clause["equal"] += 1
                        elif clause_count is None:
                            part_vs_clause["clause_count_invalid"] += 1
                        elif part_count < clause_count:
                            part_vs_clause["parts_fewer"] += 1
                        else:
                            part_vs_clause["parts_more"] += 1
                    else:
                        all_parts = False
                        part_count_distribution["missing_or_invalid"] += 1
                        part_vs_clause["parts_missing_or_invalid"] += 1
                    raw_definition = source.get("raw_definition")
                    effective_definition = source.get("effective_definition")
                    if isinstance(raw_definition, str) and isinstance(effective_definition, str):
                        records_with_text_comparison += 1
                        if raw_definition != effective_definition:
                            records_with_text_difference += 1

                active_entries = row.get("active_clause_sources")
                if not isinstance(active_entries, list):
                    malformed_active_clause_sources += 1
                    active_entries = []
                active_by_source: dict[str, set[int]] = {}
                active_pairs_for_sense = 0
                for entry in active_entries:
                    active_clause_source_entries += 1
                    if not isinstance(entry, dict):
                        malformed_active_clause_sources += 1
                        continue
                    clause_index = entry.get("clause_index")
                    if (type(clause_index) is not int or clause_index < 0
                            or clause_count is None or clause_index >= clause_count):
                        malformed_active_clause_sources += 1
                        continue
                    documents = entry.get("source_documents")
                    if not isinstance(documents, list) or not documents:
                        malformed_active_clause_sources += 1
                        continue
                    for document in documents:
                        if not isinstance(document, str) or not document:
                            malformed_active_clause_sources += 1
                            continue
                        active_clause_source_pairs += 1
                        active_pairs_for_sense += 1
                        active_by_source.setdefault(document, set()).add(clause_index)

                unique_pairs_for_sense = sum(len(indexes) for indexes in active_by_source.values())
                active_clause_source_unique_pairs += unique_pairs_for_sense
                active_clause_source_duplicate_pairs += active_pairs_for_sense - unique_pairs_for_sense
                sourced_clause_indexes = {
                    clause_index
                    for indexes in active_by_source.values()
                    for clause_index in indexes
                }
                active_clauses += len(sourced_clause_indexes)
                if clause_count is not None:
                    graph_clauses_without_source_lineage += clause_count - len(sourced_clause_indexes)
                    if clause_count == len(sourced_clause_indexes):
                        senses_with_all_clauses_sourced += 1
                for document, indexes in active_by_source.items():
                    if document not in source_rows_by_path:
                        active_clause_source_missing_records += 1
                for source_path, source in source_rows_by_path.items():
                    attributed_count = len(active_by_source.get(source_path, set()))
                    active_clause_count_per_source[attributed_count] += 1
                    if attributed_count == 0:
                        continue
                    active_source_records += 1
                    parts = source.get("parts")
                    if isinstance(parts, int) and not isinstance(parts, bool) and parts >= 0:
                        part_count = parts
                    elif isinstance(parts, list):
                        part_count = len(parts)
                    else:
                        active_parts_vs_clauses["parts_missing_or_invalid"] += 1
                        continue
                    if part_count == attributed_count:
                        active_parts_vs_clauses["equal"] += 1
                    elif part_count < attributed_count:
                        active_parts_vs_clauses["parts_fewer"] += 1
                    else:
                        active_parts_vs_clauses["parts_more"] += 1
                if any_parts:
                    senses_with_any_parts += 1
                if all_parts:
                    senses_with_all_parts += 1
    except OSError as exc:
        raise ValueError("could not read the frozen sense index") from exc

    expected_senses = manifest.get("sense_count")
    expected_sources = manifest.get("source_record_files")
    count_checks = {
        "sense_count_matches_manifest": sense_count == expected_senses if isinstance(expected_senses, int) else None,
        "source_record_count_matches_manifest": source_record_count == expected_sources if isinstance(expected_sources, int) else None,
        "identity_count_matches_sense_count": len(unique_identities) == sense_count,
    }
    return {
        "audit_version": "full-source-index-structure/2",
        "input_release_label": "OEWN_frozen_110425_154206_20261001",
        "input_graph_sha256": manifest.get("graph_sha256"),
        "input_semantic_fingerprint_sha256": manifest.get("semantic_fingerprint_sha256"),
        "sense_index_sha256": _sha256(index_path),
        "manifest_expected_senses": expected_senses,
        "manifest_expected_source_records": expected_sources,
        "senses_scanned": sense_count,
        "unique_senses_scanned": len(unique_identities),
        "source_records_scanned": source_record_count,
        "count_checks": count_checks,
        "malformed_or_duplicate_index_records": malformed_records,
        "pos_counts": dict(sorted(pos_counts.items())),
        "sense_basis_counts": dict(sorted(basis_counts.items())),
        "graph_clause_count_distribution": dict(sorted(clause_count_distribution.items())),
        "source_records_per_sense_distribution": dict(sorted((str(k), v) for k, v in source_count_per_sense.items())),
        "source_record_status_counts": dict(sorted(status_counts.items())),
        "source_record_feature_counts": dict(sorted(feature_counts.items())),
        "canonical_replay_exact_counts": dict(sorted(canonical_counts.items())),
        "parts_count_distribution": dict(sorted(part_count_distribution.items(), key=lambda item: (not item[0].isdigit(), int(item[0]) if item[0].isdigit() else item[0]))),
        "parts_vs_graph_clause_count": dict(sorted(part_vs_clause.items())),
        "source_records_with_parts": source_records_with_parts,
        "source_records_parts_count_equal_graph_clauses": source_records_matching_parts,
        "active_clause_source_entries": active_clause_source_entries,
        "active_clause_source_pairs": active_clause_source_pairs,
        "active_clause_source_unique_pairs": active_clause_source_unique_pairs,
        "active_clause_source_duplicate_pairs": active_clause_source_duplicate_pairs,
        "active_clause_source_missing_records": active_clause_source_missing_records,
        "malformed_active_clause_sources": malformed_active_clause_sources,
        "active_source_records": active_source_records,
        "active_clause_count_per_source_distribution": dict(sorted(
            (str(k), v) for k, v in active_clause_count_per_source.items()
        )),
        "active_source_records_parts_vs_attributed_clauses": dict(sorted(active_parts_vs_clauses.items())),
        "graph_clauses": graph_clauses,
        "graph_clauses_with_source_lineage": active_clauses,
        "graph_clauses_without_source_lineage": graph_clauses_without_source_lineage,
        "senses_with_all_graph_clauses_sourced": senses_with_all_clauses_sourced,
        "senses_with_any_source_parts": senses_with_any_parts,
        "senses_with_parts_in_every_source_record": senses_with_all_parts,
        "source_records_with_raw_effective_comparison": records_with_text_comparison,
        "source_records_where_raw_and_effective_definitions_differ": records_with_text_difference,
        "raw_text_emitted": False,
        "identity_or_source_paths_emitted": False,
        "scope": "complete senses.jsonl scan; active source-to-clause lineage and source-record metadata cross-checked in the index; source JSON payloads were not opened",
        "interpretation_limit": "parts/clause count equality is structural count alignment only; it does not show that parts map to the correct literals, preserve gloss meaning, or encode valid Horn implications",
    }


def _ensure_project_output(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(PROJECT_ROOT):
        raise ValueError("report output must be inside the project directory")
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        output = _ensure_project_output(args.output)
        if output.exists() and not args.force:
            raise ValueError("report already exists; choose another path or pass --force")
        report = audit_index(args.bundle)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Scanned {report['senses_scanned']} senses and {report['source_records_scanned']} indexed source records")
    print(f"Wrote aggregate-only report inside project: {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
