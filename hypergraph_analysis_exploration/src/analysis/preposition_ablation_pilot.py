"""Compare selected-witness frontiers with and without traversing prep nodes.

Descriptive pilot only: stopping at a preposition loses information and does not
produce a semantically equivalent graph. Uses the existing held-out root list.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def run(bundle, experiment, candidates, depth):
    nodes_file = bundle / 'graph/nodes.tsv'
    witnesses_file = bundle / 'graph/coverage_witnesses.jsonl'
    roots_file = experiment / 'evaluation_root_ids.txt'
    with nodes_file.open(encoding='utf-8-sig', newline='') as f:
        nodes = {r['synset_id']: r for r in csv.DictReader(f, delimiter='\t')}
    witness = {}
    with witnesses_file.open(encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            witness[row['head']] = set(row['witness_clause'])
    roots = roots_file.read_text(encoding='utf-8-sig').splitlines()
    pairs = json.loads(candidates.read_text(encoding='utf-8'))['top20']
    pair_ids = [tuple(n['id'] for n in p['pair']) for p in pairs]
    stats = {'original_frontier_total': 0, 'cut_frontier_total': 0,
             'roots_with_prep_encountered': 0, 'roots_with_changed_frontier': 0}
    counts = [[0, 0] for _ in pair_ids]
    for root in roots:
        original, cut = {root}, {root}
        encountered = False
        for _ in range(depth):
            original = set().union(*(witness[x] if nodes[x]['is_basis'].lower() != 'true' else {x} for x in original)) if original else set()
            next_cut = set()
            for x in cut:
                if nodes[x]['pos'] == 'prep':
                    encountered = True
                elif nodes[x]['is_basis'].lower() == 'true':
                    next_cut.add(x)
                else:
                    next_cut.update(witness[x])
            cut = next_cut
        # Remove prepositions reached exactly at the depth boundary as well.
        if any(nodes[x]['pos'] == 'prep' for x in cut): encountered = True
        cut = {x for x in cut if nodes[x]['pos'] != 'prep'}
        stats['roots_with_prep_encountered'] += encountered
        stats['roots_with_changed_frontier'] += original != cut
        stats['original_frontier_total'] += len(original)
        stats['cut_frontier_total'] += len(cut)
        for i, (a, b) in enumerate(pair_ids):
            counts[i][0] += a in original and b in original
            counts[i][1] += a in cut and b in cut
    return {'analysis': 'selected-witness-preposition-cut-pilot/1', 'depth': depth,
            'roots': len(roots), 'stats': stats,
            'inputs_sha256': {str(p.name): digest(p) for p in [nodes_file, witnesses_file, roots_file, candidates]},
            'pairs': [{'ids': pair_ids[i], 'labels': [v['lemmas'] for v in row['pair']],
                       'original_support': counts[i][0], 'cut_support': counts[i][1]}
                      for i, row in enumerate(pairs)],
            'limits': 'Descriptive intervention, not semantic preservation, re-ranking, randomized significance or independent validation. Cut paths lose all downstream content.'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bundle', type=Path, default=PROJECT.parent / 'OEWN')
    parser.add_argument('--depth', type=int, default=3)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.depth < 1: parser.error('depth must be positive')
    exp = PROJECT / 'outputs/experiment_2026_10_13'
    candidates = PROJECT / 'outputs/weekly_experiment_2026-10-20/preposition_filtered_screen.json'
    result = run(args.bundle, exp, candidates, args.depth)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f: json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result['stats'], ensure_ascii=False))

if __name__ == '__main__': main()
