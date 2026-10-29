"""Replay a hashed minimum-depth clause-to-source map against a frozen bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from src.analysis.frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK, verify_frozen_bundle_integrity
from src.analysis.frozen_hypergraph_audit import DEFAULT_BUNDLE, jsonl, load_graph
from src.analysis.minimum_witness_audit import minimum_depth_clauses_by_head, minimum_derivation_depths


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAP = PROJECT_ROOT / "outputs" / "phase216" / "minimum_depth_alternative_source_map.jsonl"
DEFAULT_AUDIT = PROJECT_ROOT / "outputs" / "phase216" / "minimum_depth_alternative_source_audit.json"
MAP_FIELDS = {
    "head_key_sha256", "clause_index", "body_key_sha256", "body_literal_count",
    "source_document_key_sha256", "source_payload_sha256", "source_payload_bytes",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _key_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_source_map(
    bundle: Path = DEFAULT_BUNDLE,
    integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
    source_map: Path = DEFAULT_MAP,
    audit_output: Path | None = DEFAULT_AUDIT,
) -> dict[str, Any]:
    bundle = bundle.resolve()
    source_map = source_map.resolve()
    integrity = verify_frozen_bundle_integrity(bundle, integrity_lock.resolve())
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity verification failed")

    rules, clauses, _ = load_graph(bundle)
    heads = set(rules)
    basis = {
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    depths = minimum_derivation_depths(heads, clauses, basis)
    alternatives = minimum_depth_clauses_by_head(heads, clauses, depths, basis)
    checksums = {
        row["path"]: row for row in jsonl(bundle / "checksums.jsonl")
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }

    expected_rows: list[dict[str, Any]] = []
    seen_heads: set[str] = set()
    for row in jsonl(bundle / "indexes" / "senses.jsonl"):
        head = row.get("identity") if isinstance(row, dict) else None
        if not isinstance(head, str) or head not in heads or head in seen_heads:
            raise ValueError("sense index has malformed, unknown, or duplicate graph identity")
        seen_heads.add(head)
        if head in basis:
            continue
        docs_by_clause: dict[int, set[str]] = {}
        for entry in row.get("active_clause_sources", []):
            if not isinstance(entry, dict) or type(entry.get("clause_index")) is not int:
                continue
            documents = entry.get("source_documents")
            if not isinstance(documents, list):
                continue
            docs_by_clause.setdefault(entry["clause_index"], set()).update(
                document for document in documents if isinstance(document, str) and document
            )

        clause_indices = {tuple(body): index for index, body in enumerate(rules[head])}
        for body in alternatives[head]:
            clause_index = clause_indices.get(tuple(body))
            if clause_index is None:
                raise ValueError("minimum-depth clause is absent from graph rule inventory")
            for document in docs_by_clause.get(clause_index, set()):
                checksum = checksums.get(document)
                if not isinstance(checksum, dict) or not isinstance(checksum.get("sha256"), str):
                    raise ValueError("source document lacks checksum metadata")
                if type(checksum.get("bytes")) is not int:
                    raise ValueError("source document checksum byte count is malformed")
                expected_rows.append({
                    "head_key_sha256": _key_hash(head),
                    "clause_index": clause_index,
                    "body_key_sha256": hashlib.sha256(
                        json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                    ).hexdigest(),
                    "body_literal_count": len(body),
                    "source_document_key_sha256": _key_hash(document),
                    "source_payload_sha256": checksum["sha256"],
                    "source_payload_bytes": checksum["bytes"],
                })
    if seen_heads != heads:
        raise ValueError("sense index and graph head sets differ")

    expected_rows.sort(key=lambda row: (
        row["head_key_sha256"], row["clause_index"], row["source_document_key_sha256"]
    ))
    if audit_output is not None:
        audit = json.loads(audit_output.read_text(encoding="utf-8"))
        audit_map = audit.get("source_map")
        if not isinstance(audit_map, dict) or audit_map.get("requested") is not True:
            raise ValueError("audit output does not declare a source map")
        if audit_map.get("row_count") != len(expected_rows):
            raise ValueError("audit output source-map row count differs from reconstruction")
        if audit_map.get("sha256") != _sha256(source_map):
            raise ValueError("source map hash differs from the audit output")

    actual_count = 0
    with source_map.open("r", encoding="utf-8") as stream:
        for row_number, (line, expected) in enumerate(zip(stream, expected_rows, strict=False), start=1):
            try:
                actual = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"source-map row {row_number} is invalid JSON") from exc
            if not isinstance(actual, dict) or set(actual) != MAP_FIELDS:
                raise ValueError(f"source-map row {row_number} has unexpected fields")
            if actual != expected:
                raise ValueError(f"source-map row {row_number} differs from bundle reconstruction")
            actual_count += 1
        if actual_count != len(expected_rows):
            raise ValueError("source map has fewer rows than the reconstructed mapping")
        if stream.readline():
            raise ValueError("source map has more rows than the reconstructed mapping")

    return {
        "schema_version": "minimum-depth-alternative-source-map-verification/1",
        "bundle_integrity_valid": True,
        "source_map_exactly_matches_bundle_reconstruction": True,
        "association_count": len(expected_rows),
        "unique_association_count": len({
            (row["head_key_sha256"], row["clause_index"], row["source_document_key_sha256"])
            for row in expected_rows
        }),
        "source_map_sha256": _sha256(source_map),
        "raw_paths_or_plaintext_ids_present": False,
        "source_payload_bytes_read": 0,
        "gloss_semantics_assessed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--source-map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--output", type=Path,
                        default=PROJECT_ROOT / "outputs" / "phase216" / "minimum_depth_alternative_source_map_verification.json")
    args = parser.parse_args(argv)
    try:
        result = verify_source_map(args.bundle, args.integrity_lock, args.source_map, args.audit_output)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "schema_version": "minimum-depth-alternative-source-map-verification/1",
            "valid": False,
            "error_type": type(exc).__name__,
        }, ensure_ascii=False, indent=2))
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
