"""Summarize two raw annotation returns by stratum without exposing IDs/text.

The report is a response/schema audit, not an agreement or semantic-validity
analysis. It preserves incomplete and invalid return counts rather than
silently dropping them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.logic.annotation_validator import validate_record


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BATCH = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_v3_400_blind.jsonl"
DEFAULT_ANSWER_KEY = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_v3_400_answer_key.json"
DEFAULT_MANIFEST = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_v3_400_manifest.json"
DEFAULT_SAMPLING_MANIFEST = PROJECT_ROOT / "outputs" / "phase7" / "annotation_candidate_frame_v3_400_manifest.json"
RETURN_FIELDS = {"task_id", "annotator_id", "analysis", "notes"}
ANALYSIS_STATUSES = (
    "annotated", "ambiguous", "underspecified", "unsupported", "needs_review",
    "not_a_definition", "source_unclear",
)
PROJECTION_STATUSES = ("projectable", "partial", "unsupported", "not_attempted")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[Any]:
    with path.open("r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def _canonical_record(
    row: dict[str, Any], task: dict[str, Any], answer: dict[str, Any], manifest: dict[str, Any],
) -> dict[str, Any]:
    item_id = answer.get("item_id")
    sense_id = answer.get("sense_id")
    return {
        "schema_version": "0.4-draft",
        "item_id": item_id,
        "annotation_id": f"{item_id}:{row.get('annotator_id')}:independent",
        "source": {
            "resource": manifest.get("source_release"),
            "version": manifest.get("source_release_date"),
            "record_id": sense_id,
            "input_sha256": hashlib.sha256(task["gloss"].encode("utf-8")).hexdigest(),
            "license": "CC BY 4.0; attribution in batch manifest",
        },
        "sense": {
            "synset_id": sense_id,
            "lemmas": task.get("lemmas"),
            "pos": task.get("pos"),
            "gloss": task.get("gloss"),
        },
        "analysis": row.get("analysis"),
        "annotation": {
            "annotator_id": row.get("annotator_id"),
            "adjudication_status": "independent",
            "notes": row.get("notes"),
        },
        "split": "unassigned",
        "provenance": {
            "blind_task_id": row.get("task_id"),
            "sampling_panel": answer.get("panel"),
            "stratum": answer.get("stratum"),
            "graph_structural_features": answer.get("graph_structural_features", {}),
            "release_comparison": answer.get("release_comparison", {}),
            "source_records": answer.get("source_records", []),
            "source_release_archive_sha256": manifest.get("source_release_archive_sha256"),
            "blind_batch_sha256": manifest.get("batch_sha256"),
        },
    }


def _audit_one(
    path: Path,
    task_to_stratum: dict[str, str],
    task_rows: dict[str, dict[str, Any]],
    answer_rows: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    input_counts = Counter()
    annotator_ids: set[str] = set()
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            input_counts["nonblank_rows"] += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                input_counts["invalid_json_rows"] += 1
                continue
            if not isinstance(row, dict):
                input_counts["non_object_rows"] += 1
                continue
            task_id = row.get("task_id")
            if not isinstance(task_id, str) or task_id not in task_to_stratum:
                input_counts["unknown_or_missing_task_rows"] += 1
                continue
            by_task[task_id].append(row)
            if set(row) == RETURN_FIELDS:
                annotator_id = row.get("annotator_id")
                if isinstance(annotator_id, str) and annotator_id.strip():
                    annotator_ids.add(annotator_id)

    strata = sorted(set(task_to_stratum.values()))
    summaries = {
        name: {
            "expected": 0,
            "unique_returned": 0,
            "schema_valid": 0,
            "missing": 0,
            "duplicate_task": 0,
            "invalid_return_shape": 0,
            "annotation_schema_invalid": 0,
            "analysis_status_counts": {status: 0 for status in ANALYSIS_STATUSES},
            "horn_projection_status_counts": {status: 0 for status in PROJECTION_STATUSES},
        }
        for name in strata
    }
    valid_tasks: set[str] = set()
    for task_id, stratum in task_to_stratum.items():
        summary = summaries[stratum]
        summary["expected"] += 1
        rows = by_task.get(task_id, [])
        if not rows:
            summary["missing"] += 1
            continue
        summary["unique_returned"] += 1
        if len(rows) != 1:
            summary["duplicate_task"] += 1
            input_counts["duplicate_task_groups"] += 1
            input_counts["duplicate_excess_rows"] += len(rows) - 1
            continue
        row = rows[0]
        if set(row) != RETURN_FIELDS:
            summary["invalid_return_shape"] += 1
            continue
        record = _canonical_record(row, task_rows[task_id], answer_rows[task_id], manifest)
        if validate_record(record):
            summary["annotation_schema_invalid"] += 1
            continue
        valid_tasks.add(task_id)
        summary["schema_valid"] += 1
        status = record["analysis"]["status"]
        projection = record["analysis"]["horn_projection"]["status"]
        summary["analysis_status_counts"][status] += 1
        summary["horn_projection_status_counts"][projection] += 1

    input_counts["valid_unique_tasks"] = len(valid_tasks)
    input_counts["distinct_pseudonymous_annotator_ids"] = len(annotator_ids)
    input_counts["annotator_id_consistent"] = int(len(annotator_ids) == 1)
    input_counts["missing_tasks"] = sum(row["missing"] for row in summaries.values())
    input_counts["duplicate_task_groups"] = int(input_counts["duplicate_task_groups"])
    input_counts["invalid_return_shape_tasks"] = sum(row["invalid_return_shape"] for row in summaries.values())
    input_counts["annotation_schema_invalid_tasks"] = sum(row["annotation_schema_invalid"] for row in summaries.values())
    return {
        "sha256": _sha256(path),
        "counts": dict(input_counts),
        "by_stratum": summaries,
        "valid_task_ids_internal": valid_tasks,
        "annotator_ids_internal": annotator_ids,
    }


def audit_coverage(
    returns_a: Path, returns_b: Path, batch_path: Path, answer_key_path: Path,
    manifest_path: Path, sampling_manifest_path: Path,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sampling_manifest = json.loads(sampling_manifest_path.read_text(encoding="utf-8"))
    if manifest.get("batch_sha256") != _sha256(batch_path):
        raise ValueError("batch_manifest_mismatch")
    if manifest.get("answer_key_sha256") != _sha256(answer_key_path):
        raise ValueError("answer_key_manifest_mismatch")
    batch = _read_jsonl(batch_path)
    answers = json.loads(answer_key_path.read_text(encoding="utf-8"))
    if not isinstance(answers, list) or len(batch) != len(answers) or len(batch) != manifest.get("candidate_count"):
        raise ValueError("input_count_mismatch")
    task_rows: dict[str, dict[str, Any]] = {}
    for row in batch:
        if not isinstance(row, dict) or not isinstance(row.get("task_id"), str) or row["task_id"] in task_rows:
            raise ValueError("invalid_batch_task_index")
        task_rows[row["task_id"]] = row
    answer_rows: dict[str, dict[str, Any]] = {}
    task_to_stratum: dict[str, str] = {}
    for row in answers:
        if not isinstance(row, dict) or not isinstance(row.get("task_id"), str) or row["task_id"] in answer_rows:
            raise ValueError("invalid_answer_key_task_index")
        task_id = row["task_id"]
        stratum = row.get("stratum")
        if not isinstance(stratum, str) or not stratum:
            raise ValueError("invalid_stratum_metadata")
        answer_rows[task_id] = row
        task_to_stratum[task_id] = stratum
    if set(task_rows) != set(answer_rows):
        raise ValueError("batch_answer_key_task_mismatch")
    answer_strata = Counter(row.get("stratum") for row in answers)
    planned_strata = sampling_manifest.get("random_panel_allocation")
    sampling_binding_valid = (
        isinstance(planned_strata, dict)
        and manifest.get("frame_sha256") == sampling_manifest.get("frame_sha256")
        and manifest.get("candidate_count") == sampling_manifest.get("candidate_count")
        and answer_strata == Counter(planned_strata)
        and all(
            sampling_manifest.get("random_panel_strata", {}).get(name, {}).get("sample_count") == count
            for name, count in answer_strata.items()
        )
        and all(row.get("panel") == "random_stratified" for row in answers)
    )
    if not sampling_binding_valid:
        raise ValueError("sampling_manifest_binding_mismatch")

    a = _audit_one(returns_a, task_to_stratum, task_rows, answer_rows, manifest)
    b = _audit_one(returns_b, task_to_stratum, task_rows, answer_rows, manifest)
    valid_a = a.pop("valid_task_ids_internal")
    valid_b = b.pop("valid_task_ids_internal")
    annotator_ids_a = a.pop("annotator_ids_internal")
    annotator_ids_b = b.pop("annotator_ids_internal")
    paired = valid_a & valid_b
    annotator_ids_distinct = len(annotator_ids_a) == len(annotator_ids_b) == 1 and annotator_ids_a != annotator_ids_b
    by_stratum = {}
    for stratum in sorted(set(task_to_stratum.values())):
        expected_tasks = {task for task, name in task_to_stratum.items() if name == stratum}
        paired_count = sum(task in paired for task in expected_tasks)
        by_stratum[stratum] = {
            "expected": len(expected_tasks),
            "paired_schema_valid": paired_count,
            "a_only_schema_valid": sum(task in valid_a - valid_b for task in expected_tasks),
            "b_only_schema_valid": sum(task in valid_b - valid_a for task in expected_tasks),
            "complete_pair_stratum": paired_count == len(expected_tasks),
        }
    complete = (
        len(paired) == len(task_to_stratum)
        and annotator_ids_distinct
        and a["counts"].get("annotator_id_consistent") == 1
        and b["counts"].get("annotator_id_consistent") == 1
        and a["counts"].get("unknown_or_missing_task_rows", 0) == 0
        and b["counts"].get("unknown_or_missing_task_rows", 0) == 0
        and a["counts"].get("invalid_json_rows", 0) == 0
        and b["counts"].get("invalid_json_rows", 0) == 0
        and a["counts"].get("non_object_rows", 0) == 0
        and b["counts"].get("non_object_rows", 0) == 0
        and a["counts"].get("duplicate_task_groups", 0) == 0
        and b["counts"].get("duplicate_task_groups", 0) == 0
        and a["counts"].get("invalid_return_shape_tasks", 0) == 0
        and b["counts"].get("invalid_return_shape_tasks", 0) == 0
        and a["counts"].get("annotation_schema_invalid_tasks", 0) == 0
        and b["counts"].get("annotation_schema_invalid_tasks", 0) == 0
        and sampling_binding_valid
    )
    return {
        "schema_version": "annotation-response-coverage-audit/1",
        "scope": "response_and_schema_coverage_only",
        "input_sha256": {
            "annotator_a_return": a["sha256"],
            "annotator_b_return": b["sha256"],
            "blind_batch": _sha256(batch_path),
            "answer_key": _sha256(answer_key_path),
            "batch_manifest": _sha256(manifest_path),
            "sampling_manifest": _sha256(sampling_manifest_path),
        },
        "annotator_a": {"counts": a["counts"], "by_stratum": a["by_stratum"]},
        "annotator_b": {"counts": b["counts"], "by_stratum": b["by_stratum"]},
        "paired_by_stratum": by_stratum,
        "paired_schema_valid_count": len(paired),
        "planned_item_count": len(task_to_stratum),
        "sampling_manifest_binding_valid": sampling_binding_valid,
        "annotator_ids_distinct": annotator_ids_distinct,
        "complete_valid_paired_return": complete,
        "design_weighted_agreement_eligible": complete,
        "interpretation_limit": "Coverage and schema only; this report does not estimate agreement or semantic validity.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotator_a", type=Path)
    parser.add_argument("annotator_b", type=Path)
    parser.add_argument("--batch", type=Path, default=DEFAULT_BATCH)
    parser.add_argument("--answer-key", type=Path, default=DEFAULT_ANSWER_KEY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--sampling-manifest", type=Path, default=DEFAULT_SAMPLING_MANIFEST)
    args = parser.parse_args(argv)
    try:
        result = audit_coverage(
            args.annotator_a, args.annotator_b, args.batch, args.answer_key,
            args.manifest, args.sampling_manifest,
        )
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        print(json.dumps({
            "schema_version": "annotation-response-coverage-audit/1",
            "scope": "response_and_schema_coverage_only",
            "audit_error": "input_unreadable_or_inconsistent",
        }, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["complete_valid_paired_return"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
