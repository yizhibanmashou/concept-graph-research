"""Compare frozen GCIDE evidence hashes to text extracted from official GCIDE archive.

This is an exploratory content-identity audit. It reports aggregate match counts
for explicitly named byte/text normalizations and never emits dictionary text,
source paths, local hashes, or sense identifiers. A match is not semantic support
or license clearance.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import tarfile
import unicodedata
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
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
TAG_RE = re.compile(rb"<[^>]*>")
DEF_RE = re.compile(rb"<def(?:\s[^>]*)?>(.*?)</def\s*>", re.IGNORECASE | re.DOTALL)
SOURCE_RE = re.compile(rb"<source(?:\s[^>]*)?>(.*?)</source\s*>", re.IGNORECASE | re.DOTALL)
SPACE_RE = re.compile(r"\s+")
EXPECTED_MD5 = "2fde298eb57af31e885497b81e634e88"
DEFAULT_ARCHIVE = PROJECT_ROOT / "tmp" / "phase126_gcide-0.54.tar.gz"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase126" / "gcide_archive_hash_crosswalk.json"


def _normalized_source_label(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return re.sub(r"\s+", "_", value.strip())


def _canonical_text(value: bytes, encoding: str) -> str | None:
    try:
        text = value.decode(encoding, errors="strict")
    except (UnicodeDecodeError, LookupError):
        return None
    text = html.unescape(text)
    text = unicodedata.normalize("NFC", text)
    return SPACE_RE.sub(" ", text).strip()


def _contains_string_hash(value: Any, target_hash: str) -> bool:
    """Check in-memory payload strings without returning their values."""
    if isinstance(value, str):
        return hashlib.sha256(value.encode("utf-8")).hexdigest() == target_hash
    if isinstance(value, dict):
        return any(_contains_string_hash(child, target_hash) for child in value.values())
    if isinstance(value, list):
        return any(_contains_string_hash(child, target_hash) for child in value)
    return False


def collect_candidate_hashes(bundle: Path, maximum_source_bytes: int) -> tuple[set[str], set[str], dict[str, Any]]:
    bundle = bundle.resolve()
    integrity = verify_frozen_bundle_integrity(bundle)
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity lock did not pass")
    index_path = bundle / "indexes" / "senses.jsonl"
    checksums, checksums_sha256 = _load_checksums(bundle)
    target_paths: set[str] = set()
    with index_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            sources = row.get("source_records") if isinstance(row, dict) else None
            if not isinstance(sources, list):
                continue
            for source in sources:
                relative = source.get("path") if isinstance(source, dict) else None
                if isinstance(relative, str) and relative.startswith(SOURCE_FAMILY):
                    target_paths.add(relative)

    candidate_hashes: set[str] = set()
    nonraw_definition_hashes: set[str] = set()
    evidence_count = 0
    gcide_payloads = 0
    gcide_objects = 0
    gcide_objects_matching_raw_definition = 0
    gcide_objects_matching_source_gloss_level_0 = 0
    gcide_objects_not_matching_raw_definition = 0
    nonraw_hashes_missing_from_payload_strings = 0
    gcide_payloads_with_any_raw_definition_match = 0
    gcide_payloads_all_raw_definition_match = 0
    payload_bytes = 0
    sequence = hashlib.sha256()
    for relative in sorted(target_paths):
        path = _safe_payload_path(bundle, relative, maximum_source_bytes)
        raw = path.read_bytes()
        digest = _sha256_bytes(raw)
        expected = checksums.get(relative)
        if (not isinstance(expected, dict) or expected.get("sha256") != digest
                or type(expected.get("bytes")) is not int or expected["bytes"] != len(raw)):
            raise ValueError("target source payload differs from frozen checksum sidecar")
        sequence.update(len(raw).to_bytes(8, "big")); sequence.update(bytes.fromhex(digest))
        payload_bytes += len(raw)
        payload = json.loads(raw.decode("utf-8"))
        source_record = payload.get("source_record") if isinstance(payload, dict) else None
        provenance = source_record.get("alternative_definition_provenance") if isinstance(source_record, dict) else None
        items = provenance.get("source_evidence") if isinstance(provenance, dict) else None
        if not isinstance(items, list):
            continue
        synset = payload.get("synset") if isinstance(payload.get("synset"), dict) else {}
        raw_definition = synset.get("raw_definition")
        raw_definition_hash = hashlib.sha256(raw_definition.encode("utf-8")).hexdigest() if isinstance(raw_definition, str) else None
        source_gloss_levels = source_record.get("gloss_levels") if isinstance(source_record, dict) else None
        source_gloss_level_0 = source_gloss_levels[0] if isinstance(source_gloss_levels, list) and source_gloss_levels else None
        source_gloss_level_0_hash = hashlib.sha256(source_gloss_level_0.encode("utf-8")).hexdigest() if isinstance(source_gloss_level_0, str) else None
        local_gcide = False
        local_objects = 0
        local_raw_matches = 0
        for item in items:
            if not isinstance(item, dict):
                continue
            if _normalized_source_label(item.get("source")) != GCIDE_LABEL:
                continue
            local_gcide = True
            gcide_objects += 1
            local_objects += 1
            value = item.get("definition_text_sha256")
            if not isinstance(value, str) or HASH_RE.fullmatch(value) is None:
                raise ValueError("GCIDE evidence has an invalid definition_text_sha256")
            value = value.casefold()
            candidate_hashes.add(value)
            if value == raw_definition_hash:
                gcide_objects_matching_raw_definition += 1
                local_raw_matches += 1
            else:
                gcide_objects_not_matching_raw_definition += 1
                nonraw_definition_hashes.add(value)
                if not _contains_string_hash(payload, value):
                    nonraw_hashes_missing_from_payload_strings += 1
            if value == source_gloss_level_0_hash:
                gcide_objects_matching_source_gloss_level_0 += 1
            evidence_count += 1
        gcide_payloads += int(local_gcide)
        if local_gcide:
            gcide_payloads_with_any_raw_definition_match += int(local_raw_matches > 0)
            gcide_payloads_all_raw_definition_match += int(local_raw_matches == local_objects)

    return candidate_hashes, nonraw_definition_hashes, {
        "bundle_manifest_sha256": _sha256_file(bundle / "manifest.json"),
        "bundle_integrity_lock_sha256": _sha256_file(DEFAULT_INTEGRITY_LOCK),
        "checksums_sidecar_sha256": checksums_sha256,
        "sense_index_sha256": _sha256_file(index_path),
        "target_payload_count": len(target_paths),
        "target_payload_bytes": payload_bytes,
        "target_payload_sequence_sha256": sequence.hexdigest(),
        "gcide_payload_count": gcide_payloads,
        "gcide_evidence_object_count": gcide_objects,
        "gcide_distinct_definition_hash_count": len(candidate_hashes),
        "gcide_definition_hash_object_count": evidence_count,
        "gcide_objects_matching_synset_raw_definition_sha256": gcide_objects_matching_raw_definition,
        "gcide_objects_matching_source_record_gloss_levels_0_sha256": gcide_objects_matching_source_gloss_level_0,
        "gcide_objects_not_matching_synset_raw_definition_sha256": gcide_objects_not_matching_raw_definition,
        "distinct_hashes_from_objects_not_matching_raw_definition": len(nonraw_definition_hashes),
        "gcide_payloads_with_any_raw_definition_hash_match": gcide_payloads_with_any_raw_definition_match,
        "gcide_payloads_all_evidence_hashes_match_raw_definition": gcide_payloads_all_raw_definition_match,
        "non_raw_definition_evidence_hashes_absent_from_same_payload_strings": nonraw_hashes_missing_from_payload_strings,
    }


def _source_categories(paragraph: bytes) -> set[str]:
    categories: set[str] = set()
    for raw in SOURCE_RE.findall(paragraph):
        tag = _canonical_text(raw, "utf-8") or _canonical_text(raw, "cp1252") or ""
        folded = tag.casefold()
        if "wordnet" in folded:
            categories.add("wordnet_marker")
        if "1913 webster" in folded or "webster 1913" in folded:
            categories.add("webster_1913_marker")
        if "century" in folded:
            categories.add("century_dictionary_marker")
        if tag.strip():
            categories.add("other_or_unspecified_source_marker")
    if not categories:
        categories.add("no_source_marker_in_matched_paragraph")
    return categories


def match_archive(archive: Path, candidate_hashes: set[str], nonraw_definition_hashes: set[str]) -> dict[str, Any]:
    archive_md5 = hashlib.md5()
    archive_sha256 = hashlib.sha256()
    with archive.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            archive_md5.update(chunk); archive_sha256.update(chunk)
    md5_matches = archive_md5.hexdigest() == EXPECTED_MD5
    if not md5_matches:
        raise ValueError("archive MD5 does not match the pinned official download-page value")

    transforms: dict[str, set[str]] = {
        "raw_def_inner_bytes_sha256": set(),
        "tag_stripped_inner_utf8_html_unescape_nfc_whitespace_sha256": set(),
        "tag_stripped_inner_cp1252_html_unescape_nfc_whitespace_sha256": set(),
    }
    occurrences: Counter[str] = Counter()
    matched_hashes: dict[str, set[str]] = {name: set() for name in transforms}
    matched_subsources: dict[str, Counter[str]] = {name: Counter() for name in transforms}
    nonraw_matched_hashes: dict[str, set[str]] = {name: set() for name in transforms}
    nonraw_match_occurrences: Counter[str] = Counter()
    nonraw_match_subsources: dict[str, Counter[str]] = {name: Counter() for name in transforms}
    def_count = 0
    cide_members = 0
    utf8_decodable_defs = 0
    cp1252_decodable_defs = 0
    tar_members: list[str] = []

    with tarfile.open(archive, mode="r:gz") as tar:
        for member in tar.getmembers():
            name = Path(member.name).name
            if member.isfile() and (name == "README" or name == "COPYING" or re.fullmatch(r"CIDE\.[A-Z]", name)):
                tar_members.append(name)
            if not member.isfile() or not re.fullmatch(r"CIDE\.[A-Z]", name):
                continue
            cide_members += 1
            handle = tar.extractfile(member)
            if handle is None:
                continue
            body = handle.read()
            for match in DEF_RE.finditer(body):
                def_count += 1
                inner = match.group(1)
                paragraph_start = body.rfind(b"<p", 0, match.start())
                paragraph_end = body.find(b"</p", match.end())
                paragraph = body[paragraph_start:paragraph_end + 4] if paragraph_start >= 0 and paragraph_end >= 0 else b""
                source_categories = _source_categories(paragraph)
                transformed: dict[str, bytes | None] = {
                    "raw_def_inner_bytes_sha256": inner,
                    "tag_stripped_inner_utf8_html_unescape_nfc_whitespace_sha256": None,
                    "tag_stripped_inner_cp1252_html_unescape_nfc_whitespace_sha256": None,
                }
                stripped = TAG_RE.sub(b"", inner)
                for encoding, key in (
                    ("utf-8", "tag_stripped_inner_utf8_html_unescape_nfc_whitespace_sha256"),
                    ("cp1252", "tag_stripped_inner_cp1252_html_unescape_nfc_whitespace_sha256"),
                ):
                    canonical = _canonical_text(stripped, encoding)
                    if canonical is not None:
                        transformed[key] = canonical.encode("utf-8")
                        if encoding == "utf-8": utf8_decodable_defs += 1
                        else: cp1252_decodable_defs += 1
                for key, value in transformed.items():
                    if value is None:
                        continue
                    digest = hashlib.sha256(value).hexdigest()
                    if digest in candidate_hashes:
                        matched_hashes[key].add(digest)
                        occurrences[key] += 1
                        for category in source_categories:
                            matched_subsources[key][category] += 1
                    if digest in nonraw_definition_hashes:
                        nonraw_matched_hashes[key].add(digest)
                        nonraw_match_occurrences[key] += 1
                        for category in source_categories:
                            nonraw_match_subsources[key][category] += 1

    if cide_members != 26 or not {"README", "COPYING"}.issubset(set(tar_members)):
        raise ValueError("archive member layout differs from the expected GCIDE 0.54 package")
    return {
        "archive_sha256": archive_sha256.hexdigest(),
        "archive_md5": archive_md5.hexdigest(),
        "archive_md5_matches_official_download_page": md5_matches,
        "archive_bytes": archive.stat().st_size,
        "archive_members": {"cide_letter_files": cide_members, "readme_present": "README" in tar_members, "copying_present": "COPYING" in tar_members},
        "definition_blocks_scanned": def_count,
        "definitions_utf8_decodable": utf8_decodable_defs,
        "definitions_cp1252_decodable": cp1252_decodable_defs,
        "distinct_candidate_hash_count": len(candidate_hashes),
        "nonraw_definition_hash_archive_match": {
            name: {
                "distinct_nonraw_evidence_hashes_matched": len(nonraw_matched_hashes[name]),
                "archive_definition_occurrences_matching": nonraw_match_occurrences[name],
                "matched_paragraph_source_marker_categories": dict(sorted(nonraw_match_subsources[name].items())),
            }
            for name in transforms
        },
        "transforms": {
            name: {
                "distinct_candidate_hashes_matched": len(matched_hashes[name]),
                "candidate_hash_match_rate": len(matched_hashes[name]) / len(candidate_hashes) if candidate_hashes else None,
                "archive_definition_occurrences_matching": occurrences[name],
                "matched_paragraph_source_marker_categories": dict(sorted(matched_subsources[name].items())),
            }
            for name in transforms
        },
        "signature_verified": False,
        "license_clearance": "not_assessed",
        "interpretation_limit": (
            "Hashes were compared under explicitly named extraction/normalization variants; no transformation is asserted to be the frozen producer's canonicalization. "
            "A match supports content correspondence only, not exclusive provenance, sense identity, semantic gloss support, source-span entailment, or license compatibility. "
            "Paragraph markers may be absent or malformed under regex-based boundary recovery; this is not a legal subsource adjudication."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, default=configured_bundle_root())
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--maximum-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        candidate_hashes, nonraw_definition_hashes, inputs = collect_candidate_hashes(args.bundle_root, args.maximum_source_bytes)
        archive_result = match_archive(args.archive, candidate_hashes, nonraw_definition_hashes)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, tarfile.TarError):
        print(json.dumps({"schema_version":"gcide-archive-hash-crosswalk/2","valid":False,"license_clearance":"not_assessed"},indent=2))
        return 1
    report = {
        "schema_version": "gcide-archive-hash-crosswalk/2",
        "scope": "frozen_gcide_definition_hashes_vs_official_archive_text_variants",
        "inputs": {**inputs, "archive_sha256": archive_result["archive_sha256"], "implementation_sha256": _sha256_file(Path(__file__).resolve())},
        "archive_scan": archive_result,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"schema_version":report["schema_version"],"output_sha256":_sha256_file(args.output),"archive_scan":archive_result},ensure_ascii=False,indent=2,sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
