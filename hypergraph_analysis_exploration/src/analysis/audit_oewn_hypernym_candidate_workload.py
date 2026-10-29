"""Summarize candidate and annotation workload scenarios for a pinned OEWN edge set.

This reports arithmetic consequences of alternative surface policies. It does
not choose a protocol, select a sample, render hypotheses, or estimate power.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.analysis.build_oewn_hypernym_candidate_inventory import (
    PROJECT_ROOT,
    build_inventory,
)


OUTPUT_DIR = PROJECT_ROOT / "outputs" / "phase188"
DEFAULT_REPORT = OUTPUT_DIR / "oewn_hypernym_candidate_workload_audit.json"
AUDIT_VERSION = "oewn-hypernym-candidate-workload-audit/1"
DESIGN_CONDITIONS = 2
DESIGN_ANNOTATORS_PER_NLI_PAIR = 2


def summarize(inventory: dict[str, Any]) -> dict[str, Any]:
    """Calculate workload bounds without copying candidate IDs or lemma text."""
    rows = inventory.get("candidates")
    if not isinstance(rows, list) or not rows:
        raise ValueError("candidate inventory must contain a non-empty candidates array")

    by_pos: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "edge_count": 0,
        "active_child_sense_ids": set(),
        "unique_parent_sense_ids": set(),
        "parent_surface_rows": 0,
        "child_surface_memberships_per_edge": 0,
        "child_by_parent_surface_combinations": 0,
    })
    edges_per_child: Counter[tuple[str, str]] = Counter()
    parent_surfaces_per_edge: Counter[int] = Counter()

    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("candidate rows must be objects")
        pos = row.get("child_release_pos")
        child_id = row.get("child_sense_id")
        parent_id = row.get("parent_sense_id")
        child_surfaces = row.get("child_release_lemma_surfaces")
        parent_surfaces = row.get("parent_release_lemma_surfaces")
        if (not isinstance(pos, str) or not isinstance(child_id, str)
                or not isinstance(parent_id, str) or not isinstance(child_surfaces, list)
                or not child_surfaces or not isinstance(parent_surfaces, list) or not parent_surfaces):
            raise ValueError("candidate row lacks release POS, sense IDs, or lemma surfaces")
        item = by_pos[pos]
        item["edge_count"] += 1
        item["active_child_sense_ids"].add(child_id)
        item["unique_parent_sense_ids"].add(parent_id)
        item["parent_surface_rows"] += len(parent_surfaces)
        item["child_surface_memberships_per_edge"] += len(child_surfaces)
        item["child_by_parent_surface_combinations"] += len(child_surfaces) * len(parent_surfaces)
        edges_per_child[(pos, child_id)] += 1
        parent_surfaces_per_edge[len(parent_surfaces)] += 1

    pos_summary = {}
    for pos, values in sorted(by_pos.items()):
        edge_count = values["edge_count"]
        parent_rows = values["parent_surface_rows"]
        cross_product_pairs = values["child_by_parent_surface_combinations"]
        pos_summary[pos] = {
            "edge_count": edge_count,
            "active_child_sense_count": len(values["active_child_sense_ids"]),
            "unique_parent_sense_count": len(values["unique_parent_sense_ids"]),
            "parent_surface_rows": parent_rows,
            "child_surface_memberships_per_edge": values["child_surface_memberships_per_edge"],
            "child_parent_surface_pair_rows_if_all_child_surfaces": cross_product_pairs,
            "two_condition_nli_rows_if_one_child_surface_per_edge": parent_rows * DESIGN_CONDITIONS,
            "two_condition_nli_judgments_if_two_annotators_one_child_surface": (
                parent_rows * DESIGN_CONDITIONS * DESIGN_ANNOTATORS_PER_NLI_PAIR
            ),
            "two_condition_nli_rows_if_all_child_surfaces": cross_product_pairs * DESIGN_CONDITIONS,
            "two_condition_nli_judgments_if_two_annotators_all_child_surfaces": (
                cross_product_pairs * DESIGN_CONDITIONS * DESIGN_ANNOTATORS_PER_NLI_PAIR
            ),
        }

    child_edge_multiplicity = Counter(count for (_, _), count in edges_per_child.items())
    return {
        "audit_version": AUDIT_VERSION,
        "status": "descriptive_workload_scenarios_not_protocol_or_power_analysis",
        "inventory_sha256": inventory.get("inventory_sha256"),
        "release": inventory.get("release"),
        "assumptions_from_unconfirmed_design_memo": {
            "nli_premise_conditions": DESIGN_CONDITIONS,
            "independent_annotators_per_exact_nli_pair": DESIGN_ANNOTATORS_PER_NLI_PAIR,
            "surface_scenarios": [
                "one unspecified child lemma surface per relation edge, crossed with every parent lemma surface",
                "all child lemma surfaces crossed with every parent lemma surface",
            ],
            "protocol_confirmed": False,
            "sample_size_or_power_inferred": False,
        },
        "counts": {
            "target_senses": inventory["counts"]["target_senses"],
            "direct_hypernym_edges": len(rows),
            "active_child_senses": len(edges_per_child),
            "children_with_one_direct_hypernym_edge": child_edge_multiplicity.get(1, 0),
            "children_with_two_direct_hypernym_edges": child_edge_multiplicity.get(2, 0),
            "parent_surface_count_per_edge_histogram": {
                str(k): v for k, v in sorted(parent_surfaces_per_edge.items())
            },
            "all_parent_surface_rows": sum(item["parent_surface_rows"] for item in by_pos.values()),
            "all_child_parent_surface_pair_rows": sum(
                item["child_by_parent_surface_combinations"] for item in by_pos.values()
            ),
            "source_support_edge_units_if_one_judgment_per_edge": len(rows),
            "source_support_judgments_if_two_annotators_per_edge": len(rows) * 2,
        },
        "by_child_release_pos": pos_summary,
        "interpretation_limits": [
            "All figures describe the locked 400-target candidate set, not the full OEWN release or a probability sample from it.",
            "NLI row counts assume two premise conditions proposed in the design memo; these conditions are not approved or rendered.",
            "The child×parent surface cross-product is a workload scenario, not a recommendation or a claim that every pair is linguistically valid.",
            "Repeated edges, surfaces, target senses, and groups are dependent; counts do not establish statistical power, calibration validity, or effective sample size.",
            "No gloss, synset ID, lemma string, hypothesis, annotation task, split, or label is emitted by this aggregate audit.",
        ],
        "research_state": inventory["research_state"],
    }


def _write_report(report: dict[str, Any], output: Path, force: bool) -> str:
    resolved = output.resolve()
    if not resolved.is_relative_to(OUTPUT_DIR.resolve()):
        raise ValueError("output must be inside outputs/phase188")
    if output.exists() and not force:
        raise FileExistsError(f"output already exists; pass --force to replace it: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    output.write_text(payload, encoding="utf-8", newline="\n")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error(f"output already exists; pass --force to replace it: {args.output}")
    try:
        inventory = build_inventory()
        inventory_bytes = json.dumps(inventory, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        inventory["inventory_sha256"] = hashlib.sha256(inventory_bytes.encode("utf-8")).hexdigest()
        report = summarize(inventory)
        report["builder_code_sha256"] = hashlib.sha256(
            Path(__file__).with_name("build_oewn_hypernym_candidate_inventory.py").read_bytes()
        ).hexdigest()
        report_sha256 = _write_report(report, args.output, args.force)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "audit_version": report["audit_version"],
        "counts": report["counts"],
        "by_child_release_pos": report["by_child_release_pos"],
        "output": str(args.output),
        "output_sha256": report_sha256,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
