"""Quantify parent-lemma lexicalization choices for a future Track A frame.

The report contains counts and opaque sense IDs only; it creates no candidate
pairs, hypotheses, labels, splits, or distribution-ready annotation material.
"""
from __future__ import annotations

import argparse
import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.audit_annotation_frame_release_identity import (
    _normalize_lemma,
    _read_json,
    _read_jsonl,
    _sha256_file,
    audit as audit_release_identity,
)
from src.analysis.gloss_genus_baseline import DEFAULT_RELEASE_ARCHIVE, DEFAULT_RELEASE_DIR
from src.analysis.oewn_hypernym_verifier import _pos_family
from src.analysis.project_paths import PROJECT_ROOT


DEFAULT_FRAME = PROJECT_ROOT / "outputs" / "phase7" / "annotation_candidate_frame_v3_400.jsonl"
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase145" / "track_a_hypothesis_surface_policy_audit.json"
TAXONOMY_PREFIXES = ("noun.", "verb.", "adj.", "adv.")


def audit(
    frame_path: Path = DEFAULT_FRAME,
    release_dir: Path = DEFAULT_RELEASE_DIR,
    release_archive: Path = DEFAULT_RELEASE_ARCHIVE,
) -> dict[str, Any]:
    identity = audit_release_identity(release_dir=release_dir, release_archive=release_archive)
    frame = _read_jsonl(frame_path)
    target_ids = {
        row["sense_id"].removeprefix("oewn-")
        for row in frame
        if isinstance(row.get("sense_id"), str) and row["sense_id"].startswith("oewn-")
    }
    if len(target_ids) != len(frame):
        raise ValueError("frame contains invalid or duplicate target sense IDs")

    taxonomy: dict[str, dict[str, Any]] = {}
    for path in sorted(release_dir.iterdir()):
        if (not path.is_file() or not path.name.endswith(".json")
                or not path.name.startswith(TAXONOMY_PREFIXES)):
            continue
        records = _read_json(path)
        for sense_id in target_ids & records.keys():
            if sense_id in taxonomy:
                raise ValueError(f"target sense occurs in multiple taxonomy files: {sense_id}")
            taxonomy[sense_id] = records[sense_id]
    if set(taxonomy) != target_ids:
        raise ValueError("frame target sense IDs do not match the pinned release")

    edges = [
        (child, parent)
        for child, record in taxonomy.items()
        for parent in record.get("hypernym", [])
        if isinstance(parent, str)
    ]
    if len(edges) != len(set(edges)):
        raise ValueError("release contains duplicate direct hypernym edges for a target")
    parent_ids = {parent for _, parent in edges}
    parent_taxonomy: dict[str, dict[str, Any]] = {}
    for path in sorted(release_dir.iterdir()):
        if (not path.is_file() or not path.name.endswith(".json")
                or not path.name.startswith(TAXONOMY_PREFIXES)):
            continue
        records = _read_json(path)
        for sense_id in parent_ids & records.keys():
            if sense_id in parent_taxonomy:
                raise ValueError(f"parent sense occurs in multiple taxonomy files: {sense_id}")
            parent_taxonomy[sense_id] = records[sense_id]
    if set(parent_taxonomy) != parent_ids:
        raise ValueError("one or more direct parent senses are missing from the pinned release")
    relevant_ids = target_ids | parent_ids
    lemmas = {sense_id: set() for sense_id in relevant_ids}
    for path in sorted(release_dir.glob("entries-*.json")):
        entries = _read_json(path)
        if not isinstance(entries, dict):
            raise ValueError(f"expected object in {path.name}")
        for lemma, pos_map in entries.items():
            if not isinstance(lemma, str) or not isinstance(pos_map, dict):
                continue
            normalized = _normalize_lemma(lemma)
            for entry in pos_map.values():
                senses = entry.get("sense", []) if isinstance(entry, dict) else []
                if not isinstance(senses, list):
                    continue
                for sense in senses:
                    sense_id = sense.get("synset") if isinstance(sense, dict) else None
                    if isinstance(sense_id, str):
                        sense_id = sense_id.removeprefix("oewn-")
                        if sense_id in lemmas:
                            lemmas[sense_id].add(normalized)

    missing_lemmas = sorted(sense_id for sense_id in relevant_ids if not lemmas[sense_id])
    if missing_lemmas:
        raise ValueError(f"{len(missing_lemmas)} target/parent synsets lack release lemma surfaces")

    target_pos = Counter(str(record.get("partOfSpeech")) for record in taxonomy.values())
    edge_pos_family = Counter(_pos_family(taxonomy[child].get("partOfSpeech")) for child, _ in edges)
    edge_lemma_counts = Counter(len(lemmas[parent]) for _, parent in edges)
    parent_lemma_counts = Counter(len(lemmas[parent]) for parent in parent_ids)
    parent_pos_family = Counter(_pos_family(record.get("partOfSpeech")) for record in parent_taxonomy.values())
    frame_by_id = {row["sense_id"].removeprefix("oewn-"): row for row in frame}
    all_surface_rows = [
        {
            "relation_edge": (child, parent),
            "target_sense": child,
            "parent_synset": parent,
            "target_lemmas": lemmas[child],
            "parent_lemma": parent_lemma,
            "source_gloss_hash": frame_by_id[child].get("snapshot_definition_sha256"),
        }
        for child, parent in edges
        for parent_lemma in sorted(lemmas[parent])
    ]
    canonical_rows = [(child, min(lemmas[parent])) for child, parent in edges]
    all_surface_unique = len({(row["target_sense"], row["parent_lemma"]) for row in all_surface_rows})
    canonical_unique = len(set(canonical_rows))

    def component_summary(fields: tuple[str, ...]) -> dict[str, Any]:
        parent = list(range(len(all_surface_rows)))

        def find(index: int) -> int:
            while parent[index] != index:
                parent[index] = parent[parent[index]]
                index = parent[index]
            return index

        def union(left: int, right: int) -> None:
            left_root, right_root = find(left), find(right)
            if left_root != right_root:
                parent[right_root] = left_root

        first_by_value: dict[tuple[str, Any], int] = {}
        for index, row in enumerate(all_surface_rows):
            for field in fields:
                raw = row[field]
                values = raw if isinstance(raw, set) else (raw,)
                for value in values:
                    key = (field, value)
                    if key in first_by_value:
                        union(index, first_by_value[key])
                    else:
                        first_by_value[key] = index
        sizes = Counter(find(index) for index in range(len(all_surface_rows)))
        ordered = sorted(sizes.values(), reverse=True)
        return {
            "component_count": len(ordered),
            "largest_component_row_count": ordered[0] if ordered else 0,
            "singleton_component_count": sum(size == 1 for size in ordered),
        }

    split_component_scenarios = {
        "relation_edge_variants": component_summary(("relation_edge",)),
        "target_sense_and_edge": component_summary(("target_sense", "relation_edge")),
        "parent_synset_and_edge": component_summary(("parent_synset", "relation_edge")),
        "relation_edge_and_parent_lemma_overlap": component_summary(("relation_edge", "parent_lemma")),
        "target_and_parent_lemma_overlap": component_summary(("relation_edge", "target_lemmas", "parent_lemma")),
        "target_parent_identity_and_lemma_closure": component_summary((
            "target_sense", "relation_edge", "parent_synset", "target_lemmas", "parent_lemma", "source_gloss_hash"
        )),
    }

    return {
        "schema_version": 1,
        "audit_version": "track-a-hypothesis-surface-policy/1",
        "audit_code_sha256": _sha256_file(Path(__file__)),
        "frame_sha256": _sha256_file(frame_path),
        "release_archive_sha256": identity["release"]["archive_sha256"],
        "identity_audit_code_sha256": identity["audit_code_sha256"],
        "target_sense_count": len(target_ids),
        "target_release_lemma_count_distribution": dict(sorted(Counter(len(lemmas[sid]) for sid in target_ids).items())),
        "target_release_raw_pos_distribution": dict(sorted(target_pos.items())),
        "direct_hypernym_edge_count": len(edges),
        "direct_hypernym_child_pos_family_distribution": dict(sorted(edge_pos_family.items())),
        "unique_parent_synset_count": len(parent_ids),
        "parent_pos_family_distribution": dict(sorted(parent_pos_family.items())),
        "unique_parent_lemma_count_distribution": dict(sorted(parent_lemma_counts.items())),
        "edge_weighted_parent_lemma_count_distribution": dict(sorted(edge_lemma_counts.items())),
        "edge_count_with_multiple_parent_lemma_surfaces": sum(
            edge_count for lemma_count, edge_count in edge_lemma_counts.items() if lemma_count > 1
        ),
        "surface_policy_scenarios": {
            "one_lexicographically_first_surface_per_edge": {
                "rows": len(canonical_rows),
                "unique_child_surface_claims": canonical_unique,
                "duplicate_surface_claim_rows": len(canonical_rows) - canonical_unique,
                "selection_is_semantic_canonical": False
            },
            "one_row_per_parent_lemma_surface": {
                "rows": len(all_surface_rows),
                "unique_child_surface_claims": all_surface_unique,
                "duplicate_surface_claim_rows": len(all_surface_rows) - all_surface_unique,
                "row_inflation_over_one_per_edge": len(all_surface_rows) / len(edges) if edges else 0,
                "extra_rows_over_one_per_edge": len(all_surface_rows) - len(edges),
                "requires_edge_grouping_for_split_and_inference": True
            },
            "all_lemmas_in_one_hypothesis": {
                "rows": len(edges),
                "semantic_wording_frozen": False,
                "risks_conflating_lexical_alternatives": True
            }
        },
        "split_component_scenarios": split_component_scenarios,
        "split_component_scenarios_are_diagnostic_not_a_frozen_split": True,
        "resource_hypernym_edges_are_semantic_gold": False,
        "candidate_pairs_or_labels_created": False,
        "split_created": False,
        "interpretation_limit": (
            "Counts quantify release-linked lexical surface choices only. They do not determine which lemma is the most natural hypothesis, "
            "whether a gloss entails it, annotation workload acceptability, statistical power, or model performance."
        )
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=Path, default=DEFAULT_FRAME)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error(f"output already exists; pass --force to replace it: {args.output}")
    try:
        result = audit(args.frame, args.release_dir, args.release_archive)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "audit_version": result["audit_version"],
        "direct_hypernym_edge_count": result["direct_hypernym_edge_count"],
        "one_surface_rows": result["surface_policy_scenarios"]["one_lexicographically_first_surface_per_edge"]["rows"],
        "all_surface_rows": result["surface_policy_scenarios"]["one_row_per_parent_lemma_surface"]["rows"],
        "output": str(args.output),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
