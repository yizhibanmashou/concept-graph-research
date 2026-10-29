"""Independently replay OEWN instance-to-class certificates against a pinned release."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.gloss_genus_baseline import DEFAULT_RELEASE_ARCHIVE, DEFAULT_RELEASE_DIR, _sha256
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


REPLAY_VERSION = "oewn-instance-hypernym-certificate-replay/1"
EXPECTED_PRODUCER_VERSION = "oewn-instance-hypernym-verifier/1"
DEFAULT_CLAIMS = _PROJECT_ROOT / "config" / "instance_hypernym_claims.example.jsonl"
DEFAULT_REPORT = _PROJECT_ROOT / "outputs" / "phase76" / "oewn_instance_hypernym_verification.json"
POS_VALUES = {"n", "v", "a", "s", "r"}
POS_FILE_PREFIXES = ("noun.", "verb.", "adj.", "adv.")
RELEASE_NAME = "Open English WordNet 2025 Plus"
RELEASE_DATE = "2025-12-31"
EXPECTED_BASE_RULE = {
    "rule_id": "oewn_instance_hypernym_to_instance_of_class/1",
    "body": [{"predicate": "oewn_instance_hypernym", "arguments": ["?x", "?y"]}],
    "head": {"predicate": "oewn_instance_of_class", "arguments": ["?x", "?y"]},
}
EXPECTED_LIFT_RULE = {
    "rule_id": "oewn_instance_of_class_hypernym_lifting/1",
    "body": [
        {"predicate": "oewn_instance_of_class", "arguments": ["?x", "?y"]},
        {"predicate": "oewn_hypernym", "arguments": ["?y", "?z"]},
    ],
    "head": {"predicate": "oewn_instance_of_class", "arguments": ["?x", "?z"]},
}


def _pos_family(pos: str) -> str:
    return "a" if pos == "s" else pos


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_archive_bytes_independently(release_dir: Path, archive_path: Path) -> dict[str, Any]:
    """Recompute archive/extracted file correspondence without producer helpers."""
    extracted = sorted(path for path in release_dir.iterdir()
                       if path.is_file() and path.suffix == ".json"
                       and path.name.startswith(POS_FILE_PREFIXES))
    if not extracted:
        raise FileNotFoundError(f"no noun/verb/adj/adv synset JSON files found in {release_dir}")
    archive_hashes: dict[str, str] = {}
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.namelist():
            basename = Path(member).name
            if not (basename.endswith(".json") and basename.startswith(POS_FILE_PREFIXES)):
                continue
            if basename in archive_hashes:
                raise ValueError(f"archive contains duplicate taxonomy basename: {basename}")
            digest = hashlib.sha256()
            with archive.open(member) as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            archive_hashes[basename] = digest.hexdigest()
    extracted_by_name = {path.name: path for path in extracted}
    if set(extracted_by_name) != set(archive_hashes):
        raise ValueError("extracted taxonomy file set does not match pinned release archive")
    for name, path in extracted_by_name.items():
        if _sha256_file(path) != archive_hashes[name]:
            raise ValueError(f"extracted file differs from pinned release archive: {name}")
    combined = hashlib.sha256()
    for name in sorted(archive_hashes):
        combined.update(name.encode("utf-8"))
        combined.update(bytes.fromhex(archive_hashes[name]))
    return {
        "release_name": RELEASE_NAME,
        "release_date": RELEASE_DATE,
        "archive_sha256": _sha256_file(archive_path),
        "verified_file_count": len(extracted_by_name),
        "verified_file_set_sha256": combined.hexdigest(),
    }


def _load_graph_independently(
    release_dir: Path,
) -> tuple[dict[str, dict[str, str]], dict[str, tuple[str, ...]], dict[str, tuple[str, ...]]]:
    """Parse release JSON directly; do not call the producer graph loader."""
    paths = sorted(path for path in release_dir.iterdir()
                   if path.is_file() and path.suffix == ".json" and path.name.startswith(POS_FILE_PREFIXES))
    if not paths:
        raise FileNotFoundError(f"no noun/verb/adj/adv synset JSON files found in {release_dir}")
    nodes: dict[str, dict[str, str]] = {}
    instance_edges: dict[str, set[str]] = {}
    class_edges: dict[str, set[str]] = {}
    for path in paths:
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, dict):
            raise ValueError(f"expected a JSON object in {path.name}")
        for synset_id, record in rows.items():
            if not isinstance(synset_id, str) or not synset_id or not isinstance(record, dict):
                raise ValueError(f"invalid synset record in {path.name}")
            pos = record.get("partOfSpeech")
            if not isinstance(pos, str) or pos not in POS_VALUES:
                raise ValueError(f"invalid partOfSpeech for synset {synset_id}")
            if synset_id in nodes:
                raise ValueError(f"duplicate synset ID across release files: {synset_id}")
            nodes[synset_id] = {"pos": pos, "source_file": path.name}
            for field, graph in (("instance_hypernym", instance_edges), ("hypernym", class_edges)):
                values = record.get(field, [])
                if (not isinstance(values, list)
                        or any(not isinstance(value, str) or not value for value in values)):
                    raise ValueError(f"invalid {field} list for synset {synset_id}")
                if len(set(values)) != len(values):
                    raise ValueError(f"duplicate {field} edge for synset {synset_id}")
                graph[synset_id] = set(values)
    for relation, graph in (("instance_hypernym", instance_edges), ("hypernym", class_edges)):
        for child, parents in graph.items():
            for parent in parents:
                if parent not in nodes:
                    raise ValueError(f"{relation} endpoint {parent} for {child} is absent from release")
                if _pos_family(nodes[child]["pos"]) != _pos_family(nodes[parent]["pos"]):
                    raise ValueError(f"cross-POS {relation} edge from {child} to {parent}")
    return (
        nodes,
        {child: tuple(sorted(parents)) for child, parents in instance_edges.items()},
        {child: tuple(sorted(parents)) for child, parents in class_edges.items()},
    )


def _load_claim_rows_independently(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for number, line in enumerate(stream, start=1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSON at line {number}: {exc.msg}") from exc
    return rows


def _reachable(start: str, goal: str, parents: dict[str, tuple[str, ...]]) -> bool:
    """Iterative DFS, separate from the producer's breadth-first path search."""
    pending = [start]
    seen: set[str] = set()
    while pending:
        current = pending.pop()
        if current == goal:
            return True
        if current not in seen:
            seen.add(current)
            pending.extend(parents.get(current, ()))
    return False


def _valid_instance_closure(
    instance_id: str, class_id: str,
    instance_parents: dict[str, tuple[str, ...]],
    class_parents: dict[str, tuple[str, ...]],
) -> bool:
    return any(_reachable(direct_class, class_id, class_parents)
               for direct_class in instance_parents.get(instance_id, ()))


def _path_errors(
    path: Any, instance_id: str, class_id: str,
    nodes: dict[str, dict[str, str]],
    instance_parents: dict[str, tuple[str, ...]],
    class_parents: dict[str, tuple[str, ...]],
    where: str,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(path, list) or not path:
        return [f"{where} must be a non-empty edge list"]
    current = instance_id
    direct_class: str | None = None
    visited = {instance_id}
    for index, edge in enumerate(path):
        label = f"{where}[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"{label} must be an object")
            continue
        child = edge.get("child_synset_id")
        parent = edge.get("parent_synset_id")
        relation = edge.get("relation")
        if child != current:
            errors.append(f"{label} breaks path direction/continuity")
        if not isinstance(child, str) or not isinstance(parent, str):
            errors.append(f"{label} must contain child and parent synset IDs")
            continue
        if child not in nodes or parent not in nodes:
            errors.append(f"{label} references a synset absent from the pinned release")
            continue
        if index == 0:
            if relation != "instance_hypernym":
                errors.append(f"{label} must be the direct instance_hypernym fact")
            if parent not in instance_parents.get(child, ()):
                errors.append(f"{label} is not a direct instance_hypernym edge in the pinned release")
            direct_class = parent
        else:
            if relation != "hypernym":
                errors.append(f"{label} must use the separate class hypernym relation")
            if parent not in class_parents.get(child, ()):
                errors.append(f"{label} is not a direct class hypernym edge in the pinned release")
        if edge.get("source_file") != nodes[child]["source_file"]:
            errors.append(f"{label} source_file does not match the release record for its child")
        if nodes[child]["pos"] != nodes[parent]["pos"] and {nodes[child]["pos"], nodes[parent]["pos"]} != {"a", "s"}:
            errors.append(f"{label} crosses POS families")
        current = parent
        if current in visited and index < len(path) - 1:
            errors.append(f"{where} repeats a synset before reaching its endpoint")
        visited.add(current)
    if isinstance(path[0], dict) and path[0].get("child_synset_id") != instance_id:
        errors.append(f"{where} does not begin at the claimed instance")
    if current != class_id:
        errors.append(f"{where} ends at {current!r}, expected {class_id!r}")
    if len(path) > 1 and isinstance(path[1], dict) and path[1].get("child_synset_id") != direct_class:
        errors.append(f"{where} class path does not begin at the instance's direct class")
    return errors


def _expected_logic(path: list[dict[str, Any]]) -> dict[str, Any]:
    """Construct the ground proof expected from a checked mixed-relation path."""
    instance_fact = path[0]
    instance_id = instance_fact["child_synset_id"]
    direct_class = instance_fact["parent_synset_id"]
    steps: list[dict[str, Any]] = [{
        "id": "fact-instance-0", "kind": "fact",
        "atom": {"predicate": "oewn_instance_hypernym", "arguments": [instance_id, direct_class]},
        "source_file": instance_fact["source_file"],
    }, {
        "id": "derive-instance-of-class", "kind": "rule_application",
        "rule_id": EXPECTED_BASE_RULE["rule_id"], "premises": ["fact-instance-0"],
        "atom": {"predicate": "oewn_instance_of_class", "arguments": [instance_id, direct_class]},
    }]
    previous = "derive-instance-of-class"
    for index, edge in enumerate(path[1:]):
        fact_id = f"fact-hypernym-{index}"
        steps.append({
            "id": fact_id, "kind": "fact",
            "atom": {"predicate": "oewn_hypernym",
                     "arguments": [edge["child_synset_id"], edge["parent_synset_id"]]},
            "source_file": edge["source_file"],
        })
        derived_id = f"derive-instance-ancestor-{index}"
        steps.append({
            "id": derived_id, "kind": "rule_application", "rule_id": EXPECTED_LIFT_RULE["rule_id"],
            "premises": [previous, fact_id],
            "atom": {"predicate": "oewn_instance_of_class", "arguments": [instance_id, edge["parent_synset_id"]]},
        })
        previous = derived_id
    return {"rules": [EXPECTED_BASE_RULE, EXPECTED_LIFT_RULE], "steps": steps, "root_step_id": previous}


def _validate_claim_rows(claims: list[dict[str, Any]]) -> tuple[dict[str, dict[str, str]], list[str]]:
    by_id: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claims[{index}] must be an object")
            continue
        if set(claim) != {"claim_id", "instance_synset_id", "class_synset_id"}:
            errors.append(f"claims[{index}] has malformed or unsupported fields")
            continue
        values = (claim.get("claim_id"), claim.get("instance_synset_id"), claim.get("class_synset_id"))
        if any(not isinstance(value, str) or not value.strip() or value != value.strip() for value in values):
            errors.append(f"claims[{index}] has malformed identifiers")
            continue
        claim_id = values[0]
        if claim_id in by_id:
            errors.append(f"claims contains duplicate claim_id {claim_id!r}")
            continue
        by_id[claim_id] = {"instance_synset_id": values[1], "class_synset_id": values[2]}
    if not claims:
        errors.append("claims input is empty")
    return by_id, errors


def verify_report(
    report: Any,
    claims: list[dict[str, Any]],
    taxonomy_manifest: dict[str, Any],
    nodes: dict[str, dict[str, str]],
    instance_parents: dict[str, tuple[str, ...]],
    class_parents: dict[str, tuple[str, ...]],
    claims_sha256: str,
) -> dict[str, Any]:
    """Check every emitted certificate/status against release facts and rule schema."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"replay_version": REPLAY_VERSION, "valid": False, "errors": ["report must be an object"]}
    if report.get("verifier_version") != EXPECTED_PRODUCER_VERSION:
        errors.append("unsupported producer verifier_version")
    inputs = report.get("inputs")
    if not isinstance(inputs, dict):
        inputs = {}
        errors.append("report inputs must be an object")
    for key, expected in taxonomy_manifest.items():
        if inputs.get(key) != expected:
            errors.append(f"report input {key} does not match the verified OEWN release")
    if inputs.get("claims_sha256") != claims_sha256:
        errors.append("report claims_sha256 does not match supplied claims")
    expected_graph = {
        "synset_count": len(nodes),
        "direct_instance_hypernym_edge_count": sum(map(len, instance_parents.values())),
        "direct_class_hypernym_edge_count": sum(map(len, class_parents.values())),
    }
    for key, expected in expected_graph.items():
        if inputs.get(key) != expected:
            errors.append(f"report input {key} does not match the loaded graph")

    claims_by_id, claim_errors = _validate_claim_rows(claims)
    errors.extend(claim_errors)
    results = report.get("results")
    if not isinstance(results, list):
        errors.append("report results must be a list")
        results = []
    if type(report.get("claim_count")) is not int or report.get("claim_count") != len(claims_by_id):
        errors.append("claim_count does not match supplied claims")
    if len(results) != len(claims_by_id):
        errors.append("result count does not match supplied claims")

    result_ids: set[str] = set()
    observed_counts: Counter[str] = Counter()
    replayed_positive = 0
    for index, row in enumerate(results):
        where = f"results[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{where} must be an object")
            continue
        claim_id = row.get("claim_id")
        if not isinstance(claim_id, str) or claim_id in result_ids:
            errors.append(f"{where} has missing or duplicate claim_id")
            continue
        result_ids.add(claim_id)
        claim = claims_by_id.get(claim_id)
        if claim is None:
            errors.append(f"{where} does not correspond to a supplied claim")
            continue
        instance_id, class_id = claim["instance_synset_id"], claim["class_synset_id"]
        if row.get("instance_synset_id") != instance_id or row.get("class_synset_id") != class_id:
            errors.append(f"{where} endpoints do not match supplied claim")
        status = row.get("status")
        if not isinstance(status, str):
            errors.append(f"{where}.status must be a string")
            continue
        observed_counts[status] += 1

        missing = [sid for sid in (instance_id, class_id) if sid not in nodes]
        if missing:
            if (status != "unknown_missing_synset" or row.get("missing_synset_ids") != missing
                    or row.get("proof_path") is not None or row.get("logical_proof") is not None):
                errors.append(f"{where} missing-synset result is inconsistent")
            continue
        cross_pos = (nodes[instance_id]["pos"] != nodes[class_id]["pos"]
                     and {nodes[instance_id]["pos"], nodes[class_id]["pos"]} != {"a", "s"})
        if cross_pos:
            if status != "unsupported_cross_pos" or row.get("proof_path") is not None or row.get("logical_proof") is not None:
                errors.append(f"{where} cross-POS result is inconsistent")
            continue
        if instance_id == class_id:
            if (status != "not_a_proper_instance_class_pair" or row.get("proof_path") is not None
                    or row.get("logical_proof") is not None):
                errors.append(f"{where} self-pair result is inconsistent")
            continue

        path = row.get("proof_path")
        proof = row.get("logical_proof")
        if status in {"direct_instance_membership", "lifted_instance_class_membership"}:
            errors.extend(_path_errors(path, instance_id, class_id, nodes, instance_parents,
                                       class_parents, f"{where}.proof_path"))
            if isinstance(path, list) and path and all(isinstance(edge, dict) for edge in path):
                replayed_positive += 1
                expected_status = "direct_instance_membership" if len(path) == 1 else "lifted_instance_class_membership"
                if status != expected_status:
                    errors.append(f"{where} status does not agree with relation path shape")
                if not _valid_instance_closure(instance_id, class_id, instance_parents, class_parents):
                    errors.append(f"{where} certificate is not supported by the release closure")
                expected_proof = _expected_logic(path)
                if proof != expected_proof:
                    errors.append(f"{where}.logical_proof does not replay under the declared rules")
                if proof is not None and (proof.get("root_step_id") != expected_proof["root_step_id"]
                                          if isinstance(proof, dict) else True):
                    errors.append(f"{where}.logical_proof root does not identify the conclusion")
                if isinstance(proof, dict) and proof.get("rules") != [EXPECTED_BASE_RULE, EXPECTED_LIFT_RULE]:
                    errors.append(f"{where}.logical_proof rule declarations are altered")
            elif proof is not None:
                errors.append(f"{where} malformed positive path must not carry a trusted proof")
        elif status == "not_in_instance_class_closure":
            if path is not None or proof is not None:
                errors.append(f"{where} negative result must not carry positive proof material")
            if _valid_instance_closure(instance_id, class_id, instance_parents, class_parents):
                errors.append(f"{where} claims non-reachability but a supported path exists")
        else:
            errors.append(f"{where} has unsupported status for present synsets: {status}")

    if result_ids != set(claims_by_id):
        errors.append("results do not cover every supplied claim exactly once")
    if report.get("status_counts") != dict(sorted(observed_counts.items())):
        errors.append("status_counts do not match result rows")
    return {
        "replay_version": REPLAY_VERSION,
        "valid": not errors,
        "claim_count": len(claims_by_id),
        "replayed_positive_certificates": replayed_positive,
        "status_counts": dict(sorted(observed_counts.items())),
        "release_archive_sha256": taxonomy_manifest.get("archive_sha256"),
        "errors": errors,
        "scope_note": "Replays resource paths, declared rule applications, and release/claim fingerprints only; it does not validate gloss semantics or provide an open-world negative proof.",
    }


def run(report_path: Path, claims_path: Path, release_dir: Path, archive_path: Path) -> dict[str, Any]:
    manifest = _verify_archive_bytes_independently(release_dir, archive_path)
    nodes, instance_parents, class_parents = _load_graph_independently(release_dir)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    claims = _load_claim_rows_independently(claims_path)
    return verify_report(report, claims, manifest, nodes, instance_parents, class_parents,
                         _sha256_file(claims_path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", nargs="?", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("claims", nargs="?", type=Path, default=DEFAULT_CLAIMS)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = run(args.report, args.claims, args.release_dir, args.release_archive)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Instance-hypernym certificate replay valid={result['valid']}; claims={result['claim_count']}; errors={len(result['errors'])}")
    if args.output:
        print(f"Replay report: {args.output}")
    if not result["valid"]:
        for error in result["errors"][:20]:
            print(f"- {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
