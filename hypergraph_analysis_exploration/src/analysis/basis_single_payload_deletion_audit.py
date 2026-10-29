"""Bound closure sensitivity to deleting one frozen source-record payload for a basis sense."""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

from src.analysis.basis_source_lineage_audit import build_report as build_source_lineage_report
from src.analysis.frozen_bundle_integrity import (
    DEFAULT_INTEGRITY_LOCK,
    verify_frozen_bundle_integrity,
)
from src.analysis.frozen_hypergraph_audit import DEFAULT_BUNDLE, closure, load_graph
from src.analysis.project_paths import PROJECT_ROOT


DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase231" / "basis_single_payload_deletion_audit.json"
SCHEMA_VERSION = "basis-single-payload-deletion-audit/1"


def _column_sums(row_masks: list[int], world_count: int) -> list[int]:
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


def _closure_masks(
    heads: set[str],
    clauses: list[tuple[str, tuple[str, ...], frozenset[str]]],
    basis: list[str],
    payload_paths: list[str],
    owner_paths: dict[str, set[str]],
    *,
    source_policy: str,
) -> tuple[dict[str, int], dict[str, int], int]:
    """Compute one closure world per deleted payload.

    source_policy='any': a clause stays if at least one listed source record remains.
    source_policy='all': a clause stays only if every listed source record remains.
    """
    if source_policy not in {"any", "all", "none"}:
        raise ValueError("source_policy must be any, all, or none")
    world_count = len(payload_paths)
    universe = (1 << world_count) - 1
    payload_world = {path: 1 << i for i, path in enumerate(payload_paths)}

    seed_removed_worlds = {seed: 0 for seed in basis}
    for seed, paths in owner_paths.items():
        if len(paths) == 1:
            seed_removed_worlds[seed] |= payload_world[next(iter(paths))]

    truth = {head: 0 for head in heads}
    queue: deque[str] = deque()

    def activate(head: str, candidate_worlds: int) -> None:
        delta = candidate_worlds & ~truth[head] & universe
        if delta:
            truth[head] |= delta
            queue.append(head)

    for seed in basis:
        activate(seed, universe & ~seed_removed_worlds[seed])

    clause_heads: list[str] = []
    clause_bodies: list[tuple[str, ...]] = []
    clause_active_worlds: list[int] = []
    fired_worlds: list[int] = []
    dependents: dict[str, list[int]] = defaultdict(list)
    for head, body, source_docs in clauses:
        index = len(clause_heads)
        clause_heads.append(head)
        clause_bodies.append(body)
        disabled_worlds = 0
        if source_policy == "all":
            for path in source_docs:
                disabled_worlds |= payload_world.get(path, 0)
        elif len(source_docs) == 1:
            disabled_worlds = payload_world.get(next(iter(source_docs)), 0)
        active_worlds = universe & ~disabled_worlds
        clause_active_worlds.append(active_worlds)
        fired_worlds.append(0)
        if not body:
            fired_worlds[index] = active_worlds
            activate(head, active_worlds)
        else:
            for premise in body:
                if premise not in heads:
                    raise ValueError(f"clause dependency is not a graph head: {premise}")
                dependents[premise].append(index)

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
    return truth, seed_removed_worlds, universe


def build_report(bundle: Path = DEFAULT_BUNDLE, integrity_lock: Path = DEFAULT_INTEGRITY_LOCK) -> dict[str, Any]:
    bundle = bundle.resolve()
    integrity = verify_frozen_bundle_integrity(bundle, integrity_lock)
    if not integrity.get("valid"):
        raise ValueError("frozen bundle integrity lock did not pass")
    lineage = build_source_lineage_report(bundle, integrity_lock)
    lineage_checks = lineage["checks"]
    lineage_counts = lineage["counts"]
    for check in (
        "basis_ids_match_nodes_one_to_one",
        "basis_ids_match_sense_index_one_to_one",
        "all_graph_clauses_have_exactly_one_active_source_index_row",
        "all_active_clause_documents_link_to_same_head_source_records",
    ):
        if not lineage_checks.get(check):
            raise ValueError(f"basis lineage prerequisite failed: {check}")
    if lineage_counts["basis_source_paths_shared_across_basis_seeds"]:
        raise ValueError("a source-record payload is shared across basis senses")
    if lineage_counts["basis_source_paths_linked_to_clause_evidence_for_multiple_index_rows"]:
        raise ValueError("a basis source-record payload is linked to clauses for multiple senses")

    rules, flat_clauses, _literal_count = load_graph(bundle)
    heads = set(rules)
    basis = sorted(
        line.strip()
        for line in (bundle / "graph" / "selected_basis_atoms.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    if not set(basis) <= heads:
        raise ValueError("basis contains a node absent from graph heads")
    if closure(heads, flat_clauses, set(basis)) != heads:
        raise ValueError("full basis does not derive every graph head")

    index_path = bundle / "indexes" / "senses.jsonl"
    basis_set = set(basis)
    basis_records: dict[str, set[str]] = {}
    clause_sources: dict[tuple[str, int], frozenset[str]] = {}
    for line_number, line in enumerate(index_path.open(encoding="utf-8"), 1):
        row = json.loads(line)
        identity = row.get("identity")
        if identity in basis_set:
            paths = {
                item.get("path")
                for item in row.get("source_records", [])
                if isinstance(item, dict) and isinstance(item.get("path"), str)
            }
            basis_records[identity] = paths
        for source_row in row.get("active_clause_sources", []):
            if not isinstance(source_row, dict) or not isinstance(source_row.get("clause_index"), int):
                raise ValueError(f"malformed clause-source row at sense index line {line_number}")
            key = (identity, source_row["clause_index"])
            documents = source_row.get("source_documents")
            if not isinstance(documents, list) or not documents:
                raise ValueError(f"clause has no source documents at sense index line {line_number}")
            if key in clause_sources:
                raise ValueError(f"duplicate clause-source mapping at sense index line {line_number}")
            clause_sources[key] = frozenset(documents)
    if set(basis_records) != basis_set or any(not paths for paths in basis_records.values()):
        raise ValueError("one or more basis senses lack a source-record payload")

    payload_owner: dict[str, str] = {}
    for identity, paths in basis_records.items():
        for path in paths:
            if path in payload_owner:
                raise ValueError("basis source-record payload maps to multiple sense identities")
            payload_owner[path] = identity
    payload_paths = sorted(payload_owner)
    if len(payload_paths) != lineage_counts["basis_source_record_path_associations"]:
        raise ValueError("payload scenario count disagrees with Phase229 source lineage audit")

    aligned_clauses: list[tuple[str, tuple[str, ...], frozenset[str]]] = []
    clause_cursor = 0
    for head, bodies in rules.items():
        for clause_index, body in enumerate(bodies):
            source_docs = clause_sources.get((head, clause_index))
            if not source_docs:
                raise ValueError(f"clause lacks source mapping: {head}#{clause_index}")
            aligned_clauses.append((head, body, source_docs))
            clause_cursor += 1
    if clause_cursor != len(flat_clauses) or len(clause_sources) != len(flat_clauses):
        raise ValueError("source-index clause mappings do not align exactly with graph clauses")

    seed_only_truth, seed_removed_worlds, seed_universe = _closure_masks(
        heads, aligned_clauses, basis, payload_paths, basis_records, source_policy="none"
    )
    any_truth, seed_removed_worlds, universe = _closure_masks(
        heads, aligned_clauses, basis, payload_paths, basis_records, source_policy="any"
    )
    all_truth, all_seed_removed_worlds, all_universe = _closure_masks(
        heads, aligned_clauses, basis, payload_paths, basis_records, source_policy="all"
    )
    if universe != all_universe or seed_universe != universe or seed_removed_worlds != all_seed_removed_worlds:
        raise ValueError("source policy changed the declared payload or seed-removal worlds")

    head_ids = sorted(heads)
    any_loss_masks = [universe & ~any_truth[head] for head in head_ids]
    all_loss_masks = [universe & ~all_truth[head] for head in head_ids]
    seed_only_loss_masks = [universe & ~seed_only_truth[head] for head in head_ids]
    if any(any_loss & ~all_loss for any_loss, all_loss in zip(any_loss_masks, all_loss_masks)):
        raise ValueError("permissive source policy lost a head not lost under strict policy")
    if any(
        actual_truth[head] & ~seed_only_truth[head]
        for actual_truth in (any_truth, all_truth)
        for head in heads
    ):
        raise ValueError("source deletion derived a head absent under seed-only deletion")
    if any(all_truth[head] & ~any_truth[head] for head in heads):
        raise ValueError("strict source policy derived a head absent under permissive policy")

    any_counts = _column_sums(any_loss_masks, len(payload_paths))
    all_counts = _column_sums(all_loss_masks, len(payload_paths))
    seed_counts = _column_sums(seed_only_loss_masks, len(payload_paths))
    any_extra = [all_count - any_count for any_count, all_count in zip(any_counts, all_counts)]
    any_seed_only_difference = sum(
        (actual ^ seed_only).bit_count()
        for actual, seed_only in zip(any_loss_masks, seed_only_loss_masks)
    )
    all_seed_only_difference = sum(
        (actual ^ seed_only).bit_count()
        for actual, seed_only in zip(all_loss_masks, seed_only_loss_masks)
    )

    direct_checks = []
    representative_indices = {0, len(payload_paths) - 1}
    representative_indices.update(
        index for index, path in enumerate(payload_paths)
        if len(basis_records[payload_owner[path]]) == 1
    )
    one_multi_record_payload = next(
        (index for index, path in enumerate(payload_paths)
         if len(basis_records[payload_owner[path]]) > 1),
        None,
    )
    if one_multi_record_payload is not None:
        representative_indices.add(one_multi_record_payload)
    for payload_index in sorted(representative_indices):
        removed_path = payload_paths[payload_index]
        owner = payload_owner[removed_path]
        seeds = set(basis)
        if len(basis_records[owner]) == 1:
            seeds.remove(owner)
        removed = {removed_path}
        any_clauses = [
            (head, body)
            for head, body, docs in aligned_clauses
            if bool(docs - removed)
        ]
        all_clauses = [
            (head, body)
            for head, body, docs in aligned_clauses
            if not (docs & removed)
        ]
        any_direct = closure(heads, any_clauses, seeds)
        all_direct = closure(heads, all_clauses, seeds)
        bit = 1 << payload_index
        any_expected_lost = {head for i, head in enumerate(head_ids) if any_loss_masks[i] & bit}
        all_expected_lost = {head for i, head in enumerate(head_ids) if all_loss_masks[i] & bit}
        direct_checks.append({
            "payload_scenario_index": payload_index,
            "basis_sense_source_record_count": len(basis_records[owner]),
            "permissive_policy_direct_closure_matches": heads - any_direct == any_expected_lost,
            "strict_policy_direct_closure_matches": heads - all_direct == all_expected_lost,
        })
    if not all(
        row["permissive_policy_direct_closure_matches"] and row["strict_policy_direct_closure_matches"]
        for row in direct_checks
    ):
        raise ValueError("direct closure cross-check failed")

    payload_owner_counts = Counter(len(paths) for paths in basis_records.values())
    rows = []
    for index, path in enumerate(payload_paths):
        owner = payload_owner[path]
        rows.append({
            "payload_scenario_index": index,
            "basis_owner_index": basis.index(owner),
            "basis_sense_payload_count": len(basis_records[owner]),
            "seed_retracted": len(basis_records[owner]) == 1,
            "permissive_any_source_loss_count": any_counts[index],
            "strict_all_sources_loss_count": all_counts[index],
            "strict_minus_permissive_loss_count": all_counts[index] - any_counts[index],
            "seed_only_loss_count": seed_counts[index],
        })
    max_source_doc_count = max((len(documents) for _, _, documents in aligned_clauses), default=0)
    return {
        "schema_version": SCHEMA_VERSION,
        "claim_type": "single_frozen_basis_source_record_payload_deletion_sensitivity",
        "intervention": {
            "unit": "delete exactly one frozen source-record payload path associated with a basis sense",
            "seed_policy": "retract a basis seed only when its last associated source-record payload is deleted",
            "permissive_rule_policy": "retain a clause if any listed source-record path remains",
            "strict_rule_policy": "retain a clause only if every listed source-record path remains",
            "scope_note": "These are explicit bookkeeping sensitivity policies for frozen payloads, not validated upstream source-document or semantic-support interventions.",
        },
        "inputs": {
            "bundle_integrity_valid": True,
            "bundle_root": str(bundle),
            "graph_rules_sha256": hashlib.sha256((bundle / "graph" / "hypergraph_rules.jsonl").read_bytes()).hexdigest(),
            "basis_atoms_sha256_sorted_utf8_lf": hashlib.sha256(("\n".join(basis) + "\n").encode("utf-8")).hexdigest(),
            "payload_scenario_count": len(payload_paths),
            "basis_sense_count": len(basis),
            "source_record_lineage_checks_passed": True,
            "all_graph_clause_source_mappings_aligned": True,
        },
        "counts": {
            "basis_senses_by_source_record_payload_count": dict(sorted(payload_owner_counts.items())),
            "clauses": len(aligned_clauses),
            "source_document_count_distribution_per_clause": dict(sorted(Counter(len(docs) for _, _, docs in aligned_clauses).items())),
            "maximum_source_document_count_per_clause": max_source_doc_count,
            "direct_closure_cross_checks": len(direct_checks),
        },
        "results": {
            "permissive_any_source_loss_min_median_max": _stats(any_counts),
            "strict_all_sources_loss_min_median_max": _stats(all_counts),
            "seed_only_loss_min_median_max": _stats(seed_counts),
            "payloads_with_nonzero_permissive_loss": sum(value > 0 for value in any_counts),
            "payloads_with_nonzero_strict_loss": sum(value > 0 for value in all_counts),
            "total_strict_minus_permissive_payload_head_losses": sum(any_extra),
            "permissive_vs_seed_only_differing_head_payload_incidences": any_seed_only_difference,
            "strict_vs_seed_only_differing_head_payload_incidences": all_seed_only_difference,
            "strict_loss_is_superset_of_permissive_loss_all_heads_and_worlds": True,
            "source_deletion_loss_is_superset_of_seed_only_loss_all_heads_and_worlds": True,
            "permissive_loss_is_subset_of_strict_loss_all_heads_and_worlds": True,
            "direct_closure_cross_checks_all_match": True,
        },
        "payload_rows": rows,
        "direct_closure_checks": direct_checks,
        "interpretation_limits": [
            "The 'any source remains' and 'all sources required' policies are sensitivity bounds, not a recovered producer-level logic contract.",
            "A source-record JSON payload is not the same object as an upstream WordNet document or release artifact.",
            "No gloss-span semantic support, licensing, or language-level effect is evaluated.",
            "The audit does not compare NLI systems or establish publication-level novelty.",
        ],
    }


def _stats(values: list[int]) -> list[int | float]:
    return [min(values), statistics.median(values), max(values)]


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
        f"Compared {report['inputs']['payload_scenario_count']} single-payload deletions: "
        f"{result['payloads_with_nonzero_permissive_loss']} permissive and "
        f"{result['payloads_with_nonzero_strict_loss']} strict scenarios have nonzero closure loss"
    )
    print(f"Wrote aggregate report: {args.output.resolve().relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
