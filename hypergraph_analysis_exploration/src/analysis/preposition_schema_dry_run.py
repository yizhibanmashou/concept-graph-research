"""Run the text-free T02 relation schema on the existing 40-item pilot.

This is a pipeline/structure dry run only. It emits aggregate counts and never
creates semantic labels or copies gloss text into its output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.preposition_relation_records import transform_record


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_source_record(item: dict[str, Any], source_hashes: dict[str, str],
                        sample_sha256: str) -> dict[str, Any]:
    branches = []
    occurrences = []
    for branch_index, branch in enumerate(item["branches"]):
        branch_id = f"b{branch_index:03d}"
        refs = []
        for position, node in enumerate(branch["original"]):
            occurrence_id = f"{branch_id}:o{position:03d}"
            refs.append(occurrence_id)
            occurrences.append({
                "occurrence_id": occurrence_id,
                "branch_id": branch_id,
                "branch_position": position,
                "node_id": node["synset_id"],
                "pos": node["pos"],
                "source_locator": {
                    "target_id": item["head"],
                    "branch_index": branch_index,
                    "premise_index": position,
                },
            })
        branches.append({"branch_id": branch_id, "premise_occurrence_ids": refs})

    target_digest = sha256_bytes(item["head"].encode("utf-8"))
    structural_input = [
        [(node["synset_id"], node["pos"]) for node in branch["original"]]
        for branch in item["branches"]
    ]
    input_digest = sha256_bytes(json.dumps(
        structural_input, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8"))
    return {
        "schema_version": "t02-relation-v0",
        "item_id": target_digest[:20],
        "target_id": item["head"],
        "source_version": {
            "nodes_sha256": source_hashes["nodes.tsv"],
            "rules_sha256": source_hashes["hypergraph_rules.jsonl"],
            "input_sha256": input_digest,
        },
        "source_branches": branches,
        "occurrences": occurrences,
        "transform_version": "preposition_relation_records.py",
        "pilot_sample_sha256": sample_sha256,
    }


def summarize(sample: dict[str, Any]) -> dict[str, Any]:
    if sample.get("sample_size") != len(sample.get("items", [])):
        raise ValueError("pilot sample_size does not match its items")
    source_hashes = sample["inputs_sha256"]
    expected = {"nodes.tsv", "hypergraph_rules.jsonl"}
    if not expected.issubset(source_hashes):
        raise ValueError("pilot input hash manifest is incomplete")
    sample_sha = sha256_bytes(json.dumps(
        sample, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8"))

    totals: Counter[str] = Counter()
    empty_by_condition: Counter[str] = Counter()
    pos_counts: Counter[str] = Counter()
    collision_excess = 0
    for item in sample["items"]:
        record = build_source_record(item, source_hashes, sample_sha)
        transformed = transform_record(record, relations=[])
        totals["targets"] += 1
        totals["source_branches"] += len(record["source_branches"])
        totals["prep_occurrences"] += sum(row["pos"] == "prep" for row in record["occurrences"])
        for occurrence in record["occurrences"]:
            pos_counts[occurrence["pos"]] += 1
        for condition, result in transformed["conditions"].items():
            empty_by_condition[condition] += sum(
                branch["empty_after_transform"] for branch in result["branches"]
            )

        deleted = transformed["conditions"]["prep_delete"]["branches"]
        by_signature: Counter[tuple[str, ...]] = Counter()
        for branch in deleted:
            if branch["premise_occurrence_ids"]:
                node_ids = tuple(sorted({
                    next(row["node_id"] for row in record["occurrences"]
                         if row["occurrence_id"] == occurrence_id)
                    for occurrence_id in branch["premise_occurrence_ids"]
                }))
                by_signature[node_ids] += 1
        collision_excess += sum(count - 1 for count in by_signature.values())
        totals["boundary_records"] += sum(
            len(branch["boundaries"])
            for branch in transformed["conditions"]["boundary_preserve"]["branches"]
        )
        totals["unresolved_typed_relations"] += sum(
            len(branch["relations"])
            for branch in transformed["conditions"]["typed_relation"]["branches"]
        )

    return {
        "scope": "prep only; 40-item exploratory pilot; no semantic review",
        "sample_size": sample["sample_size"],
        "inputs_sha256": source_hashes,
        "sample_sha256": sample_sha,
        "counts": dict(totals),
        "pos_occurrences": dict(sorted(pos_counts.items())),
        "empty_branches_by_condition": dict(sorted(empty_by_condition.items())),
        "nonempty_collision_excess_after_prep_deletion": collision_excess,
        "supported_semantic_relations_created": 0,
        "interpretation": (
            "Schema/transform pipeline check only. Uncurated prep relations remain unresolved; "
            "these pilot counts are not a population estimate or definition-fidelity result."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, required=True,
                        help="local preposition_paired_review JSON pilot")
    args = parser.parse_args()
    sample = json.loads(args.sample.read_text(encoding="utf-8"))
    print(json.dumps(summarize(sample), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
