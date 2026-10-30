"""Audit graph availability for frozen T04 training candidates, without gold labels."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

from src.analysis.t04_structure_views import build_relation_views


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


def summarize_train_inventory(
    rows: list[dict[str, Any]],
    nodes: dict[str, str],
    rules: dict[str, list[list[str]]],
) -> dict[str, Any]:
    """Check only candidate IDs and graph inventory; never inspect labels or text."""
    occurrence_counts: Counter[str] = Counter()
    for row in rows:
        candidate_ids = row.get("candidate_ids")
        if not isinstance(candidate_ids, list) or any(
            not isinstance(candidate_id, str) or not candidate_id for candidate_id in candidate_ids
        ):
            raise ValueError("each training row must contain nonempty candidate IDs")
        occurrence_counts.update(candidate_ids)

    unique_candidates = sorted(occurrence_counts)
    failures: Counter[str] = Counter()
    branch_counts: list[int] = []
    dependency_counts: list[int] = []
    pairwise_edge_counts: list[int] = []
    incidence_cell_counts: list[int] = []
    complete = 0

    for candidate_id in unique_candidates:
        if candidate_id not in nodes:
            failures["target_node_missing"] += 1
            continue
        if not nodes[candidate_id].strip():
            failures["target_gloss_missing"] += 1
            continue
        if candidate_id not in rules:
            failures["target_rule_missing"] += 1
            continue
        branches = rules[candidate_id]
        if not isinstance(branches, list) or not branches or any(
            not isinstance(branch, list) or not branch or any(
                not isinstance(member, str) or not member for member in branch
            )
            for branch in branches
        ):
            failures["invalid_or_empty_branch"] += 1
            continue
        dependencies = {member for branch in branches for member in branch}
        if any(dependency not in nodes for dependency in dependencies):
            failures["dependency_node_missing"] += 1
            continue
        if any(not nodes[dependency].strip() for dependency in dependencies):
            failures["dependency_gloss_missing"] += 1
            continue
        try:
            views = build_relation_views(candidate_id, branches)
        except ValueError:
            failures["relation_view_invalid"] += 1
            continue
        if set(views["node_ids"]) != {candidate_id, *dependencies}:
            failures["shared_node_inventory_mismatch"] += 1
            continue
        complete += 1
        branch_counts.append(len(views["D"]["branches"]))
        dependency_counts.append(len(views["B"]["dependencies"]))
        pairwise_edge_counts.append(len(views["C"]["pairwise_edges"]))
        incidence_cell_counts.append(sum(len(branch) for branch in views["D"]["branches"]))

    return {
        "schema": "t04-train-graph-inventory-audit/1",
        "split": "train_only",
        "rows": len(rows),
        "candidate_occurrences": sum(occurrence_counts.values()),
        "unique_candidates": len(unique_candidates),
        "complete_graph_candidates": complete,
        "failed_unique_candidates": len(unique_candidates) - complete,
        "failure_categories": dict(sorted(failures.items())),
        "complete_candidate_graph_sizes": {
            "branches": _distribution(branch_counts),
            "dependencies": _distribution(dependency_counts),
            "pairwise_edges": _distribution(pairwise_edge_counts),
            "branch_node_incidence_cells": _distribution(incidence_cell_counts),
        },
        "limits": (
            "Uses only candidate IDs from the supplied training split and graph IDs/definitions for presence checks; "
            "does not inspect labels, contexts, gloss text, development/test files, tokenizer IDs, or model performance. "
            "This does not establish source licensing or semantic correctness."
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
    parser.add_argument("--train", type=Path, required=True, help="prepared train.json; dev/test paths are not accepted")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="new output path")
    args = parser.parse_args()
    rows = json.loads(args.train.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("training input must be a JSON array")
    nodes, rules = _load_graph(args.bundle)
    report = summarize_train_inventory(rows, nodes, rules)
    report["input_sha256"] = {
        "train_json": hashlib.sha256(args.train.read_bytes()).hexdigest(),
        "nodes_tsv": hashlib.sha256((args.bundle / "graph/nodes.tsv").read_bytes()).hexdigest(),
        "hypergraph_rules_jsonl": hashlib.sha256(
            (args.bundle / "graph/hypergraph_rules.jsonl").read_bytes()
        ).hexdigest(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps({key: report[key] for key in (
        "rows", "candidate_occurrences", "unique_candidates", "complete_graph_candidates",
        "failed_unique_candidates", "failure_categories",
    )}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
