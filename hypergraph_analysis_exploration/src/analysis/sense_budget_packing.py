"""Greedily preserve whole branches under a shared A-D candidate budget."""
import argparse
import hashlib
import json
from pathlib import Path

from src.analysis.sense_representation_pilot import build
from src.analysis.sense_token_budget import lengths


def pack(item, encode, budget):
    head = item['A']['target']
    definition = item['A']['gloss']
    definitions = {entry['id']: entry['gloss'] for entry in item['B']['dependencies']}
    original = item['D']['branches']
    if not original or any(not branch for branch in original):
        raise ValueError('original branches must be nonempty')
    if set().union(*map(set, original)) != definitions.keys():
        raise ValueError('branches and dependency inventory differ')

    def compose(branches):
        return build(head, definition, branches, definitions)

    def token_counts(value):
        return lengths([value], encode, [budget])['items'][0]['tokens']

    selected = []
    base = compose(selected)
    if max(token_counts(base).values()) > budget:
        return {'target': head, 'status': 'base_over_budget', 'original_branches': len(original),
                'selected_branches': 0, 'selected_indices': [], 'tokens': token_counts(base)}
    selected_indices = []
    for index, branch in enumerate(original):
        proposal = selected + [branch]
        if max(token_counts(compose(proposal)).values()) <= budget:
            selected = proposal
            selected_indices.append(index)
    counts = token_counts(compose(selected))
    status = 'none' if not selected else 'all' if len(selected) == len(original) else 'partial'
    return {'target': head, 'status': status, 'original_branches': len(original),
            'selected_branches': len(selected), 'selected_indices': selected_indices, 'tokens': counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--vocab', type=Path, required=True)
    parser.add_argument('--vocab-revision', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    import tokenizers
    tokenizer = tokenizers.BertWordPieceTokenizer(str(args.vocab), lowercase=True)
    encode = lambda text: tokenizer.encode(text).ids
    raw = args.input.read_bytes()
    items = json.loads(raw)['items']
    if not items:
        raise ValueError('no candidate records')
    runs = {}
    for budget in (128, 256, 512):
        rows = [pack(item, encode, budget) for item in items]
        statuses = {key: sum(r['status'] == key for r in rows)
                    for key in ('all', 'partial', 'none', 'base_over_budget')}
        runs[str(budget)] = {'statuses': statuses, 'original_branches': sum(r['original_branches'] for r in rows),
                             'selected_branches': sum(r['selected_branches'] for r in rows), 'items': rows}
    result = {'runs': runs, 'vocab_revision': args.vocab_revision, 'tokenizers_version': tokenizers.__version__,
              'inputs_sha256': {'sample': hashlib.sha256(raw).hexdigest(),
                                'vocab': hashlib.sha256(args.vocab.read_bytes()).hexdigest()},
              'limits': 'Candidate-only greedy branch selection; no context, semantic labels, model performance or optimality guarantee.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps({budget: {'statuses': run['statuses'], 'selected_branches': run['selected_branches'],
                              'original_branches': run['original_branches']} for budget, run in runs.items()}))


if __name__ == '__main__':
    main()
