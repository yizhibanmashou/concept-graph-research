"""Post-hoc root-order sensitivity for selected-witness degree controls."""
import argparse
import json
import random
from pathlib import Path

from src.analysis.witness_reuse_pilot import sha, simulate_lru
from src.analysis.witness_rewire_controls import rewire


def evaluate_orders(graph, roots, order_seeds, depth, capacities):
    if not roots or len(roots) != len(set(roots)) or any(root not in graph for root in roots):
        raise ValueError('invalid roots')
    rows = []
    for order_seed in order_seeds:
        ordered = random.Random(order_seed).sample(roots, len(roots))
        rows.append({'order_seed': order_seed,
                     'metrics': [simulate_lru(graph, ordered, depth, capacity) for capacity in capacities]})
    return rows


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
    runs = []
    for graph_seed in (None, 101, 102, 103):
        graph, audit = (witnesses, None) if graph_seed is None else rewire(witnesses, graph_seed)
        for row in evaluate_orders(graph, roots, (11, 23, 31), 4, (256, 4096)):
            runs.append({'graph_seed': graph_seed, 'audit': audit, **row})
            print('completed', graph_seed, row['order_seed'], flush=True)
    result = {'protocol': 'posthoc-order-sensitivity/1', 'root_count': len(roots), 'depth': 4,
              'inputs_sha256': {'coverage_witnesses.jsonl': sha(source), 'root_ids': sha(args.roots)},
              'runs': runs, 'limits': 'Post-hoc sensitivity; repeated graph/order cells are not independent datasets or cognitive evidence.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
