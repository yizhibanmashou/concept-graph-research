"""Merge one annotator's blinded task-ID returns into canonical annotation JSONL."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from src.analysis.export_annotation_batch import PROJECT_ROOT
from src.analysis.oewn_release_crosscheck import _sha256
from src.logic.annotation_validator import load_jsonl, validate_dataset


DEFAULT_BATCH = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_blind.jsonl"
DEFAULT_ANSWER_KEY = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_answer_key.json"
DEFAULT_MANIFEST = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_manifest.json"
CANONICAL_SCHEMA_VERSIONS = {"0.4-draft", "0.5-draft", "0.6-draft", "0.7-draft"}
RETURN_FIELDS = {"task_id", "annotator_id", "analysis", "notes"}


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON file: {path}") from exc


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records, line_numbers, errors = load_jsonl(path)
    if errors:
        raise ValueError("invalid return JSONL: " + "; ".join(errors[:5]))
    if not records:
        raise ValueError("return JSONL is empty")
    return records


def build_canonical_records(
    returns_path: Path,
    batch_path: Path,
    answer_key_path: Path,
    manifest_path: Path,
    canonical_schema_version: str = "0.4-draft",
) -> list[dict[str, Any]]:
    if (not isinstance(canonical_schema_version, str)
            or canonical_schema_version not in CANONICAL_SCHEMA_VERSIONS):
        raise ValueError(
            "canonical_schema_version must be one of "
            + ", ".join(sorted(CANONICAL_SCHEMA_VERSIONS))
        )
    manifest = _read_json(manifest_path)
    if manifest.get("batch_version") != "oewn-blind-annotation-batch/1":
        raise ValueError("unsupported blind batch version")
    if manifest.get("batch_sha256") != _sha256(batch_path):
        raise ValueError("blind batch hash does not match its manifest")
    if manifest.get("answer_key_sha256") != _sha256(answer_key_path):
        raise ValueError("answer key hash does not match its manifest")

    batch_rows = _read_jsonl(batch_path)
    answer_rows = _read_json(answer_key_path)
    if not isinstance(answer_rows, list):
        raise ValueError("answer key must be a JSON list")
    if manifest.get("candidate_count") != len(batch_rows) or len(answer_rows) != len(batch_rows):
        raise ValueError("manifest, blind batch, and answer key counts differ")
    batch_by_id = {}
    for row in batch_rows:
        task_id = row.get("task_id")
        if not isinstance(task_id, str) or task_id in batch_by_id:
            raise ValueError(f"missing or duplicate task_id in blind batch: {task_id}")
        if not isinstance(row.get("gloss"), str) or not row["gloss"]:
            raise ValueError(f"missing gloss for task {task_id}")
        if not isinstance(row.get("lemmas"), list) or not row["lemmas"]:
            raise ValueError(f"missing lemmas for task {task_id}")
        batch_by_id[task_id] = row
    key_by_id = {}
    for row in answer_rows:
        if not isinstance(row, dict):
            raise ValueError("answer key rows must be objects")
        task_id = row.get("task_id")
        if not isinstance(task_id, str) or task_id in key_by_id:
            raise ValueError(f"missing or duplicate task_id in answer key: {task_id}")
        key_by_id[task_id] = row
    if set(batch_by_id) != set(key_by_id):
        raise ValueError("blind batch and answer key task IDs differ")

    returns = _read_jsonl(returns_path)
    returns_by_id = {}
    annotator_ids = set()
    for index, row in enumerate(returns, start=1):
        if set(row) != RETURN_FIELDS:
            raise ValueError(f"return row {index} must contain exactly {sorted(RETURN_FIELDS)}")
        task_id = row.get("task_id")
        if not isinstance(task_id, str) or task_id not in batch_by_id:
            raise ValueError(f"unknown task_id in return row {index}: {task_id}")
        if task_id in returns_by_id:
            raise ValueError(f"duplicate returned task_id: {task_id}")
        annotator_id = row.get("annotator_id")
        if not isinstance(annotator_id, str) or not annotator_id.strip():
            raise ValueError(f"return row {index} requires a pseudonymous annotator_id")
        annotator_ids.add(annotator_id)
        if not isinstance(row.get("analysis"), dict):
            raise ValueError(f"return row {index} analysis must be an object")
        if not isinstance(row.get("notes"), list) or any(not isinstance(note, str) for note in row["notes"]):
            raise ValueError(f"return row {index} notes must be a list of strings")
        returns_by_id[task_id] = row
    if len(annotator_ids) != 1:
        raise ValueError("each import must contain returns from exactly one annotator")
    missing = set(batch_by_id) - set(returns_by_id)
    if missing:
        raise ValueError(f"return batch is incomplete; {len(missing)} task(s) missing")

    annotator_id = next(iter(annotator_ids))
    records = []
    for task_id, task in batch_by_id.items():
        answer = key_by_id[task_id]
        sense_id = answer.get("sense_id")
        item_id = answer.get("item_id")
        if not isinstance(sense_id, str) or not isinstance(item_id, str):
            raise ValueError(f"answer key lacks sense/item identity for {task_id}")
        source_records = answer.get("source_records")
        if not isinstance(source_records, list) or not source_records:
            raise ValueError(f"answer key lacks source-record evidence for {task_id}")
        graph_features = answer.get("graph_structural_features", {})
        if not isinstance(graph_features, dict):
            raise ValueError(f"answer key has invalid graph structural features for {task_id}")
        release_comparison = answer.get("release_comparison", {})
        if not isinstance(release_comparison, dict):
            raise ValueError(f"answer key has invalid release comparison for {task_id}")
        analysis = returns_by_id[task_id]["analysis"]
        record = {
            "schema_version": canonical_schema_version,
            "item_id": item_id,
            "annotation_id": f"{item_id}:{annotator_id}:independent",
            "source": {
                "resource": manifest.get("source_release"),
                "version": manifest.get("source_release_date"),
                "record_id": sense_id,
                "input_sha256": hashlib.sha256(task["gloss"].encode("utf-8")).hexdigest(),
                "license": "CC BY 4.0; attribution in batch manifest",
            },
            "sense": {
                "synset_id": sense_id,
                "lemmas": task["lemmas"],
                "pos": task["pos"],
                "gloss": task["gloss"],
            },
            "analysis": analysis,
            "annotation": {
                "annotator_id": annotator_id,
                "adjudication_status": "independent",
                "notes": returns_by_id[task_id]["notes"],
            },
            "split": "unassigned",
            "provenance": {
                "blind_task_id": task_id,
                "sampling_panel": answer.get("panel"),
                "stratum": answer.get("stratum"),
                "graph_structural_features": graph_features,
                "release_comparison": release_comparison,
                "source_records": source_records,
                "source_release_archive_sha256": manifest.get("source_release_archive_sha256"),
                "blind_batch_sha256": manifest["batch_sha256"],
            },
        }
        records.append(record)
    errors = validate_dataset(records)
    if errors:
        raise ValueError("merged annotations failed schema validation: " + "; ".join(errors[:8]))
    return records


def write_records(records: list[dict[str, Any]], output: Path, force: bool = False) -> str:
    if output.exists() and not force:
        raise FileExistsError(f"output already exists: {output}; pass --force to replace it")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write("".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records))
    return _sha256(output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("returns", type=Path, help="completed task-ID JSONL returned by one annotator")
    parser.add_argument("--batch", type=Path, default=DEFAULT_BATCH)
    parser.add_argument("--answer-key", type=Path, default=DEFAULT_ANSWER_KEY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--canonical-schema-version", choices=sorted(CANONICAL_SCHEMA_VERSIONS),
        default="0.4-draft",
        help="schema for canonical output; experimental versions require their additional claim fields in each returned analysis",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true", help="replace an existing canonical JSONL")
    args = parser.parse_args(argv)
    try:
        records = build_canonical_records(
            args.returns, args.batch, args.answer_key, args.manifest,
            canonical_schema_version=args.canonical_schema_version,
        )
        output_hash = write_records(records, args.output, args.force)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"Imported and validated {len(records)} independent annotations: {args.output}")
    print(f"Canonical JSONL SHA-256: {output_hash}")
    print("Records remain split=unassigned; assign splits only after adjudication and leakage checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
