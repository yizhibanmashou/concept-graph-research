"""Verify the pinned OEWN bundle files before replaying a witness certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INTEGRITY_LOCK = PROJECT_ROOT / "config" / "frozen_bundle_integrity_lock.json"
REQUIRED_FILES = (
    "manifest.json",
    "checksums.jsonl",
    "graph/hypergraph_rules.jsonl",
    "graph/coverage_witnesses.jsonl",
    "indexes/senses.jsonl",
    "provenance/hypergraph_source_contract.json",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_bundle_integrity(
    bundle: Path, lock_path: Path = DEFAULT_INTEGRITY_LOCK,
) -> dict[str, Any]:
    """Compare selected bundle files with the project-pinned lock and checksums.

    The lock is a version-controlled integrity anchor for accidental/local drift,
    not a digital signature. Callers should not silently regenerate it.
    """
    errors: list[str] = []
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        manifest_path = bundle / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        checksum_path = bundle / "checksums.jsonl"
        checksum_rows = [
            json.loads(line)
            for line in checksum_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return {"valid": False, "errors": ["lock_or_bundle_metadata_unreadable"], "observed_sha256": {}}

    if lock.get("lock_version") != "oewn-frozen-bundle-integrity-lock/2":
        errors.append("unsupported_lock_version")
    expected_files = lock.get("files")
    if not isinstance(expected_files, dict) or set(expected_files) != set(REQUIRED_FILES):
        errors.append("lock_file_set_mismatch")
        expected_files = {}
    if manifest.get("semantic_fingerprint_sha256") != lock.get("bundle_semantic_fingerprint_sha256"):
        errors.append("bundle_semantic_fingerprint_mismatch")

    checksum_by_path: dict[str, str] = {}
    for row in checksum_rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            errors.append("malformed_checksum_entry")
            continue
        if row["path"] in checksum_by_path:
            errors.append("duplicate_checksum_entry")
            continue
        checksum_by_path[row["path"]] = row.get("sha256")

    observed: dict[str, str | None] = {}
    for relative in REQUIRED_FILES:
        path = bundle / Path(relative)
        actual = _sha256(path) if path.is_file() else None
        observed[relative] = actual
        if actual is None:
            errors.append(f"missing:{relative}")
            continue
        if actual != expected_files.get(relative):
            errors.append(f"lock_hash_mismatch:{relative}")
        if relative not in {"manifest.json", "checksums.jsonl"} and actual != checksum_by_path.get(relative):
            errors.append(f"bundle_checksum_mismatch:{relative}")

    if observed.get("graph/hypergraph_rules.jsonl") != manifest.get("graph_sha256"):
        errors.append("rules_hash_manifest_mismatch")
    if len(errors) != len(set(errors)):
        errors = list(dict.fromkeys(errors))
    return {"valid": not errors, "errors": errors, "observed_sha256": observed}
