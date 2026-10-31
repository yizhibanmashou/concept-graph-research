"""Parameter-free B/C/D relation pooling for synthetic T04 checks.

This module operates on already encoded node vectors. It does not define a
text encoder, infer semantic roles, train parameters, or score WSD examples.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def _canonical_branches(target_id: str, branches: Iterable[Iterable[str]]) -> tuple[tuple[str, ...], ...]:
    if not target_id:
        raise ValueError("target ID must be nonempty")
    normalized = []
    for branch in branches:
        members = tuple(sorted(set(branch)))
        if not members:
            raise ValueError("branches must be nonempty")
        if target_id in members:
            raise ValueError("branches must not repeat the target ID")
        normalized.append(members)
    if not normalized:
        raise ValueError("at least one branch is required")
    return tuple(sorted(set(normalized)))


def aggregate_relation_views(
    node_vectors: Mapping[str, Any],
    target_id: str,
    branches: Iterable[Iterable[str]],
    *,
    include_relation_items: bool = False,
) -> dict[str, Any]:
    """Return A/B/C/D pooled vectors with a shared, parameter-free operator.

    Each input value must be a one-dimensional PyTorch tensor of the same
    width. A is the target vector. B mean-pools the unique dependency set. C
    mean-pools undirected endpoint-pair means from each target-plus-branch
    clique (the pairwise 2-section). D mean-pools within each original branch,
    including the target, then mean-pools across alternative branches. This D
    output is a lossy first-order statistic, not an injective encoding of the
    full AND/OR branch structure. C's endpoint mean can likewise collapse
    distinct pairwise edge sets, so neither view is a lossless graph encoding.

    All returned candidates concatenate the same target vector and one
    relation vector, so a downstream scorer can share its parameters. This is
    a simple structural control, not a learned hypergraph encoder.
    """
    canonical = _canonical_branches(target_id, branches)
    dependency_ids = tuple(sorted({member for branch in canonical for member in branch}))
    needed = {target_id, *dependency_ids}
    missing = sorted(needed - set(node_vectors))
    if missing:
        raise ValueError("missing node vectors")

    import torch

    node_ids = tuple(sorted(needed))
    vectors = [node_vectors[node_id] for node_id in node_ids]
    if any(not isinstance(vector, torch.Tensor) or vector.ndim != 1 for vector in vectors):
        raise ValueError("node vectors must be one-dimensional torch tensors")
    widths = {int(vector.shape[0]) for vector in vectors}
    if len(widths) != 1:
        raise ValueError("node vectors must have equal width")

    node_index = {node_id: index for index, node_id in enumerate(node_ids)}
    pair_ids = tuple(sorted({
        tuple(sorted((left, right)))
        for branch in canonical
        for clique in ((target_id, *branch),)
        for index, left in enumerate(clique)
        for right in clique[index + 1:]
    }))

    # Each relation view is a weighted mean over the same packed node matrix.
    # Building weights in Python avoids many tiny device-side stack/add/mean
    # launches for each candidate; one matrix multiply computes B/C/D together.
    weights = [[0.0] * len(node_ids) for _ in range(3)]
    if not dependency_ids:
        raise ValueError("branches must contain at least one dependency")
    for node_id in dependency_ids:
        weights[0][node_index[node_id]] = 1.0 / len(dependency_ids)
    if not pair_ids:
        raise ValueError("pairwise projection must contain at least one edge")
    pair_weight = 1.0 / (2 * len(pair_ids))
    for left, right in pair_ids:
        weights[1][node_index[left]] += pair_weight
        weights[1][node_index[right]] += pair_weight
    branch_weight = 1.0 / len(canonical)
    for branch in canonical:
        member_weight = branch_weight / (len(branch) + 1)
        weights[2][node_index[target_id]] += member_weight
        for node_id in branch:
            weights[2][node_index[node_id]] += member_weight

    matrix = torch.stack(vectors)
    weight_tensor = torch.tensor(weights, dtype=matrix.dtype, device=matrix.device)
    target = matrix[node_index[target_id]]
    relation_vectors = weight_tensor @ matrix

    result = {
        "A": torch.cat([target, torch.zeros_like(target)]),
        "B": torch.cat([target, relation_vectors[0]]),
        "C": torch.cat([target, relation_vectors[1]]),
        "D": torch.cat([target, relation_vectors[2]]),
        "dependency_ids": dependency_ids,
        "pair_ids": pair_ids,
        "canonical_branches": canonical,
    }
    if include_relation_items:
        result["relation_items"] = {
            "A": target.unsqueeze(0),
            "B": torch.stack([node_vectors[node_id] for node_id in dependency_ids]),
            "C": torch.stack([
                (node_vectors[left] + node_vectors[right]) / 2 for left, right in pair_ids
            ]),
            "D": torch.stack([
                torch.stack([target, *(node_vectors[node_id] for node_id in branch)]).mean(0)
                for branch in canonical
            ]),
        }
    return result
