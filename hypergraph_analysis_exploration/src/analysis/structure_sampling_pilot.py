"""Count one-hop structures and sample exploratory candidates by stratum."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = PROJECT.parent / 'OEWN'


def summarize(rules, positions, sample_size=5, seed=17):
    if sample_size < 0:
        raise ValueError('sample_size must be nonnegative')
    rng = random.Random(seed)
    counts = Counter()
    samples = defaultdict(list)
    seen_heads = set()
    for rule in rules:
        head, clauses = rule['head'], rule['clauses']
        if head in seen_heads:
            raise ValueError('duplicate head: ' + head)
        seen_heads.add(head)
        if not clauses:
            raise ValueError('head without clauses: ' + head)
        if any(not clause for clause in clauses):
            raise ValueError('empty clause: ' + head)
        deps = {item for clause in clauses for item in clause}
        if any(item not in positions for item in deps):
            raise ValueError('dependency missing from node inventory')
        branch = 'multi' if len(clauses) > 1 else 'single'
        joint = 'joint' if any(len(clause) > 1 for clause in clauses) else 'singleton'
        prep = 'prep' if any(positions[x] in {'prep', 'prep_phrase'} for x in deps) else 'no_prep'
        key = '/'.join((branch, joint, prep))
        counts[key] += 1
        bucket = samples[key]
        if len(bucket) < sample_size:
            bucket.append(head)
        elif sample_size:
            index = rng.randrange(counts[key])
            if index < sample_size:
                bucket[index] = head
    return {'counts': dict(sorted(counts.items())),
            'sample_ids': {key: samples[key] for key in sorted(counts)},
            'seed': seed, 'sample_size_per_stratum': sample_size}


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument('--sample-size', type=int, default=5)
    parser.add_argument('--seed', type=int, default=17)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    node_file = args.bundle / 'graph/nodes.tsv'
    rules_file = args.bundle / 'graph/hypergraph_rules.jsonl'
    with node_file.open(encoding='utf-8-sig', newline='') as stream:
        positions = {r['synset_id']: r['pos'] for r in csv.DictReader(stream, delimiter='\t')}
    with rules_file.open(encoding='utf-8') as stream:
        result = summarize((json.loads(line) for line in stream if line.strip()), positions,
                           args.sample_size, args.seed)
    result['input_sha256'] = {p.name: sha256(p) for p in (node_file, rules_file)}
    result['notice'] = 'Exploratory graph sampling; not a benchmark, semantic label, or a leakage-safe evaluation split.'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'counts': result['counts'], 'output': str(args.out)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
