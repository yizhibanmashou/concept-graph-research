"""Versioned, Python-version-independent presentation-order algorithm."""
from __future__ import annotations

import hashlib


ALGORITHM_ID = "sha256-counter-fisher-yates/1"
_DOMAIN = b"codex-annotation-presentation/sha256-counter-fisher-yates/1\0"
_UINT64_SPACE = 1 << 64


def fisher_yates_task_order(task_ids: list[str], seed: int) -> list[str]:
    """Return a deterministic unbiased permutation under ``ALGORITHM_ID``.

    For each descending Fisher–Yates bound, draw a uint64 from SHA-256 of the
    domain separator, length-prefixed decimal seed, and big-endian counter.
    Reject the incomplete top interval before reducing modulo the bound.
    """
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    if len(task_ids) > _UINT64_SPACE:
        raise ValueError("task list exceeds the algorithm's uint64 bound")
    seed_bytes = str(seed).encode("ascii")
    if len(seed_bytes) >= 1 << 32:
        raise ValueError("seed encoding exceeds the algorithm's length bound")
    seed_prefix = _DOMAIN + len(seed_bytes).to_bytes(4, "big") + seed_bytes
    counter = 0

    def draw_below(bound: int) -> int:
        nonlocal counter
        limit = (_UINT64_SPACE // bound) * bound
        while True:
            if counter >= _UINT64_SPACE:
                raise ValueError("SHA-256 counter exhausted")
            digest = hashlib.sha256(seed_prefix + counter.to_bytes(8, "big")).digest()
            counter += 1
            value = int.from_bytes(digest[:8], "big")
            if value < limit:
                return value % bound

    ordered = list(task_ids)
    for index in range(len(ordered) - 1, 0, -1):
        other = draw_below(index + 1)
        ordered[index], ordered[other] = ordered[other], ordered[index]
    return ordered
