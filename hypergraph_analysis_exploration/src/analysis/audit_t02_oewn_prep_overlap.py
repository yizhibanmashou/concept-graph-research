"""Audit prep-ablation overlap with a release-verified OEWN annotation frame.

The report contains aggregate counts and hashes only. It never emits target
IDs, lemmas, definitions, annotation text, or labels.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

PINNED_RELEASE = "Open English WordNet 2025 Plus"
PINNED_ARCHIVE_SHA256 = "8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"JSONL row {line_number} is not an object")
            rows.append(value)
    return rows


def _condition_summary(
    targets: set[str],
    rules: dict[str, list[list[str]]],
    pos: dict[str, str],
    removed_pos: set[str],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for target in targets:
        branches = rules.get(target)
        if branches is None:
            counts["targets_missing_rules"] += 1
            continue
        counts["targets"] += 1
        reduced: list[frozenset[str]] = []
        for branch in branches:
            removed = [node for node in branch if pos.get(node) in removed_pos]
            kept = frozenset(node for node in branch if pos.get(node) not in removed_pos)
            counts["source_branches"] += 1
            counts["removed_occurrences"] += len(removed)
            counts["changed_branches"] += bool(removed)
            counts["new_empty_branches"] += not kept
            reduced.append(kept)
        counts["changed_targets"] += any(
            any(pos.get(node) in removed_pos for node in branch)
            for branch in branches
        )
        nonempty = [branch for branch in reduced if branch]
        counts["targets_with_new_empty_branch"] += any(not branch for branch in reduced)
        counts["targets_with_nonempty_collision"] += len(nonempty) > len(set(nonempty))
        counts["targets_with_multiple_new_empty_branches"] += sum(not branch for branch in reduced) > 1
    return dict(counts)


def run(frame_path: Path, crosscheck_path: Path, bundle: Path) -> dict[str, Any]:
    crosscheck = json.loads(crosscheck_path.read_text(encoding="utf-8"))
    if crosscheck.get("release_name") != PINNED_RELEASE:
        raise ValueError("release cross-check is not for the pinned OEWN release")
    if crosscheck.get("release_archive_sha256") != PINNED_ARCHIVE_SHA256:
        raise ValueError("release archive hash differs from the pinned OEWN release")
    if crosscheck.get("frame_sha256") != sha256(frame_path):
        raise ValueError("release cross-check does not bind this frame")
    if crosscheck.get("raw_gloss_text_emitted") is not False:
        raise ValueError("cross-check must not emit raw gloss text")
    per_sense = crosscheck.get("per_sense")
    if not isinstance(per_sense, list):
        raise ValueError("cross-check lacks per-sense evidence")
    exact_ids = {
        row.get("sense_id")
        for row in per_sense
        if isinstance(row, dict) and row.get("raw_gloss_exact_match") is True
    }
    frame_rows = _read_jsonl(frame_path)
    target_ids = [row.get("sense_id") for row in frame_rows]
    if any(not isinstance(target, str) or not target for target in target_ids):
        raise ValueError("frame contains an invalid target identifier")
    if len(set(target_ids)) != len(target_ids):
        raise ValueError("frame contains duplicate targets")
    if set(target_ids) != exact_ids:
        raise ValueError("frame targets do not exactly match release-verified IDs")

    node_path = bundle / "graph" / "nodes.tsv"
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    with node_path.open(encoding="utf-8-sig", newline="") as stream:
        pos = {row["synset_id"]: row["pos"] for row in csv.DictReader(stream, delimiter="\t")}
    rules = {}
    for row in _read_jsonl(rules_path):
        target = row.get("head")
        branches = row.get("clauses")
        if isinstance(target, str) and isinstance(branches, list):
            rules[target] = branches

    targets = set(target_ids)
    panel_targets: dict[str, set[str]] = {}
    for row in frame_rows:
        panel = row.get("panel")
        if not isinstance(panel, str) or not panel:
            raise ValueError("frame contains an invalid panel label")
        panel_targets.setdefault(panel, set()).add(row["sense_id"])
    return {
        "schema_version": "t02-oewn-prep-overlap-audit/1",
        "frame_sha256": sha256(frame_path),
        "crosscheck_sha256": sha256(crosscheck_path),
        "release_name": PINNED_RELEASE,
        "release_archive_sha256": PINNED_ARCHIVE_SHA256,
        "bundle_graph_sha256": {
            "nodes.tsv": sha256(node_path),
            "hypergraph_rules.jsonl": sha256(rules_path),
        },
        "frame_targets": len(targets),
        "release_exact_raw_gloss_targets": len(exact_ids),
        "targets_by_panel": {
            panel: len(panel_items) for panel, panel_items in sorted(panel_targets.items())
        },
        "prep_primary": _condition_summary(targets, rules, pos, {"prep"}),
        "prep_phrase_sensitivity": _condition_summary(targets, rules, pos, {"prep", "prep_phrase"}),
        "prep_primary_by_panel": {
            panel: _condition_summary(panel_items, rules, pos, {"prep"})
            for panel, panel_items in sorted(panel_targets.items())
        },
        "prep_phrase_sensitivity_by_panel": {
            panel: _condition_summary(panel_items, rules, pos, {"prep", "prep_phrase"})
            for panel, panel_items in sorted(panel_targets.items())
        },
        "limits": (
            "Metadata-only aggregate feasibility audit. It does not read or emit glosses, labels, "
            "or annotation returns; it does not estimate population fidelity, authorize batch "
            "distribution, or establish semantic effects. The frame is an existing pilot frame, "
            "not a newly approved T02 sample."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=Path, required=True)
    parser.add_argument("--crosscheck", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.frame, args.crosscheck, args.bundle)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({
        "frame_targets": result["frame_targets"],
        "targets_by_panel": result["targets_by_panel"],
        "prep_primary": result["prep_primary"],
        "prep_phrase_sensitivity": result["prep_phrase_sensitivity"],
        "prep_primary_by_panel": result["prep_primary_by_panel"],
        "prep_phrase_sensitivity_by_panel": result["prep_phrase_sensitivity_by_panel"],
        "out": str(args.out),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
