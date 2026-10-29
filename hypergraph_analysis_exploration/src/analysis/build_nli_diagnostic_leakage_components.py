"""Build text-free leakage components from opaque NLI diagnostic identities.

This tool assigns connected-component group IDs only. It does not assign
train/dev/test splits, generate candidate pairs, or inspect labels or text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXAMPLE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _read_rows(input_bytes: bytes) -> list[dict[str, Any]]:
    rows = []
    try:
        text = input_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("input JSONL must be valid UTF-8") from exc
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON ({exc.msg})") from exc
        if not isinstance(row, dict) or set(row) != {"example_id", "leakage_keys"}:
            raise ValueError(f"line {line_number}: expected only example_id and leakage_keys")
        example_id = row["example_id"]
        if not isinstance(example_id, str) or not EXAMPLE_ID_RE.fullmatch(example_id):
            raise ValueError(f"line {line_number}: example_id must be an opaque identifier")
        keys = row["leakage_keys"]
        if not isinstance(keys, list):
            raise ValueError(f"line {line_number}: leakage_keys must be a list")
        normalized = set()
        for key in keys:
            if not isinstance(key, dict) or set(key) != {"namespace", "key_sha256"}:
                raise ValueError(f"line {line_number}: each leakage key needs namespace and key_sha256")
            namespace = key["namespace"]
            key_sha256 = key["key_sha256"]
            if (not isinstance(namespace, str)
                    or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", namespace)):
                raise ValueError(f"line {line_number}: leakage-key namespace must be lower_snake_case")
            if not isinstance(key_sha256, str) or not SHA256_RE.fullmatch(key_sha256):
                raise ValueError(f"line {line_number}: key_sha256 must be a lowercase SHA-256")
            normalized.add((namespace, key_sha256))
        row["leakage_keys"] = [
            {"namespace": namespace, "key_sha256": key_sha256}
            for namespace, key_sha256 in sorted(normalized)
        ]
        rows.append(row)
    if not rows:
        raise ValueError("input JSONL contains no rows")
    ids = [row["example_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("example_id values must be unique")
    return rows


def build_component_manifest(rows: list[dict[str, Any]], *, input_sha256: str | None = None) -> dict[str, Any]:
    """Return a deterministic component manifest from validated opaque rows."""
    if not isinstance(rows, list) or not rows:
        raise ValueError("rows must be a non-empty list")
    if input_sha256 is not None and (not isinstance(input_sha256, str) or not SHA256_RE.fullmatch(input_sha256)):
        raise ValueError("input_sha256 must be a lowercase SHA-256")
    parent = list(range(len(rows)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        root_left, root_right = find(left), find(right)
        if root_left != root_right:
            parent[max(root_left, root_right)] = min(root_left, root_right)

    first_by_key: dict[tuple[str, str], int] = {}
    seen_ids: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"example_id", "leakage_keys"}:
            raise ValueError(f"row {index}: expected only example_id and leakage_keys")
        example_id = row["example_id"]
        if not isinstance(example_id, str) or not EXAMPLE_ID_RE.fullmatch(example_id):
            raise ValueError(f"row {index}: example_id must be an opaque identifier")
        if example_id in seen_ids:
            raise ValueError("example_id values must be unique")
        seen_ids.add(example_id)
        keys = row["leakage_keys"]
        if not isinstance(keys, list):
            raise ValueError(f"row {index}: leakage_keys must be a list")
        for key in keys:
            if not isinstance(key, dict) or set(key) != {"namespace", "key_sha256"}:
                raise ValueError(f"row {index}: each leakage key needs namespace and key_sha256")
            namespace, key_sha256 = key["namespace"], key["key_sha256"]
            if (not isinstance(namespace, str)
                    or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", namespace)
                    or not isinstance(key_sha256, str)
                    or not SHA256_RE.fullmatch(key_sha256)):
                raise ValueError(f"row {index}: invalid opaque leakage key")
            key_identity = (namespace, key_sha256)
            previous = first_by_key.setdefault(key_identity, index)
            union(index, previous)

    members_by_root: dict[int, list[str]] = defaultdict(list)
    for index, row in enumerate(rows):
        members_by_root[find(index)].append(row["example_id"])

    components = []
    assignments = []
    size_counts: Counter[int] = Counter()
    for member_ids in members_by_root.values():
        sorted_ids = sorted(member_ids)
        group_id = f"leak-{_digest(sorted_ids)}"
        size_counts[len(sorted_ids)] += 1
        components.append({"group_id": group_id, "member_ids": sorted_ids})
        assignments.extend({"example_id": example_id, "group_id": group_id} for example_id in sorted_ids)

    components.sort(key=lambda item: item["group_id"])
    assignments.sort(key=lambda item: item["example_id"])
    manifest = {
        "schema_version": "nli-diagnostic-leakage-components/0.1",
        "row_count": len(rows),
        "unconstrained_row_count": sum(not row["leakage_keys"] for row in rows),
        "component_count": len(components),
        "multi_row_component_count": sum(count for size, count in size_counts.items() if size > 1),
        "component_size_histogram": {str(size): size_counts[size] for size in sorted(size_counts)},
        "split_assignment_performed": False,
        "input_sha256": input_sha256,
        "components": components,
        "assignments": assignments,
    }
    return manifest


def build_manifest_file(input_path: Path, output_path: Path) -> bytes:
    if output_path.exists():
        raise ValueError(f"output already exists; choose a new path: {output_path}")
    input_bytes = input_path.read_bytes()
    rows = _read_rows(input_bytes)
    manifest = build_component_manifest(rows, input_sha256=hashlib.sha256(input_bytes).hexdigest())
    return (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="opaque leakage-key JSONL; never include text or labels")
    parser.add_argument("output", type=Path, help="new component manifest JSON path")
    args = parser.parse_args(argv)
    try:
        payload = build_manifest_file(args.input, args.output)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as stream:
            stream.write(payload)
    except (OSError, ValueError) as exc:
        print(f"NLI leakage component build failed: {exc}", file=sys.stderr)
        return 1
    manifest = json.loads(payload)
    print(json.dumps({
        "row_count": manifest["row_count"],
        "unconstrained_row_count": manifest["unconstrained_row_count"],
        "component_count": manifest["component_count"],
        "multi_row_component_count": manifest["multi_row_component_count"],
        "split_assignment_performed": False,
        "manifest_sha256": hashlib.sha256(payload).hexdigest(),
    }, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
