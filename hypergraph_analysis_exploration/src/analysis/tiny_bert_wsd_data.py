"""Prepare fixed train/dev token IDs for a small WSD cross-encoder pilot."""
import argparse
import csv
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path

from src.analysis.audit_wn30_oewn_sense_key_crosswalk import _load_oewn_sense_keys
from src.analysis.compact_sense_budget import pack, representations
from src.analysis.semcor_dev_pilot import build_index, mapped_target, observed_key, sentences
from src.analysis.semcor_train_mapping import digest, partition
from src.analysis.sense_representation_pilot import build


def stable_hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def choose_candidates(instance_id, candidate_ids, maximum=4):
    """Return the complete deterministic candidate order (or a legacy bounded view)."""
    ordered = sorted(set(candidate_ids), key=lambda value: (stable_hash(instance_id + ':' + value), value))
    return ordered if maximum is None else ordered[:maximum]


def prepare_candidate_manifest(candidate_ids, prepare):
    """Attempt every candidate and retain success or a specific failure per ID.

    ``prepare`` returns the candidate payload on success and may raise an
    exception; exception text is retained as the failure reason.
    """
    manifest = []
    for candidate_id in candidate_ids:
        try:
            payload = prepare(candidate_id)
        except Exception as exc:  # candidate-local failures must not erase the target
            manifest.append({'candidate_id': candidate_id, 'status': 'failed',
                             'failure_reason': f'{type(exc).__name__}: {exc}'})
        else:
            if payload is None:
                manifest.append({'candidate_id': candidate_id, 'status': 'failed',
                                 'failure_reason': 'preparation returned no payload'})
            else:
                manifest.append({'candidate_id': candidate_id, 'status': 'ready',
                                 'failure_reason': None, 'payload': payload})
    return manifest


def select(records, n):
    return sorted(records, key=lambda row: (row['sample_id'], row['doc'], row['sentence'], row['token']))[:n]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nltk-data', type=Path, required=True)
    parser.add_argument('--oewn-zip', type=Path, required=True)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--vocab', type=Path, required=True)
    parser.add_argument('--candidate-budget', type=int, choices=(94, 222), default=94)
    parser.add_argument('--out', type=Path, required=True, help='new directory')
    args = parser.parse_args()
    import nltk
    import tokenizers
    nltk.data.path = [str(args.nltk_data.resolve())]
    from nltk.corpus import semcor, wordnet
    if wordnet.get_version() != '3.0':
        raise ValueError('expected WordNet 3.0')
    split = partition(semcor.fileids())
    with zipfile.ZipFile(args.oewn_zip) as archive:
        mapping = _load_oewn_sense_keys(archive)
    nodes_file = args.bundle / 'graph/nodes.tsv'
    rules_file = args.bundle / 'graph/hypergraph_rules.jsonl'
    with nodes_file.open(encoding='utf-8-sig', newline='') as f:
        nodes = {row['synset_id']: row for row in csv.DictReader(f, delimiter='\t')}
    with rules_file.open(encoding='utf-8') as f:
        rules = {row['head']: row['clauses'] for row in (json.loads(line) for line in f if line.strip())}
    definitions = {key: value['definition'] for key, value in nodes.items()}
    index = build_index(nodes.values())
    tokenizer = tokenizers.BertWordPieceTokenizer(str(args.vocab), lowercase=True)
    cls_id, sep_id, pad_id = (tokenizer.token_to_id(x) for x in ('[CLS]', '[SEP]', '[PAD]'))
    if (cls_id, sep_id, pad_id) != (101, 102, 0):
        raise ValueError('expected BERT special token IDs 101, 102 and 0')
    cache = {}

    def candidate(candidate_id):
        if candidate_id not in cache:
            if candidate_id not in rules:
                raise ValueError('candidate has no graph rule')
            if candidate_id not in nodes:
                raise ValueError('candidate has no node definition')
            item = build(candidate_id, nodes[candidate_id]['definition'], rules[candidate_id], definitions)
            result = pack(item, lambda text: tokenizer.encode(text).ids, args.candidate_budget)
            if result['status'] == 'base_over_budget':
                raise ValueError('base representation exceeds candidate budget')
            branches = [item['D']['branches'][i] for i in result['selected_indices']]
            forms, _ = representations(item, branches)
            encoded = {v: tokenizer.encode(json.dumps(forms[v], sort_keys=True, ensure_ascii=False,
                                                       separators=(',', ':')), add_special_tokens=False).ids
                       for v in 'ABCD'}
            if any(len(ids) > args.candidate_budget - 2 for ids in encoded.values()):
                raise ValueError('candidate exceeds reserved budget')
            cache[candidate_id] = (encoded, result['status'])
        return cache[candidate_id]

    collected = {'train': [], 'dev': []}
    with zipfile.ZipFile(args.nltk_data / 'corpora/semcor.zip') as semcor_archive:
        for subset in ('train', 'dev'):
            for doc in split[subset]:
                for sentence_index, (context, annotated) in enumerate(sentences(semcor_archive, doc)):
                    for token_index, token in enumerate(annotated):
                        if token.get('rdf'):
                            continue
                        key = observed_key(token.text or '', token.get('pos', ''), wordnet.morphy)
                        if key is None or len(index.get(key, {})) < 2:
                            continue
                        instance_id = f'{doc}:{sentence_index}:{token_index}'
                        collected[subset].append({'sample_id': stable_hash(instance_id), 'instance_id': instance_id,
                            'doc': doc, 'sentence': sentence_index, 'token': token_index,
                            'context': context, 'surface': token.text or '', 'key': key, 'element': token})

    results = {}
    counts = {}
    for subset, size in (('train', 400), ('dev', 120)):
        records = select(collected[subset], size)
        if len(records) < size:
            raise ValueError(f'not enough eligible {subset} targets')
        output = []
        stats = Counter(selected=len(records))
        for record in records:
            ids = choose_candidates(record['instance_id'], index[record['key']].keys(), maximum=None)
            manifest = prepare_candidate_manifest(ids, candidate)
            element = record['element']
            lemma, lexsn = element.get('lemma'), element.get('lexsn')
            gold, issue = (None, 'invalid_gold') if not lemma or not lexsn or ';' in lexsn else mapped_target(lemma + '%' + lexsn, mapping, nodes)
            if issue:
                stats['gold_' + issue] += 1
            gold_index = ids.index(gold) if gold in ids else None
            ctx = tokenizer.encode('target: ' + record['surface'].replace('_', ' ') + ' context: ' + record['context'],
                                   add_special_tokens=False).ids
            if len(ctx) > 32:
                stats['context_truncated'] += 1
            ctx = ctx[:32]
            versions = {}
            for version in 'ABCD':
                pairs = []
                for candidate_record in manifest:
                    if candidate_record['status'] != 'ready':
                        continue
                    encoded, _status = candidate_record['payload']
                    seq = [cls_id] + ctx + [sep_id] + encoded[version] + [sep_id]
                    joint_budget = 128 if args.candidate_budget == 94 else 256
                    if len(seq) > joint_budget:
                        raise ValueError('joint sequence exceeds budget')
                    pairs.append(seq + [pad_id] * (joint_budget - len(seq)))
                versions[version] = pairs
            ready_ids = [item['candidate_id'] for item in manifest if item['status'] == 'ready']
            stats['encodable_candidates'] += len(ready_ids)
            stats['failed_candidates'] += len(ids) - len(ready_ids)
            if gold_index is not None and gold in ready_ids:
                stats['gold_candidate_no_branch'] += manifest[gold_index]['payload'][1] == 'none'
                stats['trainable_or_scorable'] += 1
            else:
                stats['gold_not_encodable'] += 1
            ready_label = ready_ids.index(gold) if gold in ready_ids else -1
            output.append({'sample_id': record['sample_id'], 'candidate_ids': ids,
                           'candidates': [{k: v for k, v in item.items() if k != 'payload'}
                                          for item in manifest],
                           'scorable_candidate_ids': ready_ids,
                           'gold_candidate_id': gold, 'gold_candidate_index': gold_index,
                           'label': ready_label,
                           'inputs': versions})
        results[subset] = output
        counts[subset] = dict(stats)
    args.out.mkdir(parents=True, exist_ok=False)
    for subset in ('train', 'dev'):
        (args.out / (subset + '.json')).write_text(json.dumps(results[subset], sort_keys=True, separators=(',', ':')), encoding='utf-8')
    metadata = {'counts': counts, 'split_seed': 17, 'candidate_budget': args.candidate_budget,
                'joint_budget': 128 if args.candidate_budget == 94 else 256,
                'nltk_version': nltk.__version__, 'tokenizers_version': tokenizers.__version__,
                'inputs_sha256': {'semcor.zip': digest(args.nltk_data / 'corpora/semcor.zip'),
                    'wordnet.zip': digest(args.nltk_data / 'corpora/wordnet.zip'), 'entries.zip': digest(args.oewn_zip),
                    'nodes.tsv': digest(nodes_file), 'rules.jsonl': digest(rules_file), 'vocab.txt': digest(args.vocab)},
                'sample_ids_sha256': {subset: stable_hash('\n'.join(r['sample_id'] for r in results[subset])) for subset in results},
                'limits': 'Exploratory fixed train/dev selection, no test documents read; recorded labels are local only.'}
    (args.out / 'metadata.json').write_text(json.dumps(metadata, sort_keys=True, indent=2), encoding='utf-8')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
