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
from src.analysis.semcor_dev_pilot import build_index, mapped_target, observed_key, sentence_records
from src.analysis.semcor_train_mapping import digest, partition
from src.analysis.sense_representation_pilot import build


def stable_hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def document_cluster_id(document_id):
    """Return a stable, pseudonymous join key for document-cluster analysis."""
    return stable_hash('semcor-document:' + document_id)


def choose_candidates(instance_id, candidate_ids, maximum=4):
    """Return the complete deterministic candidate order (or a legacy bounded view)."""
    ordered = sorted(set(candidate_ids), key=lambda value: (stable_hash(instance_id + ':' + value), value))
    return ordered if maximum is None else ordered[:maximum]


def candidate_ids_for_surface(surface, pos, index, all_morphy):
    """Union candidates from every morphology analysis of the observed form.

    NLTK's public ``morphy`` returns only its first analysis. The caller supplies
    an all-analyses function (WordNet 3.0 ``_morphy`` in the pilot) and records
    the exact NLTK version in run metadata. This function never accepts a gold
    key or sense ID.
    """
    from src.analysis.semcor_dev_pilot import norm, pos_class

    normalized_surface = surface.replace(' ', '_').lower()
    forms = list(all_morphy(normalized_surface, pos))
    if not forms:
        forms = [normalized_surface]
    candidate_ids = set()
    for form in forms:
        candidate_ids.update(index.get((norm(form), pos_class(pos)), {}))
    return candidate_ids


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


def encode_target_centered_context(words, target_word_index, surface, encode, start_marker, end_marker,
                                   maximum=32):
    """Encode a bounded sentence window that explicitly brackets the target occurrence."""
    surface = surface.replace('_', ' ')
    if not 0 <= target_word_index < len(words):
        raise ValueError('target word index is outside the sentence')
    if words[target_word_index] != surface:
        raise ValueError('annotated target does not match sentence word at its XML position')
    prefix = encode('target: ' + surface + ' context:')
    encoded_words = [encode(word) for word in words]
    target = encoded_words[target_word_index]
    fixed = len(prefix) + len(target) + 2
    if not target or fixed > maximum:
        raise ValueError('target occurrence does not fit the context budget')

    remaining = maximum - fixed
    left_index = target_word_index - 1
    right_index = target_word_index + 1
    left = []
    right = []
    left_open = left_index >= 0
    right_open = right_index < len(words)
    prefer_left = True
    while remaining and (left_open or right_open):
        take_left = (left_open and not right_open) or (left_open and right_open and prefer_left)
        if take_left:
            pieces = encoded_words[left_index]
            if len(pieces) <= remaining:
                left[:0] = pieces
                remaining -= len(pieces)
                left_index -= 1
                left_open = left_index >= 0
            else:
                left_open = False
        else:
            pieces = encoded_words[right_index]
            if len(pieces) <= remaining:
                right.extend(pieces)
                remaining -= len(pieces)
                right_index += 1
                right_open = right_index < len(words)
            else:
                right_open = False
        prefer_left = not prefer_left

    target_start = len(prefix) + len(left) + 1
    context_ids = prefix + left + [start_marker] + target + [end_marker] + right
    return context_ids, {'target_piece_start': target_start,
                         'target_piece_end': target_start + len(target),
                         'sentence_truncated': left_index >= 0 or right_index < len(words)}


def select(records, n):
    return sorted(records, key=lambda row: (row['sample_id'], row['doc'], row['sentence'], row['token']))[:n]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nltk-data', type=Path, required=True)
    parser.add_argument('--oewn-zip', type=Path, required=True)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--vocab', type=Path, required=True)
    parser.add_argument('--candidate-budget', type=int, choices=(94, 222), default=94)
    parser.add_argument('--document-manifest', type=Path,
                        help='optional document-disjoint train/dev manifest using official SemCor train docs')
    parser.add_argument('--out', type=Path, required=True, help='new directory')
    args = parser.parse_args()
    import nltk
    import tokenizers
    nltk.data.path = [str(args.nltk_data.resolve())]
    from nltk.corpus import semcor, wordnet
    if wordnet.get_version() != '3.0':
        raise ValueError('expected WordNet 3.0')
    split = partition(semcor.fileids())
    document_manifest = None
    document_manifest_sha256 = None
    if args.document_manifest:
        document_manifest = json.loads(args.document_manifest.read_text(encoding='utf-8'))
        if document_manifest.get('manifest_version') != 't04-semcor-doc-holdout-v1':
            raise ValueError('unsupported document manifest version')
        dev_docs = document_manifest.get('fresh_development_documents')
        if not isinstance(dev_docs, list) or not dev_docs or len(dev_docs) != len(set(dev_docs)):
            raise ValueError('fresh development documents must be a nonempty unique list')
        official_train_docs = set(split['train'])
        if not set(dev_docs).issubset(official_train_docs):
            raise ValueError('fresh development documents must be from official SemCor train only')
        if document_manifest.get('semcor_archive_sha256') != digest(args.nltk_data / 'corpora/semcor.zip'):
            raise ValueError('SemCor archive hash does not match the document manifest')
        expected_doc_hash = stable_hash('\n'.join(dev_docs))
        if document_manifest.get('fresh_development_document_set_sha256') != expected_doc_hash:
            raise ValueError('fresh development document-list hash does not match the manifest')
        split = {'train': [doc for doc in split['train'] if doc not in set(dev_docs)],
                 'dev': dev_docs}
        document_manifest_sha256 = digest(args.document_manifest)
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
    target_start_id, target_end_id = (tokenizer.token_to_id(x) for x in ('[unused0]', '[unused1]'))
    if target_start_id is None or target_end_id is None:
        raise ValueError('target markers [unused0] and [unused1] must exist in the vocabulary')
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
                for sentence_index, (_context, words, annotated) in enumerate(sentence_records(semcor_archive, doc)):
                    for token_index, (word_index, token) in enumerate(annotated):
                        if token.get('rdf'):
                            continue
                        key = observed_key(token.text or '', token.get('pos', ''), wordnet.morphy)
                        if key is None or len(index.get(key, {})) < 2:
                            continue
                        instance_id = f'{doc}:{sentence_index}:{token_index}'
                        collected[subset].append({'sample_id': stable_hash(instance_id), 'instance_id': instance_id,
                            'doc': doc, 'sentence': sentence_index, 'token': token_index,
                            'word_index': word_index, 'words': words,
                            'surface': token.text or '', 'key': key, 'element': token})

    results = {}
    counts = {}
    selected_document_ids = {}
    eligible_target_pool = {subset: len(collected[subset]) for subset in ('train', 'dev')}
    excluded_targets = {'train': [], 'dev': []}
    for subset, size in (('train', 400), ('dev', 120)):
        records = select(collected[subset], size)
        if len(records) < size:
            raise ValueError(f'not enough eligible {subset} targets')
        selected_document_ids[subset] = sorted({record['doc'] for record in records})
        output = []
        stats = Counter(selected=len(records))
        for record in records:
            ids = choose_candidates(record['instance_id'], candidate_ids_for_surface(
                record['surface'], record['key'][1], index, wordnet._morphy), maximum=None)
            manifest = prepare_candidate_manifest(ids, candidate)
            element = record['element']
            lemma, lexsn = element.get('lemma'), element.get('lexsn')
            gold, issue = (None, 'invalid_gold') if not lemma or not lexsn or ';' in lexsn else mapped_target(lemma + '%' + lexsn, mapping, nodes)
            if issue:
                stats['gold_' + issue] += 1
            gold_index = ids.index(gold) if gold in ids else None
            ready_ids = [item['candidate_id'] for item in manifest if item['status'] == 'ready']
            stats['encodable_candidates'] += len(ready_ids)
            stats['failed_candidates'] += len(ids) - len(ready_ids)
            try:
                ctx, window = encode_target_centered_context(
                    record['words'], record['word_index'], record['surface'],
                    lambda text: tokenizer.encode(text, add_special_tokens=False).ids,
                    target_start_id, target_end_id, maximum=32)
            except ValueError as exc:
                stats['excluded_target_context'] += 1
                excluded_targets[subset].append({'sample_id': record['sample_id'], 'reason': str(exc)})
                if gold_index is None or gold not in ready_ids:
                    stats['gold_not_encodable'] += 1
                continue
            if window['sentence_truncated']:
                stats['sentence_window_truncated'] += 1
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
            if gold_index is not None and gold in ready_ids:
                stats['gold_candidate_no_branch'] += manifest[gold_index]['payload'][1] == 'none'
                stats['trainable_or_scorable'] += 1
            else:
                stats['gold_not_encodable'] += 1
            ready_label = ready_ids.index(gold) if gold in ready_ids else -1
            output.append({'sample_id': record['sample_id'],
                           # Generated outputs are local/ignored; this pseudonymous key
                           # supports cluster-aware analysis without storing source names.
                           'document_cluster_id': document_cluster_id(record['doc']),
                           'candidate_ids': ids,
                           'candidates': [{k: v for k, v in item.items() if k != 'payload'}
                                          for item in manifest],
                           'scorable_candidate_ids': ready_ids,
                           'gold_candidate_id': gold, 'gold_candidate_index': gold_index,
                           'label': ready_label,
                           'inputs': versions})
        results[subset] = output
        counts[subset] = dict(stats)
    if set(selected_document_ids['train']) & set(selected_document_ids['dev']):
        raise ValueError('selected train and dev targets overlap by document')
    args.out.mkdir(parents=True, exist_ok=False)
    for subset in ('train', 'dev'):
        (args.out / (subset + '.json')).write_text(json.dumps(results[subset], sort_keys=True, separators=(',', ':')), encoding='utf-8')
    (args.out / 'excluded_targets.json').write_text(
        json.dumps(excluded_targets, sort_keys=True, indent=2), encoding='utf-8')
    metadata = {'counts': counts, 'split_seed': 17, 'candidate_budget': args.candidate_budget,
                'eligible_target_pool': eligible_target_pool,
                'document_counts': {subset: len(split[subset]) for subset in ('train', 'dev')},
                'document_ids_sha256': {subset: stable_hash('\n'.join(split[subset])) for subset in ('train', 'dev')},
                'selected_document_counts': {subset: len(selected_document_ids[subset]) for subset in ('train', 'dev')},
                'document_split_policy': ('official SemCor split seed 17' if document_manifest is None else
                    'official SemCor train documents repartitioned by frozen T04 document manifest; train/dev document-disjoint'),
                'document_manifest_sha256': document_manifest_sha256,
                'joint_budget': 128 if args.candidate_budget == 94 else 256,
                'context_budget': 32, 'context_policy': 'target-centered with [unused0]/[unused1] occurrence markers',
                'candidate_morphology_policy': 'lowercased observed surface; union of all NLTK WordNet _morphy analyses for POS; normalized-surface fallback if no analysis; gold-independent',
                'target_marker_ids': {'start': target_start_id, 'end': target_end_id},
                'nltk_version': nltk.__version__, 'tokenizers_version': tokenizers.__version__,
                'inputs_sha256': {'semcor.zip': digest(args.nltk_data / 'corpora/semcor.zip'),
                    'wordnet.zip': digest(args.nltk_data / 'corpora/wordnet.zip'), 'entries.zip': digest(args.oewn_zip),
                    'nodes.tsv': digest(nodes_file), 'rules.jsonl': digest(rules_file), 'vocab.txt': digest(args.vocab)},
                'sample_ids_sha256': {subset: stable_hash('\n'.join(r['sample_id'] for r in results[subset])) for subset in results},
                'excluded_target_ids_sha256': {subset: stable_hash('\n'.join(r['sample_id'] for r in excluded_targets[subset]))
                                               for subset in excluded_targets},
                'limits': 'Exploratory fixed train/dev selection, no test documents read; recorded labels are local only.'}
    (args.out / 'metadata.json').write_text(json.dumps(metadata, sort_keys=True, indent=2), encoding='utf-8')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
