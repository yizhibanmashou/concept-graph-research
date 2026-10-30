"""Build text-free, aligned B/C/D relation views for synthetic T04 checks."""
from __future__ import annotations

from itertools import combinations
from typing import Iterable


def build_relation_views(target_id: str, branches: Iterable[Iterable[str]]) -> dict[str, object]:
    """Return a flat dependency set, its pairwise projection, and hyperedges.

    The result contains identifiers only. It does not load glosses, labels, or
    corpus examples, and it does not assign semantic roles to graph edges.
    """
    if not target_id:
        raise ValueError("target ID must be nonempty")

    canonical_branches = []
    for branch in branches:
        members = set(branch)
        if not members:
            raise ValueError("source branches must be nonempty")
        if target_id in members:
            raise ValueError("branch dependencies must exclude the target ID")
        canonical_branches.append(tuple(sorted(members)))
    if not canonical_branches:
        raise ValueError("at least one source branch is required")

    dependency_ids = tuple(sorted({node for branch in canonical_branches for node in branch}))
    hyperedges = tuple(sorted(
        tuple(sorted((target_id, *branch))) for branch in canonical_branches
    ))
    pairwise_edges = tuple(sorted({
        tuple(sorted(pair))
        for edge in hyperedges
        for pair in combinations(edge, 2)
    }))

    # Keep a canonical shared node inventory; only the relation view changes.
    aligned_node_ids = tuple(sorted({target_id, *dependency_ids}))
    return {
        "node_ids": aligned_node_ids,
        "B": {"dependencies": dependency_ids},
        "C": {"pairwise_edges": pairwise_edges},
        "D": {"branches": hyperedges},
    }
