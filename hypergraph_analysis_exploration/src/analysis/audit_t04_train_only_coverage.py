"""Audit train-only candidate, graph, gold-map, and serialized-budget coverage.

The report contains aggregate counts and hashes only. It reads the supplied
train JSON and its metadata plus OEWN nodes/rules; it never opens dev/test or
prints sample IDs, contexts, glosses, or candidate IDs.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.profile_t04_xpu_text_structure import read_graph, read_train_candidate_ids
from src.analysis.tiny_bert_wsd_train import digest, validate


def _distribution(values: list[int]) -> dict[str, int | float]:
    ordered = sorted(values)
    if not ordered:
        return {"count": 0}
    return {
        "count": len(ordered),
        "min": ordered[0],
        "median": ordered[len(ordered) // 2],
        "p90": ordered[int(0.9 * (len(ordered) - 1))],
        "max": ordered[-1],
    }


def audit(train_path: Path, metadata_path: Path, nodes_path: Path, rules_path: Path) -> dict[str, Any]:
    rows = json.loads(train_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    width = metadata["joint_budget"]
    validate(rows, width)
    candidate_ids, candidate_occurrences = read_train_candidate_ids(train_path)
    definitions, rules = read_graph(nodes_path, rules_path, set(candidate_ids))

    candidate_status = Counter()
    input_mismatches = Counter()
    context_lengths: list[int] = []
    candidate_lengths: list[int] = []
    padding_lengths: list[int] = []
    target_marker_pairs = Counter()
    scorable_count = 0
    unscorable_count = 0
    for row in rows:
        manifest_ids = [item["candidate_id"] for item in row["candidates"]]
        if manifest_ids != row["candidate_ids"]:
            raise ValueError("manifest and candidate order differ")
        candidate_status.update(item["status"] for item in row["candidates"])
        ready_ids = [item["candidate_id"] for item in row["candidates"] if item["status"] == "ready"]
        if ready_ids != row["scorable_candidate_ids"]:
            raise ValueError("ready candidates differ from scorable candidates")
        if row["label"] >= 0:
            scorable_count += 1
        else:
            unscorable_count += 1

        for condition in "BCD":
            if row["inputs"][condition] != row["inputs"]["A"]:
                input_mismatches[condition] += 1

        for sequence in row["inputs"]["A"]:
            if len(sequence) != width or sequence[0] != 101:
                raise ValueError("unexpected joint input shape or CLS token")
            try:
                first_sep = sequence.index(102, 1)
                second_sep = sequence.index(102, first_sep + 1)
            except ValueError as exc:
                raise ValueError("joint sequence is missing its separators") from exc
            if any(token != 0 for token in sequence[second_sep + 1:]):
                raise ValueError("non-padding token follows candidate separator")
            context_lengths.append(first_sep - 1)
            candidate_lengths.append(second_sep - first_sep - 1)
            padding_lengths.append(width - second_sep - 1)

        marker_ids = metadata["target_marker_ids"]
        if row["inputs"]["A"]:
            seq = row["inputs"]["A"][0]
            sep = seq.index(102, 1)
            target_marker_pairs[(seq[:sep].count(marker_ids["start"]),
                                 seq[:sep].count(marker_ids["end"]))] += 1

    if candidate_status["failed"]:
        raise ValueError("one or more candidate encodings failed")
    train_counts = metadata["counts"]["train"]
    if unscorable_count != train_counts.get("gold_not_encodable"):
        raise ValueError("serialized unscorable count differs from metadata")

    unique_graph_nodes = set(definitions)
    for branches in rules.values():
        for branch in branches:
            unique_graph_nodes.update(branch)
    return {
        "schema": "t04-train-only-coverage-audit/1",
        "train_rows": len(rows),
        "scorable_gold_rows": scorable_count,
        "unscorable_gold_rows": unscorable_count,
        "unscorable_gold_mapping_issue_counts": {
            key: train_counts.get(key, 0)
            for key in ("gold_invalid_gold", "gold_no_exact_key", "gold_target_absent_from_graph")
        },
        "candidate_occurrences": candidate_occurrences,
        "unique_candidates": len(candidate_ids),
        "candidate_status_counts": dict(candidate_status),
        "candidate_encoding_failures": candidate_status["failed"],
        "graph_candidate_coverage": len(rules),
        "unique_graph_node_count": len(unique_graph_nodes),
        "legacy_serialized_A_B_C_D_input_mismatch_rows": dict(input_mismatches),
        "joint_budget_tokens": width,
        "A_input_context_piece_distribution": _distribution(context_lengths),
        "A_candidate_piece_distribution": _distribution(candidate_lengths),
        "A_padding_piece_distribution": _distribution(padding_lengths),
        "target_marker_pair_counts": {str(key): count for key, count in target_marker_pairs.items()},
        "truncated_sentence_windows": train_counts.get("sentence_window_truncated", 0),
        "inputs_sha256": {
            "train_json": digest(train_path),
            "metadata_json": digest(metadata_path),
            "nodes_tsv": digest(nodes_path),
            "rules_jsonl": digest(rules_path),
        },
        "limits": "Train split only. Mapping failures are not candidate encoder failures. Aggregate counts only; no dev/test read.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.train, args.metadata, args.nodes, args.rules)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
