"""Audit source-part/logic-branch traceability against active graph clauses.

This bounded pilot audit uses the existing text-free annotation frame to select
source records. It verifies their hashes and compares structural metadata only;
it does not adjudicate natural-language meaning.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from src.analysis.full_source_index_audit import DEFAULT_BUNDLE, PROJECT_ROOT


DEFAULT_FRAME = PROJECT_ROOT / "outputs" / "phase7" / "annotation_sampling_frame.jsonl"
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase8" / "source_clause_alignment_audit.json"
MAX_FRAME_SENSES = 1000
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_INDEX_BYTES = 256 * 1024 * 1024
MAX_LINE_BYTES = 8 * 1024 * 1024
MAX_DNF_BRANCHES = 10_000
MAX_LOGIC_DEPTH = 256


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_bundle_file(bundle: Path, relative: Any) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("source evidence contains a missing path")
    posix = PurePosixPath(relative)
    if posix.is_absolute() or ".." in posix.parts:
        raise ValueError("source evidence contains an unsafe relative path")
    resolved = bundle.joinpath(*posix.parts).resolve()
    if not resolved.is_relative_to(bundle) or not resolved.is_file():
        raise ValueError("source evidence is missing or escapes the frozen bundle")
    if resolved.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("a selected source JSON exceeds the 16 MiB safety limit")
    return resolved


def _read_json(path: Path, what: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid {what} JSON") from exc


def _dnf_part_branches(node: Any, depth: int = 0) -> list[frozenset[str]] | None:
    """Return DNF branches as part IDs; None means unsupported/malformed/too large."""
    if depth > MAX_LOGIC_DEPTH or not isinstance(node, dict):
        return None
    part_id = node.get("part_id")
    if isinstance(part_id, str) and part_id:
        return [frozenset({part_id})]
    op, args = node.get("op"), node.get("args")
    if op not in {"AND", "OR"} or not isinstance(args, list) or not args:
        return None
    children = [_dnf_part_branches(arg, depth + 1) for arg in args]
    if any(child is None for child in children):
        return None
    valid_children = [child for child in children if child is not None]
    if op == "OR":
        result: list[frozenset[str]] = []
        for child in valid_children:
            for branch in child:
                result.append(branch)
                if len(result) > MAX_DNF_BRANCHES:
                    return None
        return result
    result = [frozenset()]
    for child in valid_children:
        next_result: list[frozenset[str]] = []
        for left in result:
            for right in child:
                next_result.append(left | right)
                if len(next_result) > MAX_DNF_BRANCHES:
                    return None
        result = next_result
    return result


def _multiset_equal(left: list[frozenset[str]], right: list[frozenset[str]]) -> bool:
    counts = Counter(left)
    return counts == Counter(right)


def audit_alignment(frame_path: Path, bundle: Path) -> dict[str, Any]:
    frame_path, bundle = frame_path.resolve(), bundle.resolve()
    frame: list[dict[str, Any]] = []
    try:
        with frame_path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"frame line {line_number} is not an object")
                frame.append(row)
                if len(frame) > MAX_FRAME_SENSES:
                    raise ValueError("frame exceeds the 1,000-sense safety limit")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("annotation frame is missing or invalid JSONL") from exc
    if not frame:
        raise ValueError("annotation frame is empty")
    selected = {row.get("sense_id") for row in frame}
    if None in selected or len(selected) != len(frame):
        raise ValueError("annotation frame has missing or duplicate sense identities")

    manifest = _read_json(bundle / "manifest.json", "bundle manifest")
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    index_path = bundle / "indexes" / "senses.jsonl"
    if not rules_path.is_file() or not index_path.is_file():
        raise ValueError("bundle is missing the graph rules or sense index")
    if index_path.stat().st_size > MAX_INDEX_BYTES:
        raise ValueError("sense index exceeds the configured 256 MiB safety limit")
    actual_graph_hash = _sha256(rules_path)
    if manifest.get("graph_sha256") and actual_graph_hash != manifest["graph_sha256"]:
        raise ValueError("graph rules SHA-256 does not match bundle manifest")

    index_rows: dict[str, dict[str, Any]] = {}
    try:
        with index_path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                if len(line.encode("utf-8")) > MAX_LINE_BYTES:
                    raise ValueError(f"sense index line {line_number} exceeds the 8 MiB safety limit")
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"sense index line {line_number} is not an object")
                identity = row.get("identity")
                if isinstance(identity, str) and identity in selected:
                    index_rows[identity] = row
                    if len(index_rows) == len(selected):
                        break
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("sense index is missing or invalid JSONL") from exc
    if set(index_rows) != selected:
        raise ValueError("one or more frame senses are absent from the sense index")

    rules_by_head: dict[str, list[list[str]]] = {}
    try:
        with rules_path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                if len(line.encode("utf-8")) > MAX_LINE_BYTES:
                    raise ValueError(f"graph rule line {line_number} exceeds the 8 MiB safety limit")
                rule = json.loads(line)
                if not isinstance(rule, dict):
                    raise ValueError(f"graph rule line {line_number} is not an object")
                head = rule.get("head")
                if isinstance(head, str) and head in selected:
                    clauses = rule.get("clauses")
                    if not isinstance(clauses, list) or any(
                        not isinstance(c, list) or any(not isinstance(literal, str) for literal in c)
                        for c in clauses
                    ):
                        raise ValueError("selected graph rule has malformed clauses")
                    rules_by_head[head] = clauses
                    if len(rules_by_head) == len(selected):
                        break
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("graph rules are missing or invalid JSONL") from exc
    if set(rules_by_head) != selected:
        raise ValueError("one or more frame senses are absent from graph rules")

    totals: Counter[str] = Counter()
    by_panel: dict[str, Counter[str]] = defaultdict(Counter)
    for frame_row in frame:
        identity = frame_row["sense_id"]
        index_row = index_rows[identity]
        clauses = rules_by_head[identity]
        active_by_document: dict[str, set[int]] = defaultdict(set)
        for entry in index_row.get("active_clause_sources", []):
            if not isinstance(entry, dict) or type(entry.get("clause_index")) is not int:
                totals["malformed_active_clause_source_entries"] += 1
                continue
            clause_index = entry["clause_index"]
            if clause_index < 0 or clause_index >= len(clauses):
                raise ValueError("active clause source has an out-of-range clause index")
            documents = entry.get("source_documents")
            if not isinstance(documents, list):
                totals["malformed_active_clause_source_entries"] += 1
                continue
            for document in documents:
                if isinstance(document, str):
                    active_by_document[document].add(clause_index)
        panel = frame_row.get("panel")
        panel_key = panel if isinstance(panel, str) and panel in {
            "random_stratified", "diagnostic_not_for_population_estimates"
        } else "other_or_missing"
        panel_totals = by_panel[panel_key]
        totals["senses"] += 1
        panel_totals["senses"] += 1
        source_rows = frame_row.get("source_records")
        if not isinstance(source_rows, list) or not source_rows:
            raise ValueError("frame sense has no source records")
        for source_row in source_rows:
            if not isinstance(source_row, dict):
                raise ValueError("frame contains malformed source evidence")
            relative = source_row.get("path")
            expected_hash = source_row.get("sha256")
            source_path = _safe_bundle_file(bundle, relative)
            if not isinstance(expected_hash, str) or _sha256(source_path) != expected_hash:
                raise ValueError("selected source file hash does not match annotation frame")
            source = _read_json(source_path, "selected source")
            if not isinstance(source, dict):
                raise ValueError("selected source must be a JSON object")
            totals["source_records_hash_verified"] += 1
            panel_totals["source_records_hash_verified"] += 1
            if relative not in active_by_document:
                totals["inactive_source_records"] += 1
                panel_totals["inactive_source_records"] += 1
                continue
            totals["active_source_records"] += 1
            panel_totals["active_source_records"] += 1
            attributed_indexes = sorted(active_by_document[relative])
            attributed_clause_sets = [frozenset(clauses[i]) for i in attributed_indexes]
            definition = source.get("definition")
            definition = definition if isinstance(definition, dict) else {}
            parts = definition.get("parts")
            parts = parts if isinstance(parts, list) else []
            part_ids = [part.get("part_id") for part in parts if isinstance(part, dict) and isinstance(part.get("part_id"), str)]
            part_id_set = set(part_ids)
            if len(part_ids) == len(parts) and len(part_id_set) == len(part_ids):
                totals["source_records_with_unique_part_ids"] += 1
            else:
                totals["source_records_with_unique_part_ids"] += 0
            branches = _dnf_part_branches(definition.get("logic"))
            if branches is None:
                totals["active_logic_trees_unparsed_or_too_large"] += 1
                continue
            totals["active_logic_trees_parsed"] += 1
            branches_match_parts = set().union(*branches) == part_id_set if branches else not part_id_set
            if branches_match_parts and len(part_ids) == len(parts):
                totals["logic_leaf_ids_match_part_ids"] += 1
                panel_totals["logic_leaf_ids_match_part_ids"] += 1
            if len(branches) == len(attributed_indexes):
                totals["logic_branch_count_matches_attributed_clause_count"] += 1
                panel_totals["logic_branch_count_matches_attributed_clause_count"] += 1
            else:
                totals["logic_branch_count_differs_from_attributed_clause_count"] += 1
                panel_totals["logic_branch_count_differs_from_attributed_clause_count"] += 1

            part_results = source.get("part_results")
            result_by_part = {
                result.get("part_id"): result
                for result in part_results if isinstance(result, dict) and isinstance(result.get("part_id"), str)
            } if isinstance(part_results, list) else {}
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
            if len(mapped_branches) == len(attributed_clause_sets) and _multiset_equal(mapped_branches, attributed_clause_sets):
                totals["mapped_wsd_branch_sets_exactly_match_attributed_graph_clauses"] += 1
                panel_totals["mapped_wsd_branch_sets_exactly_match_attributed_graph_clauses"] += 1
            for graph_clause in attributed_clause_sets:
                totals["attributed_clause_source_pairs"] += 1
                panel_totals["attributed_clause_source_pairs"] += 1
                if any(graph_clause <= branch for branch in mapped_branches):
                    totals["attributed_clauses_subset_of_a_branch_wsd_id_union"] += 1
                    panel_totals["attributed_clauses_subset_of_a_branch_wsd_id_union"] += 1
                if any(graph_clause == branch for branch in mapped_branches):
                    totals["attributed_clauses_exactly_match_a_branch_wsd_id_union"] += 1
                    panel_totals["attributed_clauses_exactly_match_a_branch_wsd_id_union"] += 1

    report = {
        "audit_version": "source-clause-alignment-pilot/1",
        "frame_sha256": _sha256(frame_path),
        "input_graph_sha256": actual_graph_hash,
        "input_semantic_fingerprint_sha256": manifest.get("semantic_fingerprint_sha256"),
        "sense_index_sha256": _sha256(index_path),
        "candidate_senses": len(frame),
        "aggregates": dict(sorted(totals.items())),
        "by_panel": {key: dict(sorted(counts.items())) for key, counts in sorted(by_panel.items())},
        "scope": "existing bounded annotation frame; source files verified against frame hashes; only frame-linked graph clauses compared",
        "raw_text_emitted": False,
        "identities_and_paths_emitted": False,
        "interpretation_limit": "part-ID branches, clause attribution, and WSD-ID set overlap are structural traces only; neither exact set matches nor their absence establishes natural-language entailment, correct sense selection, or rule soundness",
    }
    return report


def _ensure_project_output(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(PROJECT_ROOT):
        raise ValueError("report output must be inside the project directory")
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=Path, default=DEFAULT_FRAME)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        output = _ensure_project_output(args.output)
        if output.exists() and not args.force:
            raise ValueError("report already exists; choose another path or pass --force")
        report = audit_alignment(args.frame, args.bundle)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Audited {report['candidate_senses']} sampled senses")
    print(f"Wrote aggregate-only report inside project: {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
