"""Summarize basis support across all globally minimum-height proof trees."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from src.analysis.frozen_hypergraph_audit import DEFAULT_BUNDLE, load_graph
from src.analysis.minimum_witness_audit import (
    distribution_summary,
    minimum_depth_clauses_by_head,
    minimum_derivation_depths,
)
from src.analysis.minimum_witness_basis_support import (
    global_minimum_basis_support_masks,
    local_minimum_basis_support_masks,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase18" / "global_minimum_witness_basis_support.json"


STRATA = {
    "minimum_depth": ((0, 0, "0"), (1, 5, "1-5"), (6, 25, "6-25"),
                      (26, 100, "26-100"), (101, 300, "101-300"), (301, None, "301+")),
    "or_clause_count": ((0, 0, "0"), (1, 1, "1"), (2, 5, "2-5"), (6, None, "6+")),
    "max_and_width": ((0, 0, "0"), (1, 1, "1"), (2, 3, "2-3"),
                      (4, 7, "4-7"), (8, None, "8+")),
}


def _bucket(value: int, ranges: tuple[tuple[int, int | None, str], ...]) -> str:
    for lower, upper, label in ranges:
        if value >= lower and (upper is None or value <= upper):
            return label
    raise ValueError(f"value falls outside configured strata: {value}")


def stratified_support_impact(
    heads: set[str],
    depths: dict[str, int],
    clauses_by_head: dict[str, list[tuple[str, ...]]],
    local_possible: dict[str, int],
    local_certain: dict[str, int],
    global_possible: dict[str, int],
    global_certain: dict[str, int],
) -> dict[str, list[dict[str, int | float | str]]]:
    """Aggregate local-to-global support changes by three graph dimensions."""
    result: dict[str, list[dict[str, int | str]]] = {}
    for dimension, ranges in STRATA.items():
        groups: dict[str, dict[str, int | float | str]] = {}
        for head in heads:
            if dimension == "minimum_depth":
                value = depths[head]
            elif dimension == "or_clause_count":
                value = len(clauses_by_head[head])
            else:
                value = max((len(body) for body in clauses_by_head[head]), default=0)
            label = _bucket(value, ranges)
            row = groups.setdefault(label, {
                "stratum": label,
                "head_count": 0,
                "local_possible_pairs": 0,
                "global_possible_pairs": 0,
                "possible_pairs_added": 0,
                "heads_with_possible_change": 0,
                "local_certain_pairs": 0,
                "global_certain_pairs": 0,
                "certain_pairs_removed": 0,
                "heads_with_certain_change": 0,
            })
            lp, lc = local_possible[head], local_certain[head]
            gp, gc = global_possible[head], global_certain[head]
            added = (gp & ~lp).bit_count()
            removed = (lc & ~gc).bit_count()
            row["head_count"] += 1
            row["local_possible_pairs"] += lp.bit_count()
            row["global_possible_pairs"] += gp.bit_count()
            row["possible_pairs_added"] += added
            row["heads_with_possible_change"] += gp != lp
            row["local_certain_pairs"] += lc.bit_count()
            row["global_certain_pairs"] += gc.bit_count()
            row["certain_pairs_removed"] += removed
            row["heads_with_certain_change"] += gc != lc
        ordered_labels = [label for _, _, label in ranges]
        ordered_rows = [groups[label] for label in ordered_labels if label in groups]
        for row in ordered_rows:
            count = int(row["head_count"])
            row["heads_with_possible_change_fraction"] = round(
                int(row["heads_with_possible_change"]) / count, 6
            )
            row["heads_with_certain_change_fraction"] = round(
                int(row["heads_with_certain_change"]) / count, 6
            )
            row["possible_pairs_added_per_head"] = round(
                int(row["possible_pairs_added"]) / count, 6
            )
            row["certain_pairs_removed_per_head"] = round(
                int(row["certain_pairs_removed"]) / count, 6
            )
        result[dimension] = ordered_rows

    expected = {
        "head_count": len(heads),
        "possible_pairs_added": sum((global_possible[node] & ~local_possible[node]).bit_count() for node in heads),
        "certain_pairs_removed": sum((local_certain[node] & ~global_certain[node]).bit_count() for node in heads),
    }
    for rows in result.values():
        observed = {key: sum(int(row[key]) for row in rows) for key in expected}
        if observed != expected:
            raise ValueError("support impact strata do not sum to their graph totals")
    return result


def build_report(bundle: Path, max_states: int = 5_000_000) -> dict[str, Any]:
    bundle = bundle.resolve()
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    rules, clauses, literal_count = load_graph(bundle)
    heads = set(rules)
    basis = {
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt")
        .read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    graph_sha = hashlib.sha256(rules_path.read_bytes()).hexdigest()
    if manifest.get("graph_sha256") and graph_sha != manifest["graph_sha256"]:
        raise ValueError("graph rules hash does not match the bundle manifest")

    depths = minimum_derivation_depths(heads, clauses, basis)
    possible, certain, state_count = global_minimum_basis_support_masks(
        heads, basis, depths, clauses, max_states=max_states
    )
    minimizing_clauses = minimum_depth_clauses_by_head(heads, clauses, depths, basis)
    local_possible, local_certain = local_minimum_basis_support_masks(
        heads, basis, depths, minimizing_clauses
    )
    global_possible_contains_local = all(
        possible[node] & local_possible[node] == local_possible[node]
        for node in heads
    )
    global_certain_within_local = all(
        certain[node] & ~local_certain[node] == 0
        for node in heads
    )
    if not global_possible_contains_local or not global_certain_within_local:
        raise ValueError("global proof family violates local/global support set inclusion")

    clauses_by_head = {head: [] for head in heads}
    for head, body in clauses:
        clauses_by_head[head].append(body)
    impact_by_stratum = stratified_support_impact(
        heads, depths, clauses_by_head, local_possible, local_certain, possible, certain
    )

    basis_size = len(basis)
    possible_counts = [possible[node].bit_count() for node in heads]
    certain_counts = [certain[node].bit_count() for node in heads]
    local_possible_pairs = sum(mask.bit_count() for mask in local_possible.values())
    local_certain_pairs = sum(mask.bit_count() for mask in local_certain.values())
    possible_pairs = sum(possible_counts)
    certain_pairs = sum(certain_counts)
    if possible_pairs < local_possible_pairs or certain_pairs > local_certain_pairs:
        raise ValueError("global proof family is not a monotone expansion of local witnesses")

    possible_per_basis = [0] * basis_size
    certain_per_basis = [0] * basis_size
    for node in heads:
        for index in range(basis_size):
            bit = 1 << index
            possible_per_basis[index] += bool(possible[node] & bit)
            certain_per_basis[index] += bool(certain[node] & bit)

    return {
        "audit_version": "global-minimum-witness-basis-support/1",
        "graph_rules_sha256": graph_sha,
        "graph_size": {
            "head_count": len(heads),
            "clause_count": len(clauses),
            "dependency_literal_count": literal_count,
            "basis_count": basis_size,
            "basis_heads_with_rule_clauses": sum(bool(rules.get(node)) for node in basis),
        },
        "proof_family": {
            "definition": "all proof trees for a root head whose height is at most that head's minimum grounded derivation depth; basis facts may be used as depth-zero leaves, and rule clauses remain alternative proofs when they fit the remaining height budget",
            "support_state_count": state_count,
            "state_limit": max_states,
        },
        "readout": {
            "possible_basis_count_per_head": distribution_summary(possible_counts),
            "certain_basis_count_per_head": distribution_summary(certain_counts),
            "possible_head_basis_pair_count": possible_pairs,
            "certain_head_basis_pair_count": certain_pairs,
            "possible_support_count_per_basis_atom": distribution_summary(possible_per_basis),
            "certain_support_count_per_basis_atom": distribution_summary(certain_per_basis),
            "heads_with_no_certain_basis_atom": sum(count == 0 for count in certain_counts),
            "comparison_to_local_minimum_family": {
                "local_possible_head_basis_pair_count": local_possible_pairs,
                "local_certain_head_basis_pair_count": local_certain_pairs,
                "possible_pair_delta": possible_pairs - local_possible_pairs,
                "certain_pair_delta": certain_pairs - local_certain_pairs,
            },
        },
        "impact_by_structure_stratum": impact_by_stratum,
        "validation": {
            "all_heads_have_support_masks": len(possible) == len(certain) == len(heads),
            "certain_support_is_subset_of_possible_support": certain_pairs <= possible_pairs,
            "global_possible_contains_local_possible": global_possible_contains_local,
            "global_certain_is_subset_of_local_certain": global_certain_within_local,
            "basis_identity_emitted": False,
            "raw_text_emitted": False,
        },
        "limitations": [
            "This is a structural support envelope over proofs licensed by the frozen positive Horn graph, not a semantic importance measure or evidence that a gloss supports a rule.",
            "The proof family is exact for the encoded graph and the stated bounded-height definition; it does not validate sense identity, lexical truth, or the semantic-prime status of the selected basis.",
            "No basis IDs, source paths, or gloss text are emitted.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--max-states", type=int, default=5_000_000)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("report output must remain inside the project directory")
    if args.max_states < 1:
        parser.error("--max-states must be positive")
    if output.exists() and not args.force:
        parser.error(f"output exists; pass --force to replace: {output}")
    try:
        report = build_report(args.bundle, max_states=args.max_states)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote global minimum-witness basis support audit: {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
