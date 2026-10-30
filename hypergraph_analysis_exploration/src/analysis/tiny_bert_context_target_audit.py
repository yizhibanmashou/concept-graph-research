"""Audit whether context truncation retains the annotated target occurrence."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree
import zipfile

from src.analysis.semcor_train_mapping import digest, partition


def classify_target(offsets, target_start, target_end, cutoff):
    positions = [i for i, (start, end) in enumerate(offsets)
                 if end > start and start < target_end and end > target_start]
    if not positions:
        return 'unlocatable'
    retained = sum(i < cutoff for i in positions)
    return 'full' if retained == len(positions) else ('none' if retained == 0 else 'partial')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nltk-data', type=Path, required=True)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--vocab', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    import nltk
    import tokenizers
    nltk.data.path = [str(args.nltk_data.resolve())]
    from nltk.corpus import semcor
    split = partition(semcor.fileids())
    tokenizer = tokenizers.BertWordPieceTokenizer(str(args.vocab), lowercase=True)
    metadata = json.loads((args.prepared / 'metadata.json').read_text(encoding='utf-8'))
    if digest(args.vocab) != metadata['inputs_sha256']['vocab.txt']:
        raise ValueError('vocabulary mismatch')
    if digest(args.nltk_data / 'corpora/semcor.zip') != metadata['inputs_sha256']['semcor.zip']:
        raise ValueError('corpus mismatch')
    selected = {}
    for subset in ('train', 'dev'):
        rows = json.loads((args.prepared / (subset + '.json')).read_text(encoding='utf-8'))
        selected[subset] = {r['sample_id']: r['inputs']['A'][0] for r in rows}
        if len(selected[subset]) != len(rows):
            raise ValueError('duplicate sample')
    counts = {'train': Counter(), 'dev': Counter()}
    seen = {'train': set(), 'dev': set()}
    with zipfile.ZipFile(args.nltk_data / 'corpora/semcor.zip') as archive:
        for subset in ('train', 'dev'):
            for doc in split[subset]:
                with archive.open('semcor/' + doc) as f:
                    tree = ElementTree.parse(f).getroot()
                for sentence_index, sentence in enumerate(tree.iter('s')):
                    elements = list(sentence)
                    parts = [(e.text or '').replace('_', ' ') for e in elements]
                    sentence_text = ' '.join(parts)
                    annotated = [(i, e) for i, e in enumerate(elements)
                                 if e.tag == 'wf' and e.get('wnsn') and e.get('lexsn')]
                    for token_index, (index, token) in enumerate(annotated):
                        sample = hashlib.sha256(f'{doc}:{sentence_index}:{token_index}'.encode('utf-8')).hexdigest()
                        if sample not in selected[subset]:
                            continue
                        prefix = 'target: ' + (token.text or '').replace('_', ' ') + ' context: '
                        start = len(prefix) + sum(len(part) + 1 for part in parts[:index])
                        end = start + len(parts[index])
                        encoding = tokenizer.encode(prefix + sentence_text, add_special_tokens=False)
                        expected_prefix = [101] + encoding.ids[:32] + [102]
                        if selected[subset][sample][:len(expected_prefix)] != expected_prefix:
                            raise ValueError('prepared context tokens do not match reconstructed input')
                        counts[subset][classify_target(encoding.offsets, start, end, 32)] += 1
                        seen[subset].add(sample)
    if any(seen[subset] != set(selected[subset]) for subset in ('train', 'dev')):
        raise ValueError('could not reconstruct all selected targets')
    result = {'protocol': 'tiny-bert-target-offset-audit/1', 'cutoff': 32,
              'counts': {subset: {'selected': len(selected[subset]), **dict(counts[subset])} for subset in ('train', 'dev')},
              'inputs_sha256': {'semcor.zip': digest(args.nltk_data / 'corpora/semcor.zip'),
                  'vocab.txt': digest(args.vocab), 'train.json': digest(args.prepared / 'train.json'),
                  'dev.json': digest(args.prepared / 'dev.json')},
              'tokenizers_version': tokenizers.__version__,
              'limits': 'Post-hoc covered training/development samples; target prefix may still remain. Does not assess performance or held-out documents.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
