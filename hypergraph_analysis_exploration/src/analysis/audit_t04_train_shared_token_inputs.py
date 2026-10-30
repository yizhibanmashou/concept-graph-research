"""Audit equal B/C/D text-token inventories on the frozen T04 training split only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any, Callable

from src.analysis.sense_representation_pilot import build
from src.analysis.t04_structure_views import build_aligned_relation_tensors


def _distribution(values: list[int]) -> dict[str, int | float | None]:
    if not values:
        return {"count": 0, "min": None, "median": None, "p90_nearest_rank": None, "max": None}
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "min": ordered[0],
        "median": median(ordered),
        "p90_nearest_rank": ordered[(9 * len(ordered) + 9) // 10 - 1],
        "max": ordered[-1],
    }


def summarize_shared_token_inputs(
    rows: list[dict[str, Any]],
    nodes: dict[str, str],
    rules: dict[str, list[list[str]]],
    encode: Callable[[str], list[int]],
) -> dict[str, Any]:
    """Use candidate IDs only; prepare one common node-token inventory for B/C/D."""
    occurrences: Counter[str] = Counter()
    for row in rows:
        candidate_ids = row.get("candidate_ids")
        if not isinstance(candidate_ids, list) or any(
            not isinstance(candidate_id, str) or not candidate_id for candidate_id in candidate_ids
        ):
            raise ValueError("each training row must contain nonempty candidate IDs")
        occurrences.update(candidate_ids)

    failed: Counter[str] = Counter()
    total_tokens: list[int] = []
    target_tokens: list[int] = []
    dependency_tokens: list[int] = []
    dependency_counts: list[int] = []
    branch_counts: list[int] = []
    pairwise_edges: list[int] = []
    incidence_cells: list[int] = []
    shared_hashes: Counter[str] = Counter()

    for candidate_id in sorted(occurrences):
        if candidate_id not in nodes:
            failed["target_node_missing"] += 1
            continue
        if not isinstance(nodes[candidate_id], str) or not nodes[candidate_id].strip():
            failed["target_gloss_missing"] += 1
            continue
        if candidate_id not in rules:
            failed["target_rule_missing"] += 1
            continue
        branches = rules[candidate_id]
        if not isinstance(branches, list) or not branches or any(
            not isinstance(branch, list) or not branch or any(
                not isinstance(member, str) or not member for member in branch
            )
            for branch in branches
        ):
            failed["invalid_or_empty_branch"] += 1
            continue
        dependencies = {member for branch in branches for member in branch}
        if any(dependency not in nodes for dependency in dependencies):
            failed["dependency_node_missing"] += 1
            continue
        if any(not isinstance(nodes[dependency], str) or not nodes[dependency].strip()
               for dependency in dependencies):
            failed["dependency_gloss_missing"] += 1
            continue

        try:
            item = build(candidate_id, nodes[candidate_id], branches, nodes)
            tensors = build_aligned_relation_tensors(candidate_id, branches)
            inventories = {}
            for condition in ("B", "C", "D"):
                form = item[condition]
                ordered_nodes = [(form["target"], form["gloss"])] + [
                    (entry["id"], entry["gloss"]) for entry in form["dependencies"]
                ]
                inventories[condition] = [
                    (node_id, tuple(encode(gloss))) for node_id, gloss in ordered_nodes
                ]
            if not (inventories["B"] == inventories["C"] == inventories["D"]):
                failed["condition_token_inventory_mismatch"] += 1
                continue
            expected_ids = set(tensors["node_ids"])
            if {node_id for node_id, _ in inventories["B"]} != expected_ids:
                failed["token_tensor_node_mismatch"] += 1
                continue
        except (KeyError, TypeError, ValueError):
            failed["candidate_encoding_error"] += 1
            continue

        token_lengths = [len(token_ids) for _, token_ids in inventories["B"]]
        target_length = len(inventories["B"][0][1])
        dep_length = sum(token_lengths[1:])
        total_tokens.append(sum(token_lengths))
        target_tokens.append(target_length)
        dependency_tokens.append(dep_length)
        dependency_counts.append(len(inventories["B"]) - 1)
        branch_counts.append(len(tensors["D"]["incidence_matrix"]))
        pairwise_edges.append(sum(sum(row) for row in tensors["C"]["adjacency_matrix"]) // 2)
        incidence_cells.append(sum(sum(row) for row in tensors["D"]["incidence_matrix"]))
        digest_input = json.dumps(inventories["B"], ensure_ascii=False, separators=(",", ":"))
        shared_hashes[hashlib.sha256(digest_input.encode("utf-8")).hexdigest()] += 1

    unique_candidates = len(occurrences)
    valid = unique_candidates - sum(failed.values())
    return {
        "schema": "t04-train-shared-token-input-audit/1",
        "split": "train_only",
        "rows": len(rows),
        "candidate_occurrences": sum(occurrences.values()),
        "unique_candidates": unique_candidates,
        "valid_shared_token_candidates": valid,
        "failed_unique_candidates": unique_candidates - valid,
        "failure_categories": dict(sorted(failed.items())),
        "shared_text_token_hashes": {
            "unique_bundles": len(shared_hashes),
            "conditions_equal_for_all_valid_candidates": valid,
        },
        "token_piece_counts_without_special_tokens_or_truncation": {
            "target_gloss": _distribution(target_tokens),
            "all_dependency_glosses_per_candidate": _distribution(dependency_tokens),
            "target_plus_dependency_glosses_per_candidate": _distribution(total_tokens),
        },
        "structure_sizes_per_candidate": {
            "dependency_nodes": _distribution(dependency_counts),
            "branches": _distribution(branch_counts),
            "pairwise_edges": _distribution(pairwise_edges),
            "branch_node_incidence_cells": _distribution(incidence_cells),
        },
        "limits": (
            "Uses only candidate IDs from the supplied training split; glosses are tokenized but never emitted or "
            "semantically inspected. No labels, contexts, development/test examples, model training, learned scores, "
            "special-token overhead, truncation, or memory measurements are included. Equal text tokens are verified "
            "for these candidate records, not equal compute or semantic quality."
        ),
    }


def _load_graph(bundle: Path) -> tuple[dict[str, str], dict[str, list[list[str]]]]:
    graph = bundle / "graph"
    with (graph / "nodes.tsv").open(encoding="utf-8-sig", newline="") as stream:
        nodes = {row["synset_id"]: row["definition"] for row in csv.DictReader(stream, delimiter="\t")}
    rules: dict[str, list[list[str]]] = {}
    with (graph / "hypergraph_rules.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                row = json.loads(line)
                rules[row["head"]] = row["clauses"]
    return nodes, rules


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--vocab", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="new output path")
    args = parser.parse_args()

    import tokenizers

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    if tokenizers.__version__ != metadata.get("tokenizers_version"):
        raise ValueError("tokenizers version differs from frozen training metadata")
    vocab_sha = hashlib.sha256(args.vocab.read_bytes()).hexdigest()
    if vocab_sha != metadata.get("inputs_sha256", {}).get("vocab.txt"):
        raise ValueError("vocabulary SHA-256 differs from frozen training metadata")
    nodes_path = args.bundle / "graph/nodes.tsv"
    rules_path = args.bundle / "graph/hypergraph_rules.jsonl"
    for name, path in (("nodes.tsv", nodes_path), ("rules.jsonl", rules_path)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != metadata.get("inputs_sha256", {}).get(name):
            raise ValueError(f"{name} differs from frozen training metadata")

    rows = json.loads(args.train.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("train input must be a JSON array")
    nodes, rules = _load_graph(args.bundle)
    tokenizer = tokenizers.BertWordPieceTokenizer(str(args.vocab), lowercase=True)
    report = summarize_shared_token_inputs(
        rows, nodes, rules,
        lambda text: tokenizer.encode(text, add_special_tokens=False).ids,
    )
    report["tokenizer"] = {
        "implementation": "BertWordPieceTokenizer",
        "version": tokenizers.__version__,
        "lowercase": True,
        "vocab_sha256": vocab_sha,
    }
    report["input_sha256"] = {
        "train_json": hashlib.sha256(args.train.read_bytes()).hexdigest(),
        "metadata_json": hashlib.sha256(args.metadata.read_bytes()).hexdigest(),
        "nodes_tsv": hashlib.sha256(nodes_path.read_bytes()).hexdigest(),
        "hypergraph_rules_jsonl": hashlib.sha256(rules_path.read_bytes()).hexdigest(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps({key: report[key] for key in (
        "rows", "candidate_occurrences", "unique_candidates", "valid_shared_token_candidates",
        "failed_unique_candidates", "failure_categories", "shared_text_token_hashes",
    )}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
