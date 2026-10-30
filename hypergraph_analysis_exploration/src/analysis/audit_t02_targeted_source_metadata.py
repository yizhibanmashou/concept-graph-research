"""Aggregate safe metadata patterns for the two high-frequency Kaikki labels.

This tool never emits source text, IDs, local paths, raw locators, or full URLs.
Only version-shape buckets, enumerated evidence-type tokens, and URL hostnames
are included in its report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any


SCOPE_PREFIX = "sources/Synset/alternative_or_definition_wsd_frozen/"
TARGET_LABELS = {
    "Kaikki/Wiktextract targeted OEWN gap",
    "Kaikki/Wiktextract relaxed definition-term fallback",
}
SAFE_TOKEN = re.compile(r"^[A-Za-z0-9_.:/-]{1,48}$")
DATE_LIKE = re.compile(r"\b20\d{2}[-/.]\d{1,2}(?:[-/.]\d{1,2})?\b")
SEMVER_LIKE = re.compile(r"^v?\d+\.\d+(?:\.\d+)?(?:[-+][A-Za-z0-9.-]+)?$")
HASH_LIKE = re.compile(r"^[0-9a-fA-F]{40}(?:[0-9a-fA-F]{24})?$")


def _version_shape(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return "missing"
    value = value.strip()
    if HASH_LIKE.fullmatch(value):
        return "hash_like"
    if DATE_LIKE.search(value):
        return "date_like"
    if SEMVER_LIKE.fullmatch(value):
        return "semantic_version_like"
    if len(value) <= 48 and SAFE_TOKEN.fullmatch(value):
        return "short_token"
    return "other_nonempty"


def _safe_enum(value: Any) -> str:
    if isinstance(value, str) and SAFE_TOKEN.fullmatch(value):
        return value
    return "other_or_missing"


def _host(value: Any) -> str:
    if not isinstance(value, str):
        return "missing_or_non_url"
    try:
        parsed = urlsplit(value.strip())
        hostname = (parsed.hostname or "").lower()
    except ValueError:
        return "invalid_or_non_url"
    if parsed.scheme.lower() in {"http", "https"} and hostname:
        return hostname
    return "missing_or_non_url"


def summarize_bundle(bundle: Path) -> dict[str, Any]:
    bundle = bundle.resolve()
    index_path = bundle / "indexes" / "source_records.jsonl"
    index_bytes = index_path.read_bytes()
    rows = []
    for line_number, line in enumerate(index_bytes.decode("utf-8").splitlines(), 1):
        row = json.loads(line)
        relpath = row.get("path")
        if isinstance(relpath, str) and relpath.startswith(SCOPE_PREFIX):
            rows.append((line_number, relpath))

    by_label: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "evidence_items": 0,
            "records": 0,
            "version_shape": Counter(),
            "evidence_type": Counter(),
            "locator_host": Counter(),
            "ontology_host": Counter(),
            "field_presence": Counter(),
        }
    )
    payload_digest = hashlib.sha256()
    errors = Counter()
    payloads_read = 0

    for line_number, relpath in rows:
        path = (bundle / relpath).resolve()
        if not path.is_relative_to(bundle):
            errors["path_outside_bundle"] += 1
            continue
        try:
            raw = path.read_bytes()
            payload = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors[type(exc).__name__] += 1
            continue
        payload_digest.update(relpath.encode("utf-8"))
        payload_digest.update(b"\0")
        payload_digest.update(hashlib.sha256(raw).digest())
        payloads_read += 1
        source_record = payload.get("source_record")
        provenance = (source_record.get("alternative_definition_provenance")
                      if isinstance(source_record, dict) else None)
        evidence = provenance.get("source_evidence") if isinstance(provenance, dict) else None
        if not isinstance(evidence, list):
            continue
        seen: set[str] = set()
        for item in evidence:
            if not isinstance(item, dict) or item.get("source") not in TARGET_LABELS:
                continue
            label = item["source"]
            aggregate = by_label[label]
            aggregate["evidence_items"] += 1
            seen.add(label)
            aggregate["version_shape"][_version_shape(item.get("source_version"))] += 1
            aggregate["evidence_type"][_safe_enum(item.get("evidence_type"))] += 1
            aggregate["locator_host"][_host(item.get("source_locator"))] += 1
            aggregate["ontology_host"][_host(item.get("source_ontology"))] += 1
            for field in ("source_version", "source_locator", "source_ontology", "evidence_type"):
                aggregate["field_presence"][field + ("_present" if item.get(field) not in (None, "") else "_missing")] += 1
        for label in seen:
            by_label[label]["records"] += 1

    labels = {}
    for label in sorted(TARGET_LABELS):
        aggregate = by_label[label]
        labels[label] = {
            "evidence_items": aggregate["evidence_items"],
            "records": aggregate["records"],
            "version_shape": dict(sorted(aggregate["version_shape"].items())),
            "evidence_type": dict(sorted(aggregate["evidence_type"].items())),
            "locator_host": dict(sorted(aggregate["locator_host"].items())),
            "ontology_host": dict(sorted(aggregate["ontology_host"].items())),
            "field_presence": dict(sorted(aggregate["field_presence"].items())),
        }
    return {
        "schema_version": "t02-targeted-source-metadata-audit/1",
        "summary": {"indexed_records": len(rows), "payloads_read": payloads_read,
                    "payload_errors": dict(sorted(errors.items())),
                    "target_labels": len(TARGET_LABELS),
                    "target_evidence_items": sum(x["evidence_items"] for x in labels.values())},
        "inputs_sha256": {"source_records_index": hashlib.sha256(index_bytes).hexdigest(),
                          "scoped_payload_set": payload_digest.hexdigest()},
        "labels": labels,
        "limits": "Metadata shape and hostname counts do not bind the local records to an upstream dump/version or establish rights clearance.",
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
