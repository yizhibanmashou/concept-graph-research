"""Write a text-free manifest for a frozen gloss-hypothesis candidate JSONL."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_FIELDS = {
    "candidate_id", "candidate_set_version", "group_id", "split",
    "source", "premise", "hypothesis", "direction",
}
OPTIONAL_FIELDS = {"relation", "formula_sha256", "composition"}


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _read_candidates(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_no}: invalid JSON ({exc.msg})") from exc
            if not isinstance(row, dict):
                raise ValueError(f"line {line_no}: candidate must be a JSON object")
            if (not REQUIRED_FIELDS <= set(row)
                    or set(row) - REQUIRED_FIELDS - OPTIONAL_FIELDS):
                raise ValueError(f"line {line_no}: candidate has missing or unexpected fields")
            if not isinstance(row.get("premise"), str) or not row["premise"]:
                raise ValueError(f"line {line_no}: premise must be a non-empty string")
            if not isinstance(row.get("hypothesis"), str) or not row["hypothesis"]:
                raise ValueError(f"line {line_no}: hypothesis must be a non-empty string")
            source = row.get("source")
            if not isinstance(source, dict) or set(source) != {"resource", "release", "sense_id", "pos"}:
                raise ValueError(f"line {line_no}: source must contain resource, release, sense_id, and pos")
            if "formula_sha256" in row and not (
                    isinstance(row["formula_sha256"], str)
                    and SHA256_RE.fullmatch(row["formula_sha256"])):
                raise ValueError(f"line {line_no}: formula_sha256 must be a lowercase SHA-256")
            if "composition" in row:
                composition = row["composition"]
                if (not isinstance(composition, dict)
                        or set(composition) != {"operator", "components"}
                        or not isinstance(composition.get("operator"), str)
                        or composition["operator"] not in {"and", "or"}
                        or not isinstance(composition.get("components"), list)
                        or len(composition["components"]) < 2):
                    raise ValueError(f"line {line_no}: composition must have operator=and|or and at least two components")
                component_ids = []
                for component in composition["components"]:
                    if (not isinstance(component, dict)
                            or set(component) != {"candidate_id", "negated"}
                            or not isinstance(component.get("candidate_id"), str)
                            or not component["candidate_id"].strip()
                            or type(component.get("negated")) is not bool):
                        raise ValueError(f"line {line_no}: each composition component needs candidate_id and boolean negated")
                    component_ids.append(component["candidate_id"])
                if len(component_ids) != len(set(component_ids)):
                    raise ValueError(f"line {line_no}: composition component candidate_ids must be unique")
                if "formula_sha256" not in row:
                    raise ValueError(f"line {line_no}: a composed candidate requires formula_sha256")
            rows.append(row)
    if not rows:
        raise ValueError("candidate JSONL contains no rows")
    version_values = [row.get("candidate_set_version") for row in rows]
    if (any(not isinstance(value, str) or not value.strip() for value in version_values)
            or len(set(version_values)) != 1):
        raise ValueError("all rows must share one non-empty candidate_set_version")
    errors = []
    ids: set[str] = set()
    group_splits: dict[str, str] = {}
    sense_splits: dict[str, str] = {}
    premise_splits: dict[str, str] = {}
    for line_no, row in enumerate(rows, start=1):
        for key in ("candidate_id", "group_id"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                errors.append(f"line {line_no}: {key} must be a non-empty string")
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            if candidate_id in ids:
                errors.append(f"line {line_no}: duplicate candidate_id")
            ids.add(candidate_id)
        if not isinstance(row.get("split"), str) or row["split"] not in {"train", "dev", "test", "unassigned"}:
            errors.append(f"line {line_no}: invalid split")
        if not isinstance(row.get("direction"), str) or row["direction"] not in {"target_to_gloss", "gloss_to_target", "both", "none"}:
            errors.append(f"line {line_no}: invalid direction")
        if "relation" in row and (not isinstance(row["relation"], str) or row["relation"] not in {"necessary", "sufficient", "biconditional", "typical", "example", "other"}):
            errors.append(f"line {line_no}: invalid relation")
        source = row["source"]
        if any(not isinstance(source.get(key), str) or not source[key].strip()
               for key in ("resource", "release", "sense_id")):
            errors.append(f"line {line_no}: source resource/release/sense_id must be non-empty strings")
        if not isinstance(source.get("pos"), str) or source["pos"] not in {"n", "v", "a", "r"}:
            errors.append(f"line {line_no}: invalid source.pos")
        if isinstance(row.get("split"), str) and row["split"] in {"train", "dev", "test"}:
            split = row["split"]
            for dimension, value, table in (
                    ("group_id", row.get("group_id"), group_splits),
                    ("sense_id", source.get("sense_id"), sense_splits),
                    ("exact premise_sha256", _sha256_text(row["premise"]), premise_splits)):
                if isinstance(value, str):
                    previous = table.setdefault(value, split)
                    if previous != split:
                        errors.append(f"line {line_no}: {dimension} leaks across train/dev/test")
    rows_by_id = {row.get("candidate_id"): row for row in rows if isinstance(row.get("candidate_id"), str)}
    composition_edges: dict[str, list[str]] = {}
    for line_no, row in enumerate(rows, start=1):
        composition = row.get("composition")
        if not isinstance(composition, dict) or not isinstance(composition.get("components"), list):
            continue
        parent_id = row.get("candidate_id")
        children = []
        for component in composition["components"]:
            if not isinstance(component, dict) or not isinstance(component.get("candidate_id"), str):
                continue
            child_id = component["candidate_id"]
            child = rows_by_id.get(child_id)
            if child is None:
                errors.append(f"line {line_no}: composition references unknown candidate_id {child_id!r}")
                continue
            if any(child.get(key) != row.get(key) for key in ("group_id", "split", "premise", "candidate_set_version")) or child.get("source") != row.get("source"):
                errors.append(f"line {line_no}: composition component {child_id!r} must share group, split, premise, source, and candidate_set_version")
            children.append(child_id)
        if isinstance(parent_id, str):
            composition_edges[parent_id] = children
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(candidate_id: str) -> None:
        if candidate_id in visiting:
            errors.append(f"composition dependency cycle includes candidate_id {candidate_id!r}")
            return
        if candidate_id in visited:
            return
        visiting.add(candidate_id)
        for child_id in composition_edges.get(candidate_id, []):
            visit(child_id)
        visiting.remove(candidate_id)
        visited.add(candidate_id)

    for candidate_id in composition_edges:
        visit(candidate_id)
    if errors:
        raise ValueError("candidate set validation failed:\n" + "\n".join(errors))
    return rows


def build_manifest(path: Path, candidate_set_version: str) -> bytes:
    rows = _read_candidates(path)
    if any(row["candidate_set_version"] != candidate_set_version for row in rows):
        raise ValueError("requested version differs from candidate JSONL candidate_set_version")
    candidates = []
    for row in sorted(rows, key=lambda item: item["candidate_id"]):
        item = {
            "candidate_id": row["candidate_id"],
            "group_id": row["group_id"],
            "split": row["split"],
            "source": row["source"],
            "direction": row["direction"],
            "premise_sha256": _sha256_text(row["premise"]),
            "hypothesis_sha256": _sha256_text(row["hypothesis"]),
        }
        for optional in ("relation", "formula_sha256", "composition"):
            if optional in row:
                item[optional] = row[optional]
        candidates.append(item)
    manifest = {
        "schema_version": "claim-review-candidate-manifest/0.2",
        "candidate_set_version": candidate_set_version,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    return (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidates", type=Path, help="unlabeled candidate-pair JSONL")
    parser.add_argument("manifest", type=Path, help="new text-free manifest path")
    parser.add_argument("--candidate-set-version", required=True)
    args = parser.parse_args(argv)
    if args.manifest.exists():
        parser.error(f"manifest already exists; choose a new path: {args.manifest}")
    try:
        payload = build_manifest(args.candidates, args.candidate_set_version)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_bytes(payload)
    except (OSError, ValueError) as exc:
        print(f"candidate manifest freeze failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "candidate_count": json.loads(payload)["candidate_count"],
        "candidate_set_version": args.candidate_set_version,
        "manifest_sha256": hashlib.sha256(payload).hexdigest(),
        "text_or_gold_in_manifest": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
