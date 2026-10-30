"""Post-hoc root-source sensitivity of degree-preserving graph controls."""
import argparse
import csv
import json
import random
from pathlib import Path

from src.analysis.witness_reuse_pilot import sha, simulate_lru
from src.analysis.witness_rewire_controls import rewire

SOURCES = ('fully_parsed_glosstag_plausible_wsd', 'ready_for_lingua_glosstag_plausible_wsd')


def source_groups(roots, nodes):
    if not roots or len(roots) != len(set(roots)):
        raise ValueError('invalid roots')
    mapping = {row['synset_id']: row['source_root'] for row in nodes}
    if len(mapping) != len(nodes) or any(root not in mapping for root in roots):
        raise ValueError('duplicate or missing node')
    groups = {source: [root for root in roots if mapping[root] == source] for source in SOURCES}
    if any(not values for values in groups.values()):
        raise ValueError('empty source group')
    return groups


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--roots', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    witnesses_path = args.bundle / 'graph/coverage_witnesses.jsonl'
    nodes_path = args.bundle / 'graph/nodes.tsv'
    with witnesses_path.open(encoding='utf-8') as f:
        records = [json.loads(line) for line in f if line.strip()]
    graph = {r['head']: tuple(dict.fromkeys(r['witness_clause'])) for r in records}
    if len(graph) != len(records):
        raise ValueError('duplicate witness head')
    with nodes_path.open(encoding='utf-8-sig', newline='') as f:
        nodes = list(csv.DictReader(f, delimiter='\t'))
    roots = args.roots.read_text(encoding='utf-8-sig').splitlines()
    groups = source_groups(roots, nodes)
    groups = {source: random.Random(17).sample(values, len(values)) for source, values in groups.items()}
    runs = []
    for graph_seed in (None, 101, 102):
        current, audit = (graph, None) if graph_seed is None else rewire(graph, graph_seed)
        for source, selected in groups.items():
            metrics = [simulate_lru(current, selected, 4, capacity) for capacity in (256, 4096)]
            runs.append({'graph_seed': graph_seed, 'source': source, 'roots': len(selected),
                         'audit': audit, 'metrics': metrics})
            print('completed', graph_seed, source, flush=True)
    result = {'protocol': 'posthoc-root-source-sensitivity/1', 'runs': runs,
              'inputs_sha256': {'witnesses': sha(witnesses_path), 'nodes.tsv': sha(nodes_path),
                                'root_ids': sha(args.roots)},
              'limits': 'Root source groups are from one graph; rewiring does not preserve target source, semantics or roles. No causal or cognition claim.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
