"""Audit fixed pilot samples against full versus four-candidate sets."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import zipfile

from src.analysis.audit_wn30_oewn_sense_key_crosswalk import _load_oewn_sense_keys
from src.analysis.semcor_dev_pilot import build_index, mapped_target, observed_key, sentences
from src.analysis.semcor_train_mapping import digest, partition
from src.analysis.tiny_bert_wsd_data import choose_candidates, select, stable_hash


def summarize_sizes(values):
    values = sorted(values)
    if not values:
        raise ValueError('empty sample')
    return {'min': values[0], 'median_lower': values[(len(values) - 1) // 2],
            'p90_lower': values[int((len(values) - 1) * .9)], 'max': values[-1]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--nltk-data', type=Path, required=True)
    p.add_argument('--oewn-zip', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--prepared', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    import nltk
    nltk.data.path = [str(args.nltk_data.resolve())]
    from nltk.corpus import semcor, wordnet
    if wordnet.get_version() != '3.0':
        raise ValueError('expected WordNet 3.0')
    metadata = json.loads((args.prepared / 'metadata.json').read_text(encoding='utf-8'))
    paths = {'semcor.zip': args.nltk_data / 'corpora/semcor.zip', 'wordnet.zip': args.nltk_data / 'corpora/wordnet.zip',
             'entries.zip': args.oewn_zip, 'nodes.tsv': args.bundle / 'graph/nodes.tsv'}
    if any(digest(path) != metadata['inputs_sha256'][name] for name, path in paths.items()):
        raise ValueError('inputs differ from prepared pilot')
    split = partition(semcor.fileids())
    with zipfile.ZipFile(args.oewn_zip) as archive:
        mapping = _load_oewn_sense_keys(archive)
    with paths['nodes.tsv'].open(encoding='utf-8-sig', newline='') as f:
        nodes = {row['synset_id']: row for row in csv.DictReader(f, delimiter='\t')}
    index = build_index(nodes.values())
    collected = {'train': [], 'dev': []}
    with zipfile.ZipFile(paths['semcor.zip']) as archive:
        for subset in ('train', 'dev'):
            for doc in split[subset]:
                for si, (_, annotated) in enumerate(sentences(archive, doc)):
                    for ti, token in enumerate(annotated):
                        if token.get('rdf'):
                            continue
                        key = observed_key(token.text or '', token.get('pos', ''), wordnet.morphy)
                        if key is None or len(index.get(key, {})) < 2:
                            continue
                        identity = f'{doc}:{si}:{ti}'
                        collected[subset].append({'sample_id': stable_hash(identity), 'instance_id': identity,
                            'doc': doc, 'sentence': si, 'token': ti, 'key': key, 'element': token})
    result = {}
    for subset, size in (('train', 400), ('dev', 120)):
        rows = select(collected[subset], size)
        if len(rows) != size:
            raise ValueError('insufficient targets')
        stats = Counter(selected=size)
        sizes = []
        first4_ids = set()
        for row in rows:
            candidates = index[row['key']]
            sizes.append(len(candidates))
            chosen = choose_candidates(row['instance_id'], candidates.keys())
            element = row['element']
            lemma, lexsn = element.get('lemma'), element.get('lexsn')
            if not lemma or not lexsn or ';' in lexsn:
                stats['invalid_gold'] += 1
                continue
            gold, issue = mapped_target(lemma + '%' + lexsn, mapping, nodes)
            if issue:
                stats['mapping_' + issue] += 1
                continue
            if gold in candidates:
                stats['full_gold_in_candidates'] += 1
                if gold in chosen:
                    stats['first_four_gold_in_candidates'] += 1
                    first4_ids.add(row['sample_id'])
            else:
                stats['gold_absent_even_in_full'] += 1
        prepared = json.loads((args.prepared / (subset + '.json')).read_text(encoding='utf-8'))
        if not {x['sample_id'] for x in prepared}.issubset(first4_ids):
            raise ValueError('prepared sample not covered by four candidates')
        result[subset] = {'counts': dict(stats), 'candidate_sizes': summarize_sizes(sizes),
                          'previous_prepared_samples': len(prepared)}
    payload = {'protocol': 'tiny-bert-full-candidate-coverage/1', 'splits': result,
               'inputs_sha256': {name: digest(path) for name, path in paths.items()},
               'limits': 'Candidate inventory only, not token-budget coverage or accuracy; train/dev samples reused, no held-out documents.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
