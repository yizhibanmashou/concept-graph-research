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
) -> dict[str, Any]:
    """Return A/B/C/D pooled vectors with a shared, parameter-free operator.

    Each input value must be a one-dimensional PyTorch tensor of the same
    width. A is the target vector. B mean-pools the unique dependency set. C
    mean-pools undirected endpoint-pair means from each target-plus-branch
    clique (the pairwise 2-section). D mean-pools within each original branch,
    including the target, then mean-pools across alternative branches.

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

    vectors = {node_id: node_vectors[node_id] for node_id in needed}
    if any(not isinstance(vector, torch.Tensor) or vector.ndim != 1 for vector in vectors.values()):
        raise ValueError("node vectors must be one-dimensional torch tensors")
    widths = {int(vector.shape[0]) for vector in vectors.values()}
    if len(widths) != 1:
        raise ValueError("node vectors must have equal width")

    target = vectors[target_id]
    b_relation = torch.stack([vectors[node_id] for node_id in dependency_ids]).mean(dim=0)

    pair_ids = tuple(sorted({
        tuple(sorted((left, right)))
        for branch in canonical
        for clique in ((target_id, *branch),)
        for index, left in enumerate(clique)
        for right in clique[index + 1:]
    }))
    c_relation = torch.stack([
        (vectors[left] + vectors[right]) / 2 for left, right in pair_ids
    ]).mean(dim=0)

    branch_vectors = [torch.stack([target, *(vectors[node_id] for node_id in branch)]).mean(dim=0)
                      for branch in canonical]
    d_relation = torch.stack(branch_vectors).mean(dim=0)

    return {
        "A": torch.cat([target, torch.zeros_like(target)]),
        "B": torch.cat([target, b_relation]),
        "C": torch.cat([target, c_relation]),
        "D": torch.cat([target, d_relation]),
        "dependency_ids": dependency_ids,
        "pair_ids": pair_ids,
        "canonical_branches": canonical,
    }
