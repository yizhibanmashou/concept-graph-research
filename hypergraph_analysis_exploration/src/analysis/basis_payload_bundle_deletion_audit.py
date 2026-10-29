"""Compare basis-seed deletion with deleting the frozen source-record bundle for each sense."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import statistics
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from src.analysis.basis_source_lineage_audit import build_report as build_source_lineage_report
from src.analysis.frozen_bundle_integrity import (
    DEFAULT_INTEGRITY_LOCK,
    verify_frozen_bundle_integrity,
)
from src.analysis.frozen_hypergraph_audit import DEFAULT_BUNDLE, closure, load_graph
from src.analysis.project_paths import PROJECT_ROOT


DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase230" / "basis_payload_bundle_deletion_audit.json"
SCHEMA_VERSION = "basis-payload-bundle-deletion-audit/1"


def _column_sums(row_masks: list[int], world_count: int) -> list[int]:
    """Sum packed Boolean columns without iterating over every set bit."""
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


def _pairwise_closure_masks(
    heads: set[str],
    clauses: list[tuple[str, tuple[str, ...]]],
    basis: list[str],
    *,
    disable_rules_for_removed_basis_heads: bool,
) -> tuple[list[tuple[str, str]], dict[str, int], dict[str, int]]:
    pairs = list(itertools.combinations(basis, 2))
    world_count = len(pairs)
    if not world_count:
        raise ValueError("pairwise deletion requires at least two basis atoms")
    universe = (1 << world_count) - 1
    removed_worlds = {seed: 0 for seed in basis}
    for world, pair in enumerate(pairs):
        bit = 1 << world
        removed_worlds[pair[0]] |= bit
        removed_worlds[pair[1]] |= bit

    truth = {head: 0 for head in heads}
    queue: deque[str] = deque()

    def activate(head: str, candidate_worlds: int) -> None:
        if head not in truth:
            return
        delta = candidate_worlds & ~truth[head] & universe
        if delta:
            truth[head] |= delta
            queue.append(head)

    for seed in basis:
        activate(seed, universe & ~removed_worlds[seed])

    clause_heads: list[str] = []
    clause_bodies: list[tuple[str, ...]] = []
    clause_active_worlds: list[int] = []
    fired_worlds: list[int] = []
    dependents: dict[str, list[int]] = defaultdict(list)
    for head, body in clauses:
        index = len(clause_heads)
        clause_heads.append(head)
        clause_bodies.append(body)
        active = universe
        if disable_rules_for_removed_basis_heads and head in removed_worlds:
            active &= ~removed_worlds[head]
        clause_active_worlds.append(active)
        fired_worlds.append(0)
        if not body:
            fired_worlds[index] = active
            activate(head, active)
        else:
            for dependency in body:
                if dependency not in heads:
                    raise ValueError(f"clause dependency is not a graph head: {dependency}")
                dependents[dependency].append(index)

    while queue:
        dependency = queue.popleft()
        for clause_index in dependents.get(dependency, ()):
            ready_worlds = clause_active_worlds[clause_index]
            for premise in clause_bodies[clause_index]:
                ready_worlds &= truth[premise]
                if not ready_worlds:
                    break
            newly_fired = ready_worlds & ~fired_worlds[clause_index]
            if newly_fired:
                fired_worlds[clause_index] |= newly_fired
                activate(clause_heads[clause_index], newly_fired)

    return pairs, truth, {"universe_mask": universe, "world_count": world_count}


def _stats(values: list[int]) -> list[int | float]:
    return [min(values), statistics.median(values), max(values)]


def build_report(bundle: Path = DEFAULT_BUNDLE, integrity_lock: Path = DEFAULT_INTEGRITY_LOCK) -> dict[str, Any]:
    bundle = bundle.resolve()
    integrity = verify_frozen_bundle_integrity(bundle, integrity_lock)
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity lock did not pass")

    lineage = build_source_lineage_report(bundle, integrity_lock)
    lineage_checks = lineage["checks"]
    lineage_counts = lineage["counts"]
    required_lineage_checks = (
        "basis_ids_match_nodes_one_to_one",
        "basis_ids_match_sense_index_one_to_one",
        "all_graph_clauses_have_exactly_one_active_source_index_row",
        "all_active_clause_documents_link_to_same_head_source_records",
    )
    if not all(lineage_checks.get(name) for name in required_lineage_checks):
        raise ValueError("basis source-record lineage prerequisites did not pass")
    if lineage_counts["basis_source_paths_shared_across_basis_seeds"] != 0:
        raise ValueError("basis source-record payloads are shared across senses; intervention mapping is ambiguous")
    if lineage_counts["basis_source_paths_linked_to_clause_evidence_for_multiple_index_rows"] != 0:
        raise ValueError("basis source-record payloads support clauses for multiple senses")

    rules, clauses, _literal_count = load_graph(bundle)
    heads = set(rules)
    basis = sorted(
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    if not set(basis) <= heads:
        raise ValueError("basis contains a node absent from graph heads")
    baseline = closure(heads, clauses, set(basis))
    if baseline != heads:
        raise ValueError("full basis does not derive all graph heads")

    pairs, seed_truth, masks = _pairwise_closure_masks(
        heads, clauses, basis, disable_rules_for_removed_basis_heads=False
    )
    source_pairs, payload_truth, payload_masks = _pairwise_closure_masks(
        heads, clauses, basis, disable_rules_for_removed_basis_heads=True
    )
    if pairs != source_pairs or masks != payload_masks:
        raise ValueError("pair scenario order differs between interventions")
    universe = masks["universe_mask"]

    head_ids = sorted(heads)
    seed_loss_masks: list[int] = []
    payload_loss_masks: list[int] = []
    for head in head_ids:
        seed_loss = universe & ~seed_truth[head]
        payload_loss = universe & ~payload_truth[head]
        if payload_truth[head] & ~seed_truth[head]:
            raise ValueError("source-record bundle deletion derived a head lost under seed-only deletion")
        seed_loss_masks.append(seed_loss)
        payload_loss_masks.append(payload_loss)

    seed_counts = _column_sums(seed_loss_masks, len(pairs))
    payload_counts = _column_sums(payload_loss_masks, len(pairs))
    extra_counts = _column_sums(
        [payload_loss & ~seed_loss for payload_loss, seed_loss in zip(payload_loss_masks, seed_loss_masks)],
        len(pairs),
    )
    removed_worlds = {seed: 0 for seed in basis}
    for world, pair in enumerate(pairs):
        bit = 1 << world
        removed_worlds[pair[0]] |= bit
        removed_worlds[pair[1]] |= bit
    deleted_basis_heads_rederived_worlds = sum(
        (seed_truth[seed] & removed_worlds[seed]).bit_count() for seed in basis
    )
    if deleted_basis_heads_rederived_worlds:
        raise ValueError("a removed basis head is still derivable in a seed-only deletion world")

    phase227_path = PROJECT_ROOT / "outputs" / "phase227" / "pairwise_basis_deletion_interactions.json"
    if not phase227_path.is_file():
        raise ValueError("Phase227 pairwise closure output is required for baseline reconciliation")
    phase227 = json.loads(phase227_path.read_text(encoding="utf-8"))
    phase227_rows = phase227.get("pairwise_deletion_rows")
    if not isinstance(phase227_rows, list) or len(phase227_rows) != len(pairs):
        raise ValueError("Phase227 pairwise output has an unexpected row count")
    phase227_counts = {
        row.get("pair_index"): row.get("exact_pair_and_or_closure_loss_count")
        for row in phase227_rows
        if isinstance(row, dict)
    }
    if len(phase227_counts) != len(pairs) or any(
        phase227_counts.get(index) != seed_counts[index] for index in range(len(pairs))
    ):
        raise ValueError("seed-only pairwise losses disagree with Phase227")

    direct_checks = []
    candidate_indices = {0, len(pairs) // 2, len(pairs) - 1}
    if len(pairs) > 329:
        candidate_indices.add(329)  # Phase227's maximum joint-only-loss pair.
    candidate_indices.add(max(range(len(pairs)), key=lambda i: extra_counts[i]))
    for pair_index in sorted(candidate_indices):
        removed_pair = set(pairs[pair_index])
        seeds = set(basis) - removed_pair
        seed_closure = closure(heads, clauses, seeds)
        bundle_closure = closure(
            heads,
            [clause for clause in clauses if clause[0] not in removed_pair],
            seeds,
        )
        seed_loss = heads - seed_closure
        bundle_loss = heads - bundle_closure
        expected_seed = set()
        expected_bundle = set()
        for head_index, head in enumerate(head_ids):
            bit = 1 << pair_index
            if seed_loss_masks[head_index] & bit:
                expected_seed.add(head)
            if payload_loss_masks[head_index] & bit:
                expected_bundle.add(head)
        direct_checks.append({
            "pair_index": pair_index,
            "seed_only_loss_matches_direct_closure": seed_loss == expected_seed,
            "payload_bundle_loss_matches_direct_closure": bundle_loss == expected_bundle,
            "seed_only_loss_count": len(seed_loss),
            "payload_bundle_loss_count": len(bundle_loss),
            "additional_payload_bundle_loss_count": len(bundle_loss - seed_loss),
        })
    if not all(
        item["seed_only_loss_matches_direct_closure"] and item["payload_bundle_loss_matches_direct_closure"]
        for item in direct_checks
    ):
        raise ValueError("selected direct-closure checks failed")

    basis_bytes = ("\n".join(basis) + "\n").encode("utf-8")
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    rows = [
        {
            "pair_index": i,
            "seed_only_loss_count": seed_counts[i],
            "payload_bundle_loss_count": payload_counts[i],
            "additional_loss_from_removing_head_rules": extra_counts[i],
        }
        for i in range(len(pairs))
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "claim_type": "fixed_bundle_sense_payload_removal_sensitivity_not_upstream_document_effect",
        "intervention": {
            "unit": "all frozen source-record payloads associated with one selected basis sense identity",
            "seed_policy": "remove the selected basis atom when its entire sense payload bundle is removed",
            "rule_policy": "disable every graph clause whose head is one of the removed basis senses",
            "scope_note": "This models package-level sense payload bundle removal; it is not an intervention on the original upstream WordNet release or provider documents.",
        },
        "inputs": {
            "bundle_integrity_valid": True,
            "bundle_root": str(bundle),
            "graph_rules_sha256": hashlib.sha256(rules_path.read_bytes()).hexdigest(),
            "phase227_pairwise_audit_sha256": hashlib.sha256(phase227_path.read_bytes()).hexdigest(),
            "basis_atoms_sha256_sorted_utf8_lf": hashlib.sha256(basis_bytes).hexdigest(),
            "head_count": len(heads),
            "clause_count": len(clauses),
            "basis_count": len(basis),
            "pair_scenario_count": len(pairs),
            "full_basis_closure_complete": True,
            "basis_source_lineage_checks_passed": True,
            "basis_source_record_path_associations": lineage_counts["basis_source_record_path_associations"],
            "all_graph_clauses_have_source_index_rows": lineage_counts["active_clause_source_index_rows"],
            "source_payload_sha256_matches": lineage_checks["source_payload_sha256_match_sidecar"],
        },
        "results": {
            "seed_only_pair_loss_min_median_max": _stats(seed_counts),
            "payload_bundle_pair_loss_min_median_max": _stats(payload_counts),
            "additional_loss_min_median_max": _stats(extra_counts),
            "pairs_with_any_additional_loss_from_head_rule_removal": sum(value > 0 for value in extra_counts),
            "total_pair_head_additional_losses": sum(extra_counts),
            "removed_basis_head_rederived_worlds_under_seed_only_deletion": deleted_basis_heads_rederived_worlds,
            "removed_basis_head_pair_world_incidences": sum(mask.bit_count() for mask in removed_worlds.values()),
            "seed_only_loss_counts_match_phase227_all_pairs": True,
            "pair_head_loss_sets_equal_all_pairs": sum(extra_counts) == 0,
            "payload_bundle_loss_is_superset_of_seed_only_loss_for_all_heads_and_worlds": True,
            "direct_closure_cross_checks": len(direct_checks),
            "direct_closure_cross_checks_all_match": True,
        },
        "pair_rows": rows,
        "direct_closure_checks": direct_checks,
        "interpretation_limits": [
            "This is an explicitly defined intervention on frozen source-record payload bundles, not upstream source documents.",
            "All clauses for a removed basis sense are disabled because the complete source-record bundle for that sense is removed; no within-sense payload is retained.",
            "The result does not establish that gloss spans semantically support the rules or that upstream WordNet records may be removed.",
            "The comparison isolates head-rule removal and seed removal under the pinned graph; it is not a probability-weighted reliability importance measure.",
            "No license clearance or public-release decision is implied.",
        ],
    }


def _write_json(path: Path, report: dict[str, Any], force: bool) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to(PROJECT_ROOT):
        raise ValueError("output must remain inside the project directory")
    if resolved.exists() and not force:
        raise ValueError("output already exists; choose another path or pass --force")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = build_report(args.bundle, args.integrity_lock)
        _write_json(args.output, report, args.force)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    result = report["results"]
    print(
        f"Compared {report['inputs']['pair_scenario_count']} pairs: "
        f"{result['pairs_with_any_additional_loss_from_head_rule_removal']} have additional loss under payload-bundle removal"
    )
    print(f"Wrote aggregate report: {args.output.resolve().relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
