"""Quantify how locked-frame/release identity mismatches affect edge workloads.

This is an aggregate-only, read-only diagnostic. It does not repair the locked
frame, choose which resource version is authoritative, or create annotation
items, hypotheses, labels, or splits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from src.analysis.audit_annotation_frame_release_identity import (
    DEFAULT_LOCK,
    _pos_family,
    _read_json,
    audit as audit_frame_release_identity,
)
from src.analysis.audit_oewn_hypernym_candidate_workload import (
    DESIGN_ANNOTATORS_PER_NLI_PAIR,
    DESIGN_CONDITIONS,
)
from src.analysis.build_oewn_hypernym_candidate_inventory import (
    PROJECT_ROOT,
    build_inventory,
)


OUTPUT_ROOT = PROJECT_ROOT / "outputs"
BUILDER_PATH = PROJECT_ROOT / "src" / "analysis" / "build_oewn_hypernym_candidate_inventory.py"
IDENTITY_AUDITOR_PATH = PROJECT_ROOT / "src" / "analysis" / "audit_annotation_frame_release_identity.py"
WORKLOAD_AUDITOR_PATH = PROJECT_ROOT / "src" / "analysis" / "audit_oewn_hypernym_candidate_workload.py"
DEFAULT_OUTPUT = OUTPUT_ROOT / "phase191" / "oewn_candidate_identity_impact_v2.json"
AUDIT_VERSION = "oewn-candidate-identity-impact/2"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"expected object at {path}:{line_number}")
            rows.append(row)
    return rows


def _norm_lemma(value: str) -> str:
    return " ".join(value.casefold().replace("_", " ").split())


def audit(lock_path: Path = DEFAULT_LOCK) -> dict[str, Any]:
    """Recheck locked inputs and return aggregate impact without identities."""
    lock = _read_json(lock_path)
    frame_path = PROJECT_ROOT / lock["artifacts"]["frame"]["path"]
    frame_rows = _read_jsonl(frame_path)
    frame_by_sense = {row["sense_id"]: row for row in frame_rows}
    if len(frame_by_sense) != len(frame_rows):
        raise ValueError("locked frame contains duplicate sense IDs")

    identity = audit_frame_release_identity(lock_path=lock_path)
    inventory = build_inventory(lock_path=lock_path)
    pos_mismatches = identity["frame_pos_mismatches"]
    lemma_mismatches = identity["frame_lemma_set_mismatches"]
    pos_ids = {row["sense_id"] for row in pos_mismatches}
    lemma_ids = {row["sense_id"] for row in lemma_mismatches}
    edge_rows = inventory["candidates"]

    released_noun_edges = 0
    frame_noun_edges = 0
    released_noun_parent_rows = 0
    frame_noun_parent_rows = 0
    release_child_parent_pairs = 0
    frame_child_parent_pairs = 0
    pos_edge_count = 0
    pos_parent_surface_rows = 0
    pos_child_parent_pairs = 0
    lemma_edge_count = 0
    lemma_parent_surface_rows = 0
    lemma_release_pairs = 0
    lemma_frame_pairs = 0

    for edge in edge_rows:
        child_id = edge["child_sense_id"]
        parent_count = len(edge["parent_release_lemma_surfaces"])
        release_child_count = len(edge["child_release_lemma_surfaces"])
        frame_child_count = len({
            _norm_lemma(value) for value in frame_by_sense[child_id]["lemmas"]
        })
        release_pos = edge["child_release_pos"]
        frame_pos = frame_by_sense[child_id]["pos"]
        release_child_parent_pairs += release_child_count * parent_count
        frame_child_parent_pairs += frame_child_count * parent_count

        release_is_noun = _pos_family(release_pos) == "n"
        frame_is_noun = _pos_family(frame_pos) == "n"
        if release_is_noun:
            released_noun_edges += 1
            released_noun_parent_rows += parent_count
        if frame_is_noun:
            frame_noun_edges += 1
            frame_noun_parent_rows += parent_count

        if child_id in pos_ids:
            pos_edge_count += 1
            pos_parent_surface_rows += parent_count
            pos_child_parent_pairs += release_child_count * parent_count
        if child_id in lemma_ids:
            lemma_edge_count += 1
            lemma_parent_surface_rows += parent_count
            lemma_release_pairs += release_child_count * parent_count
            lemma_frame_pairs += frame_child_count * parent_count

    frame_counts = {
        "target_senses": len(frame_rows),
        "frame_pos_mismatch_senses": len(pos_ids),
        "frame_pos_mismatch_rate": len(pos_ids) / len(frame_rows) if frame_rows else 0.0,
        "frame_lemma_set_mismatch_senses": len(lemma_ids),
        "frame_lemma_set_mismatch_rate": len(lemma_ids) / len(frame_rows) if frame_rows else 0.0,
        "mismatch_sense_overlap": len(pos_ids & lemma_ids),
        "grain": "one locked annotation-frame row per target sense",
    }
    return {
        "audit_version": AUDIT_VERSION,
        "status": "aggregate_identity_impact_only_no_repair_or_annotation",
        "inputs": {
            "lock_path": lock_path.relative_to(PROJECT_ROOT).as_posix(),
            "lock_sha256": _sha256_file(lock_path),
            "frame_path": lock["artifacts"]["frame"]["path"],
            "frame_sha256": _sha256_file(frame_path),
            "release_archive_sha256": identity["release"]["archive_sha256"],
            "inventory_builder_sha256": _sha256_file(BUILDER_PATH),
            "identity_auditor_sha256": _sha256_file(IDENTITY_AUDITOR_PATH),
            "workload_auditor_sha256": _sha256_file(WORKLOAD_AUDITOR_PATH),
        },
        "frame_quality": frame_counts,
        "pos_mismatch_impact": {
            "mismatch_senses_with_candidate_edges": len({
                edge["child_sense_id"] for edge in edge_rows
            } & pos_ids),
            "affected_direct_hypernym_edges": pos_edge_count,
            "affected_parent_surface_rows": pos_parent_surface_rows,
            "affected_child_parent_surface_pairs": pos_child_parent_pairs,
            "noun_edge_count_using_release_pos": released_noun_edges,
            "noun_edge_count_using_locked_frame_pos": frame_noun_edges,
            "noun_parent_surface_rows_using_release_pos": released_noun_parent_rows,
            "noun_parent_surface_rows_using_locked_frame_pos": frame_noun_parent_rows,
        },
        "lemma_mismatch_impact": {
            "affected_direct_hypernym_edges": lemma_edge_count,
            "affected_parent_surface_rows": lemma_parent_surface_rows,
            "affected_edge_release_child_parent_surface_pairs": lemma_release_pairs,
            "affected_edge_locked_frame_child_parent_surface_pairs": lemma_frame_pairs,
            "affected_pair_delta_release_minus_frame": lemma_release_pairs - lemma_frame_pairs,
            "affected_edge_release_pos_counts": {
                pos: sum(
                    edge["child_release_pos"] == pos
                    for edge in edge_rows if edge["child_sense_id"] in lemma_ids
                )
                for pos in sorted({
                    edge["child_release_pos"]
                    for edge in edge_rows if edge["child_sense_id"] in lemma_ids
                })
            },
            "distinct_source_record_lemma_variant_counts": sorted({
                row["source_record_lemma_variant_count"] for row in lemma_mismatches
            }),
        },
        "workload_sensitivity": {
            "nli_conditions_assumed": DESIGN_CONDITIONS,
            "independent_annotators_per_exact_pair_assumed": DESIGN_ANNOTATORS_PER_NLI_PAIR,
            "assumptions_confirmed": False,
            "release_pos_all_surface_pair_rows": release_child_parent_pairs,
            "locked_frame_lemmas_all_surface_pair_rows": frame_child_parent_pairs,
            "release_pos_nli_judgments_all_surfaces_if_assumptions_hold": (
                release_child_parent_pairs * DESIGN_CONDITIONS * DESIGN_ANNOTATORS_PER_NLI_PAIR
            ),
            "locked_frame_lemmas_nli_judgments_all_surfaces_if_assumptions_hold": (
                frame_child_parent_pairs * DESIGN_CONDITIONS * DESIGN_ANNOTATORS_PER_NLI_PAIR
            ),
            "one_child_surface_per_edge_judgment_count_is_independent_of_lemma_membership": True,
        },
        "research_state": {
            "protocol_confirmed": False,
            "distribution_authorized": lock.get("research_state", {}).get("distribution_authorized") is True,
            "release_clearance": "not_assessed",
            "annotation_tasks_generated": False,
            "semantic_gold_created": False,
        },
        "interpretation_limits": [
            "The frame and the pinned release differ; this audit quantifies downstream impact but does not decide which resource version is authoritative for the research task.",
            "The POS mismatch affects no direct-hypernym edge in this inventory; noun-only edge counts therefore do not change when edges are grouped by frame POS rather than release POS.",
            "Lemma mismatch sensitivity is conditional on using every child lemma surface. A one-unspecified-child-surface-per-edge design has unchanged row counts, but surface choice validity still requires an explicit policy.",
            "The two-condition/two-annotator counts are inherited unconfirmed design assumptions, not a protocol, sample-size calculation, power analysis, or effective sample size.",
            "No sense IDs, lemmas, glosses, hypotheses, annotation values, or split assignments are emitted.",
        ],
    }


def write_report(result: dict[str, Any], output: Path) -> str:
    resolved = output.resolve()
    if not resolved.is_relative_to(OUTPUT_ROOT.resolve()):
        raise ValueError("output must be inside project outputs/")
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    output.write_text(payload, encoding="utf-8", newline="\n")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        result = audit(args.lock)
        output_sha256 = write_report(result, args.output)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "audit_version": result["audit_version"],
        "frame_quality": result["frame_quality"],
        "pos_mismatch_impact": result["pos_mismatch_impact"],
        "lemma_mismatch_impact": result["lemma_mismatch_impact"],
        "workload_sensitivity": result["workload_sensitivity"],
        "output": str(args.output),
        "output_sha256": output_sha256,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
