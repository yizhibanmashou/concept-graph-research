"""Independently replay an exported single-witness DAG against its frozen bundle.

This validates structural Horn-closure evidence only. It does not establish that
the natural-language sources semantically support the selected clauses.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:  # Direct script execution and package/module execution are both supported.
    from .frozen_hypergraph_audit import DEFAULT_BUNDLE, PROJECT_ROOT, jsonl
    from .frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK, verify_frozen_bundle_integrity
except ImportError:
    from frozen_hypergraph_audit import DEFAULT_BUNDLE, PROJECT_ROOT, jsonl
    from frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK, verify_frozen_bundle_integrity


CLAIM_TYPE = "structural_definitional_availability_not_truth_conditional_entailment"


def verify_witness_certificate(
    certificate: dict[str, Any], bundle: Path, integrity_lock: Path = DEFAULT_INTEGRITY_LOCK,
) -> dict[str, Any]:
    """Check every exported node, selected clause, source pointer, edge and order."""
    errors: list[str] = []

    integrity = verify_frozen_bundle_integrity(bundle, integrity_lock)
    if not integrity["valid"]:
        return {
            "valid": False,
            "errors": ["bundle integrity lock failed: " + ", ".join(integrity["errors"])],
            "bundle_integrity": integrity,
        }

    def error(message: str):
        errors.append(message)

    manifest_path = bundle / "manifest.json"
    if not manifest_path.is_file():
        return {"valid": False, "errors": ["bundle manifest is missing"]}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    fingerprint = manifest.get("semantic_fingerprint_sha256")
    if not isinstance(certificate, dict):
        return {"valid": False, "errors": ["certificate must be an object"]}
    if certificate.get("claim_type") != CLAIM_TYPE:
        error("certificate claim_type is missing or unsupported")
    if not isinstance(fingerprint, str) or not fingerprint:
        error("bundle manifest lacks a usable graph semantic fingerprint")
    if certificate.get("graph_semantic_fingerprint_sha256") != fingerprint:
        error("certificate graph fingerprint does not match the bundle")

    graph_dir = bundle / "graph"
    index_dir = bundle / "indexes"
    rules_path = graph_dir / "hypergraph_rules.jsonl"
    witnesses_path = graph_dir / "coverage_witnesses.jsonl"
    senses_path = index_dir / "senses.jsonl"
    for path in (rules_path, witnesses_path, senses_path):
        if not path.is_file():
            error(f"required bundle file is missing: {path.name}")
    if errors:
        return {"valid": False, "errors": errors}

    rules: dict[str, list[list[str]]] = {}
    for row in jsonl(rules_path):
        head = row.get("head")
        clauses = row.get("clauses")
        if not isinstance(head, str) or not isinstance(clauses, list):
            error("bundle contains a malformed rule row")
            continue
        if head in rules:
            error(f"bundle contains duplicate rule head: {head}")
            continue
        if any(not isinstance(clause, list) or any(not isinstance(dep, str) for dep in clause)
               for clause in clauses):
            error(f"bundle contains a malformed clause for head: {head}")
            continue
        rules[head] = clauses

    witness_by_head: dict[str, dict[str, Any]] = {}
    for row in jsonl(witnesses_path):
        head = row.get("head")
        if not isinstance(head, str) or head in witness_by_head:
            error("bundle contains a malformed or duplicate witness head")
            continue
        witness_by_head[head] = row

    senses: dict[str, dict[str, Any]] = {}
    for row in jsonl(senses_path):
        identity = row.get("identity")
        if not isinstance(identity, str) or identity in senses:
            error("bundle contains a malformed or duplicate sense identity")
            continue
        senses[identity] = row

    raw_nodes = certificate.get("nodes")
    raw_order = certificate.get("topological_order")
    raw_edges = certificate.get("edges")
    target = certificate.get("target")
    if not isinstance(raw_nodes, list):
        error("certificate nodes must be a list")
        raw_nodes = []
    if not isinstance(raw_order, list) or any(not isinstance(item, str) for item in raw_order):
        error("certificate topological_order must be a list of head IDs")
        raw_order = []
    if not isinstance(raw_edges, list):
        error("certificate edges must be a list")
        raw_edges = []
    if not isinstance(target, str) or target not in witness_by_head:
        error("certificate target is absent from the frozen witness index")

    nodes: dict[str, dict[str, Any]] = {}
    for node in raw_nodes:
        if not isinstance(node, dict) or not isinstance(node.get("id"), str):
            error("certificate contains a malformed node")
            continue
        head = node["id"]
        if head in nodes:
            error(f"certificate contains duplicate node: {head}")
            continue
        nodes[head] = node

    if certificate.get("node_count") != len(raw_nodes):
        error("node_count does not match the nodes array")
    if certificate.get("edge_count") != len(raw_edges):
        error("edge_count does not match the edges array")
    if len(raw_order) != len(set(raw_order)) or set(raw_order) != set(nodes):
        error("topological_order must contain every certificate node exactly once")
    if raw_order and raw_order[-1] != target:
        error("target must be last in the dependency-before-head topological order")

    order_index = {head: i for i, head in enumerate(raw_order)}
    expected_edges: Counter[tuple[str, str]] = Counter()
    for head, node in nodes.items():
        reference = witness_by_head.get(head)
        if reference is None:
            error(f"certificate node is absent from the frozen witness index: {head}")
            continue
        if head not in rules:
            error(f"certificate head has no frozen rules: {head}")
            continue

        is_seed = reference.get("is_seed")
        depth = reference.get("proof_depth")
        body = reference.get("witness_clause")
        if not isinstance(is_seed, bool) or type(depth) is not int or not isinstance(body, list):
            error(f"frozen witness record is malformed: {head}")
            continue
        if node.get("is_seed") is not is_seed:
            error(f"seed marker mismatch: {head}")
        if node.get("proof_depth") != depth:
            error(f"proof depth mismatch: {head}")
        if node.get("witness_clause") != body:
            error(f"selected witness clause mismatch: {head}")

        if is_seed:
            expected_clause_index = None
            expected_source_docs: list[str] = []
            if body or depth != 0:
                error(f"frozen seed witness is malformed: {head}")
        else:
            if not all(isinstance(dep, str) for dep in body):
                error(f"frozen witness body is malformed: {head}")
                continue
            matching = [i for i, clause in enumerate(rules[head])
                        if sorted(clause) == sorted(body)]
            if not matching:
                error(f"frozen witness clause is not present in the rule set: {head}")
                continue
            expected_clause_index = matching[0]
            expected_source_docs = []
            for source in senses.get(head, {}).get("active_clause_sources", []):
                if isinstance(source, dict) and source.get("clause_index") == expected_clause_index:
                    docs = source.get("source_documents", [])
                    if isinstance(docs, list):
                        expected_source_docs.extend(doc for doc in docs if isinstance(doc, str))
            expected_source_docs = sorted(set(expected_source_docs))
            for dep in body:
                expected_edges[(dep, head)] += 1
                if dep not in nodes:
                    error(f"certificate omits witness dependency {dep} required by {head}")
                elif order_index.get(dep, len(raw_order)) >= order_index.get(head, -1):
                    error(f"dependency is not before its head in topological_order: {dep} -> {head}")
                if dep not in witness_by_head or witness_by_head[dep].get("proof_depth", depth) >= depth:
                    error(f"witness dependency depth is not strictly smaller: {dep} -> {head}")

        if node.get("witness_clause_index") != expected_clause_index:
            error(f"witness_clause_index mismatch: {head}")
        source_docs = node.get("source_documents")
        if source_docs != expected_source_docs:
            error(f"source_documents mismatch: {head}")

    actual_edges: Counter[tuple[str, str]] = Counter()
    for edge in raw_edges:
        if not isinstance(edge, dict) or not isinstance(edge.get("from"), str) or not isinstance(edge.get("to"), str):
            error("certificate contains a malformed edge")
            continue
        actual_edges[(edge["from"], edge["to"])] += 1
    if actual_edges != expected_edges:
        error("certificate edges do not exactly match selected witness literals")

    if target in nodes:
        reachable: set[str] = set()
        stack = [target]
        while stack:
            head = stack.pop()
            if head in reachable:
                continue
            reachable.add(head)
            reference = witness_by_head.get(head, {})
            body = reference.get("witness_clause", [])
            if isinstance(body, list):
                stack.extend(dep for dep in body if isinstance(dep, str))
        if reachable != set(nodes):
            error("certificate contains nodes outside the target's witness DAG or omits reachable nodes")

    return {"valid": not errors, "target": target, "node_count": len(nodes),
            "edge_count": len(raw_edges), "errors": errors,
            "claim_type": CLAIM_TYPE,
            "bundle_integrity": integrity,
            "scope_note": "Validates only structural witness replay against the frozen bundle, not semantic support from source text."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path, help="exported witness JSON")
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    certificate = json.loads(args.certificate.read_text(encoding="utf-8"))
    result = verify_witness_certificate(certificate, args.bundle.resolve(), args.integrity_lock.resolve())
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
