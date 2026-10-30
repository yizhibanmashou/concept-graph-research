"""Audit exact MultiRD development-definition overlap with local graph glosses.

The only archive member read is data/data_dev.json; held-out material is not read.
"""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import zipfile

from src.analysis.witness_reuse_pilot import sha


def normalize(text):
    return ' '.join(text.casefold().split())


def audit(records, nodes):
    definitions = defaultdict(set)
    for node in nodes:
        gloss = normalize(node['definition'])
        if gloss:
            definitions[gloss].update(normalize(x) for x in node['lemmas'].split('/') if normalize(x))
    words = set()
    exact_words = set()
    aligned_words = set()
    exact = aligned = empty_words = empty_definitions = eligible = 0
    for row in records:
        word, gloss = normalize(row['word']), normalize(row['definitions'])
        if word:
            words.add(word)
        if not word:
            empty_words += 1
        if not gloss:
            empty_definitions += 1
        if not word or not gloss:
            continue
        eligible += 1
        if gloss in definitions:
            exact += 1
            exact_words.add(word)
            if word in definitions[gloss]:
                aligned += 1
                aligned_words.add(word)
    return {'records': len(records), 'unique_words': len(words), 'eligible_records': eligible,
            'empty_words': empty_words, 'empty_definitions': empty_definitions,
            'exact_definition_records': exact, 'exact_definition_unique_words': len(exact_words),
            'exact_definition_and_lemma_records': aligned, 'exact_definition_and_lemma_unique_words': len(aligned_words)}


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
    result = {'protocol': 'multird-development-exact-overlap/1', 'counts': audit(records, nodes),
              'inputs_sha256': {'archive': sha(args.archive), 'development_member': hashlib.sha256(dev).hexdigest(),
                                'nodes.tsv': sha(args.nodes)},
              'limits': 'Exact string overlap only; slash-separated graph lemmas, no morphology or near-duplicate detection; no held-out archive member read.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
