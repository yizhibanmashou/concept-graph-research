"""Aggregate-only audit of prep deletion over the eligible OEWN target frame.

The audit connects frozen graph effects to raw/effective definitions in the
pinned OEWN 2025 Plus release. Output contains aggregate counts and hashes
only; it never writes target IDs, lemmas, glosses, or annotation labels.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from .oewn_release_crosscheck import _load_release_definitions, _sha256
    from .project_paths import configured_bundle_root
except ImportError:
    from oewn_release_crosscheck import _load_release_definitions, _sha256
    from project_paths import configured_bundle_root

PINNED_RELEASE = "Open English WordNet 2025 Plus"
PINNED_ARCHIVE_SHA256 = "8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e"
TARGET_POS = {"n", "v", "a", "r"}


def _load_jsonl(path: Path):
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"JSONL row {number} is not an object")
                yield row


def _load_graph(bundle: Path):
    nodes_path = bundle / "graph" / "nodes.tsv"
    rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
    pos: dict[str, str] = {}
    definitions: dict[str, str] = {}
    with nodes_path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            sid = row.get("synset_id", "")
            if sid:
                if sid in pos:
                    raise ValueError("duplicate graph node identity")
                pos[sid] = row.get("pos", "")
                definitions[sid] = row.get("definition", "")
    rules: dict[str, list[list[str]]] = {}
    for row in _load_jsonl(rules_path):
        head, clauses = row.get("head"), row.get("clauses")
        if not isinstance(head, str) or not isinstance(clauses, list) or head in rules:
            raise ValueError("malformed or duplicate graph rule")
        if any(not isinstance(c, list) or not c or any(not isinstance(x, str) for x in c) for c in clauses):
            raise ValueError("source rule contains an empty or malformed branch")
        rules[head] = clauses
    eligible = {
        sid for sid, p in pos.items()
        if sid.startswith("oewn-") and p in TARGET_POS and definitions.get(sid)
    }
    missing = eligible - rules.keys()
    if missing:
        raise ValueError("eligible OEWN target is missing a graph rule")
    return pos, rules, eligible, nodes_path, rules_path


def _load_expected_checksums(bundle: Path) -> dict[str, tuple[int, str]]:
    checksums = {}
    for row in _load_jsonl(bundle / "checksums.jsonl"):
        path, size, digest = row.get("path"), row.get("bytes"), row.get("sha256")
        if isinstance(path, str) and isinstance(size, int) and isinstance(digest, str):
            checksums[path] = (size, digest)
    return checksums


def _impact(clauses: list[list[str]], pos: dict[str, str], removed_pos: set[str]) -> dict[str, int]:
    before = Counter(tuple(c) for c in clauses)
    after: list[tuple[str, ...]] = []
    out = Counter(source_branches=len(clauses))
    for clause in clauses:
        removed = [node for node in clause if pos.get(node) in removed_pos]
        kept = tuple(node for node in clause if pos.get(node) not in removed_pos)
        out["removed_occurrences"] += len(removed)
        out["changed_branches"] += bool(removed)
        out["new_empty_branches"] += bool(removed) and not kept
        after.append(kept)
    after_nonempty = Counter(branch for branch in after if branch)
    before_nonempty = Counter(before)
    before_nonempty.pop((), None)
    before_collision_excess = sum(count - 1 for count in before_nonempty.values() if count > 1)
    after_collision_excess = sum(count - 1 for count in after_nonempty.values() if count > 1)
    out["new_collision_excess"] = max(0, after_collision_excess - before_collision_excess)
    out["new_nonempty_collision_target"] = after_collision_excess > before_collision_excess
    out["affected_target"] = out["removed_occurrences"] > 0
    return dict(out)


def run(bundle: Path, release_dir: Path, release_archive: Path) -> dict[str, Any]:
    bundle, release_dir = bundle.resolve(), release_dir.resolve()
    archive_sha = _sha256(release_archive)
    if archive_sha != PINNED_ARCHIVE_SHA256:
        raise ValueError("local OEWN 2025 Plus archive does not match pinned SHA-256")
    official = _load_release_definitions(release_dir)
    pos, rules, eligible, nodes_path, rules_path = _load_graph(bundle)
    index_path = bundle / "indexes" / "senses.jsonl"
    checksums = _load_expected_checksums(bundle)

    seen: set[str] = set()
    raw_status = Counter()
    effective_status = Counter()
    raw_by_pos: dict[str, Counter[str]] = {p: Counter() for p in sorted(TARGET_POS)}
    effective_by_pos: dict[str, Counter[str]] = {p: Counter() for p in sorted(TARGET_POS)}
    impacts = {
        "prep_primary": Counter(),
        "prep_phrase_sensitivity": Counter(),
    }
    impact_by_effective: dict[str, Counter[str]] = {
        "exact_match": Counter(), "different_nonempty": Counter(), "blank_or_missing": Counter()
    }
    payload_files_verified: set[str] = set()

    for row in _load_jsonl(index_path):
        target = row.get("identity")
        if target not in eligible:
            continue
        if target in seen:
            raise ValueError("duplicate eligible identity in senses index")
        seen.add(target)
        records = row.get("source_records")
        if not isinstance(records, list) or not records:
            raise ValueError("eligible target lacks source records")
        release_defs = official.get(target.removeprefix("oewn-"), set())
        raw_exact = False
        effective_exact = False
        effective_nonblank = False
        raw_present = False
        for source in records:
            if not isinstance(source, dict) or source.get("identity") != target:
                continue
            relative = source.get("path")
            if not isinstance(relative, str):
                raise ValueError("source record has an invalid path")
            relpath = PurePosixPath(relative)
            if relpath.is_absolute() or ".." in relpath.parts:
                raise ValueError("unsafe source path in index")
            payload_path = bundle.joinpath(*relpath.parts).resolve()
            if not payload_path.is_relative_to(bundle) or not payload_path.is_file():
                raise ValueError("source payload is missing or outside bundle")
            expected = checksums.get(relative)
            if expected is None:
                raise ValueError("source payload has no bundle checksum entry")
            if relative not in payload_files_verified:
                if payload_path.stat().st_size != expected[0] or _sha256(payload_path) != expected[1]:
                    raise ValueError("source payload checksum mismatch")
                payload_files_verified.add(relative)
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            synset = payload.get("synset") if isinstance(payload, dict) else None
            if not isinstance(synset, dict) or synset.get("synset_id") != target:
                raise ValueError("payload identity does not match the indexed OEWN target")
            raw = synset.get("raw_definition")
            definition = payload.get("definition")
            effective = definition.get("definition") if isinstance(definition, dict) else None
            if isinstance(raw, str):
                raw_present = True
                raw_exact |= raw in release_defs
            if isinstance(effective, str) and effective.strip():
                effective_nonblank = True
                effective_exact |= effective in release_defs

        pos_tag = pos[target]
        raw_group = "exact_match" if raw_exact else "unmatched_or_missing"
        effective_group = (
            "exact_match" if effective_exact else
            "different_nonempty" if effective_nonblank else "blank_or_missing"
        )
        raw_status[raw_group] += 1
        effective_status[effective_group] += 1
        raw_by_pos[pos_tag][raw_group] += 1
        effective_by_pos[pos_tag][effective_group] += 1

        clauses = rules[target]
        impacts["prep_primary"].update(_impact(clauses, pos, {"prep"}))
        impacts["prep_phrase_sensitivity"].update(_impact(clauses, pos, {"prep", "prep_phrase"}))
        impact_by_effective[effective_group].update(_impact(clauses, pos, {"prep"}))

    if seen != eligible:
        raise ValueError(f"eligible index coverage mismatch: {len(eligible - seen)} targets missing")
    return {
        "schema_version": "t02-full-oewn-prep-overlap/1",
        "release": PINNED_RELEASE,
        "release_archive_sha256": archive_sha,
        "bundle_graph_sha256": {"nodes.tsv": _sha256(nodes_path), "hypergraph_rules.jsonl": _sha256(rules_path)},
        "bundle_index_sha256": _sha256(index_path),
        "bundle_checksums_sha256": _sha256(bundle / "checksums.jsonl"),
        "population": {
            "eligible_oewn_targets": len(eligible),
            "eligible_identity_index_rows": len(seen),
            "unique_source_payloads_verified": len(payload_files_verified),
        },
        "raw_definition_release_match": dict(raw_status),
        "raw_definition_release_match_by_pos": {k: dict(v) for k, v in raw_by_pos.items()},
        "effective_definition_release_match": dict(effective_status),
        "effective_definition_release_match_by_pos": {k: dict(v) for k, v in effective_by_pos.items()},
        "prep_primary_structure_effect": dict(impacts["prep_primary"]),
        "prep_phrase_sensitivity_structure_effect": dict(impacts["prep_phrase_sensitivity"]),
        "prep_primary_by_effective_match": {k: dict(v) for k, v in impact_by_effective.items()},
        "limits": (
            "Finite-population structural and exact-string provenance audit only. Exact string presence "
            "does not establish source rights, source-family independence, semantic fidelity, or annotation "
            "eligibility. No target identifiers, lemmas, glosses, annotations, or labels are emitted."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=configured_bundle_root())
    parser.add_argument("--release-dir", type=Path, default=Path(__file__).resolve().parents[2] / "tmp" / "oewn-2025-plus-json")
    parser.add_argument("--release-archive", type=Path, default=Path(__file__).resolve().parents[2] / "tmp" / "oewn-2025-plus-json.zip")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.bundle, args.release_dir, args.release_archive)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
