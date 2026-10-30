"""Development-only, word-level BM25 baseline for MultiRD descriptions."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import zipfile

from src.analysis.multird_dev_overlap import normalize
from src.analysis.reverse_dictionary_pilot import GlossIndex
from src.analysis.witness_reuse_pilot import sha


def sample_groups(records, glosses, limit):
    if limit <= 0:
        raise ValueError('positive sample size required')
    groups = {'exact': [], 'nonexact': []}
    for i, row in enumerate(records):
        query = normalize(row['definitions'])
        if not query or not normalize(row['word']):
            continue
        key = hashlib.sha256(f'{query}\0{i}'.encode('utf-8')).hexdigest()
        groups['exact' if query in glosses else 'nonexact'].append((key, i))
    if any(len(values) < limit for values in groups.values()):
        raise ValueError('insufficient eligible records')
    return {key: sorted(values)[:limit] for key, values in groups.items()}


def words_from_results(results, max_words=100):
    seen = set()
    ranked = []
    for result in results:
        for value in result['lemmas'].split('/'):
            word = normalize(value)
            if word and word not in seen:
                seen.add(word)
                ranked.append(word)
                if len(ranked) >= max_words:
                    return ranked
    return ranked


def score(ranks):
    n = len(ranks)
    if not n:
        raise ValueError('empty scores')
    return {'queries': n, 'top1': sum(x == 1 for x in ranks) / n,
            'recall_at_10': sum(x is not None and x <= 10 for x in ranks) / n,
            'mrr_at_100': sum(1 / x for x in ranks if x is not None and x <= 100) / n}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--nodes', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    with zipfile.ZipFile(args.archive) as archive:
        dev = archive.read('data/data_dev.json')
    records = json.loads(dev)
    with args.nodes.open(encoding='utf-8-sig', newline='') as f:
        nodes = list(csv.DictReader(f, delimiter='\t'))
    index = GlossIndex(nodes)
    glosses = {normalize(node['definition']) for node in nodes if normalize(node['definition'])}
    lexicon = {normalize(word) for node in nodes for word in node['lemmas'].split('/') if normalize(word)}
    groups = sample_groups(records, glosses, 100)
    results = {}
    for group, selected in groups.items():
        ranks = []
        covered = 0
        for _, i in selected:
            target = normalize(records[i]['word'])
            covered += target in lexicon
            # Prediction is generated from query and graph only, prior to scoring.
            candidates = words_from_results(index.search(records[i]['definitions'], limit=100))
            ranks.append(candidates.index(target) + 1 if target in candidates else None)
        results[group] = {**score(ranks), 'vocabulary_covered': covered,
                          'selected_query_hashes': [key for key, _ in selected]}
        print(group, {k: v for k, v in results[group].items() if k != 'selected_query_hashes'}, flush=True)
    result = {'protocol': 'multird-dev-gloss-overlap-retrieval/1', 'results': results,
              'inputs_sha256': {'archive': sha(args.archive), 'development_member': hashlib.sha256(dev).hexdigest(),
                                'nodes.tsv': sha(args.nodes)},
              'limits': 'Post-hoc development sample; matched gloss and non-matched groups are not randomized. Search truncates at 100 synsets; no held-out member read.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
