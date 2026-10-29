"""Compute shortest grounded proof-depth witnesses for the frozen Horn graph.

For each OR-of-AND rule, derivation depth is 0 for basis atoms and otherwise
1 + max(depth(dependency)) for a selected clause. The algorithm treats each
clause as an AND hyperedge and computes the minimum achievable depth. It does
not assign truth-conditional meaning to graph atoms or glosses.
"""
from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.analysis.frozen_hypergraph_audit import (
    DEFAULT_BUNDLE,
    jsonl,
    load_graph,
    validate_witnesses,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase14" / "minimum_witness_audit.json"


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


def distribution_summary(values: list[int]) -> dict[str, int | float | None]:
    """Public summary helper for related structural witness audits."""
    return _distribution(values)


def minimum_derivation_depths(
    heads: set[str], clauses: list[tuple[str, tuple[str, ...]]], basis: set[str]
) -> dict[str, int]:
    """Find the least grounded derivation height for every head.

    A clause becomes available only after all its dependencies have been
    settled. Its candidate head depth is one plus the maximum dependency depth.
    The priority queue settles heads in nondecreasing depth, so cyclic clauses
    without a path from the basis cannot bootstrap themselves.
    """
    if not basis <= heads:
        raise ValueError("basis contains nodes absent from the graph")
    clause_heads: list[str] = []
    remaining: list[int] = []
    max_dependency_depth: list[int] = []
    clauses_by_dependency: dict[str, list[int]] = defaultdict(list)
    for clause_index, (head, body) in enumerate(clauses):
        if head not in heads or any(dependency not in heads for dependency in body):
            raise ValueError("clause refers to a node outside the graph head set")
        clause_heads.append(head)
        remaining.append(len(body))
        max_dependency_depth.append(0)
        for dependency in body:
            clauses_by_dependency[dependency].append(clause_index)

    depths: dict[str, int] = {}
    settled: set[str] = set()
    queue: list[tuple[int, str]] = []
    for seed in sorted(basis):
        depths[seed] = 0
        heapq.heappush(queue, (0, seed))

    for clause_index, unresolved in enumerate(remaining):
        if unresolved == 0:
            head = clause_heads[clause_index]
            candidate = 1
            if head not in basis:
                old = depths.get(head)
                if old is None or candidate < old:
                    depths[head] = candidate
                    heapq.heappush(queue, (candidate, head))

    while queue:
        depth, node = heapq.heappop(queue)
        if node in settled or depths.get(node) != depth:
            continue
        settled.add(node)
        for clause_index in clauses_by_dependency.get(node, ()):
            remaining[clause_index] -= 1
            max_dependency_depth[clause_index] = max(max_dependency_depth[clause_index], depth)
            if remaining[clause_index] != 0:
                continue
            head = clause_heads[clause_index]
            if head in basis:
                continue
            candidate = max_dependency_depth[clause_index] + 1
            old = depths.get(head)
            if old is None or candidate < old:
                if head in settled:
                    raise ValueError("minimum-depth relaxation improved an already settled node")
                depths[head] = candidate
                heapq.heappush(queue, (candidate, head))

    if set(depths) != heads:
        raise ValueError(f"{len(heads - set(depths))} graph head(s) have no grounded derivation from the basis")
    return depths


def minimum_depth_clauses_by_head(
    heads: set[str], clauses: list[tuple[str, tuple[str, ...]]], depths: dict[str, int], basis: set[str]
) -> dict[str, list[tuple[str, ...]]]:
    result: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    for head, body in clauses:
        if head in basis:
            continue
        candidate_depth = 1 + max((depths[dependency] for dependency in body), default=0)
        if candidate_depth == depths[head]:
            result[head].append(body)
    missing = heads - basis - set(result)
    if missing:
        raise ValueError(f"{len(missing)} non-basis head(s) lack a minimum-depth clause")
    return result


def _witness_rows(heads: set[str], basis: set[str], depths: dict[str, int], clauses_by_head: dict[str, list[tuple[str, ...]]]) -> list[dict[str, Any]]:
    rows = []
    for head in sorted(heads):
        if head in basis:
            rows.append({"head": head, "is_seed": True, "proof_depth": 0, "witness_clause": []})
        else:
            body = min(clauses_by_head[head])
            rows.append({"head": head, "is_seed": False, "proof_depth": depths[head], "witness_clause": list(body)})
    return rows


def _dag_profile(witnesses: dict[str, dict[str, Any]], basis: set[str], heads: set[str]) -> dict[str, Any]:
    fanout: Counter[str] = Counter(
        dependency
        for head, row in witnesses.items()
        if head not in basis
        for dependency in row["witness_clause"]
    )
    fanout_values = [fanout.get(head, 0) for head in heads]
    return {
        "edge_count": sum(len(row["witness_clause"]) for head, row in witnesses.items() if head not in basis),
        "dependency_parent_count_including_zero_use_heads": {
            **_distribution(fanout_values),
            "zero_use_head_count": sum(value == 0 for value in fanout_values),
        },
        "basis_atoms_used_as_dependencies": sum(fanout.get(seed, 0) > 0 for seed in basis),
        "basis_atoms_unused_as_dependencies": sum(fanout.get(seed, 0) == 0 for seed in basis),
    }


def build_report(bundle: Path) -> dict[str, Any]:
    bundle = bundle.resolve()
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    witness_path = bundle / "graph" / "coverage_witnesses.jsonl"
    rules, clauses, literal_count = load_graph(bundle)
    heads = set(rules)
    basis = {
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt")
        .read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    selected_check = validate_witnesses(heads, basis, rules, list(jsonl(witness_path)))
    if not selected_check["all_valid"]:
        raise ValueError("the frozen selected-witness certificate failed structural validation")

    min_depths = minimum_derivation_depths(heads, clauses, basis)
    minimizing_clauses = minimum_depth_clauses_by_head(heads, clauses, min_depths, basis)
    min_rows = _witness_rows(heads, basis, min_depths, minimizing_clauses)
    min_check = validate_witnesses(heads, basis, rules, min_rows)
    if not min_check["all_valid"]:
        raise ValueError("the derived minimum-depth witness certificate failed structural replay")

    selected = selected_check["witness_by_head"]
    slack = {
        head: selected[head]["proof_depth"] - min_depths[head]
        for head in heads
    }
    if any(value < 0 for value in slack.values()):
        raise ValueError("selected witness depth is below the computed grounded minimum")
    min_alt_counts = [len(minimizing_clauses[head]) for head in heads - basis]
    graph_sha = hashlib.sha256(rules_path.read_bytes()).hexdigest()
    if manifest.get("graph_sha256") and graph_sha != manifest["graph_sha256"]:
        raise ValueError("graph rules hash does not match the bundle manifest")
    selected_hash = hashlib.sha256(witness_path.read_bytes()).hexdigest()
    return {
        "audit_version": "minimum-witness-depth/1",
        "graph_rules_sha256": graph_sha,
        "selected_witnesses_sha256": selected_hash,
        "graph_size": {
            "head_count": len(heads),
            "clause_count": len(clauses),
            "dependency_literal_count": literal_count,
            "basis_count": len(basis),
        },
        "minimum_grounded_derivation_depth": _distribution(list(min_depths.values())),
        "minimum_depth_tied_clause_count_per_nonbasis_head": _distribution(min_alt_counts),
        "selected_witness_vs_minimum_depth": {
            "heads_at_minimum_depth": sum(value == 0 for value in slack.values()),
            "heads_with_extra_depth": sum(value > 0 for value in slack.values()),
            "depth_slack_distribution": _distribution(list(slack.values())),
        },
        "selected_witness_dag": _dag_profile(selected, basis, heads),
        "canonical_minimum_depth_witness_dag": _dag_profile(min_check["witness_by_head"], basis, heads),
        "certificate_validation": {
            "input_selected_witnesses_valid": selected_check["all_valid"],
            "minimum_depth_witnesses_valid": min_check["all_valid"],
            "minimum_depth_invalid_witness_count": min_check["invalid_head_count"],
        },
        "raw_text_emitted": False,
        "identities_emitted": False,
        "limitations": [
            "Minimum depth is measured in the frozen positive Horn dependency graph; it is not a semantic entailment distance.",
            "The canonical tie-break selects the lexicographically smallest minimum-depth clause; it does not optimize evidence quality or source faithfulness.",
            "A replayable certificate validates the encoded rules only and does not prove that glosses support those rules.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
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
    print(f"Wrote minimum-depth witness audit: {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
