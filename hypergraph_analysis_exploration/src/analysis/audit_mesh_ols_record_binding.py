"""Audit privacy-safe binding metadata for MeSH and OLS source evidence.

The report records aggregate field presence and value shapes only. It never
emits glosses, identifiers, source-record paths, full URLs, or source values
other than allow-listed source/version/ontology labels.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.analysis.audit_source_release_metadata import (
    DEFAULT_MAX_SOURCE_BYTES,
    _load_checksums,
    _safe_payload_path,
    _sha256_bytes,
    _source_family,
)
from src.analysis.frozen_bundle_integrity import verify_frozen_bundle_integrity
from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root


SOURCE_FAMILY = "sources/Synset/alternative_or_definition_wsd_frozen"
TRIAGE = PROJECT_ROOT / "outputs" / "phase24" / "source_release_candidate_triage.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "sources" / "mesh_ols_record_binding_audit_2026-10-08_phase221.json"
TARGETS = {"MeSH_2026_descriptors", "EMBL-EBI_OLS"}
SAFE_LABEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:+-]{0,79}$")
MESH_IDENTIFIER = re.compile(r"^[DQ][0-9]{5,10}$", re.I)
SIGNAL = re.compile(r"(?:^|[._-])(id|iri|uri|url|identifier|accession|term|record|source|ontology|version|release|artifact|hash|checksum|license|licence|rights|attribution)(?:$|[._-])", re.I)
OLS_ONTOLOGIES = ("mesh", "ncit", "chebi", "foodon", "doid")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _shape(value: Any) -> str:
    if value is None:
        return "missing_or_null"
    if isinstance(value, str):
        if not value.strip():
            return "blank_string"
        return "canonical_label_string" if SAFE_LABEL.fullmatch(value.strip()) else "noncanonical_string"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, (int, float)):
        return "number"
    return "other_type"


def _source_label(value: Any) -> str:
    """Match the normalized source-label contract used by the Phase24 triage."""
    if not isinstance(value, str) or not value.strip():
        return "missing"
    normalized = re.sub(r"\s+", "_", value.strip())
    return normalized if SAFE_LABEL.fullmatch(normalized) else "noncanonical_or_nonscalar"


def _dimension_label(value: Any) -> str:
    """Normalize aggregate dimensions without retaining noncanonical values."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return "missing"
    if not isinstance(value, str):
        return "noncanonical_or_nonscalar"
    normalized = re.sub(r"\s+", "_", value.strip())
    return normalized if SAFE_LABEL.fullmatch(normalized) else "noncanonical_or_nonscalar"


def _identity_forms(value: Any) -> dict[str, str] | None:
    if not isinstance(value, str) or not value.strip():
        return None
    exact = value.strip()
    terminal = exact.rsplit("/", 1)[-1].rsplit(":", 1)[-1]
    return {
        "exact_trimmed": exact,
        "casefolded_trimmed": exact.casefold(),
        "terminal_token_casefolded": terminal.casefold(),
    }


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value


def _verify_mesh_identifiers_with_nlm(identifiers: set[str]) -> dict[str, Any]:
    endpoint = "https://id.nlm.nih.gov/mesh/{identifier}.json"
    identifiers_sha = hashlib.sha256("\n".join(sorted(identifiers)).encode("utf-8")).hexdigest()
    def fetch(identifier: str) -> tuple[str, int, bytes, bool]:
        request = Request(
            endpoint.format(identifier=identifier),
            headers={"Accept": "application/json", "User-Agent": "hypergraph-analysis-exploration/phase221"},
        )
        try:
            with urlopen(request, timeout=20) as response:
                body = response.read()
                record = json.loads(body.decode("utf-8"))
                echoed = record.get("identifier") == identifier if isinstance(record, dict) else False
                return identifier, response.status, body, echoed
        except HTTPError as exc:
            return identifier, exc.code, b"", False

    try:
        results: list[tuple[str, int, bytes, bool]] = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(fetch, identifier) for identifier in sorted(identifiers)]
            for future in as_completed(futures):
                results.append(future.result())
        results.sort(key=lambda result: result[0])
        status_counts = Counter(str(status) for _, status, _, _ in results)
        echoed_count = sum(echoed for _, _, _, echoed in results)
        response_digest = hashlib.sha256()
        for identifier, status, body, echoed in results:
            response_digest.update(identifier.encode("ascii"))
            response_digest.update(str(status).encode("ascii"))
            response_digest.update(hashlib.sha256(body).digest())
        return {
            "status": "queried" if len(results) == len(identifiers) else "partial",
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "endpoint": endpoint,
            "candidate_identifier_count": len(identifiers),
            "candidate_identifiers_sha256": identifiers_sha,
            "http_status_counts": dict(sorted(status_counts.items())),
            "http_200_identifier_echo_match_count": echoed_count,
            "response_set_sha256": response_digest.hexdigest(),
            "raw_identifiers_query_and_response_emitted": False,
            "interpretation_limit": "Current REST identifier resolution only; not an exact historical release, byte, attribution, or license crosswalk.",
        }
    except (OSError, URLError, UnicodeDecodeError, json.JSONDecodeError, AttributeError, TypeError):
        return {
            "status": "query_failed",
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "endpoint": endpoint,
            "candidate_identifier_count": len(identifiers),
            "candidate_identifiers_sha256": identifiers_sha,
            "response_body_sha256": None,
            "raw_identifiers_query_and_response_emitted": False,
            "interpretation_limit": "No current-provider identity result was established.",
        }


def _capture_current_ols_metadata() -> dict[str, Any]:
    endpoint_template = "https://www.ebi.ac.uk/ols4/api/ontologies/{ontology}"

    def fetch(ontology: str) -> dict[str, Any]:
        request = Request(
            endpoint_template.format(ontology=ontology),
            headers={"Accept": "application/json", "User-Agent": "hypergraph-analysis-exploration/phase221"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
            metadata = json.loads(body.decode("utf-8"))
            config = metadata.get("config") if isinstance(metadata, dict) else None
            config = config if isinstance(config, dict) else {}
            annotations = config.get("annotations")
            annotations = annotations if isinstance(annotations, dict) else {}
            license_value = annotations.get("license")
            license_count = len(license_value) if isinstance(license_value, list) else int(bool(license_value))
            return {
                "ontology_id": ontology,
                "status": "ok",
                "loaded": metadata.get("loaded"),
                "version": metadata.get("version"),
                "version_iri": config.get("versionIri"),
                "file_location": config.get("fileLocation"),
                "license_annotation_count": license_count,
                "rights_annotation_present": bool(annotations.get("rights")),
                "response_body_sha256": hashlib.sha256(body).hexdigest(),
            }
        except (OSError, URLError, UnicodeDecodeError, json.JSONDecodeError, AttributeError, TypeError):
            return {"ontology_id": ontology, "status": "query_failed", "response_body_sha256": None}

    with ThreadPoolExecutor(max_workers=3) as executor:
        rows = list(executor.map(fetch, OLS_ONTOLOGIES))
    return {
        "status": "complete" if all(row["status"] == "ok" for row in rows) else "partial",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "endpoint_template": endpoint_template,
        "ontologies": rows,
        "interpretation_limit": "Current OLS registry metadata only; it does not identify the version, bytes, or license metadata of a local query-cache snapshot.",
    }


def audit(bundle: Path, triage_path: Path = TRIAGE, *, verify_nlm: bool = False) -> dict[str, Any]:
    bundle = bundle.resolve()
    triage_path = triage_path.resolve()
    triage = _load_json(triage_path)
    if triage.get("raw_gloss_ids_paths_and_full_urls_emitted") is not False:
        raise ValueError("triage privacy contract is missing")
    expected_profiles = [
        row for row in triage.get("candidate_profiles", [])
        if isinstance(row, dict) and row.get("source") in TARGETS
    ]
    if len(expected_profiles) != 6:
        raise ValueError("expected exactly six aggregate profiles for the selected source families")
    expected_profile_payload_counts: Counter[tuple[str, str, str, str]] = Counter()
    for profile in expected_profiles:
        key = tuple(
            profile.get(name) if isinstance(profile.get(name), str) else "missing"
            for name in ("source", "source_version", "source_ontology", "evidence_type")
        )
        expected_profile_payload_counts[key] += int(profile["payload_count"])

    integrity = verify_frozen_bundle_integrity(bundle)
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity lock failed")
    index_path = bundle / "indexes" / "senses.jsonl"
    checksums, checksums_sha = _load_checksums(bundle)

    counts: dict[str, Counter[str]] = defaultdict(Counter)
    evidence_keys: dict[str, Counter[str]] = defaultdict(Counter)
    shape_counts: dict[str, Counter[str]] = defaultdict(Counter)
    profile_counts: Counter[tuple[str, str, str, str]] = Counter()
    profile_payload_counts: Counter[tuple[str, str, str, str]] = Counter()
    cooccurrence_counts: Counter[str] = Counter()
    mesh_identity_matches: dict[str, Counter[str]] = defaultdict(Counter)
    candidate_mesh_identifiers: set[str] = set()
    seen: set[str] = set()
    sequence = hashlib.sha256()
    indexed_refs = verified_payloads = verified_bytes = target_payloads = 0
    target_evidence = 0

    with index_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            if not isinstance(row, dict) or not isinstance(row.get("source_records"), list):
                continue
            for source_meta in row["source_records"]:
                relative = source_meta.get("path") if isinstance(source_meta, dict) else None
                if not isinstance(relative, str) or _source_family(relative) != SOURCE_FAMILY:
                    continue
                indexed_refs += 1
                if relative in seen:
                    continue
                seen.add(relative)
                payload_path = _safe_payload_path(bundle, relative, DEFAULT_MAX_SOURCE_BYTES)
                raw = payload_path.read_bytes()
                digest = _sha256_bytes(raw)
                checksum = checksums.get(relative)
                if (not isinstance(checksum, dict)
                        or checksum.get("sha256") != digest
                        or type(checksum.get("bytes")) is not int
                        or checksum["bytes"] != len(raw)):
                    raise ValueError("source payload differs from frozen checksums")
                payload = json.loads(raw.decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("source payload is not an object")
                verified_payloads += 1
                verified_bytes += len(raw)
                sequence.update(len(raw).to_bytes(8, "big"))
                sequence.update(bytes.fromhex(digest))

                source_record = payload.get("source_record")
                provenance = source_record.get("alternative_definition_provenance") if isinstance(source_record, dict) else None
                evidence = provenance.get("source_evidence") if isinstance(provenance, dict) else None
                matching = [
                    item for item in evidence
                    if isinstance(item, dict) and _source_label(item.get("source")) in TARGETS
                ] if isinstance(evidence, list) else []
                if not matching:
                    continue
                target_payloads += 1
                labels = {_source_label(item.get("source")) for item in matching}
                payload_profiles: set[tuple[str, str, str, str]] = set()
                for source in labels:
                    counts[source]["payload_count"] += 1
                for item in matching:
                    source = _source_label(item.get("source"))
                    target_evidence += 1
                    counts[source]["evidence_object_count"] += 1
                    ontology = item.get("source_ontology")
                    version = item.get("source_version")
                    evidence_type = item.get("evidence_type")
                    profile = (
                        source,
                        _dimension_label(version),
                        _dimension_label(ontology),
                        _dimension_label(evidence_type),
                    )
                    profile_counts[profile] += 1
                    payload_profiles.add(profile)
                    for key in item:
                        if isinstance(key, str) and SAFE_LABEL.fullmatch(key) and SIGNAL.search(key):
                            evidence_keys[source][key] += 1
                    for field in (
                        "source_version", "source_ontology", "external_id",
                        "source_file", "source_locator", "download_url",
                    ):
                        shape_counts[source][f"{field}:{_shape(item.get(field))}"] += 1
                profile_payload_counts.update(payload_profiles)

                direct_mesh = [item for item in matching if _source_label(item.get("source")) == "MeSH_2026_descriptors"]
                ols_mesh = [
                    item for item in matching
                    if _source_label(item.get("source")) == "EMBL-EBI_OLS"
                    and _dimension_label(item.get("source_ontology")) == "mesh"
                ]
                if direct_mesh and ols_mesh:
                    cooccurrence_counts["direct_mesh_and_ols_mesh"] += 1
                    for field in ("external_id", "source_locator", "source_file"):
                        direct_forms = [
                            forms for item in direct_mesh
                            if (forms := _identity_forms(item.get(field))) is not None
                        ]
                        ols_forms = [
                            forms for item in ols_mesh
                            if (forms := _identity_forms(item.get(field))) is not None
                        ]
                        for transform in ("exact_trimmed", "casefolded_trimmed", "terminal_token_casefolded"):
                            direct_values = {forms[transform] for forms in direct_forms}
                            ols_values = {forms[transform] for forms in ols_forms}
                            if direct_values.intersection(ols_values):
                                mesh_identity_matches[field][transform] += 1
                            if field in {"external_id", "source_locator"} and transform == "terminal_token_casefolded":
                                candidate_mesh_identifiers.update(
                                    value.upper() for value in direct_values.intersection(ols_values)
                                    if MESH_IDENTIFIER.fullmatch(value)
                                )

    if profile_payload_counts != expected_profile_payload_counts:
        raise ValueError("payload counts do not reconcile to the Phase24 aggregate profiles")

    by_source: list[dict[str, Any]] = []
    for source in sorted(TARGETS):
        versions = sorted({version for src, version, _, _ in profile_counts if src == source and SAFE_LABEL.fullmatch(version)})
        ontologies = sorted({ontology for src, _, ontology, _ in profile_counts if src == source and SAFE_LABEL.fullmatch(ontology)})
        source_profiles = []
        for (src, version, ontology, evidence_type), evidence_count in sorted(profile_counts.items()):
            if src != source:
                continue
            source_profiles.append({
                "source_version": version if SAFE_LABEL.fullmatch(version) else "noncanonical_or_missing",
                "source_ontology": ontology if SAFE_LABEL.fullmatch(ontology) else "noncanonical_or_missing",
                "evidence_type": evidence_type if SAFE_LABEL.fullmatch(evidence_type) else "noncanonical_or_missing",
                "evidence_object_count": evidence_count,
                "profile_payload_count": profile_payload_counts[(src, version, ontology, evidence_type)],
            })
        by_source.append({
            "source_label": source,
            **dict(counts[source]),
            "observed_source_version_labels": versions,
            "observed_source_ontology_labels": ontologies,
            "evidence_binding_key_presence": dict(sorted(evidence_keys[source].items())),
            "metadata_value_shapes": dict(sorted(shape_counts[source].items())),
            "profiles": source_profiles,
        })

    return {
        "audit_version": "mesh-ols-record-binding/1",
        "inputs": {
            "triage_sha256": _sha256_file(triage_path),
            "sense_index_sha256": _sha256_file(index_path),
            "checksums_sha256": checksums_sha,
            "implementation_sha256": _sha256_file(Path(__file__).resolve()),
        },
        "scope": {
            "source_family": "alternative_or_definition_wsd_frozen",
            "indexed_references": indexed_refs,
            "unique_payloads_verified": verified_payloads,
            "payload_bytes_verified": verified_bytes,
            "target_payloads": target_payloads,
            "target_evidence_objects": target_evidence,
            "target_candidate_profiles_in_triage": len(expected_profiles),
            "payload_sequence_sha256": sequence.hexdigest(),
        },
        "sources": by_source,
        "same_payload_crosswalk": {
            "payload_cooccurrence_counts": dict(sorted(cooccurrence_counts.items())),
            "direct_mesh_vs_ols_mesh_field_overlap_payload_counts": {
                field: dict(sorted(transform_counts.items()))
                for field, transform_counts in sorted(mesh_identity_matches.items())
            },
            "fields_compared": ["external_id", "source_locator", "source_file"],
            "comparison_forms": ["exact_trimmed", "casefolded_trimmed", "terminal_token_casefolded"],
            "comparison_limit": "exploratory representation normalization; overlap does not prove release or item equivalence",
            "raw_field_values_emitted": False,
        },
        "current_nlm_mesh_identifier_check": (
            _verify_mesh_identifiers_with_nlm(candidate_mesh_identifiers)
            if verify_nlm else {"status": "not_requested"}
        ),
        "current_ols_api_metadata": {"status": "not_requested"},
        "release_clearance": "not_assessed",
        "interpretation_limit": (
            "Field presence and value shapes identify available binding metadata only. They do not join a local record to an upstream artifact, "
            "verify a provider release, establish license compatibility, or authorize redistribution. Payload counts are source-family profile counts, "
            "not a complete bundle source inventory."
        ),
        "raw_gloss_ids_paths_and_full_urls_emitted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=configured_bundle_root())
    parser.add_argument("--triage", type=Path, default=TRIAGE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--verify-nlm", action="store_true", help="check normalized MeSH IDs against the public NLM MeSH RDF REST API")
    parser.add_argument("--query-ols-api", action="store_true", help="capture current OLS ontology version metadata for the five source namespaces")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        report = audit(args.bundle, args.triage, verify_nlm=args.verify_nlm)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        parser.error("audit failed; no report was written")
    if args.query_ols_api:
        report["current_ols_api_metadata"] = _capture_current_ols_metadata()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), **report["scope"], "release_clearance": report["release_clearance"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
