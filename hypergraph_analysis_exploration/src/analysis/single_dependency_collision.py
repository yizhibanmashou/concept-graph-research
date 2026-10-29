"""Count head-level collisions caused by removing one dependency at a time."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def analyze(rows, pos):
    usage = Counter()
    collisions = Counter()
    empty = Counter()
    totals = Counter()
    prep_head_min = Counter()
    prep_pair_difference = Counter()
    prep_excess = 0
    for row in rows:
        branches = {frozenset(branch) for branch in row['clauses']}
        if not branches or frozenset() in branches:
            raise ValueError('source contains no branch or an empty branch')
        deps = set().union(*branches)
        if any(dep not in pos for dep in deps):
            raise ValueError('dependency absent from node inventory')
        totals['heads'] += 1
        totals['distinct_nonempty_branches'] += len(branches)
        totals['heads_with_multiple_branches'] += len(branches) > 1
        usage.update(deps)
        empty.update(next(iter(branch)) for branch in branches if len(branch) == 1)
        affected = set()
        for branch in branches:
            if len(branch) < 2:
                continue
            for dep in branch:
                if branch - {dep} in branches:
                    affected.add(dep)
        collisions.update(affected)
        projected = defaultdict(list)
        for branch in branches:
            after = frozenset(dep for dep in branch if pos[dep] != 'prep')
            if after:
                projected[after].append(branch)
        head_differences = []
        for group in projected.values():
            if len(group) < 2:
                continue
            prep_excess += len(group) - 1
            for i, left in enumerate(group):
                for right in group[i + 1:]:
                    difference = len(left.symmetric_difference(right))
                    prep_pair_difference[difference] += 1
                    head_differences.append(difference)
        if head_differences:
            prep_head_min[min(head_differences)] += 1
    groups = defaultdict(lambda: {'nodes_used': 0, 'node_head_uses': 0,
                                  'nodes_with_collisions': 0, 'collision_node_head_pairs': 0,
                                  'nodes_with_empty': 0, 'empty_node_head_pairs': 0})
    details = []
    for node, n in usage.items():
        group = pos[node] if pos[node] in {'prep', 'prep_phrase'} else 'other'
        groups[group]['nodes_used'] += 1
        groups[group]['node_head_uses'] += n
        groups[group]['nodes_with_collisions'] += collisions[node] > 0
        groups[group]['collision_node_head_pairs'] += collisions[node]
        groups[group]['nodes_with_empty'] += empty[node] > 0
        groups[group]['empty_node_head_pairs'] += empty[node]
        if collisions[node] or empty[node]:
            details.append({'id': node, 'pos': pos[node], 'head_uses': n,
                            'collision_heads': collisions[node], 'empty_heads': empty[node]})
    return {'totals': dict(totals), 'groups': dict(groups),
            'posthoc_all_prep_projection': {'affected_heads': sum(prep_head_min.values()),
                                           'collapsed_excess': prep_excess,
                                           'heads_by_min_symmetric_difference': dict(sorted(prep_head_min.items())),
                                           'pairs_by_symmetric_difference': dict(sorted(prep_pair_difference.items()))},
            'nodes': sorted(details, key=lambda x: (-x['collision_heads'], x['id']))}


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    nodes_path = args.bundle / 'graph/nodes.tsv'
    rules_path = args.bundle / 'graph/hypergraph_rules.jsonl'
    with nodes_path.open(encoding='utf-8-sig', newline='') as f:
        pos = {r['synset_id']: r['pos'] for r in csv.DictReader(f, delimiter='\t')}
    with rules_path.open(encoding='utf-8') as f:
        result = analyze((json.loads(line) for line in f if line.strip()), pos)
    result['inputs_sha256'] = {p.name: sha256(p) for p in (nodes_path, rules_path)}
    result['limits'] = 'Single-node set projection only; not semantic equivalence or evidence for deleting all prepositions.'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(json.dumps({'totals': result['totals'], 'groups': result['groups'],
                      'posthoc_all_prep_projection': result['posthoc_all_prep_projection']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
