"""Crosswalk external references in the closest-work matrix to screening logs.

This checks bibliography traceability only. It does not decide whether a work
is relevant, screened, included, or adequately covered by the literature search.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from src.analysis.audit_literature_log_deduplication import (
    DEFAULT_OUTPUT as DEFAULT_DEDUP_INDEX,
    _norm_doi,
    _norm_title,
    _norm_url,
)
from src.analysis.project_paths import PROJECT_ROOT


DEFAULT_MATRIX = PROJECT_ROOT / "docs" / "closest_work_comparison.md"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase251" / "closest_work_log_crosswalk.json"
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
NONPAPER_HOSTS = {"github.com", "gitlab.com", "tripslab.github.io"}
NONPAPER_RESOURCE_PREFIXES = {
    ("wordnet.princeton.edu", "/documentation/"),
    ("wordnetcode.princeton.edu", "/"),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_nonpaper(label: str, url: str) -> bool:
    parsed = urlsplit(url)
    host = (parsed.hostname or "").casefold().removeprefix("www.")
    path = parsed.path.casefold()
    known_resource_url = any(
        host == resource_host and path.startswith(path_prefix)
        for resource_host, path_prefix in NONPAPER_RESOURCE_PREFIXES
    )
    return host in NONPAPER_HOSTS or known_resource_url or any(term in label.casefold() for term in (
        "repository", "project page", "代码", "仓库", "项目页",
    ))


def crosswalk(matrix_path: Path, index_path: Path) -> dict[str, Any]:
    matrix_path, index_path = matrix_path.resolve(), index_path.resolve()
    index = json.loads(index_path.read_text(encoding="utf-8-sig"))
    clusters = index.get("clusters")
    if not isinstance(clusters, list):
        raise ValueError("deduplication index has no clusters list")

    by_url: dict[str, set[str]] = defaultdict(set)
    by_doi: dict[str, set[str]] = defaultdict(set)
    by_title: dict[str, set[str]] = defaultdict(set)
    for cluster in clusters:
        paper_id = cluster.get("paper_id")
        if not isinstance(paper_id, str):
            continue
        for url in cluster.get("urls", []):
            key = _norm_url(url)
            if key:
                by_url[key].add(paper_id)
        for doi in cluster.get("dois", []):
            key = _norm_doi(doi)
            if key:
                by_doi[key].add(paper_id)
        for title in [cluster.get("display_title"), *(r.get("title") for r in cluster.get("records", []))]:
            if isinstance(title, str) and title.strip():
                by_title[_norm_title(title)].add(paper_id)

    references = []
    for line_number, line in enumerate(matrix_path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.startswith("|"):
            continue
        for label, url in LINK_RE.findall(line):
            url_key = _norm_url(url)
            doi_key = _norm_doi(url)
            ids = by_url.get(url_key, set()) if url_key else set()
            method = "normalized_url" if ids else None
            if not ids and doi_key:
                ids = by_doi.get(doi_key, set())
                method = "exact_doi" if ids else None
            if not ids:
                ids = by_title.get(_norm_title(label), set())
                method = "exact_normalized_title" if ids else None
            prefix = _norm_title(label.split("(", 1)[0].strip())
            prefix_candidates = set()
            if not ids and len(prefix) >= 6:
                for normalized_title, paper_ids in by_title.items():
                    if normalized_title.startswith(prefix + " "):
                        prefix_candidates.update(paper_ids)
            references.append({
                "matrix_line": line_number,
                "label": label,
                "url": url,
                "match_status": "matched_to_screening_log" if ids else "no_exact_crosswalk_match",
                "match_method": method,
                "paper_ids": sorted(ids),
                "candidate_title_prefix_paper_ids": sorted(prefix_candidates),
                "nonpaper_resource_candidate": _is_nonpaper(label, url),
            })

    unique_targets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ref in references:
        key = _norm_url(ref["url"]) or ref["url"]
        unique_targets[key].append(ref)
    target_rows = []
    for key, refs in sorted(unique_targets.items()):
        matched_ids = sorted({paper_id for row in refs for paper_id in row["paper_ids"]})
        methods = sorted({row["match_method"] for row in refs if row["match_method"]})
        target_rows.append({
            "target_key": key,
            "labels": sorted({row["label"] for row in refs}),
            "urls": sorted({row["url"] for row in refs}),
            "matrix_lines": sorted({row["matrix_line"] for row in refs}),
            "match_status": "matched_to_screening_log" if matched_ids else "no_exact_crosswalk_match",
            "match_methods": methods,
            "paper_ids": matched_ids,
            "candidate_title_prefix_paper_ids": sorted({
                paper_id for row in refs for paper_id in row["candidate_title_prefix_paper_ids"]
            }),
            "nonpaper_resource_candidate": all(row["nonpaper_resource_candidate"] for row in refs),
        })

    by_method = Counter(row["match_method"] for row in references if row["match_method"])
    unmatched = [row for row in target_rows if row["match_status"] != "matched_to_screening_log"]
    return {
        "audit_version": "closest-work-log-crosswalk/1",
        "inputs": {
            "matrix_sha256": _sha256(matrix_path),
            "dedup_index_sha256": _sha256(index_path),
            "dedup_index_implementation_sha256": index.get("inputs", {}).get("dedup_implementation_sha256"),
            "crosswalk_implementation_sha256": _sha256(Path(__file__).resolve()),
            "matrix_link_occurrences": len(references),
            "distinct_targets": len(target_rows),
        },
        "summary": {
            "matched_link_occurrences": sum(r["match_status"] == "matched_to_screening_log" for r in references),
            "unmatched_link_occurrences": sum(r["match_status"] != "matched_to_screening_log" for r in references),
            "distinct_targets_matched": sum(r["match_status"] == "matched_to_screening_log" for r in target_rows),
            "distinct_targets_unmatched": len(unmatched),
            "unmatched_nonpaper_resource_candidates": sum(r["nonpaper_resource_candidate"] for r in unmatched),
            "unmatched_scholarly_reference_candidates": sum(not r["nonpaper_resource_candidate"] for r in unmatched),
            "unmatched_targets_with_title_prefix_candidates": sum(bool(r["candidate_title_prefix_paper_ids"]) for r in unmatched),
            "occurrence_matches_by_method": dict(sorted(by_method.items())),
        },
        "interpretation_limit": "An exact URL/DOI/title crosswalk establishes only a bibliographic link to a structured project log. An unmatched matrix citation may have been screened under variant metadata or may lack a structured record; it is not evidence that the work was not screened. A match does not establish full-text depth, relevance, inclusion, or systematic-search completeness.",
        "references": references,
        "distinct_targets": target_rows,
        "unmatched_targets_for_manual_review": unmatched,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--index", type=Path, default=DEFAULT_DEDUP_INDEX)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        result = crosswalk(args.matrix, args.index)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), **result["summary"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
