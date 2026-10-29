"""Audit source-record metadata coverage without emitting source text or IDs.

This read-only census verifies every source-record payload referenced by the
frozen sense index against checksums.jsonl, then aggregates metadata field
coverage relevant to provenance and release review. It does not determine
license compatibility or grant release clearance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

from src.analysis.frozen_bundle_integrity import verify_frozen_bundle_integrity
from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_BUNDLE = configured_bundle_root()
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase23" / "source_release_metadata_audit.json"
MAX_INDEX_BYTES = 256 * 1024 * 1024
MAX_LINE_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_SOURCE_BYTES = 16 * 1024 * 1024
SAFE_CATEGORY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}$")
LICENSE_TERMS = ("license", "licence", "copyright", "attribution", "rights")
ORIGIN_TERMS = ("source", "origin", "release", "version", "url", "doi", "sha256", "checksum", "kaikki")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_checksums(bundle: Path) -> tuple[dict[str, dict[str, Any]], str]:
    path = bundle / "checksums.jsonl"
    if not path.is_file():
        raise ValueError("frozen bundle checksums.jsonl is missing")
    if path.stat().st_size > MAX_INDEX_BYTES:
        raise ValueError("checksums.jsonl exceeds the configured 256 MiB safety limit")
    rows: dict[str, dict[str, Any]] = {}
    with path.open("rb") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            if len(raw_line) > MAX_LINE_BYTES:
                raise ValueError(f"checksums.jsonl line {line_number} exceeds the 8 MiB safety limit")
            if not raw_line.strip():
                continue
            try:
                row = json.loads(raw_line)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid checksums.jsonl record at line {line_number}") from exc
            relative = row.get("path") if isinstance(row, dict) else None
            if not isinstance(relative, str) or not relative or relative in rows:
                raise ValueError("checksums.jsonl has a missing or duplicate path")
            rows[relative] = row
    return rows, _sha256_file(path)


def _safe_payload_path(bundle: Path, relative: Any, maximum_bytes: int) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("source-record metadata has a missing path")
    posix = PurePosixPath(relative)
    if posix.is_absolute() or ".." in posix.parts:
        raise ValueError("source-record metadata has an unsafe relative path")
    path = bundle.joinpath(*posix.parts).resolve()
    if not path.is_relative_to(bundle) or not path.is_file():
        raise ValueError("source-record payload is missing or resolves outside the frozen bundle")
    if path.stat().st_size > maximum_bytes:
        raise ValueError("source-record payload exceeds the configured per-file byte limit")
    return path


def _field_paths(value: Any, prefix: str = "") -> Iterator[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                continue
            path = f"{prefix}.{key}" if prefix else key
            yield path
            yield from _field_paths(child, path)
    elif isinstance(value, list):
        for child in value:
            if isinstance(child, (dict, list)):
                yield from _field_paths(child, prefix + "[]")


def _category(value: Any) -> str | None:
    if isinstance(value, str) and SAFE_CATEGORY.fullmatch(value):
        return value
    if value is None:
        return None
    return "noncanonical_or_nonscalar"


def _source_family(relative: str) -> str:
    parts = PurePosixPath(relative).parts
    if len(parts) >= 3 and parts[0] == "sources" and parts[1] == "Synset":
        return "/".join(parts[:3])
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return "other"


def _direct_categories(payload: dict[str, Any]) -> Iterator[tuple[str, Any]]:
    yield "schema_version", payload.get("schema_version")
    yield "pipeline_version", payload.get("pipeline_version")
    yield "source_inventory", payload.get("source_inventory")
    synset = payload.get("synset")
    if isinstance(synset, dict):
        yield "synset.source_inventory", synset.get("source_inventory")
    source_record = payload.get("source_record")
    if isinstance(source_record, dict):
        yield "source_record.target_source_inventory", source_record.get("target_source_inventory")
        yield "source_record.target_source_kind", source_record.get("target_source_kind")
    pseudo = payload.get("pseudo_synset")
    if isinstance(pseudo, dict):
        yield "pseudo_synset.source_kind", pseudo.get("source_kind")


def audit_source_release_metadata(
    bundle: Path,
    *,
    maximum_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
    progress_every: int = 5000,
) -> dict[str, Any]:
    bundle = bundle.resolve()
    if not isinstance(maximum_source_bytes, int) or isinstance(maximum_source_bytes, bool) or maximum_source_bytes < 1:
        raise ValueError("maximum_source_bytes must be a positive integer")
    integrity = verify_frozen_bundle_integrity(bundle)
    if not integrity["valid"]:
        raise ValueError("frozen bundle integrity lock failed: " + ", ".join(integrity["errors"]))

    index_path = bundle / "indexes" / "senses.jsonl"
    if not index_path.is_file() or index_path.stat().st_size > MAX_INDEX_BYTES:
        raise ValueError("sense index is missing or exceeds the 256 MiB safety limit")
    checksums, checksums_sha256 = _load_checksums(bundle)

    family_counts: Counter[str] = Counter()
    category_counts: dict[str, Counter[str]] = {}
    license_field_counts: Counter[str] = Counter()
    origin_field_counts: Counter[str] = Counter()
    record_key_counts: Counter[str] = Counter()
    payload_digest = hashlib.sha256()
    seen_paths: set[str] = set()
    senses = source_references = payloads_read = payload_bytes = duplicate_references = 0
    license_payloads = origin_payloads = malformed_rows = 0

    with index_path.open("rb") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            if not raw_line.strip():
                continue
            if len(raw_line) > MAX_LINE_BYTES:
                raise ValueError(f"sense-index line {line_number} exceeds the 8 MiB safety limit")
            try:
                row = json.loads(raw_line)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid sense-index JSON at line {line_number}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"sense-index line {line_number} is not an object")
            senses += 1
            source_rows = row.get("source_records")
            if not isinstance(source_rows, list):
                malformed_rows += 1
                continue
            for source_meta in source_rows:
                if not isinstance(source_meta, dict):
                    malformed_rows += 1
                    continue
                relative = source_meta.get("path")
                if not isinstance(relative, str) or relative in seen_paths:
                    duplicate_references += int(isinstance(relative, str) and relative in seen_paths)
                    if not isinstance(relative, str):
                        malformed_rows += 1
                    continue
                seen_paths.add(relative)
                source_references += 1
                source_path = _safe_payload_path(bundle, relative, maximum_source_bytes)
                raw = source_path.read_bytes()
                try:
                    payload = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError("source-record payload is not valid UTF-8 JSON") from exc
                if not isinstance(payload, dict):
                    raise ValueError("source-record payload is not a JSON object")

                checksum = checksums.get(relative)
                actual_sha256 = _sha256_bytes(raw)
                if (not isinstance(checksum, dict)
                        or checksum.get("sha256") != actual_sha256
                        or type(checksum.get("bytes")) is not int
                        or checksum["bytes"] != len(raw)):
                    raise ValueError("source-record payload differs from frozen checksums.jsonl")

                payloads_read += 1
                payload_bytes += len(raw)
                family_counts[_source_family(relative)] += 1
                payload_digest.update(len(raw).to_bytes(8, "big"))
                payload_digest.update(bytes.fromhex(actual_sha256))

                for name, value in _direct_categories(payload):
                    category = _category(value)
                    if category is not None:
                        category_counts.setdefault(name, Counter())[category] += 1
                source_record = payload.get("source_record")
                if isinstance(source_record, dict):
                    record_key_counts.update(source_record.keys())

                paths = set(_field_paths(payload))
                license_paths = sorted(path for path in paths
                                       if any(term in path.casefold() for term in LICENSE_TERMS))
                origin_paths = sorted(path for path in paths
                                      if any(term in path.casefold() for term in ORIGIN_TERMS))
                license_payloads += bool(license_paths)
                origin_payloads += bool(origin_paths)
                license_field_counts.update(license_paths)
                origin_field_counts.update(origin_paths)

                if progress_every > 0 and payloads_read % progress_every == 0:
                    print(f"Verified {payloads_read} source payloads across {senses} senses", flush=True)

    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    return {
        "audit_version": "source-release-metadata-census/1",
        "bundle_semantic_fingerprint_sha256": manifest.get("semantic_fingerprint_sha256"),
        "bundle_integrity_lock_valid": integrity["valid"],
        "bundle_integrity_lock_version": "oewn-frozen-bundle-integrity-lock/2",
        "integrity_lock_observed_sha256": integrity["observed_sha256"],
        "sense_index_sha256": _sha256_file(index_path),
        "checksums_sha256": checksums_sha256,
        "source_payload_sequence_sha256": payload_digest.hexdigest(),
        "counts": {
            "sense_index_records": senses,
            "source_record_references": source_references,
            "unique_source_payloads_read": payloads_read,
            "duplicate_source_path_references": duplicate_references,
            "malformed_index_records": malformed_rows,
            "all_source_payloads_match_frozen_checksums": payloads_read == source_references,
            "source_payload_bytes": payload_bytes,
            "payloads_with_explicit_license_like_key": license_payloads,
            "payloads_with_origin_or_version_like_key": origin_payloads,
            "release_clearance": "not_assessed; source-level rights and license compatibility require human review",
        },
        "source_path_family_counts": dict(sorted(family_counts.items())),
        "categorical_metadata_counts": {
            name: dict(sorted(values.items())) for name, values in sorted(category_counts.items())
        },
        "source_record_key_presence_counts": dict(sorted(record_key_counts.items())),
        "license_like_field_name_counts": dict(sorted(license_field_counts.items())),
        "origin_or_version_field_name_counts": dict(sorted(origin_field_counts.items())),
        "raw_text_ids_and_paths_emitted": False,
        "scope": "every unique source-record payload referenced by indexes/senses.jsonl, including inactive and recovered-history records",
        "interpretation_limit": (
            "Field-name and categorical metadata coverage are discovery aids only. Missing conventional license keys do not prove no license applies; "
            "present origin/version identifiers do not establish rights. The census never grants public-release clearance."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--max-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--progress-every", type=int, default=5000)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error(f"output exists; pass --force to replace: {output}")
    try:
        report = audit_source_release_metadata(
            args.bundle,
            maximum_source_bytes=args.max_source_bytes,
            progress_every=args.progress_every,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = report["counts"]
    print(json.dumps({
        "output": str(output),
        "unique_source_payloads_read": counts["unique_source_payloads_read"],
        "all_checksums_match": counts["all_source_payloads_match_frozen_checksums"],
        "payloads_with_license_like_key": counts["payloads_with_explicit_license_like_key"],
        "release_clearance": counts["release_clearance"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
