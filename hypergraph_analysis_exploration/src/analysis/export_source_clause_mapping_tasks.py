"""Export internal, anonymized tasks for source-part/graph-clause mapping.

Tasks expose the candidate graph clause by design, but withhold synset IDs,
source paths, pipeline status, and sampling strata. The result is an error-
analysis annotation batch, not a blind semantic benchmark or public release.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from src.analysis.export_annotation_batch import (
    ATTRIBUTION,
    DEFAULT_KEY as DEFAULT_SOURCE_KEY,
    DEFAULT_MANIFEST as DEFAULT_SOURCE_MANIFEST,
    DEFAULT_BATCH as DEFAULT_SOURCE_BATCH,
    RELEASE_ARCHIVE_SHA256,
    RELEASE_DATE,
    RELEASE_NAME,
    RELEASE_URI,
    PROJECT_ROOT,
)
from src.analysis.full_source_index_audit import DEFAULT_BUNDLE
from src.analysis.source_clause_alignment_audit import _dnf_part_branches


DEFAULT_FRAME = PROJECT_ROOT / "outputs" / "phase7" / "annotation_sampling_frame.jsonl"
DEFAULT_BATCH = PROJECT_ROOT / "outputs" / "phase8" / "source_clause_mapping_tasks.jsonl"
DEFAULT_KEY = PROJECT_ROOT / "outputs" / "phase8" / "source_clause_mapping_answer_key.json"
DEFAULT_MANIFEST = PROJECT_ROOT / "outputs" / "phase8" / "source_clause_mapping_manifest.json"
TASK_SCHEMA_VERSION = "source-clause-alignment-task/0.1"
MAX_FRAME_SENSES = 1000
MAX_SOURCE_BYTES = 16 * 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid {label} JSON") from exc


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    rows = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"{label} line {line_number} must be an object")
                rows.append(row)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid {label} JSONL") from exc
    return rows


def _safe_source(bundle: Path, relative: Any) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("frame contains a missing source path")
    rel = PurePosixPath(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("frame contains an unsafe source path")
    path = bundle.joinpath(*rel.parts).resolve()
    if not path.is_relative_to(bundle) or not path.is_file():
        raise ValueError("frame source is missing or escapes the frozen bundle")
    if path.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("selected source JSON exceeds the 16 MiB safety limit")
    return path


def _to_local_logic(node: Any, part_ids: dict[str, str]) -> dict[str, Any]:
    if not isinstance(node, dict):
        raise ValueError("source definition logic is malformed")
    part_id = node.get("part_id")
    if isinstance(part_id, str):
        if part_id not in part_ids:
            raise ValueError("source logic references a part absent from definition.parts")
        return {"part_id": part_ids[part_id]}
    op, args = node.get("op"), node.get("args")
    if op not in {"AND", "OR"} or not isinstance(args, list) or not args:
        raise ValueError("source logic has an unsupported structure")
    return {"op": op, "args": [_to_local_logic(child, part_ids) for child in args]}


def _load_verified_source_records(frame_row: dict[str, Any], bundle: Path) -> dict[str, tuple[dict[str, Any], str]]:
    result = {}
    source_records = frame_row.get("source_records")
    if not isinstance(source_records, list) or not source_records:
        raise ValueError("frame candidate has no source records")
    for record in source_records:
        if not isinstance(record, dict):
            raise ValueError("frame contains a malformed source record")
        relative, expected = record.get("path"), record.get("sha256")
        path = _safe_source(bundle, relative)
        if not isinstance(expected, str) or _sha256(path) != expected:
            raise ValueError("source record hash does not match the annotation frame")
        source = _read_json(path, "source record")
        if not isinstance(source, dict):
            raise ValueError("source record must be a JSON object")
        if relative in result:
            raise ValueError("frame repeats a source record path")
        result[relative] = (source, expected)
    return result


def build_tasks(
    frame_path: Path,
    bundle: Path,
    release_batch_path: Path,
    release_key_path: Path,
    release_manifest_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    frame_path, bundle = frame_path.resolve(), bundle.resolve()
    frame = _read_jsonl(frame_path, "annotation frame")
    if not frame or len(frame) > MAX_FRAME_SENSES:
        raise ValueError("frame must contain between 1 and 1,000 senses")
    frame_by_sense = {row.get("sense_id"): row for row in frame}
    if len(frame_by_sense) != len(frame) or any(not isinstance(key, str) for key in frame_by_sense):
        raise ValueError("frame contains duplicate or invalid sense IDs")
    frame_hash = _sha256(frame_path)

    release_manifest = _read_json(release_manifest_path, "release batch manifest")
    if release_manifest.get("batch_version") != "oewn-blind-annotation-batch/1":
        raise ValueError("unsupported verified OEWN batch version")
    if release_manifest.get("source_release") != RELEASE_NAME or release_manifest.get("source_release_date") != RELEASE_DATE:
        raise ValueError("release batch is not the pinned OEWN 2025 Plus version")
    if release_manifest.get("source_release_archive_sha256") != RELEASE_ARCHIVE_SHA256:
        raise ValueError("release batch archive hash does not match the pinned release")
    if release_manifest.get("frame_sha256") != frame_hash:
        raise ValueError("release batch manifest refers to a different frame")
    if release_manifest.get("batch_sha256") != _sha256(release_batch_path):
        raise ValueError("release blind-batch hash does not match its manifest")
    if release_manifest.get("answer_key_sha256") != _sha256(release_key_path):
        raise ValueError("release answer-key hash does not match its manifest")
    release_batch = _read_jsonl(release_batch_path, "release blind batch")
    release_key = _read_json(release_key_path, "release answer key")
    if (not isinstance(release_key, list)
            or len(release_batch) != len(release_key)
            or release_manifest.get("candidate_count") != len(release_batch)):
        raise ValueError("release batch and answer key row counts differ")
    raw_gloss_by_sense = {}
    for visible, hidden in zip(release_batch, release_key, strict=True):
        if (not isinstance(hidden, dict) or not isinstance(hidden.get("sense_id"), str)
                or visible.get("task_id") != hidden.get("task_id")):
            raise ValueError("release answer key has malformed sense evidence")
        if not isinstance(visible.get("gloss"), str) or hidden["sense_id"] in raw_gloss_by_sense:
            raise ValueError("release batch has duplicate senses or missing raw glosses")
        raw_gloss_by_sense[hidden["sense_id"]] = visible["gloss"]
    if set(raw_gloss_by_sense) != set(frame_by_sense):
        raise ValueError("release batch and frame have different sense sets")

    manifest_path = bundle / "manifest.json"
    bundle_manifest = _read_json(manifest_path, "frozen bundle manifest")
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    index_path = bundle / "indexes" / "senses.jsonl"
    nodes_path = bundle / "graph" / "nodes.tsv"
    for path in (rules_path, index_path, nodes_path):
        if not path.is_file():
            raise ValueError("frozen bundle lacks required graph/index files")
    graph_hash = _sha256(rules_path)
    if bundle_manifest.get("graph_sha256") and graph_hash != bundle_manifest["graph_sha256"]:
        raise ValueError("frozen graph hash does not match bundle manifest")

    selected = set(frame_by_sense)
    lineage = {}
    with index_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"sense index line {line_number} must be an object")
            identity = row.get("identity")
            if isinstance(identity, str) and identity in selected:
                if identity in lineage:
                    raise ValueError("sense index contains duplicate selected identities")
                lineage[identity] = row
    if set(lineage) != selected:
        raise ValueError("one or more frame senses are absent from sense index")

    rules = {}
    needed_literals: set[str] = set()
    with rules_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"graph rule line {line_number} must be an object")
            head = row.get("head")
            if isinstance(head, str) and head in selected:
                if head in rules or not isinstance(row.get("clauses"), list):
                    raise ValueError("selected graph rules are duplicate or malformed")
                rules[head] = row["clauses"]
                for clause in row["clauses"]:
                    if not isinstance(clause, list) or any(not isinstance(literal, str) for literal in clause):
                        raise ValueError("selected graph clause contains malformed literals")
                    needed_literals.update(clause)
    if set(rules) != selected:
        raise ValueError("one or more frame senses are absent from graph rules")
    node_rows = {}
    with nodes_path.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            identity = row.get("synset_id")
            if identity in needed_literals:
                node_rows[identity] = row
                if len(node_rows) == len(needed_literals):
                    break
    missing_nodes = needed_literals - set(node_rows)
    if missing_nodes:
        raise ValueError(f"graph literals lack node descriptions ({len(missing_nodes)} missing)")

    tasks: list[dict[str, Any]] = []
    answer_key: list[dict[str, Any]] = []
    raw_mismatch_sources = inactive_sources = active_sources = 0
    frame_hash_verified_sources = 0
    for sense_id, frame_row in frame_by_sense.items():
        index_row = lineage[sense_id]
        source_records = _load_verified_source_records(frame_row, bundle)
        frame_hash_verified_sources += len(source_records)
        active_by_path: dict[str, set[int]] = defaultdict(set)
        for entry in index_row.get("active_clause_sources", []):
            if not isinstance(entry, dict) or type(entry.get("clause_index")) is not int:
                raise ValueError("sense index contains malformed active clause source metadata")
            clause_index = entry["clause_index"]
            if clause_index < 0 or clause_index >= len(rules[sense_id]):
                raise ValueError("active source metadata refers to an out-of-range clause")
            documents = entry.get("source_documents")
            if not isinstance(documents, list):
                raise ValueError("active source documents must be a list")
            for document in documents:
                if not isinstance(document, str):
                    raise ValueError("active source document reference must be a string")
                active_by_path[document].add(clause_index)
        if set(active_by_path) - set(source_records):
            raise ValueError("active source document is absent from the candidate frame")
        for relative, (source, source_hash) in source_records.items():
            synset = source.get("synset") if isinstance(source.get("synset"), dict) else {}
            source_identity = source.get("synset_id") or source.get("sense_id") or synset.get("synset_id")
            if source_identity != sense_id:
                raise ValueError("frame source record identity does not match its sense")
            clause_indexes = sorted(active_by_path.get(relative, set()))
            if not clause_indexes:
                inactive_sources += 1
                continue
            active_sources += 1
            source_raw = synset.get("raw_definition")
            official_raw = raw_gloss_by_sense[sense_id]
            if not isinstance(source_raw, str) or source_raw != official_raw:
                raw_mismatch_sources += 1
                continue
            definition = source.get("definition") if isinstance(source.get("definition"), dict) else {}
            effective = definition.get("definition")
            source_parts = definition.get("parts")
            if not isinstance(effective, str) or not isinstance(source_parts, list) or not source_parts:
                raise ValueError("active source lacks an effective definition or parts")
            original_part_ids = []
            parts = []
            for part in source_parts:
                if not isinstance(part, dict) or not isinstance(part.get("part_id"), str) or not isinstance(part.get("text"), str):
                    raise ValueError("active source has malformed parts")
                original_part_ids.append(part["part_id"])
                parts.append({"part_id": f"p{len(parts) + 1}", "text": part["text"]})
            if len(set(original_part_ids)) != len(original_part_ids):
                raise ValueError("active source has duplicate part IDs")
            local_part_ids = {original: f"p{index + 1}" for index, original in enumerate(original_part_ids)}
            logic = _to_local_logic(definition.get("logic"), local_part_ids)
            if _dnf_part_branches(definition.get("logic")) is None:
                raise ValueError("active source logic is unsupported or exceeds the safe DNF limit")
            panel = frame_row.get("panel")
            for clause_index in clause_indexes:
                local_literals = []
                original_literals = rules[sense_id][clause_index]
                for literal_index, literal_id in enumerate(original_literals, start=1):
                    node = node_rows[literal_id]
                    local_literals.append({
                        "literal_id": f"l{literal_index}",
                        "pos": node.get("pos", ""),
                        "lemmas": node.get("lemmas", ""),
                        "definition": node.get("definition", ""),
                    })
                task_id = f"MAP-{len(tasks) + 1:04d}"
                tasks.append({
                    "schema_version": TASK_SCHEMA_VERSION,
                    "task_id": task_id,
                    "pos": frame_row.get("pos", ""),
                    "lemmas": frame_row.get("lemmas", []),
                    "raw_gloss": official_raw,
                    "effective_definition": effective,
                    "parts": parts,
                    "source_logic": logic,
                    "graph_clause": {"clause_index": clause_index, "literals": local_literals},
                })
                answer_key.append({
                    "task_id": task_id,
                    "sense_id": sense_id,
                    "source_path": relative,
                    "source_sha256": source_hash,
                    "source_part_ids": original_part_ids,
                    "graph_clause_index": clause_index,
                    "graph_literal_ids": original_literals,
                    "sampling_panel": panel,
                    "source_release_archive_sha256": RELEASE_ARCHIVE_SHA256,
                })

    if not tasks:
        raise ValueError("no eligible active source-clause mapping tasks were produced")
    seed = frame[0].get("random_seed")
    if type(seed) is not int:
        raise ValueError("frame does not contain a deterministic integer random seed")
    paired_rows = list(zip(tasks, answer_key, strict=True))
    random.Random(seed ^ 0xA71A).shuffle(paired_rows)
    tasks, answer_key = [], []
    for index, (task, answer) in enumerate(paired_rows, start=1):
        task_id = f"MAP-{index:04d}"
        task["task_id"] = task_id
        answer["task_id"] = task_id
        tasks.append(task)
        answer_key.append(answer)
    manifest = {
        "batch_version": TASK_SCHEMA_VERSION,
        "candidate_sense_count": len(frame),
        "task_count": len(tasks),
        "verified_source_file_count": frame_hash_verified_sources,
        "active_source_record_count": active_sources,
        "inactive_source_record_count": inactive_sources,
        "active_sources_excluded_for_nonmatching_official_raw_gloss": raw_mismatch_sources,
        "source_release": RELEASE_NAME,
        "source_release_date": RELEASE_DATE,
        "source_release_uri": RELEASE_URI,
        "source_release_archive_sha256": RELEASE_ARCHIVE_SHA256,
        "source_release_attribution": ATTRIBUTION,
        "frame_sha256": frame_hash,
        "bundle_graph_sha256": graph_hash,
        "bundle_index_sha256": _sha256(index_path),
        "bundle_nodes_sha256": _sha256(nodes_path),
        "blindness_scope": "source synset IDs, source paths, pipeline status, and random/diagnostic panel withheld; source gloss, generated parts/logic, and graph clause are intentionally visible for mapping; task order deterministically shuffled",
        "use_limit": "internal error-analysis annotation only; not a semantic entailment gold set or a population performance estimate",
        "license_status": "OEWN raw gloss is CC BY 4.0 with attribution; package-derived effective definitions and literal descriptions require package-level source/license clearance before redistribution",
        "distribution_status": "internal only; do not redistribute before source-level licensing review",
    }
    return tasks, answer_key, manifest


def _ensure_project_paths(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    resolved = tuple(path.resolve() for path in paths)
    if any(not path.is_relative_to(PROJECT_ROOT) for path in resolved):
        raise ValueError("all generated task outputs must be inside the project directory")
    if len(set(resolved)) != len(resolved):
        raise ValueError("task, answer key, and manifest paths must be different")
    return resolved


def write_outputs(tasks: list[dict[str, Any]], key: list[dict[str, Any]], manifest: dict[str, Any],
                  task_path: Path, key_path: Path, manifest_path: Path, force: bool = False) -> None:
    task_path, key_path, manifest_path = _ensure_project_paths((task_path, key_path, manifest_path))
    paths = (task_path, key_path, manifest_path)
    if not force and any(path.exists() for path in paths):
        raise FileExistsError("a task output already exists; pass --force to replace it")
    task_path.parent.mkdir(parents=True, exist_ok=True)
    task_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in tasks), encoding="utf-8")
    key_path.write_text(json.dumps(key, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    final_manifest = dict(manifest)
    final_manifest["task_batch_sha256"] = _sha256(task_path)
    final_manifest["answer_key_sha256"] = _sha256(key_path)
    manifest_path.write_text(json.dumps(final_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=Path, default=DEFAULT_FRAME)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--release-batch", type=Path, default=DEFAULT_SOURCE_BATCH)
    parser.add_argument("--release-answer-key", type=Path, default=DEFAULT_SOURCE_KEY)
    parser.add_argument("--release-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_BATCH)
    parser.add_argument("--answer-key", type=Path, default=DEFAULT_KEY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        tasks, key, manifest = build_tasks(
            args.frame, args.bundle, args.release_batch, args.release_answer_key, args.release_manifest
        )
        write_outputs(tasks, key, manifest, args.tasks, args.answer_key, args.manifest, args.force)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"Wrote {len(tasks)} internal source-clause mapping tasks to {args.tasks}")
    print(f"Keep the ID/path answer key restricted: {args.answer_key}")
    print(f"Redistribution remains blocked pending package-level source/license review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
