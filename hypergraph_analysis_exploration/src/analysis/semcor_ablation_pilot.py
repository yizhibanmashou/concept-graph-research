"""Exploratory matched-candidate BM25 A-D representations on SemCor dev."""
import argparse
import csv
import functools
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from src.analysis.audit_wn30_oewn_sense_key_crosswalk import _load_oewn_sense_keys
from src.analysis.reverse_dictionary_pilot import GlossIndex
from src.analysis.semcor_train_mapping import digest, partition
from src.analysis.semcor_dev_pilot import build_index, mapped_target, observed_key, sentences
from src.analysis.sense_representation_pilot import build
from src.analysis.sense_budget_packing import pack


def compact(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def make_texts(row, clauses, definitions, encode, budget):
    item = build(row['synset_id'], row['definition'], clauses, definitions)
    selected = pack(item, encode, budget)
    if selected['status'] == 'base_over_budget':
        return None, selected['status']
    selected_branches = [clauses[i] for i in selected['selected_indices']]
    rebuilt = build(row['synset_id'], row['definition'], selected_branches, definitions)
    return {version: compact(rebuilt[version]) for version in 'ABCD'}, selected['status']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nltk-data', type=Path, required=True)
    parser.add_argument('--oewn-zip', type=Path, required=True)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--vocab', type=Path, required=True)
    parser.add_argument('--vocab-revision', required=True)
    parser.add_argument('--out', type=Path, required=True)
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
    definitions = {key: value['definition'] for key, value in nodes.items()}
    with rules_file.open(encoding='utf-8') as f:
        rules = {row['head']: row['clauses'] for row in (json.loads(line) for line in f if line.strip())}
    index = build_index(nodes.values())
    tokenizer = tokenizers.BertWordPieceTokenizer(str(args.vocab), lowercase=True)
    encode = lambda text: tokenizer.encode(text).ids

    @functools.lru_cache(maxsize=None)
    def indexes(key):
        candidates = index.get(key, {})
        if not candidates:
            return None
        text_rows = {v: [] for v in 'ABCD'}
        statuses = Counter()
        status_by_id = {}
        for candidate_id, row in candidates.items():
            if candidate_id not in rules:
                return None
            texts, status = make_texts(row, rules[candidate_id], definitions, encode, 256)
            if texts is None:
                return None
            statuses[status] += 1
            status_by_id[candidate_id] = status
            for version in 'ABCD':
                text_rows[version].append({'synset_id': candidate_id, 'lemmas': row['lemmas'], 'definition': texts[version]})
        return ({v: GlossIndex(text_rows[v]) for v in 'ABCD'}, statuses, status_by_id)

    counts = Counter()
    slices = defaultdict(Counter)
    with zipfile.ZipFile(args.nltk_data / 'corpora/semcor.zip') as semcor_archive:
        for doc in split['dev']:
            for context, annotated in sentences(semcor_archive, doc):
                for token in annotated:
                    counts['annotated_tokens'] += 1
                    if token.get('rdf'):
                        counts['skipped_named_entity_rdf'] += 1
                        continue
                    key = observed_key(token.text or '', token.get('pos', ''), wordnet.morphy)
                    if key is None:
                        counts['unsupported_surface_pos'] += 1
                        continue
                    counts['eligible_tokens'] += 1
                    candidates = index.get(key, {})
                    if not candidates:
                        counts['no_candidates'] += 1
                        continue
                    prepared = indexes(key)
                    if prepared is None:
                        counts['budget_or_graph_excluded'] += 1
                        continue
                    index_by_version, statuses, status_by_id = prepared
                    predictions = {}
                    for version, candidate_index in index_by_version.items():
                        ranked = candidate_index.search(context, len(candidates))
                        predictions[version] = ranked[0]['id'] if ranked else min(candidates)
                    # Gold key is consulted only after candidate construction and predictions.
                    gold_lemma, lexsn = token.get('lemma'), token.get('lexsn')
                    if not gold_lemma or not lexsn or ';' in lexsn:
                        counts['invalid_gold_key'] += 1
                        continue
                    target, issue = mapped_target(gold_lemma + '%' + lexsn, mapping, nodes)
                    if issue:
                        counts[issue] += 1
                        continue
                    if target not in candidates:
                        counts['target_not_in_candidates'] += 1
                        continue
                    counts['covered'] += 1
                    counts['queries_with_any_no_branch'] += bool(statuses['none'])
                    counts['gold_candidate_status_' + status_by_id[target]] += 1
                    counts['A_only_vs_D'] += predictions['A'] == target and predictions['D'] != target
                    counts['D_only_vs_A'] += predictions['D'] == target and predictions['A'] != target
                    category = 'one_candidate' if len(candidates) == 1 else 'multiple_candidates'
                    slices[category]['covered'] += 1
                    for version in 'ABCD':
                        is_correct = predictions[version] == target
                        counts[version + '_correct'] += is_correct
                        slices[category][version + '_correct'] += is_correct
    denominator, covered = counts['eligible_tokens'], counts['covered']
    inputs = {'semcor.zip': args.nltk_data / 'corpora/semcor.zip', 'wordnet.zip': args.nltk_data / 'corpora/wordnet.zip',
              'oewn_entries.zip': args.oewn_zip, 'nodes.tsv': nodes_file, 'hypergraph_rules.jsonl': rules_file, 'vocab.txt': args.vocab}
    result = {'split_seed': 17, 'budget_candidate_tokens': 256, 'counts': dict(counts),
              'slices': {key: dict(val) for key, val in sorted(slices.items())},
              'accuracy_covered': {v: counts[v + '_correct'] / covered if covered else None for v in 'ABCD'},
              'accuracy_all_eligible': {v: counts[v + '_correct'] / denominator if denominator else None for v in 'ABCD'},
              'inputs_sha256': {name: digest(path) for name, path in inputs.items()},
              'split_ids_sha256': hashlib.sha256(json.dumps(split, sort_keys=True).encode()).hexdigest(),
              'nltk_version': nltk.__version__, 'tokenizers_version': tokenizers.__version__, 'vocab_revision': args.vocab_revision,
              'limits': 'Exploratory dev on a previously inspected split; BM25 over serialized JSON is not structure-aware; no final benchmark or semantic validation.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps({'counts': result['counts'], 'slices': result['slices'], 'accuracy_covered': result['accuracy_covered']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
