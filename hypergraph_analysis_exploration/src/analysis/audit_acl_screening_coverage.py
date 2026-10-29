"""Build an aggregate, current ACL Anthology screening-coverage snapshot.

Uses exact URL joins and the existing explicit per-study depth classifier;
emits no paper titles, authors, abstracts, or URLs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.analysis.reconcile_acl_screening_logs import LOG_GLOB, reconcile
from src.analysis.project_paths import PROJECT_ROOT


DEFAULT_SOURCES_DIR = PROJECT_ROOT / "sources"
DEFAULT_CANDIDATES = PROJECT_ROOT / "sources" / "acl_anthology_candidates_2026-10-06_v3.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase91" / "acl_screening_coverage.json"
DEPTHS = (
    "full_text_screened",
    "targeted_sections_screened",
    "metadata_or_abstract_only",
    "prior_log_depth_unresolved",
    "pending_title_abstract_screen",
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _count_dict(counter: Counter[str]) -> dict[str, int]:
    return {key: counter.get(key, 0) for key in DEPTHS}


def audit_acl_screening_coverage(candidates_path: Path, sources_dir: Path) -> dict[str, Any]:
    candidates_path = candidates_path.resolve()
    sources_dir = sources_dir.resolve()
    logs = sorted(sources_dir.glob(LOG_GLOB))
    if not logs:
        raise ValueError("no structured literature screening logs were found")
    input_manifest = {
        "candidate_frame_sha256": _sha256_file(candidates_path),
        "screening_log_count": len(logs),
        "screening_logs_sha256": hashlib.sha256(json.dumps(
            [(path.name, _sha256_file(path)) for path in logs],
            ensure_ascii=False, separators=(",", ":"),
        ).encode("utf-8")).hexdigest(),
        "reconciler_implementation_sha256": _sha256_file(
            Path(__file__).resolve().with_name("reconcile_acl_screening_logs.py")
        ),
        "audit_implementation_sha256": _sha256_file(Path(__file__).resolve()),
    }

    frame = reconcile(candidates_path, sources_dir)
    candidates = frame.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("candidate frame must contain a nonempty candidates list")

    overall: Counter[str] = Counter()
    by_year: dict[str, Counter[str]] = defaultdict(Counter)
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    evidence_multiplicity: Counter[str] = Counter()
    for row in candidates:
        if not isinstance(row, dict):
            raise ValueError("candidate frame contains a malformed row")
        depth = row.get("screening_depth_status", "pending_title_abstract_screen")
        if depth not in DEPTHS:
            raise ValueError("candidate frame contains an unknown screening depth")
        overall[depth] += 1
        year = str(row.get("year", "missing"))
        by_year[year][depth] += 1
        evidence = row.get("screening_evidence", [])
        evidence_multiplicity[str(len(evidence) if isinstance(evidence, list) else 0)] += 1
        families = row.get("matched_query_families", [])
        if isinstance(families, list):
            for family in families:
                if isinstance(family, str):
                    by_family[family][depth] += 1

    candidate_total = len(candidates)
    if sum(overall.values()) != candidate_total:
        raise ValueError("screening-depth totals do not equal the fixed candidate count")
    matched = candidate_total - overall["pending_title_abstract_screen"]
    if matched != frame["screening_reconciliation"].get("matched_candidate_count"):
        raise ValueError("aggregate depth counts differ from the exact-URL reconciler")

    return {
        "audit_version": "acl-screening-coverage/1",
        "inputs": input_manifest,
        "scope": {
            "database": frame.get("database"),
            "export_content_sha256": frame.get("export_content_sha256"),
            "date_window": frame.get("date_window"),
            "candidate_count": candidate_total,
            "unique_screening_log_matched_candidates": matched,
            "pending_title_abstract_screen": overall["pending_title_abstract_screen"],
            "distinct_query_families": len(by_family),
            "screening_evidence_record_multiplicity_by_candidate": dict(sorted(
                evidence_multiplicity.items(), key=lambda item: int(item[0])
            )),
        },
        "screening_depth_counts": _count_dict(overall),
        "by_publication_year": {
            year: _count_dict(counts) for year, counts in sorted(by_year.items())
        },
        "by_query_family_membership_and_global_log_match_depth": {
            family: {
                "candidate_memberships": sum(counts.values()),
                "depth_counts": _count_dict(counts),
            }
            for family, counts in sorted(by_family.items())
        },
        "interpretation_limit": (
            "A URL join means a candidate has at least one structured log record; it is not a relevance decision. "
            "Depth categories use only explicit per-study evidence. Query-family rows describe candidates tagged with "
            "each family and their global URL-join depth against all logs; they do not measure screening coverage "
            "within that query family. Candidate memberships overlap across query families. "
            "This is a fixed-frame screening-coverage audit, not a systematic review, quality appraisal, exhaustive "
            "full-text synthesis, novelty finding, or absence claim."
        ),
        "raw_titles_authors_abstracts_and_urls_emitted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--sources-dir", type=Path, default=DEFAULT_SOURCES_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        report = audit_acl_screening_coverage(args.candidates, args.sources_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), **report["scope"],
                      "screening_depth_counts": report["screening_depth_counts"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
