"""Diagnose WN30-lfs entries not resolved by the strict WordNet 3.0 key join.

This is a diagnostic layer over the Phase257 exact crosswalk. It compares
normalized gloss strings to release glosses and reports candidate synset IDs,
without promoting gloss matches into strict identity matches or copying gloss
text into the audit output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import iterparse


POS_FILES = {"n": "data.noun", "v": "data.verb", "a": "data.adj", "r": "data.adv"}
SENSE_TYPE_TO_POS = {"1": "n", "2": "v", "3": "a", "4": "r", "5": "a"}
PLACEHOLDER_RE = re.compile(r"\bSOMETHING_\d+\b", re.IGNORECASE)
NONWORD_RE = re.compile(r"[^\w]+", re.UNICODE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def norm_gloss(value: str, *, strip_placeholders: bool = False) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    if strip_placeholders:
        value = PLACEHOLDER_RE.sub(" ", value)
    value = NONWORD_RE.sub(" ", value)
    return " ".join(value.split())


def _member(tar: tarfile.TarFile, suffix: str):
    hits = [member for member in tar.getmembers() if member.name.endswith(suffix)]
    if len(hits) != 1:
        raise ValueError(f"Expected one member ending in {suffix!r}; found {len(hits)}")
    stream = tar.extractfile(hits[0])
    if stream is None:
        raise ValueError(f"Unable to read archive member {hits[0].name}")
    return hits[0], stream


def _read_sense_index(tar: tarfile.TarFile):
    _member_info, stream = _member(tar, "/dict/index.sense")
    by_lemma_pos: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    exact_keys = set()
    for raw in stream:
        sense_key, offset, sense_number, _tag_count = raw.decode("ascii").split()
        lemma, lex_sense = sense_key.split("%", 1)
        pos = SENSE_TYPE_TO_POS[lex_sense.split(":", 1)[0]]
        sense_number = int(sense_number)
        by_lemma_pos[(lemma.casefold(), pos)].append({"sense_number": sense_number, "synset_id": f"{pos}:{offset}"})
        exact_keys.add((lemma.casefold(), pos, sense_number))
    return by_lemma_pos, exact_keys


def _read_data_glosses(tar: tarfile.TarFile):
    gloss_index: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    synset_meta: dict[tuple[str, str], dict[str, Any]] = {}
    for pos, filename in POS_FILES.items():
        _member_info, stream = _member(tar, f"/dict/{filename}")
        for raw in stream:
            if raw.startswith(b"  ") or b"|" not in raw:
                continue
            fields_raw, gloss_raw = raw.decode("ascii").rstrip("\n").split("|", 1)
            fields = fields_raw.split()
            offset = fields[0]
            word_count = int(fields[3], 16)
            lemmas = [fields[4 + 2 * i].casefold() for i in range(word_count)]
            gloss = gloss_raw.strip()
            synset_id = f"{pos}:{offset}"
            synset_meta[(pos, offset)] = {"lemmas": lemmas, "gloss": gloss}
            candidates = [
                {"synset_id": synset_id, "wordnet_gloss_variant": "full"},
                {"synset_id": synset_id, "wordnet_gloss_variant": "before_first_semicolon"},
            ]
            variants = {norm_gloss(gloss): "full"}
            if ";" in gloss:
                variants.setdefault(norm_gloss(gloss.split(";", 1)[0]), "before_first_semicolon")
            for lemma in set(lemmas):
                for normalized, variant in variants.items():
                    gloss_index[(pos, normalized)].append({
                        "synset_id": synset_id,
                        "matched_lemma": lemma,
                        "wordnet_gloss_variant": variant,
                    })
    return gloss_index, synset_meta


def diagnose(lfs_zip: Path, wordnet_tar: Path, crosswalk_json: Path) -> dict[str, Any]:
    lfs_zip, wordnet_tar, crosswalk_json = lfs_zip.resolve(), wordnet_tar.resolve(), crosswalk_json.resolve()
    strict = json.loads(crosswalk_json.read_text(encoding="utf-8"))
    if strict.get("audit_version") != "wn30-lfs-synset-crosswalk/1":
        raise ValueError("Crosswalk JSON is not a supported Phase257 audit output")
    strict_keys = strict["crosswalk"]["unmapped_entry_keys"]
    with tarfile.open(wordnet_tar, "r:gz") as tar:
        lemma_pos_index, exact_keys = _read_sense_index(tar)
        gloss_index, synset_meta = _read_data_glosses(tar)

    unresolved_rows = []
    with zipfile.ZipFile(lfs_zip) as archive:
        xml_members = [name for name in archive.namelist() if name.lower().endswith(".xml")]
        if len(xml_members) != 1:
            raise ValueError(f"Expected exactly one WN30-lfs XML member; found {len(xml_members)}")
        xml_member = xml_members[0]
        with archive.open(xml_member) as stream:
            for _event, element in iterparse(stream, events=("end",)):
                if element.tag != "entry":
                    continue
                word = element.attrib.get("word", "")
                parts = word.rsplit("#", 2)
                if len(parts) != 3 or not parts[2].isdigit():
                    if word in strict_keys:
                        unresolved_rows.append((word, element.attrib.get("status", "missing"), element.findtext("gloss", "")))
                else:
                    lemma, pos, sense = parts[0].casefold(), parts[1].casefold(), int(parts[2])
                    if (lemma, pos, sense) not in exact_keys and word in strict_keys:
                        unresolved_rows.append((word, element.attrib.get("status", "missing"), element.findtext("gloss", "")))
                element.clear()

    unresolved_key_counter = Counter(word for word, _status, _gloss in unresolved_rows)
    if dict(sorted(unresolved_key_counter.items())) != dict(sorted(strict_keys.items())):
        raise ValueError("Unmapped XML entries do not match the supplied Phase257 crosswalk key counts")

    diagnostics = []
    category_counts: Counter[str] = Counter()
    for word, status, gloss in sorted(unresolved_rows):
        lemma, pos, _sense = word.rsplit("#", 2)
        lemma_pos_candidates = lemma_pos_index.get((lemma.casefold(), pos.casefold()), [])
        full_normalized = norm_gloss(gloss)
        placeholder_normalized = norm_gloss(gloss, strip_placeholders=True)
        xml_forms = {"full": full_normalized}
        if placeholder_normalized != full_normalized:
            xml_forms["placeholder_removed"] = placeholder_normalized
        matches: dict[str, set[str]] = defaultdict(set)
        for xml_variant, normalized in xml_forms.items():
            if not normalized:
                continue
            for match in gloss_index.get((pos.casefold(), normalized), []):
                match_label = f"xml_{xml_variant}:wordnet_{match['wordnet_gloss_variant']}"
                matches[match["synset_id"]].add(match_label)

        candidate_ids = {item["synset_id"] for item in lemma_pos_candidates}
        gloss_candidate_ids = set(matches)
        same_lemma_gloss_ids = candidate_ids & gloss_candidate_ids
        if len(same_lemma_gloss_ids) == 1:
            category = "unique_exact_gloss_match_with_same_lemma_pos"
        elif len(same_lemma_gloss_ids) > 1:
            category = "ambiguous_exact_gloss_matches_with_same_lemma_pos"
        elif len(gloss_candidate_ids) == 1:
            category = "unique_exact_gloss_match_other_lemma_same_pos"
        elif len(gloss_candidate_ids) > 1:
            category = "ambiguous_exact_gloss_matches_same_pos"
        elif candidate_ids:
            category = "lemma_pos_present_but_no_exact_gloss_match"
        else:
            category = "no_exact_lemma_pos_or_gloss_match"
        category_counts[category] += 1

        gloss_candidate_details = []
        for synset_id in sorted(gloss_candidate_ids):
            syn_pos, offset = synset_id.split(":", 1)
            meta = synset_meta[(syn_pos, offset)]
            gloss_candidate_details.append({
                "synset_id": synset_id,
                "wordnet_lemmas": meta["lemmas"],
                "matched_entry_lemma": lemma.casefold() in meta["lemmas"],
                "matched_variants": sorted(matches[synset_id]),
            })
        diagnostics.append({
            "wn30_lfs_key": word,
            "status": status,
            "normalized_gloss_sha256": hashlib.sha256(norm_gloss(gloss).encode("utf-8")).hexdigest(),
            "gloss_character_count": len(gloss),
            "category": category,
            "lemma_pos_candidate_count": len(candidate_ids),
            "lemma_pos_candidates": lemma_pos_candidates,
            "exact_gloss_candidate_count_same_pos": len(gloss_candidate_ids),
            "exact_gloss_candidates": gloss_candidate_details,
            "note": "Exact normalized string candidate for diagnosis only; it does not change Phase257 strict identity coverage.",
        })

    return {
        "audit_version": "wn30-lfs-unmapped-entry-diagnostic/1",
        "source_crosswalk_sha256": sha256(crosswalk_json),
        "inputs": {
            "wn30_lfs_zip": {"name": lfs_zip.name, "bytes": lfs_zip.stat().st_size, "sha256": sha256(lfs_zip)},
            "wordnet_3_0_tar_gz": {"name": wordnet_tar.name, "bytes": wordnet_tar.stat().st_size, "sha256": sha256(wordnet_tar)},
        },
        "matching_policy": {
            "exact_key": "lemma/POS/sense_number match from index.sense remains authoritative and is not altered.",
            "gloss_candidates": "After NFKC, case-fold, punctuation-to-space and whitespace normalization, compare WN30-lfs gloss against the full release gloss or its text before the first semicolon. SOMETHING_N placeholders are ignored in an additional diagnostic variant.",
            "no_gloss_text_copied": "The output stores only normalized gloss hashes and lengths, not gloss strings.",
            "candidate_policy": "Gloss matches are diagnostic candidates and do not count as exact identity matches or coverage.",
        },
        "unmapped_entry_count": len(unresolved_rows),
        "unmapped_unique_key_count": len(unresolved_key_counter),
        "category_counts": dict(sorted(category_counts.items())),
        "entries": diagnostics,
        "interpretation_limits": [
            "An exact definition-string match can identify a plausible release candidate but does not prove that the WN30-lfs key was generated from that release or that the LF is semantically faithful.",
            "No approximate string similarity, fuzzy lemma transformation, release mapping, or sense-number reassignment is performed.",
            "Entries without a unique exact gloss candidate remain unresolved.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lfs-zip", type=Path, required=True)
    parser.add_argument("--wordnet-tar", type=Path, required=True)
    parser.add_argument("--crosswalk-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = diagnose(args.lfs_zip, args.wordnet_tar, args.crosswalk_json)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output.resolve()),
        "unmapped_entries": result["unmapped_entry_count"],
        "unmapped_unique_keys": result["unmapped_unique_key_count"],
        "category_counts": result["category_counts"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
