"""Suggest exact source-text substring offsets for existing part annotations.

The suggestions locate strings only. They do not establish that a part is a
faithful semantic analysis, a valid Horn premise, or supported by the gloss.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:  # Direct script execution and package/module execution are both supported.
    from .project_paths import PROJECT_ROOT
except ImportError:
    from project_paths import PROJECT_ROOT


DEFAULT_TASKS = PROJECT_ROOT / "outputs" / "phase8" / "source_clause_mapping_tasks.jsonl"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase8" / "source_part_span_suggestions.jsonl"
DEFAULT_MANIFEST = PROJECT_ROOT / "outputs" / "phase8" / "source_part_span_suggestions_manifest.json"
STATUSES = ("unique_exact_substring", "multiple_exact_substrings", "no_exact_substring")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _find_all(text: str, needle: str) -> list[dict[str, int]]:
    spans = []
    start = 0
    while True:
        index = text.find(needle, start)
        if index < 0:
            return spans
        spans.append({"start": index, "end": index + len(needle)})
        start = index + 1  # Preserve overlapping matches as ambiguity.


def _status(spans: list[dict[str, int]]) -> str:
    if not spans:
        return "no_exact_substring"
    if len(spans) == 1:
        return "unique_exact_substring"
    return "multiple_exact_substrings"


def suggest_spans(tasks_path: Path):
    task_hash = _sha256(tasks_path)
    output_rows = []
    counters = {"raw_gloss": Counter({status: 0 for status in STATUSES}),
                "effective_definition": Counter({status: 0 for status in STATUSES})}
    task_ids = set()
    part_count = 0

    with tasks_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                task = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid task JSONL at {tasks_path}:{line_number}: {exc}") from exc
            if not isinstance(task, dict):
                raise ValueError(f"Task row {line_number} must be an object")
            task_id = task.get("task_id")
            raw_gloss = task.get("raw_gloss")
            effective = task.get("effective_definition")
            parts = task.get("parts")
            if not isinstance(task_id, str) or not task_id or task_id in task_ids:
                raise ValueError(f"Task row {line_number} has a missing or duplicate task_id")
            if not isinstance(raw_gloss, str) or not isinstance(effective, str):
                raise ValueError(f"Task row {line_number} lacks raw/effective definition text")
            if not isinstance(parts, list) or not parts:
                raise ValueError(f"Task row {line_number} must contain non-empty parts")
            task_ids.add(task_id)

            seen_part_ids = set()
            part_suggestions = []
            for part in parts:
                if (not isinstance(part, dict) or not isinstance(part.get("part_id"), str)
                        or not part["part_id"] or not isinstance(part.get("text"), str)
                        or not part["text"]):
                    raise ValueError(f"Task row {line_number} contains a malformed part")
                part_id = part["part_id"]
                if part_id in seen_part_ids:
                    raise ValueError(f"Task row {line_number} contains duplicate part_id {part_id!r}")
                seen_part_ids.add(part_id)
                raw_spans = _find_all(raw_gloss, part["text"])
                effective_spans = _find_all(effective, part["text"])
                raw_status = _status(raw_spans)
                effective_status = _status(effective_spans)
                counters["raw_gloss"][raw_status] += 1
                counters["effective_definition"][effective_status] += 1
                part_suggestions.append({
                    "part_id": part_id,
                    "raw_gloss": {"status": raw_status, "spans": raw_spans},
                    "effective_definition": {"status": effective_status, "spans": effective_spans},
                })
                part_count += 1
            output_rows.append({
                "schema_version": "source-part-span-suggestions/1",
                "task_id": task_id,
                "offset_convention": "Python Unicode code-point offsets; half-open [start,end); case-sensitive exact substring only",
                "part_suggestions": part_suggestions,
            })

    if not output_rows:
        raise ValueError("No source-clause mapping tasks were supplied")
    return {
        "rows": output_rows,
        "manifest": {
            "tool_version": "source-part-span-suggestions/1",
            "input_tasks_sha256": task_hash,
            "task_count": len(output_rows),
            "part_count": part_count,
            "raw_gloss_match_status_counts": dict(counters["raw_gloss"]),
            "effective_definition_match_status_counts": dict(counters["effective_definition"]),
            "output_contains_gloss_or_part_text": False,
            "interpretation_limit": "Exact substring offsets are localization suggestions only. They do not establish token boundaries, semantic support, definition faithfulness, or a valid source-to-clause mapping; zero matches may reflect paraphrase or preprocessing differences.",
        },
    }


def _inside_project(*paths: Path):
    resolved = tuple(path.resolve() for path in paths)
    if any(not path.is_relative_to(PROJECT_ROOT.resolve()) for path in resolved):
        raise ValueError("input and output files must be inside the project directory")
    if len(set(resolved)) != len(resolved):
        raise ValueError("input, suggestions, and manifest paths must be distinct")
    return resolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest-output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--force", action="store_true", help="replace existing suggestion outputs")
    args = parser.parse_args()
    try:
        tasks_path, output_path, manifest_path = _inside_project(
            args.tasks, args.output, args.manifest_output)
    except ValueError as exc:
        parser.error(str(exc))
    if not tasks_path.is_file():
        parser.error(f"tasks file does not exist: {tasks_path}")
    if not args.force and (output_path.exists() or manifest_path.exists()):
        parser.error("output exists; pass --force to replace existing suggestion outputs")

    result = suggest_spans(tasks_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered_rows = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in result["rows"])
    output_path.write_text(rendered_rows, encoding="utf-8")
    result["manifest"]["suggestions_sha256"] = _sha256(output_path)
    manifest_path.write_text(json.dumps(result["manifest"], ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
    print(f"Suggested exact substring offsets for {result['manifest']['task_count']} task(s), "
          f"{result['manifest']['part_count']} part(s); text-free output: {output_path}")


if __name__ == "__main__":
    main()
