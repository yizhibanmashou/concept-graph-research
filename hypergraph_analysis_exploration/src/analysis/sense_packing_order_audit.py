"""Audit branch identity and count sensitivity to greedy branch ordering."""
import argparse
import copy
import hashlib
import json
import random
from pathlib import Path

from src.analysis.sense_budget_packing import pack


def chosen(item, packed):
    branches = item['D']['branches']
    return sorted(tuple(sorted(branches[index])) for index in packed['selected_indices'])


def audit(items, encode, budget, seeds):
    if not items or not seeds or len(seeds) != len(set(seeds)):
        raise ValueError('nonempty items and distinct seeds required')
    results = []
    for item in items:
        original = pack(item, encode, budget)
        reference = chosen(item, original)
        alternatives = []
        for seed in seeds:
            shuffled = copy.deepcopy(item)
            random.Random(seed).shuffle(shuffled['D']['branches'])
            result = pack(shuffled, encode, budget)
            alternatives.append({'seed': seed,
                                 'selected_count': result['selected_branches'],
                                 'identity_changed': chosen(shuffled, result) != reference})
        results.append({'target': item['A']['target'], 'baseline_count': original['selected_branches'],
                        'count_changed': any(row['selected_count'] != original['selected_branches'] for row in alternatives),
                        'identity_changed': any(row['identity_changed'] for row in alternatives),
                        'shuffles': alternatives})
    return {'items': results, 'count_changed_targets': sum(r['count_changed'] for r in results),
            'identity_changed_targets': sum(r['identity_changed'] for r in results)}


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
    seeds = list(range(10))
    runs = {str(b): audit(items, lambda text: tokenizer.encode(text).ids, b, seeds) for b in (128, 256, 512)}
    result = {'seeds': seeds, 'runs': runs, 'vocab_revision': args.vocab_revision,
              'tokenizers_version': tokenizers.__version__,
              'inputs_sha256': {'sample': hashlib.sha256(raw).hexdigest(),
                                'vocab': hashlib.sha256(args.vocab.read_bytes()).hexdigest()},
              'limits': 'Post-hoc greedy ordering sensitivity; no semantic correctness, context or independent benchmark.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps({b: {'count_changed_targets': r['count_changed_targets'],
                          'identity_changed_targets': r['identity_changed_targets']} for b, r in runs.items()}))


if __name__ == '__main__':
    main()
