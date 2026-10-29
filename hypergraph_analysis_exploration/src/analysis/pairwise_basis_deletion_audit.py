"""Exact pairwise basis-deletion interactions in the frozen AND/OR Horn graph.

The analysis measures targets lost only when two basis atoms are removed
together, beyond the union of targets lost after either single deletion. All
claims are structural and relative to the pinned positive Horn representation.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import statistics
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from src.analysis.frozen_hypergraph_audit import (
    DEFAULT_BUNDLE,
    closure,
    jsonl,
    load_graph,
)
from src.analysis.frozen_bundle_integrity import (
    DEFAULT_INTEGRITY_LOCK,
    verify_frozen_bundle_integrity,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase227" / "pairwise_basis_deletion_interactions.json"
SCHEMA_VERSION = "pairwise-basis-deletion-interactions/1"


def _pairwise_closure_masks(
    heads: set[str],
    clauses: list[tuple[str, tuple[str, ...]]],
    basis: list[str],
) -> tuple[list[tuple[str, str]], dict[str, int], dict[str, int], dict[str, int], dict[str, int]]:
    """Propagate all two-basis-deletion worlds together using Python bit masks."""
    pairs = list(itertools.combinations(basis, 2))
    world_count = len(pairs)
    if world_count == 0:
        raise ValueError("pairwise analysis requires at least two basis atoms")
    universe = (1 << world_count) - 1
    removed_worlds = {seed: 0 for seed in basis}
    for world, pair in enumerate(pairs):
        bit = 1 << world
        removed_worlds[pair[0]] |= bit
        removed_worlds[pair[1]] |= bit

    truth = {head: 0 for head in heads}
    queue: deque[tuple[str, int]] = deque()

    def activate(head: str, candidate_worlds: int) -> None:
        if head not in truth:
            return
        delta = candidate_worlds & ~truth[head] & universe
        if delta:
            truth[head] |= delta
            queue.append((head, delta))

    for seed in basis:
        activate(seed, universe & ~removed_worlds[seed])

    clause_heads: list[str] = []
    clause_bodies: list[tuple[str, ...]] = []
    fired_worlds: list[int] = []
    dependents: dict[str, list[int]] = defaultdict(list)
    for head, body in clauses:
        index = len(clause_heads)
        clause_heads.append(head)
        clause_bodies.append(body)
        fired_worlds.append(0)
        if not body:
            fired_worlds[index] = universe
            activate(head, universe)
        else:
            for dependency in body:
                if dependency not in heads:
                    raise ValueError(f"clause dependency is not a graph head: {dependency}")
                dependents[dependency].append(index)

    processed_events = 0
    dependency_updates = 0
    while queue:
        dependency, _new_worlds = queue.popleft()
        processed_events += 1
        for clause_index in dependents.get(dependency, ()):
            dependency_updates += 1
            ready_worlds = universe
            for premise in clause_bodies[clause_index]:
                ready_worlds &= truth[premise]
                if not ready_worlds:
                    break
            newly_fired = ready_worlds & ~fired_worlds[clause_index]
            if newly_fired:
                fired_worlds[clause_index] |= newly_fired
                activate(clause_heads[clause_index], newly_fired)

    return pairs, truth, removed_worlds, {
        "processed_node_world_events": processed_events,
        "dependency_event_updates": dependency_updates,
        "world_count": world_count,
    }, {"universe_mask": universe}


def _column_sums(row_masks: list[int], world_count: int) -> list[int]:
    """Sum Boolean columns of packed rows with bit-sliced integer addition."""
    planes: list[int] = []
    for row in row_masks:
        carry = row
        level = 0
        while carry:
            if level == len(planes):
                planes.append(0)
            previous = planes[level]
            planes[level] = previous ^ carry
            carry = previous & carry
            level += 1
    totals = []
    for world in range(world_count):
        value = 0
        for level, plane in enumerate(planes):
            value |= ((plane >> world) & 1) << level
        totals.append(value)
    return totals


def build_report(bundle: Path = DEFAULT_BUNDLE, integrity_lock: Path = DEFAULT_INTEGRITY_LOCK) -> dict[str, Any]:
    bundle = bundle.resolve()
    integrity = verify_frozen_bundle_integrity(bundle, integrity_lock)
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity lock did not pass")
    rules, clauses, literal_count = load_graph(bundle)
    heads = set(rules)
    basis = sorted({
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    })
    if len(basis) < 2 or not set(basis) <= heads:
        raise ValueError("basis must contain at least two graph heads")
    baseline = closure(heads, clauses, set(basis))
    if baseline != heads:
        raise ValueError("full basis does not derive every graph head")

    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    graph_sha256 = hashlib.sha256(rules_path.read_bytes()).hexdigest()
    basis_bytes = ("\n".join(basis) + "\n").encode("utf-8")
    basis_sha256 = hashlib.sha256(basis_bytes).hexdigest()
    pairs, truth_masks, removed_worlds, propagation_stats, masks = _pairwise_closure_masks(
        heads, clauses, basis
    )
    universe = masks["universe_mask"]
    world_count = len(pairs)
    active_counts = _column_sums(list(truth_masks.values()), world_count)

    head_ids = sorted(heads)
    head_positions = {head: index for index, head in enumerate(head_ids)}
    all_heads_mask = (1 << len(head_ids)) - 1
    single_loss_masks: dict[str, int] = {}
    single_loss_counts: dict[str, int] = {}
    for seed in basis:
        single_closure = closure(heads, clauses, set(basis) - {seed})
        retained_mask = 0
        for head in single_closure:
            retained_mask |= 1 << head_positions[head]
        lost_mask = all_heads_mask & ~retained_mask
        single_loss_masks[seed] = lost_mask
        single_loss_counts[seed] = lost_mask.bit_count()

    single_loss_seed_mask_by_head = [0] * len(head_ids)
    for seed_index, seed in enumerate(basis):
        lost_heads = single_loss_masks[seed]
        while lost_heads:
            least_bit = lost_heads & -lost_heads
            head_index = least_bit.bit_length() - 1
            single_loss_seed_mask_by_head[head_index] |= 1 << seed_index
            lost_heads ^= least_bit
    for head_index, head in enumerate(head_ids):
        individually_losing_seeds = single_loss_seed_mask_by_head[head_index]
        required_pair_loss_worlds = 0
        while individually_losing_seeds:
            least_bit = individually_losing_seeds & -individually_losing_seeds
            seed_index = least_bit.bit_length() - 1
            required_pair_loss_worlds |= removed_worlds[basis[seed_index]]
            individually_losing_seeds ^= least_bit
        actual_pair_loss_worlds = universe & ~truth_masks[head]
        if required_pair_loss_worlds & ~actual_pair_loss_worlds:
            raise ValueError(f"pairwise set-inclusion monotonicity failed for head {head!r}")

    rows = []
    for world, (left, right) in enumerate(pairs):
        exact_pair_loss = len(heads) - active_counts[world]
        union_of_single_losses = (
            single_loss_counts[left] + single_loss_counts[right]
            - (single_loss_masks[left] & single_loss_masks[right]).bit_count()
        )
        pair_only_loss = exact_pair_loss - union_of_single_losses
        if pair_only_loss < 0:
            left, right = pairs[world]
            direct_loss = len(heads) - len(closure(heads, clauses, set(basis) - {left, right}))
            raise ValueError(
                "pair deletion lost fewer heads than the union of single-deletion losses: "
                f"pair={left!r},{right!r}; batched={exact_pair_loss}; direct={direct_loss}; "
                f"single_union={union_of_single_losses}"
            )
        rows.append({
            "pair_index": world,
            "removed_basis_atoms": [left, right],
            "exact_pair_and_or_closure_loss_count": exact_pair_loss,
            "union_of_single_deletion_loss_count": union_of_single_losses,
            "joint_only_loss_count": pair_only_loss,
            "joint_only_loss_fraction_of_pair_loss": (
                round(pair_only_loss / exact_pair_loss, 8) if exact_pair_loss else None
            ),
        })

    direct_check_worlds = sorted({0, world_count // 2, world_count - 1})
    if rows:
        direct_check_worlds.append(max(range(world_count), key=lambda index: rows[index]["joint_only_loss_count"]))
    direct_checks = []
    for world in sorted(set(direct_check_worlds)):
        left, right = pairs[world]
        direct_loss = len(heads) - len(closure(heads, clauses, set(basis) - {left, right}))
        if direct_loss != rows[world]["exact_pair_and_or_closure_loss_count"]:
            raise ValueError(f"batched pair closure disagrees with direct closure at world {world}")
        direct_checks.append({
            "pair_index": world,
            "removed_basis_atoms": [left, right],
            "direct_closure_loss_count": direct_loss,
            "batched_loss_count": rows[world]["exact_pair_and_or_closure_loss_count"],
            "matches": True,
        })

    losses = [row["exact_pair_and_or_closure_loss_count"] for row in rows]
    interactions = [row["joint_only_loss_count"] for row in rows]
    synergy_pairs = sum(value > 0 for value in interactions)
    return {
        "schema_version": SCHEMA_VERSION,
        "claim_type": "structural_pairwise_redundancy_in_fixed_positive_horn_graph",
        "method": "batched exact least-Horn closure over every two-basis-deletion world using event-driven bit masks",
        "inputs": {
            "bundle_root": str(bundle),
            "graph_rules_sha256": graph_sha256,
            "basis_atoms_sha256_sorted_utf8_lf": basis_sha256,
            "head_count": len(heads),
            "clause_count": len(clauses),
            "dependency_literal_count": literal_count,
            "basis_count": len(basis),
            "basis_pair_count": world_count,
            "bundle_integrity": integrity,
        },
        "definitions": {
            "exact_pair_loss": "heads absent from closure(B - {a,b})",
            "single_union_loss": "loss(B - {a}) union loss(B - {b})",
            "joint_only_loss": "exact_pair_loss minus single_union_loss; heads surviving either single deletion but lost after deleting both",
        },
        "summary": {
            "all_pair_deletions_have_loss": all(value > 0 for value in losses),
            "pairwise_loss_set_inclusion_checked_for_all_heads": True,
            "pairwise_loss_set_inclusion_violations": 0,
            "pair_loss_count_min_median_max": [min(losses), statistics.median(losses), max(losses)],
            "pairs_with_joint_only_losses": synergy_pairs,
            "pairs_without_joint_only_losses": world_count - synergy_pairs,
            "joint_only_loss_count_min_median_max": [min(interactions), statistics.median(interactions), max(interactions)],
            "maximum_joint_only_loss_count": max(interactions),
            "maximum_joint_only_loss_pairs": [
                row["removed_basis_atoms"] for row in rows
                if row["joint_only_loss_count"] == max(interactions)
            ],
            "sum_pair_joint_only_loss_scenario_head_items": sum(interactions),
        },
        "propagation": propagation_stats,
        "direct_closure_cross_checks": direct_checks,
        "pairwise_deletion_rows": rows,
        "interpretation_limits": [
            "This is exact only for the pinned positive Horn AND/OR graph and the declared basis.",
            "A joint-only loss is a structural redundancy interaction, not semantic importance or a causal effect on language meaning.",
            "This does not establish gloss support, source fidelity, an optimal basis, or behavior under removal of source documents unless source-to-rule identity is independently established.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        raise SystemExit(f"output already exists; pass --force to replace: {args.output}")
    report = build_report(args.bundle, args.integrity_lock)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.output.write_text(payload, encoding="utf-8")
    print(f"Pairwise scenarios: {report['inputs']['basis_pair_count']}")
    print(f"Pairs with joint-only losses: {report['summary']['pairs_with_joint_only_losses']}")
    print(f"Maximum joint-only loss: {report['summary']['maximum_joint_only_loss_count']}")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
