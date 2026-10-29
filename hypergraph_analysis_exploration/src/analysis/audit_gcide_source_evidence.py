"""Audit GCIDE-labeled provenance in the frozen alternative/definition source family.

The output contains aggregate counts and file-level bundle fingerprints only. It
never emits gloss text, sense IDs, source paths, or arbitrary source labels. This
is a frozen-bundle evidence census, not an upstream archive match or a license
clearance decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.audit_source_release_metadata import (
    DEFAULT_MAX_SOURCE_BYTES,
    _load_checksums,
    _safe_payload_path,
    _sha256_bytes,
    _sha256_file,
)
from src.analysis.frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK, verify_frozen_bundle_integrity
from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root

SOURCE_FAMILY = "sources/Synset/alternative_or_definition_wsd_frozen/"
GCIDE_LABEL = "GCIDE_0.54"
VERSION_EXPECTED = "expected_0.54"
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _normalized_source_label(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return re.sub(r"\s+", "_", value.strip())
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase125" / "gcide_source_evidence_census.json"


def audit_gcide_source_evidence(
    bundle: Path,
    *,
    maximum_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
) -> dict[str, Any]:
    bundle = bundle.resolve()
    integrity = verify_frozen_bundle_integrity(bundle)
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity lock did not pass")
    index_path = bundle / "indexes" / "senses.jsonl"
    if not index_path.is_file():
        raise ValueError("frozen sense index is missing")
    checksums, checksums_sha256 = _load_checksums(bundle)

    target_paths: set[str] = set()
    index_rows = 0
    indexed_path_references = 0
    with index_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            try:
                row = json.loads(raw_line)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("frozen sense index contains invalid JSON") from exc
            index_rows += 1
            source_records = row.get("source_records") if isinstance(row, dict) else None
            if not isinstance(source_records, list):
                continue
            for metadata in source_records:
                relative = metadata.get("path") if isinstance(metadata, dict) else None
                if isinstance(relative, str) and relative.startswith(SOURCE_FAMILY):
                    indexed_path_references += 1
                    target_paths.add(relative)

    payload_sequence = hashlib.sha256()
    payload_bytes = 0
    payloads_with_evidence = 0
    evidence_objects = 0
    gcide_payloads = 0
    gcide_objects = 0
    gcide_multiplicity: Counter[str] = Counter()
    version_counts: Counter[str] = Counter()
    hash_field_counts: Counter[str] = Counter()

    for relative in sorted(target_paths):
        payload_path = _safe_payload_path(bundle, relative, maximum_source_bytes)
        raw = payload_path.read_bytes()
        digest = _sha256_bytes(raw)
        expected = checksums.get(relative)
        if (
            not isinstance(expected, dict)
            or expected.get("sha256") != digest
            or type(expected.get("bytes")) is not int
            or expected["bytes"] != len(raw)
        ):
            raise ValueError("target source payload differs from frozen checksum sidecar")
        payload_sequence.update(len(raw).to_bytes(8, "big"))
        payload_sequence.update(bytes.fromhex(digest))
        payload_bytes += len(raw)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("target source payload is invalid UTF-8 JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("target source payload is not a JSON object")
        source_record = payload.get("source_record")
        provenance = (
            source_record.get("alternative_definition_provenance")
            if isinstance(source_record, dict) else None
        )
        evidence = provenance.get("source_evidence") if isinstance(provenance, dict) else None
        if not isinstance(evidence, list):
            continue
        payloads_with_evidence += 1
        found_gcide = False
        for item in evidence:
            if not isinstance(item, dict):
                continue
            evidence_objects += 1
            if _normalized_source_label(item.get("source")) != GCIDE_LABEL:
                continue
            found_gcide = True
            gcide_objects += 1
            version = item.get("source_version")
            if version == "0.54":
                version_counts[VERSION_EXPECTED] += 1
            elif version is None:
                version_counts["missing"] += 1
            elif isinstance(version, str):
                version_counts["other_string"] += 1
            else:
                version_counts["non_string"] += 1

            definition_hash = item.get("definition_text_sha256")
            ili = item.get("ili")
            hash_field_counts["definition_hash_present"] += isinstance(definition_hash, str)
            hash_field_counts["definition_hash_sha256_format"] += (
                isinstance(definition_hash, str) and HASH_RE.fullmatch(definition_hash) is not None
            )
            hash_field_counts["ili_present"] += isinstance(ili, str) and bool(ili.strip())
            hash_field_counts["ili_and_definition_hash_present"] += (
                isinstance(ili, str) and bool(ili.strip())
                and isinstance(definition_hash, str) and bool(definition_hash)
            )
        gcide_payloads += int(found_gcide)
        count_in_payload = sum(1 for item in evidence if isinstance(item, dict) and _normalized_source_label(item.get("source")) == GCIDE_LABEL)
        gcide_multiplicity[str(count_in_payload)] += 1

    manifest_path = bundle / "manifest.json"
    lock_path = DEFAULT_INTEGRITY_LOCK
    return {
        "schema_version": "gcide-source-evidence-census/2",
        "scope": "frozen_bundle_source_evidence_profile_only",
        "inputs": {
            "bundle_manifest_sha256": _sha256_file(manifest_path),
            "bundle_integrity_lock_sha256": _sha256_file(lock_path),
            "checksums_sidecar_sha256": checksums_sha256,
            "sense_index_sha256": _sha256_file(index_path),
            "implementation_sha256": _sha256_file(Path(__file__).resolve()),
        },
        "counts": {
            "sense_index_rows": index_rows,
            "indexed_target_path_references": indexed_path_references,
            "unique_target_payload_paths": len(target_paths),
            "verified_target_payloads": len(target_paths),
            "target_payload_bytes": payload_bytes,
            "payloads_with_source_evidence": payloads_with_evidence,
            "all_source_evidence_objects_in_target_family": evidence_objects,
            "payloads_with_gcide_0_54_label": gcide_payloads,
            "gcide_0_54_evidence_objects": gcide_objects,
            "gcide_evidence_objects_per_payload_distribution_among_payloads_with_source_evidence": dict(sorted(gcide_multiplicity.items(), key=lambda item: int(item[0]))),
            "gcide_source_version_categories": dict(sorted(version_counts.items())),
            "gcide_definition_hash_field_counts": dict(sorted(hash_field_counts.items())),
        },
        "upstream_archive_match": False,
        "release_clearance": "not_assessed",
        "interpretation_limit": (
            "Counts and hashes describe the indexed frozen source-record family only. "
            "A GCIDE_0.54 source label or version field is not a byte-level match to the official archive; "
            "this audit does not inspect definition text, validate paragraph subsource tags, trace rules/witnesses, "
            "resolve third-party rights, or authorize redistribution."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, default=configured_bundle_root())
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--maximum-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        report = audit_gcide_source_evidence(
            args.bundle_root,
            maximum_source_bytes=args.maximum_source_bytes,
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        print(json.dumps({
            "schema_version": "gcide-source-evidence-census/2",
            "valid": False,
            "scope": "frozen_bundle_source_evidence_profile_only",
            "release_clearance": "not_assessed",
        }, indent=2))
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "schema_version": report["schema_version"],
        "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "counts": report["counts"],
        "upstream_archive_match": report["upstream_archive_match"],
        "release_clearance": report["release_clearance"],
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
