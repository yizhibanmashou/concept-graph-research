"""Audit the public WN30-lfs XML container and identifier schema.

This audit records archive/XML structure and entry-key shape without copying
glosses or logical forms. It does not infer synset identity or assess LF
semantics, release coverage, or license compatibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import iterparse


ENTRY_KEY_RE = re.compile(r"^.+#[nvar]#\d+$", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_schema(archive_path: Path) -> dict[str, Any]:
    archive_path = archive_path.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        xml_members = [item for item in archive.infolist() if item.filename.lower().endswith(".xml")]
        if len(xml_members) != 1:
            raise ValueError(f"Expected exactly one XML member; found {len(xml_members)}")
        xml_info = xml_members[0]
        root_tag: str | None = None
        root_attributes: dict[str, str] = {}
        entry_attribute_counts: Counter[str] = Counter()
        child_tag_counts: Counter[str] = Counter()
        status_counts: Counter[str] = Counter()
        pos_counts: Counter[str] = Counter()
        keys: Counter[str] = Counter()
        malformed_keys: Counter[str] = Counter()
        entry_count = 0
        entries_with_offset_attribute = 0
        entries_with_explicit_release_attribute = 0

        with archive.open(xml_info.filename) as stream:
            for event, element in iterparse(stream, events=("start", "end")):
                if event == "start" and root_tag is None:
                    root_tag = element.tag
                    root_attributes = dict(element.attrib)
                    continue
                if event != "end" or element.tag != "entry":
                    continue

                entry_count += 1
                entry_attribute_counts.update(element.attrib.keys())
                status_counts[element.attrib.get("status", "<missing>")] += 1
                key = element.attrib.get("word", "")
                keys[key] += 1
                match = ENTRY_KEY_RE.fullmatch(key)
                if match:
                    pos_counts[key.rsplit("#", 2)[1].casefold()] += 1
                else:
                    malformed_keys[key or "<missing-word-attribute>"] += 1
                entries_with_offset_attribute += int(any(name.casefold() in {"offset", "synset_offset", "synsetid", "synset_id"} for name in element.attrib))
                entries_with_explicit_release_attribute += int(any(name.casefold() in {"release", "wordnet_version", "version"} for name in element.attrib))
                child_tag_counts.update(child.tag for child in element)
                element.clear()

    return {
        "audit_version": "wn30-lfs-source-schema/1",
        "input": {
            "archive_name": archive_path.name,
            "archive_bytes": archive_path.stat().st_size,
            "archive_sha256": sha256(archive_path),
            "archive_member_count": len(archive.infolist()),
            "xml_member": xml_info.filename,
            "xml_member_uncompressed_bytes": xml_info.file_size,
        },
        "xml_container": {
            "root_tag": root_tag,
            "root_attributes": dict(sorted(root_attributes.items())),
            "entry_count": entry_count,
            "entry_attribute_name_counts": dict(sorted(entry_attribute_counts.items())),
            "direct_child_tag_counts": dict(sorted(child_tag_counts.items())),
            "entry_status_counts": dict(sorted(status_counts.items())),
            "entry_key_format": "lemma#pos#sense_number (observed regex: ^.+#[nvar]#\\d+$)",
            "entry_key_pos_counts": dict(sorted(pos_counts.items())),
            "unique_entry_key_count": len(keys),
            "duplicate_entry_key_occurrence_count": sum(count - 1 for count in keys.values()),
            "malformed_entry_key_count": sum(malformed_keys.values()),
            "entry_keys_with_explicit_synset_offset_attribute": entries_with_offset_attribute,
            "entry_keys_with_explicit_release_attribute": entries_with_explicit_release_attribute,
        },
        "interpretation_limits": [
            "The XML structure records a word key and status plus gloss/LF and optional subLF children; it contains no explicit synset-offset attribute on entries.",
            "A lemma/POS/sense-number key is release-dependent and cannot be treated as a stable cross-version identifier without a version-specific crosswalk.",
            "This structural audit does not independently validate the paper's source/version description, identity coverage, LF semantics, or resource license.",
            "Gloss and logical-form text are not copied into this output.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True, help="Official WN30-lfs ZIP archive")
    parser.add_argument("--output", type=Path, required=True, help="JSON output path")
    args = parser.parse_args(argv)

    result = audit_schema(args.archive)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output.resolve()),
        "archive_sha256": result["input"]["archive_sha256"],
        "xml_member": result["input"]["xml_member"],
        "entry_count": result["xml_container"]["entry_count"],
        "unique_entry_key_count": result["xml_container"]["unique_entry_key_count"],
        "malformed_entry_key_count": result["xml_container"]["malformed_entry_key_count"],
        "offset_attributes": result["xml_container"]["entry_keys_with_explicit_synset_offset_attribute"],
        "release_attributes": result["xml_container"]["entry_keys_with_explicit_release_attribute"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
