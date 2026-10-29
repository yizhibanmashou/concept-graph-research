"""Prepare one-hop A/B/C/D sense records for future controlled experiments.

B, C and D share exactly the same ordered dependency inventory and glosses;
only C adds pair edges and D adds branch memberships. No role labels inferred.
This is data preparation, not an encoder or a WSD benchmark.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]

def build(head, definition, clauses, definitions):
    deps = sorted({item for branch in clauses for item in branch})
    missing = [item for item in deps if item not in definitions]
    if missing:
        raise ValueError('dependencies missing from node inventory: ' + ', '.join(missing[:5]))
    items = [{'id': item, 'gloss': definitions[item]} for item in deps]
    a = {'target': head, 'gloss': definition}
    b = {**a, 'dependencies': items}
    c = {**b, 'edges': [{'head': head, 'dependency': item} for item in deps]}
    d = {**b, 'branches': [list(branch) for branch in clauses]}
    return {'A': a, 'B': b, 'C': c, 'D': d}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bundle', type=Path, default=PROJECT.parent / 'OEWN')
    parser.add_argument('--ids', nargs='+', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    node_file = args.bundle / 'graph/nodes.tsv'
    rules_file = args.bundle / 'graph/hypergraph_rules.jsonl'
    with node_file.open(encoding='utf-8-sig', newline='') as f:
        nodes = {row['synset_id']: row['definition'] for row in csv.DictReader(f, delimiter='\t')}
    rules = {}
    with rules_file.open(encoding='utf8') as f:
        for line in f:
            row = json.loads(line)
            if row['head'] in args.ids:
                rules[row['head']] = row['clauses']
    absent = [identity for identity in args.ids if identity not in nodes or identity not in rules]
    if absent:
        raise ValueError('targets missing from data: ' + ', '.join(absent))
    output = {'schema': 'sense-representation-preparation/1',
              'input_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (node_file, rules_file)},
              'limitations': 'One-hop graph data; no role labels inferred; representations have unequal serialization length and require matched input budgets before any model comparison.',
              'items': [build(x, nodes[x], rules[x], nodes) for x in args.ids]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(json.dumps({'items': len(output['items']), 'branches': [len(v['D']['branches']) for v in output['items']]}))

if __name__ == '__main__': main()
