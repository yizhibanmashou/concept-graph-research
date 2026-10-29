"""Audit cycles in the simple-arc projection of all frozen Horn clauses.

Each dependency literal d in a clause headed by h contributes a directed
projection arc d -> h. Strongly connected components describe only this
over-approximate simple graph; they do not establish cyclic Horn derivations
because a projected edge ignores the other conjuncts in its hyperedge.
"""
from __future__ import annotations

import argparse
import array
import hashlib
import json
import statistics
from pathlib import Path
from typing import Iterable

from src.analysis.frozen_hypergraph_audit import (
    DEFAULT_BUNDLE,
    jsonl,
    load_graph,
    validate_witnesses,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase13" / "dependency_projection_scc.json"


def _distribution(values: list[int]) -> dict[str, int | float | None]:
    if not values:
        return {"count": 0, "min": None, "median": None, "p90": None, "max": None}
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "min": ordered[0],
        "median": statistics.median(ordered),
        "p90": ordered[int(0.9 * (len(ordered) - 1))],
        "max": ordered[-1],
    }


def _strong_components(node_count: int, encoded_edges: set[int]) -> tuple[list[int], list[int]]:
    """Return component ID per node and component sizes using iterative Kosaraju."""
    if node_count < 0 or node_count >= 2**32:
        raise ValueError("node_count must fit in an unsigned 32-bit adjacency index")
    edge_count = len(encoded_edges)
    if edge_count >= 2**32:
        raise ValueError("projected edge count exceeds the supported unsigned 32-bit range")

    out_degree = [0] * node_count
    in_degree = [0] * node_count
    for encoded in encoded_edges:
        source, target = divmod(encoded, node_count)
        out_degree[source] += 1
        in_degree[target] += 1

    out_offsets = [0] * (node_count + 1)
    in_offsets = [0] * (node_count + 1)
    for node in range(node_count):
        out_offsets[node + 1] = out_offsets[node] + out_degree[node]
        in_offsets[node + 1] = in_offsets[node] + in_degree[node]

    out_neighbors = array.array("I", [0]) * edge_count
    in_neighbors = array.array("I", [0]) * edge_count
    out_cursor = out_offsets[:-1].copy()
    in_cursor = in_offsets[:-1].copy()
    for encoded in encoded_edges:
        source, target = divmod(encoded, node_count)
        out_neighbors[out_cursor[source]] = target
        out_cursor[source] += 1
        in_neighbors[in_cursor[target]] = source
        in_cursor[target] += 1

    visited = bytearray(node_count)
    finish_order: list[int] = []
    for root in range(node_count):
        if visited[root]:
            continue
        visited[root] = 1
        stack = [(root, out_offsets[root])]
        while stack:
            node, cursor = stack[-1]
            end = out_offsets[node + 1]
            if cursor < end:
                neighbor = out_neighbors[cursor]
                stack[-1] = (node, cursor + 1)
                if not visited[neighbor]:
                    visited[neighbor] = 1
                    stack.append((neighbor, out_offsets[neighbor]))
            else:
                finish_order.append(node)
                stack.pop()

    component_by_node = [-1] * node_count
    component_sizes: list[int] = []
    for root in reversed(finish_order):
        if component_by_node[root] != -1:
            continue
        component_id = len(component_sizes)
        component_by_node[root] = component_id
        stack = [root]
        size = 0
        while stack:
            node = stack.pop()
            size += 1
            for edge_index in range(in_offsets[node], in_offsets[node + 1]):
                neighbor = in_neighbors[edge_index]
                if component_by_node[neighbor] == -1:
                    component_by_node[neighbor] = component_id
                    stack.append(neighbor)
        component_sizes.append(size)
    return component_by_node, component_sizes


def analyze_projection(heads: set[str], clauses: list[tuple[str, tuple[str, ...]]], basis: set[str], witness_by_head: dict[str, dict]) -> dict:
    nodes = sorted(heads | {dependency for _, body in clauses for dependency in body})
    node_index = {node: index for index, node in enumerate(nodes)}
    node_count = len(nodes)
    encoded_edges: set[int] = set()
    for head, body in clauses:
        target = node_index[head]
        for dependency in body:
            source = node_index[dependency]
            encoded_edges.add(source * node_count + target)

    component_by_node, component_sizes = _strong_components(node_count, encoded_edges)
    self_loop_nodes = set()
    internal_cyclic_arcs = 0
    for encoded in encoded_edges:
        source, target = divmod(encoded, node_count)
        if source == target:
            self_loop_nodes.add(source)
    cyclic_component_ids = {
        component_id
        for component_id, size in enumerate(component_sizes)
        if size > 1
    } | {
        component_by_node[node] for node in self_loop_nodes
    }
    cyclic_sizes = [component_sizes[component_id] for component_id in cyclic_component_ids]
    cyclic_node_count = sum(cyclic_sizes)
    for encoded in encoded_edges:
        source, target = divmod(encoded, node_count)
        component_id = component_by_node[source]
        if component_id == component_by_node[target] and component_id in cyclic_component_ids:
            internal_cyclic_arcs += 1

    selected_edge_count = 0
    selected_encoded_edges: set[int] = set()
    selected_depths = {
        head: row.get("proof_depth")
        for head, row in witness_by_head.items()
        if isinstance(row.get("proof_depth"), int) and not isinstance(row.get("proof_depth"), bool)
    }
    selected_depths_strict = True
    for head, row in witness_by_head.items():
        if head in basis:
            continue
        body = row.get("witness_clause")
        if not isinstance(body, list):
            selected_depths_strict = False
            continue
        selected_edge_count += len(body)
        target = node_index[head]
        for dependency in body:
            source = node_index[dependency]
            selected_encoded_edges.add(source * node_count + target)
            if selected_depths.get(dependency, -1) >= selected_depths.get(head, -1):
                selected_depths_strict = False

    return {
        "projection_direction": "dependency_to_head",
        "node_count": node_count,
        "head_nodes_without_dependencies": len(heads - {dependency for _, body in clauses for dependency in body}),
        "raw_dependency_literal_count": sum(len(body) for _, body in clauses),
        "unique_projected_arc_count": len(encoded_edges),
        "repeated_projected_arc_count_across_alternative_clauses": sum(len(body) for _, body in clauses) - len(encoded_edges),
        "strongly_connected_component_count": len(component_sizes),
        "cyclic_component_count": len(cyclic_component_ids),
        "nodes_in_cyclic_components": cyclic_node_count,
        "cyclic_component_size_distribution": _distribution(cyclic_sizes),
        "self_loop_arc_count": len(self_loop_nodes),
        "arcs_internal_to_cyclic_components": internal_cyclic_arcs,
        "selected_witness": {
            "raw_dependency_count": selected_edge_count,
            "unique_projected_arc_count": len(selected_encoded_edges),
            "strict_depth_increase_dependency_to_head": selected_depths_strict,
            "selected_arcs_internal_to_full_projection_cyclic_components": sum(
                1 for encoded in selected_encoded_edges
                if component_by_node[encoded // node_count]
                == component_by_node[encoded % node_count]
                and component_by_node[encoded // node_count] in cyclic_component_ids
            ),
        },
        "limitations": [
            "The simple-arc projection removes the AND grouping of each Horn hyperedge; a cyclic SCC is not itself a cyclic or circular Horn proof.",
            "OR alternatives remain projected together. Cyclic components identify where alternative dependencies mutually reach, not whether those alternatives are semantically valid.",
            "Selected-witness depth monotonicity verifies acyclicity of the chosen witness relation only; it does not validate gloss semantics.",
        ],
    }


def build_report(bundle: Path) -> dict:
    bundle = bundle.resolve()
    rules, clauses, _ = load_graph(bundle)
    heads = set(rules)
    basis = {
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt")
        .read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    witness_check = validate_witnesses(
        heads, basis, rules, list(jsonl(bundle / "graph" / "coverage_witnesses.jsonl"))
    )
    if not witness_check["all_valid"]:
        raise ValueError("the frozen witness certificate failed structural validation")
    graph_path = bundle / "graph" / "hypergraph_rules.jsonl"
    digest = hashlib.sha256(graph_path.read_bytes()).hexdigest()
    return {
        "audit_version": "dependency-projection-scc/1",
        "graph_rules_sha256": digest,
        "graph_size": {
            "head_count": len(heads),
            "clause_count": len(clauses),
            "dependency_literal_count": sum(len(body) for _, body in clauses),
            "basis_count": len(basis),
        },
        "projection_scc": analyze_projection(heads, clauses, basis, witness_check["witness_by_head"]),
        "witness_certificate_validation": {
            "all_valid": witness_check["all_valid"],
            "invalid_witnesses": witness_check["invalid_head_count"],
        },
        "raw_text_emitted": False,
        "identities_emitted": False,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error(f"output exists; pass --force to replace: {output}")
    try:
        report = build_report(args.bundle)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote dependency-projection SCC audit: {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
