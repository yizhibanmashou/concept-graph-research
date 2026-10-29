"""Verify every file named by an OEWN frozen bundle checksum manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from src.analysis.frozen_hypergraph_audit import DEFAULT_BUNDLE


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT.parent / "report" / "oewn_full_bundle_integrity_2026-10-28.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PACKAGE_METADATA_FILES = {"manifest.json", "checksums.jsonl"}
SELF_REFERENTIAL_METADATA_FILES = {"checksums.jsonl"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit(bundle: Path) -> dict[str, Any]:
    bundle = bundle.resolve()
    manifest_path = bundle / "checksums.jsonl"
    expected: dict[str, tuple[int, str]] = {}
    malformed = duplicate = unsafe = 0
    errors: list[dict[str, str]] = []

    for line_no, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            if len(errors) < 20:
                errors.append({"kind": "malformed_json", "entry": str(line_no)})
            continue
        relative = row.get("path") if isinstance(row, dict) else None
        byte_count = row.get("bytes") if isinstance(row, dict) else None
        digest = row.get("sha256") if isinstance(row, dict) else None
        parsed = PurePosixPath(relative) if isinstance(relative, str) else None
        if (
            parsed is None
            or parsed.is_absolute()
            or ".." in parsed.parts
            or "\\" in relative
            or not isinstance(byte_count, int)
            or byte_count < 0
            or not isinstance(digest, str)
            or SHA256_RE.fullmatch(digest) is None
        ):
            unsafe += 1
            if len(errors) < 20:
                errors.append({"kind": "invalid_or_unsafe_entry", "entry": str(line_no)})
            continue
        key = parsed.as_posix()
        if key in SELF_REFERENTIAL_METADATA_FILES:
            unsafe += 1
            if len(errors) < 20:
                errors.append({"kind": "self_referential_metadata_entry", "path": key})
            continue
        if key in expected:
            duplicate += 1
            if len(errors) < 20:
                errors.append({"kind": "duplicate_path", "path": key})
            continue
        expected[key] = (byte_count, digest)

    matched = size_mismatches = hash_mismatches = missing = symlinks = 0
    hashed_bytes = 0
    actual: set[str] = set()
    for path in bundle.rglob("*"):
        relative = path.relative_to(bundle).as_posix()
        if path.is_symlink():
            symlinks += 1
            if len(errors) < 20:
                errors.append({"kind": "symlink", "path": relative})
            continue
        if not path.is_file():
            continue
        actual.add(relative)
        if relative in SELF_REFERENTIAL_METADATA_FILES:
            continue
        record = expected.get(relative)
        if record is None:
            if len(errors) < 20:
                errors.append({"kind": "unlisted_file", "path": relative})
            continue
        expected_bytes, expected_hash = record
        observed_bytes = path.stat().st_size
        if observed_bytes != expected_bytes:
            size_mismatches += 1
            if len(errors) < 20:
                errors.append({"kind": "size_mismatch", "path": relative})
            continue
        observed_hash = _sha256(path)
        hashed_bytes += observed_bytes
        if observed_hash != expected_hash:
            hash_mismatches += 1
            if len(errors) < 20:
                errors.append({"kind": "sha256_mismatch", "path": relative})
        else:
            matched += 1

    expected_paths = set(expected)
    manifest_checksum_missing = int("manifest.json" not in expected_paths)
    if manifest_checksum_missing and len(errors) < 20:
        errors.append({"kind": "manifest_not_covered_by_checksum_list"})
    for relative in sorted(expected_paths - actual):
        missing += 1
        if len(errors) < 20:
            errors.append({"kind": "missing_file", "path": relative})

    unlisted_files = max(0, len(actual - expected_paths - PACKAGE_METADATA_FILES))
    passed = (
        matched == len(expected)
        and not any((malformed, duplicate, unsafe, size_mismatches, hash_mismatches, missing, symlinks, unlisted_files))
        and manifest_checksum_missing == 0
    )
    return {
        "audit": "oewn-frozen-bundle-all-files/1",
        "bundle": bundle.name,
        "expected_file_count": len(expected),
        "actual_file_count_including_metadata": len(actual),
        "matched_file_count": matched,
        "expected_bytes": sum(byte_count for byte_count, _ in expected.values()),
        "hashed_bytes": hashed_bytes,
        "malformed_entries": malformed,
        "duplicate_entries": duplicate,
        "unsafe_entries": unsafe,
        "size_mismatches": size_mismatches,
        "sha256_mismatches": hash_mismatches,
        "missing_files": missing,
        "unlisted_files": unlisted_files,
        "symlinks": symlinks,
        "manifest_checksum_missing": manifest_checksum_missing,
        "passed": passed,
        "error_examples": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit(args.bundle)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "error_examples"}, ensure_ascii=False, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
