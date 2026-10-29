"""Reconcile an ACL candidate frame with existing screening logs.

Matches exact ACL Anthology page URLs and normalizes only explicit, per-study
screening-depth evidence. It does not infer relevance or infer a study's depth
from a log-level review method or count.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


DEFAULT_CANDIDATES = Path("sources/acl_anthology_candidates_2026-10-05.json")
LOG_GLOB = "literature_screening_log*.json"


def _canonical_anthology_url(value: str) -> str | None:
    parsed = urlparse(value.strip())
    if parsed.netloc.casefold() not in {"aclanthology.org", "www.aclanthology.org"}:
        return None
    path = parsed.path.rstrip("/")
    if path.casefold().endswith(".pdf"):
        path = path[:-4]
    if not path:
        return None
    return f"https://aclanthology.org{path}"


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


DEPTH_FIELDS = {
    "full_text_read",
    "full_text_read_this_turn",
    "full_text_screened",
    "official_full_text_reviewed",
    "full_text_status",
    "screening_depth_status",
    "screening_depth",
    "screening_status",
    "status",
    "reviewed_scope",
}


def _depth_from_explicit_fields(fields: dict[str, Any]) -> str:
    declared_depth = fields.get("screening_depth_status", fields.get("screening_depth"))
    if declared_depth in {
        "full_text_screened",
        "official_full_text",
        "targeted_sections_screened",
        "metadata_or_abstract_only",
        "prior_log_depth_unresolved",
    }:
        return "full_text_screened" if declared_depth == "official_full_text" else declared_depth

    values = [(key, str(value).casefold()) for key, value in fields.items()]
    if any(
        "full text not reviewed" in value
        or "full-text not reviewed" in value
        or "full text not read" in value
        or "full-text not read" in value
        or "full text not screened" in value
        or "full-text not screened" in value
        for _, value in values
    ):
        return "metadata_or_abstract_only"
    if any(value is True for key, value in fields.items() if key in {
        "full_text_read", "full_text_screened", "official_full_text_reviewed"
    }):
        return "full_text_screened"
    if any(
        "full_text_screened" in value
        or "full_text_read" in value
        or "full pdf" in value
        or "full " in value and " pdf" in value and any(term in value for term in ("screened", "reviewed", "inspected", "read"))
        or key == "reviewed_scope" and "full " in value and " pdf" in value
        or "full-text" in value and any(term in value for term in ("screened", "reviewed", "inspected"))
        or "full text" in value and any(term in value for term in ("screened", "reviewed", "inspected"))
        or "pdf inspected" in value
        or "pdf screened" in value
        or "pdf reviewed" in value
        for key, value in values
    ):
        return "full_text_screened"
    if any(
        "targeted pdf sections" in value
        or "relevant full-paper sections" in value
        or "targeted sections" in value
        for _, value in values
    ):
        return "targeted_sections_screened"
    if any(
        "abstract" in value and any(term in value for term in ("checked", "screened", "inspected"))
        or "page/abstract" in value
        or "metadata only" in value
        or "metadata and abstract" in value and "full pdf" not in value
        for _, value in values
    ) or fields.get("full_text_read_this_turn") is False:
        return "metadata_or_abstract_only"
    return "prior_log_depth_unresolved"


def _study_url_records(log: dict[str, Any], log_name: str) -> list[dict[str, Any]]:
    matches: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in _walk(log):
        title = record.get("title")
        if not isinstance(title, str) or not title.strip():
            continue
        depth_evidence = {
            key: value for key, value in record.items()
            if key.casefold() in DEPTH_FIELDS and isinstance(value, (str, bool))
        }
        depth_status = _depth_from_explicit_fields(depth_evidence)
        for key, value in record.items():
            if not isinstance(value, str) or key.casefold() not in {"url", "pdf", "paper_url", "official_url"}:
                continue
            canonical = _canonical_anthology_url(value)
            if canonical is None:
                continue
            evidence_key = (canonical, title.strip(), json.dumps(depth_evidence, ensure_ascii=False, sort_keys=True))
            matches[evidence_key] = {
                "log": log_name,
                "study_title_in_log": title.strip(),
                "explicit_depth_evidence": depth_evidence,
                "screening_depth_status": depth_status,
            }
    return [{"url": url, **detail} for (url, _, _), detail in sorted(matches.items())]


def reconcile(candidates_path: Path, sources_dir: Path) -> dict[str, Any]:
    frame = json.loads(candidates_path.read_text(encoding="utf-8-sig"))
    candidates = frame.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("candidate frame must contain a candidates list")

    source_records: list[dict[str, Any]] = []
    for path in sorted(sources_dir.glob(LOG_GLOB)):
        log = json.loads(path.read_text(encoding="utf-8-sig"))
        source_records.extend(_study_url_records(log, path.name))

    by_url: dict[str, list[dict[str, str]]] = {}
    for record in source_records:
        by_url.setdefault(record["url"], []).append(record)

    logged_count = 0
    for candidate in candidates:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("url"), str):
            raise ValueError("every candidate must be an object with a URL")
        url = _canonical_anthology_url(candidate["url"])
        evidence = by_url.get(url or "", [])
        if evidence:
            candidate["screening_status"] = "prior_screening_log_match"
            candidate["screening_evidence"] = evidence
            depths = {record["screening_depth_status"] for record in evidence}
            if "full_text_screened" in depths:
                depth = "full_text_screened"
            elif "targeted_sections_screened" in depths:
                depth = "targeted_sections_screened"
            elif "metadata_or_abstract_only" in depths:
                depth = "metadata_or_abstract_only"
            else:
                depth = "prior_log_depth_unresolved"
            candidate["screening_depth_status"] = depth
            logged_count += 1
        else:
            candidate["screening_status"] = "pending_title_abstract_screen"
            candidate.pop("screening_evidence", None)
            candidate.pop("screening_depth_status", None)

    frame["screening_reconciliation"] = {
        "method": "exact normalized ACL Anthology URL match against structured literature-screening log records",
        "source_log_pattern": LOG_GLOB,
        "matched_candidate_count": logged_count,
        "candidate_count": len(candidates),
        "depth_statuses": {
            "full_text_screened": "An explicit per-study full-text/PDF read or screening status is present in at least one matched log record.",
            "targeted_sections_screened": "A matched per-study record explicitly says targeted/relevant full-paper sections were checked, with no explicit full-text screening evidence found.",
            "metadata_or_abstract_only": "A matched per-study record explicitly limits review to metadata, an official page, or an abstract, with no deeper evidence found.",
            "prior_log_depth_unresolved": "A URL match exists, but matched per-study records do not establish screening depth.",
        },
        "interpretation_limit": "A log match proves only that the cited study is present in a project screening log. Depth is derived only from explicit fields on matched per-study records, never from log-level methods or counts. This is not a relevance decision or a systematic-review inclusion count.",
    }
    return frame


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--sources-dir", type=Path, default=Path("sources"))
    parser.add_argument("--output", type=Path, help="defaults to updating --candidates in place")
    parser.add_argument("--force", action="store_true", help="required when output already exists")
    args = parser.parse_args(argv)

    output = args.output or args.candidates
    if output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        result = reconcile(args.candidates, args.sources_dir)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result["screening_reconciliation"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
