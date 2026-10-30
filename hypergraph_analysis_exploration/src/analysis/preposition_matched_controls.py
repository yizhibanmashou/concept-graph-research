"""Match dependency nodes by head frequency and compare batch deletion effects."""
import argparse
import csv
import hashlib
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path


def match(usage, pos, prep_seed, control_seeds):
    pools = defaultdict(lambda: {'prep': [], 'control': []})
    for node, freq in usage.items():
        group = 'prep' if pos[node] == 'prep' else 'control' if pos[node] != 'prep_phrase' else None
        if group:
            pools[freq][group].append(node)
    rng = random.Random(prep_seed)
    chosen = set()
    strata = []
    for freq, groups in sorted(pools.items()):
        a, b = sorted(groups['prep']), sorted(groups['control'])
        count = min(len(a), len(b))
        if count:
            chosen.update(rng.sample(a, count))
            strata.append((freq, count, b))
    controls = []
    for seed in control_seeds:
        rng = random.Random(seed)
        selection = set()
        for _, count, candidates in strata:
            selection.update(rng.sample(candidates, count))
        controls.append(selection)
    return chosen, controls


def effects(rows, removed):
    stats = Counter()
    for row in rows:
        branches = {frozenset(b) for b in row['clauses']}
        if not branches or frozenset() in branches:
            raise ValueError('source contains empty or missing branches')
        reduced = [branch - removed for branch in branches]
        new_empty = sum(not branch for branch in reduced)
        remaining = [branch for branch in reduced if branch]
        excess = len(remaining) - len(set(remaining))
        stats['heads'] += 1
        stats['changed_heads'] += any(a != b for a, b in zip(branches, reduced))
        stats['new_empty_branches'] += new_empty
        stats['heads_with_new_empty'] += new_empty > 0
        stats['collision_heads'] += excess > 0
        stats['collision_excess'] += excess
    return dict(stats)


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--prep-seed', type=int, default=17)
    parser.add_argument('--control-start', type=int, default=100)
    parser.add_argument('--replicates', type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.replicates <= 100:
        parser.error('replicates must be between 1 and 100')
    nodes = args.bundle / 'graph/nodes.tsv'
    rules = args.bundle / 'graph/hypergraph_rules.jsonl'
    with nodes.open(encoding='utf-8-sig', newline='') as f:
        pos = {r['synset_id']: r['pos'] for r in csv.DictReader(f, delimiter='\t')}
    with rules.open(encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    usage = Counter()
    for row in rows:
        deps = {d for branch in row['clauses'] for d in branch}
        if any(d not in pos for d in deps):
            raise ValueError('missing dependency POS')
        usage.update(deps)
    seeds = list(range(args.control_start, args.control_start + args.replicates))
    prep, controls = match(usage, pos, args.prep_seed, seeds)
    if not prep:
        raise ValueError('no matched nodes')
    def identity(selection):
        return digest_bytes('\n'.join(sorted(selection)).encode('utf-8'))
    all_prep = {n for n in usage if pos[n] == 'prep'}
    rows_out = [{'seed': seed, 'selection_sha256': identity(selected), 'metrics': effects(rows, selected)}
                for seed, selected in zip(seeds, controls)]
    summary = {}
    for key in rows_out[0]['metrics']:
        values = [r['metrics'][key] for r in rows_out]
        summary[key] = {'min': min(values), 'median': statistics.median(values), 'max': max(values)}
    result = {'inputs_sha256': {p.name: digest_bytes(p.read_bytes()) for p in (nodes, rules)},
              'matching': {'prep_seed': args.prep_seed, 'control_seeds': seeds, 'all_prep_nodes': len(all_prep),
                           'matched_prep_nodes': len(prep), 'all_prep_node_head_uses': sum(usage[n] for n in all_prep),
                           'matched_prep_node_head_uses': sum(usage[n] for n in prep),
                           'prep_selection_sha256': identity(prep)},
              'prep_metrics': effects(rows, prep), 'control_runs': rows_out, 'control_summary': summary,
              'limits': 'Exploratory exact head-frequency matching; selected low-frequency subset; not semantic validation or causal evidence.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, sort_keys=True)
    print(json.dumps({'matching': result['matching'], 'prep_metrics': result['prep_metrics'], 'control_summary': summary}, ensure_ascii=False))


if __name__ == '__main__':
    main()
