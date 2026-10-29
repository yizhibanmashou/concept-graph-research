"""Trace the six OEWN 2025+ provenance payloads into frozen graph objects.

Only aggregate counts and input hashes are emitted. The audit reads local
source payloads but does not output glosses, identities, paths, or rule text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

from src.analysis.audit_source_release_metadata import (
    _load_checksums,
    _safe_payload_path,
    _sha256_file,
)
from src.analysis.frozen_bundle_integrity import verify_frozen_bundle_integrity
from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_BUNDLE = configured_bundle_root()
DEFAULT_RELEASE_MATCH = PROJECT_ROOT / "outputs" / "phase88" / "oewn_2025_plus_payload_release_match.json"
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase89" / "oewn_2025_plus_graph_lineage.json"
SOURCE_FAMILY = "sources/Synset/alternative_or_definition_wsd_frozen/"
SOURCE_LABEL = "Open English WordNet 2025+"
SOURCE_VERSION = "2025+"
MAX_SOURCE_BYTES = 16 * 1024 * 1024


def _string_values(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from _string_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _string_values(child)
    elif isinstance(value, str):
        yield value


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label} JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def audit_oewn_2025_plus_graph_lineage(bundle: Path, release_match_path: Path) -> dict[str, Any]:
    bundle = bundle.resolve()
    release_match_path = release_match_path.resolve()
    integrity = verify_frozen_bundle_integrity(bundle)
    if not integrity["valid"]:
        raise ValueError("frozen bundle integrity lock failed")
    release_match = _load_object(release_match_path, "OEWN release-match report")
    release_scope = release_match.get("scope", {})
    if (release_match.get("audit_version") != "oewn-2025-plus-payload-match/1"
            or release_scope.get("candidate_payloads") != 6
            or release_scope.get("pairs_uniquely_found_in_release") != 6):
        raise ValueError("the Phase 88 report does not certify six unique archive record matches")

    checksums, checksums_sha256 = _load_checksums(bundle)
    index_path = bundle / "indexes" / "senses.jsonl"
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    hyperedges_path = bundle / "graph" / "hyperedges.jsonl"
    witnesses_path = bundle / "graph" / "coverage_witnesses.jsonl"
    for path in (index_path, rules_path, hyperedges_path, witnesses_path):
        if not path.is_file():
            raise ValueError("a required frozen graph/index file is missing")

    candidates: dict[str, dict[str, Any]] = {}
    seen_source_paths: set[str] = set()
    with index_path.open("rb") as stream:
        for raw_line in stream:
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
                if (not isinstance(relative, str) or not relative.startswith(SOURCE_FAMILY)
                        or relative in seen_source_paths):
                    continue
                seen_source_paths.add(relative)
                path = _safe_payload_path(bundle, relative, MAX_SOURCE_BYTES)
                payload_bytes = path.read_bytes()
                if b"2025+" not in payload_bytes:
                    continue
                try:
                    payload = json.loads(payload_bytes.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError("source payload is not valid UTF-8 JSON") from exc
                source_record = payload.get("source_record") if isinstance(payload, dict) else None
                provenance = source_record.get("alternative_definition_provenance") if isinstance(source_record, dict) else None
                evidence = provenance.get("source_evidence") if isinstance(provenance, dict) else None
                matching = [item for item in evidence if isinstance(item, dict)
                            and item.get("source") == SOURCE_LABEL
                            and item.get("source_version") == SOURCE_VERSION] if isinstance(evidence, list) else []
                if not matching:
                    continue
                digest = hashlib.sha256(payload_bytes).hexdigest()
                expected = checksums.get(relative)
                if (not isinstance(expected, dict) or expected.get("sha256") != digest
                        or expected.get("bytes") != len(payload_bytes)):
                    raise ValueError("candidate source payload differs from frozen checksum sidecar")
                if len(matching) != 1:
                    raise ValueError("a candidate payload has ambiguous OEWN evidence entries")
                if relative in candidates:
                    raise ValueError("candidate source payload was indexed more than once")
                candidates[relative] = {
                    "synset_id": payload.get("synset_id"),
                    "sense_id": payload.get("sense_id"),
                    "ili": matching[0].get("ili"),
                    "definition_text_sha256": matching[0].get("definition_text_sha256"),
                    "payload_sha256": digest,
                }

    if len(candidates) != 6:
        raise ValueError("expected six distinct OEWN candidate source payloads")

    index_rows: dict[str, dict[str, Any]] = {}
    refs: dict[str, int] = {path: 0 for path in candidates}
    with index_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            if not isinstance(row, dict) or not isinstance(row.get("source_records"), list):
                continue
            for metadata in row["source_records"]:
                relative = metadata.get("path") if isinstance(metadata, dict) else None
                if relative in candidates:
                    refs[relative] += 1
                    if relative in index_rows:
                        raise ValueError("a candidate path appears in multiple sense-index rows")
                    index_rows[relative] = row

    rules_by_head: dict[str, dict[str, Any]] = {}
    with rules_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            if not isinstance(row, dict) or not isinstance(row.get("head"), str):
                raise ValueError("hypergraph rule record is malformed")
            if row["head"] in {item["synset_id"] for item in candidates.values()}:
                if row["head"] in rules_by_head:
                    raise ValueError("candidate graph head is duplicated")
                rules_by_head[row["head"]] = row

    hyperedges: dict[tuple[str, int], list[Any]] = {}
    with hyperedges_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            if not isinstance(row, dict):
                raise ValueError("hyperedge record is malformed")
            head, clause_index, dependencies = row.get("head"), row.get("clause_index"), row.get("dependencies")
            if isinstance(head, str) and type(clause_index) is int and isinstance(dependencies, list):
                key = (head, clause_index)
                if key in hyperedges:
                    raise ValueError("duplicate hyperedge head/clause index")
                hyperedges[key] = dependencies

    witnesses: dict[str, dict[str, Any]] = {}
    with witnesses_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            if isinstance(row, dict) and isinstance(row.get("head"), str):
                if row["head"] in {item["synset_id"] for item in candidates.values()}:
                    if row["head"] in witnesses:
                        raise ValueError("duplicate selected-witness head")
                    witnesses[row["head"]] = row

    counts = {
        "payloads_referenced_once_by_sense_index": 0,
        "payload_synset_id_equals_index_identity": 0,
        "payload_sense_id_equals_index_identity": 0,
        "candidate_graph_heads_found": 0,
        "graph_clauses_joined_to_hyperedges": 0,
        "active_clause_source_indices_valid": 0,
        "active_source_documents_include_candidate_payload": 0,
        "active_source_documents_join_other_indexed_source_record": 0,
        "selected_witness_rows_found": 0,
        "selected_witness_clauses_match_graph_rule": 0,
        "selected_witness_clauses_match_hyperedges": 0,
        "selected_witness_source_rows_found": 0,
        "selected_witness_source_documents_verified": 0,
        "selected_witness_source_documents_equal_candidate_payload_path": 0,
        "selected_witness_documents_with_oewn_2025_plus_evidence": 0,
        "selected_witness_documents_with_matching_ili_and_definition_hash": 0,
        "selected_witness_documents_with_candidate_definition_text_hash": 0,
        "candidate_payloads_in_nonwitness_active_clauses_only": 0,
        "candidate_payloads_absent_from_all_active_clauses": 0,
    }
    clause_total = active_clause_total = 0
    witness_depths: list[int] = []
    verified_source_documents: dict[str, dict[str, Any]] = {}
    for relative, candidate in candidates.items():
        row = index_rows.get(relative, {})
        counts["payloads_referenced_once_by_sense_index"] += refs[relative] == 1
        counts["payload_synset_id_equals_index_identity"] += candidate["synset_id"] == row.get("identity")
        counts["payload_sense_id_equals_index_identity"] += candidate["sense_id"] == row.get("identity")
        head = candidate["synset_id"]
        rule = rules_by_head.get(head)
        clauses = rule.get("clauses", []) if isinstance(rule, dict) else []
        if rule is not None and isinstance(clauses, list):
            counts["candidate_graph_heads_found"] += 1
            clause_total += len(clauses)
            for index, dependencies in enumerate(clauses):
                if hyperedges.get((head, index)) == dependencies:
                    counts["graph_clauses_joined_to_hyperedges"] += 1
        active = row.get("active_clause_sources", [])
        active = active if isinstance(active, list) else []
        active_clause_total += len(active)
        for item in active:
            if not isinstance(item, dict):
                continue
            ci = item.get("clause_index")
            if type(ci) is int and rule is not None and 0 <= ci < len(clauses):
                counts["active_clause_source_indices_valid"] += 1
            documents = item.get("source_documents", [])
            documents = documents if isinstance(documents, list) else []
            if relative in documents:
                counts["active_source_documents_include_candidate_payload"] += 1
            source_paths = {source.get("path") for source in row.get("source_records", [])
                            if isinstance(source, dict)}
            if any(document in source_paths for document in documents):
                counts["active_source_documents_join_other_indexed_source_record"] += 1
        witness = witnesses.get(head)
        witness_clause_indices: list[int] = []
        if witness is not None:
            counts["selected_witness_rows_found"] += 1
            witness_clause = witness.get("witness_clause")
            if isinstance(witness_clause, list) and witness_clause in clauses:
                counts["selected_witness_clauses_match_graph_rule"] += 1
                witness_clause_indices = [i for i, clause in enumerate(clauses) if clause == witness_clause]
                if any(hyperedges.get((head, i)) == witness_clause for i in witness_clause_indices):
                    counts["selected_witness_clauses_match_hyperedges"] += 1
            depth = witness.get("proof_depth")
            if type(depth) is int and depth >= 0:
                witness_depths.append(depth)

        selected_entries = [entry for entry in active if isinstance(entry, dict)
                            and entry.get("clause_index") in witness_clause_indices]
        if selected_entries:
            counts["selected_witness_source_rows_found"] += 1
        selected_documents = [document for entry in selected_entries
                              for document in (entry.get("source_documents") or [])
                              if isinstance(document, str)]
        candidate_in_any_active = any(
            relative in (entry.get("source_documents") or [])
            for entry in active if isinstance(entry, dict)
        )
        candidate_in_nonwitness_active = any(
            relative in (entry.get("source_documents") or [])
            for entry in active if isinstance(entry, dict)
            and entry.get("clause_index") not in witness_clause_indices
        )
        if candidate_in_nonwitness_active and relative not in selected_documents:
            counts["candidate_payloads_in_nonwitness_active_clauses_only"] += 1
        elif not candidate_in_any_active:
            counts["candidate_payloads_absent_from_all_active_clauses"] += 1
        if relative in selected_documents:
            counts["selected_witness_source_documents_equal_candidate_payload_path"] += 1

        source_evidence_found = pair_match_found = False
        for document in selected_documents:
            if document not in source_paths:
                raise ValueError("selected witness document is absent from the same sense source index")
            cached = verified_source_documents.get(document)
            if cached is None:
                document_path = _safe_payload_path(bundle, document, MAX_SOURCE_BYTES)
                raw_document = document_path.read_bytes()
                digest = hashlib.sha256(raw_document).hexdigest()
                checksum = checksums.get(document)
                if (not isinstance(checksum, dict) or checksum.get("sha256") != digest
                        or checksum.get("bytes") != len(raw_document)):
                    raise ValueError("selected witness source document differs from frozen checksum sidecar")
                try:
                    source_document = json.loads(raw_document.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError("selected witness source document is invalid JSON") from exc
                source_record = source_document.get("source_record") if isinstance(source_document, dict) else None
                provenance = source_record.get("alternative_definition_provenance") if isinstance(source_record, dict) else None
                evidence = provenance.get("source_evidence") if isinstance(provenance, dict) else None
                text_hashes = {
                    hashlib.sha256(value.encode("utf-8")).hexdigest()
                    for value in _string_values(source_document)
                }
                cached = {
                    "evidence": evidence if isinstance(evidence, list) else [],
                    "text_hashes": text_hashes,
                }
                verified_source_documents[document] = cached
                counts["selected_witness_source_documents_verified"] += 1
            evidence_rows = cached["evidence"]
            has_oewn_evidence = any(isinstance(item, dict)
                                    and item.get("source") == SOURCE_LABEL
                                    and item.get("source_version") == SOURCE_VERSION
                                    for item in evidence_rows)
            has_pair_match = any(isinstance(item, dict)
                                 and item.get("source") == SOURCE_LABEL
                                 and item.get("source_version") == SOURCE_VERSION
                                 and item.get("ili") == candidate["ili"]
                                 and item.get("definition_text_sha256") == candidate["definition_text_sha256"]
                                 for item in evidence_rows)
            source_evidence_found |= has_oewn_evidence
            pair_match_found |= has_pair_match
            if candidate["definition_text_sha256"] in cached["text_hashes"]:
                counts["selected_witness_documents_with_candidate_definition_text_hash"] += 1
        counts["selected_witness_documents_with_oewn_2025_plus_evidence"] += source_evidence_found
        counts["selected_witness_documents_with_matching_ili_and_definition_hash"] += pair_match_found

    return {
        "audit_version": "oewn-2025-plus-graph-lineage/3",
        "inputs": {
            "bundle_manifest_sha256": _sha256_file(bundle / "manifest.json"),
            "checksums_sha256": checksums_sha256,
            "sense_index_sha256": _sha256_file(index_path),
            "hypergraph_rules_sha256": _sha256_file(rules_path),
            "hyperedges_sha256": _sha256_file(hyperedges_path),
            "coverage_witnesses_sha256": _sha256_file(witnesses_path),
            "release_match_report_sha256": _sha256_file(release_match_path),
            "implementation_sha256": _sha256_file(Path(__file__).resolve()),
        },
        "scope": {
            "candidate_payloads": len(candidates),
            "candidate_payloads_with_graph_head": counts["candidate_graph_heads_found"],
            "candidate_head_clauses": clause_total,
            "candidate_head_clauses_joined_to_hyperedges": counts["graph_clauses_joined_to_hyperedges"],
            "active_clause_source_rows": active_clause_total,
            "active_source_documents_equal_candidate_payload_path": counts["active_source_documents_include_candidate_payload"],
            "active_source_documents_join_an_indexed_record_for_same_sense": counts["active_source_documents_join_other_indexed_source_record"],
            "payloads_referenced_once_by_sense_index": counts["payloads_referenced_once_by_sense_index"],
            "payload_synset_id_equals_index_identity": counts["payload_synset_id_equals_index_identity"],
            "payload_sense_id_equals_index_identity": counts["payload_sense_id_equals_index_identity"],
            "active_clause_source_rows_with_valid_clause_index": counts["active_clause_source_indices_valid"],
            "selected_witness_rows_found": counts["selected_witness_rows_found"],
            "selected_witness_clauses_matching_graph_rules": counts["selected_witness_clauses_match_graph_rule"],
            "selected_witness_clauses_matching_hyperedges": counts["selected_witness_clauses_match_hyperedges"],
            "selected_witness_source_rows_found": counts["selected_witness_source_rows_found"],
            "selected_witness_source_documents_checksum_verified": counts["selected_witness_source_documents_verified"],
            "selected_witness_source_documents_equal_candidate_payload_path": counts["selected_witness_source_documents_equal_candidate_payload_path"],
            "selected_witness_documents_with_oewn_2025_plus_evidence": counts["selected_witness_documents_with_oewn_2025_plus_evidence"],
            "selected_witness_documents_with_matching_ili_and_definition_hash": counts["selected_witness_documents_with_matching_ili_and_definition_hash"],
            "selected_witness_documents_with_candidate_definition_text_hash": counts["selected_witness_documents_with_candidate_definition_text_hash"],
            "candidate_payloads_in_nonwitness_active_clauses_only": counts["candidate_payloads_in_nonwitness_active_clauses_only"],
            "candidate_payloads_absent_from_all_active_clauses": counts["candidate_payloads_absent_from_all_active_clauses"],
            "selected_witness_depth_min": min(witness_depths) if witness_depths else None,
            "selected_witness_depth_median": statistics.median(witness_depths) if witness_depths else None,
            "selected_witness_depth_max": max(witness_depths) if witness_depths else None,
        },
        "release_clearance": "not_assessed",
        "interpretation_limit": (
            "All six candidate payloads join by synset_id/sense_id to one sense-index identity and a graph head. "
            "Their selected witness clauses join to graph clauses/hyperedges, and the selected source documents are "
            "checksum-verified and indexed under the same sense. Only two selected witness documents contain the "
            "candidate payload path and matching OEWN ILI/definition hash; two further candidate paths occur only in "
            "nonwitness active clauses, while two occur in no active clause document. This is structural lineage, not "
            "proof that an OEWN definition semantically supports a clause or that its reuse is licensed."
        ),
        "raw_text_ids_paths_and_full_urls_emitted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--release-match", type=Path, default=DEFAULT_RELEASE_MATCH)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error("output exists; pass --force to replace")
    try:
        report = audit_oewn_2025_plus_graph_lineage(args.bundle, args.release_match)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), **report["scope"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
