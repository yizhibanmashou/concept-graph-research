"""Compare frozen annotation-frame POS/lemmas with the pinned OEWN release.

This audit emits identifiers and counts only; it never writes gloss or lemma
text. The v3 annotation files are read-only inputs and are not repaired here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

from src.analysis.gloss_genus_baseline import DEFAULT_RELEASE_ARCHIVE, DEFAULT_RELEASE_DIR
from src.analysis.oewn_hypernym_verifier import _pos_family, verify_extracted_taxonomy
from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_LOCK = PROJECT_ROOT / "config" / "annotation_preregistration_v3_lock.json"
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase144" / "annotation_frame_release_identity_audit.json"
TAXONOMY_PREFIXES = ("noun.", "verb.", "adj.", "adv.")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {path}:{line_number}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"expected a JSON object at {path}:{line_number}")
            rows.append(row)
    return rows


def _normalize_lemma(value: str) -> str:
    return " ".join(value.casefold().replace("_", " ").split())


def _entry_inventory(release_dir: Path, archive_path: Path) -> dict[str, Any]:
    extracted = sorted(path for path in release_dir.glob("entries-*.json") if path.is_file())
    if not extracted:
        raise FileNotFoundError(f"no entries-*.json files found in {release_dir}")
    archive_hashes: dict[str, str] = {}
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.namelist():
            basename = Path(member).name
            if not (basename.startswith("entries-") and basename.endswith(".json")):
                continue
            if basename in archive_hashes:
                raise ValueError(f"archive contains duplicate entry basename: {basename}")
            with archive.open(member) as stream:
                digest = hashlib.sha256()
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            archive_hashes[basename] = digest.hexdigest()
    extracted_by_name = {path.name: path for path in extracted}
    if len(extracted_by_name) != len(extracted) or set(extracted_by_name) != set(archive_hashes):
        raise ValueError("extracted entry file set does not match the pinned release archive")
    for name, path in extracted_by_name.items():
        if _sha256_file(path) != archive_hashes[name]:
            raise ValueError(f"extracted entry file differs from pinned release archive: {name}")

    aggregate = hashlib.sha256()
    for name in sorted(archive_hashes):
        aggregate.update(name.encode("utf-8"))
        aggregate.update(bytes.fromhex(archive_hashes[name]))
    return {
        "verified_entry_file_count": len(extracted_by_name),
        "verified_entry_file_set_sha256": aggregate.hexdigest(),
    }


def _release_lemmas(release_dir: Path, wanted_ids: set[str]) -> dict[str, set[str]]:
    lemmas = {synset_id: set() for synset_id in wanted_ids}
    for path in sorted(release_dir.glob("entries-*.json")):
        entries = _read_json(path)
        if not isinstance(entries, dict):
            raise ValueError(f"expected an object in {path.name}")
        for lemma, pos_map in entries.items():
            if not isinstance(lemma, str) or not isinstance(pos_map, dict):
                continue
            for entry in pos_map.values():
                senses = entry.get("sense", []) if isinstance(entry, dict) else []
                if not isinstance(senses, list):
                    continue
                for sense in senses:
                    synset_id = sense.get("synset") if isinstance(sense, dict) else None
                    if isinstance(synset_id, str):
                        synset_id = synset_id.removeprefix("oewn-")
                        if synset_id in lemmas:
                            lemmas[synset_id].add(lemma)
    return lemmas


def _source_lemma_variants(
    frame: list[dict[str, Any]], bundle: Path,
) -> tuple[dict[str, int], dict[str, list[str]]]:
    variants: dict[str, set[tuple[str, ...]]] = {}
    source_pos: dict[str, set[str]] = {}
    for row in frame:
        sense_id = row.get("sense_id")
        if not isinstance(sense_id, str):
            continue
        for source in row.get("source_records", []):
            if not isinstance(source, dict):
                raise ValueError(f"malformed source record for {sense_id}")
            relative = source.get("path")
            expected_hash = source.get("sha256")
            if not isinstance(relative, str) or not isinstance(expected_hash, str):
                raise ValueError(f"malformed source path/hash for {sense_id}")
            posix = PurePosixPath(relative)
            if posix.is_absolute() or ".." in posix.parts:
                raise ValueError(f"unsafe source path for {sense_id}")
            path = bundle.joinpath(*posix.parts).resolve()
            if not path.is_relative_to(bundle) or not path.is_file():
                raise ValueError(f"source file missing or outside bundle for {sense_id}")
            if _sha256_file(path) != expected_hash:
                raise ValueError(f"source file hash mismatch for {sense_id}")
            payload = _read_json(path)
            synset = payload.get("synset") if isinstance(payload, dict) else None
            if not isinstance(synset, dict) or synset.get("synset_id") != sense_id:
                continue
            raw_lemmas = synset.get("lemmas")
            if isinstance(raw_lemmas, list) and all(isinstance(item, str) for item in raw_lemmas):
                variants.setdefault(sense_id, set()).add(
                    tuple(sorted({_normalize_lemma(item) for item in raw_lemmas}))
                )
            pos = synset.get("pos")
            if isinstance(pos, str):
                source_pos.setdefault(sense_id, set()).add(pos)
    variant_counts = {sense_id: len(values) for sense_id, values in variants.items()}
    pos_values = {sense_id: sorted(values) for sense_id, values in source_pos.items()}
    return variant_counts, pos_values


def audit(
    lock_path: Path = DEFAULT_LOCK,
    release_dir: Path = DEFAULT_RELEASE_DIR,
    release_archive: Path = DEFAULT_RELEASE_ARCHIVE,
    bundle: Path | None = None,
) -> dict[str, Any]:
    lock = _read_json(lock_path)
    artifacts = lock.get("artifacts") if isinstance(lock, dict) else None
    if not isinstance(artifacts, dict):
        raise ValueError("annotation input lock has no artifacts object")
    artifact_hashes: dict[str, str] = {}
    for name, spec in artifacts.items():
        if not isinstance(spec, dict) or not isinstance(spec.get("path"), str):
            raise ValueError(f"invalid artifact spec in input lock: {name}")
        path = PROJECT_ROOT / spec["path"]
        digest = _sha256_file(path)
        if digest != spec.get("sha256"):
            raise ValueError(f"locked artifact hash mismatch: {name}")
        artifact_hashes[spec["path"]] = digest
    expected_archive_sha256 = lock.get("expected", {}).get("release_archive_sha256")
    if not isinstance(expected_archive_sha256, str) or _sha256_file(release_archive) != expected_archive_sha256:
        raise ValueError("release archive does not match the annotation input lock")

    frame_path = PROJECT_ROOT / artifacts["frame"]["path"]
    blind_path = PROJECT_ROOT / artifacts["blind_batch"]["path"]
    answer_path = PROJECT_ROOT / artifacts["answer_key"]["path"]
    crosscheck_path = PROJECT_ROOT / artifacts["release_crosscheck"]["path"]
    frame = _read_jsonl(frame_path)
    blind = _read_jsonl(blind_path)
    answer_key = _read_json(answer_path)
    crosscheck = _read_json(crosscheck_path)
    if not isinstance(answer_key, list):
        raise ValueError("answer key must be a JSON array")
    if not isinstance(crosscheck, dict) or not isinstance(crosscheck.get("per_sense"), list):
        raise ValueError("release crosscheck report lacks per_sense rows")

    frame_by_item = {row.get("item_id"): row for row in frame if isinstance(row.get("item_id"), str)}
    answer_by_task = {row.get("task_id"): row for row in answer_key if isinstance(row, dict)}
    answer_by_item = {row.get("item_id"): row for row in answer_key if isinstance(row, dict)}
    blind_by_task = {
        row.get("task_id"): row for row in blind if isinstance(row.get("task_id"), str)
    }
    if len(frame_by_item) != len(frame) or len(answer_by_task) != len(answer_key):
        raise ValueError("duplicate or missing frame item / answer task IDs")
    if (len(answer_by_item) != len(answer_key)
            or len(blind_by_task) != len(blind)):
        raise ValueError("duplicate or missing answer-key item / blind task IDs")
    if len(blind) != len(frame) or len(answer_key) != len(frame):
        raise ValueError("frame, blind batch, and answer key row counts differ")
    if set(answer_by_task) != set(blind_by_task):
        raise ValueError("blind batch task IDs do not match the answer key")

    target_ids = {
        row["sense_id"].removeprefix("oewn-")
        for row in frame
        if isinstance(row.get("sense_id"), str) and row["sense_id"].startswith("oewn-")
    }
    if len(target_ids) != len(frame):
        raise ValueError("frame contains invalid or duplicate OEWN sense IDs")
    release_integrity = verify_extracted_taxonomy(release_dir, release_archive)
    if not release_integrity.get("verified_file_count"):
        raise ValueError("release taxonomy integrity check did not verify files")
    entry_integrity = _entry_inventory(release_dir, release_archive)
    release_nodes: dict[str, dict[str, Any]] = {}
    for path in sorted(release_dir.iterdir()):
        if not path.is_file() or not path.name.endswith(".json") or not path.name.startswith(TAXONOMY_PREFIXES):
            continue
        data = _read_json(path)
        for synset_id in target_ids & data.keys():
            if synset_id in release_nodes:
                raise ValueError(f"target synset occurs in multiple release files: {synset_id}")
            record = data[synset_id]
            if not isinstance(record, dict):
                raise ValueError(f"invalid release record for {synset_id}")
            release_nodes[synset_id] = record
    missing_ids = target_ids - release_nodes.keys()
    if missing_ids:
        raise ValueError(f"{len(missing_ids)} frame target(s) are missing from the pinned release")

    direct_parents = {
        parent
        for record in release_nodes.values()
        for parent in record.get("hypernym", [])
        if isinstance(parent, str)
    }
    relevant_lemmas = _release_lemmas(release_dir, target_ids | direct_parents)
    source_variant_counts, source_pos_values = _source_lemma_variants(
        frame, (bundle or configured_bundle_root()).resolve()
    )

    pos_distribution = Counter()
    release_pos_distribution = Counter()
    pos_mismatches = []
    source_pos_mismatches = []
    lemma_mismatches = []
    batch_pos_mismatches = 0
    batch_lemma_mismatches = 0
    for row in frame:
        sense_id = row["sense_id"]
        release_id = sense_id.removeprefix("oewn-")
        release_record = release_nodes[release_id]
        frame_pos = row.get("pos")
        release_pos = release_record.get("partOfSpeech")
        pos_distribution[str(frame_pos)] += 1
        release_pos_distribution[str(release_pos)] += 1
        if _pos_family(frame_pos) != _pos_family(release_pos):
            pos_mismatches.append({"sense_id": sense_id, "frame_pos": frame_pos, "release_pos": release_pos})
        source_pos_families = {
            _pos_family(value) for value in source_pos_values.get(sense_id, [])
        }
        if source_pos_families and source_pos_families != {_pos_family(release_pos)}:
            source_pos_mismatches.append({
                "sense_id": sense_id,
                "source_pos_values": source_pos_values[sense_id],
                "release_pos": release_pos,
            })
        frame_lemmas_raw = row.get("lemmas")
        if not isinstance(frame_lemmas_raw, list) or any(not isinstance(x, str) for x in frame_lemmas_raw):
            raise ValueError(f"invalid frame lemma list for {sense_id}")
        frame_lemmas = {_normalize_lemma(item) for item in frame_lemmas_raw}
        release_lemmas = {_normalize_lemma(item) for item in relevant_lemmas.get(release_id, set())}
        if frame_lemmas != release_lemmas:
            lemma_mismatches.append({
                "sense_id": sense_id,
                "frame_lemma_count": len(frame_lemmas),
                "release_lemma_count": len(release_lemmas),
                "source_record_lemma_variant_count": source_variant_counts.get(sense_id, 0),
            })
        answer_row = answer_by_item.get(row.get("item_id"))
        if not isinstance(answer_row, dict):
            raise ValueError(f"frame item has no answer-key task: {sense_id}")
        blind_row = blind_by_task.get(answer_row.get("task_id"))
        if not isinstance(blind_row, dict):
            raise ValueError(f"answer-key task has no blind row: {sense_id}")
        if blind_row.get("pos") != frame_pos:
            batch_pos_mismatches += 1
        blind_lemmas = blind_row.get("lemmas")
        if (not isinstance(blind_lemmas, list)
                or any(not isinstance(item, str) for item in blind_lemmas)
                or {_normalize_lemma(item) for item in blind_lemmas} != frame_lemmas):
            batch_lemma_mismatches += 1

    crosscheck_by_sense = {
        row.get("sense_id"): row for row in crosscheck["per_sense"] if isinstance(row, dict)
    }
    if set(crosscheck_by_sense) != {row["sense_id"] for row in frame}:
        raise ValueError("release crosscheck sense set does not match the frame")
    raw_gloss_exact_match_count = sum(
        row.get("raw_gloss_exact_match") is True for row in crosscheck_by_sense.values()
    )
    direct_edges = [
        (sense_id, parent)
        for sense_id, record in release_nodes.items()
        for parent in record.get("hypernym", [])
        if isinstance(parent, str)
    ]
    parent_lemma_counts = [len(relevant_lemmas.get(parent, set())) for parent in direct_parents]
    return {
        "schema_version": 1,
        "audit_version": "annotation-frame-release-identity/1",
        "audit_code_sha256": _sha256_file(Path(__file__)),
        "input_lock_sha256": _sha256_file(lock_path),
        "locked_artifact_sha256": artifact_hashes,
        "bundle_path": str((bundle or configured_bundle_root()).resolve()),
        "release": {**release_integrity, **entry_integrity},
        "frame_count": len(frame),
        "crosscheck_raw_gloss_exact_match_count": raw_gloss_exact_match_count,
        "frame_pos_distribution": dict(sorted(pos_distribution.items())),
        "release_pos_distribution": dict(sorted(release_pos_distribution.items())),
        "target_senses_found_in_release": len(release_nodes),
        "target_senses_with_direct_hypernym": len({child for child, _ in direct_edges}),
        "direct_hypernym_candidate_edges": len(direct_edges),
        "unique_direct_parent_synsets": len(direct_parents),
        "direct_parent_synsets_with_multiple_lemma_surfaces": sum(count > 1 for count in parent_lemma_counts),
        "direct_parent_synset_lemma_surface_count_min": min(parent_lemma_counts, default=0),
        "direct_parent_synset_lemma_surface_count_median": sorted(parent_lemma_counts)[len(parent_lemma_counts) // 2] if parent_lemma_counts else 0,
        "direct_parent_synset_lemma_surface_count_max": max(parent_lemma_counts, default=0),
        "frame_pos_mismatch_count": len(pos_mismatches),
        "frame_pos_mismatches": pos_mismatches,
        "source_payload_pos_mismatch_count": len(source_pos_mismatches),
        "source_payload_pos_mismatches": source_pos_mismatches,
        "frame_lemma_set_mismatch_count": len(lemma_mismatches),
        "frame_lemma_set_mismatches": lemma_mismatches,
        "blind_batch_pos_mismatch_against_frame_count": batch_pos_mismatches,
        "blind_batch_lemma_mismatch_against_frame_count": batch_lemma_mismatches,
        "crosscheck_pos_or_lemma_verified": False,
        "interpretation_limit": (
            "The legacy crosscheck verifies gloss strings and synset availability, not POS or complete lemma-set identity. "
            "Resource hypernym edges only supply candidate-generation strata, never NLI labels or semantic gold."
        ),
        "distribution_authorized": lock.get("research_state", {}).get("distribution_authorized") is True,
        "semantic_gold_created": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error(f"output already exists; pass --force to replace it: {args.output}")
    try:
        result = audit(args.lock, args.release_dir, args.release_archive, args.bundle)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "audit_version": result["audit_version"],
        "frame_count": result["frame_count"],
        "crosscheck_raw_gloss_exact_match_count": result["crosscheck_raw_gloss_exact_match_count"],
        "frame_pos_mismatch_count": result["frame_pos_mismatch_count"],
        "frame_lemma_set_mismatch_count": result["frame_lemma_set_mismatch_count"],
        "output": str(args.output),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
