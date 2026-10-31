"""Profile the parameter-free relation operator on real train-only graph shapes.

Node vectors are deterministic random tensors, not semantic/text embeddings.
Only candidate_ids are used from train.json; no labels, contexts, dev or test
examples are read. The output is a local resource diagnostic, not a model run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path
from statistics import median
from typing import Any

from src.analysis.t04_relation_aggregation import aggregate_relation_views


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _quantiles(values: list[int]) -> dict[str, int | float | None]:
    if not values:
        return {"count": 0, "median": None, "p90_nearest_rank": None, "max": None}
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "median": median(ordered),
        "p90_nearest_rank": ordered[(9 * len(ordered) + 9) // 10 - 1],
        "max": ordered[-1],
    }


def _read_candidate_ids(path: Path) -> list[str]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("train input must be a JSON array")
    ids: set[str] = set()
    occurrences = 0
    for row in rows:
        values = row.get("candidate_ids") if isinstance(row, dict) else None
        if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
            raise ValueError("every row must have nonempty candidate_ids")
        occurrences += len(values)
        ids.update(values)
    return sorted(ids)


def _read_rules(path: Path, target_ids: set[str]) -> dict[str, list[list[str]]]:
    rules: dict[str, list[list[str]]] = {}
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("head") in target_ids:
                rules[row["head"]] = row["clauses"]
    return rules


def _random_vectors(node_ids: set[str], width: int, device: str, torch: Any) -> dict[str, Any]:
    vectors = {}
    for node_id in node_ids:
        seed = int.from_bytes(hashlib.sha256(node_id.encode("utf-8")).digest()[:8], "big") & 0x7FFF_FFFF_FFFF_FFFF
        generator = torch.Generator(device="cpu").manual_seed(seed)
        vectors[node_id] = torch.randn(width, generator=generator, dtype=torch.float32).to(device)
    return vectors


def profile(
    target_ids: list[str],
    rules: dict[str, list[list[str]]],
    vectors: dict[str, Any],
    device: str,
    warmup: int = 32,
) -> dict[str, Any]:
    import torch

    if torch.device(device).type != "xpu" or not torch.xpu.is_available():
        raise ValueError("an available XPU is required")
    missing = [target_id for target_id in target_ids if target_id not in rules]
    if missing:
        raise ValueError("train candidate rules missing")

    node_counts: list[int] = []
    branch_counts: list[int] = []
    edge_counts: list[int] = []
    for target_id in target_ids:
        clauses = rules[target_id]
        dependencies = {member for branch in clauses for member in branch}
        node_counts.append(1 + len(dependencies))
        branch_counts.append(len(clauses))
        edges = {
            tuple(sorted((left, right)))
            for branch in clauses
            for clique in ((target_id, *branch),)
            for index, left in enumerate(clique)
            for right in clique[index + 1:]
        }
        edge_counts.append(len(edges))

    for target_id in target_ids[:min(warmup, len(target_ids))]:
        aggregate_relation_views(vectors, target_id, rules[target_id])
    torch.xpu.synchronize()
    baseline_bytes = torch.xpu.memory_allocated()
    torch.xpu.reset_peak_memory_stats()

    started = time.perf_counter()
    checksum = 0.0
    for target_id in target_ids:
        result = aggregate_relation_views(vectors, target_id, rules[target_id])
        checksum += float(result["D"][0].item())
    torch.xpu.synchronize()
    elapsed = time.perf_counter() - started
    peak_bytes = torch.xpu.max_memory_allocated()

    return {
        "candidate_unique_count": len(target_ids),
        "warmup_candidates": min(warmup, len(target_ids)),
        "relation_nodes_per_candidate": _quantiles(node_counts),
        "branches_per_candidate": _quantiles(branch_counts),
        "pairwise_edges_per_candidate": _quantiles(edge_counts),
        "total_relation_nodes_processed": sum(node_counts),
        "total_branches_processed": sum(branch_counts),
        "total_pairwise_edges_processed": sum(edge_counts),
        "wall_clock_seconds": elapsed,
        "candidates_per_second": len(target_ids) / elapsed if elapsed else None,
        "baseline_allocated_bytes_for_random_node_vectors": baseline_bytes,
        "peak_allocated_bytes_after_peak_reset": peak_bytes,
        "peak_increment_over_baseline_bytes": max(0, peak_bytes - baseline_bytes),
        "finite_output_check": bool(torch.isfinite(torch.tensor(checksum))),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="new local output path")
    parser.add_argument("--width", type=int, default=128)
    parser.add_argument("--warmup", type=int, default=32)
    args = parser.parse_args()
    import torch

    if args.width < 1 or args.warmup < 0:
        raise ValueError("width must be positive and warmup nonnegative")
    target_ids = _read_candidate_ids(args.train)
    rules = _read_rules(args.rules, set(target_ids))
    node_ids = set(target_ids)
    for target_id in target_ids:
        for branch in rules.get(target_id, []):
            node_ids.update(branch)
    vectors = _random_vectors(node_ids, args.width, "xpu", torch)
    result = profile(target_ids, rules, vectors, "xpu", args.warmup)
    result.update({
        "schema": "t04-xpu-relation-aggregation-profile/1",
        "device_name": torch.xpu.get_device_name(0),
        "torch_version": torch.__version__,
        "python_version": platform.python_version(),
        "vector_width": args.width,
        "vector_source": "deterministic_random_nonsemantic_vectors",
        "inputs_sha256": {"train_json": _sha256(args.train), "hypergraph_rules_jsonl": _sha256(args.rules)},
        "limits": (
            "Uses only candidate_ids from the frozen train split; random vectors replace text embeddings. Measures this "
            "Python relation-pooling implementation only, not BERT encoding, training, semantic quality, model accuracy, "
            "or general XPU capacity. No labels, contexts, dev/test examples, or gloss text are emitted."
        ),
    })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps({key: result[key] for key in (
        "candidate_unique_count", "total_relation_nodes_processed", "total_branches_processed",
        "total_pairwise_edges_processed", "wall_clock_seconds", "candidates_per_second",
        "peak_increment_over_baseline_bytes", "finite_output_check",
    )}, sort_keys=True))


if __name__ == "__main__":
    main()
