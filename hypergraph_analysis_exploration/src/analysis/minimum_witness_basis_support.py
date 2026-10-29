"""Summarize structural basis support across local minimum-depth witnesses.

The readout preserves the frozen OR-of-AND clauses. It describes only the
family in which every non-basis head recursively chooses a clause attaining
that head's own minimum grounded depth; it is not the set of every globally
minimum-height proof tree and has no truth-conditional semantic meaning.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
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


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase17" / "minimum_witness_basis_support.json"


def local_minimum_basis_support_masks(
    heads: set[str],
    basis: set[str],
    depths: dict[str, int],
    minimizing_clauses: dict[str, list[tuple[str, ...]]],
) -> tuple[dict[str, int], dict[str, int]]:
    """Return possible/certain basis masks in the local-minimum witness family.

    For one AND clause, a basis atom is possible if any dependency can use it,
    and certain if at least one dependency must use it. Across OR clauses,
    possible support is the union and certain support is the intersection.
    Recursion is safe because every minimum-depth clause dependency is strictly
    shallower than its head.
    """
    if not basis <= heads or set(depths) != heads:
        raise ValueError("basis/depth map must cover exactly the graph heads")
    basis_order = sorted(basis)
    basis_bit = {node: 1 << index for index, node in enumerate(basis_order)}
    possible: dict[str, int] = dict(basis_bit)
    certain: dict[str, int] = dict(basis_bit)

    for head in sorted(heads - basis, key=lambda node: (depths[node], node)):
        bodies = minimizing_clauses.get(head)
        if not bodies:
            raise ValueError(f"non-basis head lacks a minimum-depth clause: {head}")
        clause_possible_masks: list[int] = []
        clause_certain_masks: list[int] = []
        for body in bodies:
            possible_mask = 0
            certain_mask = 0
            for dependency in body:
                if dependency not in possible:
                    raise ValueError("minimum-depth clause is not grounded in depth order")
                if depths[dependency] >= depths[head]:
                    raise ValueError("minimum-depth clause does not decrease proof depth")
                possible_mask |= possible[dependency]
                certain_mask |= certain[dependency]
            clause_possible_masks.append(possible_mask)
            clause_certain_masks.append(certain_mask)

        head_possible = 0
        for mask in clause_possible_masks:
            head_possible |= mask
        head_certain = clause_certain_masks[0]
        for mask in clause_certain_masks[1:]:
            head_certain &= mask
        if head_certain & ~head_possible:
            raise ValueError("certain basis support is not a subset of possible support")
        possible[head] = head_possible
        certain[head] = head_certain

    if set(possible) != heads or set(certain) != heads:
        raise ValueError("basis support readout did not cover all graph heads")
    return possible, certain


def global_minimum_basis_support_masks(
    heads: set[str],
    basis: set[str],
    depths: dict[str, int],
    clauses: list[tuple[str, tuple[str, ...]]],
    *,
    max_states: int | None = None,
) -> tuple[dict[str, int], dict[str, int], int]:
    """Summarize support over every proof tree within each root's min-depth bound.

    Unlike :func:`local_minimum_basis_support_masks`, a child may use a
    non-minimum-depth derivation when it still fits the remaining height budget.
    Basis facts are available as depth-zero leaves, while their rule clauses
    remain valid alternative proofs when the caller has enough budget.
    """
    if not basis <= heads or set(depths) != heads:
        raise ValueError("basis/depth map must cover exactly the graph heads")
    basis_order = sorted(basis)
    basis_bit = {node: 1 << index for index, node in enumerate(basis_order)}
    clauses_by_head: dict[str, list[tuple[tuple[str, ...], int]]] = {
        head: [] for head in heads
    }
    for head, body in clauses:
        if head not in heads or any(dependency not in heads for dependency in body):
            raise ValueError("clause references a node outside the graph heads")
        clause_min_depth = 1 + max((depths[node] for node in body), default=0)
        clauses_by_head[head].append((body, clause_min_depth))

    state_count = 0

    @lru_cache(maxsize=None)
    def support_at_budget(head: str, budget: int) -> tuple[int, int]:
        nonlocal state_count
        state_count += 1
        if max_states is not None and state_count > max_states:
            raise RuntimeError(f"global support state limit exceeded: {max_states}")

        alternative_possible: list[int] = []
        alternative_certain: list[int] = []
        if head in basis and budget >= 0:
            bit = basis_bit[head]
            alternative_possible.append(bit)
            alternative_certain.append(bit)

        if budget >= 1:
            for body, clause_min_depth in clauses_by_head[head]:
                if clause_min_depth > budget:
                    continue
                body_possible = 0
                body_certain = 0
                for dependency in body:
                    dep_possible, dep_certain = support_at_budget(dependency, budget - 1)
                    body_possible |= dep_possible
                    body_certain |= dep_certain
                alternative_possible.append(body_possible)
                alternative_certain.append(body_certain)

        if not alternative_possible:
            raise ValueError(f"head has no proof within its requested depth budget: {head}")
        possible_mask = 0
        for mask in alternative_possible:
            possible_mask |= mask
        certain_mask = alternative_certain[0]
        for mask in alternative_certain[1:]:
            certain_mask &= mask
        return possible_mask, certain_mask

    possible: dict[str, int] = {}
    certain: dict[str, int] = {}
    for head in sorted(heads, key=lambda node: (depths[node], node)):
        possible[head], certain[head] = support_at_budget(head, depths[head])
    return possible, certain, state_count


def build_report(bundle: Path) -> dict[str, Any]:
    bundle = bundle.resolve()
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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
    minimizing_clauses = minimum_depth_clauses_by_head(heads, clauses, depths, basis)
    possible, certain = local_minimum_basis_support_masks(
        heads, basis, depths, minimizing_clauses
    )
    basis_size = len(basis)
    possible_counts = [possible[node].bit_count() for node in heads]
    certain_counts = [certain[node].bit_count() for node in heads]
    possible_pairs = sum(possible_counts)
    certain_pairs = sum(certain_counts)
    if any(count > basis_size for count in possible_counts + certain_counts):
        raise ValueError("support mask exceeds basis cardinality")

    possible_per_basis = [0] * basis_size
    certain_per_basis = [0] * basis_size
    for node in heads:
        for index in range(basis_size):
            bit = 1 << index
            possible_per_basis[index] += bool(possible[node] & bit)
            certain_per_basis[index] += bool(certain[node] & bit)

    return {
        "audit_version": "minimum-witness-basis-support/1",
        "graph_rules_sha256": graph_sha,
        "graph_size": {
            "head_count": len(heads),
            "clause_count": len(clauses),
            "dependency_literal_count": literal_count,
            "basis_count": basis_size,
        },
        "readout": {
            "scope": "recursive family where each non-basis head selects one clause attaining its own minimum grounded derivation depth",
            "possible_basis_count_per_head": distribution_summary(possible_counts),
            "certain_basis_count_per_head": distribution_summary(certain_counts),
            "possible_head_basis_pair_count": possible_pairs,
            "certain_head_basis_pair_count": certain_pairs,
            "possible_support_count_per_basis_atom": distribution_summary(possible_per_basis),
            "certain_support_count_per_basis_atom": distribution_summary(certain_per_basis),
            "heads_with_no_certain_basis_atom": sum(count == 0 for count in certain_counts),
        },
        "validation": {
            "all_heads_have_support_masks": len(possible) == len(certain) == len(heads),
            "certain_support_is_subset_of_possible_support": certain_pairs <= possible_pairs,
            "basis_identity_emitted": False,
            "raw_text_emitted": False,
        },
        "limitations": [
            "This is a structural support envelope over recursively local minimum-depth clause choices, not a semantic importance measure for the basis atoms.",
            "It excludes derivations that use a non-minimum-depth subproof even if a shallower sibling keeps the root at the same global height; it is not the full set of globally minimum-height proof trees.",
            "A basis atom being certain or possible only describes membership in this encoded witness family; it does not establish that a gloss supports a rule or that the basis is a semantic prime.",
            "No basis IDs, sense identities, source paths, or gloss text are emitted.",
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
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote minimum-witness basis support audit: {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
