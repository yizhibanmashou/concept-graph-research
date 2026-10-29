"""Export paired original/deleted branches for exploratory human review."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def prepare(nodes, rules, ids, removed_pos):
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate target IDs')
    missing = set(ids) - nodes.keys()
    if missing or set(ids) - rules.keys():
        raise ValueError('some targets are absent from nodes or rules')
    output = []
    for head in ids:
        branches = rules[head]
        if any(not branch for branch in branches):
            raise ValueError(f'{head}: source contains an empty branch')
        if any(dep not in nodes for branch in branches for dep in branch):
            raise ValueError(f'{head}: dependency absent from nodes')
        reduced = [[d for d in branch if nodes[d]['pos'] not in removed_pos] for branch in branches]
        counts = {}
        for branch in reduced:
            if branch:
                key = tuple(sorted(set(branch)))
                counts[key] = counts.get(key, 0) + 1
        output.append({
            'head': head, 'lemmas': nodes[head]['lemmas'], 'definition': nodes[head]['definition'],
            'branches': [{'original': [node(d, nodes) for d in original],
                          'deleted': [node(d, nodes) for d in after],
                          'newly_empty': not after,
                          'review': {'source_fidelity': None, 'direction_or_negation_lost': None, 'notes': ''}}
                         for original, after in zip(branches, reduced)],
            'nonempty_collapsed_excess': sum(n - 1 for n in counts.values()),
        })
    return output


def node(node_id, nodes):
    row = nodes[node_id]
    return {key: row[key] for key in ('synset_id', 'lemmas', 'pos', 'definition')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--sample', type=Path, required=True, help='structure_sampling_pilot JSON')
    parser.add_argument('--pos', choices=('prep', 'prep-and-phrase'), default='prep')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    nodes_file = args.bundle / 'graph/nodes.tsv'
    rules_file = args.bundle / 'graph/hypergraph_rules.jsonl'
    sample = json.loads(args.sample.read_text(encoding='utf-8'))
    ids = [head for group in sorted(sample['sample_ids']) for head in sample['sample_ids'][group]]
    with nodes_file.open(encoding='utf-8-sig', newline='') as f:
        nodes = {r['synset_id']: r for r in csv.DictReader(f, delimiter='\t')}
    rules = {}
    with rules_file.open(encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            if row['head'] in ids:
                rules[row['head']] = row['clauses']
    removed = {'prep'} if args.pos == 'prep' else {'prep', 'prep_phrase'}
    result = {'removed_pos': sorted(removed), 'sample_size': len(ids),
              'inputs_sha256': {p.name: sha256(p) for p in (nodes_file, rules_file, args.sample)},
              'sampling': 'Preserves supplied sample order by sorted stratum; see source sample for seed and strata.',
              'limit': 'Structural deletion only; neither role-aware rewriting nor semantic correctness is established.',
              'items': prepare(nodes, rules, ids, removed)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(ids)} paired targets to {args.out}")


if __name__ == '__main__':
    main()
