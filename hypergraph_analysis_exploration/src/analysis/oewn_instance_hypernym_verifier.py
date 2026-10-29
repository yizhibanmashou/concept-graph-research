"""Verify instance-to-class claims against a pinned OEWN JSON release.

Direct ``instance_hypernym`` facts are kept distinct from ordinary
``hypernym`` facts. A claim may additionally be lifted to an ancestor class
using the two declared rules below. Results are resource-relative certificates,
not independent judgments about gloss meaning or real-world membership.
"""
from __future__ import annotations

import argparse
import json
import zipfile
from collections import Counter, deque
from pathlib import Path
from typing import Any

from src.analysis.gloss_genus_baseline import (
    DEFAULT_RELEASE_ARCHIVE,
    DEFAULT_RELEASE_DIR,
    _sha256,
)
from src.analysis.oewn_hypernym_verifier import (
    POS_FILE_PREFIXES,
    POS_VALUES,
    _pos_family,
    verify_extracted_taxonomy,
)


VERIFIER_VERSION = "oewn-instance-hypernym-verifier/1"
INSTANCE_BASE_RULE_ID = "oewn_instance_hypernym_to_instance_of_class/1"
INSTANCE_LIFT_RULE_ID = "oewn_instance_of_class_hypernym_lifting/1"
INSTANCE_BASE_RULE = {
    "rule_id": INSTANCE_BASE_RULE_ID,
    "body": [{"predicate": "oewn_instance_hypernym", "arguments": ["?x", "?y"]}],
    "head": {"predicate": "oewn_instance_of_class", "arguments": ["?x", "?y"]},
}
INSTANCE_LIFT_RULE = {
    "rule_id": INSTANCE_LIFT_RULE_ID,
    "body": [
        {"predicate": "oewn_instance_of_class", "arguments": ["?x", "?y"]},
        {"predicate": "oewn_hypernym", "arguments": ["?y", "?z"]},
    ],
    "head": {"predicate": "oewn_instance_of_class", "arguments": ["?x", "?z"]},
}
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CLAIMS = PROJECT_ROOT / "config" / "instance_hypernym_claims.example.jsonl"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase76" / "oewn_instance_hypernym_verification.json"


def _taxonomy_file(path: Path) -> bool:
    return path.suffix == ".json" and path.name.startswith(POS_FILE_PREFIXES)


def load_instance_graph(
    release_dir: Path,
) -> tuple[dict[str, dict[str, str]], dict[str, tuple[str, ...]], dict[str, tuple[str, ...]]]:
    """Load separate direct instance-hypernym and ordinary hypernym edges."""
    paths = sorted(path for path in release_dir.iterdir() if path.is_file() and _taxonomy_file(path))
    if not paths:
        raise FileNotFoundError(f"no noun/verb/adj/adv synset JSON files found in {release_dir}")

    nodes: dict[str, dict[str, str]] = {}
    instance_parents_mutable: dict[str, set[str]] = {}
    class_parents_mutable: dict[str, set[str]] = {}
    for path in paths:
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, dict):
            raise ValueError(f"expected a JSON object in {path.name}")
        for synset_id, record in records.items():
            if not isinstance(synset_id, str) or not synset_id or not isinstance(record, dict):
                raise ValueError(f"invalid synset record in {path.name}")
            pos = record.get("partOfSpeech")
            if not isinstance(pos, str) or pos not in POS_VALUES:
                raise ValueError(f"invalid partOfSpeech for synset {synset_id}")
            if synset_id in nodes:
                raise ValueError(f"duplicate synset ID across release files: {synset_id}")
            relations: dict[str, list[str]] = {}
            for key in ("hypernym", "instance_hypernym"):
                edges = record.get(key, [])
                if not isinstance(edges, list) or any(not isinstance(item, str) or not item for item in edges):
                    raise ValueError(f"invalid {key} list for synset {synset_id}")
                if len(edges) != len(set(edges)):
                    raise ValueError(f"duplicate direct {key} edge for synset {synset_id}")
                relations[key] = edges
            nodes[synset_id] = {"pos": pos, "source_file": path.name}
            instance_parents_mutable[synset_id] = set(relations["instance_hypernym"])
            class_parents_mutable[synset_id] = set(relations["hypernym"])

    for relation, graph in (("instance_hypernym", instance_parents_mutable),
                            ("hypernym", class_parents_mutable)):
        for child_id, parent_ids in graph.items():
            for parent_id in parent_ids:
                if parent_id not in nodes:
                    raise ValueError(f"{relation} endpoint {parent_id} for {child_id} is absent from release")
                if _pos_family(nodes[child_id]["pos"]) != _pos_family(nodes[parent_id]["pos"]):
                    raise ValueError(f"cross-POS {relation} edge from {child_id} to {parent_id}")

    return (
        nodes,
        {sid: tuple(sorted(edges)) for sid, edges in instance_parents_mutable.items()},
        {sid: tuple(sorted(edges)) for sid, edges in class_parents_mutable.items()},
    )


def _shortest_path(start: str, goal: str, parents: dict[str, tuple[str, ...]]) -> list[str] | None:
    queue = deque([start])
    predecessor: dict[str, str | None] = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            path: list[str] = []
            cursor: str | None = current
            while cursor is not None:
                path.append(cursor)
                cursor = predecessor[cursor]
            return list(reversed(path))
        for parent in parents.get(current, ()):
            if parent not in predecessor:
                predecessor[parent] = current
                queue.append(parent)
    return None


def verify_instance_claim(
    instance_id: str,
    class_id: str,
    nodes: dict[str, dict[str, str]],
    instance_parents: dict[str, tuple[str, ...]],
    class_parents: dict[str, tuple[str, ...]],
) -> dict[str, Any]:
    """Verify direct instance membership or membership lifted to an ancestor class."""
    base = {"instance_synset_id": instance_id, "class_synset_id": class_id}
    missing = [sid for sid in (instance_id, class_id) if sid not in nodes]
    if missing:
        return {**base, "status": "unknown_missing_synset", "missing_synset_ids": missing,
                "proof_path": None, "logical_proof": None}
    if _pos_family(nodes[instance_id]["pos"]) != _pos_family(nodes[class_id]["pos"]):
        return {**base, "status": "unsupported_cross_pos", "proof_path": None, "logical_proof": None}
    if instance_id == class_id:
        return {**base, "status": "not_a_proper_instance_class_pair", "proof_path": None,
                "logical_proof": None}

    for direct_class in instance_parents.get(instance_id, ()):
        class_path = _shortest_path(direct_class, class_id, class_parents)
        if class_path is None:
            continue
        edge_path = [{
            "relation": "instance_hypernym",
            "child_synset_id": instance_id,
            "parent_synset_id": direct_class,
            "source_file": nodes[instance_id]["source_file"],
        }]
        edge_path.extend({
            "relation": "hypernym",
            "child_synset_id": child,
            "parent_synset_id": parent,
            "source_file": nodes[child]["source_file"],
        } for child, parent in zip(class_path, class_path[1:]))
        steps: list[dict[str, Any]] = [{
            "id": "fact-instance-0", "kind": "fact",
            "atom": {"predicate": "oewn_instance_hypernym", "arguments": [instance_id, direct_class]},
            "source_file": nodes[instance_id]["source_file"],
        }]
        root_id = "derive-instance-of-class"
        steps.append({
            "id": root_id, "kind": "rule_application", "rule_id": INSTANCE_BASE_RULE_ID,
            "premises": ["fact-instance-0"],
            "atom": {"predicate": "oewn_instance_of_class", "arguments": [instance_id, direct_class]},
        })
        previous_id = root_id
        for index, (_, parent) in enumerate(zip(class_path, class_path[1:])):
            fact_id = f"fact-hypernym-{index}"
            class_child = class_path[index]
            steps.append({
                "id": fact_id, "kind": "fact",
                "atom": {"predicate": "oewn_hypernym", "arguments": [class_child, parent]},
                "source_file": nodes[class_child]["source_file"],
            })
            derived_id = f"derive-instance-ancestor-{index}"
            steps.append({
                "id": derived_id, "kind": "rule_application", "rule_id": INSTANCE_LIFT_RULE_ID,
                "premises": [previous_id, fact_id],
                "atom": {"predicate": "oewn_instance_of_class", "arguments": [instance_id, parent]},
            })
            previous_id = derived_id
        return {
            **base,
            "status": "direct_instance_membership" if len(class_path) == 1 else "lifted_instance_class_membership",
            "proof_path": edge_path,
            "logical_proof": {"rules": [INSTANCE_BASE_RULE, INSTANCE_LIFT_RULE],
                              "steps": steps, "root_step_id": previous_id},
        }
    return {**base, "status": "not_in_instance_class_closure", "proof_path": None, "logical_proof": None}


def verify_claim_batch(
    claims: list[dict[str, Any]], nodes: dict[str, dict[str, str]],
    instance_parents: dict[str, tuple[str, ...]], class_parents: dict[str, tuple[str, ...]],
) -> dict[str, Any]:
    if not claims:
        raise ValueError("claims file is empty")
    seen: set[str] = set()
    results = []
    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            raise ValueError(f"claim line {index} must be a JSON object")
        values = (claim.get("claim_id"), claim.get("instance_synset_id"), claim.get("class_synset_id"))
        if not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError(f"claim line {index} requires non-empty claim_id, instance_synset_id, and class_synset_id")
        if any(value != value.strip() for value in values):
            raise ValueError(f"claim line {index} identifiers must not have surrounding whitespace")
        if set(claim) != {"claim_id", "instance_synset_id", "class_synset_id"}:
            raise ValueError(f"claim line {index} has unsupported fields")
        claim_id = values[0]
        if claim_id in seen:
            raise ValueError(f"duplicate claim_id: {claim_id}")
        seen.add(claim_id)
        results.append({"claim_id": claim_id, **verify_instance_claim(values[1], values[2], nodes,
                                                                       instance_parents, class_parents)})
    counts = Counter(row["status"] for row in results)
    return {"claim_count": len(results), "status_counts": dict(sorted(counts.items())), "results": results}


def _load_claims(path: Path) -> list[dict[str, Any]]:
    claims = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if line.strip():
                try:
                    claims.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSON at line {line_number}: {exc.msg}") from exc
    return claims


def run(claims_path: Path, release_dir: Path, archive_path: Path) -> dict[str, Any]:
    input_verification = verify_extracted_taxonomy(release_dir, archive_path)
    nodes, instance_parents, class_parents = load_instance_graph(release_dir)
    batch = verify_claim_batch(_load_claims(claims_path), nodes, instance_parents, class_parents)
    return {
        "verifier_version": VERIFIER_VERSION,
        "method": "direct instance_hypernym facts, optionally lifted over the separate class hypernym hierarchy",
        "inputs": {**input_verification, "claims_sha256": _sha256(claims_path),
                   "synset_count": len(nodes),
                   "direct_instance_hypernym_edge_count": sum(map(len, instance_parents.values())),
                   "direct_class_hypernym_edge_count": sum(map(len, class_parents.values()))},
        **batch,
        "interpretation_limits": [
            "A positive result is a resource-relative OEWN certificate, not an independent judgment of gloss entailment or real-world membership.",
            "instance_hypernym is treated only as a direct instance-to-class fact; it is not assumed transitive.",
            "Lifted results use the explicit bridge and class-hypernym lifting rules included in each logical proof.",
            "not_in_instance_class_closure means no supported path was found in this finite release graph; it is not a semantic negative.",
            "The verifier takes explicit synset pairs and does not perform word-sense disambiguation, gloss parsing, or NLI.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("claims", nargs="?", type=Path, default=DEFAULT_CLAIMS)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        result = run(args.claims, args.release_dir, args.release_archive)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))
    print(f"Verified {result['claim_count']} instance-hypernym claim(s); statuses={result['status_counts']}")
    print(f"Taxonomy synsets={result['inputs']['synset_count']}; direct instance edges={result['inputs']['direct_instance_hypernym_edge_count']}")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
