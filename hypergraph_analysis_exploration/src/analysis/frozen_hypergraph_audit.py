"""Reproducible structural audit for the delivered OEWN frozen Horn bundle.

This verifies pinned bundle integrity, AND/OR closure and witness certificates.
It does not establish truth-conditional entailment of natural-language definitions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict, deque
from pathlib import Path

try:  # Direct script execution and package/module execution are both supported.
    from .frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK, verify_frozen_bundle_integrity
    from .project_paths import PROJECT_ROOT, configured_bundle_root
except ImportError:
    from frozen_bundle_integrity import DEFAULT_INTEGRITY_LOCK, verify_frozen_bundle_integrity
    from project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_BUNDLE = configured_bundle_root()


def jsonl(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc


def load_graph(bundle: Path):
    rules = {}
    clauses = []
    literals = 0
    for row in jsonl(bundle / "graph" / "hypergraph_rules.jsonl"):
        head = row["head"]
        if head in rules:
            raise ValueError(f"Duplicate rule head: {head}")
        body_list = [tuple(sorted(set(body))) for body in row["clauses"]]
        if any(len(body) != len(raw) for body, raw in zip(body_list, row["clauses"])):
            raise ValueError(f"Duplicate literal in clause for {head}")
        rules[head] = body_list
        for body in body_list:
            clauses.append((head, body))
            literals += len(body)
    return rules, clauses, literals


def closure(heads, clauses, seeds):
    """Least forward Horn closure for OR-of-AND rules.

    Empty bodies are true conjunctions, so their heads enter the closure before
    forward propagation begins.
    """
    by_dep = defaultdict(list)
    remaining = []
    covered = set(seeds)
    queue = deque(seeds)
    for head, body in clauses:
        if not body:
            remaining.append(0)
            if head not in covered:
                covered.add(head)
                queue.append(head)
            continue
        idx = len(remaining)
        remaining.append(len(body))
        for dep in body:
            by_dep[dep].append(idx)
    clause_head = [head for head, _ in clauses]
    while queue:
        dep = queue.popleft()
        for idx in by_dep.get(dep, ()):
            remaining[idx] -= 1
            if remaining[idx] == 0:
                head = clause_head[idx]
                if head not in covered:
                    covered.add(head)
                    queue.append(head)
    return covered


def basis_sensitivity(heads, clauses, basis, witness_by_head):
    """Compare exact single-seed closure loss with selected-witness descendants.

    Both measures are structural. The closure loss respects every OR alternative;
    witness descendants use only the package's one selected proof per head and
    exclude the removed seed itself. Keep a root-inclusive legacy difference for
    continuity, but compare descendants against non-seed closure loss for the
    like-for-like diagnostic.
    """
    reverse_witness_edges = defaultdict(set)
    for head, witness in witness_by_head.items():
        for dependency in witness.get("witness_clause", []):
            reverse_witness_edges[dependency].add(head)

    rows = []
    for seed in sorted(basis):
        reduced = closure(heads, clauses, basis - {seed})
        exact_lost = heads - reduced
        exact_nonseed_lost = exact_lost - {seed}
        descendants = set()
        queue = deque(sorted(reverse_witness_edges.get(seed, ())))
        while queue:
            current = queue.popleft()
            if current in descendants or current == seed:
                continue
            descendants.add(current)
            queue.extend(sorted(reverse_witness_edges.get(current, ())))
        rows.append({
            "basis_atom": seed,
            "exact_and_or_closure_loss_count": len(exact_lost),
            "exact_nonseed_and_or_closure_loss_count": len(exact_nonseed_lost),
            "selected_witness_descendant_count": len(descendants),
            "exact_nonseed_loss_outside_selected_witness_descendants_count": len(exact_nonseed_lost - descendants),
            "selected_witness_descendants_not_lost_after_deletion_count": len(descendants - exact_nonseed_lost),
            "witness_minus_exact_nonseed_loss_count": len(descendants) - len(exact_nonseed_lost),
            # Retained for consumers of the original Phase175 metric. This compares
            # descendants (which omit the root) against root-inclusive loss.
            "witness_minus_exact_loss_count": len(descendants) - len(exact_lost),
            "removed_basis_atom_rederived": seed in reduced,
        })
    return rows


def validate_witnesses(heads, basis, rules, witness_rows):
    """Check one selected witness per head and exact max-dependency depth.

    This validates certificates relative to the package's declared basis and
    AND/OR rules. It does not validate the natural-language semantics of a rule.
    """
    witness_by_head = {}
    duplicate_heads = set()
    malformed_rows = 0
    for row in witness_rows:
        if not isinstance(row, dict) or not isinstance(row.get("head"), str):
            malformed_rows += 1
            continue
        head = row["head"]
        if head in witness_by_head:
            duplicate_heads.add(head)
        else:
            witness_by_head[head] = row

    missing_heads = set(heads) - set(witness_by_head)
    unexpected_heads = set(witness_by_head) - set(heads)
    invalid_heads = set(duplicate_heads) | set(unexpected_heads)
    seed_flag_mismatches = set()
    wrong_depth_heads = set()

    for head, witness in witness_by_head.items():
        if head not in heads:
            continue
        is_seed = witness.get("is_seed")
        depth = witness.get("proof_depth")
        body = witness.get("witness_clause")
        if not isinstance(depth, int) or isinstance(depth, bool) or depth < 0:
            invalid_heads.add(head)
            continue
        if not isinstance(body, list) or any(not isinstance(dep, str) for dep in body):
            invalid_heads.add(head)
            continue
        if len(body) != len(set(body)):
            invalid_heads.add(head)

        if head in basis:
            if is_seed is not True or depth != 0 or body:
                seed_flag_mismatches.add(head)
                invalid_heads.add(head)
            continue

        if is_seed is not False:
            seed_flag_mismatches.add(head)
            invalid_heads.add(head)
        body_key = tuple(sorted(body))
        if body_key not in rules.get(head, []):
            invalid_heads.add(head)
            continue
        if any(dep not in witness_by_head for dep in body):
            invalid_heads.add(head)
            continue
        dependency_depths = [witness_by_head[dep].get("proof_depth") for dep in body]
        if any(not isinstance(dep_depth, int) or isinstance(dep_depth, bool) or dep_depth < 0
               for dep_depth in dependency_depths):
            invalid_heads.add(head)
            continue
        if depth != 1 + max(dependency_depths, default=0):
            wrong_depth_heads.add(head)
            invalid_heads.add(head)

    return {
        "witness_by_head": witness_by_head,
        "missing_head_count": len(missing_heads),
        "unexpected_head_count": len(unexpected_heads),
        "duplicate_head_count": len(duplicate_heads),
        "malformed_record_count": malformed_rows,
        "seed_flag_mismatch_count": len(seed_flag_mismatches),
        "wrong_depth_count": len(wrong_depth_heads),
        "invalid_head_count": len(invalid_heads) + malformed_rows,
        "all_valid": not (missing_heads or unexpected_heads or duplicate_heads
                           or malformed_rows or invalid_heads),
    }


def audit(bundle: Path, integrity_lock: Path = DEFAULT_INTEGRITY_LOCK):
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    bundle_integrity = verify_frozen_bundle_integrity(bundle, integrity_lock)
    rules, clauses, literal_count = load_graph(bundle)
    heads = set(rules)
    basis = {line.strip() for line in (bundle / "graph" / "selected_basis_atoms.txt").read_text(encoding="utf-8").splitlines() if line.strip()}
    widths = [len(body) for _, body in clauses]
    missing = sorted({dep for _, body in clauses for dep in body} - heads)
    self_clauses = sum(head in body for head, body in clauses)
    empty_clauses = sum(not body for _, body in clauses)
    duplicate_clauses = sum(len(body_list) - len(set(body_list)) for body_list in rules.values())
    full_closure = closure(heads, clauses, basis)

    witness_check = validate_witnesses(
        heads, basis, rules, jsonl(bundle / "graph" / "coverage_witnesses.jsonl"))
    witness_by_head = witness_check["witness_by_head"]
    depth_counter = Counter()
    for head, witness in witness_by_head.items():
        depth = witness.get("proof_depth")
        if isinstance(depth, int) and not isinstance(depth, bool) and depth >= 0:
            depth_counter[depth] += 1

    basis_sensitivity_rows = basis_sensitivity(heads, clauses, basis, witness_by_head)
    deletion_losses = [row["exact_and_or_closure_loss_count"] for row in basis_sensitivity_rows]
    witness_overestimates = sum(row["witness_minus_exact_nonseed_loss_count"] > 0 for row in basis_sensitivity_rows)
    witness_underestimates = sum(row["witness_minus_exact_nonseed_loss_count"] < 0 for row in basis_sensitivity_rows)
    witness_matches = len(basis_sensitivity_rows) - witness_overestimates - witness_underestimates

    expected = manifest
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    graph_sha256 = hashlib.sha256()
    with rules_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            graph_sha256.update(chunk)
    graph_sha256 = graph_sha256.hexdigest()
    checksum_row = next((row for row in jsonl(bundle / "checksums.jsonl")
                         if row.get("path") == "graph/hypergraph_rules.jsonl"), None)
    node_ids = set()
    with (bundle / "graph" / "nodes.tsv").open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            node_ids.add(row.get("synset_id", ""))
    hyperedge_rows = list(jsonl(bundle / "graph" / "hyperedges.jsonl"))
    hyperedge_counter = Counter((row["head"], tuple(sorted(row["dependencies"]))) for row in hyperedge_rows)
    rule_counter = Counter((head, tuple(sorted(body))) for head, body in clauses)
    hyperedges_match_rules = hyperedge_counter == rule_counter
    return {
        "claim_type": "structural_definitional_availability_not_truth_conditional_entailment",
        "bundle": str(bundle),
        "manifest": {
            "graph_sha256": manifest.get("graph_sha256"),
            "observed_rules_file_sha256": graph_sha256,
            "checksums_entry_sha256": checksum_row.get("sha256") if checksum_row else None,
            "semantic_fingerprint_sha256": manifest.get("semantic_fingerprint_sha256"),
            "manifest_head_count": manifest.get("head_count"),
            "manifest_clause_count": manifest.get("clause_count"),
            "manifest_max_structural_layer": manifest.get("max_structural_layer"),
        },
        "bundle_integrity": bundle_integrity,
        "observed": {
            "head_count": len(heads), "clause_count": len(clauses),
            "dependency_literal_count": literal_count, "basis_count": len(basis),
            "basis_closure_count": len(full_closure), "basis_closure_complete": full_closure == heads,
            "missing_dependency_head_count": len(missing), "self_dependent_clause_count": self_clauses,
            "empty_clause_count": empty_clauses, "duplicate_clause_count": duplicate_clauses,
            "alternative_head_count": sum(len(x) > 1 for x in rules.values()),
            "clause_width": {"min": min(widths), "median": statistics.median(widths),
                             "p90": sorted(widths)[int(.9 * (len(widths)-1))], "max": max(widths)},
            "witness_record_count": sum(1 for _ in jsonl(bundle / "graph" / "coverage_witnesses.jsonl")),
            "witness_missing_head_count": witness_check["missing_head_count"],
            "witness_unexpected_head_count": witness_check["unexpected_head_count"],
            "witness_duplicate_head_count": witness_check["duplicate_head_count"],
            "witness_malformed_record_count": witness_check["malformed_record_count"],
            "witness_seed_flag_mismatch_count": witness_check["seed_flag_mismatch_count"],
            "witness_wrong_depth_count": witness_check["wrong_depth_count"],
            "invalid_witness_count": witness_check["invalid_head_count"], "max_witness_depth": max(depth_counter, default=0),
            "witness_depth_301_plus_count": sum(n for d, n in depth_counter.items() if d >= 301),
            "witness_depth_301_plus_fraction": sum(n for d, n in depth_counter.items() if d >= 301) / len(heads),
            "nodes_tsv_id_count": len(node_ids), "nodes_tsv_ids_match_rules": node_ids == heads,
            "hyperedge_record_count": len(hyperedge_rows), "hyperedges_match_rules": hyperedges_match_rules,
            "basis_single_deletion_loss": {"min": min(deletion_losses), "median": statistics.median(deletion_losses),
                                            "max": max(deletion_losses), "all_nonzero": all(x > 0 for x in deletion_losses),
                                            "witness_descendant_comparison": {
                                                "compared_with": "exact_nonseed_and_or_closure_loss_count",
                                                "overestimates": witness_overestimates,
                                                "underestimates": witness_underestimates,
                                                "matches": witness_matches,
                                                "sum_exact_nonseed_losses_outside_descendants": sum(
                                                    row["exact_nonseed_loss_outside_selected_witness_descendants_count"]
                                                    for row in basis_sensitivity_rows
                                                ),
                                                "sum_descendants_not_lost_after_deletion": sum(
                                                    row["selected_witness_descendants_not_lost_after_deletion_count"]
                                                    for row in basis_sensitivity_rows
                                                ),
                                            }},
        },
        "basis_single_deletion_sensitivity": basis_sensitivity_rows,
        "manifest_count_checks": {
            "heads_match": len(heads) == expected.get("head_count"),
            "clauses_match": len(clauses) == expected.get("clause_count"),
            "rules_file_sha256_matches_manifest": graph_sha256 == expected.get("graph_sha256"),
            "rules_file_sha256_matches_checksums": bool(checksum_row and graph_sha256 == checksum_row.get("sha256")),
        },
        "integrity_checks": {
            "pinned_bundle_files_match_integrity_lock": bundle_integrity["valid"],
            "no_missing_dependencies": not missing, "no_self_dependent_clauses": self_clauses == 0,
            "no_empty_clauses": empty_clauses == 0, "no_duplicate_clauses": duplicate_clauses == 0,
            "complete_basis_closure": full_closure == heads, "all_witnesses_valid": witness_check["all_valid"],
            "nodes_match_rules": node_ids == heads, "hyperedges_match_rules": hyperedges_match_rules,
        },
        "limitations": [
            "Closure is over the package's positive Horn dependency representation only.",
            "A witness DAG is a structural derivation certificate, not by itself a proof of natural-language entailment.",
            "Single-deletion irredundancy does not prove global minimum cardinality of the basis.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--integrity-lock", type=Path, default=DEFAULT_INTEGRITY_LOCK)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "outputs" / "phase6" / "frozen_hypergraph_audit.json")
    parser.add_argument("--force", action="store_true", help="replace the existing report")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and not args.force:
        parser.error(f"Output exists; pass --force to replace: {output}")
    result = audit(args.bundle.resolve(), args.integrity_lock.resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "integrity_checks": result["integrity_checks"]}, ensure_ascii=False, indent=2))
    if not all(result["integrity_checks"].values()) or not all(result["manifest_count_checks"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
