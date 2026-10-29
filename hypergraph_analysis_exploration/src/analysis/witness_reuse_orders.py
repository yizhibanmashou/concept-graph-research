"""Explore fixed-capacity LRU sensitivity to repeated seeded root orders."""
import argparse
import json
import random
from pathlib import Path
from statistics import median

from src.analysis.witness_reuse_pilot import sha, simulate_lru


def compare(witnesses, roots, depth, capacities, seeds):
    if len(roots) != len(set(roots)) or not roots:
        raise ValueError('roots must be nonempty and unique')
    if len(seeds) != len(set(seeds)) or not seeds:
        raise ValueError('seeds must be nonempty and unique')
    if any(capacity < 0 for capacity in capacities) or len(capacities) != len(set(capacities)):
        raise ValueError('capacities must be distinct and nonnegative')
    rows = []
    for seed in seeds:
        order = random.Random(seed).sample(roots, len(roots))
        for capacity in capacities:
            rows.append({'seed': seed, **simulate_lru(witnesses, order, depth, capacity)})
    summaries = []
    for capacity in capacities:
        values = [row['computed_states'] for row in rows if row['capacity'] == capacity]
        summaries.append({'capacity': capacity, 'min_computed_states': min(values),
                          'median_computed_states': median(values), 'max_computed_states': max(values)})
    return {'root_count': len(roots), 'depth': depth, 'rows': rows, 'summaries': summaries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--roots', type=Path, required=True)
    parser.add_argument('--depth', type=int, default=4)
    parser.add_argument('--capacities', type=int, nargs='+', default=[0, 256, 4096])
    parser.add_argument('--seeds', type=int, nargs='+', default=[11, 17, 23, 31, 47])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if not 0 <= args.depth <= 20:
        parser.error('depth must be between 0 and 20')
    path = args.bundle / 'graph/coverage_witnesses.jsonl'
    with path.open(encoding='utf-8') as f:
        records = [json.loads(line) for line in f if line.strip()]
    witnesses = {r['head']: tuple(dict.fromkeys(r['witness_clause'])) for r in records}
    if len(witnesses) != len(records):
        raise ValueError('duplicate witness head')
    roots = args.roots.read_text(encoding='utf-8-sig').splitlines()
    result = {'metrics': compare(witnesses, roots, args.depth, args.capacities, args.seeds),
              'inputs_sha256': {'coverage_witnesses.jsonl': sha(path), 'root_ids': sha(args.roots)},
              'limits': 'Exploratory computational accounting for selected witnesses; not timing, semantic validation, or human learning.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result['metrics']['summaries']))


if __name__ == '__main__':
    main()
