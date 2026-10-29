"""Build a path-, gloss-, and identity-free source candidate triage report.

The audit is intentionally limited to alternative/definition-WSD source records
and their ``source_record.alternative_definition_provenance.source_evidence``.
It verifies payload bytes against the frozen checksum sidecar and summarizes
only allow-listed provenance labels and download hosts. It does not assess
license compatibility or grant release clearance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from src.analysis.audit_source_release_metadata import (
    DEFAULT_MAX_SOURCE_BYTES,
    _load_checksums,
    _safe_payload_path,
    _sha256_bytes,
    _sha256_file,
    _source_family,
)
from src.analysis.frozen_bundle_integrity import verify_frozen_bundle_integrity
from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase24" / "source_release_candidate_triage.json"
SOURCE_FAMILY = "sources/Synset/alternative_or_definition_wsd_frozen"
SAFE_LABEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:+-]{0,79}$")
CONTENT_HASH = re.compile(r"(?i)^(?:raw-)?sha(?:1|256|512)[:_-]?[0-9a-f]{32,128}$")
PROFILE_FIELDS = ("source", "source_version", "source_ontology", "evidence_type")


def _label(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return "missing"
    normalized = re.sub(r"\s+", "_", value.strip())
    if CONTENT_HASH.fullmatch(normalized):
        return "content_hash_value"
    return normalized if SAFE_LABEL.fullmatch(normalized) else "noncanonical_or_nonscalar"


def _value_shape(value: Any) -> str:
    """Return a fixed structural category without exposing a metadata value."""
    if value is None:
        return "missing_or_null"
    if isinstance(value, str):
        if not value.strip():
            return "blank_string"
        normalized = re.sub(r"\s+", "_", value.strip())
        if CONTENT_HASH.fullmatch(normalized):
            return "content_hash_string"
        if SAFE_LABEL.fullmatch(normalized):
            return "canonical_label_string"
        return "noncanonical_string"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, (int, float)):
        return "number"
    return "other_type"


def _download_host(value: Any) -> str:
    if value is None:
        return "missing"
    if not isinstance(value, str):
        return "noncanonical_or_nonscalar"
    try:
        parsed = urlsplit(value.strip())
        host = parsed.hostname
        if parsed.scheme.casefold() not in {"http", "https"} or not host or parsed.username or parsed.password:
            return "noncanonical_or_nonscalar"
        normalized = host.encode("idna").decode("ascii").casefold()
    except (UnicodeError, ValueError):
        return "noncanonical_or_nonscalar"
    return normalized if SAFE_LABEL.fullmatch(normalized) else "noncanonical_or_nonscalar"


def _source_value_host(value: Any) -> str:
    """Extract a host only when a source string is an explicit safe URL."""
    if not isinstance(value, str):
        return "non_string_source_value"
    try:
        parsed = urlsplit(value.strip())
        host = parsed.hostname
        if parsed.scheme.casefold() not in {"http", "https", "ftp"} or not host or parsed.username or parsed.password:
            return "no_safe_url_host"
        normalized = host.encode("idna").decode("ascii").casefold()
    except (UnicodeError, ValueError):
        return "no_safe_url_host"
    return normalized if SAFE_LABEL.fullmatch(normalized) else "no_safe_url_host"


def audit_source_release_candidates(
    bundle: Path,
    *,
    maximum_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
    progress_every: int = 1000,
) -> dict[str, Any]:
    """Verify and aggregate candidate provenance for one source-record family."""
    bundle = bundle.resolve()
    integrity = verify_frozen_bundle_integrity(bundle)
    if not integrity["valid"]:
        raise ValueError("frozen bundle integrity lock failed: " + ", ".join(integrity["errors"]))
    index_path = bundle / "indexes" / "senses.jsonl"
    if not index_path.is_file():
        raise ValueError("sense index is missing")
    checksums, checksums_sha256 = _load_checksums(bundle)
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))

    seen: set[str] = set()
    profile_payload_counts: Counter[tuple[str, ...]] = Counter()
    dimension_counts: dict[str, Counter[str]] = {
        name: Counter() for name in (*PROFILE_FIELDS, "download_host", "source_value_host")
    }
    metadata_value_shape_counts: dict[str, Counter[str]] = {
        name: Counter() for name in (*PROFILE_FIELDS, "download_url")
    }
    source_shape_evidence_counts: Counter[tuple[str, str]] = Counter()
    source_shape_payload_counts: Counter[tuple[str, str]] = Counter()
    source_value_host_evidence_counts: Counter[tuple[str, str]] = Counter()
    source_value_host_payload_counts: Counter[tuple[str, str]] = Counter()
    indexed = verified = payloads_with_evidence = evidence_objects = malformed_evidence = 0
    payloads_with_version = payloads_with_download_url = 0
    evidence_with_version = evidence_with_download_url = 0
    payload_bytes = 0
    sequence_digest = hashlib.sha256()

    with index_path.open("rb") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            if not raw_line.strip():
                continue
            try:
                row = json.loads(raw_line)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid sense-index JSON at line {line_number}") from exc
            if not isinstance(row, dict) or not isinstance(row.get("source_records"), list):
                continue
            for metadata in row["source_records"]:
                relative = metadata.get("path") if isinstance(metadata, dict) else None
                if not isinstance(relative, str) or _source_family(relative) != SOURCE_FAMILY:
                    continue
                indexed += 1
                if relative in seen:
                    continue
                seen.add(relative)
                path = _safe_payload_path(bundle, relative, maximum_source_bytes)
                raw = path.read_bytes()
                digest = _sha256_bytes(raw)
                checksum = checksums.get(relative)
                if (not isinstance(checksum, dict)
                        or checksum.get("sha256") != digest
                        or type(checksum.get("bytes")) is not int
                        or checksum["bytes"] != len(raw)):
                    raise ValueError("source-record payload differs from frozen checksums.jsonl")
                try:
                    payload = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError("source-record payload is not valid UTF-8 JSON") from exc
                if not isinstance(payload, dict):
                    raise ValueError("source-record payload is not a JSON object")

                verified += 1
                payload_bytes += len(raw)
                sequence_digest.update(len(raw).to_bytes(8, "big"))
                sequence_digest.update(bytes.fromhex(digest))
                source_record = payload.get("source_record")
                provenance = source_record.get("alternative_definition_provenance") if isinstance(source_record, dict) else None
                evidence = provenance.get("source_evidence") if isinstance(provenance, dict) else None
                if isinstance(evidence, list) and evidence:
                    payloads_with_evidence += 1
                    payload_profiles: set[tuple[str, ...]] = set()
                    payload_source_shapes: set[tuple[str, str]] = set()
                    payload_source_value_hosts: set[tuple[str, str]] = set()
                    has_version = has_download_url = False
                    for item in evidence:
                        if not isinstance(item, dict):
                            malformed_evidence += 1
                            continue
                        evidence_objects += 1
                        labels = {name: _label(item.get(name)) for name in PROFILE_FIELDS}
                        host = _download_host(item.get("download_url"))
                        source_shape = _value_shape(item.get("source"))
                        payload_source_shapes.add((labels["source"], source_shape))
                        source_shape_evidence_counts[(labels["source"], source_shape)] += 1
                        source_value_host = _source_value_host(item.get("source"))
                        payload_source_value_hosts.add((labels["source"], source_value_host))
                        source_value_host_evidence_counts[(labels["source"], source_value_host)] += 1
                        for name in PROFILE_FIELDS:
                            metadata_value_shape_counts[name][_value_shape(item.get(name))] += 1
                        metadata_value_shape_counts["download_url"][_value_shape(item.get("download_url"))] += 1
                        profile = tuple(labels[name] for name in PROFILE_FIELDS) + (host, source_value_host)
                        payload_profiles.add(profile)
                        for name, value in labels.items():
                            dimension_counts[name][value] += 1
                        dimension_counts["download_host"][host] += 1
                        dimension_counts["source_value_host"][source_value_host] += 1
                        has_version |= item.get("source_version") is not None
                        has_download_url |= item.get("download_url") is not None
                        evidence_with_version += item.get("source_version") is not None
                        evidence_with_download_url += item.get("download_url") is not None
                    profile_payload_counts.update(payload_profiles)
                    source_shape_payload_counts.update(payload_source_shapes)
                    source_value_host_payload_counts.update(payload_source_value_hosts)
                    payloads_with_version += has_version
                    payloads_with_download_url += has_download_url

                if progress_every > 0 and verified % progress_every == 0:
                    print(f"Verified {verified} source payloads in the selected family", flush=True)

    profiles = [
        {
            **dict(zip((*PROFILE_FIELDS, "download_host", "source_value_host"), values, strict=True)),
            "payload_count": count,
        }
        for values, count in sorted(profile_payload_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    return {
        "audit_version": "source-release-candidate-triage/3",
        "bundle_integrity_lock_valid": integrity["valid"],
        "bundle_semantic_fingerprint_sha256": manifest.get("semantic_fingerprint_sha256"),
        "audit_implementation_sha256": _sha256_file(Path(__file__).resolve()),
        "sense_index_sha256": _sha256_file(index_path),
        "checksums_sha256": checksums_sha256,
        "source_payload_sequence_sha256": sequence_digest.hexdigest(),
        "scope": {
            "source_family": "alternative_or_definition_wsd_frozen",
            "indexed_references": indexed,
            "unique_payloads_verified": verified,
            "payload_bytes": payload_bytes,
        },
        "counts": {
            "payloads_with_source_evidence": payloads_with_evidence,
            "evidence_objects": evidence_objects,
            "malformed_evidence_objects": malformed_evidence,
            "payloads_with_source_version": payloads_with_version,
            "evidence_objects_with_source_version": evidence_with_version,
            "payloads_with_download_url": payloads_with_download_url,
            "evidence_objects_with_download_url": evidence_with_download_url,
            "unique_candidate_profiles": len(profiles),
            "license_clearance": "not_assessed; source-level rights and license compatibility require human review",
        },
        "evidence_dimension_counts": {
            name: dict(sorted(counter.items())) for name, counter in sorted(dimension_counts.items())
        },
        "metadata_value_shape_counts": {
            name: dict(sorted(counter.items()))
            for name, counter in sorted(metadata_value_shape_counts.items())
        },
        "source_label_value_shape_counts": [
            {
                "source_label_category": label_category,
                "value_shape": value_shape,
                "evidence_object_count": source_shape_evidence_counts[(label_category, value_shape)],
                "payload_count": source_shape_payload_counts[(label_category, value_shape)],
            }
            for label_category, value_shape in sorted(source_shape_evidence_counts)
        ],
        "source_label_value_host_counts": [
            {
                "source_label_category": label_category,
                "host_category": host_category,
                "evidence_object_count": source_value_host_evidence_counts[(label_category, host_category)],
                "payload_count": source_value_host_payload_counts[(label_category, host_category)],
            }
            for label_category, host_category in sorted(source_value_host_evidence_counts)
        ],
        "candidate_profiles": profiles,
        "raw_gloss_ids_paths_and_full_urls_emitted": False,
        "interpretation_limit": (
            "Profiles are discovery aids for one source family only. Labels, source-value hosts, and download hosts do not establish a unique upstream release, "
            "license, attribution, legal compatibility, or public-release clearance. Full URLs, local paths, text, and identities are omitted."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=configured_bundle_root())
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--max-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--progress-every", type=int, default=1000)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error(f"output exists; pass --force to replace: {output}")
    try:
        report = audit_source_release_candidates(
            args.bundle,
            maximum_source_bytes=args.max_source_bytes,
            progress_every=args.progress_every,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), **report["scope"], **report["counts"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
