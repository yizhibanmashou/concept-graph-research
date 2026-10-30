"""Audit OEWN candidate coverage on a document-disjoint SemCor training split."""
import argparse
import csv
import hashlib
import json
import random
import zipfile
from collections import Counter
from pathlib import Path

from src.analysis.audit_wn30_oewn_sense_key_crosswalk import _load_oewn_sense_keys


def partition(document_ids, seed=17):
    ids = sorted(document_ids)
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('document IDs must be nonempty and unique')
    random.Random(seed).shuffle(ids)
    train_end = int(len(ids) * 0.70)
    dev_end = train_end + int(len(ids) * 0.15)
    return {'train': ids[:train_end], 'dev': ids[train_end:dev_end], 'test': ids[dev_end:]}


def classify(key, lemma, pos, mapping, nodes):
    targets = mapping.get(key.casefold(), set())
    if not targets:
        return 'no_exact_key'
    if len(targets) != 1:
        return 'multiple_oewn_targets'
    target = next(iter(targets))
    # Official OEWN entry IDs are bare offsets; the frozen graph uses oewn-.
    if target not in nodes and not target.startswith('oewn-'):
        target = 'oewn-' + target
    if target not in nodes:
        return 'target_absent_from_graph'
    node = nodes[target]
    lemma = lemma.casefold().replace('_', ' ')
    options = {value.strip().casefold().replace('_', ' ') for value in node['lemmas'].split('/')}
    if node['pos'] != pos or lemma not in options:
        return 'target_not_in_strict_lemma_pos_candidates'
    return 'strict_candidate_covered'


def adjective_relaxed_recovery(key, lemma, pos, mapping, nodes):
    """Count a/s compatibility only; never change the strict result."""
    targets = mapping.get(key.casefold(), set())
    if len(targets) != 1 or pos not in {'a', 's'}:
        return False
    target = next(iter(targets))
    if target not in nodes and not target.startswith('oewn-'):
        target = 'oewn-' + target
    if target not in nodes or nodes[target]['pos'] not in {'a', 's'}:
        return False
    options = {v.strip().casefold().replace('_', ' ') for v in nodes[target]['lemmas'].split('/')}
    return lemma.casefold().replace('_', ' ') in options


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nltk-data', type=Path, required=True)
    parser.add_argument('--oewn-zip', type=Path, required=True)
    parser.add_argument('--nodes', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    import nltk
    nltk.data.path = [str(args.nltk_data.resolve())]
    from nltk.corpus import semcor, wordnet
    if wordnet.get_version() != '3.0':
        raise ValueError('expected WordNet 3.0')
    split = partition(semcor.fileids())
    with zipfile.ZipFile(args.oewn_zip) as archive:
        mapping = _load_oewn_sense_keys(archive)
    with args.nodes.open(encoding='utf-8-sig', newline='') as f:
        nodes = {row['synset_id']: row for row in csv.DictReader(f, delimiter='\t')}
    counts = Counter()
    pos_counts = {}
    for doc in split['train']:
        for sentence in semcor.tagged_sents(fileids=doc, tag='sem'):
            counts['sentences'] += 1
            for item in sentence:
                if not hasattr(item, 'label'):
                    continue
                label = item.label()
                if not callable(getattr(label, 'key', None)):
                    counts['unresolved_nonlemma_labels'] += 1
                    continue
                pos = label.synset().pos()
                category = classify(label.key(), label.name(), pos, mapping, nodes)
                counts['lemma_labels'] += 1
                counts[category] += 1
                pos_counts.setdefault(pos, Counter())[category] += 1
                if category == 'target_not_in_strict_lemma_pos_candidates' and adjective_relaxed_recovery(
                        label.key(), label.name(), pos, mapping, nodes):
                    counts['additional_covered_with_adjective_a_s_equivalence'] += 1
                    pos_counts[pos]['additional_covered_with_adjective_a_s_equivalence'] += 1
    input_files = {'semcor.zip': args.nltk_data / 'corpora/semcor.zip',
                   'wordnet.zip': args.nltk_data / 'corpora/wordnet.zip',
                   'oewn_entries.zip': args.oewn_zip, 'nodes.tsv': args.nodes}
    result = {'split_seed': 17, 'split': split, 'counts': dict(counts),
              'per_pos': {pos: dict(values) for pos, values in sorted(pos_counts.items())},
              'inputs_sha256': {key: digest(path) for key, path in input_files.items()},
              'nltk_version': nltk.__version__,
              'limits': 'Train documents only; exact identity/candidate coverage is not semantic equivalence or WSD accuracy.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(json.dumps({'document_counts': {k: len(v) for k, v in split.items()}, 'counts': counts,
                      'per_pos': result['per_pos']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
