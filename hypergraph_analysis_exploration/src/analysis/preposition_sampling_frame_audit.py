"""Audit anonymized target strata for a future T02 fidelity sample."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def classify_target(clauses, pos_by_node):
    """Return a structural-deletion stratum without reading glosses or labels."""
    reduced = [[node for node in clause if pos_by_node[node] != 'prep'] for clause in clauses]
    signatures = Counter(tuple(sorted(set(clause))) for clause in reduced if clause)
    collision_excess = sum(count - 1 for count in signatures.values())
    new_empty = any(not clause for clause in reduced)
    affected = any(before != after for before, after in zip(clauses, reduced))
    if new_empty and collision_excess:
        category = 'empty_and_collision'
    elif new_empty:
        category = 'new_empty'
    elif collision_excess:
        category = 'new_collision'
    elif affected:
        category = 'other_affected'
    else:
        category = 'unaffected'
    return category


def summarize_strata(target_counts, branch_counts):
    """Summarize target prevalence and branch-level review workload by stratum."""
    summary = {}
    for category in sorted(set(target_counts) | set(branch_counts)):
        targets = target_counts[category]
        branches = branch_counts[category]
        summary[category] = {
            'targets': targets,
            'branches': branches,
            'mean_branches_per_target': branches / targets if targets else None,
        }
    return summary


def audit(nodes_path, rules_path):
    with nodes_path.open(encoding='utf-8-sig', newline='') as stream:
        nodes = {row['synset_id']: row for row in csv.DictReader(stream, delimiter='\t')}
    pos_by_node = {identity: row['pos'] for identity, row in nodes.items()}
    source_root_by_node = {identity: row.get('source_root') or 'missing' for identity, row in nodes.items()}
    by_class = Counter()
    by_pos_class = Counter()
    by_root_class = Counter()
    branches_by_class = Counter()
    source_root_sizes = Counter()
    targets = 0
    with rules_path.open(encoding='utf-8') as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            head = row['head']
            category = classify_target(row['clauses'], pos_by_node)
            pos = nodes[head]['pos']
            source_root = source_root_by_node[head]
            targets += 1
            by_class[category] += 1
            branches_by_class[category] += len(row['clauses'])
            by_pos_class[(pos, category)] += 1
            by_root_class[(source_root, category)] += 1
            source_root_sizes[source_root] += 1
    return {
        'schema': 'preposition-sampling-frame-audit/2',
        'targets': targets,
        'source_root_group_count': len(source_root_sizes),
        'source_root_size_distribution': sorted(source_root_sizes.values()),
        'by_effect_class': dict(sorted(by_class.items())),
        'by_effect_class_review_workload': summarize_strata(by_class, branches_by_class),
        'by_pos_and_effect_class': [
            {'pos': pos, 'effect_class': category, 'targets': count}
            for (pos, category), count in sorted(by_pos_class.items())
        ],
        'by_source_root_and_effect_class': [
            {'source_root': root, 'effect_class': category, 'targets': count}
            for (root, category), count in sorted(by_root_class.items())
        ],
        'inputs_sha256': {'nodes.tsv': sha256(nodes_path),
                          'hypergraph_rules.jsonl': sha256(rules_path)},
        'limits': [
            'Uses POS-only prep deletion; does not inspect definitions, semantic labels, or reviewer data.',
            'source_root labels describe construction lineage and are not verified independent dictionary families.',
            'Counts define a stratified finite-graph sample frame; they do not define a semantic estimand or sample size.',
            'Branch counts are workload proxies only; they do not account for definition length, reviewer time, or disagreement.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True, help='new local output file')
    args = parser.parse_args()
    result = audit(args.bundle / 'graph/nodes.tsv', args.bundle / 'graph/hypergraph_rules.jsonl')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps({'targets': result['targets'],
                      'source_root_group_count': result['source_root_group_count'],
                      'by_effect_class': result['by_effect_class']}))


if __name__ == '__main__':
    main()
