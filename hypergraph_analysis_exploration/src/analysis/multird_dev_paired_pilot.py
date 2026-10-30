"""Post-hoc paired-word development diagnostic; human test remains unread."""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import zipfile

from src.analysis.multird_dev_overlap import normalize
from src.analysis.multird_dev_retrieval_pilot import score, words_from_results
from src.analysis.reverse_dictionary_pilot import GlossIndex
from src.analysis.witness_reuse_pilot import sha


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def select_pairs(records, glosses, limit=100):
    grouped = defaultdict(lambda: {'exact': [], 'nonexact': []})
    for i, row in enumerate(records):
        word, query = normalize(row['word']), normalize(row['definitions'])
        if not word or not query:
            continue
        group = 'exact' if query in glosses else 'nonexact'
        grouped[word][group].append((digest(f'{query}\0{i}'), i))
    eligible = sorted((digest(word), word) for word, groups in grouped.items()
                      if groups['exact'] and groups['nonexact'])
    if not eligible or limit <= 0:
        raise ValueError('no eligible word pairs or invalid limit')
    return [(key, word, min(grouped[word]['exact'])[1], min(grouped[word]['nonexact'])[1])
            for key, word in eligible[:limit]], len(eligible)


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
    glosses = {normalize(x['definition']) for x in nodes if normalize(x['definition'])}
    lexicon = {normalize(w) for x in nodes for w in x['lemmas'].split('/') if normalize(w)}
    pairs, eligible = select_pairs(records, glosses)
    ranks = {'exact': [], 'nonexact': []}
    for _, word, exact, nonexact in pairs:
        for group, i in (('exact', exact), ('nonexact', nonexact)):
            candidates = words_from_results(index.search(records[i]['definitions'], limit=100))
            ranks[group].append(candidates.index(word) + 1 if word in candidates else None)
    exact_only = sum(a == 1 and b != 1 for a, b in zip(ranks['exact'], ranks['nonexact']))
    nonexact_only = sum(a != 1 and b == 1 for a, b in zip(ranks['exact'], ranks['nonexact']))
    result = {'protocol': 'multird-dev-paired-word-retrieval/1', 'eligible_word_pairs': eligible,
              'selected_pairs': len(pairs), 'vocabulary_covered_pairs': sum(word in lexicon for _, word, _, _ in pairs),
              'metrics': {key: score(value) for key, value in ranks.items()},
              'top1_exact_only': exact_only, 'top1_nonexact_only': nonexact_only,
              'selected_word_hashes': [key for key, _, _, _ in pairs],
              'inputs_sha256': {'archive': sha(args.archive), 'development_member': hashlib.sha256(dev).hexdigest(),
                                'nodes.tsv': sha(args.nodes)},
              'limits': 'Post-hoc paired word forms can represent different senses; definitions and sources are not randomized. No test member read.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in result.items() if k not in ('selected_word_hashes', 'inputs_sha256')}))


if __name__ == '__main__':
    main()
