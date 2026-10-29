"""Create deterministic, independently randomized views of a locked blind batch.

The canonical batch and answer key are not modified. Presentation exports retain
stable task IDs so annotation returns are joined by ID rather than row position.
These exports contain raw gloss text and must remain within the approved local
workspace until the separate rights and distribution gates are cleared.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from src.analysis.presentation_order import ALGORITHM_ID, fisher_yates_task_order


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLAN = PROJECT_ROOT / "config" / "annotation_presentation_plan_v2.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase7" / "annotation_presentation_v2"
EXPECTED_FIELDS = {"task_id", "pos", "lemmas", "gloss"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid UTF-8 JSON: {path}") from exc


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, raw in enumerate(stream, start=1):
                if not raw.strip():
                    raise ValueError(f"blank line in canonical batch at line {line_number}")
                try:
                    value = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSON at canonical batch line {line_number}") from exc
                if not isinstance(value, dict) or set(value) != EXPECTED_FIELDS:
                    raise ValueError(f"canonical batch line {line_number} has unexpected fields")
                task_id = value.get("task_id")
                if (not isinstance(task_id, str) or not task_id
                        or not isinstance(value.get("pos"), str)
                        or not isinstance(value.get("lemmas"), list)
                        or any(not isinstance(item, str) or not item for item in value["lemmas"])
                        or not isinstance(value.get("gloss"), str) or not value["gloss"]):
                    raise ValueError(f"invalid task record at canonical batch line {line_number}")
                rows.append(value)
    except UnicodeDecodeError as exc:
        raise ValueError(f"canonical batch is not UTF-8: {path}") from exc
    if not rows:
        raise ValueError("canonical batch is empty")
    task_ids = [row["task_id"] for row in rows]
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("canonical batch contains duplicate task IDs")
    return rows


def create_presentation_views(
    batch_path: Path,
    plan_path: Path,
    output_dir: Path,
    force: bool = False,
) -> dict[str, Any]:
    batch_path = batch_path.resolve()
    plan_path = plan_path.resolve()
    output_dir = output_dir.resolve()
    plan = _read_json(plan_path)
    if not isinstance(plan, dict) or plan.get("schema_version") != "annotation-presentation-plan/2":
        raise ValueError("unsupported annotation presentation plan schema")
    if plan.get("ordering_algorithm") != ALGORITHM_ID:
        raise ValueError("unsupported presentation ordering algorithm")
    authorization_status = plan.get("status")
    if authorization_status not in {
        "draft_not_authorized_for_distribution",
        "authorized_for_distribution",
    }:
        raise ValueError("plan status must explicitly record whether distribution is authorized")
    source = plan.get("source_batch")
    if not isinstance(source, dict):
        raise ValueError("presentation plan lacks source_batch")
    if not isinstance(source.get("batch_sha256"), str) or _sha256(batch_path) != source["batch_sha256"].lower():
        raise ValueError("canonical batch hash does not match the presentation plan")
    rows = _read_jsonl(batch_path)
    if len(rows) != source.get("candidate_count"):
        raise ValueError("canonical batch count does not match the presentation plan")

    slots = plan.get("presentation_slots")
    if not isinstance(slots, list) or len(slots) != 2:
        raise ValueError("the current study plan must define exactly two presentation slots")
    slot_ids: set[str] = set()
    seeds: set[int] = set()
    outputs: dict[str, dict[str, Any]] = {}
    ordered_id_sequences: list[list[str]] = []
    for slot in slots:
        if not isinstance(slot, dict):
            raise ValueError("presentation slot must be an object")
        presentation_id, seed = slot.get("presentation_id"), slot.get("seed")
        if not isinstance(presentation_id, str) or not presentation_id.strip() or presentation_id in slot_ids:
            raise ValueError("presentation IDs must be non-empty and unique")
        if isinstance(seed, bool) or not isinstance(seed, int) or seed in seeds:
            raise ValueError("presentation seeds must be unique integers")
        slot_ids.add(presentation_id)
        seeds.add(seed)
        ordered_ids = fisher_yates_task_order([row["task_id"] for row in rows], seed)
        if ordered_ids == [row["task_id"] for row in rows]:
            raise ValueError(f"presentation slot {presentation_id} retained the canonical order")
        ordered_id_sequences.append(ordered_ids)
        order = {task_id: index for index, task_id in enumerate(ordered_ids)}
        view_rows = sorted(rows, key=lambda row: order[row["task_id"]])
        output_path = output_dir / f"{presentation_id}.jsonl"
        payload = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in view_rows)
        output_bytes = payload.encode("utf-8")
        outputs[presentation_id] = {
            "seed": seed,
            "path": output_path.name,
            "rows": len(view_rows),
            "task_order_sha256": hashlib.sha256("\n".join(ordered_ids).encode("utf-8")).hexdigest(),
            "presentation_batch_sha256": hashlib.sha256(output_bytes).hexdigest(),
            "_payload": payload,
        }
    if ordered_id_sequences[0] == ordered_id_sequences[1]:
        raise ValueError("the two presentation slots produced identical task orders")
    if output_dir.exists() and not force:
        raise FileExistsError(f"output directory already exists: {output_dir}; pass --force to replace its files")
    output_dir.mkdir(parents=True, exist_ok=True)
    for presentation_id, spec in outputs.items():
        (output_dir / spec["path"]).write_text(spec.pop("_payload"), encoding="utf-8", newline="\n")
    manifest = {
        "schema_version": "annotation-presentation-manifest/2",
        "ordering_algorithm": ALGORITHM_ID,
        "source_batch_sha256": _sha256(batch_path),
        "source_batch_rows": len(rows),
        "plan_sha256": _sha256(plan_path),
        "ordering_algorithm_source_sha256": _sha256(Path(__file__).with_name("presentation_order.py")),
        "generator_source_sha256": _sha256(Path(__file__)),
        "presentation_slots": outputs,
        "task_fields": sorted(EXPECTED_FIELDS),
        "alignment": "task_id; row order is randomized independently per presentation slot",
        "answer_key_included": False,
        "authorization_status": authorization_status,
        "distribution_authorized": authorization_status == "authorized_for_distribution",
    }
    manifest_path = output_dir / "presentation_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    manifest["presentation_manifest_sha256"] = _sha256(manifest_path)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, default=PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_v3_400_blind.jsonl")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="replace existing presentation files")
    args = parser.parse_args(argv)
    try:
        manifest = create_presentation_views(args.batch, args.plan, args.output_dir, args.force)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
