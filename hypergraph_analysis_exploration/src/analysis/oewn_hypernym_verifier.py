"""Verify synset-level hypernym claims against a pinned OEWN JSON release.

Positive results carry a shortest path of versioned ``hypernym`` edges. A
negative result means only that no path was found in this release's graph; it
is not a natural-language contradiction or an independent semantic judgment.
"""
from __future__ import annotations

import argparse
import hashlib
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


VERIFIER_VERSION = "oewn-hypernym-closure-verifier/2"
TRANSITIVITY_RULE_ID = "oewn_hypernym_transitivity/1"
TRANSITIVITY_RULE = {
    "rule_id": TRANSITIVITY_RULE_ID,
    "body": [
        {"predicate": "oewn_hypernym", "arguments": ["?x", "?y"]},
        {"predicate": "oewn_hypernym", "arguments": ["?y", "?z"]},
    ],
    "head": {"predicate": "oewn_hypernym", "arguments": ["?x", "?z"]},
}
RELEASE_NAME = "Open English WordNet 2025 Plus"
RELEASE_DATE = "2025-12-31"
POS_FILE_PREFIXES = ("noun.", "verb.", "adj.", "adv.")
POS_VALUES = {"n", "v", "a", "s", "r"}
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CLAIMS = PROJECT_ROOT / "config" / "hypernym_claims.example.jsonl"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase16" / "oewn_hypernym_verification.json"


def _taxonomy_file(path: str) -> bool:
    name = Path(path).name
    return name.endswith(".json") and name.startswith(POS_FILE_PREFIXES)


def _pos_family(pos: str) -> str:
    """Treat WordNet satellites as members of the adjective family."""
    return "a" if pos == "s" else pos


def verify_extracted_taxonomy(release_dir: Path, archive_path: Path) -> dict[str, Any]:
    """Byte-verify all POS synset files consumed by this verifier."""
    extracted = sorted(
        path for path in release_dir.iterdir()
        if path.is_file() and _taxonomy_file(path.name)
    )
    if not extracted:
        raise FileNotFoundError(f"no noun/verb/adj/adv synset JSON files found in {release_dir}")

    archive_hashes: dict[str, str] = {}
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.namelist():
            if not _taxonomy_file(member):
                continue
            basename = Path(member).name
            if basename in archive_hashes:
                raise ValueError(f"archive contains duplicate taxonomy basename: {basename}")
            digest = hashlib.sha256()
            with archive.open(member) as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            archive_hashes[basename] = digest.hexdigest()

    extracted_by_name = {path.name: path for path in extracted}
    if set(extracted_by_name) != set(archive_hashes):
        raise ValueError("extracted taxonomy file set does not match the pinned release archive")
    for name, path in extracted_by_name.items():
        if _sha256(path) != archive_hashes[name]:
            raise ValueError(f"extracted file differs from pinned release archive: {name}")

    combined = hashlib.sha256()
    for name in sorted(archive_hashes):
        combined.update(name.encode("utf-8"))
        combined.update(bytes.fromhex(archive_hashes[name]))
    return {
        "release_name": RELEASE_NAME,
        "release_date": RELEASE_DATE,
        "archive_sha256": _sha256(archive_path),
        "verified_file_count": len(extracted_by_name),
        "verified_file_set_sha256": combined.hexdigest(),
    }


def load_hypernym_graph(release_dir: Path) -> tuple[dict[str, dict[str, str]], dict[str, tuple[str, ...]]]:
    """Load all OEWN synsets and their direct child-to-parent hypernym edges."""
    paths = sorted(
        path for path in release_dir.iterdir()
        if path.is_file() and _taxonomy_file(path.name)
    )
    if not paths:
        raise FileNotFoundError(f"no noun/verb/adj/adv synset JSON files found in {release_dir}")

    nodes: dict[str, dict[str, str]] = {}
    parents_mutable: dict[str, set[str]] = {}
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"expected a JSON object in {path.name}")
        for synset_id, record in data.items():
            if not isinstance(synset_id, str) or not synset_id or not isinstance(record, dict):
                raise ValueError(f"invalid synset record in {path.name}")
            pos = record.get("partOfSpeech")
            if not isinstance(pos, str) or pos not in POS_VALUES:
                raise ValueError(f"invalid partOfSpeech for synset {synset_id}")
            if synset_id in nodes:
                raise ValueError(f"duplicate synset ID across release files: {synset_id}")
            hypernyms = record.get("hypernym", [])
            if not isinstance(hypernyms, list) or any(not isinstance(item, str) or not item for item in hypernyms):
                raise ValueError(f"invalid hypernym list for synset {synset_id}")
            if len(hypernyms) != len(set(hypernyms)):
                raise ValueError(f"duplicate direct hypernym for synset {synset_id}")
            nodes[synset_id] = {"pos": pos, "source_file": path.name}
            parents_mutable[synset_id] = set(hypernyms)

    for child_id, parent_ids in parents_mutable.items():
        for parent_id in parent_ids:
            if parent_id not in nodes:
                raise ValueError(f"hypernym endpoint {parent_id} for {child_id} is absent from release")
            if _pos_family(nodes[child_id]["pos"]) != _pos_family(nodes[parent_id]["pos"]):
                raise ValueError(f"cross-POS hypernym edge from {child_id} to {parent_id}")
    parents = {synset_id: tuple(sorted(values)) for synset_id, values in parents_mutable.items()}
    return nodes, parents


def _shortest_path(start: str, goal: str, parents: dict[str, tuple[str, ...]]) -> list[str] | None:
    """Return a deterministic shortest path through direct hypernym edges."""
    queue = deque([start])
    predecessor: dict[str, str | None] = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            cursor: str | None = current
            while cursor is not None:
                path.append(cursor)
                cursor = predecessor[cursor]
            return list(reversed(path))
        for parent_id in parents.get(current, ()):
            if parent_id not in predecessor:
                predecessor[parent_id] = current
                queue.append(parent_id)
    return None


def _logic_proof(path: list[dict[str, str]]) -> dict[str, Any]:
    """Expand a taxonomy path into direct facts and explicit transitivity steps."""
    steps = []
    for index, edge in enumerate(path):
        steps.append({
            "id": f"fact-{index}",
            "kind": "fact",
            "atom": {"predicate": "oewn_hypernym",
                     "arguments": [edge["child_synset_id"], edge["hypernym_synset_id"]]},
            "source_file": edge["source_file"],
        })
    root_step_id = "fact-0"
    for index in range(1, len(path)):
        previous_step_id = "fact-0" if index == 1 else f"derive-{index - 1}"
        root_step_id = f"derive-{index}"
        steps.append({
            "id": root_step_id,
            "kind": "rule_application",
            "rule_id": TRANSITIVITY_RULE_ID,
            "premises": [previous_step_id, f"fact-{index}"],
            "atom": {"predicate": "oewn_hypernym",
                     "arguments": [path[0]["child_synset_id"], path[index]["hypernym_synset_id"]]},
        })
    return {"rule": TRANSITIVITY_RULE, "steps": steps, "root_step_id": root_step_id}


def audit_hypernym_acyclicity(
    nodes: dict[str, dict[str, str]], parents: dict[str, tuple[str, ...]]
) -> dict[str, Any]:
    """Check whether the directed hypernym graph is acyclic via Kahn's algorithm."""
    indegree = {synset_id: 0 for synset_id in nodes}
    for parent_ids in parents.values():
        for parent_id in parent_ids:
            indegree[parent_id] += 1
    queue = deque(sorted(synset_id for synset_id, degree in indegree.items() if degree == 0))
    removed = 0
    while queue:
        child_id = queue.popleft()
        removed += 1
        for parent_id in parents.get(child_id, ()):
            indegree[parent_id] -= 1
            if indegree[parent_id] == 0:
                queue.append(parent_id)
    residual = len(nodes) - removed
    return {"acyclic": residual == 0, "unprocessed_node_count": residual}


def verify_hypernym_claim(
    child_id: str,
    ancestor_id: str,
    nodes: dict[str, dict[str, str]],
    parents: dict[str, tuple[str, ...]],
) -> dict[str, Any]:
    """Check one directed child-is-a-ancestor claim against the loaded release."""
    base = {"child_synset_id": child_id, "ancestor_synset_id": ancestor_id}
    if child_id not in nodes or ancestor_id not in nodes:
        missing = [sid for sid in (child_id, ancestor_id) if sid not in nodes]
        return {**base, "status": "unknown_missing_synset", "missing_synset_ids": missing,
                "proof_path": None, "logical_proof": None, "reverse_path": None}
    if _pos_family(nodes[child_id]["pos"]) != _pos_family(nodes[ancestor_id]["pos"]):
        return {**base, "status": "unsupported_cross_pos", "child_pos": nodes[child_id]["pos"],
                "ancestor_pos": nodes[ancestor_id]["pos"], "proof_path": None,
                "logical_proof": None, "reverse_path": None}
    if child_id == ancestor_id:
        return {**base, "status": "not_a_proper_hypernym", "child_pos": nodes[child_id]["pos"],
                "proof_path": None,
                "logical_proof": None, "reverse_path": None}

    path = _shortest_path(child_id, ancestor_id, parents)
    if path is not None:
        proof = [
            {"child_synset_id": left, "hypernym_synset_id": right,
             "source_file": nodes[left]["source_file"]}
            for left, right in zip(path, path[1:])
        ]
        return {**base, "status": "direct_hypernym" if len(proof) == 1 else "transitive_hypernym",
                "child_pos": nodes[child_id]["pos"], "proof_path": proof,
                "logical_proof": _logic_proof(proof), "reverse_path": None}

    reverse_nodes = _shortest_path(ancestor_id, child_id, parents)
    reverse_path = None
    if reverse_nodes is not None:
        reverse_path = [
            {"child_synset_id": left, "hypernym_synset_id": right,
             "source_file": nodes[left]["source_file"]}
            for left, right in zip(reverse_nodes, reverse_nodes[1:])
        ]
    return {**base, "status": "not_in_hypernym_closure", "child_pos": nodes[child_id]["pos"],
            "proof_path": None, "logical_proof": None, "reverse_path": reverse_path}


def verify_claim_batch(
    claims: list[dict[str, Any]],
    nodes: dict[str, dict[str, str]],
    parents: dict[str, tuple[str, ...]],
) -> dict[str, Any]:
    """Verify strict JSON claim rows and return aggregate counts plus proof paths."""
    if not claims:
        raise ValueError("claims file is empty")
    seen_ids: set[str] = set()
    results = []
    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            raise ValueError(f"claim line {index} must be a JSON object")
        claim_id = claim.get("claim_id")
        child_id = claim.get("child_synset_id")
        ancestor_id = claim.get("ancestor_synset_id")
        identifiers = (claim_id, child_id, ancestor_id)
        if not all(isinstance(value, str) and value.strip() for value in identifiers):
            raise ValueError(f"claim line {index} requires non-empty claim_id, child_synset_id, and ancestor_synset_id")
        if any(value != value.strip() for value in identifiers):
            raise ValueError(f"claim line {index} identifiers must not have surrounding whitespace")
        if set(claim) != {"claim_id", "child_synset_id", "ancestor_synset_id"}:
            raise ValueError(f"claim line {index} has unsupported fields")
        if claim_id in seen_ids:
            raise ValueError(f"duplicate claim_id: {claim_id}")
        seen_ids.add(claim_id)
        results.append({"claim_id": claim_id, **verify_hypernym_claim(child_id, ancestor_id, nodes, parents)})
    counts = Counter(row["status"] for row in results)
    return {"claim_count": len(results), "status_counts": dict(sorted(counts.items())), "results": results}


def load_claims(path: Path) -> list[dict[str, Any]]:
    claims = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                claims.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at line {line_number}: {exc.msg}") from exc
    return claims


def run(claims_path: Path, release_dir: Path, archive_path: Path) -> dict[str, Any]:
    input_verification = verify_extracted_taxonomy(release_dir, archive_path)
    nodes, parents = load_hypernym_graph(release_dir)
    batch = verify_claim_batch(load_claims(claims_path), nodes, parents)
    graph_audit = audit_hypernym_acyclicity(nodes, parents)
    return {
        "verifier_version": VERIFIER_VERSION,
        "method": "direct OEWN hypernym edges with directed breadth-first proof-path search",
        "inputs": {**input_verification, "claims_sha256": _sha256(claims_path),
                   "synset_count": len(nodes),
                   "direct_hypernym_edge_count": sum(len(edges) for edges in parents.values())},
        "taxonomy_graph_audit": graph_audit,
        **batch,
        "interpretation_limits": [
            "A positive result proves only that the directed relation is reachable in the pinned OEWN release; it is a resource-relative certificate, not an independent semantic judgment.",
            "not_in_hypernym_closure means no path was found in this release, not that natural-language entailment is false.",
            "logical_proof uses the declared transitivity axiom over direct OEWN hypernym facts; that axiom is an explicit proof assumption, not a gloss-derived rule.",
            "This verifier consumes explicit synset pairs; it does not parse glosses, select senses, infer new facts, or use NLI.",
            "Proof paths contain only synset IDs and release file names; they do not copy definition or example text.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("claims", nargs="?", type=Path, default=DEFAULT_CLAIMS,
                        help="JSONL rows with claim_id, child_synset_id, ancestor_synset_id")
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
    print(f"Verified {result['claim_count']} hypernym claim(s); statuses={result['status_counts']}")
    print(f"Taxonomy synsets={result['inputs']['synset_count']}; direct hypernym edges={result['inputs']['direct_hypernym_edge_count']}")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
