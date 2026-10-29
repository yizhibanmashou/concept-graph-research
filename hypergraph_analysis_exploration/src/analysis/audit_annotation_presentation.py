"""Audit generated annotation presentation views without displaying task text."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from src.analysis.presentation_order import ALGORITHM_ID, fisher_yates_task_order


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BATCH = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_v3_400_blind.jsonl"
DEFAULT_PLAN = PROJECT_ROOT / "config" / "annotation_presentation_plan_v2.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "phase7" / "annotation_presentation_v2"
TASK_FIELDS = {"task_id", "pos", "lemmas", "gloss"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid UTF-8 JSON: {path}") from exc


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_no, line in enumerate(stream, start=1):
                if not line.strip():
                    raise ValueError(f"blank JSONL row at {path}:{line_no}")
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL row at {path}:{line_no}") from exc
                if not isinstance(row, dict) or set(row) != TASK_FIELDS:
                    raise ValueError(f"unexpected task fields at {path}:{line_no}")
                if (not isinstance(row.get("task_id"), str) or not row["task_id"]
                        or not isinstance(row.get("pos"), str)
                        or not isinstance(row.get("lemmas"), list)
                        or any(not isinstance(x, str) or not x for x in row["lemmas"])
                        or not isinstance(row.get("gloss"), str) or not row["gloss"]):
                    raise ValueError(f"invalid task row at {path}:{line_no}")
                rows.append(row)
    except UnicodeDecodeError as exc:
        raise ValueError(f"file is not UTF-8: {path}") from exc
    ids = [row["task_id"] for row in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ValueError(f"empty rows or duplicate task IDs: {path}")
    return rows


def audit_presentation_views(
    batch_path: Path = DEFAULT_BATCH,
    plan_path: Path = DEFAULT_PLAN,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    batch_path, plan_path, output_dir = batch_path.resolve(), plan_path.resolve(), output_dir.resolve()
    plan, manifest = _json(plan_path), _json(output_dir / "presentation_manifest.json")
    if not isinstance(plan, dict) or plan.get("schema_version") != "annotation-presentation-plan/2":
        raise ValueError("unsupported presentation plan schema")
    if plan.get("ordering_algorithm") != ALGORITHM_ID:
        raise ValueError("unsupported presentation ordering algorithm")
    status = plan.get("status")
    if status not in {"draft_not_authorized_for_distribution", "authorized_for_distribution"}:
        raise ValueError("presentation plan lacks explicit authorization status")
    source = plan.get("source_batch")
    if not isinstance(source, dict) or _sha256(batch_path) != source.get("batch_sha256"):
        raise ValueError("canonical batch hash does not match plan")
    canonical = _jsonl(batch_path)
    if len(canonical) != source.get("candidate_count"):
        raise ValueError("canonical batch row count does not match plan")
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "annotation-presentation-manifest/2":
        raise ValueError("unsupported presentation manifest schema")
    if manifest.get("ordering_algorithm") != ALGORITHM_ID:
        raise ValueError("manifest ordering algorithm mismatch")
    algorithm_source = Path(__file__).with_name("presentation_order.py")
    generator_source = Path(__file__).with_name("randomize_annotation_presentation.py")
    if (manifest.get("ordering_algorithm_source_sha256") != _sha256(algorithm_source)
            or manifest.get("generator_source_sha256") != _sha256(generator_source)):
        raise ValueError("manifest does not match the current ordering/generator source files")
    if manifest.get("source_batch_sha256") != _sha256(batch_path):
        raise ValueError("manifest source batch hash mismatch")
    if manifest.get("source_batch_rows") != len(canonical):
        raise ValueError("manifest source batch row count mismatch")
    if manifest.get("plan_sha256") != _sha256(plan_path):
        raise ValueError("manifest plan hash mismatch")
    if manifest.get("authorization_status") != status:
        raise ValueError("manifest authorization status differs from plan")
    if manifest.get("distribution_authorized") is not (status == "authorized_for_distribution"):
        raise ValueError("manifest distribution flag is inconsistent")
    if manifest.get("answer_key_included") is not False or set(manifest.get("task_fields", [])) != TASK_FIELDS:
        raise ValueError("manifest must exclude answer key and retain only blind fields")

    slots = plan.get("presentation_slots")
    outputs = manifest.get("presentation_slots")
    if not isinstance(slots, list) or len(slots) != 2 or not isinstance(outputs, dict):
        raise ValueError("expected exactly two presentation slots")
    if set(outputs) != {slot.get("presentation_id") for slot in slots if isinstance(slot, dict)}:
        raise ValueError("manifest slot IDs do not match plan")

    source_by_id = {row["task_id"]: row for row in canonical}
    sequences: list[list[str]] = []
    allowed_files = {"presentation_manifest.json"}
    slot_summaries: dict[str, dict[str, Any]] = {}
    for slot in slots:
        if not isinstance(slot, dict):
            raise ValueError("presentation slot must be an object")
        presentation_id = slot["presentation_id"]
        spec = outputs[presentation_id]
        if not isinstance(spec, dict):
            raise ValueError(f"invalid slot manifest: {presentation_id}")
        expected_ids = fisher_yates_task_order(list(source_by_id), slot["seed"])
        relative_name = spec.get("path")
        if not isinstance(relative_name, str) or Path(relative_name).name != relative_name:
            raise ValueError(f"unsafe output path for {presentation_id}")
        allowed_files.add(relative_name)
        view_path = output_dir / relative_name
        view = _jsonl(view_path)
        actual_ids = [row["task_id"] for row in view]
        if actual_ids != expected_ids:
            raise ValueError(f"task order does not replay from plan seed: {presentation_id}")
        if any(row != source_by_id[row["task_id"]] for row in view):
            raise ValueError(f"task content differs from canonical batch: {presentation_id}")
        order_sha = hashlib.sha256("\n".join(actual_ids).encode("utf-8")).hexdigest()
        file_sha = _sha256(view_path)
        if (spec.get("seed") != slot.get("seed") or spec.get("rows") != len(view)
                or spec.get("task_order_sha256") != order_sha
                or spec.get("presentation_batch_sha256") != file_sha):
            raise ValueError(f"presentation slot hashes or counts do not match: {presentation_id}")
        sequences.append(actual_ids)
        slot_summaries[presentation_id] = {
            "rows": len(view), "seed": slot["seed"],
            "task_order_sha256": order_sha, "presentation_batch_sha256": file_sha,
        }
    if sequences[0] == sequences[1]:
        raise ValueError("presentation slots have identical task orders")
    actual_files = {path.name for path in output_dir.iterdir() if path.is_file()}
    if actual_files != allowed_files:
        raise ValueError("output directory has missing or unexpected files")

    return {
        "integrity_pass": True,
        "source_batch_rows": len(canonical),
        "presentation_slots": slot_summaries,
        "manifest_sha256": _sha256(output_dir / "presentation_manifest.json"),
        "authorization_status": status,
        "distribution_authorized": status == "authorized_for_distribution",
        "answer_key_included": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, default=DEFAULT_BATCH)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    try:
        result = audit_presentation_views(args.batch, args.plan, args.output_dir)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
