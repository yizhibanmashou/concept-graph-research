"""Post-hoc degree and per-head target-source-preserving witness controls."""
import argparse
import csv
import json
import random
from pathlib import Path

from src.analysis.witness_reuse_pilot import sha, simulate_lru
from src.analysis.witness_rewire_controls import rewire


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--roots', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    witness_path, nodes_path = args.bundle / 'graph/coverage_witnesses.jsonl', args.bundle / 'graph/nodes.tsv'
    with witness_path.open(encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    graph = {r['head']: tuple(dict.fromkeys(r['witness_clause'])) for r in rows}
    if len(graph) != len(rows):
        raise ValueError('duplicate witness head')
    with nodes_path.open(encoding='utf-8-sig', newline='') as f:
        nodes = list(csv.DictReader(f, delimiter='\t'))
    labels = {r['synset_id']: r['source_root'] for r in nodes}
    if len(labels) != len(nodes) or any(node not in labels for node in graph):
        raise ValueError('duplicate or missing node source')
    roots = args.roots.read_text(encoding='utf-8-sig').splitlines()
    if not roots or len(roots) != len(set(roots)) or any(root not in graph for root in roots):
        raise ValueError('invalid roots')
    roots = random.Random(17).sample(roots, len(roots))
    runs = []
    for seed in (None, 101, 102, 103):
        g, audit = (graph, None) if seed is None else rewire(graph, seed, groups=labels)
        metrics = [simulate_lru(g, roots, 4, capacity) for capacity in (0, 256, 4096)]
        runs.append({'graph_seed': seed, 'audit': audit, 'metrics': metrics})
        print('completed', seed, flush=True)
    result = {'protocol': 'posthoc-source-preserving-control/1', 'root_count': len(roots), 'runs': runs,
              'inputs_sha256': {'witnesses': sha(witness_path), 'nodes.tsv': sha(nodes_path), 'root_ids': sha(args.roots)},
              'limits': 'Source is a graph-pipeline label; randomized edges have no semantics. This is not an independent graph or cognitive evidence.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
