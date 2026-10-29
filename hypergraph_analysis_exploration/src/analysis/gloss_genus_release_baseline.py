"""Run the lexical genus-candidate baseline across all OEWN noun synsets.

This measures internal consistency with the same release's direct hypernym
links. It is not a semantic gold evaluation and emits no source gloss text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.analysis.gloss_genus_baseline import (
    BASELINE_VERSION,
    DEFAULT_RELEASE_ARCHIVE,
    DEFAULT_RELEASE_DIR,
    DEFAULT_MANIFEST,
    _sha256,
    build_noun_lemma_index,
    find_first_noun_candidate,
)


RELEASE_BASELINE_VERSION = "oewn-release-genus-baseline/1"


def verify_extracted_inputs(release_dir: Path, release_archive: Path) -> dict[str, Any]:
    """Verify every entries/noun file consumed by the analysis against the pinned ZIP."""
    files = sorted(list(release_dir.glob("entries-*.json")) + list(release_dir.glob("noun.*.json")))
    if not files:
        raise FileNotFoundError(f"no entries-*.json or noun.*.json files found in {release_dir}")
    archive_hashes = {}
    with zipfile.ZipFile(release_archive) as archive:
        relevant = [name for name in archive.namelist()
                    if Path(name).name.startswith(("entries-", "noun.")) and name.endswith(".json")]
        for name in relevant:
            basename = Path(name).name
            if basename in archive_hashes:
                raise ValueError(f"archive contains duplicate relevant basename: {basename}")
            with archive.open(name) as stream:
                digest = hashlib.sha256()
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            archive_hashes[basename] = digest.hexdigest()
    extracted_names = {path.name for path in files}
    if extracted_names != set(archive_hashes):
        raise ValueError("extracted entries/noun file set does not match the pinned release archive")
    for path in files:
        if _sha256(path) != archive_hashes[path.name]:
            raise ValueError(f"extracted file differs from pinned release archive: {path.name}")
    combined = hashlib.sha256()
    for path in files:
        combined.update(path.name.encode("utf-8"))
        combined.update(bytes.fromhex(archive_hashes[path.name]))
    return {
        "verified_file_count": len(files),
        "entries_file_count": sum(path.name.startswith("entries-") for path in files),
        "noun_synset_file_count": sum(path.name.startswith("noun.") for path in files),
        "extracted_inputs_sha256": combined.hexdigest(),
    }


def load_noun_synsets(release_dir: Path) -> list[dict[str, Any]]:
    """Read noun definitions and direct hypernyms without retaining source text in results."""
    paths = sorted(release_dir.glob("noun.*.json"))
    if not paths:
        raise FileNotFoundError(f"no noun.*.json synset files found in {release_dir}")
    records = []
    seen_ids = set()
    for path in paths:
        lexname = path.stem.removeprefix("noun.")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"expected a JSON object in {path}")
        for synset_id, record in data.items():
            if not isinstance(synset_id, str) or not isinstance(record, dict):
                raise ValueError(f"invalid synset record in {path}")
            if synset_id in seen_ids:
                raise ValueError(f"duplicate noun synset ID across release files: {synset_id}")
            seen_ids.add(synset_id)
            definitions = record.get("definition")
            members = record.get("members")
            hypernyms = record.get("hypernym", [])
            if (not isinstance(definitions, list) or not definitions
                    or any(not isinstance(text, str) or not text.strip() for text in definitions)):
                raise ValueError(f"invalid definition list for noun synset {synset_id}")
            if not isinstance(members, list) or any(not isinstance(x, str) for x in members):
                raise ValueError(f"invalid members list for noun synset {synset_id}")
            if not isinstance(hypernyms, list) or any(not isinstance(x, str) for x in hypernyms):
                raise ValueError(f"invalid hypernym list for noun synset {synset_id}")
            records.append({
                "synset_id": synset_id,
                "lexname": lexname,
                "definitions": definitions,
                "members": members,
                "hypernyms": sorted(set(hypernyms)),
            })
    return records


def evaluate_synsets(records: list[dict[str, Any]], noun_index: dict[str, list[str]]) -> dict[str, Any]:
    """Evaluate one exact-match candidate per noun definition instance."""
    by_lexname: dict[str, list[dict[str, Any]]] = defaultdict(list)
    overall_rows = []
    multi_definition_synsets = 0
    definition_instances = 0
    no_hypernym_definition_instances = 0
    for record in records:
        definitions = record["definitions"]
        if len(definitions) > 1:
            multi_definition_synsets += 1
        for definition_index, gloss in enumerate(definitions):
            definition_instances += 1
            if not record["hypernyms"]:
                no_hypernym_definition_instances += 1
                continue
            candidate = find_first_noun_candidate(gloss, record["members"], noun_index)
            if candidate is None:
                status = "no_lexical_candidate"
                match_count = 0
            else:
                matches = set(candidate["candidate_synset_ids"]).intersection(record["hypernyms"])
                match_count = len(matches)
                status = "candidate_matches_direct_hypernym" if matches else "candidate_not_direct_hypernym"
            row = {
                "status": status,
                "candidate": candidate,
                "matched_hypernym_sense_count": match_count,
                "definition_index": definition_index,
            }
            overall_rows.append(row)
            by_lexname[record["lexname"]].append(row)

    def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
        counts = Counter(row["status"] for row in rows)
        eligible = len(rows)
        covered = counts["candidate_matches_direct_hypernym"] + counts["candidate_not_direct_hypernym"]
        matched = counts["candidate_matches_direct_hypernym"]
        sense_counts = [row["candidate"]["candidate_sense_count"] for row in rows if row["candidate"]]
        return {
            "eligible_definition_instances": eligible,
            "status_counts": dict(sorted(counts.items())),
            "candidate_coverage": covered / eligible if eligible else None,
            "direct_hypernym_match_rate_among_candidates": matched / covered if covered else None,
            "direct_hypernym_match_rate_over_eligible": matched / eligible if eligible else None,
            "candidate_sense_count_mean": sum(sense_counts) / len(sense_counts) if sense_counts else None,
            "candidate_sense_count_max": max(sense_counts, default=0),
        }

    return {
        "baseline_version": BASELINE_VERSION,
        "release_baseline_version": RELEASE_BASELINE_VERSION,
        "method": "Same first exact 1-4 token noun-lemma heuristic as the phase9 pilot baseline; process each definition string separately and exclude all target members.",
        "evaluation_target": "Whether at least one candidate noun sense appears among the target synset's direct hypernym IDs in this same OEWN release. This is an internal resource-alignment proxy, not semantic gold.",
        "noun_synset_count": len(records),
        "definition_instance_count": definition_instances,
        "synsets_with_multiple_definition_strings": multi_definition_synsets,
        "definition_instances_without_direct_hypernym": no_hypernym_definition_instances,
        "overall": summarize(overall_rows),
        "by_lexname": {key: summarize(rows) for key, rows in sorted(by_lexname.items())},
        "source_gloss_text_emitted": False,
        "limitations": [
            "The first exact noun lemma is a weak heuristic without contextual POS tagging, phrase-head parsing, or sense disambiguation.",
            "Any-sense matching is deliberately lenient and can overstate sense-level alignment.",
            "Both candidate vocabulary and comparison taxonomy come from the same release; results are not independent semantic validation.",
            "This does not test logicization, rule direction, proof validity, natural-language entailment, or NLI.",
        ],
    }


def analyze_release(release_dir: Path, release_archive: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = manifest.get("source_release_archive_sha256")
    archive_hash = _sha256(release_archive)
    if archive_hash != expected:
        raise ValueError("release archive SHA-256 does not match the phase7 manifest")
    if manifest.get("source_release") != "Open English WordNet 2025 Plus":
        raise ValueError("expected the pinned Open English WordNet 2025 Plus release")
    extracted_verification = verify_extracted_inputs(release_dir, release_archive)
    records = load_noun_synsets(release_dir)
    noun_index = build_noun_lemma_index(release_dir)
    result = evaluate_synsets(records, noun_index)
    result["inputs"] = {
        "release_name": manifest.get("source_release"),
        "release_date": manifest.get("source_release_date"),
        "release_archive_sha256": archive_hash,
        **extracted_verification,
    }
    result["reproducibility_note"] = (
        "The per-synset definition content is read from the archive whose SHA-256 is recorded above. "
        "Every extracted entries/noun JSON file consumed by this baseline was byte-verified against the archive; "
        "the aggregate extracted_inputs_sha256 fingerprints filenames and their file digests without exposing glosses."
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        result = analyze_release(args.release_dir, args.release_archive, args.manifest)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["overall"], ensure_ascii=False, sort_keys=True))
    print(f"Scanned {result['noun_synset_count']} noun synsets / {result['definition_instance_count']} definitions")
    print(f"Aggregate report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
