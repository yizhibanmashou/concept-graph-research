"""Bounded selected-witness expansion and memoization accounting.

A computational property of a supplied graph, not a model of human cognition.
Memoization keys include remaining depth; per-root and cross-root caches are
reported separately. Every prerequisite of the selected branch is retained.
"""
from __future__ import annotations
import argparse
import functools
import hashlib
import json
import random
from collections import OrderedDict
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def measure(witnesses, roots, depth):
    @functools.lru_cache(None)
    def unfolded(node, remaining):
        children = witnesses[node]
        if remaining == 0 or not children:
            return 1
        return 1 + sum(unfolded(child, remaining - 1) for child in children)
    def keys(root):
        seen = set()
        pending = [(root, depth)]
        while pending:
            key = pending.pop()
            if key in seen:
                continue
            seen.add(key)
            node, remaining = key
            if remaining > 0:
                pending.extend((child, remaining - 1) for child in witnesses[node])
        return seen
    cross = set()
    visits = local_cache = 0
    for root in roots:
        visits += unfolded(root, depth)
        local = keys(root)
        local_cache += len(local)
        cross.update(local)
    cache_orders = {
        'listed': list(roots),
        'reverse': list(reversed(roots)),
        'shuffle_seed_17': random.Random(17).sample(list(roots), len(roots)),
    }
    capacities = (0, 16, 64, 256, 1024, 4096, 16384, None)
    capacity_results = {
        order_name: [simulate_lru(witnesses, order, depth, capacity) for capacity in capacities]
        for order_name, order in cache_orders.items()
    }
    return {'root_count': len(roots), 'depth': depth, 'unfolded_node_visits': visits,
            'per_root_unique_node_depth_keys': local_cache,
            'across_root_unique_node_depth_keys': len(cross),
            'lru_cache_capacity_sensitivity': {
                'capacity_keys': list(capacities),
                'root_orders': capacity_results,
                'capacity_unit': 'distinct (node_id, remaining_depth) keys',
                'order_note': 'listed order follows the supplied root file; reverse and seed-17 shuffle are deterministic sensitivity checks',
            }}

def simulate_lru(witnesses, roots, depth, capacity):
    cache = OrderedDict()
    misses = hits = evictions = 0

    def evaluate(key):
        nonlocal misses, hits, evictions
        if capacity != 0 and key in cache:
            hits += 1
            cache.move_to_end(key)
            return
        misses += 1
        node, remaining = key
        if remaining > 0:
            for child in witnesses[node]:
                evaluate((child, remaining - 1))
        if capacity == 0:
            return
        cache[key] = None
        cache.move_to_end(key)
        if capacity is not None and len(cache) > capacity:
            cache.popitem(last=False)
            evictions += 1

    for root in roots:
        evaluate((root, depth))
    return {
        'capacity': capacity,
        'computed_states': misses,
        'cache_hits': hits,
        'evictions': evictions,
        'final_cache_size': len(cache),
        'visits_avoided_percent': round(100 * (1 - misses / sum_unfolded(witnesses, roots, depth)), 4)
        if roots else 0.0,
    }

def sum_unfolded(witnesses, roots, depth):
    @functools.lru_cache(None)
    def count(node, remaining):
        return 1 + (sum(count(child, remaining - 1) for child in witnesses[node]) if remaining > 0 else 0)
    return sum(count(root, depth) for root in roots)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--bundle', type=Path, default=PROJECT.parent / 'OEWN')
    p.add_argument('--roots', type=Path, default=PROJECT / 'outputs/experiment_2026_10_13/evaluation_root_ids.txt')
    p.add_argument('--depth', type=int, default=4)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    if not 0 <= args.depth <= 20:
        p.error('depth must be between 0 and 20')
    path = args.bundle / 'graph/coverage_witnesses.jsonl'
    with path.open(encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    witnesses = {r['head']: tuple(dict.fromkeys(r['witness_clause'])) for r in rows}
    if len(witnesses) != len(rows):
        raise ValueError('duplicate witness head')
    roots = args.roots.read_text(encoding='utf-8-sig').splitlines()
    if len(roots) != len(set(roots)):
        raise ValueError('duplicate root')
    metrics = measure(witnesses, roots, args.depth)
    result = {'analysis': 'bounded-witness-reuse/1', 'metrics': metrics,
              'inputs_sha256': {'coverage_witnesses.jsonl': sha(path), 'root_ids': sha(args.roots)},
              'limits': 'Selected witness only, bounded by depth; no timing, human data, semantic validation or evidence of psychological learning.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(metrics))

if __name__ == '__main__':
    main()
