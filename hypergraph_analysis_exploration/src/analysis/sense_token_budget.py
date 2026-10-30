"""Count WordPiece tokens in prepared A-D candidate serializations."""
import argparse
import hashlib
import json
import statistics
from pathlib import Path


def lengths(items, encode, budgets):
    if not items or not budgets or any(b <= 0 for b in budgets):
        raise ValueError('items and positive budgets required')
    rows = []
    for item in items:
        counts = {}
        for version in ('A', 'B', 'C', 'D'):
            text = json.dumps(item[version], sort_keys=True, ensure_ascii=False, separators=(',', ':'))
            counts[version] = len(encode(text))
        rows.append({'target': item['A']['target'], 'tokens': counts})
    summary = {}
    for version in ('A', 'B', 'C', 'D'):
        counts = [r['tokens'][version] for r in rows]
        summary[version] = {'min': min(counts), 'median': statistics.median(counts), 'max': max(counts),
                            'over_budget': {str(b): sum(x > b for x in counts) for b in budgets}}
    return {'items': rows, 'summary': summary}


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
    data = json.loads(raw)
    result = lengths(data['items'], lambda text: tokenizer.encode(text).ids, [128, 256, 512])
    result['inputs_sha256'] = {'sample': hashlib.sha256(raw).hexdigest(),
                               'vocab': hashlib.sha256(args.vocab.read_bytes()).hexdigest()}
    result['vocab_revision'] = args.vocab_revision
    result['tokenizers_version'] = tokenizers.__version__
    result['limits'] = 'Exploratory candidate-only sorted JSON; includes special tokens; no context, model, accuracy, or actual truncation.'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(json.dumps(result['summary'], ensure_ascii=False))


if __name__ == '__main__':
    main()
