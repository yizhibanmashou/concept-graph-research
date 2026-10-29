"""Build a text-free, internal candidate frame for later human relation review.

This tool emits only synset IDs and hidden sampling metadata. It does not build
an annotator-ready file and does not authorize or distribute gloss text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import zipfile
from collections import deque
from pathlib import Path
from typing import Any

from src.analysis.gloss_genus_baseline import DEFAULT_RELEASE_ARCHIVE, DEFAULT_RELEASE_DIR, _sha256
from src.analysis.oewn_hypernym_verifier import _pos_family, verify_extracted_taxonomy
from src.analysis.oewn_instance_hypernym_verifier import (
    VERIFIER_VERSION,
    load_instance_graph,
    verify_claim_batch,
)
from src.analysis.replay_oewn_instance_hypernym_certificates import REPLAY_VERSION, verify_report


GENERATOR_VERSION = "oewn-instance-manual-audit-frame/1"
SEED = 20261008
PER_STRATUM = 64
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATES = PROJECT_ROOT / "outputs" / "phase78" / "instance_relation_candidate_ids.jsonl"
DEFAULT_KEY = PROJECT_ROOT / "outputs" / "phase78" / "instance_relation_sampling_key.jsonl"
DEFAULT_MANIFEST = PROJECT_ROOT / "outputs" / "phase78" / "instance_relation_candidate_manifest.json"
NOUN_POS = "n"


def _reachable(
    instance_id: str, target: str,
    instance_parents: dict[str, tuple[str, ...]],
    class_parents: dict[str, tuple[str, ...]],
) -> bool:
    pending = list(instance_parents.get(instance_id, ()))
    seen: set[str] = set()
    while pending:
        current = pending.pop()
        if current == target:
            return True
        if current not in seen:
            seen.add(current)
            pending.extend(class_parents.get(current, ()))
    return False


def _ancestor_distances(start: str, parents: dict[str, tuple[str, ...]]) -> dict[str, int]:
    distances = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for parent in parents.get(current, ()):
            if parent not in distances:
                distances[parent] = distances[current] + 1
                queue.append(parent)
    return distances


def _lift_pair_depths(
    instance_parents: dict[str, tuple[str, ...]],
    class_parents: dict[str, tuple[str, ...]],
) -> dict[tuple[str, str], int]:
    """Map unique lifted pairs to their shortest number of class edges."""
    direct_pairs = direct_parents_pairs(instance_parents)
    depths: dict[tuple[str, str], int] = {}
    for instance, direct_classes in instance_parents.items():
        for direct_class in direct_classes:
            for ancestor, distance in _ancestor_distances(direct_class, class_parents).items():
                if distance == 0:
                    continue
                pair = (instance, ancestor)
                if pair in direct_pairs:
                    continue
                lift_depth = distance
                depths[pair] = min(depths.get(pair, lift_depth), lift_depth)
    return depths


def _sample(pool: list[tuple[str, str]], count: int, rng: random.Random, label: str) -> list[tuple[str, str]]:
    if len(pool) < count:
        raise ValueError(f"stratum {label!r} has {len(pool)} candidates; need {count}")
    return rng.sample(pool, count)


def build_candidate_rows(
    nodes: dict[str, dict[str, str]],
    instance_parents: dict[str, tuple[str, ...]],
    class_parents: dict[str, tuple[str, ...]],
    *, per_stratum: int = PER_STRATUM,
) -> tuple[list[dict[str, str]], list[dict[str, Any]], dict[str, int]]:
    """Select balanced review candidates; key rows carry hidden stratum metadata."""
    if per_stratum < 1:
        raise ValueError("per_stratum must be positive")
    rng = random.Random(SEED)
    direct = sorted((instance, cls) for instance, parents in instance_parents.items() for cls in parents)
    direct_set = set(direct)
    lift_depths = _lift_pair_depths(instance_parents, class_parents)
    lift_one_set = {pair for pair, depth in lift_depths.items() if depth == 1}
    lift_two_plus_set = {pair for pair, depth in lift_depths.items() if depth >= 2}
    lift_one = sorted(lift_one_set)
    lift_two_plus = sorted(lift_two_plus_set)

    reversed_set = set()
    positive_pairs = direct_set | lift_one_set | lift_two_plus_set
    for instance, cls in direct:
        reverse = (cls, instance)
        if reverse not in positive_pairs and not _reachable(cls, instance, instance_parents, class_parents):
            reversed_set.add(reverse)

    strata: dict[str, list[tuple[str, str]]] = {
        "direct_edge": _sample(direct, per_stratum, rng, "direct_edge"),
        "lift_one_class_edge": _sample(lift_one, per_stratum, rng, "lift_one_class_edge"),
        "lift_two_plus_class_edges": _sample(lift_two_plus, per_stratum, rng, "lift_two_plus_class_edges"),
        "reverse_direct_challenge": _sample(sorted(reversed_set), per_stratum, rng, "reverse_direct_challenge"),
    }

    # Diagnostic negative pairs use a two-stage sample: source synsets uniformly,
    # then a noun target uniformly among that source's nonreachable noun synsets.
    noun_ids = sorted(sid for sid, row in nodes.items() if row["pos"] == NOUN_POS)
    source_ids = sorted(sid for sid, parents in instance_parents.items()
                        if parents and nodes[sid]["pos"] == NOUN_POS)
    if len(source_ids) < per_stratum:
        raise ValueError(f"only {len(source_ids)} noun instance sources; need {per_stratum}")
    sampled_sources = _sample([(sid, sid) for sid in source_ids], per_stratum, rng,
                              "same_pos_nonclosure_challenge")
    same_pos_pairs = []
    same_pos_target_counts: dict[tuple[str, str], int] = {}
    for instance_id, _ in sampled_sources:
        reachable = set()
        for direct_class in instance_parents[instance_id]:
            reachable.update(_ancestor_distances(direct_class, class_parents))
        candidates = [target for target in noun_ids
                      if target != instance_id and target not in reachable
                      and (instance_id, target) not in reversed_set]
        if not candidates:
            raise ValueError(f"no nonreachable noun target available for source {instance_id}")
        pair = (instance_id, rng.choice(candidates))
        same_pos_pairs.append(pair)
        same_pos_target_counts[pair] = len(candidates)
    strata["same_pos_nonclosure_challenge"] = same_pos_pairs

    # Remove any accidental pair overlap before constructing the blind IDs.
    all_pairs = [pair for pairs in strata.values() for pair in pairs]
    if len(all_pairs) != len(set(all_pairs)):
        raise ValueError("candidate strata repeat a directed synset pair")

    keys: list[dict[str, Any]] = []
    for stratum, pairs in strata.items():
        for instance_id, class_id in pairs:
            key = f"pair-{len(keys):04d}"
            if stratum == "direct_edge":
                depth, resource_status = 0, "direct_instance_membership"
            elif stratum == "lift_one_class_edge":
                depth, resource_status = 1, "lifted_instance_class_membership"
            elif stratum == "lift_two_plus_class_edges":
                depth = lift_depths[(instance_id, class_id)]
                resource_status = "lifted_instance_class_membership"
            elif stratum == "reverse_direct_challenge":
                depth, resource_status = None, "not_in_instance_class_closure"
            else:
                depth, resource_status = None, "not_in_instance_class_closure"
            keys.append({"candidate_id": key, "stratum": stratum,
                         "resource_status": resource_status,
                         "class_lift_depth": depth,
                         "within_source_target_population_count": same_pos_target_counts.get(
                             (instance_id, class_id))})

    candidates = [{"candidate_id": row["candidate_id"],
                   "instance_synset_id": pair[0], "class_synset_id": pair[1]}
                  for stratum in strata
                  for row, pair in zip((key for key in keys if key["stratum"] == stratum), strata[stratum])]
    rng.shuffle(candidates)
    original_ids: dict[str, str] = {}
    for index, row in enumerate(candidates):
        old_id = row["candidate_id"]
        new_id = f"pair-{index:04d}"
        original_ids[new_id] = old_id
        row["candidate_id"] = new_id
    key_by_id = {row["candidate_id"]: row for row in keys}
    sampling_key = []
    for row in candidates:
        old_id = original_ids[row["candidate_id"]]
        key_by_id[old_id]["candidate_id"] = row["candidate_id"]
        sampling_key.append(key_by_id[old_id])
    counts = {name: len(rows) for name, rows in sorted(strata.items())}
    return candidates, sampling_key, counts


def _jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                   for row in rows).encode("utf-8")


def run(
    candidates_path: Path,
    key_path: Path,
    manifest_path: Path,
    release_dir: Path,
    archive_path: Path,
    *,
    force: bool = False,
) -> dict[str, Any]:
    if not force and any(path.exists() for path in (candidates_path, key_path, manifest_path)):
        raise FileExistsError("candidate output exists; pass --force to replace it")
    release_manifest = verify_extracted_taxonomy(release_dir, archive_path)
    nodes, instance_parents, class_parents = load_instance_graph(release_dir)
    eligible_noun_instance_sources = sum(
        bool(parents) and nodes[instance_id]["pos"] == NOUN_POS
        for instance_id, parents in instance_parents.items()
    )
    noun_target_count = sum(row["pos"] == NOUN_POS for row in nodes.values())
    candidates, sampling_key, counts = build_candidate_rows(nodes, instance_parents,
                                                            class_parents)
    replay_claims = [{"claim_id": row["candidate_id"],
                      "instance_synset_id": row["instance_synset_id"],
                      "class_synset_id": row["class_synset_id"]}
                     for row in candidates]
    internal_claim_hash = hashlib.sha256(_jsonl_bytes(replay_claims)).hexdigest()
    batch = verify_claim_batch(replay_claims, nodes, instance_parents, class_parents)
    graph_sizes = {
        "synset_count": len(nodes),
        "direct_instance_hypernym_edge_count": sum(map(len, instance_parents.values())),
        "direct_class_hypernym_edge_count": sum(map(len, class_parents.values())),
    }
    internal_report = {
        "verifier_version": VERIFIER_VERSION,
        "inputs": {**release_manifest, "claims_sha256": internal_claim_hash, **graph_sizes},
        **batch,
    }
    replay = verify_report(internal_report, replay_claims, release_manifest, nodes,
                           instance_parents, class_parents, internal_claim_hash)
    if not replay["valid"]:
        raise ValueError(f"candidate frame failed independent replay: {replay['errors'][:5]}")
    key_by_id = {row["candidate_id"]: row for row in sampling_key}
    results_by_id = {row["claim_id"]: row for row in batch["results"]}
    mismatches = [candidate_id for candidate_id, row in key_by_id.items()
                  if results_by_id[candidate_id]["status"] != row["resource_status"]]
    if mismatches:
        raise ValueError(f"candidate hidden key disagrees with relation checker: {mismatches[:5]}")
    for path in (candidates_path, key_path, manifest_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    candidates_path.write_bytes(_jsonl_bytes(candidates))
    key_path.write_bytes(_jsonl_bytes(sampling_key))
    lift_depths = _lift_pair_depths(instance_parents, class_parents)
    direct_pairs = direct_parents_pairs(instance_parents)
    all_positive_pairs = direct_pairs | set(lift_depths)
    reverse_candidates = {
        (parent, instance) for instance, parent in direct_pairs
        if (parent, instance) not in all_positive_pairs
        and not _reachable(parent, instance, instance_parents, class_parents)
    }
    manifest = {
        "generator_version": GENERATOR_VERSION,
        "seed": SEED,
        "per_stratum": PER_STRATUM,
        "runtime": {"python_version": platform.python_version(),
                    "random_generator": "random.Random (MT19937)"},
        "purpose": "internal text-free candidate selection only; not an annotator-facing batch",
        "external_distribution_authorized": False,
        "blind_candidate_fields": ["candidate_id", "instance_synset_id", "class_synset_id"],
        "hidden_key_fields": ["candidate_id", "stratum", "resource_status", "class_lift_depth",
                              "within_source_target_population_count"],
        "candidate_count": len(candidates),
        "stratum_counts": counts,
        "resource_preflight": {
            "producer_status_counts": batch["status_counts"],
            "producer_claim_count": batch["claim_count"],
            "independent_replay_valid": replay["valid"],
            "independent_replay_errors": len(replay["errors"]),
            "internal_claim_set_sha256": internal_claim_hash,
        },
        "candidate_file": str(candidates_path.relative_to(PROJECT_ROOT)),
        "candidate_sha256": _sha256(candidates_path),
        "sampling_key_file": str(key_path.relative_to(PROJECT_ROOT)),
        "sampling_key_sha256": _sha256(key_path),
        "taxonomy_release": release_manifest,
        "synset_count": len(nodes),
        "direct_instance_hypernym_edge_count": sum(map(len, instance_parents.values())),
        "direct_class_hypernym_edge_count": sum(map(len, class_parents.values())),
        "population_counts": {
            "direct_edge": len(direct_pairs),
            "lift_one_class_edge": sum(depth == 1 for depth in lift_depths.values()),
            "lift_two_plus_class_edges": sum(depth >= 2 for depth in lift_depths.values()),
            "reverse_direct_challenge": len(reverse_candidates),
            "same_pos_nonclosure_challenge": {
                "eligible_source_synset_count": eligible_noun_instance_sources,
                "noun_target_synset_count": noun_target_count,
                "source_sampling": "uniform without replacement",
                "target_sampling": "one uniform eligible nonclosure noun per selected source; exact eligible target count in hidden key",
            },
        },
        "estimation_notes": [
            "direct_edge is an unweighted SRSWOR sample from direct OEWN instance_hypernym edges.",
            "lift strata are depth-specific samples from distinct reachable instance/class pairs; analyze separately or use their known population counts for a predeclared closure-weighted estimate.",
            "the two challenge strata are diagnostic and are not part of a pooled accuracy estimate.",
            "same_pos_nonclosure uses a two-stage macro design: source synsets sampled uniformly among noun synsets with at least one instance edge, then one target sampled uniformly among that source's nonreachable noun targets after excluding reverse-direct challenge pairs; the key records each eligible target count.",
        ],
        "toolchain": {
            "generator_source_sha256": _sha256(Path(__file__).resolve()),
            "producer_verifier_version": VERIFIER_VERSION,
            "producer_verifier_source_sha256": _sha256(PROJECT_ROOT / "src/analysis/oewn_instance_hypernym_verifier.py"),
            "replay_version": REPLAY_VERSION,
            "replay_source_sha256": _sha256(PROJECT_ROOT / "src/analysis/replay_oewn_instance_hypernym_certificates.py"),
        },
        "interpretation_limits": [
            "This text-free frame is not legal review, protocol signature, external preregistration, or distribution authorization.",
            "It is a relation-stratified candidate pool, not representative across all glosses, lemmas, or senses.",
            "Resource-relation agreement and source-gloss semantic support are different labels and require separate tasks.",
            "No gloss, lemma, example, or word form is included in the candidate file or hidden key.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def direct_parents_pairs(instance_parents: dict[str, tuple[str, ...]]) -> set[tuple[str, str]]:
    return {(instance, parent) for instance, parents in instance_parents.items() for parent in parents}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--sampling-key", type=Path, default=DEFAULT_KEY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = run(args.candidates, args.sampling_key, args.manifest,
                       args.release_dir, args.release_archive, force=args.force)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))
    print(f"Built {manifest['candidate_count']} text-free candidates; strata={manifest['stratum_counts']}")
    print(f"Candidate SHA-256: {manifest['candidate_sha256']}")
    print(f"External distribution authorized: {manifest['external_distribution_authorized']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
