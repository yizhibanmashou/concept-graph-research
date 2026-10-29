"""Measure proof-tree unfolding pressure in the frozen witness DAG.

The audit compares selected and minimum-depth witness DAGs with their
recursively unfolded proof trees. It can also select a minimum-depth witness
that minimizes recursive tree occurrences, with a deterministic clause-body
tie-break. It uses only the locked formal graph and emits no atom identities,
glosses, or source text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.frozen_bundle_integrity import verify_frozen_bundle_integrity
from src.analysis.frozen_hypergraph_audit import DEFAULT_BUNDLE, jsonl, load_graph, validate_witnesses
from src.analysis.minimum_witness_audit import (
    _witness_rows,
    distribution_summary,
    minimum_depth_clauses_by_head,
    minimum_derivation_depths,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase196" / "witness_tree_expansion_current.json"


def _tree_sizes(witness_by_head: dict[str, dict[str, Any]], basis: set[str], heads: set[str]) -> dict[str, int]:
    sizes: dict[str, int] = {}
    ordered = sorted(heads, key=lambda head: (witness_by_head[head]["proof_depth"], head))
    for head in ordered:
        if head in basis:
            sizes[head] = 1
            continue
        body = witness_by_head[head]["witness_clause"]
        if any(dependency not in sizes for dependency in body):
            raise ValueError("witness dependency is not earlier than its head in proof-depth order")
        sizes[head] = 1 + sum(sizes[dependency] for dependency in body)
    return sizes


def _size_profile(sizes: dict[str, int]) -> dict[str, Any]:
    values = list(sizes.values())
    bit_lengths = [value.bit_length() for value in values]
    total = sum(values)
    return {
        "root_count": len(values),
        "per_root_node_occurrence_bit_length": distribution_summary(bit_lengths),
        "roots_over_node_occurrence_thresholds": {
            str(threshold): sum(value > threshold for value in values)
            for threshold in (10**3, 10**6, 10**12)
        },
        "sum_of_per_root_tree_occurrences_bit_length": total.bit_length(),
    }


def _dag_edge_count(witness_by_head: dict[str, dict[str, Any]], basis: set[str]) -> int:
    return sum(
        len(row["witness_clause"])
        for head, row in witness_by_head.items()
        if head not in basis
    )


def minimum_tree_witness_rows(
    heads: set[str],
    basis: set[str],
    depths: dict[str, int],
    clauses_by_head: dict[str, list[tuple[str, ...]]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Build the deterministic minimum-tree certificate among minimum-depth clauses."""
    sizes: dict[str, int] = {seed: 1 for seed in basis}
    rows: list[dict[str, Any]] = [
        {"head": seed, "is_seed": True, "proof_depth": 0, "witness_clause": []}
        for seed in sorted(basis)
    ]
    for head in sorted(heads - basis, key=lambda node: (depths[node], node)):
        alternatives = clauses_by_head[head]
        if any(dependency not in sizes for body in alternatives for dependency in body):
            raise ValueError("minimum-depth clause dependency is not earlier than its head")
        body_sizes = {
            body: 1 + sum(sizes[dependency] for dependency in body)
            for body in alternatives
        }
        chosen_body = min(alternatives, key=lambda body: (body_sizes[body], body))
        sizes[head] = body_sizes[chosen_body]
        rows.append({
            "head": head,
            "is_seed": False,
            "proof_depth": depths[head],
            "witness_clause": list(chosen_body),
        })
    return rows, sizes


def build_report(bundle: Path = DEFAULT_BUNDLE) -> dict[str, Any]:
    bundle = bundle.resolve()
    integrity = verify_frozen_bundle_integrity(bundle)
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity verification failed")
    rules, clauses, literal_count = load_graph(bundle)
    heads = set(rules)
    basis = {
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    witness_path = bundle / "graph" / "coverage_witnesses.jsonl"
    selected_check = validate_witnesses(heads, basis, rules, list(jsonl(witness_path)))
    if not selected_check["all_valid"]:
        raise ValueError("selected witness certificate failed structural validation")

    depths = minimum_derivation_depths(heads, clauses, basis)
    clauses_by_head = minimum_depth_clauses_by_head(heads, clauses, depths, basis)
    canonical_rows = _witness_rows(heads, basis, depths, clauses_by_head)
    canonical_check = validate_witnesses(heads, basis, rules, canonical_rows)
    if not canonical_check["all_valid"]:
        raise ValueError("canonical minimum-depth witness certificate failed structural validation")

    selected = selected_check["witness_by_head"]
    canonical = canonical_check["witness_by_head"]
    selected_sizes = _tree_sizes(selected, basis, heads)
    canonical_sizes = _tree_sizes(canonical, basis, heads)

    minimum_tree_rows, min_sizes = minimum_tree_witness_rows(
        heads, basis, depths, clauses_by_head
    )
    max_sizes: dict[str, int] = {seed: 1 for seed in basis}
    tied_clause_counts = []
    for head in sorted(heads - basis, key=lambda node: (depths[node], node)):
        alternatives = clauses_by_head[head]
        tied_clause_counts.append(len(alternatives))
        if any(dependency not in max_sizes for body in alternatives for dependency in body):
            raise ValueError("minimum-depth clause dependency is not earlier than its head")
        max_sizes[head] = max(1 + sum(max_sizes[dep] for dep in body) for body in alternatives)

    minimum_tree_check = validate_witnesses(heads, basis, rules, minimum_tree_rows)
    if not minimum_tree_check["all_valid"]:
        raise ValueError("minimum-tree minimum-depth witness certificate failed structural validation")
    minimum_tree_by_head = minimum_tree_check["witness_by_head"]
    minimum_tree_sizes = _tree_sizes(minimum_tree_by_head, basis, heads)
    if minimum_tree_sizes != min_sizes:
        raise ValueError("minimum-tree witness certificate does not realize the dynamic-programming sizes")

    eligible = heads - basis
    selected_depth_minimum_count = sum(
        selected[head]["proof_depth"] == depths[head] for head in eligible
    )
    comparable = [head for head in eligible if selected[head]["proof_depth"] == depths[head]]
    canonical_over_min = [canonical_sizes[head] > min_sizes[head] for head in eligible]
    selected_over_min = [selected_sizes[head] > min_sizes[head] for head in comparable]
    selected_over_canonical = [selected_sizes[head] > canonical_sizes[head] for head in comparable]
    selected_under_canonical = [selected_sizes[head] < canonical_sizes[head] for head in comparable]

    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    return {
        "audit_version": "witness-tree-expansion/2",
        "bundle_integrity_valid": True,
        "graph_rules_sha256": hashlib.sha256(rules_path.read_bytes()).hexdigest(),
        "selected_witnesses_sha256": hashlib.sha256(witness_path.read_bytes()).hexdigest(),
        "graph_size": {
            "head_count": len(heads),
            "basis_count": len(basis),
            "clause_count": len(clauses),
            "dependency_literal_count": literal_count,
        },
        "selected_witness_certificate_valid": selected_check["all_valid"],
        "canonical_minimum_depth_certificate_valid": canonical_check["all_valid"],
        "minimum_tree_minimum_depth_certificate_valid": minimum_tree_check["all_valid"],
        "selected_witness_heads_at_minimum_depth": selected_depth_minimum_count,
        "nonbasis_heads": len(eligible),
        "selected_witness_dag_edge_count": _dag_edge_count(selected, basis),
        "canonical_minimum_depth_dag_edge_count": _dag_edge_count(canonical, basis),
        "minimum_tree_minimum_depth_dag_edge_count": _dag_edge_count(minimum_tree_by_head, basis),
        "selected_witness_tree_unfolding": _size_profile(selected_sizes),
        "canonical_minimum_depth_tree_unfolding": _size_profile(canonical_sizes),
        "minimum_tree_minimum_depth_tree_unfolding": _size_profile(minimum_tree_sizes),
        "minimum_depth_clause_tie_expansion_bounds": {
            "tied_clause_count_per_nonbasis_head": distribution_summary(tied_clause_counts),
            "minimum_possible_tree_unfolding": _size_profile(min_sizes),
            "maximum_possible_tree_unfolding": _size_profile(max_sizes),
            "canonical_lexicographic_witness_exceeds_minimum_tree_size_count": sum(canonical_over_min),
            "selected_witness_exceeds_minimum_tree_size_among_depth_minimal_heads": sum(selected_over_min),
            "selected_vs_canonical_tree_size_on_depth_minimal_heads": {
                "selected_larger": sum(selected_over_canonical),
                "equal": len(comparable) - sum(selected_over_canonical) - sum(selected_under_canonical),
                "selected_smaller": sum(selected_under_canonical),
                "compared_heads": len(comparable),
            },
        },
        "identities_emitted": False,
        "raw_text_emitted": False,
        "limitations": [
            "Tree sizes count repeated dependency occurrences in recursive proof-tree unfolding; they are not unique DAG node counts.",
            "The min/max bounds optimize only among clauses that attain minimum grounded depth, with a fixed deterministic witness choice per atom.",
            "The lexicographic tie-break is not an evidence-quality or source-faithfulness objective.",
            "All results describe the frozen formal graph and do not prove gloss support or lexical entailment.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project directory")
    if output.exists():
        parser.error(f"output exists; choose a new path: {output}")
    try:
        report = build_report(args.bundle)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        with output.open("xb") as stream:
            stream.write(payload)
    except OSError as exc:
        print(f"witness tree expansion audit failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "output": str(output.relative_to(PROJECT_ROOT)),
        "graph_rules_sha256": report["graph_rules_sha256"],
        "head_count": report["graph_size"]["head_count"],
        "selected_witness_heads_at_minimum_depth": report["selected_witness_heads_at_minimum_depth"],
        "selected_witness_dag_edge_count": report["selected_witness_dag_edge_count"],
        "selected_tree_occurrence_max_bit_length": report["selected_witness_tree_unfolding"]
        ["per_root_node_occurrence_bit_length"]["max"],
        "manifest_sha256": hashlib.sha256(payload).hexdigest(),
    }, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
