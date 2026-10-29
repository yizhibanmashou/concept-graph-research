"""Crosswalk WN30-lfs entries to the official Princeton WordNet 3.0 synset inventory.

The WN30-lfs ``word`` attribute stores lemma/POS/sense-number keys rather than
synset offsets. Resolve those keys through WordNet 3.0 ``index.sense`` and
compare the resulting offsets with the release's four ``data.*`` inventories.
This is an identity/coverage audit only; it does not assess LF semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import iterparse


POS_BY_SENSE_TYPE = {"1": "n", "2": "v", "3": "a", "4": "r", "5": "a"}
DATA_FILES = ("data.noun", "data.verb", "data.adj", "data.adv")
DATA_LINE_RE = re.compile(rb"^(\d{8})\s")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_member(tar: tarfile.TarFile, suffix: str):
    matches = [member for member in tar.getmembers() if member.name.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"Expected one tar member ending in {suffix!r}; found {len(matches)}")
    stream = tar.extractfile(matches[0])
    if stream is None:
        raise ValueError(f"Could not read tar member: {matches[0].name}")
    return matches[0], stream


def _load_sense_index(tar: tarfile.TarFile) -> tuple[dict[tuple[str, str, int], str], dict[str, Any], set[tuple[str, str]]]:
    member, stream = _read_member(tar, "/dict/index.sense")
    key_to_offset: dict[tuple[str, str, int], str] = {}
    offset_to_keys: dict[tuple[str, str], list[str]] = defaultdict(list)
    rows = 0
    for raw_line in stream:
        fields = raw_line.decode("ascii").split()
        if len(fields) != 4:
            raise ValueError(f"Malformed index.sense row {rows + 1}: {raw_line[:120]!r}")
        sense_key, offset, sense_number, _tag_count = fields
        lemma, separator, sense_type_and_rest = sense_key.partition("%")
        if not separator:
            raise ValueError(f"Malformed sense key: {sense_key!r}")
        sense_type = sense_type_and_rest.split(":", 1)[0]
        pos = POS_BY_SENSE_TYPE.get(sense_type)
        if pos is None:
            raise ValueError(f"Unknown WordNet sense type {sense_type!r} in {sense_key!r}")
        identity = (lemma.casefold(), pos, int(sense_number))
        if identity in key_to_offset:
            raise ValueError(f"Duplicate lemma/POS/sense-number key: {identity!r}")
        key_to_offset[identity] = offset
        offset_to_keys[(pos, offset)].append(sense_key)
        rows += 1
    return key_to_offset, {
        "archive_member": member.name,
        "member_bytes": member.size,
        "sense_key_rows": rows,
        "unique_sense_offsets": len(offset_to_keys),
        "sense_keys_per_offset_max": max(map(len, offset_to_keys.values()), default=0),
    }, set(offset_to_keys)


def _load_synset_inventory(tar: tarfile.TarFile) -> tuple[set[tuple[str, str]], dict[str, int], dict[str, set[tuple[str, str]]]]:
    offsets: set[tuple[str, str]] = set()
    counts: dict[str, int] = {}
    offsets_by_pos: dict[str, set[tuple[str, str]]] = {}
    for filename in DATA_FILES:
        member, stream = _read_member(tar, f"/dict/{filename}")
        file_offsets: set[tuple[str, str]] = set()
        pos = {"data.noun": "n", "data.verb": "v", "data.adj": "a", "data.adv": "r"}[filename]
        for raw_line in stream:
            match = DATA_LINE_RE.match(raw_line)
            if match:
                file_offsets.add((pos, match.group(1).decode("ascii")))
        counts[filename] = len(file_offsets)
        offsets_by_pos[filename.removeprefix("data.")] = file_offsets
        offsets.update(file_offsets)
        if member.size <= 0:
            raise ValueError(f"Unexpected empty database member: {member.name}")
    return offsets, counts, offsets_by_pos


def crosswalk(lfs_zip: Path, wordnet_tar: Path) -> dict[str, Any]:
    lfs_zip, wordnet_tar = lfs_zip.resolve(), wordnet_tar.resolve()
    with tarfile.open(wordnet_tar, "r:gz") as tar:
        sense_index, sense_index_metadata, sense_index_offsets = _load_sense_index(tar)
        synset_offsets, synset_counts_by_file, synset_offsets_by_file = _load_synset_inventory(tar)

    with zipfile.ZipFile(lfs_zip) as archive:
        members = [name for name in archive.namelist() if name.lower().endswith(".xml")]
        if len(members) != 1:
            raise ValueError(f"Expected one XML member in WN30-lfs archive; found {len(members)}")
        xml_member = members[0]
        entry_count = 0
        status_counts: Counter[str] = Counter()
        pos_entry_counts: Counter[str] = Counter()
        mapped_offsets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        unmapped_keys: Counter[str] = Counter()
        unmapped_by_pos: Counter[str] = Counter()
        unmapped_known_lemma_pos: Counter[str] = Counter()
        indexed_lemma_pos = {(lemma, pos) for lemma, pos, _sense in sense_index}
        indexed_offsets_by_lemma_pos: dict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
        for lemma, pos, sense_number in sense_index:
            indexed_offsets_by_lemma_pos[(lemma, pos)].append((sense_number, sense_index[(lemma, pos, sense_number)]))
        entry_key_counts: Counter[str] = Counter()

        with archive.open(xml_member) as xml_stream:
            for _event, element in iterparse(xml_stream, events=("end",)):
                if element.tag != "entry":
                    continue
                entry_count += 1
                word = element.attrib.get("word", "")
                status = element.attrib.get("status", "missing")
                status_counts[status] += 1
                entry_key_counts[word] += 1
                parts = word.rsplit("#", 2)
                if len(parts) != 3 or not parts[2].isdigit():
                    unmapped_keys[word or "<missing-word-attribute>"] += 1
                else:
                    lemma, pos, sense_text = parts
                    identity = (lemma.casefold(), pos.casefold(), int(sense_text))
                    pos_entry_counts[pos.casefold()] += 1
                    offset = sense_index.get(identity)
                    if offset is None:
                        unmapped_keys[word] += 1
                        unmapped_by_pos[pos.casefold()] += 1
                        if identity[:2] in indexed_lemma_pos:
                            unmapped_known_lemma_pos[word] += 1
                    else:
                        synset_identity = (pos.casefold(), offset)
                        mapped_offsets[synset_identity].append({"word": word, "status": status})
                element.clear()

    lfs_offsets = set(mapped_offsets)
    missing_offsets = synset_offsets - lfs_offsets
    extra_offsets = lfs_offsets - synset_offsets
    offset_status_counts: Counter[str] = Counter()
    for entries in mapped_offsets.values():
        statuses = {entry["status"] for entry in entries}
        offset_status_counts[next(iter(statuses)) if len(statuses) == 1 else "status_conflict"] += 1

    exact_duplicate_entry_keys = {
        key: count for key, count in sorted(entry_key_counts.items()) if count > 1
    }
    unique_lemma_pos_candidates: dict[str, str] = {}
    ambiguous_lemma_pos_candidates: dict[str, list[dict[str, Any]]] = {}
    for word in unmapped_keys:
        parts = word.rsplit("#", 2)
        if len(parts) != 3 or not parts[2].isdigit():
            continue
        lemma, pos, _sense = parts
        candidates = indexed_offsets_by_lemma_pos.get((lemma.casefold(), pos.casefold()), [])
        if len(candidates) == 1:
            unique_lemma_pos_candidates[word] = f"{pos.casefold()}:{candidates[0][1]}"
        elif len(candidates) > 1:
            ambiguous_lemma_pos_candidates[word] = [
                {"wordnet_3_0_sense_number": sense_number, "synset_id": f"{pos.casefold()}:{offset}"}
                for sense_number, offset in sorted(candidates)
            ]
    multi_entry_offsets = {
        f"{pos}:{offset}": entries
        for (pos, offset), entries in sorted(mapped_offsets.items())
        if len(entries) > 1
    }

    return {
        "audit_version": "wn30-lfs-synset-crosswalk/1",
        "inputs": {
            "wn30_lfs_zip": {"name": lfs_zip.name, "bytes": lfs_zip.stat().st_size, "sha256": sha256(lfs_zip)},
            "wordnet_3_0_tar_gz": {"name": wordnet_tar.name, "bytes": wordnet_tar.stat().st_size, "sha256": sha256(wordnet_tar)},
        },
        "identity_method": {
            "wn30_lfs_key_format": "lemma#pos#sense_number",
            "join": "exact case-folded lemma + POS + sense_number against WordNet 3.0 index.sense; compare resolved offsets to WordNet 3.0 data.noun/data.verb/data.adj/data.adv offsets",
            "pos_mapping": {"n": "noun", "v": "verb", "a": "adjective including satellite senses", "r": "adverb"},
        },
        "wordnet_3_0_inventory": {
            "index_sense": sense_index_metadata,
            "synsets_by_data_file": synset_counts_by_file,
            "unique_synset_offsets": len(synset_offsets),
            "index_sense_offset_difference_from_data_files": {
                "sense_index_offsets_missing_from_data_files": len(sense_index_offsets - synset_offsets),
                "data_file_offsets_missing_from_sense_index": len(synset_offsets - sense_index_offsets),
            },
        },
        "wn30_lfs": {
            "xml_member": xml_member,
            "entry_count": entry_count,
            "entry_status_counts": dict(sorted(status_counts.items())),
            "entry_pos_counts": dict(sorted(pos_entry_counts.items())),
            "unique_mapped_synset_ids": len(lfs_offsets),
            "unique_offset_status_counts_consistent_across_entries": dict(sorted(offset_status_counts.items())),
            "exact_entry_key_duplicate_count": sum(count - 1 for count in exact_duplicate_entry_keys.values()),
            "exact_entry_key_duplicates": exact_duplicate_entry_keys,
        },
        "crosswalk": {
            "matched_unique_offsets": len(lfs_offsets & synset_offsets),
            "strict_synset_coverage_percent": round(len(lfs_offsets & synset_offsets) / len(synset_offsets) * 100, 4),
            "wordnet_offsets_missing_from_wn30_lfs": len(missing_offsets),
            "wn30_lfs_offsets_absent_from_wordnet_3_0": len(extra_offsets),
            "unmapped_entry_count": sum(unmapped_keys.values()),
            "unmapped_entry_count_by_pos": dict(sorted(unmapped_by_pos.items())),
            "unmapped_entry_keys": dict(sorted(unmapped_keys.items())),
            "unmapped_keys_with_known_lemma_pos_but_unmatched_sense_number": dict(sorted(unmapped_known_lemma_pos.items())),
            "unmapped_entries_with_single_lemma_pos_candidate_not_used_in_strict_join": unique_lemma_pos_candidates,
            "unmapped_entries_with_ambiguous_lemma_pos_candidates": ambiguous_lemma_pos_candidates,
            "duplicate_offset_entry_count_beyond_one_entry_per_offset": sum(len(entries) - 1 for entries in multi_entry_offsets.values()),
            "offsets_with_multiple_entries_count": len(multi_entry_offsets),
            "offsets_with_multiple_distinct_entry_keys_count": sum(
                len({entry["word"] for entry in entries}) > 1 for entries in multi_entry_offsets.values()
            ),
            "offsets_with_multiple_entries": multi_entry_offsets,
            "missing_offsets_by_pos": {
                pos: len(synset_offsets_by_file[filename] - lfs_offsets)
                for pos, filename in (("n", "noun"), ("v", "verb"), ("a", "adj"), ("r", "adv"))
            },
            "matched_synsets_by_pos": {
                pos: len(synset_offsets_by_file[filename] & lfs_offsets)
                for pos, filename in (("n", "noun"), ("v", "verb"), ("a", "adj"), ("r", "adv"))
            },
            "missing_synset_ids": [f"{pos}:{offset}" for pos, offset in sorted(missing_offsets)],
            "extra_offsets": [f"{pos}:{offset}" for pos, offset in sorted(extra_offsets)],
        },
        "interpretation": [
            "Offset matching is exact and scoped to the Princeton WordNet 3.0 release used to build index.sense and the data.* inventory.",
            "This audit establishes identifier alignment and resource entry coverage only; it does not assess LF semantic fidelity, parsing correctness, or license compatibility of WN30-lfs.",
            "Synset identity is (POS, eight-digit data offset); offsets may overlap across the separate POS database files.",
            "The strict coverage numerator uses only exact lemma/POS/sense_number matches; candidate lemma/POS-only fallbacks are listed for diagnosis and are not counted as matches.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lfs-zip", type=Path, required=True)
    parser.add_argument("--wordnet-tar", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    result = crosswalk(args.lfs_zip, args.wordnet_tar)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = result["crosswalk"]
    print(json.dumps({
        "output": str(args.output.resolve()),
        "wordnet_3_0_synsets": result["wordnet_3_0_inventory"]["unique_synset_offsets"],
        "wn30_lfs_entries": result["wn30_lfs"]["entry_count"],
        "matched_unique_offsets": summary["matched_unique_offsets"],
        "strict_synset_coverage_percent": summary["strict_synset_coverage_percent"],
        "missing_offsets": summary["wordnet_offsets_missing_from_wn30_lfs"],
        "extra_offsets": summary["wn30_lfs_offsets_absent_from_wordnet_3_0"],
        "unmapped_entries": summary["unmapped_entry_count"],
        "duplicate_offset_entries_beyond_first": summary["duplicate_offset_entry_count_beyond_one_entry_per_offset"],
        "exact_entry_key_duplicates": result["wn30_lfs"]["exact_entry_key_duplicate_count"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
