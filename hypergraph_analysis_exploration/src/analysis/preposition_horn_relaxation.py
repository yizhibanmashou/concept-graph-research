"""Measure how removing preposition literals relaxes the full Horn hypergraph.

This is a structural counterfactual, not a semantics-preserving graph rewrite.
All non-preposition conjuncts and OR alternatives are kept intact.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import json
import statistics
from collections import defaultdict
from pathlib import Path

from src.analysis.frozen_bundle_integrity import verify_frozen_bundle_integrity
from src.analysis.frozen_hypergraph_audit import DEFAULT_BUNDLE, load_graph
from src.analysis.minimum_witness_audit import minimum_derivation_depths


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT.parent / "report" / "preposition_horn_relaxation_2026-10-28.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relax_preposition_literals(
    clauses: list[tuple[str, tuple[str, ...]]],
    pos_by_node: dict[str, str],
) -> tuple[list[tuple[str, tuple[str, ...]]], dict[str, int]]:
    """Drop preposition dependencies while retaining every other literal."""
    relaxed: list[tuple[str, tuple[str, ...]]] = []
    clauses_with_preposition = 0
    removed_literals = 0
    newly_empty_clauses = 0
    for head, body in clauses:
        kept = tuple(dep for dep in body if pos_by_node.get(dep) != "prep")
        removed = len(body) - len(kept)
        if removed:
            clauses_with_preposition += 1
            removed_literals += removed
            if not kept:
                newly_empty_clauses += 1
        relaxed.append((head, kept))
    return relaxed, {
        "clauses_with_preposition_literals": clauses_with_preposition,
        "removed_preposition_literals": removed_literals,
        "newly_empty_clauses": newly_empty_clauses,
    }


def summarize_depths(depths: list[int]) -> dict[str, int | float | None]:
    if not depths:
        return {"count": 0, "min": None, "median": None, "p90": None, "max": None}
    ordered = sorted(depths)
    return {
        "count": len(ordered),
        "min": ordered[0],
        "median": statistics.median(ordered),
        "p90": ordered[int(0.9 * (len(ordered) - 1))],
        "max": ordered[-1],
    }


def minimum_derivation_depths_allow_unreachable(
    heads: set[str], clauses: list[tuple[str, tuple[str, ...]]], basis: set[str]
) -> dict[str, int]:
    """Return grounded depths without rejecting heads made unreachable by ablation."""
    remaining = [len(body) for _, body in clauses]
    max_dependency_depth = [0] * len(clauses)
    clauses_by_dependency: dict[str, list[int]] = defaultdict(list)
    for clause_index, (head, body) in enumerate(clauses):
        if head not in heads or any(dependency not in heads for dependency in body):
            raise ValueError("clause refers to a node outside the graph head set")
        for dependency in body:
            clauses_by_dependency[dependency].append(clause_index)

    depths = {seed: 0 for seed in basis}
    queue = [(0, seed) for seed in basis]
    heapq.heapify(queue)
    settled: set[str] = set()
    for clause_index, (_, body) in enumerate(clauses):
        if not body:
            head = clauses[clause_index][0]
            if head not in basis and depths.get(head, 2**63) > 1:
                depths[head] = 1
                heapq.heappush(queue, (1, head))

    while queue:
        depth, node = heapq.heappop(queue)
        if node in settled or depths.get(node) != depth:
            continue
        settled.add(node)
        for clause_index in clauses_by_dependency.get(node, ()):
            remaining[clause_index] -= 1
            max_dependency_depth[clause_index] = max(max_dependency_depth[clause_index], depth)
            if remaining[clause_index] == 0:
                head = clauses[clause_index][0]
                candidate = max_dependency_depth[clause_index] + 1
                if head not in basis and candidate < depths.get(head, 2**63):
                    if head in settled:
                        raise ValueError("minimum-depth relaxation improved an already settled node")
                    depths[head] = candidate
                    heapq.heappush(queue, (candidate, head))
    return depths


def run(bundle: Path) -> dict:
    bundle = bundle.resolve()
    integrity = verify_frozen_bundle_integrity(bundle)
    if not integrity.get("valid"):
        raise ValueError(f"frozen bundle integrity check failed: {integrity.get('errors')}")

    rules, clauses, literal_count = load_graph(bundle)
    heads = set(rules)
    basis = {
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    with (bundle / "graph" / "nodes.tsv").open(encoding="utf-8-sig", newline="") as stream:
        pos_by_node = {
            row["synset_id"]: row["pos"]
            for row in csv.DictReader(stream, delimiter="\t")
        }
    if set(pos_by_node) != heads:
        raise ValueError("node inventory and Horn rule heads do not align")

    original_depths = minimum_derivation_depths(heads, clauses, basis)
    relaxed_clauses, intervention = relax_preposition_literals(clauses, pos_by_node)
    # Removing the only conjunct would turn a rule into a fact. Also report a
    # conservative variant that drops only those newly empty alternatives.
    guarded_clauses = [
        relaxed
        for original, relaxed in zip(clauses, relaxed_clauses, strict=True)
        if original[1] == () or relaxed[1]
    ]
    relaxed_depths = minimum_derivation_depths(heads, relaxed_clauses, basis)
    guarded_depths = minimum_derivation_depths_allow_unreachable(heads, guarded_clauses, basis)
    reductions = {
        head: original_depths[head] - relaxed_depths[head]
        for head in heads
    }
    guarded_reductions = {head: original_depths[head] - depth for head, depth in guarded_depths.items()}
    if any(reduction < 0 for reduction in reductions.values()):
        raise ValueError("removing conjuncts unexpectedly increased a minimum derivation depth")

    by_pos: dict[str, list[int]] = defaultdict(list)
    for head, reduction in reductions.items():
        by_pos[pos_by_node[head]].append(reduction)
    guarded_by_pos: dict[str, list[int]] = defaultdict(list)
    for head, reduction in guarded_reductions.items():
        guarded_by_pos[pos_by_node[head]].append(reduction)

    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    input_paths = [
        bundle / "manifest.json",
        bundle / "checksums.jsonl",
        bundle / "graph" / "nodes.tsv",
        bundle / "graph" / "hypergraph_rules.jsonl",
        bundle / "graph" / "selected_basis_atoms.txt",
    ]
    return {
        "analysis": "preposition-horn-literal-relaxation/1",
        "bundle_semantic_fingerprint_sha256": manifest.get("semantic_fingerprint_sha256"),
        "head_count": len(heads),
        "basis_count": len(basis),
        "clause_count": len(clauses),
        "original_literal_count": literal_count,
        "intervention": "remove every POS=prep dependency literal from every AND clause; preserve heads, all other literals, and OR alternatives",
        "integrity_lock_valid": integrity.get("valid"),
        "change_counts": intervention,
        "guarded_clause_count": len(guarded_clauses),
        "baseline_depth": summarize_depths(list(original_depths.values())),
        "baseline_depth_for_heads_reachable_after_drop": summarize_depths(
            [original_depths[head] for head in guarded_depths]
        ),
        "relaxed_depth_keep_empty_as_facts": summarize_depths(list(relaxed_depths.values())),
        "relaxed_depth_drop_newly_empty_clauses": summarize_depths(list(guarded_depths.values())),
        "unreachable_heads_drop_newly_empty_clauses": len(heads - set(guarded_depths)),
        "depth_reduction_keep_empty_as_facts": {
            "heads_with_any_reduction": sum(value > 0 for value in reductions.values()),
            "heads_with_no_reduction": sum(value == 0 for value in reductions.values()),
            "distribution": summarize_depths(list(reductions.values())),
            "by_head_pos": {pos: summarize_depths(values) for pos, values in sorted(by_pos.items())},
        },
        "depth_reduction_drop_newly_empty_clauses": {
            "heads_with_any_reduction": sum(value > 0 for value in guarded_reductions.values()),
            "heads_with_no_reduction": sum(value == 0 for value in guarded_reductions.values()),
            "distribution": summarize_depths(list(guarded_reductions.values())),
            "by_head_pos": {
                pos: summarize_depths(values) for pos, values in sorted(guarded_by_pos.items())
            },
        },
        "input_sha256": {str(path.relative_to(bundle)): _sha256(path) for path in input_paths},
        "limits": [
            "This deletes dependency conditions and can create empty-body clauses; it is deliberately an over-relaxation, not a semantics-preserving rewrite.",
            "A shorter derivation does not show that the original preposition relation was wrong or that the relaxed definition is true.",
            "Minimum proof depth is a graph property, not cognitive acquisition time or human comprehensibility.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.bundle)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({
        "head_count": result["head_count"],
        "clauses_with_preposition_literals": result["change_counts"]["clauses_with_preposition_literals"],
        "removed_preposition_literals": result["change_counts"]["removed_preposition_literals"],
        "heads_with_any_depth_reduction_drop_newly_empty": result["depth_reduction_drop_newly_empty_clauses"]["heads_with_any_reduction"],
        "unreachable_heads_drop_newly_empty": result["unreachable_heads_drop_newly_empty_clauses"],
        "baseline_depth": result["baseline_depth"],
        "baseline_depth_for_heads_reachable_after_drop": result["baseline_depth_for_heads_reachable_after_drop"],
        "relaxed_depth_drop_newly_empty_clauses": result["relaxed_depth_drop_newly_empty_clauses"],
        "output": str(args.out),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
