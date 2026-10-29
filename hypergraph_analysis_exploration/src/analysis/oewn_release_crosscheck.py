"""Compare frozen source-record raw/effective glosses with a pinned OEWN JSON release.

The report includes IDs and match booleans only; it never copies definition
text. Exact string matches verify a text string's presence in the release, not
the correctness of downstream logicization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any


try:  # Direct script execution and package/module execution are both supported.
    from .project_paths import PROJECT_ROOT, configured_bundle_root
except ImportError:
    from project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_FRAME = PROJECT_ROOT / "outputs" / "phase7" / "annotation_sampling_frame.jsonl"
DEFAULT_BUNDLE = configured_bundle_root()
DEFAULT_RELEASE_DIR = PROJECT_ROOT / "tmp" / "oewn-2025-json"
DEFAULT_RELEASE_ARCHIVE = PROJECT_ROOT / "tmp" / "oewn-2025-json.zip"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase7" / "oewn_2025_release_crosscheck.json"
DEFAULT_RELEASE_NAME = "Open English WordNet 2025 Edition"
DEFAULT_RELEASE_DATE = "2025-12-31"
DEFAULT_RELEASE_URI = "https://en-word.net/static/english-wordnet-2025-json.zip"
OFFICIAL_JSON_PREFIXES = ("noun.", "verb.", "adj.", "adv.")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalise(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


def _load_frame(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid frame JSON at {path}:{line_number}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"frame line {line_number} must be an object")
            rows.append(row)
    return rows


def _load_release_definitions(release_dir: Path) -> dict[str, set[str]]:
    definitions: dict[str, set[str]] = defaultdict(set)
    files = [path for path in release_dir.glob("*.json") if path.name.startswith(OFFICIAL_JSON_PREFIXES)]
    if not files:
        raise ValueError(f"no OEWN synset JSON files found in {release_dir}")
    for path in sorted(files):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid official release JSON: {path.name}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"official release JSON must be an object: {path.name}")
        for synset_id, record in data.items():
            if not isinstance(synset_id, str) or not isinstance(record, dict):
                continue
            raw_definitions = record.get("definition")
            if isinstance(raw_definitions, str):
                definitions[synset_id].add(raw_definitions)
            elif isinstance(raw_definitions, list):
                definitions[synset_id].update(value for value in raw_definitions if isinstance(value, str))
    return definitions


def crosscheck_release(
    frame_path: Path,
    bundle: Path,
    release_dir: Path,
    release_archive: Path | None = None,
    release_name: str = DEFAULT_RELEASE_NAME,
    release_date: str = DEFAULT_RELEASE_DATE,
    release_uri: str = DEFAULT_RELEASE_URI,
):
    bundle = bundle.resolve()
    frame = _load_frame(frame_path)
    official = _load_release_definitions(release_dir)
    per_sense = []
    for candidate in frame:
        sense_id = candidate.get("sense_id")
        if not isinstance(sense_id, str) or not sense_id.startswith("oewn-"):
            raise ValueError(f"candidate is not in the OEWN namespace: {sense_id}")
        release_id = sense_id.removeprefix("oewn-")
        release_defs = official.get(release_id, set())
        source_rows = candidate.get("source_records")
        if not isinstance(source_rows, list) or not source_rows:
            raise ValueError(f"missing source records for {sense_id}")
        raw_defs = []
        effective_defs = []
        source_comparisons = []
        for source_row in source_rows:
            if not isinstance(source_row, dict):
                raise ValueError(f"malformed source record for {sense_id}")
            relative = source_row.get("path")
            expected_hash = source_row.get("sha256")
            if not isinstance(relative, str) or not isinstance(expected_hash, str):
                raise ValueError(f"malformed source evidence for {sense_id}")
            posix_path = PurePosixPath(relative)
            if posix_path.is_absolute() or ".." in posix_path.parts:
                raise ValueError(f"unsafe source path: {relative}")
            source_path = bundle.joinpath(*posix_path.parts).resolve()
            if not source_path.is_relative_to(bundle) or not source_path.is_file():
                raise ValueError(f"source file missing or outside bundle: {relative}")
            if _sha256(source_path) != expected_hash:
                raise ValueError(f"source hash mismatch: {relative}")
            try:
                source_doc = json.loads(source_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"source JSON is invalid: {relative}") from exc
            if not isinstance(source_doc, dict):
                raise ValueError(f"source JSON must be an object: {relative}")
            synset = source_doc.get("synset")
            raw = synset.get("raw_definition") if isinstance(synset, dict) else None
            if isinstance(raw, str):
                raw_defs.append(raw)
            definition = source_doc.get("definition")
            effective = definition.get("definition") if isinstance(definition, dict) else None
            if isinstance(effective, str):
                effective_defs.append(effective)
            raw_present = isinstance(raw, str)
            effective_present = isinstance(effective, str)
            raw_normalized = any(
                _normalise(raw) == _normalise(release_definition) for release_definition in release_defs
            ) if raw_present else False
            effective_normalized = any(
                _normalise(effective) == _normalise(release_definition) for release_definition in release_defs
            ) if effective_present else False
            source_comparisons.append({
                "source_payload_sha256": expected_hash,
                "source_raw_gloss_present": raw_present,
                "source_raw_gloss_length_codepoints": len(raw) if raw_present else None,
                "source_effective_gloss_present": effective_present,
                "source_effective_gloss_length_codepoints": len(effective) if effective_present else None,
                "raw_gloss_exact_match": raw in release_defs if raw_present else False,
                "raw_gloss_normalized_match": raw_normalized,
                "effective_gloss_exact_match": effective in release_defs if effective_present else False,
                "effective_gloss_normalized_match": effective_normalized,
                "raw_equals_effective": raw == effective if raw_present and effective_present else None,
            })
        exact = any(raw in release_defs for raw in raw_defs)
        normalized = any(_normalise(raw) == _normalise(definition) for raw in raw_defs for definition in release_defs)
        effective_exact = any(value in release_defs for value in effective_defs)
        effective_normalized = any(
            _normalise(value) == _normalise(release_definition)
            for value in effective_defs for release_definition in release_defs
        )
        per_sense.append({
            "sense_id": sense_id,
            "panel": candidate.get("panel", "unknown"),
            "source_record_count": len(source_rows),
            "source_raw_gloss_count": len(raw_defs),
            "source_raw_gloss_blank_count": sum(value == "" for value in raw_defs),
            "source_effective_gloss_count": len(effective_defs),
            "source_effective_gloss_blank_count": sum(value == "" for value in effective_defs),
            "official_release_synset_found": bool(release_defs),
            "raw_gloss_exact_match": exact,
            "raw_gloss_normalized_match": normalized,
            "effective_gloss_exact_match": effective_exact,
            "effective_gloss_normalized_match": effective_normalized,
            "source_record_comparisons": source_comparisons,
        })

    by_panel: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in per_sense:
        by_panel[row["panel"]].append(row)

    def counts(rows: list[dict[str, Any]]) -> dict[str, int]:
        return {
            "sense_count": len(rows),
            "official_release_synset_found": sum(row["official_release_synset_found"] for row in rows),
            "exact_raw_gloss_match": sum(row["raw_gloss_exact_match"] for row in rows),
            "normalized_raw_gloss_match": sum(row["raw_gloss_normalized_match"] for row in rows),
            "exact_effective_gloss_match": sum(row["effective_gloss_exact_match"] for row in rows),
            "normalized_effective_gloss_match": sum(row["effective_gloss_normalized_match"] for row in rows),
            "no_source_raw_gloss": sum(row["source_raw_gloss_count"] == 0 for row in rows),
            "blank_source_raw_gloss": sum(row["source_raw_gloss_blank_count"] for row in rows),
            "no_source_effective_gloss": sum(row["source_effective_gloss_count"] == 0 for row in rows),
            "blank_source_effective_gloss": sum(row["source_effective_gloss_blank_count"] for row in rows),
        }

    archive_hash = _sha256(release_archive) if release_archive and release_archive.is_file() else None
    report = {
        "audit_version": "oewn-release-crosscheck/2",
        "release_name": release_name,
        "release_date": release_date,
        "official_release_page": "https://github.com/globalwordnet/english-wordnet",
        "official_download_uri": release_uri,
        "release_archive_sha256": archive_hash,
        "release_directory": str(release_dir.resolve()),
        "frame_path": str(frame_path.resolve()),
        "frame_sha256": _sha256(frame_path),
        "bundle_path": str(bundle),
        "candidate_sense_count": len(per_sense),
        "unique_candidate_sense_count": len({row["sense_id"] for row in per_sense}),
        "raw_gloss_text_emitted": False,
        "interpretation_limit": "raw and effective string matches identify source strings present in this release; they do not validate transformations, decomposition, WSD, rule direction, or logic semantics",
        "by_panel": {panel: counts(rows) for panel, rows in sorted(by_panel.items())},
        "overall": counts(per_sense),
        "per_sense": per_sense,
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=Path, default=DEFAULT_FRAME)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--release-name", default=DEFAULT_RELEASE_NAME)
    parser.add_argument("--release-date", default=DEFAULT_RELEASE_DATE)
    parser.add_argument("--release-uri", default=DEFAULT_RELEASE_URI)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="replace an existing report")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; choose another path or pass --force to replace it")
    try:
        report = crosscheck_release(args.frame, args.bundle, args.release_dir, args.release_archive,
                                    args.release_name, args.release_date, args.release_uri)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Cross-checked {report['candidate_sense_count']} candidates against {report['release_name']}")
    print(f"Exact raw-gloss matches: {report['overall']['exact_raw_gloss_match']}")
    print(f"Exact effective-gloss matches: {report['overall']['exact_effective_gloss_match']}")
    print(f"Wrote match-only report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
