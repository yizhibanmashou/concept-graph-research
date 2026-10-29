"""Measure structural information loss under two naive graph flattenings.

The canonical rules use head := OR(AND(body)). The relaxed arc baseline treats
each dependency literal as an independent sufficient singleton rule; the strict
arc baseline treats the union of all incoming dependencies as one conjunction.
These are diagnostic semantics, not proposed inference methods.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable

from src.analysis.frozen_hypergraph_audit import DEFAULT_BUNDLE, closure, load_graph
from src.analysis.minimum_witness_audit import minimum_derivation_depths


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase21" / "flattening_ablation.json"


def _comparison(reference: set[str], candidate: set[str], head_count: int) -> dict:
    extra = candidate - reference
    missed = reference - candidate
    return {
        "derived_count": len(candidate),
        "agreement_count": head_count - len(extra) - len(missed),
        "overgenerated_count": len(extra),
        "undergenerated_count": len(missed),
        "exact_match": not extra and not missed,
    }


def _distribution(values: list[int]) -> dict:
    ordered = sorted(values)
    if not ordered:
        return {"count": 0, "min": None, "median": None, "p90": None, "max": None}
    return {
        "count": len(ordered),
        "min": ordered[0],
        "median": statistics.median(ordered),
        "p90": ordered[int(0.9 * (len(ordered) - 1))],
        "max": ordered[-1],
    }


def simple_arc_shortest_depths(
    heads: set[str], clauses: list[tuple[str, tuple[str, ...]]], basis: set[str]
) -> dict[str, int]:
    """Compute shortest dependency-to-head path lengths from the basis."""
    outgoing: dict[str, set[str]] = defaultdict(set)
    for head, body in clauses:
        if head not in heads or any(dependency not in heads for dependency in body):
            raise ValueError("clause refers to a node outside the graph head set")
        for dependency in body:
            outgoing[dependency].add(head)
    depths = {seed: 0 for seed in basis}
    queue = deque(sorted(basis))
    while queue:
        dependency = queue.popleft()
        candidate = depths[dependency] + 1
        for head in outgoing.get(dependency, ()):
            if head not in depths:
                depths[head] = candidate
                queue.append(head)
    return depths


def build_report(bundle: Path) -> dict:
    bundle = bundle.resolve()
    rules, clauses, literal_count = load_graph(bundle)
    heads = set(rules)
    basis = {
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt")
        .read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    if not basis <= heads:
        raise ValueError("basis contains atoms absent from the rule-head inventory")

    canonical = closure(heads, clauses, basis)
    canonical_depths = minimum_derivation_depths(heads, clauses, basis)

    # Simple dependency-to-head arcs interpreted as OR over singleton rules.
    relaxed_clauses = [
        (head, (dependency,)) for head, body in clauses for dependency in body
    ]
    relaxed_clauses.extend((head, ()) for head, body in clauses if not body)
    relaxed = closure(heads, relaxed_clauses, basis)
    arc_depths = simple_arc_shortest_depths(heads, clauses, basis)
    if set(arc_depths) != relaxed:
        raise ValueError("simple-arc BFS and singleton-rule closure disagree")
    depth_gaps = {
        head: canonical_depths[head] - arc_depths[head]
        for head in heads
    }
    if any(gap < 0 for gap in depth_gaps.values()):
        raise ValueError("simple-arc path exceeds canonical AND/OR derivation depth")

    # The opposite naive reading: all unique incoming dependencies are required.
    union_clauses = [
        (head, tuple(sorted({dependency for body in body_list for dependency in body})))
        for head, body_list in rules.items()
    ]
    strict = closure(heads, union_clauses, basis)

    graph_path = bundle / "graph" / "hypergraph_rules.jsonl"
    graph_digest = hashlib.sha256(graph_path.read_bytes()).hexdigest()
    return {
        "audit_version": "and-or-flattening-ablation/1",
        "claim_type": "structural_semantics_ablation_not_semantic_accuracy",
        "graph_rules_sha256": graph_digest,
        "graph_size": {
            "head_count": len(heads),
            "clause_count": len(clauses),
            "dependency_literal_count": literal_count,
            "unique_dependency_to_head_arc_count": len({
                (dependency, head) for head, body in clauses for dependency in body
            }),
            "basis_count": len(basis),
        },
        "canonical_and_or_closure": {
            "derived_count": len(canonical),
            "complete": canonical == heads,
            "minimum_grounded_depth": _distribution(list(canonical_depths.values())),
        },
        "flattening_comparisons": {
            "simple_arc_existential_relaxation": {
                **_comparison(canonical, relaxed, len(heads)),
                "interpretation": "any one projected dependency arc suffices for its head",
            },
            "simple_arc_conjunctive_union": {
                **_comparison(canonical, strict, len(heads)),
                "interpretation": "all unique projected dependencies for a head are required together",
            },
        },
        "derivation_depth_information_loss": {
            "simple_arc_shortest_path_depth": _distribution(list(arc_depths.values())),
            "and_or_minus_simple_arc_depth_gap": _distribution(list(depth_gaps.values())),
            "heads_with_strictly_shorter_simple_arc_depth": sum(gap > 0 for gap in depth_gaps.values()),
            "heads_with_equal_depth": sum(gap == 0 for gap in depth_gaps.values()),
            "definition": "For each head, minimum AND/OR proof depth minus shortest dependency-to-head path length in the flattened simple graph.",
        },
        "limitations": [
            "The two flattenings are deliberately simple structural readings, not learned baselines or semantic gold labels.",
            "Over/under-generation is measured only against the frozen package's own AND/OR closure from its declared basis.",
            "This comparison does not establish that the frozen rules are supported by natural-language glosses or that the 85 basis atoms are semantic primitives.",
            "Aggregated closure agreement is not a release-clearance or lexical-relation accuracy result.",
        ],
        "raw_text_emitted": False,
        "identities_emitted": False,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
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
    print(f"Wrote AND/OR flattening ablation: {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
