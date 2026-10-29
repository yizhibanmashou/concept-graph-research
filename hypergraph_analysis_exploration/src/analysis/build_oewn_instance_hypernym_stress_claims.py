"""Build a deterministic resource-relative stress frame for the instance adapter.

The frame probes status branches and class-lift depths. It is not a semantic
gold set, probability sample, or accuracy benchmark.
"""
from __future__ import annotations

import argparse
import json
import platform
import random
from collections import Counter, deque
from pathlib import Path
from typing import Any

from src.analysis.gloss_genus_baseline import DEFAULT_RELEASE_ARCHIVE, DEFAULT_RELEASE_DIR, _sha256
from src.analysis.oewn_hypernym_verifier import _pos_family, verify_extracted_taxonomy
from src.analysis.oewn_instance_hypernym_verifier import VERIFIER_VERSION, load_instance_graph
from src.analysis.replay_oewn_instance_hypernym_certificates import REPLAY_VERSION


GENERATOR_VERSION = "oewn-instance-hypernym-stress-frame/1"
SEED = 20261007
PER_STRATUM = 40
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CLAIMS = PROJECT_ROOT / "outputs" / "phase77" / "oewn_instance_hypernym_stress_v1_claims.jsonl"
DEFAULT_MANIFEST = PROJECT_ROOT / "outputs" / "phase77" / "oewn_instance_hypernym_stress_v1_manifest.json"


def _reachable_from_instance(
    instance_id: str,
    target_class_id: str,
    instance_parents: dict[str, tuple[str, ...]],
    class_parents: dict[str, tuple[str, ...]],
) -> bool:
    pending = list(instance_parents.get(instance_id, ()))
    seen: set[str] = set()
    while pending:
        current = pending.pop()
        if current == target_class_id:
            return True
        if current not in seen:
            seen.add(current)
            pending.extend(class_parents.get(current, ()))
    return False


def _ancestors(start: str, class_parents: dict[str, tuple[str, ...]]) -> dict[str, int]:
    distances = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for parent in class_parents.get(current, ()):
            if parent not in distances:
                distances[parent] = distances[current] + 1
                queue.append(parent)
    return distances


def _sample(pool: list[Any], count: int, rng: random.Random, label: str) -> list[Any]:
    if len(pool) < count:
        raise ValueError(f"only {len(pool)} candidates available for stratum {label!r}; need {count}")
    return rng.sample(pool, count)


def build_claims(
    nodes: dict[str, dict[str, str]],
    instance_parents: dict[str, tuple[str, ...]],
    class_parents: dict[str, tuple[str, ...]],
    *, per_stratum: int = PER_STRATUM,
) -> tuple[list[dict[str, str]], dict[str, int]]:
    if per_stratum < 1:
        raise ValueError("per_stratum must be positive")
    rng = random.Random(SEED)
    grouped: dict[str, list[str]] = {}
    for synset_id, row in nodes.items():
        grouped.setdefault(_pos_family(row["pos"]), []).append(synset_id)
    for values in grouped.values():
        values.sort()

    direct = sorted((instance, cls) for instance, classes in instance_parents.items() for cls in classes)
    lift_one: list[tuple[str, str]] = []
    lift_two_plus: list[tuple[str, str]] = []
    for instance, classes in instance_parents.items():
        for cls in classes:
            for ancestor, distance in _ancestors(cls, class_parents).items():
                if distance == 1:
                    lift_one.append((instance, ancestor))
                elif distance >= 2:
                    lift_two_plus.append((instance, ancestor))

    positive_pairs = set(direct) | set(lift_one) | set(lift_two_plus)
    reversed_direct = set()
    for instance, cls in direct:
        reversed_pair = (cls, instance)
        if (reversed_pair not in positive_pairs
                and not _reachable_from_instance(cls, instance, instance_parents, class_parents)):
            reversed_direct.add(reversed_pair)

    same_pos_nonreach: list[tuple[str, str]] = []
    node_ids = sorted(nodes)
    reserved_pairs = positive_pairs | reversed_direct
    same_pos_seen: set[tuple[str, str]] = set()
    for _ in range(max(per_stratum * 200, 1000)):
        instance = rng.choice(node_ids)
        family = _pos_family(nodes[instance]["pos"])
        target = rng.choice(grouped[family])
        pair = (instance, target)
        if (instance != target and pair not in reserved_pairs and pair not in same_pos_seen
                and not _reachable_from_instance(instance, target, instance_parents, class_parents)):
            same_pos_nonreach.append(pair)
            same_pos_seen.add(pair)
            if len(same_pos_nonreach) >= per_stratum * 5:
                break

    families = sorted(grouped)
    cross_pos: set[tuple[str, str]] = set()
    while len(cross_pos) < per_stratum:
        left_family, right_family = rng.sample(families, 2)
        cross_pos.add((rng.choice(grouped[left_family]), rng.choice(grouped[right_family])))

    strata: dict[str, list[tuple[str, str]]] = {
        "direct_instance": _sample(direct, per_stratum, rng, "direct_instance"),
        "lift_one_class_edge": _sample(lift_one, per_stratum, rng, "lift_one_class_edge"),
        "lift_two_plus_class_edges": _sample(lift_two_plus, per_stratum, rng, "lift_two_plus_class_edges"),
        "direction_reversed": _sample(sorted(reversed_direct), per_stratum, rng, "direction_reversed"),
        "same_pos_nonclosure": _sample(same_pos_nonreach, per_stratum, rng, "same_pos_nonclosure"),
        "cross_pos": sorted(cross_pos),
        "missing_synset": [(f"__missing_oewn_instance_stress_{i:04d}__", target)
                           for i, target in enumerate(_sample(node_ids, per_stratum, rng, "missing_synset"))],
        "self_pair": [(node_id, node_id) for node_id in _sample(node_ids, per_stratum, rng, "self_pair")],
    }
    claims: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    for stratum, pairs in strata.items():
        for instance, class_id in sorted(pairs):
            claim_id = f"{stratum}/{counts[stratum]:04d}"
            claims.append({"claim_id": claim_id, "instance_synset_id": instance, "class_synset_id": class_id})
            counts[stratum] += 1
    pair_keys = [(row["instance_synset_id"], row["class_synset_id"]) for row in claims]
    claim_ids = [row["claim_id"] for row in claims]
    if len(pair_keys) != len(set(pair_keys)):
        raise ValueError("stress strata repeat a directed instance/class pair")
    if len(claim_ids) != len(set(claim_ids)):
        raise ValueError("stress frame contains duplicate claim IDs")
    return claims, dict(sorted(counts.items()))


def run(
    claims_path: Path,
    manifest_path: Path,
    release_dir: Path,
    archive_path: Path,
    *,
    force: bool = False,
) -> dict[str, Any]:
    if not force and (claims_path.exists() or manifest_path.exists()):
        raise FileExistsError("stress frame output exists; pass --force to replace it")
    taxonomy = verify_extracted_taxonomy(release_dir, archive_path)
    nodes, instance_parents, class_parents = load_instance_graph(release_dir)
    claims, counts = build_claims(nodes, instance_parents, class_parents)
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    claims_bytes = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                            for row in claims).encode("utf-8")
    claims_path.write_bytes(claims_bytes)
    manifest = {
        "generator_version": GENERATOR_VERSION,
        "seed": SEED,
        "per_stratum": PER_STRATUM,
        "runtime": {"python_version": platform.python_version(),
                    "random_generator": "random.Random (MT19937)"},
        "selection_design": "deterministic stratified verifier stress frame; not a probability sample",
        "claims_file": str(claims_path.relative_to(PROJECT_ROOT)),
        "claims_sha256": _sha256(claims_path),
        "claim_count": len(claims),
        "stratum_counts": counts,
        "toolchain": {
            "generator_version": GENERATOR_VERSION,
            "generator_source_sha256": _sha256(Path(__file__).resolve()),
            "producer_verifier_version": VERIFIER_VERSION,
            "producer_verifier_source_sha256": _sha256(
                PROJECT_ROOT / "src" / "analysis" / "oewn_instance_hypernym_verifier.py"),
            "replay_version": REPLAY_VERSION,
            "replay_source_sha256": _sha256(
                PROJECT_ROOT / "src" / "analysis" / "replay_oewn_instance_hypernym_certificates.py"),
        },
        "taxonomy_release": taxonomy,
        "synset_count": len(nodes),
        "direct_instance_hypernym_edge_count": sum(map(len, instance_parents.values())),
        "direct_class_hypernym_edge_count": sum(map(len, class_parents.values())),
        "interpretation_limits": [
            "Strata probe verifier branches and class-lift depths; the frame is not semantic gold, a probability sample, or an accuracy estimate.",
            "direction_reversed and same_pos_nonclosure denote lack of reachability under the declared finite relation rules, not semantic falsehood.",
            "Missing-synset IDs are synthetic sentinels and do not denote lexical items.",
            "No gloss, example, lemma, or synset text is copied into claims or manifest.",
        ],
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
        manifest = run(args.claims, args.manifest, args.release_dir, args.release_archive, force=args.force)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))
    print(f"Generated {manifest['claim_count']} claims; strata={manifest['stratum_counts']}")
    print(f"Claims SHA-256: {manifest['claims_sha256']}")
    print(f"Manifest: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
