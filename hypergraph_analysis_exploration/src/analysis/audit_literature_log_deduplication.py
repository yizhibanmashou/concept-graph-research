"""Create a conservative, source-traceable deduplication index for literature logs.

Exact DOI and normalized URL matches are preferred. Exact normalized title
matches are used only when their known years and DOI identities do not conflict.
This is a project-log audit, not a literature search or systematic-review count.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from src.analysis.project_paths import PROJECT_ROOT
from src.analysis.reconcile_acl_screening_logs import DEPTH_FIELDS, _depth_from_explicit_fields


DEFAULT_SOURCES = PROJECT_ROOT / "sources"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase250" / "literature_log_dedup_index.json"
LOG_GLOB = "literature_screening_log*.json"
URL_FIELDS = (
    "official_url", "official_record", "official_pdf", "official_page", "url",
    "paper_url", "source_url", "landing_page", "anthology_url", "proceedings_page", "pdf",
)
DOI_RE = re.compile(r"(?:https?://(?:dx\.)?doi\.org/|doi:\s*)?(10\.\d{4,9}/[^\s]+)", re.I)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _norm_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join("".join(ch if ch.isalnum() else " " for ch in value).split())


def _norm_doi(value: str | None) -> str | None:
    if not value:
        return None
    match = DOI_RE.search(value.strip())
    if not match:
        return None
    doi = match.group(1).rstrip(".,;:)]}>").casefold()
    return doi if doi.startswith("10.") else None


def _norm_url(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not re.match(r"^https?://", value, re.I):
        return None
    parsed = urlsplit(value)
    host = (parsed.hostname or "").casefold()
    if host.startswith("www."):
        host = host[4:]
    path = re.sub(r"/+", "/", parsed.path).rstrip("/")
    path = re.sub(r"\.pdf$", "", path, flags=re.I)
    if host in {"doi.org", "dx.doi.org"}:
        return None
    if not host or not path:
        return None
    return urlunsplit(("https", host, path, "", ""))


def _year(value: Any) -> int | None:
    match = re.search(r"\b(19|20)\d{2}\b", str(value)) if value is not None else None
    return int(match.group(0)) if match else None


def _record_urls(item: dict[str, Any]) -> set[str]:
    values = [item]
    for key in ("sources", "links", "identifiers"):
        nested = item.get(key)
        if isinstance(nested, dict):
            values.extend(v for v in nested.values() if isinstance(v, dict))
        elif isinstance(nested, list):
            values.extend(v for v in nested if isinstance(v, dict))
    return {
        url for fields in values for field in URL_FIELDS
        if isinstance(fields.get(field), str)
        if (url := _norm_url(fields[field]))
    }


class DisjointSet:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)


def build_index(sources_dir: Path) -> dict[str, Any]:
    paths = sorted(sources_dir.glob(LOG_GLOB))
    if not paths:
        raise ValueError(f"no logs matching {LOG_GLOB!r} in {sources_dir}")

    records: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        ordinal = 0
        for item in _walk(payload):
            title = item.get("title")
            if not isinstance(title, str) or not title.strip():
                continue
            ordinal += 1
            urls = sorted(_record_urls(item))
            doi_values = [item.get("doi"), *(item.get(k) for k in URL_FIELDS)]
            # A few existing logs embed DOI identifiers in bibliographic prose
            # such as `venue` rather than a dedicated DOI field.
            doi_values.extend(item.get(k) for k in ("venue", "citation", "proceedings", "official_citation"))
            for source in item.get("sources", []) if isinstance(item.get("sources"), list) else []:
                if isinstance(source, dict):
                    doi_values.extend(source.get(k) for k in ("doi", *URL_FIELDS, "citation"))
            dois = {_norm_doi(str(value)) for value in doi_values if value}
            dois.discard(None)
            authors = item.get("authors")
            if isinstance(authors, list):
                authors = [str(a) for a in authors]
            elif not isinstance(authors, str):
                authors = None
            depth_evidence = {
                key: value for key, value in item.items()
                if key.casefold() in DEPTH_FIELDS and isinstance(value, (str, bool))
            }
            records.append({
                "record_id": f"{path.name}#{ordinal}",
                "log": path.name,
                "title": title.strip(),
                "normalized_title": _norm_title(title),
                "year": _year(item.get("year", item.get("publication_year"))),
                "authors": authors,
                "venue": item.get("venue") if isinstance(item.get("venue"), str) else None,
                "dois": sorted(dois),
                "urls": urls,
                "decision": item.get("decision") if isinstance(item.get("decision"), str) else None,
                "screening_depth_status": _depth_from_explicit_fields(depth_evidence),
                "explicit_depth_evidence": depth_evidence,
                "record_fields": sorted(item.keys()),
            })

    dsu = DisjointSet(len(records))
    merge_edges: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    doi_to_ids: dict[str, list[int]] = defaultdict(list)
    url_to_ids: dict[str, list[int]] = defaultdict(list)
    title_to_ids: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(records):
        for doi in row["dois"]:
            doi_to_ids[doi].append(i)
        for url in row["urls"]:
            url_to_ids[url].append(i)
        title_to_ids[row["normalized_title"]].append(i)

    def root_dois(root: int) -> set[str]:
        return {doi for i, row in enumerate(records) if dsu.find(i) == root for doi in row["dois"]}

    def try_merge(a: int, b: int, method: str, key: str) -> bool:
        ra, rb = dsu.find(a), dsu.find(b)
        if ra == rb:
            return True
        da, db = root_dois(ra), root_dois(rb)
        if da and db and da.isdisjoint(db):
            conflicts.append({"left_record_id": records[a]["record_id"],
                              "right_record_id": records[b]["record_id"],
                              "match_method": method, "match_key": key,
                              "reason": "conflicting_doi_identities"})
            return False
        dsu.union(ra, rb)
        merge_edges.append({"left_record_id": records[a]["record_id"],
                            "right_record_id": records[b]["record_id"],
                            "match_method": method, "match_key": key})
        return True

    for method, groups in (("exact_doi", doi_to_ids), ("normalized_url", url_to_ids)):
        for key, ids in sorted(groups.items()):
            for other in ids[1:]:
                try_merge(ids[0], other, method, key)

    # Exact title fallback: require compatible known years, and do not use a
    # title collision to bridge records with distinct DOI identities.
    for title, ids in sorted(title_to_ids.items()):
        for pos, left in enumerate(ids):
            for right in ids[pos + 1:]:
                yl, yr = records[left]["year"], records[right]["year"]
                if yl is not None and yr is not None and yl != yr:
                    conflicts.append({"left_record_id": records[left]["record_id"],
                                      "right_record_id": records[right]["record_id"],
                                      "match_method": "exact_title", "match_key": title,
                                      "reason": "conflicting_known_years"})
                    continue
                try_merge(left, right, "exact_title_and_compatible_year", title)

    clusters: dict[int, list[int]] = defaultdict(list)
    for i in range(len(records)):
        clusters[dsu.find(i)].append(i)
    paper_rows = []
    for number, (_, ids) in enumerate(sorted(clusters.items(), key=lambda pair: min(pair[1])), start=1):
        paper = [records[i] for i in ids]
        methods = sorted({edge["match_method"] for edge in merge_edges
                          if edge["left_record_id"] in {r["record_id"] for r in paper}
                          or edge["right_record_id"] in {r["record_id"] for r in paper}})
        paper_rows.append({
            "paper_id": f"P{number:05d}",
            "display_title": min((r["title"] for r in paper), key=lambda s: (len(s), s.casefold())),
            "years": sorted({r["year"] for r in paper if r["year"] is not None}),
            "dois": sorted({doi for r in paper for doi in r["dois"]}),
            "urls": sorted({url for r in paper for url in r["urls"]}),
            "merge_methods": methods,
            "screening_log_count": len({r["log"] for r in paper}),
            "record_count": len(paper),
            "records": paper,
        })

    depth_counts = Counter(r["screening_depth_status"] or "missing" for r in records)
    return {
        "audit_version": "literature-log-dedup/1",
        "inputs": {
            "source_log_pattern": LOG_GLOB,
            "log_count": len(paths),
            "logs_sha256": hashlib.sha256(json.dumps(
                [(p.name, _sha256(p)) for p in paths], separators=(",", ":"),
            ).encode("utf-8")).hexdigest(),
            "dedup_implementation_sha256": _sha256(Path(__file__).resolve()),
            "depth_classifier_implementation_sha256": _sha256(
                Path(__file__).resolve().with_name("reconcile_acl_screening_logs.py")
            ),
            "record_count": len(records),
        },
        "method": {
            "priority": ["exact DOI", "normalized URL", "exact normalized title with compatible known year"],
            "title_normalization": "Unicode NFKC, casefold, punctuation to spaces, whitespace collapse",
            "url_normalization": "lowercase host, remove www/query/fragment/trailing slash/.pdf, force https",
            "doi_normalization": "casefold DOI extracted from explicit DOI or DOI URL fields",
            "interpretation_limit": "Log records are grouped conservatively for bibliography navigation. Clusters are not relevance decisions, inclusion counts, exhaustive retrieval, or systematic-review evidence. Exact title matches can still conflate versions; inspect source records before citing.",
        },
        "summary": {
            "record_count": len(records),
            "deduplicated_cluster_count": len(paper_rows),
            "records_in_multirecord_clusters": sum(p["record_count"] for p in paper_rows if p["record_count"] > 1),
            "multirecord_cluster_count": sum(p["record_count"] > 1 for p in paper_rows),
            "merge_edge_count": len(merge_edges),
            "conflict_candidate_count": len(conflicts),
            "screening_depth_by_record": dict(sorted(depth_counts.items())),
            "merge_edges_by_method": dict(sorted(Counter(edge["match_method"] for edge in merge_edges).items())),
            "clusters_by_merge_method": dict(sorted(Counter(m for p in paper_rows for m in p["merge_methods"]).items())),
        },
        "clusters": paper_rows,
        "merge_edges": merge_edges,
        "unmerged_conflict_candidates": conflicts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources-dir", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        result = build_index(args.sources_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), **result["summary"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
