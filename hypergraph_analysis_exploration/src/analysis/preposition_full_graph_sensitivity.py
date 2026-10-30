"""Aggregate full-graph structural sensitivity to prep/prep_phrase deletion.

The frozen OEWN bundle is read only. Output contains aggregate counts and
hashes, not gloss text or per-target records. Structural change is not semantic
equivalence or definition fidelity.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


PROJECT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = PROJECT.parent / "OEWN"
SCOPES = {
    "prep_only": {"prep"},
    "prep_phrase_only": {"prep_phrase"},
    "prep_and_prep_phrase": {"prep", "prep_phrase"},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def signature(branch: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(set(branch)))


def summarize_scope(rules_file: Path, pos_by_id: dict[str, str], removed_pos: set[str]) -> dict[str, int]:
    heads = branches_total = source_empty_branches = occurrences_removed = 0
    source_empty_heads = affected_heads = empty_branches = heads_with_empty = 0
    collision_excess = heads_with_collision = distinct_branch_reduction = 0
    heads_with_any_change = 0
    with rules_file.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            branches = row["clauses"]
            heads += 1
            branches_total += len(branches)
            source_empty = sum(not branch for branch in branches)
            source_empty_branches += source_empty
            source_empty_heads += source_empty > 0
            before = Counter(signature(branch) for branch in branches)
            after_branches = []
            removed_for_head = 0
            for branch in branches:
                kept = []
                for dep in branch:
                    pos = pos_by_id.get(dep)
                    if pos is None:
                        raise ValueError(f"dependency missing from nodes.tsv: {dep}")
                    if pos in removed_pos:
                        removed_for_head += 1
                    else:
                        kept.append(dep)
                after_branches.append(kept)
            after = Counter(signature(branch) for branch in after_branches)
            occurrences_removed += removed_for_head
            affected_heads += removed_for_head > 0
            heads_with_any_change += before != after
            empty_count = sum(bool(original) and not transformed
                              for original, transformed in zip(branches, after_branches))
            empty_branches += empty_count
            heads_with_empty += empty_count > 0
            nonempty_after = Counter({key: count for key, count in after.items() if key})
            excess = sum(count - 1 for count in nonempty_after.values() if count > 1)
            collision_excess += excess
            heads_with_collision += excess > 0
            distinct_before = len({key for key in before if key})
            distinct_after = len(nonempty_after)
            distinct_branch_reduction += distinct_before - distinct_after
    return {
        "targets": heads,
        "source_branches": branches_total,
        "source_empty_branches": source_empty_branches,
        "targets_with_source_empty_branches": source_empty_heads,
        "targets_with_removed_occurrences": affected_heads,
        "removed_occurrences": occurrences_removed,
        "targets_with_any_branch_multiset_change": heads_with_any_change,
        "new_empty_branches": empty_branches,
        "targets_with_new_empty_branches": heads_with_empty,
        "nonempty_collision_excess": collision_excess,
        "targets_with_nonempty_collisions": heads_with_collision,
        "reduction_in_distinct_nonempty_branch_signatures": distinct_branch_reduction,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    nodes_file = args.bundle / "graph/nodes.tsv"
    rules_file = args.bundle / "graph/hypergraph_rules.jsonl"
    with nodes_file.open(encoding="utf-8-sig", newline="") as stream:
        pos_by_id = {row["synset_id"]: row["pos"] for row in csv.DictReader(stream, delimiter="\t")}
    if not pos_by_id:
        raise ValueError("nodes.tsv produced an empty node table")
    results = {name: summarize_scope(rules_file, pos_by_id, pos)
               for name, pos in SCOPES.items()}
    output = {
        "analysis": "read-only full-graph structural sensitivity; not semantic evaluation",
        "input_sha256": {"nodes.tsv": sha256(nodes_file), "hypergraph_rules.jsonl": sha256(rules_file)},
        "pos_scopes": {name: sorted(pos) for name, pos in SCOPES.items()},
        "results": results,
        "limits": [
            "No semantic labels or definition-fidelity judgments are used.",
            "A branch signature is a sorted set of dependency IDs; order and duplicate occurrences do not affect collision counts.",
            "Structural collision or an empty branch does not establish semantic equivalence or truth.",
            "The three scope variants are descriptive interventions on one frozen graph, not randomized causal estimates.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
