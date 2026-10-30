"""Audit a compact local-alias serialization for shared branch budgets."""
import argparse
import hashlib
from itertools import combinations
import json
from pathlib import Path

def representations(item, branches):
    definitions = {entry['id']: entry['gloss'] for entry in item['B']['dependencies']}
    ids = sorted({dep for branch in branches for dep in branch})
    if any(dep not in definitions for dep in ids):
        raise ValueError('branch dependency missing from inventory')
    aliases = {node: f'd{i}' for i, node in enumerate(ids)}
    a = {'gloss': item['A']['gloss']}
    b = {**a, 'deps': [{'id': aliases[node], 'gloss': definitions[node]} for node in ids]}
    # C is the simple undirected 2-section of the selected AND branches:
    # connect two dependencies iff they co-occur in at least one branch.
    # D retains the branch partition that this projection intentionally loses.
    edges = {
        tuple(sorted((aliases[left], aliases[right])))
        for branch in branches
        for left, right in combinations(sorted(set(branch)), 2)
    }
    c = {**b, 'edges': [list(edge) for edge in sorted(edges)]}
    d = {**b, 'branches': [[aliases[node] for node in branch] for branch in branches]}
    return {'A': a, 'B': b, 'C': c, 'D': d}, aliases


def pack(item, encode, budget):
    original = item['D']['branches']
    if not original or any(not branch for branch in original):
        raise ValueError('source must have nonempty branches')
    inventory = {entry['id'] for entry in item['B']['dependencies']}
    if set().union(*map(set, original)) != inventory:
        raise ValueError('branch union differs from dependency inventory')

    def counts(branches):
        representations_, _ = representations(item, branches)
        return {v: len(encode(json.dumps(representations_[v], sort_keys=True, ensure_ascii=False,
                                         separators=(',', ':')))) for v in 'ABCD'}

    selected = []
    selected_indices = []
    base = counts([])
    if max(base.values()) > budget:
        return {'target': item['A']['target'], 'status': 'base_over_budget', 'selected_indices': [],
                'original_branches': len(original), 'selected_branches': 0, 'tokens': base}
    for index, branch in enumerate(original):
        proposal = selected + [branch]
        if max(counts(proposal).values()) <= budget:
            selected = proposal
            selected_indices.append(index)
    return {'target': item['A']['target'],
            'status': 'none' if not selected else 'all' if len(selected) == len(original) else 'partial',
            'selected_indices': selected_indices, 'original_branches': len(original),
            'selected_branches': len(selected), 'tokens': counts(selected)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--vocab', type=Path, required=True)
    parser.add_argument('--vocab-revision', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    import tokenizers
    tokenizer = tokenizers.BertWordPieceTokenizer(str(args.vocab), lowercase=True)
    raw = args.input.read_bytes()
    items = json.loads(raw)['items']
    if not items:
        raise ValueError('no candidate records')
    runs = {}
    for budget in (128, 256, 512):
        rows = [pack(item, lambda text: tokenizer.encode(text).ids, budget) for item in items]
        runs[str(budget)] = {'statuses': {key: sum(r['status'] == key for r in rows)
                                        for key in ('all', 'partial', 'none', 'base_over_budget')},
                             'original_branches': sum(r['original_branches'] for r in rows),
                             'selected_branches': sum(r['selected_branches'] for r in rows), 'items': rows}
    result = {'runs': runs, 'vocab_revision': args.vocab_revision, 'tokenizers_version': tokenizers.__version__,
              'inputs_sha256': {'sample': hashlib.sha256(raw).hexdigest(),
                                'vocab': hashlib.sha256(args.vocab.read_bytes()).hexdigest()},
              'limits': 'Post-hoc candidate-only compact aliases, original branch order; no context, semantic labels, model performance or optimality guarantee.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps({budget: {'statuses': run['statuses'], 'selected_branches': run['selected_branches'],
                              'original_branches': run['original_branches']} for budget, run in runs.items()}))


if __name__ == '__main__':
    main()
