"""Compare bounded witness expansion against degree-preserving edge swaps.

Randomized graphs are computational nulls, not valid semantic constructions.
"""
import argparse
from collections import Counter
import json
import random
from pathlib import Path

from src.analysis.witness_reuse_pilot import sha, simulate_lru


def rewire(witnesses, seed, attempts_per_edge=3, groups=None):
    """Swap targets, preserving directed degrees and preventing new loops/duplicates."""
    if attempts_per_edge < 0:
        raise ValueError('attempts must be nonnegative')
    graph = {head: list(children) for head, children in witnesses.items()}
    if any(len(children) != len(set(children)) for children in graph.values()):
        raise ValueError('duplicate input edges')
    if any(child not in graph for children in graph.values() for child in children):
        raise ValueError('edge target missing from graph')
    if groups is not None and any(node not in groups for node in graph):
        raise ValueError('missing source group')
    edge_slots = [(head, i) for head, children in graph.items() for i in range(len(children))]
    original = {(head, child) for head, children in graph.items() for child in children}
    neighbors = {head: set(children) for head, children in graph.items()}
    rng = random.Random(seed)
    accepted = 0
    attempts = len(edge_slots) * attempts_per_edge
    if len(edge_slots) >= 2:
        for _ in range(attempts):
            a, b = rng.sample(range(len(edge_slots)), 2)
            left, li = edge_slots[a]
            right, ri = edge_slots[b]
            x, y = graph[left][li], graph[right][ri]
            # Preserve existing loops but never create or move one.
            if left == right or x == y or left == x or right == y or left == y or right == x:
                continue
            if groups is not None and groups[x] != groups[y]:
                continue
            if y in neighbors[left] or x in neighbors[right]:
                continue
            neighbors[left].remove(x)
            neighbors[right].remove(y)
            neighbors[left].add(y)
            neighbors[right].add(x)
            graph[left][li], graph[right][ri] = y, x
            accepted += 1
    else:
        attempts = 0
    result = {head: tuple(children) for head, children in graph.items()}
    if Counter(child for values in result.values() for child in values) != Counter(child for values in witnesses.values() for child in values):
        raise AssertionError('incoming degree changed')
    if any(len(result[node]) != len(witnesses[node]) for node in witnesses):
        raise AssertionError('outgoing degree changed')
    if groups is not None and any(Counter(groups[x] for x in result[node]) !=
                                  Counter(groups[x] for x in witnesses[node]) for node in witnesses):
        raise AssertionError('per-head target groups changed')
    remaining = len(original & {(head, child) for head, children in result.items() for child in children})
    return result, {'attempts': attempts, 'accepted': accepted, 'edge_count': len(original),
                    'original_edges_remaining': remaining}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--roots', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = args.bundle / 'graph/coverage_witnesses.jsonl'
    with source.open(encoding='utf-8') as f:
        records = [json.loads(line) for line in f if line.strip()]
    witnesses = {r['head']: tuple(dict.fromkeys(r['witness_clause'])) for r in records}
    if len(witnesses) != len(records):
        raise ValueError('duplicate witness head')
    roots = args.roots.read_text(encoding='utf-8-sig').splitlines()
    if not roots or len(roots) != len(set(roots)) or any(root not in witnesses for root in roots):
        raise ValueError('invalid roots')
    roots = random.Random(17).sample(roots, len(roots))
    def evaluate(graph):
        return [simulate_lru(graph, roots, 4, capacity) for capacity in (0, 256, 4096)]
    runs = [{'kind': 'original', 'metrics': evaluate(witnesses)}]
    for seed in (101, 102, 103, 104, 105):
        graph, audit = rewire(witnesses, seed)
        runs.append({'kind': 'rewired', 'seed': seed, 'audit': audit, 'metrics': evaluate(graph)})
        print('completed', seed, flush=True)
    result = {'protocol': 'degree-preserving-witness-control/1', 'root_count': len(roots),
              'depth': 4, 'root_order_seed': 17, 'runs': runs,
              'inputs_sha256': {'coverage_witnesses.jsonl': sha(source), 'root_ids': sha(args.roots)},
              'limits': 'Computational graph nulls; not uniform samples, semantic constructions or cognitive evidence.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
