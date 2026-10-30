"""Summarize source-evidence coverage without emitting glosses or locators.

The audit is scoped to the frozen bundle's alternative/definition WSD records.
Declared source labels are preserved as labels; they are not treated as
independent source families or as evidence that reuse is licensed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "t02-source-provenance-audit/2"
SCOPE_PREFIX = "sources/Synset/alternative_or_definition_wsd_frozen/"
LICENSE_KEYS = {"license", "licence", "license_url", "licence_url"}
RELATION_FIELD_GROUPS = {
    "predicate_or_relation_type": {"predicate", "relation", "relation_type", "semantic_relation"},
    "argument_or_role": {
        "arguments", "roles", "semantic_roles", "agent", "patient", "theme",
        "source_role", "goal_role",
    },
    "polarity_or_negation_scope": {"polarity", "negation", "negation_scope"},
    "evidence_span_locator": {
        "evidence_span", "source_span", "text_span", "evidence_locator", "quote_locator",
    },
}


def _walk_license_fields(value: Any) -> bool:
    if isinstance(value, dict):
        if any(str(key).lower() in LICENSE_KEYS for key in value):
            return True
        return any(_walk_license_fields(child) for child in value.values())
    if isinstance(value, list):
        return any(_walk_license_fields(child) for child in value)
    return False


def summarize_bundle(bundle: Path) -> dict[str, Any]:
    """Read the scoped source index and aggregate provenance metadata only."""
    bundle = bundle.resolve()
    index_path = bundle / "indexes" / "source_records.jsonl"
    index_bytes = index_path.read_bytes()
    rows = []
    for line_number, line in enumerate(index_bytes.decode("utf-8").splitlines(), 1):
        row = json.loads(line)
        relpath = row.get("path")
        if isinstance(relpath, str) and relpath.startswith(SCOPE_PREFIX):
            rows.append((line_number, relpath))

    totals = Counter()
    labels: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"evidence_items": 0, "record_count": 0,
                 "source_version_present": 0, "source_version_missing": 0,
                 "source_locator_present": 0, "source_locator_missing": 0,
                 "download_url_present": 0, "download_url_missing": 0,
                 "definition_sha256_present": 0, "license_field_present": 0}
    )
    errors = []
    payloads_digest = hashlib.sha256()
    relation_field_counts = Counter()
    evidence_items_with_relation_fields = 0

    for line_number, relpath in rows:
        source_file = (bundle / relpath).resolve()
        if not source_file.is_relative_to(bundle):
            errors.append({"index_line": line_number, "error": "path_outside_bundle"})
            continue
        try:
            payload_bytes = source_file.read_bytes()
            payload = json.loads(payload_bytes.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append({"index_line": line_number, "error": type(exc).__name__})
            continue
        payloads_digest.update(relpath.encode("utf-8"))
        payloads_digest.update(b"\0")
        payloads_digest.update(hashlib.sha256(payload_bytes).digest())
        totals["payloads_read"] += 1
        source_record = payload.get("source_record")
        provenance = (source_record.get("alternative_definition_provenance")
                      if isinstance(source_record, dict) else None)
        if not isinstance(provenance, dict):
            totals["records_without_provenance"] += 1
            continue
        evidence = provenance.get("source_evidence")
        if not isinstance(evidence, list) or not evidence:
            totals["records_without_evidence_list"] += 1
            continue
        totals["records_with_source_evidence"] += 1
        seen_labels = set()
        for item in evidence:
            if not isinstance(item, dict):
                totals["nonobject_evidence_items"] += 1
                continue
            totals["evidence_items"] += 1
            label = item.get("source")
            label = label.strip() if isinstance(label, str) and label.strip() else "<missing>"
            aggregate = labels[label]
            aggregate["evidence_items"] += 1
            seen_labels.add(label)
            for field, name in (("source_version", "source_version"),
                                ("source_locator", "source_locator"),
                                ("download_url", "download_url"),
                                ("definition_text_sha256", "definition_sha256")):
                aggregate[name + ("_present" if item.get(field) not in (None, "") else "_missing")] += 1
            aggregate["license_field_present"] += _walk_license_fields(item)
            evidence_keys = {str(key).lower() for key in item}
            present_groups = [
                group for group, field_names in RELATION_FIELD_GROUPS.items()
                if evidence_keys & field_names
            ]
            evidence_items_with_relation_fields += bool(present_groups)
            relation_field_counts.update(present_groups)
        for label in seen_labels:
            labels[label]["record_count"] += 1
        totals["records_with_license_field_in_evidence"] += _walk_license_fields(evidence)

    # The report intentionally contains no source path, raw locator, URL, gloss,
    # definition text, candidate ID, or unreviewed source_evidence payload.
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE_PREFIX,
        "summary": {
            "indexed_records": len(rows),
            "payloads_read": totals["payloads_read"],
            "payload_errors": len(errors),
            "records_with_source_evidence": totals["records_with_source_evidence"],
            "records_without_provenance": totals["records_without_provenance"],
            "records_without_evidence_list": totals["records_without_evidence_list"],
            "evidence_items": totals["evidence_items"],
            "unique_exact_source_labels": len(labels),
            "records_with_license_field_in_evidence": totals["records_with_license_field_in_evidence"],
            "source_evidence_items_with_typed_relation_fields": evidence_items_with_relation_fields,
        },
        "typed_relation_field_coverage": {
            "evidence_items_with_any_field_group": evidence_items_with_relation_fields,
            "evidence_items_by_field_group": {
                group: relation_field_counts[group] for group in RELATION_FIELD_GROUPS
            },
            "field_groups": {
                "predicate_or_relation_type": "explicit relation/predicate field name on the evidence object",
                "argument_or_role": "argument list or participant-role field name on the evidence object",
                "polarity_or_negation_scope": "polarity, negation, or scope field name on the evidence object",
                "evidence_span_locator": "explicit span/quote locator field name on the evidence object",
            },
            "limits": (
                "Counts inspect only top-level keys of source_evidence objects; they do not read field values, "
                "definitions, quotes, or locators. Field presence would not establish that a relation is correct "
                "or supported. Absence here does not prove the upstream source lacks usable evidence."
            ),
        },
        "inputs_sha256": {
            "source_records_index": hashlib.sha256(index_bytes).hexdigest(),
            "scoped_payload_set": payloads_digest.hexdigest(),
        },
        "declared_source_labels": [
            {"source_label_exact": label, **labels[label]}
            for label in sorted(labels)
        ],
        "errors": errors,
        "limits": (
            "Source labels and versions are package-declared metadata, not normalized independent source families. "
            "This audit does not verify upstream identity, version authenticity, license compatibility, or semantic fidelity. "
            "Raw locators, URLs, glosses, definitions, and candidate IDs are not emitted."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = summarize_bundle(args.bundle)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
