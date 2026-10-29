"""Build a reproducible ACL Anthology candidate frame from its official export.

This is a bounded discovery aid for the project's scoping review, not an
automatic relevance judgment or a complete cross-database systematic review.
It downloads the official BibTeX+abstract export, filters records dated
2016--2026 by fixed English title/abstract term families, and retains the
resulting candidates with their bibliographic source fields. It does not
enforce a language field or make title/abstract relevance decisions.
Runs can reuse a pinned compressed export and exclude query families to make
same-export ablations reproducible. BibTeX records are parsed incrementally,
so decompressed export text and all parsed records are not retained in memory.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
from io import BytesIO
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


EXPORT_URL = "https://aclanthology.org/anthology+abstracts.bib.gz"
MIN_YEAR = 2016  # ACL Anthology materials from 2016 onward use CC BY 4.0.
MAX_YEAR = 2026
MAX_COMPRESSED_BYTES = 128 * 1024 * 1024
DEFAULT_OUTPUT = Path("sources/acl_anthology_candidates_2026-10-05.json")
ENTRY_TYPES = {"inproceedings", "article", "incollection", "proceedings"}

QUERY_TERMS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "wordnet_gloss_lexical_relations": (
        ("wordnet", "word net", "glosstag"),
        ("gloss", "definition", "hypernym", "lexical relation", "semantic relation"),
    ),
    "definition_conditioned_lexical_prediction": (
        ("wordnet", "word net", "dictionary definition", "gloss", "definition"),
        (
            "inverse definition modelling",
            "inverse definition modeling",
            "definition-to-term",
            "definition to term",
            "definition-to-word",
            "hypernym prediction",
            "synonym prediction",
            "gloss-based lexical prediction",
        ),
    ),
    "definition_to_formal_logic": (
        ("definition", "gloss", "wordnet", "dictionary", "natural language"),
        ("autoformaliz", "formaliz", "formalisation", "first-order logic", "logical form", "horn clause", "theorem prover"),
    ),
    "nli_logic_proof_verification": (
        ("natural language inference", "nli", "entailment"),
        ("first-order logic", "formaliz", "proof", "prover", "verification", "verifier"),
    ),
    "source_grounded_entailment": (
        ("natural language inference", "textual entailment", "entailment"),
        ("attributable", "source", "faithfulness", "factual consistency", "factual inconsistenc", "hallucination", "prefix"),
    ),
    "graph_rule_provenance": (
        ("knowledge graph", "hypergraph", "hyperedge", "datalog", "horn"),
        ("provenance", "proof", "rule", "reasoning", "explanation"),
    ),
    "long_context_evidence": (
        ("long-context", "long context", "long-context reasoning", "extended context"),
        ("evidence retrieval", "evidence identification", "evidence attribution", "multi-evidence", "multi evidence", "distractor"),
    ),
    "multi_evidence_selection": (
        ("multi-evidence", "multi evidence", "evidence set", "evidence sentence", "evidence tree", "evidence selection"),
        ("retrieval", "reasoning", "search", "selection", "support", "contradiction"),
    ),
    "evidence_evaluation_attribution": (
        ("evidence evaluation", "evidence attribution", "source attribution", "span-based evidence", "evidence quality"),
        ("benchmark", "metric", "support", "retrieval", "human judgment", "faithfulness"),
    ),
}


def _bibtex_entries(lines: Iterable[str]) -> Iterator[tuple[str, str]]:
    """Yield entries incrementally, retaining only the current BibTeX record."""
    header = re.compile(r"@\s*([A-Za-z0-9_:-]+)\s*([{(])")
    entry_type = ""
    opening = ""
    closing = ""
    depth = 0
    in_quote = False
    escaped = False
    body_parts: list[str] = []
    active = False

    for line in lines:
        position = 0
        while position < len(line):
            if not active:
                start = line.find("@", position)
                if start < 0:
                    break
                match = header.match(line, start)
                if match is None:
                    position = start + 1
                    continue
                entry_type = match.group(1).casefold()
                opening = match.group(2)
                closing = "}" if opening == "{" else ")"
                depth = 1
                in_quote = False
                escaped = False
                body_parts = []
                active = True
                position = match.end()

            body_start = position
            while position < len(line):
                char = line[position]
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_quote = not in_quote
                elif not in_quote:
                    if char == opening:
                        depth += 1
                    elif char == closing:
                        depth -= 1
                        if depth == 0:
                            body_parts.append(line[body_start:position])
                            yield entry_type, "".join(body_parts)
                            active = False
                            position += 1
                            break
                position += 1

            if active:
                body_parts.append(line[body_start:])
                break

    if active:
        raise ValueError("unterminated BibTeX entry in ACL Anthology export")


def _split_top_level(value: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    in_quote = False
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            in_quote = not in_quote
        elif not in_quote:
            if char == "{":
                depth += 1
            elif char == "}" and depth:
                depth -= 1
            elif char == delimiter and depth == 0:
                parts.append(value[start:index])
                start = index + 1
    parts.append(value[start:])
    return parts


def _field_map(body: str) -> tuple[str, dict[str, str]]:
    pieces = _split_top_level(body, ",")
    key = pieces[0].strip()
    fields: dict[str, str] = {}
    for piece in pieces[1:]:
        pair = _split_top_level(piece, "=")
        if len(pair) < 2:
            continue
        name = pair[0].strip().casefold()
        raw = "=".join(pair[1:]).strip()
        if raw.startswith("{") and raw.endswith("}"):
            raw = raw[1:-1]
        elif raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        raw = re.sub(r"\s+", " ", raw)
        fields[name] = raw
    return key, fields


def _year(fields: dict[str, str]) -> int | None:
    match = re.search(r"\b(19|20)\d{2}\b", fields.get("year", ""))
    return int(match.group(0)) if match else None


def _matches(text: str, query: tuple[tuple[str, ...], tuple[str, ...]]) -> bool:
    left, right = query
    return any(term in text for term in left) and any(term in text for term in right)


def _download_export() -> bytes:
    request = Request(EXPORT_URL, headers={"User-Agent": "hypergraph-analysis-exploration/1.0 (literature search)"})
    with urlopen(request, timeout=120) as response:
        compressed = response.read(MAX_COMPRESSED_BYTES + 1)
    if len(compressed) > MAX_COMPRESSED_BYTES:
        raise ValueError("ACL Anthology export exceeds the 128 MiB safety limit")
    return compressed


def run_search(
    compressed_export: bytes | None = None,
    query_terms: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = QUERY_TERMS,
    export_source: str = "official_http_download",
) -> dict[str, object]:
    compressed = compressed_export if compressed_export is not None else _download_export()
    if len(compressed) > MAX_COMPRESSED_BYTES:
        raise ValueError("ACL Anthology export exceeds the 128 MiB safety limit")
    compressed_sha256 = hashlib.sha256(compressed).hexdigest()
    export_content_hasher = hashlib.sha256()

    def decoded_export_lines() -> Iterator[str]:
        with gzip.GzipFile(fileobj=BytesIO(compressed), mode="rb") as export_stream:
            for raw_line in export_stream:
                export_content_hasher.update(raw_line)
                yield raw_line.decode("utf-8")

    counts = {query_id: 0 for query_id in query_terms}
    candidates: dict[str, dict[str, object]] = {}
    bibtex_entry_count = 0
    for entry_type, body in _bibtex_entries(decoded_export_lines()):
        bibtex_entry_count += 1
        if entry_type not in ENTRY_TYPES:
            continue
        key, fields = _field_map(body)
        year = _year(fields)
        if not key or year is None or not MIN_YEAR <= year <= MAX_YEAR:
            continue
        title = fields.get("title", "")
        abstract = fields.get("abstract", "")
        searchable = f"{title} {abstract}".casefold()
        matched = [name for name, terms in query_terms.items() if _matches(searchable, terms)]
        if not matched:
            continue
        for name in matched:
            counts[name] += 1
        candidates[key] = {
            "anthology_id": key,
            "year": year,
            "title": title,
            "authors": fields.get("author"),
            "venue": fields.get("booktitle") or fields.get("journal"),
            "doi": fields.get("doi"),
            "url": fields.get("url") or f"https://aclanthology.org/{key}/",
            "abstract": abstract,
            "matched_query_families": matched,
            "screening_status": "pending_title_abstract_screen",
        }

    export_content_sha256 = export_content_hasher.hexdigest()
    return {
        "schema_version": "acl-anthology-related-work-candidates/1",
        "searched_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds"),
        "database": "ACL Anthology official BibTeX+abstract export",
        "export_url": EXPORT_URL,
        "export_source": export_source,
        "export_compressed_sha256": compressed_sha256,
        "export_content_sha256": export_content_sha256,
        "date_window": {"from_year": MIN_YEAR, "through_year": MAX_YEAR},
        "bibtex_entry_count_all_types": bibtex_entry_count,
        "query_families": {
            name: {"all_of_any_terms": list(left), "and_all_of_any_terms": list(right), "pre_dedup_match_count": counts[name]}
            for name, (left, right) in query_terms.items()
        },
        "unique_candidate_count": len(candidates),
        "candidates": sorted(candidates.values(), key=lambda row: (row["year"], str(row["title"]).casefold(), row["anthology_id"])),
        "interpretation_limit": "Keyword candidate frame only. Phrase matching is not semantic screening; duplicate concepts can appear under different Anthology IDs; venue tracks require manual verification. This export does not represent other databases and does not establish recall, relevance, or novelty.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--export-file", type=Path, help="reuse a previously saved official compressed BibTeX export")
    parser.add_argument("--save-export-copy", type=Path, help="save the exact compressed export bytes used by this run")
    parser.add_argument("--exclude-query-family", action="append", default=[], choices=sorted(QUERY_TERMS), help="omit a query family; may be repeated for same-export ablation")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    if args.save_export_copy and args.save_export_copy.exists() and not args.force:
        parser.error("export copy already exists; pass --force to replace it")
    try:
        compressed = args.export_file.read_bytes() if args.export_file else _download_export()
        if len(compressed) > MAX_COMPRESSED_BYTES:
            raise ValueError("ACL Anthology export exceeds the 128 MiB safety limit")
        if args.save_export_copy:
            args.save_export_copy.parent.mkdir(parents=True, exist_ok=True)
            args.save_export_copy.write_bytes(compressed)
        selected_terms = {name: terms for name, terms in QUERY_TERMS.items() if name not in args.exclude_query_family}
        report = run_search(
            compressed_export=compressed,
            query_terms=selected_terms,
            export_source=str(args.export_file) if args.export_file else "official_http_download",
        )
    except (OSError, EOFError, UnicodeError, ValueError) as exc:
        parser.error(f"ACL Anthology search failed: {exc}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ACL Anthology candidate export: {args.output}")
    print(f"Compressed export SHA-256: {report['export_compressed_sha256']}")
    for query_id, query in report["query_families"].items():
        print(f"{query_id}: {query['pre_dedup_match_count']} matches")
    print(f"Unique candidates: {report['unique_candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
