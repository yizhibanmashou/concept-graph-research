"""Summarize source decomposition metadata for a text-free annotation frame.

Only aggregate counts and booleans are emitted; no gloss, example, or formula
text is copied into the report. This audits field alignment, not semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

try:  # Direct script execution and package/module execution are both supported.
    from .project_paths import PROJECT_ROOT, configured_bundle_root
except ImportError:
    from project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_BUNDLE = configured_bundle_root()
DEFAULT_FRAME = PROJECT_ROOT / "outputs" / "phase7" / "annotation_sampling_frame.jsonl"
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase7" / "source_structure_audit.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_frame(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid frame JSON at {path}:{line_number}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"frame line {line_number} must be an object")
            rows.append(row)
    return rows


def _group_name(relative_path: str) -> str:
    parts = PurePosixPath(relative_path).parts
    if len(parts) >= 3 and parts[0] == "sources" and parts[1] == "Synset":
        return parts[2]
    return "/".join(parts[:2]) or "unknown"


def _summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    op_counts = Counter(row["logic_op"] for row in records)
    panel_rows = defaultdict(list)
    root_rows = defaultdict(list)
    pipeline_rows = defaultdict(list)
    op_alternative_rows = defaultdict(list)
    for row in records:
        panel_rows[row["panel"]].append(row)
        root_rows[row["source_group"]].append(row)
        pipeline_rows[row["pipeline"]].append(row)
        key = f"logic_op={row['logic_op']}|graph_has_multiple_clauses={str(row['graph_clause_count'] > 1).lower()}"
        op_alternative_rows[key].append(row)

    def counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
        part_rows = [row for row in rows if row["part_count"] is not None]
        changed_rows = [row for row in rows if row["raw_effective_comparison_available"]]
        return {
            "source_record_count": len(rows),
            "definition_logic_operator_counts": dict(sorted(Counter(row["logic_op"] for row in rows).items())),
            "part_count_present": len(part_rows),
            "part_count_matches_graph_clause_count": sum(row["part_count_matches_graph_clause_count"] is True for row in part_rows),
            "raw_effective_comparison_available": len(changed_rows),
            "raw_effective_text_differs": sum(row["raw_effective_text_differs"] is True for row in changed_rows),
            "record_status_counts": dict(sorted(Counter(row["status"] for row in rows).items())),
        }

    return {
        "source_record_count": len(records),
        "definition_logic_operator_counts": dict(sorted(op_counts.items())),
        "part_count_present": sum(row["part_count"] is not None for row in records),
        "part_count_matches_graph_clause_count": sum(row["part_count_matches_graph_clause_count"] is True for row in records),
        "raw_effective_comparison_available": sum(row["raw_effective_comparison_available"] for row in records),
        "raw_effective_text_differs": sum(row["raw_effective_text_differs"] is True for row in records),
        "by_panel": {key: counts(value) for key, value in sorted(panel_rows.items())},
        "by_source_group": {key: counts(value) for key, value in sorted(root_rows.items())},
        "by_pipeline": {key: counts(value) for key, value in sorted(pipeline_rows.items())},
        "by_logic_op_and_graph_alternatives": {
            key: counts(value) for key, value in sorted(op_alternative_rows.items())
        },
    }


def audit_sources(frame_path: Path, bundle: Path) -> dict[str, Any]:
    frame = _load_frame(frame_path)
    bundle = bundle.resolve()
    records = []
    verified_source_files = 0
    for frame_row in frame:
        if frame_row.get("gloss_text") or "snapshot_definition" in frame_row:
            raise ValueError("frame must not contain gloss text")
        source_rows = frame_row.get("source_records")
        if not isinstance(source_rows, list) or not source_rows:
            raise ValueError(f"missing source records for {frame_row.get('sense_id')}")
        for source_row in source_rows:
            if not isinstance(source_row, dict):
                raise ValueError(f"malformed source evidence for {frame_row.get('sense_id')}")
            relative = source_row.get("path")
            expected_hash = source_row.get("sha256")
            if not isinstance(relative, str) or not isinstance(expected_hash, str):
                raise ValueError(f"malformed source evidence for {frame_row.get('sense_id')}")
            source_relative = PurePosixPath(relative)
            if source_relative.is_absolute() or ".." in source_relative.parts:
                raise ValueError(f"unsafe source path: {relative}")
            source_path = bundle.joinpath(*source_relative.parts).resolve()
            if not source_path.is_relative_to(bundle) or not source_path.is_file():
                raise ValueError(f"source file missing or outside bundle: {relative}")
            actual_hash = _sha256(source_path)
            if actual_hash != expected_hash:
                raise ValueError(f"source hash mismatch: {relative}")
            verified_source_files += 1
            try:
                source = json.loads(source_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"source JSON is invalid: {relative}") from exc
            if not isinstance(source, dict):
                raise ValueError(f"source JSON must be an object: {relative}")
            definition = source.get("definition") if isinstance(source.get("definition"), dict) else {}
            synset = source.get("synset") if isinstance(source.get("synset"), dict) else {}
            logic = definition.get("logic") if isinstance(definition.get("logic"), dict) else {}
            parts = definition.get("parts")
            if not isinstance(parts, list):
                parts = None
            raw_gloss = synset.get("raw_definition")
            effective_gloss = definition.get("definition")
            comparison_available = isinstance(raw_gloss, str) and isinstance(effective_gloss, str)
            records.append({
                "panel": frame_row.get("panel", "unknown"),
                "source_group": _group_name(relative),
                "pipeline": source.get("pipeline", "missing"),
                "status": source.get("status", "missing"),
                "logic_op": logic.get("op", "missing"),
                "part_count": len(parts) if parts is not None else None,
                "graph_clause_count": frame_row.get("structural_features", {}).get("clause_count", 0),
                "part_count_matches_graph_clause_count": (
                    len(parts) == frame_row.get("structural_features", {}).get("clause_count")
                    if parts is not None else None
                ),
                "raw_effective_comparison_available": comparison_available,
                "raw_effective_text_differs": raw_gloss != effective_gloss if comparison_available else None,
            })
    sense_ids = [row.get("sense_id") for row in frame]
    bundle_manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    return {
        "audit_version": "annotation-source-structure/1",
        "frame_path": str(frame_path.resolve()),
        "frame_sha256": _sha256(frame_path),
        "bundle_path": str(bundle),
        "bundle_graph_version": bundle_manifest.get("graph_version"),
        "bundle_semantic_fingerprint_sha256": bundle_manifest.get("semantic_fingerprint_sha256"),
        "candidate_sense_count": len(frame),
        "unique_candidate_sense_count": len(set(sense_ids)),
        "source_file_hashes_verified": verified_source_files,
        "raw_text_emitted": False,
        "interpretation_limit": "field presence/count alignment is structural metadata only; it does not establish semantic equivalence or logic correctness",
        "aggregates": _summarize(records),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=Path, default=DEFAULT_FRAME)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true", help="replace an existing report")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; choose another path or pass --force to replace it")
    try:
        report = audit_sources(args.frame, args.bundle)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Audited {report['source_file_hashes_verified']} source records for {report['candidate_sense_count']} candidates")
    print(f"Wrote aggregate-only report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
