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


def build_aligned_relation_tensors(target_id: str, branches: Iterable[Iterable[str]]) -> dict[str, object]:
    """Build ID-only B/C/D masks over one shared, canonical node inventory.

    B is a flat dependency-membership vector, C is the undirected 2-section,
    and D is a branch-by-node incidence matrix. These are serialization
    fixtures, not learned representations or claims about semantic roles.
    """
    views = build_relation_views(target_id, branches)
    node_ids = views["node_ids"]
    node_index = {node_id: index for index, node_id in enumerate(node_ids)}
    size = len(node_ids)

    flat_dependencies = set(views["B"]["dependencies"])
    dependency_mask = tuple(node_id in flat_dependencies for node_id in node_ids)

    adjacency = [[False] * size for _ in range(size)]
    for left, right in views["C"]["pairwise_edges"]:
        i, j = node_index[left], node_index[right]
        adjacency[i][j] = True
        adjacency[j][i] = True

    incidence = tuple(
        tuple(node_id in branch for node_id in node_ids)
        for branch in views["D"]["branches"]
    )

    return {
        "node_ids": node_ids,
        "target_index": node_index[target_id],
        "B": {"dependency_mask": dependency_mask},
        "C": {"adjacency_matrix": tuple(tuple(row) for row in adjacency)},
        "D": {"incidence_matrix": incidence},
    }
