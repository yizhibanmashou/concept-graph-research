"""Export a bounded source-linked witness DAG for one frozen graph head.

The output certifies Horn-closure availability only; it is not a semantic proof.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:  # Direct script execution and package/module execution are both supported.
    from .frozen_hypergraph_audit import DEFAULT_BUNDLE, PROJECT_ROOT, jsonl
except ImportError:
    from frozen_hypergraph_audit import DEFAULT_BUNDLE, PROJECT_ROOT, jsonl


def export_witness(bundle: Path, target: str, max_nodes: int):
    rules = {row["head"]: row["clauses"] for row in jsonl(bundle / "graph" / "hypergraph_rules.jsonl")}
    witnesses = {row["head"]: row for row in jsonl(bundle / "graph" / "coverage_witnesses.jsonl")}
    senses = {row["identity"]: row for row in jsonl(bundle / "indexes" / "senses.jsonl")}
    if target not in witnesses:
        raise ValueError(f"Unknown target head: {target}")
    visited, ordered, edges, active = set(), [], [], set()

    def visit(head):
        if head in visited:
            return
        if head in active:
            raise ValueError(f"Cycle in witness pointers at {head}")
        if len(visited) >= max_nodes:
            raise ValueError(f"Witness exceeds --max-nodes={max_nodes}; choose a larger bound")
        active.add(head)
        record = witnesses[head]
        body = record.get("witness_clause", [])
        depth = record["proof_depth"]
        if record.get("is_seed"):
            if body or depth != 0:
                raise ValueError(f"Malformed seed witness: {head}")
            source_docs = []
            active_clause = None
        else:
            body_sorted = sorted(body)
            matching = [i for i, clause in enumerate(rules[head]) if sorted(clause) == body_sorted]
            if not matching:
                raise ValueError(f"Witness clause not found among rules: {head}")
            active_clause = matching[0]
            source_docs = []
            for source in senses.get(head, {}).get("active_clause_sources", []):
                if source.get("clause_index") == active_clause:
                    source_docs.extend(source.get("source_documents", []))
            for dep in body:
                if dep not in witnesses or witnesses[dep]["proof_depth"] >= depth:
                    raise ValueError(f"Non-decreasing or missing witness dependency: {head} -> {dep}")
                edges.append({"from": dep, "to": head})
                visit(dep)
        active.remove(head)
        visited.add(head)
        ordered.append({
            "id": head,
            "proof_depth": depth,
            "is_seed": bool(record.get("is_seed")),
            "witness_clause_index": active_clause,
            "witness_clause": body,
            "source_documents": sorted(set(source_docs)),
        })

    visit(target)
    return {
        "claim_type": "structural_definitional_availability_not_truth_conditional_entailment",
        "graph_semantic_fingerprint_sha256": json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))["semantic_fingerprint_sha256"],
        "target": target,
        "node_count": len(ordered),
        "edge_count": len(edges),
        "topological_order": [node["id"] for node in ordered],
        "nodes": ordered,
        "edges": edges,
        "limitations": [
            "Edges encode prerequisites in the selected Horn witness, not ordinary semantic entailment.",
            "Source documents identify the active decomposition record; clause evidence still needs semantic review.",
            "This single-witness DAG is not necessarily the shortest or only derivation.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="exact frozen head/sense identifier")
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--max-nodes", type=int, default=10000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.max_nodes < 1:
        parser.error("--max-nodes must be positive")
    result = export_witness(args.bundle.resolve(), args.target, args.max_nodes)
    output = args.output.resolve() if args.output else PROJECT_ROOT / "outputs" / "phase6" / f"witness_{args.target}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {result['node_count']} nodes and {result['edge_count']} prerequisite edges to {output}")


if __name__ == "__main__":
    main()
