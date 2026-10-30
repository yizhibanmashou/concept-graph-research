"""Rebuild an existing WSD pilot using target-centered context windows."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree
import zipfile

from src.analysis.semcor_train_mapping import digest, partition


def centered_window(prefix_ids, sentence_ids, target_indices, budget=32):
    if not target_indices or target_indices != list(range(target_indices[0], target_indices[-1] + 1)):
        raise ValueError('target must occupy contiguous sentence tokens')
    room = budget - len(prefix_ids)
    if room < len(target_indices):
        raise ValueError('target or prefix exceeds context budget')
    start = max(0, min(target_indices[0] - (room - len(target_indices)) // 2,
                       max(0, len(sentence_ids) - room)))
    window = sentence_ids[start:start + room]
    if not (start <= target_indices[0] and target_indices[-1] < start + len(window)):
        raise ValueError('target not retained')
    return prefix_ids + window


def replace_context(row, old_context, new_context, width):
    output = {'sample_id': row['sample_id'], 'label': row['label'], 'inputs': {}}
    for version in 'ABCD':
        output['inputs'][version] = []
        for sequence in row['inputs'][version]:
            expected = [101] + old_context + [102]
            if sequence[:len(expected)] != expected:
                raise ValueError('old prepared input does not match original context')
            end = len(sequence)
            while end and sequence[end - 1] == 0:
                end -= 1
            candidate = sequence[len(expected):end]
            if not candidate or candidate[-1] != 102:
                raise ValueError('candidate separator missing')
            replaced = [101] + new_context + [102] + candidate
            if len(replaced) > width:
                raise ValueError('joint budget exceeded')
            output['inputs'][version].append(replaced + [0] * (width - len(replaced)))
    return output


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
    if digest(args.vocab) != metadata['inputs_sha256']['vocab.txt'] or digest(args.nltk_data / 'corpora/semcor.zip') != metadata['inputs_sha256']['semcor.zip']:
        raise ValueError('vocabulary or corpus mismatch')
    original = {}
    output = {'train': {}, 'dev': {}}
    for subset in ('train', 'dev'):
        rows = json.loads((args.prepared / (subset + '.json')).read_text(encoding='utf-8'))
        original[subset] = {row['sample_id']: row for row in rows}
        if len(original[subset]) != len(rows):
            raise ValueError('duplicate sample')
    stats = {'train': Counter(), 'dev': Counter()}
    with zipfile.ZipFile(args.nltk_data / 'corpora/semcor.zip') as archive:
        for subset in ('train', 'dev'):
            for doc in split[subset]:
                with archive.open('semcor/' + doc) as f:
                    tree = ElementTree.parse(f).getroot()
                for sentence_index, sentence in enumerate(tree.iter('s')):
                    elements = list(sentence)
                    parts = [(e.text or '').replace('_', ' ') for e in elements]
                    text = ' '.join(parts)
                    annotated = [(i, e) for i, e in enumerate(elements) if e.tag == 'wf' and e.get('wnsn') and e.get('lexsn')]
                    for token_index, (index, token) in enumerate(annotated):
                        sample = hashlib.sha256(f'{doc}:{sentence_index}:{token_index}'.encode()).hexdigest()
                        if sample not in original[subset]:
                            continue
                        prefix = 'target: ' + (token.text or '').replace('_', ' ') + ' context: '
                        start = len(prefix) + sum(len(part) + 1 for part in parts[:index])
                        end = start + len(parts[index])
                        encoding = tokenizer.encode(prefix + text, add_special_tokens=False)
                        prefix_indices = [i for i, (_, b) in enumerate(encoding.offsets) if b <= len(prefix)]
                        context_indices = [i for i, (a, _) in enumerate(encoding.offsets) if a >= len(prefix)]
                        if prefix_indices + context_indices != list(range(len(encoding.ids))):
                            raise ValueError('token crosses prefix boundary')
                        target_indices = [j for j, i in enumerate(context_indices)
                                          if encoding.offsets[i][0] < end and encoding.offsets[i][1] > start]
                        prefix_ids = [encoding.ids[i] for i in prefix_indices]
                        context_ids = [encoding.ids[i] for i in context_indices]
                        centered = centered_window(prefix_ids, context_ids, target_indices)
                        output[subset][sample] = replace_context(original[subset][sample], encoding.ids[:32], centered, metadata['joint_budget'])
                        stats[subset]['target_fully_retained'] += 1
                        stats[subset]['sentence_truncated'] += len(prefix_ids) + len(context_ids) > 32
    if any(set(output[s]) != set(original[s]) for s in ('train', 'dev')):
        raise ValueError('selected samples not reconstructed')
    args.out.mkdir(parents=True, exist_ok=False)
    for subset in ('train', 'dev'):
        rows = [output[subset][sample] for sample in original[subset]]
        (args.out / (subset + '.json')).write_text(json.dumps(rows, sort_keys=True, separators=(',', ':')), encoding='utf-8')
    metadata['context_policy'] = 'target-centered-wordpiece-32/1'
    metadata['context_audit'] = {s: dict(stats[s]) for s in ('train', 'dev')}
    metadata['original_prepared_sha256'] = {f: digest(args.prepared / f) for f in ('train.json', 'dev.json', 'metadata.json')}
    (args.out / 'metadata.json').write_text(json.dumps(metadata, sort_keys=True, indent=2), encoding='utf-8')
    print(json.dumps(metadata['context_audit']))


if __name__ == '__main__':
    main()
