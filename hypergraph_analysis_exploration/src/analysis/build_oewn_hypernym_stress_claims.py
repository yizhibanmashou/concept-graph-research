"""Build a deterministic, resource-relative stress frame for the OEWN checker.

The frame probes verifier branches; it is not a sampled semantic benchmark and
its non-closure examples are not natural-language negative judgments.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter, deque
from pathlib import Path
from typing import Any

from src.analysis.gloss_genus_baseline import (
    DEFAULT_RELEASE_ARCHIVE,
    DEFAULT_RELEASE_DIR,
    _sha256,
)
from src.analysis.oewn_hypernym_verifier import (
    PROJECT_ROOT,
    VERIFIER_VERSION,
    _pos_family,
    load_hypernym_graph,
    verify_extracted_taxonomy,
)
from src.analysis.verify_oewn_hypernym_certificates import REPLAY_VERSION


GENERATOR_VERSION = "oewn-hypernym-stress-frame/1"
SEED = 20261006
PER_STRATUM = 40
DEFAULT_CLAIMS = PROJECT_ROOT / "outputs" / "phase16" / "oewn_hypernym_stress_v1_claims.jsonl"
DEFAULT_MANIFEST = PROJECT_ROOT / "outputs" / "phase16" / "oewn_hypernym_stress_v1_manifest.json"


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


def _sample_exact(pool: list[Any], count: int, rng: random.Random, label: str) -> list[Any]:
    if len(pool) < count:
        raise ValueError(f"only {len(pool)} candidates available for stratum {label!r}; need {count}")
    return rng.sample(pool, count)


def build_claims(nodes: dict[str, dict[str, str]],
                 parents: dict[str, tuple[str, ...]]) -> tuple[list[dict[str, str]], dict[str, int]]:
    rng = random.Random(SEED)
    node_ids = sorted(nodes)
    edges = sorted((child, parent) for child, parent_ids in parents.items() for parent in parent_ids)
    grouped: dict[str, list[str]] = {}
    for synset_id, row in nodes.items():
        grouped.setdefault(_pos_family(row["pos"]), []).append(synset_id)
    for values in grouped.values():
        values.sort()

    transitive: dict[str, list[tuple[str, str]]] = {"depth_2": [], "depth_3": [], "depth_4_plus": []}
    disconnected: list[tuple[str, str]] = []
    starts = node_ids[:]
    rng.shuffle(starts)
    target_pool = PER_STRATUM * 5
    for child in starts:
        distances = _ancestor_distances(child, parents)
        for ancestor, distance in distances.items():
            if distance == 2:
                transitive["depth_2"].append((child, ancestor))
            elif distance == 3:
                transitive["depth_3"].append((child, ancestor))
            elif distance >= 4:
                transitive["depth_4_plus"].append((child, ancestor))
        family = grouped[_pos_family(nodes[child]["pos"])]
        ancestor_set = set(distances)
        candidates = [candidate for candidate in family if candidate not in ancestor_set]
        if candidates:
            disconnected.append((child, rng.choice(candidates)))
        if (all(len(rows) >= target_pool for rows in transitive.values())
                and len(disconnected) >= target_pool):
            break

    strata: dict[str, list[tuple[str, str]]] = {
        "direct": _sample_exact(edges, PER_STRATUM, rng, "direct"),
        "depth_2": _sample_exact(transitive["depth_2"], PER_STRATUM, rng, "depth_2"),
        "depth_3": _sample_exact(transitive["depth_3"], PER_STRATUM, rng, "depth_3"),
        "depth_4_plus": _sample_exact(transitive["depth_4_plus"], PER_STRATUM, rng, "depth_4_plus"),
        "direction_reversed": _sample_exact([(parent, child) for child, parent in edges], PER_STRATUM,
                                             rng, "direction_reversed"),
        "same_pos_nonforward_closure": _sample_exact(disconnected, PER_STRATUM, rng,
                                                       "same_pos_nonforward_closure"),
    }

    # Avoid a quadratic Cartesian product: sample unique deterministic cross-family pairs directly.
    cross_pos: set[tuple[str, str]] = set()
    families = sorted(grouped)
    while len(cross_pos) < PER_STRATUM:
        left_family, right_family = rng.sample(families, 2)
        cross_pos.add((rng.choice(grouped[left_family]), rng.choice(grouped[right_family])))
    strata["cross_pos"] = sorted(cross_pos)
    strata["missing_synset"] = [
        (f"__missing_oewn_stress_{index:04d}__", node_id)
        for index, node_id in enumerate(_sample_exact(node_ids, PER_STRATUM, rng, "missing_synset"))
    ]
    strata["self_link"] = [(node_id, node_id) for node_id in _sample_exact(node_ids, PER_STRATUM, rng, "self_link")]

    claims: list[dict[str, str]] = []
    stratum_counts: Counter[str] = Counter()
    for stratum, pairs in strata.items():
        for child, ancestor in sorted(pairs):
            claim_id = f"{stratum}/{stratum_counts[stratum]:04d}"
            claims.append({"claim_id": claim_id,
                           "child_synset_id": child,
                           "ancestor_synset_id": ancestor})
            stratum_counts[stratum] += 1
    pair_keys = [(row["child_synset_id"], row["ancestor_synset_id"]) for row in claims]
    claim_ids = [row["claim_id"] for row in claims]
    if len(set(pair_keys)) != len(pair_keys):
        raise ValueError("strata must not repeat the same directed synset pair")
    if len(set(claim_ids)) != len(claim_ids):
        raise ValueError("generated claim IDs must be unique")
    return claims, dict(sorted(stratum_counts.items()))


def run(claims_path: Path, manifest_path: Path, release_dir: Path, archive_path: Path,
        *, force: bool = False) -> dict[str, Any]:
    if not force and (claims_path.exists() or manifest_path.exists()):
        raise FileExistsError("stress frame output exists; pass --force to replace it")
    taxonomy = verify_extracted_taxonomy(release_dir, archive_path)
    nodes, parents = load_hypernym_graph(release_dir)
    claims, stratum_counts = build_claims(nodes, parents)
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                     for row in claims).encode("utf-8")
    claims_path.write_bytes(payload)
    manifest = {
        "generator_version": GENERATOR_VERSION,
        "seed": SEED,
        "selection_design": "deterministic stratified verifier stress frame; not a probability sample",
        "claims_file": str(claims_path.relative_to(PROJECT_ROOT)),
        "claims_sha256": _sha256(claims_path),
        "claim_count": len(claims),
        "stratum_counts": stratum_counts,
        "toolchain": {
            "generator_version": GENERATOR_VERSION,
            "generator_source_sha256": _sha256(Path(__file__).resolve()),
            "producer_verifier_version": VERIFIER_VERSION,
            "producer_verifier_source_sha256": _sha256(
                PROJECT_ROOT / "src" / "analysis" / "oewn_hypernym_verifier.py"
            ),
            "replay_version": REPLAY_VERSION,
            "replay_source_sha256": _sha256(
                PROJECT_ROOT / "src" / "analysis" / "verify_oewn_hypernym_certificates.py"
            ),
        },
        "taxonomy_release": taxonomy,
        "synset_count": len(nodes),
        "direct_hypernym_edge_count": sum(len(row) for row in parents.values()),
        "interpretation_limits": [
            "The frame probes resource-verifier status branches and path depths; it is not semantic gold or an accuracy sample.",
            "same_pos_nonforward_closure means no child-to-ancestor path in the pinned graph, not a false natural-language relation.",
            "The only missing-synset IDs are synthetic sentinels and must not be interpreted as lexical items.",
            "No gloss or example text is copied into this frame or manifest."
        ]
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", type=Path, default=DEFAULT_CLAIMS)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = run(args.claims, args.manifest, args.release_dir, args.release_archive,
                       force=args.force)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(f"Generated {manifest['claim_count']} claims; strata={manifest['stratum_counts']}")
    print(f"Claims SHA-256: {manifest['claims_sha256']}")
    print(f"Manifest: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
