"""Validate links from adjudicated gloss candidates to OEWN hypernym proofs.

This validates identity, sense mapping, resource-pair, report-hash, and replay
bindings. It does not judge whether a gloss entails the mapped relation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from src.logic.annotation_validator import load_jsonl
from src.logic.claim_review_validator import (
    validate_against_candidate_manifest,
    validate_dataset as validate_claim_review_dataset,
)


LINK_SCHEMA_VERSION = "gloss-oewn-relation-link/0.1"
VALIDATOR_VERSION = "gloss-oewn-relation-link-validator/0.3"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SOURCE_FIELDS = {"resource", "release", "sense_id", "gloss_sha256"}
MAPPING_FIELDS = {"status", "span", "ancestor_synset_id", "adjudicator_id", "rationale"}
QUERY_FIELDS = {"relation", "claim_id", "child_synset_id", "ancestor_synset_id"}
MAPPING_STATUSES = {"adjudicated", "ambiguous", "unassessed"}
RESOURCE_STATUSES = {
    "direct_hypernym", "transitive_hypernym", "not_in_hypernym_closure",
    "unknown_missing_synset", "not_a_proper_hypernym", "unsupported_cross_pos",
}
OEWN_RESOURCE_NAMES = {"oewn", "open english wordnet", "open english wordnet 2025 plus"}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_record_sha256(record: dict[str, Any]) -> str:
    payload = json.dumps(
        record, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return _sha256_bytes(payload)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    rows, _, errors = load_jsonl(path)
    if errors:
        raise ValueError(f"invalid {label} JSONL: " + "; ".join(errors[:8]))
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"{label} rows must be JSON objects")
    return rows


def _has_exact_keys(
    value: Any, required: set[str], optional: set[str] | frozenset[str] = frozenset()
) -> bool:
    return isinstance(value, dict) and required <= set(value) and not (set(value) - required - optional)


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _taxonomy_synset_id(value: Any) -> str | None:
    """Normalize the project ``oewn-`` identity prefix to the release ID."""
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.removeprefix("oewn-")
    return normalized if normalized else None


def validate_links(
    links: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    query_rows: list[dict[str, Any]],
    verifier_report: dict[str, Any] | None,
    replay_report: dict[str, Any] | None,
    *,
    candidate_rows_sha256: str,
    candidate_manifest: Any,
    candidate_manifest_sha256: str,
    expected_candidate_manifest_sha256: str,
    query_rows_sha256: str | None,
    verifier_report_sha256: str | None,
    replay_report_sha256: str | None,
    expected_release_name: str,
    expected_release_archive_sha256: str,
) -> dict[str, Any]:
    """Validate candidate-to-taxonomy evidence links without interpreting glosses."""
    errors: list[str] = []
    input_fingerprints = {
        "claim_review_rows_sha256": candidate_rows_sha256,
        "candidate_manifest_sha256": candidate_manifest_sha256,
        "expected_candidate_manifest_sha256": expected_candidate_manifest_sha256,
        "relation_queries_sha256": query_rows_sha256,
        "verifier_report_sha256": verifier_report_sha256,
        "replay_report_sha256": replay_report_sha256,
        "expected_release_name": expected_release_name,
        "expected_release_archive_sha256": expected_release_archive_sha256,
    }
    if not links:
        errors.append("bridge link JSONL must contain at least one row")
    if not _valid_sha256(expected_release_archive_sha256):
        errors.append("expected_release_archive_sha256 must be lowercase SHA-256")
    if not isinstance(expected_release_name, str) or not expected_release_name.strip():
        errors.append("expected_release_name must be a non-empty string")
    if not _valid_sha256(expected_candidate_manifest_sha256):
        errors.append("expected_candidate_manifest_sha256 must be lowercase SHA-256")
    if candidate_manifest_sha256 != expected_candidate_manifest_sha256:
        errors.append("candidate manifest file hash does not match the externally pinned value")

    review_errors = validate_claim_review_dataset(candidate_rows)
    errors.extend(f"claim-review rows: {error}" for error in review_errors[:20])
    errors.extend(
        f"candidate manifest: {error}"
        for error in validate_against_candidate_manifest(candidate_rows, candidate_manifest)[:20]
    )
    if review_errors:
        return {
            "schema_version": "gloss-oewn-relation-link-validation/0.2",
            "validator_version": VALIDATOR_VERSION,
            "valid": False,
            "errors": errors,
            "inputs": input_fingerprints,
        }
    candidate_by_id: dict[str, dict[str, Any]] = {}
    for row in candidate_rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            if candidate_id in candidate_by_id:
                errors.append(f"duplicate candidate-review candidate_id {candidate_id!r}")
            candidate_by_id[candidate_id] = row

    query_by_id: dict[str, dict[str, Any]] = {}
    for index, query in enumerate(query_rows):
        label = f"query_rows[{index}]"
        if not _has_exact_keys(query, {"claim_id", "child_synset_id", "ancestor_synset_id"}):
            errors.append(f"{label} must contain exactly claim_id, child_synset_id, ancestor_synset_id")
            continue
        claim_id = query.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id.strip():
            errors.append(f"{label}.claim_id must be a non-empty string")
            continue
        if claim_id in query_by_id:
            errors.append(f"duplicate relation query claim_id {claim_id!r}")
        query_by_id[claim_id] = query

    mapped_candidate_ids: set[str] = set()
    seen_link_ids: set[str] = set()
    mapping_counts: Counter[str] = Counter()
    relation_counts: Counter[str] = Counter()
    link_results: list[dict[str, Any]] = []

    for index, link in enumerate(links):
        label = f"links[{index}]"
        if not _has_exact_keys(link, {"schema_version", "candidate_id", "candidate_record_sha256", "source", "genus_mapping"},
                               {"resource_query", "verifier_report_sha256", "replay_report_sha256"}):
            errors.append(f"{label} has missing or unsupported fields")
            continue
        if link.get("schema_version") != LINK_SCHEMA_VERSION:
            errors.append(f"{label}.schema_version must be {LINK_SCHEMA_VERSION!r}")
        candidate_id = link.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            errors.append(f"{label}.candidate_id must be a non-empty string")
            continue
        if candidate_id in seen_link_ids:
            errors.append(f"duplicate bridge candidate_id {candidate_id!r}")
        seen_link_ids.add(candidate_id)
        candidate = candidate_by_id.get(candidate_id)
        if candidate is None:
            errors.append(f"{label} candidate_id is absent from the claim-review sidecar")
            continue
        try:
            candidate_hash = canonical_record_sha256(candidate)
        except (TypeError, ValueError) as exc:
            errors.append(f"{label} cannot canonicalize candidate-review row: {exc}")
            continue
        if link.get("candidate_record_sha256") != candidate_hash:
            errors.append(f"{label}.candidate_record_sha256 does not match the exact claim-review row")

        source = link.get("source")
        if not _has_exact_keys(source, SOURCE_FIELDS):
            errors.append(f"{label}.source must contain exactly {sorted(SOURCE_FIELDS)}")
        else:
            candidate_source = candidate.get("source", {})
            if not isinstance(candidate_source, dict):
                errors.append(f"{label} candidate source is malformed")
                candidate_source = {}
            expected_source = {
                "resource": candidate_source.get("resource"),
                "release": candidate_source.get("release"),
                "sense_id": candidate_source.get("sense_id"),
                "gloss_sha256": candidate_source.get("gloss_sha256"),
            }
            if source != expected_source:
                errors.append(f"{label}.source does not match the claim-review row")
            resource_name = source.get("resource")
            if not isinstance(resource_name, str) or resource_name.casefold() not in OEWN_RESOURCE_NAMES:
                errors.append(f"{label}.source.resource is not an OEWN resource identifier")
            if source.get("release") != expected_release_name:
                errors.append(f"{label}.source.release does not match the externally pinned release name")
            if source.get("gloss_sha256") != candidate.get("source", {}).get("gloss_sha256"):
                errors.append(f"{label}.source.gloss_sha256 does not match the claim-review row")

        mapping = link.get("genus_mapping")
        if not isinstance(mapping, dict) or set(mapping) - MAPPING_FIELDS or "status" not in mapping:
            errors.append(f"{label}.genus_mapping has missing or unsupported fields")
            continue
        mapping_status = mapping.get("status")
        if not isinstance(mapping_status, str) or mapping_status not in MAPPING_STATUSES:
            errors.append(f"{label}.genus_mapping.status must be one of {sorted(MAPPING_STATUSES)}")
            continue
        mapping_counts[mapping_status] += 1
        premise = candidate.get("premise")
        span = mapping.get("span")
        if span is not None:
            if (not isinstance(span, dict) or set(span) != {"start", "end"}
                    or type(span.get("start")) is not int or type(span.get("end")) is not int
                    or not isinstance(premise, str)
                    or span["start"] < 0 or span["end"] <= span["start"] or span["end"] > len(premise)):
                errors.append(f"{label}.genus_mapping.span must satisfy 0 <= start < end <= raw gloss length")
            elif not premise[span["start"]:span["end"]].strip():
                errors.append(f"{label}.genus_mapping.span must select non-whitespace gloss text")
        if mapping_status == "adjudicated":
            if span is None:
                errors.append(f"{label}: adjudicated genus mapping requires an exact gloss span")
            if not isinstance(mapping.get("ancestor_synset_id"), str) or not mapping["ancestor_synset_id"].strip():
                errors.append(f"{label}: adjudicated genus mapping requires ancestor_synset_id")
            if not isinstance(mapping.get("adjudicator_id"), str) or not mapping["adjudicator_id"].strip():
                errors.append(f"{label}: adjudicated genus mapping requires adjudicator_id")
            if not isinstance(mapping.get("rationale"), str) or not mapping["rationale"].strip():
                errors.append(f"{label}: adjudicated genus mapping requires rationale")
            if (link.get("resource_query") is None
                    or not _valid_sha256(link.get("verifier_report_sha256"))
                    or not _valid_sha256(link.get("replay_report_sha256"))):
                errors.append(f"{label}: adjudicated mapping requires resource_query and producer/replay report hashes")
            query = link.get("resource_query")
            if not _has_exact_keys(query, QUERY_FIELDS):
                errors.append(f"{label}.resource_query must contain exactly {sorted(QUERY_FIELDS)}")
            else:
                expected_pair = {
                    "relation": "hypernym",
                    "claim_id": candidate_id,
                    "child_synset_id": _taxonomy_synset_id(candidate.get("source", {}).get("sense_id")),
                    "ancestor_synset_id": _taxonomy_synset_id(mapping.get("ancestor_synset_id")),
                }
                if query != expected_pair:
                    errors.append(f"{label}.resource_query does not match candidate sense and adjudicated genus mapping")
                query_row = query_by_id.get(candidate_id)
                expected_query_row = {
                    "claim_id": candidate_id,
                    "child_synset_id": expected_pair["child_synset_id"],
                    "ancestor_synset_id": expected_pair["ancestor_synset_id"],
                }
                if query_row is not None and query_row != expected_query_row:
                    errors.append(
                        f"{label}.resource_query does not match the supplied relation query row"
                    )
                if candidate_id in mapped_candidate_ids:
                    errors.append(f"candidate_id {candidate_id!r} has more than one adjudicated mapping")
                mapped_candidate_ids.add(candidate_id)
        else:
            if "resource_query" in link or "verifier_report_sha256" in link or "replay_report_sha256" in link:
                errors.append(f"{label}: non-adjudicated mapping cannot carry a resource proof query")
            if "ancestor_synset_id" in mapping:
                errors.append(f"{label}: non-adjudicated mapping cannot select one ancestor synset")
            if not isinstance(mapping.get("rationale"), str) or not mapping["rationale"].strip():
                errors.append(f"{label}: ambiguous/unassessed mapping requires rationale")

        link_results.append({
            "candidate_id": candidate_id,
            "mapping_status": mapping_status,
            "resource_relation_status": None,
        })

    if seen_link_ids != set(candidate_by_id):
        errors.append(
            "bridge candidate set must exactly equal the claim-review candidate set; "
            f"missing={sorted(set(candidate_by_id) - seen_link_ids)[:8]}, "
            f"extra={sorted(seen_link_ids - set(candidate_by_id))[:8]}"
        )

    if mapped_candidate_ids != set(query_by_id):
        errors.append(
            "relation query candidate set must exactly equal adjudicated genus-mapping candidate set; "
            f"missing={sorted(mapped_candidate_ids - set(query_by_id))[:8]}, "
            f"extra={sorted(set(query_by_id) - mapped_candidate_ids)[:8]}"
        )

    adjudicated_links = {
        link.get("candidate_id"): link for link in links
        if isinstance(link, dict)
        and isinstance(link.get("genus_mapping"), dict)
        and link["genus_mapping"].get("status") == "adjudicated"
    }
    if adjudicated_links:
        if not all((verifier_report, replay_report, query_rows_sha256,
                    verifier_report_sha256, replay_report_sha256)):
            errors.append("adjudicated mappings require query, verifier, and replay artifacts")
        if verifier_report is not None and replay_report is not None:
            inputs = verifier_report.get("inputs")
            if verifier_report.get("verifier_version") != "oewn-hypernym-closure-verifier/2":
                errors.append("unsupported OEWN verifier version")
            if not isinstance(inputs, dict):
                errors.append("verifier report inputs must be an object")
                inputs = {}
            if inputs.get("release_name") != expected_release_name:
                errors.append("verifier report release_name does not match expected release")
            if inputs.get("archive_sha256") != expected_release_archive_sha256:
                errors.append("verifier report archive hash does not match the pinned release hash")
            if inputs.get("claims_sha256") != query_rows_sha256:
                errors.append("verifier report claims hash does not match the supplied query JSONL")
            if verifier_report_sha256 is not None:
                for link in adjudicated_links.values():
                    if link.get("verifier_report_sha256") != verifier_report_sha256:
                        errors.append("bridge row verifier_report_sha256 does not match supplied report bytes")
                        break
            if replay_report_sha256 is not None:
                for link in adjudicated_links.values():
                    if link.get("replay_report_sha256") != replay_report_sha256:
                        errors.append("bridge row replay_report_sha256 does not match supplied replay bytes")
                        break
            if replay_report.get("replay_version") != "oewn-hypernym-path-replay/3":
                errors.append("unsupported independent replay version")
            if replay_report.get("claims_sha256") != query_rows_sha256:
                errors.append("replay report claims hash does not match supplied relation query JSONL")
            if replay_report.get("producer_report_sha256") != verifier_report_sha256:
                errors.append("replay report producer hash does not match supplied verifier report bytes")
            if replay_report.get("valid") is not True or replay_report.get("errors") != []:
                errors.append("independent replay report is not valid with an empty error list")
            if replay_report.get("release_archive_sha256") != expected_release_archive_sha256:
                errors.append("replay report release hash does not match the pinned release hash")
            if replay_report.get("claim_count") != len(query_rows):
                errors.append("replay report claim_count does not match supplied relation queries")
            if replay_report.get("claim_count") != verifier_report.get("claim_count"):
                errors.append("replay and producer claim_count differ")
            if replay_report.get("status_counts") != verifier_report.get("status_counts"):
                errors.append("replay and producer status_counts differ")
            producer_results = verifier_report.get("results")
            if not isinstance(producer_results, list):
                errors.append("verifier report results must be a list")
                producer_results = []
            producer_by_id: dict[str, dict[str, Any]] = {}
            for result in producer_results:
                if not isinstance(result, dict) or not isinstance(result.get("claim_id"), str):
                    errors.append("verifier report contains a malformed result row")
                    continue
                if result["claim_id"] in producer_by_id:
                    errors.append(f"verifier report has duplicate claim_id {result['claim_id']!r}")
                producer_by_id[result["claim_id"]] = result
            if verifier_report.get("claim_count") != len(query_rows):
                errors.append("verifier report claim_count does not match supplied relation queries")
            if set(producer_by_id) != mapped_candidate_ids:
                errors.append("verifier result candidate IDs do not exactly match adjudicated bridge rows")
            observed_status_counts = Counter(
                result.get("status") for result in producer_results
                if isinstance(result, dict) and isinstance(result.get("status"), str)
            )
            if dict(sorted(observed_status_counts.items())) != verifier_report.get("status_counts"):
                errors.append("verifier report status_counts do not match its result rows")
            positive_count = sum(
                status in {"direct_hypernym", "transitive_hypernym"}
                for status in observed_status_counts.elements()
            )
            if replay_report.get("replayed_positive_paths") != positive_count:
                errors.append("replay positive path count does not match producer result rows")
            for candidate_id, link in adjudicated_links.items():
                result = producer_by_id.get(candidate_id)
                query = link.get("resource_query")
                if result is None or not isinstance(query, dict):
                    continue
                if (result.get("child_synset_id") != query.get("child_synset_id")
                        or result.get("ancestor_synset_id") != query.get("ancestor_synset_id")):
                    errors.append(f"verifier result pair does not match bridge row for {candidate_id!r}")
                    continue
                status = result.get("status")
                if not isinstance(status, str) or status not in RESOURCE_STATUSES:
                    errors.append(f"verifier result has unsupported resource status for {candidate_id!r}")
                    continue
                relation_counts[status] += 1
                for summary in link_results:
                    if summary["candidate_id"] == candidate_id:
                        summary["resource_relation_status"] = status
                        break
    elif query_rows or verifier_report is not None or replay_report is not None:
        errors.append("query/producer/replay artifacts supplied but no bridge row has an adjudicated mapping")

    if errors:
        return {
            "schema_version": "gloss-oewn-relation-link-validation/0.2",
            "validator_version": VALIDATOR_VERSION,
            "valid": False,
            "errors": errors,
            "inputs": input_fingerprints,
        }
    return {
        "schema_version": "gloss-oewn-relation-link-validation/0.2",
        "validator_version": VALIDATOR_VERSION,
        "valid": True,
        "link_count": len(links),
        "mapping_status_counts": dict(sorted(mapping_counts.items())),
        "resource_relation_status_counts": dict(sorted(relation_counts.items())),
        "inputs": input_fingerprints,
        "results": link_results,
        "interpretation_limit": (
            "Validation checks cross-artifact identity and a separately replayed OEWN resource relation only. "
            "It does not validate the genus mapping or imply that the gloss supports the relation."
        ),
    }


def run(
    links_path: Path,
    claim_review_path: Path,
    candidate_manifest_path: Path,
    *,
    expected_candidate_manifest_sha256: str,
    expected_release_name: str,
    expected_release_archive_sha256: str,
    query_path: Path | None = None,
    verifier_report_path: Path | None = None,
    replay_report_path: Path | None = None,
) -> dict[str, Any]:
    links = _read_jsonl(links_path, "bridge link")
    candidate_rows = _read_jsonl(claim_review_path, "claim-review")
    candidate_manifest_bytes = candidate_manifest_path.read_bytes()
    candidate_manifest_sha256 = hashlib.sha256(candidate_manifest_bytes).hexdigest()
    candidate_manifest = json.loads(candidate_manifest_bytes.decode("utf-8"))
    query_rows = _read_jsonl(query_path, "relation query") if query_path else []
    verifier_report = _read_json(verifier_report_path, "verifier report") if verifier_report_path else None
    replay_report = _read_json(replay_report_path, "replay report") if replay_report_path else None
    supplied = (query_path is not None, verifier_report_path is not None, replay_report_path is not None)
    adjudicated = any(
        isinstance(row.get("genus_mapping"), dict)
        and row["genus_mapping"].get("status") == "adjudicated"
        for row in links
    )
    if adjudicated and not all(supplied):
        raise ValueError("adjudicated mappings require --queries, --verifier-report, and --replay-report")
    if not adjudicated and any(supplied):
        raise ValueError("relation proof artifacts are only valid when at least one mapping is adjudicated")
    query_sha = hashlib.sha256(query_path.read_bytes()).hexdigest() if query_path else None
    verifier_sha = hashlib.sha256(verifier_report_path.read_bytes()).hexdigest() if verifier_report_path else None
    replay_sha = hashlib.sha256(replay_report_path.read_bytes()).hexdigest() if replay_report_path else None
    result = validate_links(
        links, candidate_rows, query_rows, verifier_report, replay_report,
        candidate_rows_sha256=hashlib.sha256(claim_review_path.read_bytes()).hexdigest(),
        candidate_manifest=candidate_manifest,
        candidate_manifest_sha256=candidate_manifest_sha256,
        expected_candidate_manifest_sha256=expected_candidate_manifest_sha256,
        query_rows_sha256=query_sha,
        verifier_report_sha256=verifier_sha,
        replay_report_sha256=replay_sha,
        expected_release_name=expected_release_name,
        expected_release_archive_sha256=expected_release_archive_sha256,
    )
    result.setdefault("inputs", {})["links_sha256"] = hashlib.sha256(links_path.read_bytes()).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("links", type=Path)
    parser.add_argument("claim_review", type=Path)
    parser.add_argument("candidate_manifest", type=Path)
    parser.add_argument("--candidate-manifest-sha256", required=True)
    parser.add_argument("--expected-release-name", required=True)
    parser.add_argument("--expected-release-archive-sha256", required=True)
    parser.add_argument("--queries", type=Path)
    parser.add_argument("--verifier-report", type=Path)
    parser.add_argument("--replay-report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        result = run(
            args.links, args.claim_review, args.candidate_manifest,
            expected_candidate_manifest_sha256=args.candidate_manifest_sha256,
            expected_release_name=args.expected_release_name,
            expected_release_archive_sha256=args.expected_release_archive_sha256,
            query_path=args.queries,
            verifier_report_path=args.verifier_report,
            replay_report_path=args.replay_report,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Validated {result.get('link_count', 0)} gloss–OEWN relation link(s); valid={result['valid']}")
    if not result["valid"]:
        for error in result["errors"][:20]:
            print(f"- {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
