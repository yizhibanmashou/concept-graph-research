"""Validate independent human mappings from source parts to graph literals.

This validator checks task/annotation structure and evidence offsets. Passing
it does not establish that a mapping or entailment judgment is semantically
correct.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


MAPPING_STATUSES = {"exact", "partial", "none", "ambiguous", "unassessable"}
TEXT_VIEWS = {"raw_gloss", "effective_definition", "part_text"}
POS_VALUES = {"n", "v", "a", "r"}
TASK_SCHEMA_VERSION = "source-clause-alignment-task/0.1"
RETURN_SCHEMA_VERSION = "source-clause-alignment-return/0.1"
RETURN_FIELDS = {"schema_version", "task_id", "annotator_id", "mappings", "unmapped_part_ids", "notes"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _task_parts(task: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    parts = task.get("parts")
    if not isinstance(parts, list):
        return result
    for part in parts:
        if isinstance(part, dict) and _nonempty(part.get("part_id")) and isinstance(part.get("text"), str):
            result[part["part_id"]] = part["text"]
    return result


def _task_literals(task: dict[str, Any]) -> set[str]:
    clause = task.get("graph_clause")
    literals = clause.get("literals") if isinstance(clause, dict) else None
    if not isinstance(literals, list):
        return set()
    return {
        literal["literal_id"] for literal in literals
        if isinstance(literal, dict) and _nonempty(literal.get("literal_id"))
    }


def _logic_part_leaves(node: Any, known_parts: set[str], depth: int = 0) -> list[str] | None:
    if depth > 256 or not isinstance(node, dict):
        return None
    part_id = node.get("part_id")
    if isinstance(part_id, str):
        return [part_id] if part_id in known_parts else None
    op, args = node.get("op"), node.get("args")
    if not isinstance(op, str) or op not in {"AND", "OR"} or not isinstance(args, list) or not args:
        return None
    result: list[str] = []
    for child in args:
        child_leaves = _logic_part_leaves(child, known_parts, depth + 1)
        if child_leaves is None:
            return None
        result.extend(child_leaves)
    return result


def validate_task(task: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(task, dict):
        return ["task must be a JSON object"]
    if not _nonempty(task.get("task_id")):
        errors.append("task_id must be a non-empty string")
    if task.get("schema_version") != TASK_SCHEMA_VERSION:
        errors.append(f"schema_version must be {TASK_SCHEMA_VERSION!r}")
    if not _nonempty(task.get("raw_gloss")):
        errors.append("raw_gloss must be a non-empty string")
    if not _nonempty(task.get("effective_definition")):
        errors.append("effective_definition must be a non-empty string")
    if not isinstance(task.get("pos"), str) or task["pos"] not in POS_VALUES:
        errors.append(f"pos must be one of {sorted(POS_VALUES)}")
    lemmas = task.get("lemmas")
    if not isinstance(lemmas, list) or not lemmas or any(not _nonempty(lemma) for lemma in lemmas):
        errors.append("lemmas must be a non-empty list of non-empty strings")
    parts = task.get("parts")
    if not isinstance(parts, list):
        errors.append("parts must be a list")
        parts = []
    elif not parts:
        errors.append("parts must not be empty")
    part_ids = []
    for index, part in enumerate(parts):
        if not isinstance(part, dict) or not _nonempty(part.get("part_id")) or not isinstance(part.get("text"), str):
            errors.append(f"parts[{index}] must contain non-empty part_id and string text")
            continue
        part_ids.append(part["part_id"])
    if len(set(part_ids)) != len(part_ids):
        errors.append("part_id values must be unique")
    logic = task.get("source_logic")
    if logic is None:
        errors.append("source_logic must preserve the source AND/OR structure")
    else:
        known_parts = set(part_ids)
        logic_leaves = _logic_part_leaves(logic, known_parts)
        if logic_leaves is None:
            errors.append("source_logic must be a bounded AND/OR tree referencing known part IDs")
        elif len(logic_leaves) != len(known_parts) or set(logic_leaves) != known_parts:
            errors.append("source_logic must reference each declared part exactly once")
    clause = task.get("graph_clause")
    if not isinstance(clause, dict):
        errors.append("graph_clause must be an object")
        clause = {}
    if type(clause.get("clause_index")) is not int or clause["clause_index"] < 0:
        errors.append("graph_clause.clause_index must be a non-negative integer")
    literals = clause.get("literals")
    if not isinstance(literals, list) or not literals:
        errors.append("graph_clause.literals must be a non-empty list")
        literals = []
    literal_ids = []
    for index, literal in enumerate(literals):
        if not isinstance(literal, dict) or not _nonempty(literal.get("literal_id")):
            errors.append(f"graph_clause.literals[{index}] must have a non-empty literal_id")
            continue
        if not _nonempty(literal.get("lemmas")) or not _nonempty(literal.get("definition")):
            errors.append(f"graph_clause.literals[{index}] must include non-empty display lemmas and definition")
        literal_ids.append(literal["literal_id"])
    if len(set(literal_ids)) != len(literal_ids):
        errors.append("literal_id values must be unique within a task")
    return errors


def validate_alignment(task: Any, annotation: Any) -> list[str]:
    errors = validate_task(task)
    if not isinstance(task, dict) or not isinstance(annotation, dict):
        return errors + (["annotation must be a JSON object"] if not isinstance(annotation, dict) else [])
    if annotation.get("task_id") != task.get("task_id"):
        errors.append("annotation task_id does not match its task")
    if annotation.get("schema_version") != RETURN_SCHEMA_VERSION:
        errors.append(f"schema_version must be {RETURN_SCHEMA_VERSION!r}")
    if not _nonempty(annotation.get("annotator_id")):
        errors.append("annotator_id must be a non-empty pseudonymous string")
    extra_fields = set(annotation) - RETURN_FIELDS
    if extra_fields:
        errors.append(f"unsupported annotation field(s): {sorted(extra_fields)}")
    mappings = annotation.get("mappings")
    if not isinstance(mappings, list):
        errors.append("mappings must be a list")
        mappings = []
    part_text = _task_parts(task)
    literal_ids = _task_literals(task)
    raw_gloss = task.get("raw_gloss") if isinstance(task.get("raw_gloss"), str) else ""
    effective = task.get("effective_definition") if isinstance(task.get("effective_definition"), str) else ""
    seen_literals: set[str] = set()
    used_parts: set[str] = set()
    for index, mapping in enumerate(mappings):
        where = f"mappings[{index}]"
        if not isinstance(mapping, dict):
            errors.append(f"{where} must be an object")
            continue
        literal_id = mapping.get("literal_id")
        if not _nonempty(literal_id):
            errors.append(f"{where}.literal_id must be a non-empty string")
        elif literal_id not in literal_ids:
            errors.append(f"{where}.literal_id is not present in graph_clause")
        elif literal_id in seen_literals:
            errors.append(f"{where}.literal_id is duplicated")
        else:
            seen_literals.add(literal_id)
        status = mapping.get("status")
        if not isinstance(status, str) or status not in MAPPING_STATUSES:
            errors.append(f"{where}.status must be one of {sorted(MAPPING_STATUSES)}")
        supporting = mapping.get("supporting_part_ids")
        if not isinstance(supporting, list) or any(not _nonempty(value) for value in supporting):
            errors.append(f"{where}.supporting_part_ids must be a list of part IDs")
            supporting = []
        if len(set(supporting)) != len(supporting):
            errors.append(f"{where}.supporting_part_ids contains duplicates")
        for part_id in supporting:
            if part_id not in part_text:
                errors.append(f"{where} references an unknown part_id")
            else:
                used_parts.add(part_id)
        if status in {"exact", "partial"} and not supporting:
            errors.append(f"{where} requires supporting_part_ids for status {status}")
        if status == "none" and supporting:
            errors.append(f"{where} cannot cite supporting parts when status is none")

        spans = mapping.get("evidence_spans")
        if not isinstance(spans, list):
            errors.append(f"{where}.evidence_spans must be a list")
            spans = []
        has_gloss_evidence = False
        for span_index, span in enumerate(spans):
            span_where = f"{where}.evidence_spans[{span_index}]"
            if not isinstance(span, dict):
                errors.append(f"{span_where} must be an object")
                continue
            view = span.get("text_view")
            part_id = span.get("part_id")
            if not isinstance(view, str) or view not in TEXT_VIEWS:
                errors.append(f"{span_where}.text_view must be one of {sorted(TEXT_VIEWS)}")
                continue
            if view == "raw_gloss":
                text = raw_gloss
                has_gloss_evidence = True
                if part_id is not None:
                    errors.append(f"{span_where}.part_id is only valid for part_text")
            elif view == "effective_definition":
                text = effective
                has_gloss_evidence = True
                if part_id is not None:
                    errors.append(f"{span_where}.part_id is only valid for part_text")
            else:
                if part_id not in part_text:
                    errors.append(f"{span_where}.part_id must reference a known part for part_text")
                    continue
                if part_id not in supporting:
                    errors.append(f"{span_where}.part_id must be listed in supporting_part_ids")
                text = part_text[part_id]
            start, end = span.get("start"), span.get("end")
            if type(start) is not int or type(end) is not int or start < 0 or end <= start or end > len(text):
                errors.append(f"{span_where} must satisfy 0 <= start < end <= selected text length")
        if status in {"exact", "partial"} and not has_gloss_evidence:
            errors.append(f"{where} requires at least one raw_gloss or effective_definition evidence span")

    if seen_literals != literal_ids:
        errors.append("mappings must cover every graph_clause literal exactly once")
    unmapped = annotation.get("unmapped_part_ids")
    if not isinstance(unmapped, list) or any(not _nonempty(value) for value in unmapped):
        errors.append("unmapped_part_ids must be a list of part IDs")
        unmapped = []
    if len(set(unmapped)) != len(unmapped):
        errors.append("unmapped_part_ids contains duplicates")
    if any(part_id not in part_text for part_id in unmapped):
        errors.append("unmapped_part_ids references an unknown part_id")
    if set(unmapped) != set(part_text) - used_parts:
        errors.append("unmapped_part_ids must list exactly the parts unused by all literal mappings")
    notes = annotation.get("notes")
    if not isinstance(notes, list) or any(not isinstance(note, str) for note in notes):
        errors.append("notes must be a list of strings")
    return errors


def validate_task_batch(tasks: list[Any]) -> list[str]:
    errors: list[str] = []
    if not tasks:
        errors.append("task batch is empty")
    tasks_by_id: dict[str, dict[str, Any]] = {}
    for index, task in enumerate(tasks, start=1):
        for error in validate_task(task):
            errors.append(f"task line {index}: {error}")
        if not isinstance(task, dict):
            continue
        task_id = task.get("task_id")
        if not isinstance(task_id, str):
            continue
        if task_id in tasks_by_id:
            errors.append(f"duplicate task_id in task batch at line {index}")
        else:
            tasks_by_id[task_id] = task
    return errors


def validate_dataset(tasks: list[Any], annotations: list[Any]) -> list[str]:
    errors = validate_task_batch(tasks)
    if not annotations:
        errors.append("annotation batch is empty")
    tasks_by_id = {
        task["task_id"]: task for task in tasks
        if isinstance(task, dict) and isinstance(task.get("task_id"), str)
    }
    annotations_by_id: dict[str, dict[str, Any]] = {}
    annotators: set[str] = set()
    for index, annotation in enumerate(annotations, start=1):
        if not isinstance(annotation, dict):
            errors.append(f"annotation line {index}: annotation must be an object")
            continue
        task_id = annotation.get("task_id")
        if not isinstance(task_id, str) or task_id not in tasks_by_id:
            errors.append(f"annotation line {index}: unknown task_id")
            continue
        if task_id in annotations_by_id:
            errors.append(f"duplicate annotation for a task_id at line {index}")
            continue
        annotations_by_id[task_id] = annotation
        if isinstance(annotation.get("annotator_id"), str):
            annotators.add(annotation["annotator_id"])
        for error in validate_alignment(tasks_by_id[task_id], annotation):
            errors.append(f"annotation line {index}: {error}")
    if len(annotators) > 1:
        errors.append("each independent import must contain exactly one annotator ID")
    missing = set(tasks_by_id) - set(annotations_by_id)
    if missing:
        errors.append(f"annotation batch is incomplete: {len(missing)} task(s) missing")
    return errors


def _load_jsonl(path: Path) -> list[Any]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at line {line_number}: {exc.msg}") from exc
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tasks", type=Path, help="one JSONL task per active source-clause pair")
    parser.add_argument("annotations", type=Path, nargs="?", help="optional one-annotator returned JSONL")
    args = parser.parse_args(argv)
    try:
        tasks = _load_jsonl(args.tasks)
        if args.annotations is None:
            errors = validate_task_batch(tasks)
        else:
            annotations = _load_jsonl(args.annotations)
            errors = validate_dataset(tasks, annotations)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if errors:
        parser.error("alignment validation failed: " + "; ".join(errors[:20]))
    count = len(tasks) if args.annotations is None else len(annotations)
    print(f"Valid source-clause {'tasks' if args.annotations is None else 'mappings'}: {count} rows")
    print("Structural validation only; semantic validity remains a separate judgment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
