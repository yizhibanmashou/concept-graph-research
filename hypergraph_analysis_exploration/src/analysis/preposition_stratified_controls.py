"""Post-hoc source and branch-count stratification of matched deletions."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from src.analysis.preposition_matched_controls import match


def stratify(rows, nodes, removed):
    strata = defaultdict(Counter)
    for row in rows:
        old = {frozenset(b) for b in row['clauses']}
        if not old or frozenset() in old:
            raise ValueError('source contains empty or missing branches')
        head = nodes[row['head']]
        group = (head['source_root'], head['pos'], 'one' if len(old) == 1 else 'two' if len(old) == 2 else 'three_or_more')
        reduced = [branch - removed for branch in old]
        nonempty = [branch for branch in reduced if branch]
        strata[group]['heads'] += 1
        strata[group]['changed_heads'] += any(branch & removed for branch in old)
        strata[group]['collision_heads'] += len(nonempty) > len(set(nonempty))
        strata[group]['heads_with_new_empty'] += any(not branch for branch in reduced)
    return [{'source_root': s, 'head_pos': p, 'branch_bin': b, **dict(values)}
            for (s, p, b), values in sorted(strata.items())]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    node_file = args.bundle / 'graph/nodes.tsv'
    rule_file = args.bundle / 'graph/hypergraph_rules.jsonl'
    with node_file.open(encoding='utf-8-sig', newline='') as f:
        nodes = {r['synset_id']: r for r in csv.DictReader(f, delimiter='\t')}
    with rule_file.open(encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    usage = Counter()
    for row in rows:
        usage.update({d for b in row['clauses'] for d in b})
    prep, controls = match(usage, {n: v['pos'] for n, v in nodes.items()}, 17, list(range(100, 120)))
    result = {'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (node_file, rule_file)},
              'prep_seed': 17, 'control_seeds': list(range(100, 120)),
              'prep': stratify(rows, nodes, prep),
              'controls': [{'seed': seed, 'strata': stratify(rows, nodes, selected)}
                           for seed, selected in zip(range(100, 120), controls)],
              'limits': 'Post-hoc descriptive strata on one graph; no semantic judgments, causal claims, or independent replication.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"Stratified {len(rows)} targets; {len(result['prep'])} strata; 20 controls.")


if __name__ == '__main__':
    main()
