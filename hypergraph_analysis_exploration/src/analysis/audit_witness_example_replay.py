"""Re-replay a bounded witness/Datalog example and bind it to the full source-lineage audit.

The report contains only file hashes, aggregate counts, and validation flags; it
does not copy certificate nodes, source paths, glosses, or lemma text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from src.analysis.frozen_hypergraph_audit import DEFAULT_BUNDLE, PROJECT_ROOT
from src.analysis.frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK
from src.analysis.verify_witness_certificate import verify_witness_certificate
from src.analysis.verify_witness_datalog_bridge import verify_witness_datalog_bridge


DEFAULT_CERTIFICATE = PROJECT_ROOT / "outputs" / "phase6" / "witness_oewn-00520548-n.json"
DEFAULT_BRIDGE = PROJECT_ROOT / "outputs" / "phase148" / "witness_oewn-00520548-n_datalog_bridge.json"
DEFAULT_LEGACY_BRIDGE = PROJECT_ROOT / "outputs" / "phase6" / "witness_oewn-00520548-n_datalog_bridge.json"
DEFAULT_SOURCE_LINEAGE = PROJECT_ROOT / "outputs" / "phase117" / "selected_witness_source_lineage.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase148" / "witness_example_replay_audit.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def audit(
    certificate_path: Path = DEFAULT_CERTIFICATE,
    bridge_path: Path = DEFAULT_BRIDGE,
    source_lineage_path: Path = DEFAULT_SOURCE_LINEAGE,
    bundle: Path = DEFAULT_BUNDLE,
    integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
    legacy_bridge_path: Path = DEFAULT_LEGACY_BRIDGE,
) -> dict[str, Any]:
    certificate = _read_json(certificate_path)
    bridge_artifact = _read_json(bridge_path)
    legacy_bridge_artifact = _read_json(legacy_bridge_path)
    source_lineage = _read_json(source_lineage_path)

    structural = verify_witness_certificate(certificate, bundle.resolve(), integrity_lock.resolve())
    bridge = verify_witness_datalog_bridge(bridge_artifact, bundle.resolve(), integrity_lock.resolve())
    legacy_bridge = verify_witness_datalog_bridge(legacy_bridge_artifact, bundle.resolve(), integrity_lock.resolve())
    errors: list[str] = []

    nested_certificate = bridge_artifact.get("structural_certificate") if isinstance(bridge_artifact, dict) else None
    certificate_match = nested_certificate == certificate
    if not certificate_match:
        errors.append("Datalog bridge embeds a different structural certificate")

    embedded = bridge_artifact.get("bridge_verification") if isinstance(bridge_artifact, dict) else None
    embedded_summary_match = (
        isinstance(embedded, dict)
        and embedded.get("valid") is bridge.get("valid")
        and embedded.get("target") == bridge.get("target")
        and embedded.get("node_count") == bridge.get("node_count")
        and embedded.get("edge_count") == bridge.get("edge_count")
        and embedded.get("node_sets_match") == bridge.get("node_sets_match")
        and embedded.get("edge_multisets_match") == bridge.get("edge_multisets_match")
    )
    if not embedded_summary_match:
        errors.append("stored bridge_verification summary differs from independent re-replay")

    lineage_integrity = source_lineage.get("bundle_integrity", {}) if isinstance(source_lineage, dict) else {}
    current_integrity = structural.get("bundle_integrity", {})
    lineage_bundle_matches = (
        source_lineage.get("audit_version") == "selected-witness-source-lineage/2"
        and lineage_integrity.get("valid") is True
        and lineage_integrity.get("observed_sha256") == current_integrity.get("observed_sha256")
        and source_lineage.get("validation", {}).get("all_selected_source_payloads_match_checksums") is True
        and source_lineage.get("validation", {}).get("all_selected_source_payloads_match_witness_head_identity") is True
    )
    if not lineage_bundle_matches:
        errors.append("full selected-source lineage artifact does not validate the current witness bundle")

    if not structural.get("valid"):
        errors.append("structural certificate replay failed")
    if not bridge.get("valid"):
        errors.append("independent Datalog bridge replay failed")
    same_target = structural.get("target") == bridge.get("target") == certificate.get("target")
    if not same_target:
        errors.append("structural and Datalog replays do not identify the same target")

    source_documents = {
        source
        for node in certificate.get("nodes", []) if isinstance(node, dict)
        for source in node.get("source_documents", []) if isinstance(source, str)
    }
    legacy_stored_summary = legacy_bridge_artifact.get("bridge_verification", {})
    legacy_proof_result = legacy_bridge_artifact.get("datalog_proof_result", {})
    legacy_embedded_proof = legacy_proof_result.get("certificate", {})
    current_proof_result = bridge_artifact.get("datalog_proof_result", {})
    current_embedded_proof = current_proof_result.get("certificate", {})
    legacy_node_fields = sorted({
        key for node in legacy_embedded_proof.get("nodes", []) if isinstance(node, dict) for key in node
    })
    current_node_fields = sorted({
        key for node in current_embedded_proof.get("nodes", []) if isinstance(node, dict) for key in node
    })
    legacy_format_drift = (
        legacy_bridge.get("errors") == ["Datalog proof result does not match independent recomputation"]
        and legacy_stored_summary.get("valid") is True
        and legacy_stored_summary.get("datalog_certificate_valid") is True
        and legacy_stored_summary.get("node_sets_match") is True
        and legacy_stored_summary.get("edge_multisets_match") is True
        and set(current_node_fields) - set(legacy_node_fields) == {"source_bindings", "source_claim_refs"}
    )
    return {
        "schema_version": 1,
        "audit_version": "witness-example-replay-audit/2",
        "input_sha256": {
            "structural_certificate": _sha256(certificate_path),
            "current_datalog_bridge_artifact": _sha256(bridge_path),
            "historical_datalog_bridge_artifact": _sha256(legacy_bridge_path),
            "selected_source_lineage_artifact": _sha256(source_lineage_path),
            "frozen_bundle_integrity_lock": _sha256(integrity_lock),
        },
        "implementation_sha256": {
            relative: _sha256(PROJECT_ROOT / relative)
            for relative in (
                "src/analysis/verify_witness_certificate.py",
                "src/analysis/verify_witness_datalog_bridge.py",
                "src/analysis/frozen_bundle_integrity.py",
                "src/logic/datalog_checker.py",
            )
        },
        "target": certificate.get("target"),
        "structural_replay": {
            "valid": structural.get("valid") is True,
            "node_count": structural.get("node_count"),
            "edge_count": structural.get("edge_count"),
            "error_count": len(structural.get("errors", [])),
        },
        "datalog_replay": {
            "valid": bridge.get("valid") is True,
            "node_count": bridge.get("node_count"),
            "edge_count": bridge.get("edge_count"),
            "rule_count": bridge.get("datalog_rule_count"),
            "certificate_valid": bridge.get("datalog_certificate_valid") is True,
            "node_sets_match": bridge.get("node_sets_match") is True,
            "edge_multisets_match": bridge.get("edge_multisets_match") is True,
            "error_count": len(bridge.get("errors", [])),
        },
        "historical_datalog_bridge": {
            "stored_validation_passed_when_created": legacy_stored_summary.get("valid") is True,
            "current_checker_replay_valid": legacy_bridge.get("valid") is True,
            "current_checker_errors": legacy_bridge.get("errors", []),
            "proof_certificate_field_additions": sorted(set(current_node_fields) - set(legacy_node_fields)),
            "proof_schema_drift_explains_replay_mismatch": legacy_format_drift,
        },
        "cross_artifact_checks": {
            "same_target": same_target,
            "bridge_embeds_exact_structural_certificate": certificate_match,
            "stored_bridge_summary_matches_rereplay": embedded_summary_match,
            "current_bridge_stored_summary_matches_rereplay": (
                isinstance(bridge_artifact.get("bridge_verification"), dict)
                and bridge_artifact["bridge_verification"].get("valid") is bridge.get("valid")
                and bridge_artifact["bridge_verification"].get("node_count") == bridge.get("node_count")
                and bridge_artifact["bridge_verification"].get("edge_count") == bridge.get("edge_count")
                and bridge_artifact["bridge_verification"].get("node_sets_match") == bridge.get("node_sets_match")
                and bridge_artifact["bridge_verification"].get("edge_multisets_match") == bridge.get("edge_multisets_match")
            ),
            "legacy_checker_format_drift_isolated": legacy_format_drift,
            "phase117_full_source_lineage_matches_current_bundle": lineage_bundle_matches,
            "selected_source_document_count_in_example": len(source_documents),
        },
        "graph_semantic_fingerprint_sha256": certificate.get("graph_semantic_fingerprint_sha256"),
        "valid": not errors,
        "errors": errors,
        "scope_limit": (
            "This verifies structural witness replay, selected-clause identity, an independent ground Datalog proof, "
            "and linkage to the separately hash-verified full selected-source lineage audit. It does not assess gloss-span "
            "semantic support, WSD correctness, alternative clauses, open-world entailment, or license clearance."
        ),
        "raw_text_or_source_paths_emitted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_CERTIFICATE)
    parser.add_argument("--bridge", type=Path, default=DEFAULT_BRIDGE)
    parser.add_argument("--legacy-bridge", type=Path, default=DEFAULT_LEGACY_BRIDGE)
    parser.add_argument("--source-lineage", type=Path, default=DEFAULT_SOURCE_LINEAGE)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error(f"output already exists; pass --force to replace it: {args.output}")
    try:
        report = audit(args.certificate, args.bridge, args.source_lineage, args.bundle, args.integrity_lock,
                       args.legacy_bridge)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "valid": report["valid"],
        "target": report["target"],
        "nodes": report["structural_replay"]["node_count"],
        "edges": report["structural_replay"]["edge_count"],
        "source_lineage_matches_current_bundle": report["cross_artifact_checks"]["phase117_full_source_lineage_matches_current_bundle"],
        "legacy_checker_format_drift_isolated": report["historical_datalog_bridge"]["proof_schema_drift_explains_replay_mismatch"],
        "output": str(args.output),
    }, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
