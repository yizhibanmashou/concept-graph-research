"""Audit frozen v3 annotation inputs without emitting annotation content or IDs.

This is an integrity/schema preflight only. A passing result does not indicate
that the protocol is signed/registered, that licensing was reviewed, or that
distribution is authorized.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCK = PROJECT_ROOT / "config" / "annotation_preregistration_v3_lock.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[Any]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def audit(lock_path: Path) -> dict[str, Any]:
    lock = _read_json(lock_path)
    expected = lock["expected"]
    root = PROJECT_ROOT
    artifact_paths = {
        name: root / artifact["path"]
        for name, artifact in lock["artifacts"].items()
    }

    actual_hashes: dict[str, str | None] = {}
    checks: dict[str, bool] = {}
    for name, path in artifact_paths.items():
        exists = path.is_file()
        actual_hashes[name] = _sha256(path) if exists else None
        checks[f"{name}_exists"] = exists
        checks[f"{name}_sha256_matches_lock"] = (
            exists and actual_hashes[name] == lock["artifacts"][name]["sha256"]
        )

    counts: dict[str, int | None] = {
        "frame_rows": None,
        "frame_unique_items": None,
        "random_panel_rows": None,
        "diagnostic_panel_rows": None,
        "frame_strata": None,
        "blind_batch_rows": None,
        "answer_key_rows": None,
        "answer_key_task_coverage": None,
        "crosscheck_rows": None,
        "annotation_return_files": None,
    }
    # Parse only when all inputs exist; malformed JSON becomes a failed,
    # content-free check rather than an exception containing row values.
    if all(path.is_file() for path in artifact_paths.values()):
        try:
            frame = _read_jsonl(artifact_paths["frame"])
            frame_manifest = _read_json(artifact_paths["frame_manifest"])
            crosscheck = _read_json(artifact_paths["release_crosscheck"])
            batch = _read_jsonl(artifact_paths["blind_batch"])
            answer_key = _read_json(artifact_paths["answer_key"])
            batch_manifest = _read_json(artifact_paths["batch_manifest"])

            frame_ids = [row.get("item_id") for row in frame if isinstance(row, dict)]
            frame_senses = [row.get("sense_id") for row in frame if isinstance(row, dict)]
            panels = [row.get("panel") for row in frame if isinstance(row, dict)]
            strata = [row.get("stratum") for row in frame if isinstance(row, dict)]
            counts["frame_rows"] = len(frame)
            counts["frame_unique_items"] = len(set(frame_ids))
            counts["random_panel_rows"] = sum(panel == "random_stratified" for panel in panels)
            counts["diagnostic_panel_rows"] = sum(panel == "diagnostic" for panel in panels)
            counts["frame_strata"] = len(set(strata))

            counts["blind_batch_rows"] = len(batch)
            counts["answer_key_rows"] = len(answer_key) if isinstance(answer_key, list) else 0
            batch_ids = [row.get("task_id") for row in batch if isinstance(row, dict)]
            key_ids = [row.get("task_id") for row in answer_key if isinstance(row, dict)] if isinstance(answer_key, list) else []
            counts["answer_key_task_coverage"] = len(set(batch_ids) & set(key_ids))
            cross_rows = crosscheck.get("per_sense") if isinstance(crosscheck, dict) else None
            counts["crosscheck_rows"] = len(cross_rows) if isinstance(cross_rows, list) else 0
            return_files = list(root.glob(lock["return_file_glob"]))
            counts["annotation_return_files"] = len(return_files)

            expected_fields = set(expected["annotator_file_fields"])
            batch_fields_ok = all(
                isinstance(row, dict) and set(row) == expected_fields for row in batch
            )
            batch_values_ok = all(
                isinstance(row.get("task_id"), str)
                and isinstance(row.get("pos"), str)
                and row.get("pos") in {"n", "v", "a", "r"}
                and isinstance(row.get("lemmas"), list)
                and bool(row.get("lemmas"))
                and all(isinstance(lemma, str) and bool(lemma) for lemma in row["lemmas"])
                and isinstance(row.get("gloss"), str)
                and bool(row.get("gloss"))
                for row in batch if isinstance(row, dict)
            ) and len(batch_ids) == len(batch)
            no_gloss_in_frame = all(
                isinstance(row, dict)
                and "gloss" not in row
                and "definition" not in row
                and isinstance(row.get("item_id"), str)
                and bool(row.get("item_id"))
                and isinstance(row.get("sense_id"), str)
                and bool(row.get("sense_id"))
                for row in frame
            )
            checks.update({
                "frame_schema_and_counts": (
                    len(frame) == expected["candidate_count"]
                    and counts["frame_unique_items"] == expected["candidate_count"]
                    and counts["random_panel_rows"] == expected["random_panel_count"]
                    and counts["diagnostic_panel_rows"] == expected["diagnostic_panel_count"]
                    and counts["frame_strata"] == expected["stratum_count"]
                    and no_gloss_in_frame
                    and all(type(seed) is int and seed == expected["seed"] for seed in [row.get("random_seed") for row in frame if isinstance(row, dict)])
                ),
                "frame_manifest_matches_lock_and_frame": (
                    frame_manifest.get("candidate_count") == expected["candidate_count"]
                    and frame_manifest.get("frame_sha256") == actual_hashes["frame"]
                    and frame_manifest.get("frame_version") == expected["frame_version"]
                    and frame_manifest.get("seed") == expected["seed"]
                    and frame_manifest.get("random_panel_count") == expected["random_panel_count"]
                    and frame_manifest.get("diagnostic_panel_count") == expected["diagnostic_panel_count"]
                    and frame_manifest.get("gloss_text_included") is False
                    and frame_manifest.get("annotator_visible") is False
                ),
                "crosscheck_matches_pinned_release": (
                    crosscheck.get("release_name") == expected["release_name"]
                    and crosscheck.get("release_date") == expected["release_date"]
                    and crosscheck.get("official_download_uri") == expected["release_uri"]
                    and crosscheck.get("release_archive_sha256") == expected["release_archive_sha256"]
                    and crosscheck.get("frame_sha256") == actual_hashes["frame"]
                    and crosscheck.get("raw_gloss_text_emitted") is False
                    and crosscheck.get("candidate_sense_count") == expected["candidate_count"]
                    and crosscheck.get("unique_candidate_sense_count") == expected["candidate_count"]
                    and crosscheck.get("overall", {}).get("official_release_synset_found") == expected["candidate_count"]
                    and crosscheck.get("overall", {}).get("exact_raw_gloss_match") == expected["candidate_count"]
                    and isinstance(cross_rows, list)
                    and len(cross_rows) == expected["candidate_count"]
                    and all(isinstance(row, dict) and row.get("raw_gloss_exact_match") is True for row in cross_rows)
                    and {row.get("sense_id") for row in cross_rows if isinstance(row, dict)} == set(frame_senses)
                ),
                "blind_batch_schema_and_answer_key_coverage": (
                    len(batch) == expected["candidate_count"]
                    and batch_fields_ok
                    and all(isinstance(task_id, str) and task_id for task_id in batch_ids)
                    and len(set(batch_ids)) == expected["candidate_count"]
                    and batch_values_ok
                    and isinstance(answer_key, list)
                    and len(answer_key) == expected["candidate_count"]
                    and len(set(key_ids)) == expected["candidate_count"]
                    and set(batch_ids) == set(key_ids)
                ),
                "batch_manifest_binds_inputs_and_attribution": (
                    batch_manifest.get("batch_version") == expected["batch_version"]
                    and batch_manifest.get("candidate_count") == expected["candidate_count"]
                    and batch_manifest.get("frame_sha256") == actual_hashes["frame"]
                    and batch_manifest.get("crosscheck_sha256") == actual_hashes["release_crosscheck"]
                    and batch_manifest.get("batch_sha256") == actual_hashes["blind_batch"]
                    and batch_manifest.get("answer_key_sha256") == actual_hashes["answer_key"]
                    and batch_manifest.get("source_release") == expected["release_name"]
                    and batch_manifest.get("source_release_date") == expected["release_date"]
                    and batch_manifest.get("source_release_uri") == expected["release_uri"]
                    and batch_manifest.get("source_release_archive_sha256") == expected["release_archive_sha256"]
                    and batch_manifest.get("license") == expected["license"]
                    and batch_manifest.get("annotator_file_fields") == expected["annotator_file_fields"]
                    and batch_manifest.get("withheld_from_annotators") == expected["withheld_from_annotators"]
                    and bool(batch_manifest.get("attribution"))
                    and bool(batch_manifest.get("copyright_notice"))
                    and bool(batch_manifest.get("use_limit"))
                ),
                "no_annotation_return_files": counts["annotation_return_files"] == 0,
                "lock_does_not_claim_registration_or_distribution": (
                    lock.get("research_state") == {
                        "protocol_signed": False,
                        "external_preregistration_id": None,
                        "distribution_authorized": False,
                    }
                ),
            })
        except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError):
            checks["json_and_schema_parse"] = False
    else:
        checks["json_and_schema_parse"] = False

    # Zip validation is byte-level only; file members are not read or emitted.
    result = {
        "schema_version": "annotation-preregistration-v3-preflight/1",
        "scope": "integrity_and_schema_only",
        "integrity_pass": bool(checks) and all(checks.values()),
        "checks": checks,
        "counts": counts,
        "actual_sha256": actual_hashes,
        "research_state": lock.get("research_state", {}),
        "distribution_authorized": False,
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    args = parser.parse_args(argv)
    try:
        result = audit(args.lock.resolve())
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        # Keep exception details out of the output: they can contain local paths
        # or content-derived values.
        print(json.dumps({
            "schema_version": "annotation-preregistration-v3-preflight/1",
            "scope": "integrity_and_schema_only",
            "integrity_pass": False,
            "checks": {"lock_readable_and_valid": False},
            "distribution_authorized": False,
        }, indent=2))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["integrity_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
