"""Cross-check the six OEWN 2025+ source-profile payloads against the pinned ZIP.

The audit emits only aggregate counts and artifact hashes. It never emits
glosses, local paths, sense identifiers, or source identifiers, and it does
not assess license compatibility or authorize redistribution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.audit_source_release_metadata import _load_checksums, _safe_payload_path, _sha256_file
from src.analysis.frozen_bundle_integrity import verify_frozen_bundle_integrity
from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_BUNDLE = configured_bundle_root()
DEFAULT_ARCHIVE = PROJECT_ROOT / "tmp" / "oewn-2025-plus-json.zip"
DEFAULT_TRIAGE = PROJECT_ROOT / "outputs" / "phase24" / "source_release_candidate_triage.json"
DEFAULT_INVENTORY = PROJECT_ROOT / "sources" / "data_release_inventory.json"
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase88" / "oewn_2025_plus_payload_release_match.json"
SOURCE_LABEL = "Open English WordNet 2025+"
SOURCE_VERSION = "2025+"
SOURCE_FAMILY = "sources/Synset/alternative_or_definition_wsd_frozen/"


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label} JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def audit_oewn_2025_plus_payload_matches(
    bundle: Path, archive: Path, triage_path: Path, inventory_path: Path
) -> dict[str, Any]:
    bundle = bundle.resolve()
    archive = archive.resolve()
    triage_path = triage_path.resolve()
    inventory_path = inventory_path.resolve()

    integrity = verify_frozen_bundle_integrity(bundle)
    if not integrity["valid"]:
        raise ValueError("frozen bundle integrity lock failed")
    triage = _load_object(triage_path, "source candidate triage")
    inventory = _load_object(inventory_path, "data release inventory")
    profile_count = sum(
        row.get("payload_count", 0)
        for row in triage.get("candidate_profiles", [])
        if isinstance(row, dict)
        and row.get("source") == "Open_English_WordNet_2025+"
        and row.get("source_version") == SOURCE_VERSION
    )
    if profile_count != 6:
        raise ValueError("expected six OEWN 2025+ candidate-profile payloads")

    resource = next(
        (row for row in inventory.get("upstream_resources", [])
         if isinstance(row, dict) and row.get("resource_id") == "oewn_2025_plus_json"),
        None,
    )
    if not isinstance(resource, dict):
        raise ValueError("release inventory has no OEWN 2025+ resource")
    archive_sha256 = _sha256_file(archive)
    if archive_sha256 != resource.get("local_archive_sha256"):
        raise ValueError("local OEWN archive differs from the pinned inventory digest")

    checksums, checksums_sha256 = _load_checksums(bundle)
    manifest_path = bundle / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("frozen bundle manifest is missing")
    index_path = bundle / "indexes" / "senses.jsonl"
    if not index_path.is_file():
        raise ValueError("frozen sense index is missing")
    candidate_by_path: dict[str, set[tuple[str, str]]] = {}
    seen: set[str] = set()
    with index_path.open("rb") as index_stream:
        for raw_line in index_stream:
            if not raw_line.strip():
                continue
            try:
                row = json.loads(raw_line)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("frozen sense index contains invalid JSON") from exc
            if not isinstance(row, dict) or not isinstance(row.get("source_records"), list):
                continue
            for metadata in row["source_records"]:
                relative = metadata.get("path") if isinstance(metadata, dict) else None
                if not isinstance(relative, str) or not relative.startswith(SOURCE_FAMILY) or relative in seen:
                    continue
                seen.add(relative)
                payload_path = _safe_payload_path(bundle, relative, 16 * 1024 * 1024)
                raw_payload = payload_path.read_bytes()
                digest = hashlib.sha256(raw_payload).hexdigest()
                expected = checksums.get(relative)
                if (not isinstance(expected, dict) or expected.get("sha256") != digest
                        or expected.get("bytes") != len(raw_payload)):
                    raise ValueError("source payload differs from frozen checksum sidecar")
                try:
                    payload = json.loads(raw_payload.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError("source payload is not valid UTF-8 JSON") from exc
                source_record = payload.get("source_record") if isinstance(payload, dict) else None
                provenance = source_record.get("alternative_definition_provenance") if isinstance(source_record, dict) else None
                evidence = provenance.get("source_evidence") if isinstance(provenance, dict) else None
                if not isinstance(evidence, list):
                    continue
                for item in evidence:
                    if (isinstance(item, dict) and item.get("source") == SOURCE_LABEL
                            and item.get("source_version") == SOURCE_VERSION):
                        ili = item.get("ili")
                        definition_hash = item.get("definition_text_sha256")
                        if not isinstance(ili, str) or not isinstance(definition_hash, str):
                            raise ValueError("OEWN source evidence is missing an ILI or definition hash")
                        candidate_by_path.setdefault(relative, set()).add((ili, definition_hash))

    candidate_pairs = [pair for pairs in candidate_by_path.values() for pair in pairs]
    if len(candidate_by_path) != 6 or len(candidate_pairs) != 6:
        raise ValueError("OEWN candidate payload/evidence count differs from six")

    release_pair_counts: Counter[tuple[str, str]] = Counter()
    json_member_count = 0
    with zipfile.ZipFile(archive) as zipped:
        for member in zipped.namelist():
            if not member.lower().endswith(".json"):
                continue
            json_member_count += 1
            try:
                document = json.loads(zipped.read(member))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("OEWN archive contains an invalid JSON member") from exc
            if not isinstance(document, dict):
                continue
            for synset in document.values():
                if not isinstance(synset, dict):
                    continue
                ili = synset.get("ili")
                definitions = synset.get("definition", [])
                if isinstance(definitions, str):
                    definitions = [definitions]
                if not isinstance(definitions, list):
                    continue
                for definition in definitions:
                    texts = [definition] if isinstance(definition, str) else (
                        list(definition.values()) if isinstance(definition, dict) else []
                    )
                    for text in texts:
                        if isinstance(ili, str) and isinstance(text, str):
                            release_pair_counts[(ili, _hash_text(text))] += 1

    multiplicities = [release_pair_counts[pair] for pair in candidate_pairs]
    exact_unique_matches = sum(count == 1 for count in multiplicities)
    return {
        "audit_version": "oewn-2025-plus-payload-match/1",
        "inputs": {
            "bundle_manifest_sha256": _sha256_file(manifest_path),
            "checksums_sha256": checksums_sha256,
            "sense_index_sha256": _sha256_file(index_path),
            "triage_sha256": _sha256_file(triage_path),
            "inventory_sha256": _sha256_file(inventory_path),
            "archive_sha256": archive_sha256,
            "implementation_sha256": _sha256_file(Path(__file__).resolve()),
        },
        "scope": {
            "candidate_payloads": len(candidate_by_path),
            "candidate_evidence_pairs": len(candidate_pairs),
            "release_json_members": json_member_count,
            "pairs_found_in_release": sum(count > 0 for count in multiplicities),
            "pairs_uniquely_found_in_release": exact_unique_matches,
            "candidate_pairs_per_release_record": multiplicities,
        },
        "release_clearance": "not_assessed",
        "interpretation_limit": (
            "Each local source-evidence ILI and definition-text SHA-256 pair was matched to exactly one JSON synset row "
            "in the locally pinned archive. This binds these six evidence records to archive content at the compared "
            "fields only; it does not establish graph-rule lineage, resolve all bundle sources, assess license "
            "compatibility, or authorize redistribution."
        ),
        "raw_text_ids_paths_and_full_urls_emitted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--triage", type=Path, default=DEFAULT_TRIAGE)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error("output exists; pass --force to replace")
    try:
        report = audit_oewn_2025_plus_payload_matches(args.bundle, args.archive, args.triage, args.inventory)
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), **report["scope"], "release_clearance": "not_assessed"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
