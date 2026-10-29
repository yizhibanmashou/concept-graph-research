"""Summarize structural complexity strata in the frozen Horn witness graph.

The report is intended to support sampling and later evaluation design. It does
not estimate semantic difficulty or natural-language entailment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path

from src.analysis.frozen_hypergraph_audit import (
    DEFAULT_BUNDLE,
    jsonl,
    load_graph,
    validate_witnesses,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEPTH_BINS = (
    (0, 0, "0"),
    (1, 5, "1-5"),
    (6, 25, "6-25"),
    (26, 100, "26-100"),
    (101, 300, "101-300"),
    (301, None, "301+"),
)


def distribution(values: list[int]) -> dict:
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


def depth_bin(depth: int) -> str:
    for lower, upper, label in DEPTH_BINS:
        if depth >= lower and (upper is None or depth <= upper):
            return label
    raise ValueError(f"Unsupported negative witness depth: {depth}")


def build_profile(bundle: Path) -> dict:
    rules, clauses, literal_count = load_graph(bundle)
    heads = set(rules)
    basis = {
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt")
        .read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    witness_rows = list(jsonl(bundle / "graph" / "coverage_witnesses.jsonl"))
    witness_check = validate_witnesses(heads, basis, rules, witness_rows)
    witnesses = witness_check["witness_by_head"]

    clause_count_by_head = {head: len(body_list) for head, body_list in rules.items()}
    dependency_fanout = Counter(dep for _, body in clauses for dep in body)
    selected_witness_fanout = Counter(
        dep
        for head, row in witnesses.items()
        if head not in basis
        and isinstance(row.get("witness_clause"), list)
        and all(isinstance(dep, str) for dep in row["witness_clause"])
        for dep in row["witness_clause"]
    )
    valid_depths = {
        head: row["proof_depth"]
        for head, row in witnesses.items()
        if isinstance(row.get("proof_depth"), int)
        and not isinstance(row.get("proof_depth"), bool)
        and row["proof_depth"] >= 0
    }
    selected_widths = {
        head: len(row["witness_clause"])
        for head, row in witnesses.items()
        if isinstance(row.get("witness_clause"), list)
        and all(isinstance(dep, str) for dep in row["witness_clause"])
    }

    depth_strata = {}
    for lower, upper, label in DEPTH_BINS:
        stratum_heads = [
            head for head, depth in valid_depths.items()
            if depth >= lower and (upper is None or depth <= upper)
        ]
        alt_counts = [clause_count_by_head[head] for head in stratum_heads]
        stratum_widths = [selected_widths[head] for head in stratum_heads if head in selected_widths]
        depth_strata[label] = {
            "head_count": len(stratum_heads),
            "heads_with_multiple_alternatives": sum(count > 1 for count in alt_counts),
            "fraction_with_multiple_alternatives": (
                sum(count > 1 for count in alt_counts) / len(alt_counts) if alt_counts else None
            ),
            "alternative_clause_count": distribution(alt_counts),
            "selected_witness_and_width": distribution(stratum_widths),
        }

    selected_witness_depth_strata = {}
    for _, _, label in DEPTH_BINS:
        stratum_heads = [
            head for head, depth in valid_depths.items()
            if depth_bin(depth) == label
        ]
        fanouts = [selected_witness_fanout.get(head, 0) for head in stratum_heads]
        selected_witness_depth_strata[label] = {
            "dependency_node_count": len(stratum_heads),
            "referenced_by_other_selected_witnesses": sum(value > 0 for value in fanouts),
            "dependency_parent_count": distribution(fanouts),
        }

    graph_path = bundle / "graph" / "hypergraph_rules.jsonl"
    graph_hash = hashlib.sha256(graph_path.read_bytes()).hexdigest()
    return {
        "claim_type": "structural_complexity_profile_not_semantic_difficulty",
        "bundle": str(bundle),
        "graph_rules_sha256": graph_hash,
        "witness_certificate_validation": {
            "all_valid": witness_check["all_valid"],
            "missing_heads": witness_check["missing_head_count"],
            "unexpected_heads": witness_check["unexpected_head_count"],
            "duplicate_heads": witness_check["duplicate_head_count"],
            "invalid_witnesses": witness_check["invalid_head_count"],
        },
        "graph_size": {
            "head_count": len(heads),
            "clause_count": len(clauses),
            "dependency_literal_count": literal_count,
            "basis_count": len(basis),
        },
        "head_alternative_clause_count": distribution(list(clause_count_by_head.values())),
        "heads_with_multiple_alternative_clauses": sum(
            count > 1 for count in clause_count_by_head.values()
        ),
        "all_clause_and_width": distribution([len(body) for _, body in clauses]),
        "selected_witness_depth": distribution(list(valid_depths.values())),
        "selected_witness_and_width": distribution(list(selected_widths.values())),
        "dependency_clause_reference_fanout_including_zero_use_heads": {
            **distribution([dependency_fanout.get(head, 0) for head in heads]),
            "zero_use_head_count": sum(dependency_fanout.get(head, 0) == 0 for head in heads),
        },
        "selected_witness_dag": {
            "edge_count": sum(
                len(row["witness_clause"])
                for head, row in witnesses.items()
                if head not in basis
                and isinstance(row.get("witness_clause"), list)
                and all(isinstance(dep, str) for dep in row["witness_clause"])
            ),
            "dependency_parent_count_including_zero_use_heads": {
                **distribution([selected_witness_fanout.get(head, 0) for head in heads]),
                "zero_use_head_count": sum(selected_witness_fanout.get(head, 0) == 0 for head in heads),
            },
            "basis_atoms_used_as_dependencies": sum(selected_witness_fanout.get(head, 0) > 0 for head in basis),
            "basis_atoms_unused_as_dependencies": sum(selected_witness_fanout.get(head, 0) == 0 for head in basis),
            "depth_strata_by_dependency_node": selected_witness_depth_strata,
        },
        "depth_strata": depth_strata,
        "limitations": [
            "Depth and selected clause width describe the package's chosen structural witness, not the optimal proof or semantic difficulty.",
            "Alternative-clause counts describe OR alternatives in the encoded rules, not independently validated natural-language readings.",
            "Dependency fanout counts literal references across all clauses and is not a semantic importance score.",
            "Selected-witness fanout counts parents in the package's chosen one-witness-per-head DAG; it is not all-proof provenance or semantic importance.",
            "The profile cannot establish gloss-to-rule faithfulness or entailment validity.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument(
        "--output", type=Path,
        default=PROJECT_ROOT / "outputs" / "phase6" / "hypergraph_complexity_profile.json",
    )
    parser.add_argument("--force", action="store_true", help="replace the existing report")
    args = parser.parse_args()
    if args.output.exists() and not args.force:
        raise SystemExit(f"Output exists; pass --force to replace: {args.output}")
    report = build_profile(args.bundle.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote structural complexity profile: {args.output}")


if __name__ == "__main__":
    main()
