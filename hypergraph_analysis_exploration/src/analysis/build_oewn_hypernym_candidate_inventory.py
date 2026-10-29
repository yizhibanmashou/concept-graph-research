"""Build a text-minimal inventory of direct OEWN hypernym edges for a locked sense set.

The inventory is a design aid, not an annotation batch or a preregistered sample.
It includes pinned-release sense identities and lemma surfaces but no gloss text,
rendered hypotheses, labels, splits, or hidden sampling strata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from src.analysis.audit_annotation_frame_release_identity import (
    DEFAULT_LOCK,
    DEFAULT_RELEASE_ARCHIVE,
    DEFAULT_RELEASE_DIR,
    _entry_inventory,
    _read_jsonl,
    _release_lemmas,
    _sha256_file,
    audit as audit_locked_frame,
)
from src.analysis.oewn_hypernym_verifier import load_hypernym_graph


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "phase186"
DEFAULT_OUTPUT = OUTPUT_DIR / "oewn_hypernym_candidate_inventory.json"
INVENTORY_VERSION = "oewn-hypernym-candidate-inventory/0.1"


def build_inventory(
    lock_path: Path = DEFAULT_LOCK,
    release_dir: Path = DEFAULT_RELEASE_DIR,
    release_archive: Path = DEFAULT_RELEASE_ARCHIVE,
) -> dict[str, Any]:
    """Validate locked inputs and enumerate each direct hypernym edge once."""
    identity = audit_locked_frame(lock_path, release_dir, release_archive)
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    frame_spec = lock["artifacts"]["frame"]
    frame_path = PROJECT_ROOT / frame_spec["path"]
    frame = _read_jsonl(frame_path)
    target_ids = {
        row["sense_id"].removeprefix("oewn-")
        for row in frame
        if isinstance(row, dict) and isinstance(row.get("sense_id"), str)
    }
    if len(target_ids) != len(frame) or len(target_ids) != lock["expected"]["candidate_count"]:
        raise ValueError("locked frame sense IDs are invalid, duplicated, or inconsistent with its count")

    taxonomy, direct_parents = load_hypernym_graph(release_dir)
    entry_integrity = _entry_inventory(release_dir, release_archive)
    parent_ids = {parent for child in target_ids for parent in direct_parents.get(child, ())}
    relevant_ids = target_ids | parent_ids
    release_lemmas = _release_lemmas(release_dir, relevant_ids)
    missing_lemmas = sorted(synset_id for synset_id in relevant_ids
                            if not release_lemmas.get(synset_id))
    if missing_lemmas:
        raise ValueError(f"{len(missing_lemmas)} target/parent synsets lack release lemma surfaces")

    edge_rows = []
    for child_id in sorted(target_ids):
        for parent_id in direct_parents.get(child_id, ()):
            identity_material = {
                "archive_sha256": identity["release"]["archive_sha256"],
                "relation": "hypernym",
                "child_synset_id": child_id,
                "parent_synset_id": parent_id,
            }
            canonical = json.dumps(identity_material, sort_keys=True, separators=(",", ":"))
            edge_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            child_pos = taxonomy[child_id]["pos"]
            parent_pos = taxonomy[parent_id]["pos"]
            edge_rows.append({
                "relation_edge_id": f"oewn-hypernym-{edge_hash}",
                "relation": "hypernym",
                "direction": "child_to_parent",
                "child_sense_id": f"oewn-{child_id}",
                "child_release_pos": child_pos,
                "child_release_lemma_surfaces": sorted(release_lemmas[child_id]),
                "parent_sense_id": f"oewn-{parent_id}",
                "parent_release_pos": parent_pos,
                "parent_release_lemma_surfaces": sorted(release_lemmas[parent_id]),
                "candidate_parent_surface_count": len(release_lemmas[parent_id]),
            })
    edge_rows.sort(key=lambda row: (row["child_sense_id"], row["parent_sense_id"]))

    parent_surface_memberships = sum(len(release_lemmas[synset_id]) for synset_id in parent_ids)
    unique_parent_surface_strings = set().union(*(release_lemmas[synset_id] for synset_id in parent_ids))
    expanded_parent_surface_count = sum(row["candidate_parent_surface_count"] for row in edge_rows)
    child_surface_memberships = sum(len(release_lemmas[synset_id]) for synset_id in target_ids)
    unique_child_surface_strings = set().union(*(release_lemmas[synset_id] for synset_id in target_ids))
    return {
        "schema_version": INVENTORY_VERSION,
        "status": "design_inventory_only_not_annotation_input",
        "research_state": {
            "protocol_confirmed": lock.get("research_state", {}).get("protocol_signed") is True,
            "distribution_authorized": lock.get("research_state", {}).get("distribution_authorized") is True,
            "release_clearance": "not_assessed",
            "annotation_tasks_generated": False,
            "semantic_gold_created": False,
        },
        "release": {
            "name": lock["expected"]["release_name"],
            "date": lock["expected"]["release_date"],
            "archive_sha256": identity["release"]["archive_sha256"],
            "taxonomy_file_count": identity["release"]["verified_file_count"],
            "taxonomy_file_set_sha256": identity["release"]["verified_file_set_sha256"],
            "entry_file_count": entry_integrity["verified_entry_file_count"],
            "entry_file_set_sha256": entry_integrity["verified_entry_file_set_sha256"],
        },
        "inputs": {
            "lock_path": lock_path.relative_to(PROJECT_ROOT).as_posix(),
            "lock_sha256": _sha256_file(lock_path),
            "frame_path": frame_spec["path"],
            "frame_sha256": _sha256_file(frame_path),
            "candidate_sense_count": len(target_ids),
            "frame_pos_mismatch_count": identity["frame_pos_mismatch_count"],
            "frame_lemma_set_mismatch_count": identity["frame_lemma_set_mismatch_count"],
        },
        "selection_policy": {
            "target_set": "sense IDs in the hash-locked annotation candidate frame",
            "relation_source": "pinned OEWN taxonomy direct hypernym field",
            "relation_included": "hypernym",
            "instance_hypernym_included": False,
            "hypotheses_rendered": False,
            "glosses_included": False,
            "sampling_or_splits_assigned": False,
            "lemma_surface_policy": "enumerate every release lemma per parent edge; child lemma surfaces are recorded separately; no child-parent cross-product is generated",
        },
        "counts": {
            "target_senses": len(target_ids),
            "target_senses_with_direct_hypernym": len({row["child_sense_id"] for row in edge_rows}),
            "direct_hypernym_edges": len(edge_rows),
            "unique_parent_senses": len(parent_ids),
            "parent_sense_lemma_surface_memberships": parent_surface_memberships,
            "unique_parent_lemma_surface_strings": len(unique_parent_surface_strings),
            "edge_expanded_parent_surface_rows": expanded_parent_surface_count,
            "child_sense_lemma_surface_memberships": child_surface_memberships,
            "unique_child_lemma_surface_strings": len(unique_child_surface_strings),
        },
        "interpretation_limits": [
            "This inventory enumerates resource-provided candidate relations; it does not show that a child gloss semantically supports an edge.",
            "An OEWN hypernym edge is not an NLI label, source-support judgment, proof from natural-language text, or gold annotation.",
            "The frame contains one POS and one lemma-set discrepancy against the pinned release; release fields here are read from the pinned archive and the discrepancies remain unresolved in the locked frame.",
            "This local artifact includes OEWN lemma surfaces and sense identities; it is not authorized for external distribution.",
            "No premise, hypothesis, sample, split, annotation protocol, or statistical estimand is frozen by this inventory.",
        ],
        "candidates": edge_rows,
    }


def write_inventory(inventory: dict[str, Any], output: Path, force: bool = False) -> str:
    resolved_output = output.resolve()
    if not resolved_output.is_relative_to(OUTPUT_DIR.resolve()):
        raise ValueError("output must be inside outputs/phase186")
    if output.exists() and not force:
        raise FileExistsError(f"output already exists; pass --force to replace it: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(inventory, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    output.write_text(payload, encoding="utf-8", newline="\n")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error(f"output already exists; pass --force to replace it: {args.output}")
    try:
        inventory = build_inventory(args.lock, args.release_dir, args.release_archive)
        output_sha256 = write_inventory(inventory, args.output, force=args.force)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "schema_version": inventory["schema_version"],
        "counts": inventory["counts"],
        "output": str(args.output),
        "output_sha256": output_sha256,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
