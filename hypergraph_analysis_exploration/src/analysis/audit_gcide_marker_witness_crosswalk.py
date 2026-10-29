"""Crosswalk normalized GCIDE archive markers with selected-witness gloss hashes.

Only aggregate counts and input fingerprints are emitted. Gloss text, identities,
source paths, rule text, and definition hashes remain in memory and are never
serialized. This is a provenance audit, not a semantic-support evaluation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.analysis.audit_gcide_source_evidence import GCIDE_LABEL, SOURCE_FAMILY, _normalized_source_label
from src.analysis.audit_source_release_metadata import (
    DEFAULT_MAX_SOURCE_BYTES,
    _load_checksums,
    _safe_payload_path,
    _sha256_bytes,
    _sha256_file,
)
from src.analysis.frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK, verify_frozen_bundle_integrity
from src.analysis.match_gcide_evidence_hashes import (
    DEF_RE,
    EXPECTED_MD5,
    TAG_RE,
    _canonical_text,
    _source_categories,
)
from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root

DEFAULT_ARCHIVE = PROJECT_ROOT / "tmp" / "phase126_gcide-0.54.tar.gz"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase128" / "gcide_marker_witness_crosswalk.json"
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _load_gcide_payloads(bundle: Path, maximum_source_bytes: int) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    index_path = bundle / "indexes" / "senses.jsonl"
    checksums, checksums_sha256 = _load_checksums(bundle)
    target_paths: set[str] = set()
    with index_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            records = row.get("source_records") if isinstance(row, dict) else None
            if not isinstance(records, list):
                continue
            for record in records:
                relative = record.get("path") if isinstance(record, dict) else None
                if isinstance(relative, str) and relative.startswith(SOURCE_FAMILY):
                    target_paths.add(relative)

    payload_sequence = hashlib.sha256()
    payload_bytes = 0
    gcide: dict[str, dict[str, Any]] = {}
    evidence_count = 0
    hash_raw_definition_matches = 0
    nonraw_evidence_objects = 0
    for relative in sorted(target_paths):
        path = _safe_payload_path(bundle, relative, maximum_source_bytes)
        raw = path.read_bytes()
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
        payload = json.loads(raw.decode("utf-8"))
        source_record = payload.get("source_record") if isinstance(payload, dict) else None
        provenance = source_record.get("alternative_definition_provenance") if isinstance(source_record, dict) else None
        evidence = provenance.get("source_evidence") if isinstance(provenance, dict) else None
        if not isinstance(evidence, list):
            continue
        items = [
            item for item in evidence
            if isinstance(item, dict) and _normalized_source_label(item.get("source")) == GCIDE_LABEL
        ]
        if not items:
            continue
        synset = payload.get("synset") if isinstance(payload.get("synset"), dict) else {}
        raw_definition = synset.get("raw_definition")
        if not isinstance(raw_definition, str):
            raise ValueError("GCIDE payload is missing synset.raw_definition")
        raw_hash = hashlib.sha256(raw_definition.encode("utf-8")).hexdigest()
        evidence_hashes: set[str] = set()
        for item in items:
            value = item.get("definition_text_sha256")
            if not isinstance(value, str) or HASH_RE.fullmatch(value) is None:
                raise ValueError("GCIDE evidence has an invalid definition_text_sha256")
            value = value.casefold()
            evidence_hashes.add(value)
            evidence_count += 1
            if value == raw_hash:
                hash_raw_definition_matches += 1
            else:
                nonraw_evidence_objects += 1
        if raw_hash is not None:
            gcide[relative] = {
                "raw_definition_hash": raw_hash,
                "evidence_hashes": evidence_hashes,
                "synset_id": payload.get("synset_id"),
                "sense_id": payload.get("sense_id"),
            }

    return gcide, {
        "checksums_sidecar_sha256": checksums_sha256,
        "sense_index_sha256": _sha256_file(index_path),
        "target_payload_count": len(target_paths),
        "target_payload_bytes": payload_bytes,
        "target_payload_sequence_sha256": payload_sequence.hexdigest(),
        "gcide_payload_count": len(gcide),
        "gcide_evidence_object_count": evidence_count,
        "gcide_evidence_objects_hash_equal_to_raw_definition_utf8": hash_raw_definition_matches,
        "gcide_evidence_objects_hash_not_equal_to_raw_definition_utf8": nonraw_evidence_objects,
    }


def _selected_witness_payload_paths(bundle: Path, gcide: dict[str, dict[str, Any]]) -> tuple[set[str], dict[str, str]]:
    index_path = bundle / "indexes" / "senses.jsonl"
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    hyperedges_path = bundle / "graph" / "hyperedges.jsonl"
    witnesses_path = bundle / "graph" / "coverage_witnesses.jsonl"
    candidate_heads = {x.get("synset_id") for x in gcide.values() if isinstance(x.get("synset_id"), str)}

    rows_by_path: dict[str, dict[str, Any]] = {}
    refs: Counter[str] = Counter()
    with index_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            records = row.get("source_records") if isinstance(row, dict) else None
            if not isinstance(records, list):
                continue
            for record in records:
                relative = record.get("path") if isinstance(record, dict) else None
                if relative in gcide:
                    refs[relative] += 1
                    rows_by_path[relative] = row
    if any(refs[p] != 1 for p in gcide):
        raise ValueError("GCIDE payload is missing or duplicated in the sense index")

    rules: dict[str, dict[str, Any]] = {}
    with rules_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            if not isinstance(row, dict):
                raise ValueError("hypergraph rule record is malformed")
            if row.get("head") in candidate_heads:
                if row["head"] in rules:
                    raise ValueError("candidate graph head is duplicated")
                rules[row["head"]] = row
    hyperedges: dict[tuple[str, int], list[Any]] = {}
    with hyperedges_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            if not isinstance(row, dict):
                raise ValueError("hyperedge record is malformed")
            head, clause_index, dependencies = row.get("head"), row.get("clause_index"), row.get("dependencies")
            if head in candidate_heads and isinstance(head, str) and type(clause_index) is int and isinstance(dependencies, list):
                key = (head, clause_index)
                if key in hyperedges:
                    raise ValueError("candidate hyperedge head/clause index is duplicated")
                hyperedges[key] = dependencies
    witnesses: dict[str, dict[str, Any]] = {}
    with witnesses_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            head = row.get("head") if isinstance(row, dict) else None
            if head in candidate_heads:
                if head in witnesses:
                    raise ValueError("candidate selected-witness head is duplicated")
                witnesses[head] = row

    selected_paths: set[str] = set()
    for relative, info in gcide.items():
        row = rows_by_path[relative]
        head = info.get("synset_id")
        if row.get("identity") != head or info.get("sense_id") != row.get("identity"):
            raise ValueError("GCIDE payload identity differs from its sense-index identity")
        rule = rules.get(head) if isinstance(head, str) else None
        witness = witnesses.get(head) if isinstance(head, str) else None
        if rule is None or witness is None:
            raise ValueError("GCIDE graph head or selected witness is missing")
        clauses = rule.get("clauses")
        witness_clause = witness.get("witness_clause")
        selected_indices = [i for i, clause in enumerate(clauses) if clause == witness_clause] if isinstance(clauses, list) and isinstance(witness_clause, list) else []
        if witness.get("is_seed") is not True and not selected_indices:
            raise ValueError("non-seed selected witness does not match a graph rule clause")
        if witness.get("is_seed") is not True and any(hyperedges.get((head, i)) != clauses[i] for i in selected_indices):
            raise ValueError("selected witness clause does not match a graph hyperedge")
        entries = row.get("active_clause_sources", [])
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("clause_index") not in selected_indices:
                continue
            documents = entry.get("source_documents")
            if isinstance(documents, list) and relative in documents:
                selected_paths.add(relative)
    return selected_paths, {
        "rules_sha256": _sha256_file(rules_path),
        "hyperedges_sha256": _sha256_file(hyperedges_path),
        "witnesses_sha256": _sha256_file(witnesses_path),
    }


def _archive_marker_crosswalk(archive: Path, candidate_hashes: set[str]) -> dict[str, Any]:
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    with archive.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            md5.update(chunk)
            sha256.update(chunk)
    if md5.hexdigest() != EXPECTED_MD5:
        raise ValueError("archive MD5 does not match the official download-page value")

    matched: set[str] = set()
    marker_hashes: dict[str, set[str]] = defaultdict(set)
    occurrence_markers: Counter[str] = Counter()
    occurrence_count = 0
    definitions_scanned = 0
    with tarfile.open(archive, mode="r:gz") as tar:
        cide_members = [m for m in tar.getmembers() if m.isfile() and re.fullmatch(r"CIDE\.[A-Z]", Path(m.name).name)]
        if len(cide_members) != 26:
            raise ValueError("archive member count differs from the expected GCIDE 0.54 package")
        for member in cide_members:
            handle = tar.extractfile(member)
            if handle is None:
                continue
            body = handle.read()
            for match in DEF_RE.finditer(body):
                definitions_scanned += 1
                inner = match.group(1)
                stripped = TAG_RE.sub(b"", inner)
                canonical = _canonical_text(stripped, "utf-8")
                if canonical is None:
                    continue
                digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
                if digest not in candidate_hashes:
                    continue
                matched.add(digest)
                occurrence_count += 1
                start = body.rfind(b"<p", 0, match.start())
                end = body.find(b"</p", match.end())
                paragraph = body[start:end + 4] if start >= 0 and end >= 0 else b""
                categories = _source_categories(paragraph)
                marker_hashes[digest].update(categories)
                for category in categories:
                    occurrence_markers[category] += 1
    return {
        "archive_sha256": sha256.hexdigest(),
        "archive_md5": md5.hexdigest(),
        "definitions_scanned": definitions_scanned,
        "matched_candidate_hashes": matched,
        "marker_hashes": marker_hashes,
        "matched_definition_occurrences": occurrence_count,
        "matched_occurrence_marker_counts": occurrence_markers,
    }


def audit_gcide_marker_witness_crosswalk(bundle: Path, archive: Path, maximum_source_bytes: int) -> dict[str, Any]:
    bundle = bundle.resolve()
    archive = archive.resolve()
    integrity = verify_frozen_bundle_integrity(bundle)
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity lock did not pass")
    gcide, payload_inputs = _load_gcide_payloads(bundle, maximum_source_bytes)
    selected_paths, graph_inputs = _selected_witness_payload_paths(bundle, gcide)
    selected_hashes = {gcide[path]["raw_definition_hash"] for path in selected_paths}
    archive_result = _archive_marker_crosswalk(archive, selected_hashes)
    matched_hashes = archive_result["matched_candidate_hashes"]
    marker_hashes = archive_result["marker_hashes"]

    matched_paths = {p for p in selected_paths if gcide[p]["raw_definition_hash"] in matched_hashes}
    wordnet_hashes = {h for h, cats in marker_hashes.items() if "wordnet_marker" in cats}
    webster_hashes = {h for h, cats in marker_hashes.items() if "webster_1913_marker" in cats}
    century_hashes = {h for h, cats in marker_hashes.items() if "century_dictionary_marker" in cats}
    no_marker_hashes = {h for h, cats in marker_hashes.items() if "no_source_marker_in_matched_paragraph" in cats}
    recovered_marker_hashes = {
        h for h, cats in marker_hashes.items()
        if "other_or_unspecified_source_marker" in cats
    }
    return {
        "schema_version": "gcide-marker-witness-crosswalk/1",
        "scope": "selected_witness_gcide_gloss_hashes_vs_normalized_archive_definition_markers",
        "inputs": {
            "bundle_manifest_sha256": _sha256_file(bundle / "manifest.json"),
            "bundle_integrity_lock_sha256": _sha256_file(DEFAULT_INTEGRITY_LOCK),
            **payload_inputs,
            **graph_inputs,
            "selected_witness_gcide_payload_count": len(selected_paths),
            "selected_witness_distinct_raw_gloss_hash_count": len(selected_hashes),
            "archive_sha256": archive_result["archive_sha256"],
            "archive_md5": archive_result["archive_md5"],
            "archive_md5_matches_official_download_page": True,
            "archive_definition_blocks_scanned": archive_result["definitions_scanned"],
        },
        "counts": {
            "selected_witness_payloads_with_normalized_archive_hash_match": len(matched_paths),
            "selected_witness_payloads_without_normalized_archive_hash_match": len(selected_paths) - len(matched_paths),
            "selected_witness_distinct_gloss_hashes_with_archive_match": len(matched_hashes),
            "matched_archive_definition_occurrences_for_selected_hashes": archive_result["matched_definition_occurrences"],
            "selected_witness_payloads_with_wordnet_marker_match": sum(gcide[p]["raw_definition_hash"] in wordnet_hashes for p in selected_paths),
            "selected_witness_payloads_with_webster_1913_marker_match": sum(gcide[p]["raw_definition_hash"] in webster_hashes for p in selected_paths),
            "selected_witness_payloads_with_century_marker_match": sum(gcide[p]["raw_definition_hash"] in century_hashes for p in selected_paths),
            "selected_witness_payloads_with_no_marker_match": sum(gcide[p]["raw_definition_hash"] in no_marker_hashes for p in selected_paths),
            "selected_witness_payloads_with_recovered_source_marker_match": sum(gcide[p]["raw_definition_hash"] in recovered_marker_hashes for p in selected_paths),
            "matched_archive_occurrence_marker_counts": dict(sorted(archive_result["matched_occurrence_marker_counts"].items())),
        },
        "interpretation_limit": (
            "A normalized hash match links a frozen selected-witness payload's raw gloss string to one or more archive <def> blocks. "
            "Source-marker categories are recovered from enclosing paragraphs by regex and may overlap; a hash may occur in paragraphs with different markers. "
            "This does not prove exclusive authorship, source-span support for a graph literal, sense identity, legal compatibility, or redistribution rights. "
            "The archive detached signature remains unverified."
        ),
        "raw_text_ids_paths_rule_text_or_hashes_emitted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, default=configured_bundle_root())
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--maximum-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error("output exists; pass --force to replace it")
    try:
        report = audit_gcide_marker_witness_crosswalk(args.bundle_root, args.archive, args.maximum_source_bytes)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, tarfile.TarError):
        print(json.dumps({"schema_version": "gcide-marker-witness-crosswalk/1", "valid": False}, indent=2))
        return 1
    report["implementation_sha256"] = _sha256_file(Path(__file__).resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"schema_version": report["schema_version"], "counts": report["counts"], "output_sha256": _sha256_file(output)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
