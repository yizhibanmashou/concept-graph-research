"""Export a blinded annotation batch from a verified OEWN 2025 Plus sample.

The annotator-facing file omits synset IDs, graph features, sampling strata,
and source paths. A separate answer key retains those fields and must not be
shared with annotators before independent annotation is complete.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path, PurePosixPath
from typing import Any

from src.analysis.oewn_release_crosscheck import (
    DEFAULT_BUNDLE,
    DEFAULT_FRAME,
    _load_frame,
    _load_release_definitions,
    _sha256,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RELEASE_DIR = PROJECT_ROOT / "tmp" / "oewn-2025-plus-json"
DEFAULT_CROSSCHECK = PROJECT_ROOT / "outputs" / "phase7" / "oewn_2025_plus_release_crosscheck.json"
DEFAULT_BATCH = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_blind.jsonl"
DEFAULT_KEY = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_answer_key.json"
DEFAULT_MANIFEST = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_manifest.json"
RELEASE_NAME = "Open English WordNet 2025 Plus"
RELEASE_DATE = "2025-12-31"
RELEASE_URI = "https://en-word.net/static/english-wordnet-2025-plus-json.zip"
RELEASE_ARCHIVE_SHA256 = "8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e"
ATTRIBUTION = (
    "Open English WordNet 2025 Plus, based on Princeton WordNet and the Open English WordNet team; "
    "licensed under CC BY 4.0."
)
COPYRIGHT_NOTICE = (
    "Copyright (c) 2019-present, The Open English WordNet Team; underlying WordNet data incorporates "
    "the Princeton University WordNet database."
)
LICENSE_URI = "https://creativecommons.org/licenses/by/4.0/"
SOURCE_URI = "https://github.com/globalwordnet/english-wordnet"
LICENSE_NOTICE_URI = "https://github.com/globalwordnet/english-wordnet/blob/main/LICENSE.md"


def _load_crosscheck(path: Path, frame_path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("release_name") != RELEASE_NAME or report.get("release_date") != RELEASE_DATE:
        raise ValueError("cross-check report is not for the pinned OEWN 2025 Plus release")
    if report.get("official_download_uri") != RELEASE_URI:
        raise ValueError("cross-check report has an unexpected official release URI")
    if report.get("release_archive_sha256") != RELEASE_ARCHIVE_SHA256:
        raise ValueError("cross-check report does not match the pinned 2025 Plus archive hash")
    if report.get("frame_sha256") != _sha256(frame_path):
        raise ValueError("cross-check report was generated from a different annotation frame")
    if report.get("raw_gloss_text_emitted") is not False:
        raise ValueError("cross-check report must be match-only and contain no raw gloss text")
    overall = report.get("overall", {})
    total = report.get("candidate_sense_count")
    if not isinstance(total, int) or total <= 0:
        raise ValueError("cross-check report has no candidates")
    if overall.get("sense_count") != total:
        raise ValueError("cross-check aggregate count is inconsistent")
    if overall.get("official_release_synset_found") != total:
        raise ValueError("not every candidate exists in the pinned release")
    if overall.get("exact_raw_gloss_match") != total:
        raise ValueError("not every candidate raw gloss exactly matches the pinned release")
    rows = report.get("per_sense")
    if not isinstance(rows, list) or len(rows) != total:
        raise ValueError("cross-check per-sense evidence is incomplete")
    matches = {row.get("sense_id"): row for row in rows if isinstance(row, dict)}
    if len(matches) != total or any(row.get("raw_gloss_exact_match") is not True for row in matches.values()):
        raise ValueError("cross-check per-sense evidence is duplicated or has a non-matching gloss")
    return matches


def build_batch(
    frame_path: Path,
    bundle: Path,
    release_dir: Path,
    crosscheck_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    frame_path = frame_path.resolve()
    bundle = bundle.resolve()
    frame = _load_frame(frame_path)
    if len({row.get("sense_id") for row in frame}) != len(frame):
        raise ValueError("annotation frame contains duplicate sense IDs")
    evidence = _load_crosscheck(crosscheck_path, frame_path)
    if set(evidence) != {row.get("sense_id") for row in frame}:
        raise ValueError("cross-check report and frame have different candidate sets")
    official = _load_release_definitions(release_dir)

    rows = []
    key_rows = []
    for row in frame:
        sense_id = row.get("sense_id")
        if not isinstance(sense_id, str) or not sense_id.startswith("oewn-"):
            raise ValueError(f"candidate is not an OEWN sense: {sense_id}")
        source_records = row.get("source_records")
        if not isinstance(source_records, list) or not source_records:
            raise ValueError(f"missing source evidence for {sense_id}")
        source_docs = []
        for source_record in source_records:
            if not isinstance(source_record, dict):
                raise ValueError(f"malformed source record for {sense_id}")
            relative = source_record.get("path")
            expected_hash = source_record.get("sha256")
            if not isinstance(relative, str) or not isinstance(expected_hash, str):
                raise ValueError(f"malformed source hash evidence for {sense_id}")
            relative_path = PurePosixPath(relative)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                raise ValueError(f"unsafe source path: {relative}")
            source_path = bundle.joinpath(*relative_path.parts).resolve()
            if not source_path.is_relative_to(bundle) or not source_path.is_file():
                raise ValueError(f"source file missing or outside bundle: {relative}")
            if _sha256(source_path) != expected_hash:
                raise ValueError(f"source hash mismatch: {relative}")
            source_doc = json.loads(source_path.read_text(encoding="utf-8"))
            synset = source_doc.get("synset") if isinstance(source_doc, dict) else None
            if isinstance(synset, dict) and synset.get("synset_id") == sense_id:
                source_docs.append((source_record, source_doc))
        raw_glosses = {
            source_doc.get("synset", {}).get("raw_definition")
            for _, source_doc in source_docs
            if isinstance(source_doc.get("synset", {}).get("raw_definition"), str)
        }
        if not raw_glosses:
            raise ValueError(f"no raw gloss found in verified source records for {sense_id}")
        release_defs = official.get(sense_id.removeprefix("oewn-"), set())
        exact_candidates = sorted(raw_glosses & release_defs)
        if not exact_candidates:
            raise ValueError(f"raw gloss does not match pinned official release for {sense_id}")
        if len(exact_candidates) != 1:
            raise ValueError(f"multiple exact release glosses for {sense_id}; manual resolution required")
        lemmas = row.get("lemmas")
        if not isinstance(lemmas, list) or not lemmas or any(not isinstance(x, str) or not x for x in lemmas):
            raise ValueError(f"invalid lemma list for {sense_id}")
        structural_features = row.get("structural_features", {})
        if not isinstance(structural_features, dict):
            raise ValueError(f"invalid graph structural features for {sense_id}")
        release_evidence = evidence[sense_id]
        source_release_details = release_evidence.get("source_record_comparisons")
        if source_release_details is not None:
            if not isinstance(source_release_details, list):
                raise ValueError(f"invalid source release comparisons for {sense_id}")
            expected_hashes = [record["sha256"] for record in source_records]
            actual_hashes = [
                detail.get("source_payload_sha256") if isinstance(detail, dict) else None
                for detail in source_release_details
            ]
            if actual_hashes != expected_hashes:
                raise ValueError(f"source release comparisons do not match frame records for {sense_id}")
            for detail in source_release_details:
                for field in (
                    "raw_gloss_exact_match",
                    "effective_gloss_exact_match",
                    "effective_gloss_normalized_match",
                ):
                    if type(detail.get(field)) is not bool:
                        raise ValueError(f"invalid source release comparison field {field} for {sense_id}")
        rows.append({
            "pos": row.get("pos"),
            "lemmas": lemmas,
            "gloss": exact_candidates[0],
            "_sense_id": sense_id,
            "_item_id": row.get("item_id"),
            "_panel": row.get("panel"),
            "_stratum": row.get("stratum"),
            "_source_records": source_records,
            "_graph_features": structural_features,
            "_release_comparison": {
                "raw_gloss_exact_match": release_evidence["raw_gloss_exact_match"],
                "raw_gloss_normalized_match": release_evidence.get("raw_gloss_normalized_match"),
                "effective_gloss_exact_match": release_evidence.get("effective_gloss_exact_match"),
                "effective_gloss_normalized_match": release_evidence.get("effective_gloss_normalized_match"),
                "source_record_details_status": (
                    "present" if source_release_details is not None else "not_in_legacy_crosscheck"
                ),
                "source_record_details": source_release_details or [],
            },
        })

    seed = frame[0].get("random_seed") if frame else None
    if type(seed) is not int:
        raise ValueError("frame does not contain a deterministic integer random seed")
    random.Random(seed ^ 0x5A17).shuffle(rows)
    batch = []
    for index, row in enumerate(rows, start=1):
        task_id = f"WN-{index:04d}"
        batch.append({"task_id": task_id, "pos": row["pos"], "lemmas": row["lemmas"], "gloss": row["gloss"]})
        key_rows.append({
            "task_id": task_id,
            "sense_id": row["_sense_id"],
            "item_id": row["_item_id"],
            "panel": row["_panel"],
            "stratum": row["_stratum"],
            "source_records": row["_source_records"],
            "graph_structural_features": row["_graph_features"],
            "release_comparison": row["_release_comparison"],
        })
    manifest = {
        "batch_version": "oewn-blind-annotation-batch/1",
        "candidate_count": len(batch),
        "source_release": RELEASE_NAME,
        "source_release_date": RELEASE_DATE,
        "source_release_uri": RELEASE_URI,
        "source_release_archive_sha256": RELEASE_ARCHIVE_SHA256,
        "source_repository": SOURCE_URI,
        "license": "CC BY 4.0",
        "license_uri": LICENSE_URI,
        "license_notice_uri": LICENSE_NOTICE_URI,
        "copyright_notice": COPYRIGHT_NOTICE,
        "attribution": ATTRIBUTION,
        "modification_notice": "Selected and shuffled synset records; raw gloss strings retained verbatim; assigned blind task IDs. No definition text edits were made.",
        "frame_sha256": _sha256(frame_path),
        "crosscheck_sha256": _sha256(crosscheck_path),
        "annotator_file_fields": ["task_id", "pos", "lemmas", "gloss"],
        "withheld_from_annotators": [
            "synset_id", "item_id", "graph_features", "release_comparison",
            "sampling_panel", "stratum", "source_paths",
        ],
        "blindness_scope": "blinded to graph/system outputs and panel membership; lemma, POS, and source gloss remain visible because they are annotation context",
        "use_limit": "annotation input only; not a gold dataset until independent annotations and adjudication are complete",
    }
    return batch, key_rows, manifest


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_batch_outputs(
    batch: list[dict[str, Any]],
    answer_key: list[dict[str, Any]],
    manifest: dict[str, Any],
    batch_path: Path,
    answer_key_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    """Write LF-stable exports and return their content hashes in the manifest."""
    batch_path.parent.mkdir(parents=True, exist_ok=True)
    with batch_path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in batch))
    _write_json(answer_key_path, answer_key)
    result_manifest = dict(manifest)
    result_manifest["batch_sha256"] = _sha256(batch_path)
    result_manifest["answer_key_sha256"] = _sha256(answer_key_path)
    _write_json(manifest_path, result_manifest)
    return result_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=Path, default=DEFAULT_FRAME)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--crosscheck", type=Path, default=DEFAULT_CROSSCHECK)
    parser.add_argument("--batch", type=Path, default=DEFAULT_BATCH)
    parser.add_argument("--answer-key", type=Path, default=DEFAULT_KEY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--force", action="store_true", help="replace existing export files")
    args = parser.parse_args(argv)
    output_paths = (args.batch, args.answer_key, args.manifest)
    if not args.force and any(path.exists() for path in output_paths):
        parser.error("an output already exists; choose new paths or pass --force to replace")
    try:
        batch, answer_key, manifest = build_batch(args.frame, args.bundle, args.release_dir, args.crosscheck)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    manifest = write_batch_outputs(batch, answer_key, manifest, args.batch, args.answer_key, args.manifest)
    print(f"Wrote blinded annotation input ({len(batch)} rows): {args.batch}")
    print(f"Keep the answer key from annotators: {args.answer_key}")
    print(f"Attribution and export provenance: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
