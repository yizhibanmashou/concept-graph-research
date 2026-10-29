"""Independently replay OEWN hypernym proof paths against a pinned release.

This checks resource-relative graph reachability certificates only. It does not
judge whether a source definition entails the relation.
"""
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from typing import Any

from src.analysis.oewn_hypernym_verifier import (
    DEFAULT_RELEASE_ARCHIVE,
    DEFAULT_RELEASE_DIR,
    _pos_family,
    load_claims,
    load_hypernym_graph,
    verify_extracted_taxonomy,
)
from src.analysis.gloss_genus_baseline import _sha256


REPLAY_VERSION = "oewn-hypernym-path-replay/3"
EXPECTED_TRANSITIVITY_RULE = {
    "rule_id": "oewn_hypernym_transitivity/1",
    "body": [
        {"predicate": "oewn_hypernym", "arguments": ["?x", "?y"]},
        {"predicate": "oewn_hypernym", "arguments": ["?y", "?z"]},
    ],
    "head": {"predicate": "oewn_hypernym", "arguments": ["?x", "?z"]},
}
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase16" / "oewn_hypernym_verification.json"


def _reachable(start: str, goal: str, parents: dict[str, tuple[str, ...]]) -> bool:
    """Independent reachability replay; deliberately does not reuse producer BFS."""
    stack = [start]
    seen: set[str] = set()
    while stack:
        current = stack.pop()
        if current == goal:
            return True
        if current in seen:
            continue
        seen.add(current)
        stack.extend(parents.get(current, ()))
    return False


def _independent_acyclicity_check(
    nodes: dict[str, dict[str, str]], parents: dict[str, tuple[str, ...]]
) -> dict[str, Any]:
    """Recompute graph acyclicity using iterative DFS colors (not Kahn's method)."""
    children: dict[str, list[str]] = {synset_id: [] for synset_id in nodes}
    for child_id, parent_ids in parents.items():
        children[child_id].extend(parent_ids)
    color: dict[str, int] = {}  # 0=unseen, 1=active, 2=finished
    has_cycle = False
    for start in nodes:
        if color.get(start, 0):
            continue
        color[start] = 1
        stack: list[tuple[str, int]] = [(start, 0)]
        while stack:
            current, index = stack[-1]
            neighbors = children.get(current, ())
            if index >= len(neighbors):
                color[current] = 2
                stack.pop()
                continue
            neighbor = neighbors[index]
            stack[-1] = (current, index + 1)
            state = color.get(neighbor, 0)
            if state == 1:
                has_cycle = True
            elif state == 0:
                color[neighbor] = 1
                stack.append((neighbor, 0))
    return {"acyclic": not has_cycle}


def _path_errors(
    path: Any,
    start: str,
    goal: str,
    nodes: dict[str, dict[str, str]],
    parents: dict[str, tuple[str, ...]],
    where: str,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(path, list) or not path:
        return [f"{where} must be a non-empty edge list"]
    current = start
    visited = {start}
    for index, edge in enumerate(path):
        label = f"{where}[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"{label} must be an object")
            continue
        child_id = edge.get("child_synset_id")
        parent_id = edge.get("hypernym_synset_id")
        if child_id != current:
            errors.append(f"{label} breaks path direction/continuity")
        if not isinstance(child_id, str) or not isinstance(parent_id, str):
            errors.append(f"{label} must contain child and hypernym synset IDs")
            continue
        if child_id not in nodes or parent_id not in nodes:
            errors.append(f"{label} references a synset absent from the pinned release")
            continue
        if parent_id not in parents.get(child_id, ()):
            errors.append(f"{label} is not a direct hypernym edge in the pinned release")
        if edge.get("source_file") != nodes[child_id]["source_file"]:
            errors.append(f"{label} source_file does not match the release record for its child")
        if _pos_family(nodes[child_id]["pos"]) != _pos_family(nodes[parent_id]["pos"]):
            errors.append(f"{label} crosses POS families")
        current = parent_id
        if current in visited and index < len(path) - 1:
            errors.append(f"{where} repeats a synset before reaching its endpoint")
        visited.add(current)
    if current != goal:
        errors.append(f"{where} ends at {current!r}, expected {goal!r}")
    return errors


def _logical_proof_errors(proof: Any, path: Any, where: str) -> list[str]:
    """Check the explicit ground-fact and Horn-transitivity proof DAG."""
    if not isinstance(proof, dict):
        return [f"{where} must be an object for a positive path"]
    if not isinstance(path, list) or not path or any(not isinstance(edge, dict) for edge in path):
        return [f"{where} cannot be checked because proof_path is malformed"]
    errors = []
    if proof.get("rule") != EXPECTED_TRANSITIVITY_RULE:
        errors.append(f"{where} transitivity rule schema is missing or altered")
    expected_steps = []
    for index, edge in enumerate(path):
        expected_steps.append({
            "id": f"fact-{index}",
            "kind": "fact",
            "atom": {"predicate": "oewn_hypernym",
                     "arguments": [edge.get("child_synset_id"), edge.get("hypernym_synset_id")]},
            "source_file": edge.get("source_file"),
        })
    root_step_id = "fact-0"
    first_child = path[0].get("child_synset_id")
    for index in range(1, len(path)):
        root_step_id = f"derive-{index}"
        previous_step_id = "fact-0" if index == 1 else f"derive-{index - 1}"
        expected_steps.append({
            "id": root_step_id,
            "kind": "rule_application",
            "rule_id": EXPECTED_TRANSITIVITY_RULE["rule_id"],
            "premises": [previous_step_id, f"fact-{index}"],
            "atom": {"predicate": "oewn_hypernym",
                     "arguments": [first_child, path[index].get("hypernym_synset_id")]},
        })
    if proof.get("steps") != expected_steps:
        errors.append(f"{where} proof steps do not exactly follow the path facts and transitivity rule")
    if proof.get("root_step_id") != root_step_id:
        errors.append(f"{where} root_step_id does not identify the final claim")
    return errors


def verify_report(
    report: Any,
    claims: list[dict[str, Any]],
    taxonomy_manifest: dict[str, Any],
    nodes: dict[str, dict[str, str]],
    parents: dict[str, tuple[str, ...]],
    claims_sha256: str,
) -> dict[str, Any]:
    """Replay every result row and bind it to the exact release and claim file."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"valid": False, "errors": ["report must be a JSON object"]}
    if report.get("verifier_version") != "oewn-hypernym-closure-verifier/2":
        errors.append("unsupported producer verifier_version")
    inputs = report.get("inputs")
    if not isinstance(inputs, dict):
        inputs = {}
        errors.append("report inputs must be an object")
    for key, value in taxonomy_manifest.items():
        if inputs.get(key) != value:
            errors.append(f"report input {key} does not match the verified OEWN release")
    if inputs.get("claims_sha256") != claims_sha256:
        errors.append("report claims_sha256 does not match the supplied claims file")
    expected_edge_count = sum(len(row) for row in parents.values())
    expected_inputs = {"synset_count": len(nodes), "direct_hypernym_edge_count": expected_edge_count}
    for key, value in expected_inputs.items():
        if inputs.get(key) != value:
            errors.append(f"report input {key} does not match the loaded graph")
    claimed_graph_audit = report.get("taxonomy_graph_audit")
    independent_graph_audit = _independent_acyclicity_check(nodes, parents)
    graph_residual = claimed_graph_audit.get("unprocessed_node_count") if isinstance(claimed_graph_audit, dict) else None
    residual_valid = (
        type(graph_residual) is int and graph_residual == 0
        if independent_graph_audit["acyclic"]
        else type(graph_residual) is int and 0 < graph_residual <= len(nodes)
    )
    if (not isinstance(claimed_graph_audit, dict)
            or claimed_graph_audit.get("acyclic") != independent_graph_audit["acyclic"]
            or not residual_valid):
        errors.append("taxonomy_graph_audit does not match independent cycle verification")

    claim_by_id = {row.get("claim_id"): row for row in claims if isinstance(row, dict)}
    if len(claim_by_id) != len(claims):
        errors.append("claims file contains malformed or duplicate claim IDs")
    result_rows = report.get("results")
    if not isinstance(result_rows, list):
        errors.append("report results must be a list")
        result_rows = []
    if type(report.get("claim_count")) is not int or report["claim_count"] != len(claims):
        errors.append("claim_count does not match supplied claims")
    if len(result_rows) != len(claims):
        errors.append("result row count does not match supplied claims")

    seen_result_ids: set[str] = set()
    counts: dict[str, int] = {}
    replayed_paths = 0
    for index, result in enumerate(result_rows):
        where = f"results[{index}]"
        if not isinstance(result, dict):
            errors.append(f"{where} must be an object")
            continue
        claim_id = result.get("claim_id")
        if not isinstance(claim_id, str) or claim_id in seen_result_ids:
            errors.append(f"{where} has a missing or duplicate claim_id")
            continue
        seen_result_ids.add(claim_id)
        claim = claim_by_id.get(claim_id)
        if claim is None:
            errors.append(f"{where} is not present in the supplied claims")
            continue
        child_id, ancestor_id = claim.get("child_synset_id"), claim.get("ancestor_synset_id")
        if result.get("child_synset_id") != child_id or result.get("ancestor_synset_id") != ancestor_id:
            errors.append(f"{where} endpoints do not match the supplied claim")
        status = result.get("status")
        if not isinstance(status, str):
            errors.append(f"{where}.status must be a string")
            continue
        counts[status] = counts.get(status, 0) + 1

        if not isinstance(child_id, str) or not isinstance(ancestor_id, str):
            errors.append(f"{where} claim endpoints are malformed")
            continue
        if child_id not in nodes or ancestor_id not in nodes:
            if (status != "unknown_missing_synset" or result.get("proof_path") is not None
                    or result.get("logical_proof") is not None):
                errors.append(f"{where} missing-synset status/certificate is inconsistent")
            continue
        if result.get("child_pos") != nodes[child_id]["pos"]:
            errors.append(f"{where} child_pos does not match the pinned release")
        if _pos_family(nodes[child_id]["pos"]) != _pos_family(nodes[ancestor_id]["pos"]):
            if (status != "unsupported_cross_pos" or result.get("proof_path") is not None
                    or result.get("logical_proof") is not None):
                errors.append(f"{where} cross-POS status/certificate is inconsistent")
            continue
        if child_id == ancestor_id:
            if (status != "not_a_proper_hypernym" or result.get("proof_path") is not None
                    or result.get("logical_proof") is not None):
                errors.append(f"{where} reflexive status/certificate is inconsistent")
            continue

        path = result.get("proof_path")
        if status in {"direct_hypernym", "transitive_hypernym"}:
            if result.get("reverse_path") is not None:
                errors.append(f"{where} positive result must not contain reverse_path")
            errors.extend(_path_errors(path, child_id, ancestor_id, nodes, parents, f"{where}.proof_path"))
            errors.extend(_logical_proof_errors(result.get("logical_proof"), path,
                                                f"{where}.logical_proof"))
            if isinstance(path, list) and path:
                replayed_paths += 1
                expected_status = "direct_hypernym" if len(path) == 1 else "transitive_hypernym"
                if status != expected_status:
                    errors.append(f"{where} status does not match proof path length")
                if not _reachable(child_id, ancestor_id, parents):
                    errors.append(f"{where} path claims a relation absent from the pinned graph")
                # A positive edge path is sufficient evidence; check the claimed
                # shortest-path property using reverse reachability distances.
                if _shortest_distance_to_target(child_id, ancestor_id, parents) != len(path):
                    errors.append(f"{where} proof_path is not shortest")
        elif status == "not_in_hypernym_closure":
            if path is not None or result.get("logical_proof") is not None:
                errors.append(f"{where} negative result must not contain positive proof material")
            if _reachable(child_id, ancestor_id, parents):
                errors.append(f"{where} claims non-reachability but a path exists in the pinned graph")
            reverse_path = result.get("reverse_path")
            if reverse_path is not None:
                errors.extend(_path_errors(reverse_path, ancestor_id, child_id, nodes, parents,
                                           f"{where}.reverse_path"))
        else:
            errors.append(f"{where} has unsupported status for present same-family synsets: {status}")

    if seen_result_ids != set(claim_by_id):
        errors.append("results do not cover every supplied claim exactly once")
    if report.get("status_counts") != dict(sorted(counts.items())):
        errors.append("status_counts do not match result rows")
    return {
        "replay_version": REPLAY_VERSION,
        "valid": not errors,
        "claim_count": len(claims),
        "claims_sha256": claims_sha256,
        "replayed_positive_paths": replayed_paths,
        "status_counts": dict(sorted(counts.items())),
        "release_archive_sha256": taxonomy_manifest.get("archive_sha256"),
        "errors": errors,
        "scope_note": "Replays relation paths and release/claim fingerprints only; it does not validate gloss semantics or provide an open-world negative proof.",
    }


def _shortest_distance_to_target(
    start: str, goal: str, parents: dict[str, tuple[str, ...]]
) -> int | None:
    """Compute shortest length independently by traversing reverse adjacency."""
    children: dict[str, list[str]] = {synset_id: [] for synset_id in parents}
    for child_id, parent_ids in parents.items():
        for parent_id in parent_ids:
            children[parent_id].append(child_id)
    queue = deque([(goal, 0)])
    seen = {goal}
    while queue:
        current, distance = queue.popleft()
        if current == start:
            return distance
        for child_id in children.get(current, ()):
            if child_id not in seen:
                seen.add(child_id)
                queue.append((child_id, distance + 1))
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", nargs="?", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("claims", nargs="?", type=Path, default=PROJECT_ROOT / "config" / "hypernym_claims.example.jsonl")
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = verify_extracted_taxonomy(args.release_dir, args.release_archive)
        nodes, parents = load_hypernym_graph(args.release_dir)
        claims = load_claims(args.claims)
        report = json.loads(args.report.read_text(encoding="utf-8"))
        result = verify_report(report, claims, manifest, nodes, parents, _sha256(args.claims))
        result["producer_report_sha256"] = _sha256(args.report)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Certificate replay valid={result['valid']}; claims={result['claim_count']}; errors={len(result['errors'])}")
    if args.output:
        print(f"Replay report: {args.output}")
    if not result["valid"]:
        for error in result["errors"][:20]:
            print(f"- {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
