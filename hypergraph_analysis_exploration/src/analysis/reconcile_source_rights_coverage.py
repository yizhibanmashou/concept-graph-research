"""Reconcile aggregate source profiles with official-source review labels.

This report crosswalks two already privacy-filtered audit artifacts. It does
not open source payloads, gloss text, identities, paths, or full URLs, and an
exact label match is not a license or release-clearance decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from src.analysis.project_paths import PROJECT_ROOT


DEFAULT_TRIAGE = PROJECT_ROOT / "outputs" / "phase24" / "source_release_candidate_triage.json"
DEFAULT_RIGHTS = PROJECT_ROOT / "sources" / "source_release_rights_evidence_2026-10-06.json"
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase50" / "source_rights_crosswalk_audit.json"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label} JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def reconcile_source_rights_coverage(triage_path: Path, rights_path: Path) -> dict[str, Any]:
    """Join aggregate profiles to rights records by exact source-label only."""
    triage_path = triage_path.resolve()
    rights_path = rights_path.resolve()
    triage = _load_object(triage_path, "source candidate triage")
    rights = _load_object(rights_path, "source rights evidence")

    profiles = triage.get("candidate_profiles")
    rights_rows = rights.get("sources")
    if not isinstance(profiles, list) or not isinstance(rights_rows, list):
        raise ValueError("input audit schemas are missing candidate_profiles or sources arrays")
    if triage.get("raw_gloss_ids_paths_and_full_urls_emitted") is not False:
        raise ValueError("candidate triage does not certify its privacy-filtered output")

    rights_by_label: dict[str, dict[str, Any]] = {}
    for row in rights_rows:
        if not isinstance(row, dict):
            raise ValueError("rights evidence contains a malformed source row")
        label = row.get("source_label")
        if not isinstance(label, str) or not label:
            raise ValueError("rights evidence contains a missing source label")
        if label in rights_by_label:
            raise ValueError("rights evidence contains duplicate source labels")
        rights_by_label[label] = row

    aggregate: dict[str, dict[str, Any]] = {}
    for profile in profiles:
        if not isinstance(profile, dict):
            raise ValueError("candidate triage contains a malformed profile")
        label = profile.get("source")
        count = profile.get("payload_count")
        if not isinstance(label, str) or not label or type(count) is not int or count <= 0:
            raise ValueError("candidate profile has an invalid source label or payload count")
        item = aggregate.setdefault(label, {"profile_count": 0, "payload_count": 0})
        item["profile_count"] += 1
        item["payload_count"] += count

    candidate_sources = []
    matched_payloads = unmatched_payloads = 0
    for label, counts in sorted(aggregate.items()):
        rights_row = rights_by_label.get(label)
        exact_match = rights_row is not None
        if exact_match:
            matched_payloads += counts["payload_count"]
        else:
            unmatched_payloads += counts["payload_count"]
        candidate_sources.append({
            "source_label": label,
            **counts,
            "exact_rights_log_label_match": exact_match,
            "rights_evidence_status": (
                rights_row.get("license_status", rights_row.get("status")) if exact_match else None
            ),
        })

    referenced_labels = set(aggregate)
    total_profiles = sum(item["profile_count"] for item in aggregate.values())
    total_payloads = matched_payloads + unmatched_payloads
    return {
        "audit_version": "source-rights-crosswalk/1",
        "inputs": {
            "candidate_triage_sha256": _sha256_file(triage_path),
            "rights_evidence_sha256": _sha256_file(rights_path),
            "implementation_sha256": _sha256_file(Path(__file__).resolve()),
            "triage_audit_version": triage.get("audit_version"),
            "rights_audit_date": rights.get("audit_date"),
        },
        "scope": {
            "join_policy": "exact source-label equality only; no aliases inferred",
            "candidate_profiles": len(profiles),
            "distinct_candidate_source_labels": len(aggregate),
            "rights_log_source_labels": len(rights_by_label),
            "candidate_payloads_across_profiles": total_payloads,
            "exact_label_matched_profiles": sum(
                item["profile_count"] for label, item in aggregate.items() if label in rights_by_label
            ),
            "exact_label_matched_payloads": matched_payloads,
            "unmatched_profiles": sum(
                item["profile_count"] for label, item in aggregate.items() if label not in rights_by_label
            ),
            "unmatched_payloads": unmatched_payloads,
            "rights_log_labels_not_in_candidate_profiles": sorted(set(rights_by_label) - referenced_labels),
        },
        "candidate_sources": candidate_sources,
        "release_clearance": "not_assessed",
        "interpretation_limit": (
            "Exact label matches only identify a source label with a row in the rights-evidence log. "
            "Unmatched labels may be aliases or unreviewed sources; neither condition is resolved here. "
            "A match does not bind payload bytes to an upstream artifact/release or establish license compatibility, "
            "attribution sufficiency, or public-release clearance."
        ),
        "raw_text_ids_paths_and_full_urls_emitted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--triage", type=Path, default=DEFAULT_TRIAGE)
    parser.add_argument("--rights-evidence", type=Path, default=DEFAULT_RIGHTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error(f"output exists; pass --force to replace: {output}")
    try:
        report = reconcile_source_rights_coverage(args.triage, args.rights_evidence)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), **report["scope"], "release_clearance": report["release_clearance"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
