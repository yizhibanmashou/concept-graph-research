"""Cross-check declared source-replay exceptions against the frozen graph/index."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:  # Direct script execution and package/module execution are both supported.
    from .frozen_hypergraph_audit import DEFAULT_BUNDLE, jsonl
    from .project_paths import PROJECT_ROOT
except ImportError:
    from frozen_hypergraph_audit import DEFAULT_BUNDLE, jsonl
    from project_paths import PROJECT_ROOT


DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase8" / "frozen_bundle_replay_exceptions.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_replay_exceptions(bundle: Path) -> dict[str, Any]:
    """Verify the bundle's declared replay exception(s) without reading source payloads."""
    manifest_path = bundle / "manifest.json"
    replay_path = bundle / "reports" / "source_replay.json"
    index_path = bundle / "indexes" / "senses.jsonl"
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    witnesses_path = bundle / "graph" / "coverage_witnesses.jsonl"
    required = (manifest_path, replay_path, index_path, rules_path, witnesses_path)
    missing = [path.name for path in required if not path.is_file()]
    if missing:
        raise ValueError(f"Frozen bundle is missing required files: {', '.join(missing)}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    fingerprint = manifest.get("semantic_fingerprint_sha256")
    if not isinstance(fingerprint, str) or not fingerprint:
        raise ValueError("Frozen bundle manifest lacks semantic_fingerprint_sha256")
    if replay.get("semantic_fingerprint_sha256") != fingerprint:
        raise ValueError("source_replay report fingerprint does not match manifest")

    index_by_id: dict[str, dict[str, Any]] = {}
    canonical_counts = {"true": 0, "false": 0, "missing_or_invalid": 0}
    for row in jsonl(index_path):
        identity = row.get("identity")
        if not isinstance(identity, str) or not identity or identity in index_by_id:
            raise ValueError("sense index contains malformed or duplicate identities")
        index_by_id[identity] = row
        flag = row.get("canonical_replay_exact")
        key = str(flag).lower() if isinstance(flag, bool) else "missing_or_invalid"
        canonical_counts[key] += 1

    declared_exact = replay.get("canonical_replay_exact_heads")
    manifest_exact = manifest.get("canonical_replay_exact_heads")
    if declared_exact != canonical_counts["true"] or manifest_exact != canonical_counts["true"]:
        raise ValueError("canonical replay exact count disagrees across index, report, and manifest")
    if len(index_by_id) != manifest.get("sense_count"):
        raise ValueError("sense index count does not match manifest")

    rule_by_id: dict[str, list[list[str]]] = {}
    for row in jsonl(rules_path):
        identity = row.get("head")
        clauses = row.get("clauses")
        if not isinstance(identity, str) or identity in rule_by_id or not isinstance(clauses, list):
            raise ValueError("rule file contains malformed or duplicate heads")
        if any(not isinstance(clause, list) or any(not isinstance(dep, str) for dep in clause)
               for clause in clauses):
            raise ValueError(f"rule file contains malformed clauses for {identity}")
        rule_by_id[identity] = clauses

    witness_by_id: dict[str, dict[str, Any]] = {}
    for row in jsonl(witnesses_path):
        identity = row.get("head")
        if not isinstance(identity, str) or identity in witness_by_id:
            raise ValueError("witness file contains malformed or duplicate heads")
        witness_by_id[identity] = row

    exceptions = replay.get("graph_slice_selection_heads")
    if not isinstance(exceptions, list):
        raise ValueError("source_replay graph_slice_selection_heads must be a list")
    exception_ids: set[str] = set()
    audited_exceptions = []
    for exception in exceptions:
        if not isinstance(exception, dict):
            raise ValueError("source_replay exception must be an object")
        identity = exception.get("head")
        if not isinstance(identity, str) or identity in exception_ids:
            raise ValueError("source_replay exceptions contain malformed or duplicate heads")
        exception_ids.add(identity)
        index_row = index_by_id.get(identity)
        if index_row is None or index_row.get("canonical_replay_exact") is not False:
            raise ValueError(f"declared replay exception is not marked false in sense index: {identity}")
        clauses = rule_by_id.get(identity)
        witness = witness_by_id.get(identity)
        if clauses is None or witness is None:
            raise ValueError(f"replay exception lacks graph rules or witness: {identity}")
        if index_row.get("graph_clause_count") != len(clauses):
            raise ValueError(f"graph clause count disagrees with sense index for {identity}")
        witness_clause = witness.get("witness_clause")
        witness_matches = [clause for clause in clauses if sorted(clause) == sorted(witness_clause or [])]
        if not isinstance(witness_clause, list) or len(witness_matches) != 1:
            raise ValueError(f"selected witness is not a unique graph clause for {identity}")
        direct_evidence = exception.get("all_graph_clauses_have_direct_source_dnf_evidence")
        if not isinstance(direct_evidence, bool):
            raise ValueError(f"source DNF evidence flag is malformed for {identity}")
        audited_exceptions.append({
            "identity": identity,
            "pos": index_row.get("pos"),
            "graph_clause_count": len(clauses),
            "graph_clauses": clauses,
            "selected_witness_clause": witness_clause,
            "selected_witness_depth": witness.get("proof_depth"),
            "missing_from_canonical_replay": exception.get("missing_from_canonical_replay"),
            "extra_in_canonical_replay": exception.get("extra_in_canonical_replay"),
            "all_graph_clauses_have_direct_source_dnf_evidence": direct_evidence,
            "selection_policy": exception.get("policy"),
        })

    false_ids = {identity for identity, row in index_by_id.items()
                 if row.get("canonical_replay_exact") is False}
    if false_ids != exception_ids:
        raise ValueError("source_replay exception list does not exactly cover false index flags")
    if replay.get("heads") != len(index_by_id) or replay.get("heads") != manifest.get("head_count"):
        raise ValueError("source_replay head count disagrees with index or manifest")

    return {
        "audit_version": "frozen-bundle-replay-exceptions/1",
        "claim_type": "bundle_source_replay_consistency_audit_not_semantic_validation",
        "bundle_semantic_fingerprint_sha256": fingerprint,
        "input_sha256": {
            "manifest": _sha256(manifest_path),
            "source_replay_report": _sha256(replay_path),
            "sense_index": _sha256(index_path),
            "graph_rules": _sha256(rules_path),
        },
        "sense_count": len(index_by_id),
        "canonical_replay_exact_counts": canonical_counts,
        "exception_count": len(audited_exceptions),
        "exceptions": audited_exceptions,
        "source_payloads_opened": False,
        "interpretation_limit": "This cross-check validates consistency of the frozen package's declared replay exception against its index, rules, and witness. It does not rerun the upstream source normalization/replay, authenticate source payload licenses, or establish gloss semantics.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="replace the existing report")
    args = parser.parse_args()
    output = args.output.resolve()
    try:
        output.relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        parser.error("output must be inside the project directory")
    if output.exists() and not args.force:
        parser.error(f"output already exists; pass --force to replace it: {output}")
    report = audit_replay_exceptions(args.bundle.resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Audited {report['exception_count']} replay exception(s); report: {output}")


if __name__ == "__main__":
    main()
