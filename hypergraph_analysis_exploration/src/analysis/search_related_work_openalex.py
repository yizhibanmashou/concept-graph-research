"""Reproduce a bounded OpenAlex title/abstract search for recent related work.

This is one discovery channel in the project's scoping review, not a complete
systematic review. The exported candidate set is deliberately screened by a
human after retrieval; OpenAlex venue and type metadata require verification
against the publisher or proceedings record before citation.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://api.openalex.org/works"
DATE_FROM = "2024-01-01"
DATE_TO = "2026-10-04"
PER_PAGE = 100
QUERIES = (
    ("wordnet_gloss", "WordNet gloss"),
    ("wordnet_hypernym", "WordNet hypernym"),
    ("dictionary_gloss_relation", "dictionary gloss lexical relation"),
    ("nl_fol_verification", "natural language first-order logic verification"),
    ("definition_fol_prover", "definition first-order logic prover"),
    ("semantic_faithfulness_verification", "semantic faithfulness logical verification"),
    ("kg_provenance_proof", "knowledge graph provenance proof"),
    ("hypergraph_proof_provenance", "hypergraph proof provenance"),
)
SELECT_FIELDS = ",".join((
    "id", "doi", "title", "publication_date", "type", "primary_location",
    "authorships", "abstract_inverted_index",
))


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    if not isinstance(inverted_index, dict):
        return None
    tokens: dict[int, str] = {}
    for token, positions in inverted_index.items():
        if not isinstance(token, str) or not isinstance(positions, list):
            continue
        for position in positions:
            if isinstance(position, int) and position >= 0:
                tokens[position] = token
    return " ".join(tokens[index] for index in range(max(tokens) + 1)) if tokens else None


def _normalized_title(title: str) -> str:
    normalized = unicodedata.normalize("NFKC", title).casefold()
    return " ".join(re.findall(r"[\w]+", normalized))


def _doi_key(doi: str | None) -> str | None:
    if not doi:
        return None
    key = doi.casefold().strip()
    key = re.sub(r"^https?://(dx\.)?doi\.org/", "", key)
    return key or None


def merge_query_results(query_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for run in query_runs:
        for work in run.get("results", []):
            doi_key = _doi_key(work.get("doi"))
            title_key = _normalized_title(work.get("title") or "")
            year = str(work.get("publication_date") or "")[:4]
            identity = doi_key or f"title-year:{title_key}:{year}"
            if not identity or identity.endswith(":"):
                identity = work.get("id") or f"unidentified:{len(merged)}"
            if identity not in merged:
                primary = work.get("primary_location") or {}
                source = primary.get("source") or {}
                authorships = work.get("authorships") or []
                merged[identity] = {
                    "openalex_id": work.get("id"),
                    "doi": work.get("doi"),
                    "title": work.get("title"),
                    "publication_date": work.get("publication_date"),
                    "type": work.get("type"),
                    "venue_metadata": source.get("display_name"),
                    "landing_page_metadata": primary.get("landing_page_url"),
                    "authors_metadata": [
                        entry.get("author", {}).get("display_name")
                        for entry in authorships if isinstance(entry, dict)
                        and isinstance(entry.get("author"), dict)
                    ],
                    "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
                    "matched_queries": [],
                }
            if run["query_id"] not in merged[identity]["matched_queries"]:
                merged[identity]["matched_queries"].append(run["query_id"])
    return sorted(merged.values(), key=lambda work: (
        work.get("publication_date") or "", _normalized_title(work.get("title") or ""),
    ))


def _request_page(query: str, page: int) -> dict[str, Any]:
    params = {
        "search.title_and_abstract": query,
        "filter": f"from_publication_date:{DATE_FROM},to_publication_date:{DATE_TO},type:conference-paper",
        "per-page": PER_PAGE,
        "page": page,
        "select": SELECT_FIELDS,
    }
    request = Request(
        f"{API_BASE}?{urlencode(params)}",
        headers={"User-Agent": "hypergraph-analysis-exploration/1.0 (research literature search)"},
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def run_search(*, pause_seconds: float = 0.15) -> dict[str, Any]:
    query_runs: list[dict[str, Any]] = []
    for query_id, query in QUERIES:
        first = _request_page(query, 1)
        results = list(first.get("results", []))
        expected_count = int(first.get("meta", {}).get("count", len(results)))
        pages = (expected_count + PER_PAGE - 1) // PER_PAGE
        for page in range(2, pages + 1):
            if pause_seconds:
                time.sleep(pause_seconds)
            payload = _request_page(query, page)
            results.extend(payload.get("results", []))
        query_runs.append({
            "query_id": query_id,
            "query": query,
            "search_field": "title_and_abstract",
            "database_result_count": expected_count,
            "retrieved_result_count": len(results),
            "results": results,
        })
        if pause_seconds:
            time.sleep(pause_seconds)
    return {
        "schema_version": "openalex-related-work-search/1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "database": "OpenAlex Works API",
        "api_endpoint": API_BASE,
        "date_window": {"from": DATE_FROM, "through": DATE_TO},
        "filter": {"type": "conference-paper"},
        "scope_note": (
            "Discovery export only. Search indexing, conference type and venue metadata can be incomplete; "
            "screening status is assigned separately and venue/publication facts require primary-source verification."
        ),
        "queries": [
            {key: value for key, value in run.items() if key != "results"}
            for run in query_runs
        ],
        "unique_candidate_count": len(merge_query_results(query_runs)),
        "candidates": merge_query_results(query_runs),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("sources/openalex_related_work_2026-10-04.json"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        report = run_search()
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(f"OpenAlex search failed: {exc}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OpenAlex candidate export: {args.output}")
    for query in report["queries"]:
        print(f"{query['query_id']}: {query['database_result_count']} found; {query['retrieved_result_count']} retrieved")
    print(f"Unique candidates: {report['unique_candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
