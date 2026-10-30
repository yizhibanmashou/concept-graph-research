"""Evaluate a train-sample MFS baseline on the exact prepared WSD target rows."""
import argparse
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from src.analysis.semcor_dev_pilot import observed_key, sentence_records
from src.analysis.semcor_train_mapping import partition


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def source_keys(nltk_data, wanted_ids, subset=None, documents=None):
    import nltk
    nltk.data.path = [str(nltk_data.resolve())]
    from nltk.corpus import semcor, wordnet

    if documents is None:
        if subset not in {'train', 'dev'}:
            raise ValueError('provide a valid SemCor subset or explicit document list')
        documents = partition(semcor.fileids())[subset]
    keys = {}
    with zipfile.ZipFile(nltk_data / 'corpora/semcor.zip') as archive:
        for document in documents:
            for sentence_index, (_context, _words, annotated) in enumerate(sentence_records(archive, document)):
                for token_index, (_word_index, token) in enumerate(annotated):
                    if token.get('rdf'):
                        continue
                    key = observed_key(token.text or '', token.get('pos', ''), wordnet.morphy)
                    if key is None:
                        continue
                    instance_id = f'{document}:{sentence_index}:{token_index}'
                    sample_id = hashlib.sha256(instance_id.encode('utf-8')).hexdigest()
                    if sample_id in wanted_ids:
                        keys[sample_id] = key
    if set(keys) != set(wanted_ids):
        missing = len(set(wanted_ids) - set(keys))
        raise ValueError(f'could not reconstruct {missing} selected target keys')
    return keys, nltk.__version__, wordnet.get_version()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nltk-data', type=Path, required=True)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--document-manifest', type=Path,
                        help='document manifest used to build a fresh SemCor train/dev split')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()

    prepared = args.prepared
    train = json.loads((prepared / 'train.json').read_text(encoding='utf-8'))
    dev = json.loads((prepared / 'dev.json').read_text(encoding='utf-8'))
    metadata = json.loads((prepared / 'metadata.json').read_text(encoding='utf-8'))
    if args.document_manifest:
        import nltk
        nltk.data.path = [str(args.nltk_data.resolve())]
        from nltk.corpus import semcor
        manifest = json.loads(args.document_manifest.read_text(encoding='utf-8'))
        official_train = partition(semcor.fileids())['train']
        dev_documents = manifest['fresh_development_documents']
        if not set(dev_documents).issubset(set(official_train)):
            raise ValueError('fresh development documents must be in official SemCor train')
        train_documents = [doc for doc in official_train if doc not in set(dev_documents)]
        train_keys, nltk_version, wn_version = source_keys(
            args.nltk_data, {row['sample_id'] for row in train}, documents=train_documents)
        dev_keys, _nltk_version, _wn_version = source_keys(
            args.nltk_data, {row['sample_id'] for row in dev}, documents=dev_documents)
    else:
        train_keys, nltk_version, wn_version = source_keys(
            args.nltk_data, {row['sample_id'] for row in train}, 'train')
        dev_keys, _nltk_version, _wn_version = source_keys(
            args.nltk_data, {row['sample_id'] for row in dev}, 'dev')

    counts = defaultdict(Counter)
    for row in train:
        if row['label'] >= 0:
            counts[train_keys[row['sample_id']]][row['gold_candidate_id']] += 1

    evaluation = []
    for row in dev:
        key = dev_keys[row['sample_id']]
        candidates = row['scorable_candidate_ids']
        prediction = min(candidates, key=lambda sense: (-counts[key][sense], sense)) if candidates else None
        evaluation.append({'sample_id': row['sample_id'], 'key_seen_in_train': bool(counts[key]),
                           'candidate_count': len(candidates), 'prediction': prediction,
                           'gold': row['gold_candidate_id'], 'label': row['label']})

    scored = [row for row in evaluation if row['label'] >= 0]
    slices = {}
    for name, group in (('all_scored', scored),
                        ('key_seen_in_train', [row for row in scored if row['key_seen_in_train']]),
                        ('key_unseen_in_train', [row for row in scored if not row['key_seen_in_train']])):
        correct = sum(row['prediction'] == row['gold'] for row in group)
        slices[name] = {'correct': correct, 'total': len(group),
                        'accuracy': correct / len(group) if group else None}

    result = {'method': 'most-frequent gold candidate by observed surface lemma and POS; training counts from the exact prepared train rows only; ties by candidate ID',
              'split_seed': metadata['split_seed'], 'nltk_version': nltk_version,
              'wordnet_version': wn_version, 'candidate_morphology_in_data': metadata['candidate_morphology_policy'],
              'counts': {'selected_train': len(train), 'scorable_train': sum(row['label'] >= 0 for row in train),
                         'selected_dev': len(dev), 'scorable_dev': len(scored)},
              'accuracy': slices, 'unscored_targets_are_incorrect_if_all_selected_denominator':
                  sum(row['prediction'] == row['gold'] for row in evaluation) / len(evaluation) if evaluation else None,
              'dev_predictions': evaluation,
              'inputs_sha256': {name: digest(prepared / name) for name in ('train.json', 'dev.json', 'metadata.json')},
              'limitations': 'Exploratory baseline on the same repeatedly explored 120-row development sample; not a confirmatory benchmark. Training counts use only the 400 selected train rows, not full SemCor.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'counts': result['counts'], 'accuracy': slices,
                      'all_selected_accuracy': result['unscored_targets_are_incorrect_if_all_selected_denominator']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
