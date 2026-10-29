"""Verify annotation source-record references against a frozen source bundle.

This is a byte- and identity-level provenance check. It does not adjudicate
whether a formula is semantically supported by a gloss or determine release
rights. The JSON report intentionally omits glosses, identities, and paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.analysis.audit_source_release_metadata import (
    DEFAULT_MAX_SOURCE_BYTES,
    _load_checksums,
    _safe_payload_path,
    _sha256_file,
)
from src.analysis.frozen_bundle_integrity import (
    DEFAULT_INTEGRITY_LOCK,
    verify_frozen_bundle_integrity,
)
from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root
from src.logic.annotation_validator import load_jsonl, validate_dataset


SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
MAX_INDEX_BYTES = 256 * 1024 * 1024
MAX_LINE_BYTES = 8 * 1024 * 1024


class AnnotationSourceBundleVerifier:
    """Reusable verified view of immutable bundle metadata for batch routing.

    Bundle locks, the checksum sidecar, and the sense index are read and
    verified once at construction. Each ``verify`` call still rereads and
    hashes every source payload cited by those annotation records.
    """

    def __init__(
        self,
        bundle: Path,
        *,
        maximum_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
        integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
    ) -> None:
        if (not isinstance(maximum_source_bytes, int)
                or isinstance(maximum_source_bytes, bool) or maximum_source_bytes < 1):
            raise ValueError("maximum_source_bytes must be a positive integer")
        self.bundle = bundle.resolve()
        self.maximum_source_bytes = maximum_source_bytes
        self.integrity_lock = Path(integrity_lock)
        self.integrity = verify_frozen_bundle_integrity(self.bundle, self.integrity_lock)
        if not self.integrity["valid"]:
            raise ValueError("frozen bundle integrity lock failed")
        self.index_path = self.bundle / "indexes" / "senses.jsonl"
        if not self.index_path.is_file() or self.index_path.stat().st_size > MAX_INDEX_BYTES:
            raise ValueError("sense index is missing or exceeds the size limit")
        self.checksums, self.checksums_sha256 = _load_checksums(self.bundle)
        manifest = json.loads((self.bundle / "manifest.json").read_text(encoding="utf-8"))
        self.bundle_semantic_fingerprint_sha256 = manifest.get("semantic_fingerprint_sha256")
        self.sense_index_sha256 = _sha256_file(self.index_path)
        self.source_senses: dict[str, set[str]] = defaultdict(set)
        self.index_rows = 0
        with self.index_path.open("rb") as stream:
            for line_number, raw_line in enumerate(stream, start=1):
                if len(raw_line) > MAX_LINE_BYTES:
                    raise ValueError("sense-index line exceeds the size limit")
                if not raw_line.strip():
                    continue
                try:
                    row = json.loads(raw_line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError(f"invalid sense-index record at line {line_number}") from exc
                if not isinstance(row, dict):
                    raise ValueError(f"invalid sense-index record at line {line_number}")
                identity = row.get("identity")
                sources = row.get("source_records")
                if not isinstance(identity, str) or not identity or not isinstance(sources, list):
                    raise ValueError(f"incomplete sense-index record at line {line_number}")
                self.index_rows += 1
                for item in sources:
                    if isinstance(item, dict) and isinstance(item.get("path"), str):
                        self.source_senses[item["path"]].add(identity)

        self._anchor_signatures = {
            self.bundle / relative: self._file_signature(self.bundle / relative)
            for relative in self.integrity["observed_sha256"]
        }

    @staticmethod
    def _file_signature(path: Path) -> tuple[int, int]:
        stat = path.stat()
        return stat.st_size, stat.st_mtime_ns

    def _assert_bundle_metadata_unchanged(self) -> None:
        for path, signature in self._anchor_signatures.items():
            if not path.is_file() or self._file_signature(path) != signature:
                raise ValueError("frozen bundle metadata changed after verifier initialization")

    def verify(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        """Verify source records while reusing this instance's checked index."""
        self._assert_bundle_metadata_unchanged()
        return _verify_annotation_records_with_bundle(records, self)


def verify_annotation_records(
    records: list[dict[str, Any]],
    bundle: Path,
    *,
    maximum_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
    verifier: AnnotationSourceBundleVerifier | None = None,
) -> dict[str, Any]:
    """Check annotation source paths, payload hashes, sense links, and gloss bytes."""
    verifier = verifier or AnnotationSourceBundleVerifier(
        bundle, maximum_source_bytes=maximum_source_bytes
    )
    if verifier.bundle != bundle.resolve():
        raise ValueError("source bundle verifier root does not match the requested bundle")
    if maximum_source_bytes != DEFAULT_MAX_SOURCE_BYTES and verifier.maximum_source_bytes != maximum_source_bytes:
        raise ValueError("source bundle verifier has a different maximum_source_bytes setting")
    return verifier.verify(records)


def _verify_annotation_records_with_bundle(
    records: list[dict[str, Any]],
    verifier: AnnotationSourceBundleVerifier,
) -> dict[str, Any]:
    """Run per-annotation checks using one initialized frozen bundle context."""
    bundle = verifier.bundle
    index_path = verifier.index_path
    checksums = verifier.checksums
    checksums_sha256 = verifier.checksums_sha256
    source_senses = verifier.source_senses
    index_rows = verifier.index_rows
    validation_errors = validate_dataset(records)

    failures: Counter[str] = Counter()
    payload_cache: dict[str, tuple[dict[str, Any] | None, str]] = {}
    unique_paths: set[str] = set()
    source_entries = verified_entries = gloss_match_entries = 0
    records_with_verified_gloss = 0

    for record in records:
        sense = record.get("sense") if isinstance(record.get("sense"), dict) else {}
        provenance = record.get("provenance") if isinstance(record.get("provenance"), dict) else {}
        source_rows = provenance.get("source_records")
        if not isinstance(source_rows, list) or not source_rows:
            failures["missing_source_records"] += 1
            continue
        gloss = sense.get("gloss")
        sense_id = sense.get("synset_id")
        record_has_gloss_match = False
        for source_row in source_rows:
            source_entries += 1
            if not isinstance(source_row, dict):
                failures["malformed_source_record"] += 1
                continue
            relative = source_row.get("path")
            expected_hash = source_row.get("sha256")
            if (not isinstance(relative, str) or not relative
                    or "\\" in relative
                    or not isinstance(expected_hash, str)
                    or not SHA256_RE.fullmatch(expected_hash)):
                failures["malformed_source_reference"] += 1
                continue
            if sense_id not in source_senses.get(relative, set()):
                failures["source_not_indexed_for_annotation_sense"] += 1
                continue
            unique_paths.add(relative)
            if relative not in payload_cache:
                try:
                    path = _safe_payload_path(bundle, relative, verifier.maximum_source_bytes)
                    raw = path.read_bytes()
                    actual_hash = hashlib.sha256(raw).hexdigest()
                    checksum = checksums.get(relative)
                    if (actual_hash != expected_hash.lower()
                            or not isinstance(checksum, dict)
                            or checksum.get("sha256") != actual_hash
                            or type(checksum.get("bytes")) is not int
                            or checksum["bytes"] != len(raw)):
                        payload_cache[relative] = (None, "source_hash_mismatch")
                    else:
                        payload = json.loads(raw.decode("utf-8"))
                        if not isinstance(payload, dict):
                            payload_cache[relative] = (None, "source_payload_not_object")
                        else:
                            payload_cache[relative] = (payload, "")
                except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
                    payload_cache[relative] = (None, "source_payload_unreadable_or_unsafe")
            payload, error_code = payload_cache[relative]
            if error_code:
                failures[error_code] += 1
                continue
            verified_entries += 1
            synset = payload.get("synset") if isinstance(payload.get("synset"), dict) else {}
            definition = payload.get("definition") if isinstance(payload.get("definition"), dict) else {}
            text_candidates = (synset.get("raw_definition"), definition.get("definition"))
            if isinstance(gloss, str) and any(candidate == gloss for candidate in text_candidates):
                gloss_match_entries += 1
                record_has_gloss_match = True
        if record_has_gloss_match:
            records_with_verified_gloss += 1
        else:
            failures["annotation_gloss_not_found_in_verified_sources"] += 1

    integrity_pass = (
        bool(records)
        and not validation_errors
        and not failures
        and records_with_verified_gloss == len(records)
    )
    return {
        "schema_version": "annotation-source-record-verification/1",
        "scope": "source_path_payload_hash_indexed_sense_and_exact_gloss_field_match",
        "integrity_pass": integrity_pass,
        "annotation_records_canonical_sha256": hashlib.sha256(
            json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        ).hexdigest(),
        "bundle_semantic_fingerprint_sha256": verifier.bundle_semantic_fingerprint_sha256,
        "bundle_integrity_lock_valid": verifier.integrity["valid"],
        "sense_index_sha256": verifier.sense_index_sha256,
        "checksums_sha256": checksums_sha256,
        "counts": {
            "annotation_records": len(records),
            "annotation_validation_errors": len(validation_errors),
            "sense_index_rows": index_rows,
            "source_reference_entries": source_entries,
            "unique_source_payloads_checked": len(unique_paths),
            "verified_source_reference_entries": verified_entries,
            "exact_gloss_field_matches": gloss_match_entries,
            "annotation_records_with_verified_gloss": records_with_verified_gloss,
        },
        "failure_counts": dict(sorted(failures.items())),
        "interpretation_limit": (
            "A passing result binds each annotation source path to a payload indexed for its sense, "
            "checks payload bytes against both the annotation reference and frozen checksum sidecar, "
            "and finds the annotation gloss exactly in a raw/effective definition field. It does not "
            "establish upstream release identity, license compatibility, semantic support for any "
            "formula, or correctness of human adjudication."
        ),
    }


def verify_annotation_source_records(
    annotation_path: Path,
    bundle: Path,
    *,
    maximum_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> dict[str, Any]:
    """Load canonical JSONL and verify its source records against the bundle."""
    annotation_path = annotation_path.resolve()
    records, line_numbers, parse_errors = load_jsonl(annotation_path)
    if parse_errors:
        return {
            "schema_version": "annotation-source-record-verification/1",
            "scope": "source_path_payload_hash_indexed_sense_and_exact_gloss_field_match",
            "integrity_pass": False,
            "input_sha256": _sha256_file(annotation_path),
            "counts": {
                "annotation_records": len(records),
                "parse_errors": len(parse_errors),
            },
            "failure_counts": {"invalid_annotation_jsonl": len(parse_errors)},
            "interpretation_limit": (
                "Source verification was not attempted because the annotation JSONL contains parse errors."
            ),
        }
    report = verify_annotation_records(records, bundle, maximum_source_bytes=maximum_source_bytes)
    report["input_sha256"] = _sha256_file(annotation_path)
    report["counts"]["annotation_jsonl_validation_errors"] = len(
        validate_dataset(records, line_numbers)
    )
    if report["counts"]["annotation_jsonl_validation_errors"]:
        report["integrity_pass"] = False
        report["failure_counts"]["invalid_annotation_jsonl_records"] = report["counts"][
            "annotation_jsonl_validation_errors"
        ]
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotations", type=Path, help="canonical annotation JSONL")
    parser.add_argument("--bundle", type=Path, default=configured_bundle_root())
    parser.add_argument("--max-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    args = parser.parse_args(argv)
    try:
        report = verify_annotation_source_records(
            args.annotations, args.bundle, maximum_source_bytes=args.max_source_bytes
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["integrity_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
