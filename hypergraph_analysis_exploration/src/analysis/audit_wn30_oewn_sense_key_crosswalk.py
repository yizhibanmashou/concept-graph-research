"""Audit WordNet 3.0 to OEWN 2025+ identity alignment via exact sense keys."""
from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree.ElementTree import iterparse

try:
    from .audit_wn30_lfs_synset_crosswalk import POS_BY_SENSE_TYPE
except ImportError:  # Direct script execution from this directory.
    from audit_wn30_lfs_synset_crosswalk import POS_BY_SENSE_TYPE


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_wordnet_sense_keys(
    archive: tarfile.TarFile,
) -> tuple[dict[str, tuple[str, str]], dict[tuple[str, str, int], str]]:
    matches = [member for member in archive.getmembers() if member.name.endswith("/dict/index.sense")]
    if len(matches) != 1:
        raise ValueError(f"Expected one WordNet index.sense member; found {len(matches)}")
    stream = archive.extractfile(matches[0])
    if stream is None:
        raise ValueError(f"Could not read {matches[0].name}")
    result: dict[str, tuple[str, str]] = {}
    key_by_identity: dict[tuple[str, str, int], str] = {}
    for line_number, raw in enumerate(stream, start=1):
        fields = raw.decode("ascii").split()
        if len(fields) != 4:
            raise ValueError(f"Malformed index.sense row {line_number}")
        key, offset, sense_number, _tag_count = fields
        sense_type = key.partition("%")[2][:1]
        pos = POS_BY_SENSE_TYPE.get(sense_type)
        if pos is None:
            raise ValueError(f"Unknown sense type {sense_type!r} in {key!r}")
        normalized = key.casefold()
        if normalized in result:
            raise ValueError(f"Duplicate WordNet sense key: {key!r}")
        result[normalized] = (pos, offset)
        identity = (key.partition("%")[0].casefold(), pos, int(sense_number))
        if identity in key_by_identity:
            raise ValueError(f"Duplicate WordNet lemma/POS/sense number: {identity!r}")
        key_by_identity[identity] = normalized
    return result, key_by_identity


def _load_oewn_sense_keys(archive: zipfile.ZipFile) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for name in archive.namelist():
        if not (name.startswith("entries-") and name.endswith(".json")):
            continue
        entries = json.loads(archive.read(name))
        for by_pos in entries.values():
            for info in by_pos.values():
                for sense in info.get("sense", []):
                    result[sense["id"].casefold()].add(sense["synset"])
    return result


def _synset_alignment(wordnet: dict[str, tuple[str, str]], oewn: dict[str, set[str]]) -> dict[str, int]:
    keys_by_wn_synset: dict[tuple[str, str], set[str]] = defaultdict(set)
    targets_by_wn_synset: dict[tuple[str, str], set[str]] = defaultdict(set)
    matched_keys = 0
    conflicting_key_targets = 0
    for key, wn_synset in wordnet.items():
        keys_by_wn_synset[wn_synset].add(key)
        targets = oewn.get(key, set())
        if targets:
            matched_keys += 1
            targets_by_wn_synset[wn_synset].update(targets)
            if len(targets) > 1:
                conflicting_key_targets += 1

    complete = partial = conflicting = unmatched = 0
    for synset, keys in keys_by_wn_synset.items():
        matched = sum(bool(oewn.get(key)) for key in keys)
        targets = targets_by_wn_synset[synset]
        if not matched:
            unmatched += 1
        elif len(targets) > 1:
            conflicting += 1
        elif matched == len(keys):
            complete += 1
        else:
            partial += 1
    return {
        "wordnet_sense_keys": len(wordnet),
        "exact_oewn_sense_key_matches": matched_keys,
        "unmatched_wordnet_sense_keys": len(wordnet) - matched_keys,
        "sense_key_coverage_percent": round(100 * matched_keys / len(wordnet), 4),
        "wordnet_synsets": len(keys_by_wn_synset),
        "synsets_all_keys_map_to_one_oewn_synset": complete,
        "synsets_partially_mapped_to_one_oewn_synset": partial,
        "synsets_with_multiple_oewn_targets": conflicting,
        "synsets_with_no_oewn_target": unmatched,
        "sense_keys_with_multiple_oewn_targets": conflicting_key_targets,
    }


def audit(wordnet_tar: Path, oewn_zip: Path, lfs_zip: Path | None = None) -> dict:
    wordnet_tar, oewn_zip = wordnet_tar.resolve(), oewn_zip.resolve()
    with tarfile.open(wordnet_tar, "r:gz") as archive:
        wordnet, key_by_identity = _load_wordnet_sense_keys(archive)
    with zipfile.ZipFile(oewn_zip) as archive:
        oewn = _load_oewn_sense_keys(archive)
    alignment = _synset_alignment(wordnet, oewn)
    result = {
        "audit": "wordnet30-oewn-sense-key-crosswalk/1",
        "inputs": {
            "wordnet_3_0": {"name": wordnet_tar.name, "bytes": wordnet_tar.stat().st_size, "sha256": _sha256(wordnet_tar)},
            "oewn_2025_plus": {"name": oewn_zip.name, "bytes": oewn_zip.stat().st_size, "sha256": _sha256(oewn_zip)},
        },
        "method": "case-folded exact WordNet sense-key ID match in OEWN entry records; synset-level alignment is grouped through matched keys, not offset equality",
        "alignment": alignment,
        "limitations": [
            "This is identifier coverage, not semantic validation or proof that aligned glosses are interchangeable.",
            "A WordNet synset can map to multiple OEWN synsets when its member sense keys disagree; these cases must not be forced into a one-to-one synset mapping.",
            "Benchmark gold labels and evaluation sentences are not read by this audit.",
        ],
    }
    if lfs_zip is not None:
        result["inputs"]["wn30_lfs"] = {"name": lfs_zip.name, "bytes": lfs_zip.stat().st_size, "sha256": _sha256(lfs_zip)}
        result["wn30_lfs"] = _audit_lfs(lfs_zip.resolve(), oewn, key_by_identity)
    return result


def _audit_lfs(
    path: Path,
    oewn: dict[str, set[str]],
    key_by_identity: dict[tuple[str, str, int], str],
) -> dict:
    with zipfile.ZipFile(path) as archive:
        xml_members = [name for name in archive.namelist() if name.lower().endswith(".xml")]
        if len(xml_members) != 1:
            raise ValueError(f"Expected one WN30-lfs XML member; found {len(xml_members)}")
        entries = mapped = no_wordnet_key = no_oewn_key = malformed = 0
        with archive.open(xml_members[0]) as stream:
            for _event, element in iterparse(stream, events=("end",)):
                if element.tag != "entry":
                    continue
                entries += 1
                parts = element.attrib.get("word", "").rsplit("#", 2)
                if len(parts) != 3 or not parts[2].isdigit():
                    malformed += 1
                else:
                    lemma, pos, sense_number = parts
                    identity = (lemma.casefold(), pos.casefold(), int(sense_number))
                    key = key_by_identity.get(identity)
                    if key is None:
                        no_wordnet_key += 1
                    elif key not in oewn:
                        no_oewn_key += 1
                    else:
                        mapped += 1
                element.clear()
    return {"entry_count": entries, "mapped_via_exact_sense_key": mapped, "unmapped_wordnet_key": no_wordnet_key,
            "unmapped_oewn_key": no_oewn_key, "malformed_entry_key": malformed}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wordnet-tar", type=Path, required=True)
    parser.add_argument("--oewn-zip", type=Path, required=True)
    parser.add_argument("--lfs-zip", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.wordnet_tar, args.oewn_zip, args.lfs_zip)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "alignment": result["alignment"], "wn30_lfs": result.get("wn30_lfs")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
