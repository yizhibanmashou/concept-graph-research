"""Measure the existing lexical genus heuristic on the locked target-sense slice.

This is an exploratory resource-alignment diagnostic, not semantic-support gold,
an annotation export, or a Track A protocol decision. It emits aggregates only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.analysis.build_oewn_hypernym_candidate_inventory import (
    DEFAULT_LOCK,
    DEFAULT_OUTPUT as DEFAULT_INVENTORY,
    build_inventory,
)
from src.analysis.gloss_genus_baseline import (
    DEFAULT_RELEASE_ARCHIVE,
    DEFAULT_RELEASE_DIR,
    _sha256,
    build_noun_lemma_index,
    find_first_noun_candidate,
)
from src.analysis.gloss_genus_release_baseline import load_noun_synsets


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase245" / "track_a_genus_resource_diagnostic.json"
REPORT_VERSION = "track-a-genus-resource-diagnostic/1"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            rows.append(row)
    return rows


def audit_genus_baseline(
    inventory_path: Path = DEFAULT_INVENTORY,
    lock_path: Path = DEFAULT_LOCK,
    release_dir: Path = DEFAULT_RELEASE_DIR,
    release_archive: Path = DEFAULT_RELEASE_ARCHIVE,
) -> dict[str, Any]:
    inventory_bytes = inventory_path.read_bytes()
    inventory = json.loads(inventory_bytes.decode("utf-8"))
    if not isinstance(inventory, dict) or inventory.get("schema_version") != "oewn-hypernym-candidate-inventory/0.1":
        raise ValueError("candidate inventory has an unsupported schema")

    rebuilt = build_inventory(lock_path, release_dir, release_archive)
    if inventory != rebuilt:
        raise ValueError("saved candidate inventory differs from the current locked frame/release rebuild")

    inputs = inventory.get("inputs")
    if not isinstance(inputs, dict):
        raise ValueError("candidate inventory is missing input identities")
    frame_path = (PROJECT_ROOT / inputs["frame_path"]).resolve()
    if _sha256(lock_path) != inputs.get("lock_sha256"):
        raise ValueError("candidate inventory lock hash does not match the current lock")
    if _sha256(frame_path) != inputs.get("frame_sha256"):
        raise ValueError("candidate inventory frame hash does not match the current frame")
    archive_sha256 = _sha256(release_archive)
    if archive_sha256 != inventory.get("release", {}).get("archive_sha256"):
        raise ValueError("candidate inventory release archive hash does not match the current archive")

    frame_rows = _load_jsonl(frame_path)
    target_ids: set[str] = set()
    noun_target_ids: set[str] = set()
    for row in frame_rows:
        sense_id = row.get("sense_id")
        if not isinstance(sense_id, str) or not sense_id:
            raise ValueError("locked frame contains an invalid sense_id")
        target_id = sense_id.removeprefix("oewn-")
        target_ids.add(target_id)
        if row.get("pos") == "n":
            noun_target_ids.add(target_id)
        elif row.get("pos") not in {"a", "s", "r", "v"}:
            raise ValueError("locked frame contains an unsupported part of speech")
    if (len(target_ids) != len(frame_rows)
            or len(target_ids) != inputs.get("candidate_sense_count")
            or len(noun_target_ids) == 0):
        raise ValueError("locked frame identities are duplicated or differ from the inventory")

    edges = inventory.get("candidates")
    if not isinstance(edges, list):
        raise ValueError("candidate inventory is missing its edge list")
    parents_by_child: dict[str, set[str]] = defaultdict(set)
    seen_edges: set[tuple[str, str]] = set()
    for row in edges:
        if not isinstance(row, dict) or row.get("relation") != "hypernym":
            raise ValueError("candidate inventory has a malformed ordinary-hypernym row")
        child = row.get("child_sense_id")
        parent = row.get("parent_sense_id")
        if (not isinstance(child, str) or not isinstance(parent, str)
                or row.get("child_release_pos") != "n" or row.get("parent_release_pos") != "n"):
            continue
        pair = (child.removeprefix("oewn-"), parent.removeprefix("oewn-"))
        if pair in seen_edges:
            raise ValueError("candidate inventory contains a duplicate noun-hypernym edge")
        seen_edges.add(pair)
        parents_by_child[pair[0]].add(pair[1])

    noun_records = load_noun_synsets(release_dir)
    noun_by_id = {record["synset_id"]: record for record in noun_records}
    noun_targets = noun_target_ids & noun_by_id.keys()
    missing_noun_target_ids = noun_target_ids - noun_by_id.keys()
    if missing_noun_target_ids:
        raise ValueError("locked noun targets are missing from the pinned release noun inventory")
    noun_index = build_noun_lemma_index(release_dir)

    gloss_instances = 0
    candidate_covered_instances = 0
    predicted_sense_pairs = 0
    correct_resource_pairs = 0
    resource_pair_denominator = 0
    senses_with_direct_parent = 0
    senses_with_any_candidate = 0
    senses_with_any_parent_match = 0
    senses_with_exact_parent_set = 0
    senses_with_no_direct_parent = 0

    for child_id in sorted(noun_targets):
        record = noun_by_id[child_id]
        gold_parents = parents_by_child.get(child_id, set())
        if gold_parents:
            senses_with_direct_parent += 1
        else:
            senses_with_no_direct_parent += 1
        predicted_union: set[str] = set()
        any_candidate = False
        any_match = False
        for gloss in record["definitions"]:
            gloss_instances += 1
            resource_pair_denominator += len(gold_parents)
            candidate = find_first_noun_candidate(gloss, record["members"], noun_index)
            if candidate is None:
                continue
            any_candidate = True
            candidate_ids = set(candidate["candidate_synset_ids"])
            predicted_union.update(candidate_ids)
            candidate_covered_instances += 1
            predicted_sense_pairs += len(candidate_ids)
            correct = candidate_ids & gold_parents
            correct_resource_pairs += len(correct)
            any_match = any_match or bool(correct)

        senses_with_any_candidate += int(any_candidate)
        senses_with_any_parent_match += int(any_match)
        senses_with_exact_parent_set += int(predicted_union == gold_parents)

    precision = correct_resource_pairs / predicted_sense_pairs if predicted_sense_pairs else None
    recall = correct_resource_pairs / resource_pair_denominator if resource_pair_denominator else None
    f1 = (2 * precision * recall / (precision + recall)
          if precision is not None and recall is not None and precision + recall else None)
    return {
        "report_version": REPORT_VERSION,
        "claim_type": "locked_target_lexical_genus_vs_same_release_hypernym_alignment_not_semantic_validation",
        "method": {
            "baseline_version": "first-exact-noun-lemma/1",
            "candidate_rule": "first exact noun lemma match among the first 12 gloss tokens, matching 1-4 token spans and excluding all target member lemmas",
            "candidate_senses": "all OEWN noun synsets associated with the selected lemma",
            "resource_reference": "ordinary direct hypernym edges from the same pinned OEWN 2025 Plus release; instance_hypernym excluded",
            "unit": "each release noun definition string; multiple definitions within one target sense are nested, not independent observations",
        },
        "inputs": {
            "candidate_inventory_path": inventory_path.resolve().relative_to(PROJECT_ROOT).as_posix(),
            "candidate_inventory_sha256": hashlib.sha256(inventory_bytes).hexdigest(),
            "lock_path": lock_path.resolve().relative_to(PROJECT_ROOT).as_posix(),
            "lock_sha256": _sha256(lock_path),
            "frame_path": frame_path.relative_to(PROJECT_ROOT).as_posix(),
            "frame_sha256": _sha256(frame_path),
            "release_archive_sha256": archive_sha256,
        },
        "counts": {
            "locked_target_senses": len(target_ids),
            "locked_noun_target_senses": len(noun_target_ids),
            "locked_non_noun_target_senses": len(target_ids - noun_target_ids),
            "locked_noun_targets_present_in_release_noun_inventory": len(noun_targets),
            "locked_noun_targets_not_in_release_noun_inventory": len(missing_noun_target_ids),
            "noun_target_senses_with_direct_hypernym": senses_with_direct_parent,
            "noun_target_senses_without_direct_hypernym": senses_with_no_direct_parent,
            "ordinary_noun_hypernym_edges": len(seen_edges),
            "noun_definition_instances": gloss_instances,
            "definition_instances_with_a_lexical_candidate": candidate_covered_instances,
            "candidate_coverage": candidate_covered_instances / gloss_instances if gloss_instances else None,
            "predicted_child_parent_sense_pairs": predicted_sense_pairs,
            "resource_positive_pairs": correct_resource_pairs,
            "resource_pair_precision": precision,
            "resource_pair_recall": recall,
            "resource_pair_f1": f1,
            "noun_target_senses_with_any_lexical_candidate": senses_with_any_candidate,
            "noun_target_senses_with_any_parent_match": senses_with_any_parent_match,
            "noun_target_senses_with_exact_parent_set_recovered": senses_with_exact_parent_set,
            "resource_positive_pair_denominator_over_definition_instances": resource_pair_denominator,
        },
        "privacy_and_interpretation": {
            "raw_gloss_text_emitted": False,
            "sense_ids_or_lemma_surfaces_emitted": False,
            "annotation_pairs_or_labels_generated": False,
            "splits_or_estimands_assigned": False,
            "semantic_support_gold_available": False,
            "limitations": [
                "Matching a release's direct hypernym edge measures resource alignment only; it does not establish that a gloss span supports the proposed parent relation.",
                "The candidate lemma and target synsets come from the same OEWN release, so this is not independent semantic validation.",
                "The first-exact-lemma heuristic can overgenerate senses and miss paraphrased or multi-clause genera.",
                "This noun-slice diagnostic does not freeze or approve Track A's candidate surface policy, estimand, split, annotation protocol, or NLI conditions.",
            ],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT_ROOT):
        parser.error("output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error(f"output exists; pass --force to replace it: {output}")
    try:
        report = audit_genus_baseline(args.inventory, args.lock, args.release_dir, args.release_archive)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], ensure_ascii=False, sort_keys=True, indent=2))
    print(f"Wrote aggregate-only diagnostic: {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
