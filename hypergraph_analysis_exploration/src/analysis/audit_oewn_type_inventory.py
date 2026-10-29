"""Profile authoritative OEWN synset labels and relation families without gloss output.

The profile is an input audit, not a semantic type induction system. It keeps
only release-bound aggregate counts and non-text relation structure.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.oewn_hypernym_verifier import (
    DEFAULT_RELEASE_ARCHIVE,
    DEFAULT_RELEASE_DIR,
    POS_VALUES,
    RELEASE_DATE,
    RELEASE_NAME,
    _pos_family,
    _taxonomy_file,
    verify_extracted_taxonomy,
)


AUDIT_VERSION = "oewn-type-inventory-profile/1"
RELATIONS = ("hypernym", "instance_hypernym")
FILE_FAMILY_POS = {"noun": "n", "verb": "v", "adj": "a", "adv": "r"}
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase73" / "oewn_type_inventory_audit.json"


def audit_type_inventory(release_dir: Path, release_archive: Path) -> dict[str, Any]:
    """Return a deterministic, text-free profile of the pinned synset inventory."""
    release_check = verify_extracted_taxonomy(release_dir, release_archive)
    paths = sorted(
        path for path in release_dir.iterdir()
        if path.is_file() and _taxonomy_file(path.name)
    )
    if not paths:
        raise FileNotFoundError(f"no noun/verb/adj/adv synset JSON files found in {release_dir}")

    nodes: dict[str, dict[str, str]] = {}
    pos_counts: Counter[str] = Counter()
    lexname_counts: Counter[str] = Counter()
    pos_file_mismatches = 0
    pending_edges: dict[str, list[tuple[str, str, str]]] = {name: [] for name in RELATIONS}

    for path in paths:
        lexname = path.stem
        expected_family = FILE_FAMILY_POS.get(lexname.split(".", 1)[0])
        if expected_family is None:
            raise ValueError(f"unexpected lexicographer filename family: {path.name}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"expected a JSON object in {path.name}")
        for synset_id, record in data.items():
            if not isinstance(synset_id, str) or not synset_id or not isinstance(record, dict):
                raise ValueError(f"invalid synset record in {path.name}")
            pos = record.get("partOfSpeech")
            if not isinstance(pos, str) or pos not in POS_VALUES:
                raise ValueError(f"invalid partOfSpeech in {path.name}")
            if synset_id in nodes:
                raise ValueError("duplicate synset ID across release files")
            if _pos_family(pos) != expected_family:
                pos_file_mismatches += 1
            nodes[synset_id] = {"pos": pos, "lexname": lexname}
            pos_counts[pos] += 1
            lexname_counts[lexname] += 1
            for relation in RELATIONS:
                targets = record.get(relation, [])
                if (not isinstance(targets, list)
                        or any(not isinstance(target, str) or not target for target in targets)):
                    raise ValueError(f"invalid {relation} targets in {path.name}")
                if len(targets) != len(set(targets)):
                    raise ValueError(f"duplicate {relation} target in {path.name}")
                pending_edges[relation].extend((synset_id, target, lexname) for target in targets)

    relation_profiles = {}
    for relation, edges in pending_edges.items():
        lexname_pairs: Counter[tuple[str, str]] = Counter()
        cross_pos_edges = 0
        missing_targets = 0
        for source_id, target_id, source_lexname in edges:
            target = nodes.get(target_id)
            if target is None:
                missing_targets += 1
                continue
            lexname_pairs[(source_lexname, target["lexname"])] += 1
            if _pos_family(nodes[source_id]["pos"]) != _pos_family(target["pos"]):
                cross_pos_edges += 1
        if missing_targets:
            raise ValueError(f"{relation} references {missing_targets} missing synset endpoint(s)")
        relation_profiles[relation] = {
            "edge_count": len(edges),
            "cross_pos_edge_count": cross_pos_edges,
            "cross_lexname_edge_count": sum(
                count for (source, target), count in lexname_pairs.items() if source != target
            ),
            "lexname_pair_counts": [
                {"source": source, "target": target, "edge_count": count}
                for (source, target), count in sorted(lexname_pairs.items())
            ],
        }

    return {
        "schema_version": AUDIT_VERSION,
        "release": {
            "name": RELEASE_NAME,
            "date": RELEASE_DATE,
            **release_check,
        },
        "synset_count": len(nodes),
        "part_of_speech_counts": dict(sorted(pos_counts.items())),
        "lexicographer_file_count": len(lexname_counts),
        "lexicographer_file_synset_counts": dict(sorted(lexname_counts.items())),
        "part_of_speech_file_mismatch_count": pos_file_mismatches,
        "relation_profiles": relation_profiles,
        "interpretation_limits": [
            "Lexicographer-file counts are inventory metadata, not a typed ontology or a sort-subsumption lattice.",
            "hypernym and instance_hypernym are profiled separately; neither is silently converted into Datalog sort declarations.",
            "The profile contains no definitions, examples, lemmas, synset IDs, or source paths.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="replace an existing output")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        profile = audit_type_inventory(args.release_dir, args.release_archive)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(profile, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(f"Verified {profile['synset_count']} synsets across {profile['lexicographer_file_count']} lexicographer files")
    print(f"Type inventory profile: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
