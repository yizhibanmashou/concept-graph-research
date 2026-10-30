"""Reconcile T02 source labels with the local source-rights evidence log.

This performs only a conservative lexical join. It does not verify that a
frozen record came from the upstream source/release or that reuse is cleared.
The output contains aggregate source labels and categorical log status only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "t02-source-label-rights-reconciliation/1"


def normalize_label(label: str) -> str:
    """Normalize case and separators only; do not perform fuzzy matching."""
    return re.sub(r"\s+", " ", label.replace("_", " ").strip()).casefold()


def reconcile(audit_path: Path, rights_path: Path) -> dict[str, Any]:
    audit_bytes = audit_path.read_bytes()
    rights_bytes = rights_path.read_bytes()
    audit = json.loads(audit_bytes.decode("utf-8"))
    rights_log = json.loads(rights_bytes.decode("utf-8"))
    labels = audit.get("declared_source_labels")
    rights = rights_log.get("sources")
    if not isinstance(labels, list) or not isinstance(rights, list):
        raise ValueError("input schema requires declared_source_labels and sources arrays")

    rights_by_normalized: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in rights:
        if not isinstance(entry, dict):
            continue
        label = entry.get("source_label")
        if isinstance(label, str) and label.strip():
            rights_by_normalized[normalize_label(label)].append(entry)

    totals = Counter()
    reconciled = []
    for entry in labels:
        if not isinstance(entry, dict):
            raise ValueError("source label entries must be objects")
        label = entry.get("source_label_exact")
        if not isinstance(label, str) or not label.strip():
            raise ValueError("source_label_exact must be a non-empty string")
        evidence_items = entry.get("evidence_items")
        record_count = entry.get("record_count")
        if not isinstance(evidence_items, int) or evidence_items < 0:
            raise ValueError("evidence_items must be a non-negative integer")
        candidates = rights_by_normalized.get(normalize_label(label), [])
        if len(candidates) == 1:
            match_status = "unique_normalized_label_match"
            matched_label = candidates[0]["source_label"]
            license_status = candidates[0].get("license_status")
            license_status = license_status if isinstance(license_status, str) else "not_recorded"
            totals["matched_profiles"] += 1
            totals["matched_evidence_items"] += evidence_items
        elif len(candidates) > 1:
            match_status = "ambiguous_normalized_label_match"
            matched_label = None
            license_status = "not_joined_ambiguous"
            totals["ambiguous_profiles"] += 1
            totals["ambiguous_evidence_items"] += evidence_items
        else:
            match_status = "no_normalized_label_match"
            matched_label = None
            license_status = "no_matching_log_entry"
            totals["unmatched_profiles"] += 1
            totals["unmatched_evidence_items"] += evidence_items
        totals["source_profiles"] += 1
        totals["evidence_items"] += evidence_items
        reconciled.append({
            "source_label_exact": label,
            "evidence_items": evidence_items,
            "record_count": record_count,
            "match_status": match_status,
            "rights_log_label": matched_label,
            "rights_log_status": license_status,
        })

    if len({row["source_label_exact"] for row in reconciled}) != len(reconciled):
        raise ValueError("declared source labels must be unique for profile aggregation")
    return {
        "schema_version": SCHEMA_VERSION,
        "normalization": "casefold; replace underscore with space; collapse whitespace; no fuzzy aliases",
        "inputs_sha256": {
            "t02_source_audit": hashlib.sha256(audit_bytes).hexdigest(),
            "source_rights_log": hashlib.sha256(rights_bytes).hexdigest(),
        },
        "summary": {
            "source_profiles": totals["source_profiles"],
            "evidence_items": totals["evidence_items"],
            "unique_normalized_matches": totals["matched_profiles"],
            "matched_evidence_items": totals["matched_evidence_items"],
            "ambiguous_profiles": totals["ambiguous_profiles"],
            "ambiguous_evidence_items": totals["ambiguous_evidence_items"],
            "unmatched_profiles": totals["unmatched_profiles"],
            "unmatched_evidence_items": totals["unmatched_evidence_items"],
        },
        "source_labels": sorted(reconciled, key=lambda row: row["source_label_exact"].casefold()),
        "limitations": (
            "A normalized label match only locates a source-rights log row. It does not establish upstream identity, "
            "release/version alignment, record-level provenance, license compatibility, attribution compliance, "
            "semantic fidelity, or independent source-family status. Ambiguous and unmatched labels require manual review."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--rights-log", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = reconcile(args.audit, args.rights_log)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps(result["summary"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
