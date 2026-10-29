"""Cross-check one frozen witness DAG with the independent positive-Datalog checker.

The bridge replays the selected graph clause for each node as a ground Horn rule.
It validates structural availability in the frozen graph, not gloss semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:  # Direct script execution and package/module execution are both supported.
    from .frozen_hypergraph_audit import DEFAULT_BUNDLE, PROJECT_ROOT, jsonl
    from .frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK
    from .verify_witness_certificate import CLAIM_TYPE, verify_witness_certificate
    from src.logic.datalog_checker import verify_certificate, verify_query
except ImportError:
    from frozen_hypergraph_audit import DEFAULT_BUNDLE, PROJECT_ROOT, jsonl
    from frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK
    from verify_witness_certificate import CLAIM_TYPE, verify_witness_certificate
    from src.logic.datalog_checker import verify_certificate, verify_query


BRIDGE_SCHEMA = "frozen-witness-datalog-bridge/1"


def _canonical_sha256(value: Any) -> str:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def build_ground_datalog_program(
    certificate: dict[str, Any], bundle: Path, integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
) -> dict[str, Any]:
    """Compile only the already-selected clauses in a verified witness DAG."""
    structural = verify_witness_certificate(certificate, bundle, integrity_lock)
    if not structural["valid"]:
        raise ValueError("structural witness certificate is invalid: " + "; ".join(structural["errors"]))

    nodes = certificate["nodes"]
    node_by_id = {node["id"]: node for node in nodes}
    graph_rules = {}
    for row in jsonl(bundle / "graph" / "hypergraph_rules.jsonl"):
        head = row.get("head")
        if head in node_by_id:
            if head in graph_rules:
                raise ValueError(f"duplicate frozen rule head in witness DAG: {head}")
            graph_rules[head] = row.get("clauses")

    facts = [
        {"predicate": head, "arguments": [], "source_documents": []}
        for head, node in sorted(node_by_id.items())
        if node["is_seed"]
    ]
    rules = []
    for head, node in sorted(node_by_id.items(), key=lambda pair: (pair[1]["proof_depth"], pair[0])):
        if node["is_seed"]:
            continue
        clauses = graph_rules.get(head)
        clause_index = node["witness_clause_index"]
        if (not isinstance(clauses, list) or type(clause_index) is not int
                or clause_index < 0 or clause_index >= len(clauses)):
            raise ValueError(f"selected frozen clause is unavailable for {head}")
        clause = clauses[clause_index]
        if not isinstance(clause, list) or Counter(clause) != Counter(node["witness_clause"]):
            raise ValueError(f"selected frozen clause differs from witness body for {head}")
        rules.append({
            "id": f"witness:{node['proof_depth']:06d}:{head}",
            "head": {"predicate": head, "arguments": []},
            "body": [{"predicate": dep, "arguments": []} for dep in clause],
            "provenance": {
                "claim_type": CLAIM_TYPE,
                "graph_semantic_fingerprint_sha256": certificate["graph_semantic_fingerprint_sha256"],
                "head": head,
                "proof_depth": node["proof_depth"],
                "selected_clause_index": clause_index,
                "source_documents": node["source_documents"],
            },
        })

    return {
        "schema_version": "ground-datalog-program/1",
        "graph_semantic_fingerprint_sha256": certificate["graph_semantic_fingerprint_sha256"],
        "facts": facts,
        "rules": rules,
        "query": {"predicate": certificate["target"], "arguments": []},
    }


def _proof_graph_edges(proof_certificate: dict[str, Any]) -> Counter[tuple[str, str]]:
    nodes = {node["node_id"]: node for node in proof_certificate["nodes"]}
    edges: Counter[tuple[str, str]] = Counter()
    for node in proof_certificate["nodes"]:
        if node["kind"] != "rule":
            continue
        head = node["atom"]["predicate"]
        for premise_id in node["premise_node_ids"]:
            edges[(nodes[premise_id]["atom"]["predicate"], head)] += 1
    return edges


def verify_witness_datalog_bridge(
    artifact: dict[str, Any], bundle: Path, integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
) -> dict[str, Any]:
    """Independently validate both certificates and require exact DAG agreement."""
    errors = []
    if not isinstance(artifact, dict) or artifact.get("schema_version") != BRIDGE_SCHEMA:
        return {"valid": False, "errors": ["unsupported or malformed bridge artifact"]}
    structural_certificate = artifact.get("structural_certificate")
    structural = verify_witness_certificate(structural_certificate, bundle, integrity_lock)
    if not structural["valid"]:
        errors.append("structural certificate failed replay: " + "; ".join(structural["errors"]))
    if artifact.get("structural_certificate_canonical_sha256") != _canonical_sha256(structural_certificate):
        errors.append("structural certificate hash mismatch")
    if errors:
        return {"valid": False, "target": structural_certificate.get("target")
                if isinstance(structural_certificate, dict) else None, "errors": errors}

    expected_program = build_ground_datalog_program(structural_certificate, bundle, integrity_lock)
    program = artifact.get("datalog_program")
    if program != expected_program:
        errors.append("Datalog program does not exactly match the selected frozen witness clauses")
        return {"valid": False, "target": structural_certificate["target"], "errors": errors}

    proof_result = verify_query(program)
    if artifact.get("datalog_proof_result") != proof_result:
        errors.append("Datalog proof result does not match independent recomputation")
    if proof_result.get("status") != "entailed_in_positive_datalog":
        errors.append("selected witness target was not derived by the Datalog replay")
    proof_certificate = proof_result.get("certificate")
    if (not isinstance(proof_certificate, dict)
            or not verify_certificate(program, proof_certificate)):
        errors.append("Datalog proof certificate failed independent replay")
        proof_certificate = {"nodes": []}

    graph_nodes = {node["id"] for node in structural_certificate["nodes"]}
    proof_nodes = set()
    for node in proof_certificate["nodes"]:
        atom = node.get("atom", {})
        if not isinstance(atom, dict) or atom.get("arguments") != []:
            errors.append("Datalog proof contains a non-ground graph atom")
            continue
        predicate = atom.get("predicate")
        if not isinstance(predicate, str) or predicate in proof_nodes:
            errors.append("Datalog proof contains malformed or duplicate graph nodes")
            continue
        proof_nodes.add(predicate)
    node_sets_match = proof_nodes == graph_nodes
    if not node_sets_match:
        errors.append("Datalog and structural certificates contain different node sets")

    graph_edges = Counter((edge["from"], edge["to"]) for edge in structural_certificate["edges"])
    proof_edges = _proof_graph_edges(proof_certificate)
    edge_multisets_match = proof_edges == graph_edges
    if not edge_multisets_match:
        errors.append("Datalog and structural certificates contain different dependency-edge multisets")

    return {
        "valid": not errors,
        "target": structural_certificate["target"],
        "node_count": len(graph_nodes),
        "edge_count": sum(graph_edges.values()),
        "datalog_rule_count": len(program["rules"]),
        "datalog_certificate_valid": isinstance(artifact.get("datalog_proof_result"), dict)
        and artifact["datalog_proof_result"].get("certificate_valid") is True,
        "node_sets_match": node_sets_match,
        "edge_multisets_match": edge_multisets_match,
        "bundle_integrity": structural.get("bundle_integrity"),
        "errors": errors,
        "scope_note": "Cross-checks structural availability in the selected frozen Horn witness using a separate ground Datalog proof checker. It does not validate gloss semantics, alternative clauses, or open-world entailment.",
    }


def create_bridge_artifact(
    certificate: dict[str, Any], bundle: Path, integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
) -> dict[str, Any]:
    program = build_ground_datalog_program(certificate, bundle, integrity_lock)
    proof_result = verify_query(program)
    artifact = {
        "schema_version": BRIDGE_SCHEMA,
        "claim_type": CLAIM_TYPE,
        "structural_certificate_canonical_sha256": _canonical_sha256(certificate),
        "structural_certificate": certificate,
        "datalog_program": program,
        "datalog_proof_result": proof_result,
    }
    artifact["bridge_verification"] = verify_witness_datalog_bridge(artifact, bundle, integrity_lock)
    return artifact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path, help="exported selected-witness DAG JSON")
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-nodes", type=int, default=10000)
    parser.add_argument("--force", action="store_true", help="replace an existing bridge artifact")
    args = parser.parse_args()
    if args.max_nodes < 1:
        parser.error("--max-nodes must be positive")
    certificate = json.loads(args.certificate.read_text(encoding="utf-8"))
    if not isinstance(certificate, dict) or not isinstance(certificate.get("nodes"), list):
        parser.error("certificate must contain a nodes list")
    if len(certificate["nodes"]) > args.max_nodes:
        parser.error(f"certificate exceeds --max-nodes={args.max_nodes}")
    target = certificate.get("target")
    if not isinstance(target, str) or not target:
        parser.error("certificate target must be a non-empty string")
    output = (args.output.resolve() if args.output else
              PROJECT_ROOT / "outputs" / "phase6" / f"witness_{target}_datalog_bridge.json")
    if output.exists() and not args.force:
        parser.error("output exists; pass --force to replace it")
    artifact = create_bridge_artifact(certificate, args.bundle.resolve(), args.integrity_lock.resolve())
    if not artifact["bridge_verification"]["valid"]:
        parser.error("bridge verification failed: " + "; ".join(artifact["bridge_verification"]["errors"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Verified witness/Datalog bridge for {target}: {len(certificate['nodes'])} nodes, "
          f"{len(certificate['edges'])} dependency edges; wrote {output}")


if __name__ == "__main__":
    main()
