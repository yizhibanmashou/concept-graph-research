"""Train-frequency and gloss-overlap baselines on independently inferred target lemmas."""
import argparse
import csv
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree

from src.analysis.audit_wn30_oewn_sense_key_crosswalk import _load_oewn_sense_keys
from src.analysis.reverse_dictionary_pilot import GlossIndex
from src.analysis.semcor_train_mapping import digest, partition


def norm(lemma):
    return lemma.casefold().strip().replace('_', ' ')


def pos_class(pos):
    return 'a' if pos in {'a', 's'} else pos


def penn_pos(tag):
    for prefix, pos in (('NN', 'n'), ('VB', 'v'), ('JJ', 'a'), ('RB', 'r')):
        if tag.startswith(prefix):
            return pos
    return None


def build_index(rows):
    index = defaultdict(dict)
    for row in rows:
        for word in row['lemmas'].split('/'):
            index[(norm(word), pos_class(row['pos']))][row['synset_id']] = row
    return index


def mapped_target(key, mapping, nodes):
    targets = mapping.get(key.casefold(), set())
    if not targets:
        return None, 'no_exact_key'
    if len(targets) != 1:
        return None, 'multiple_oewn_targets'
    target = next(iter(targets))
    if target not in nodes and not target.startswith('oewn-'):
        target = 'oewn-' + target
    if target not in nodes:
        return None, 'target_absent_from_graph'
    return target, None


def ranked_mfs(candidates, counts):
    return min(candidates, key=lambda item: (-counts[item], item))


def ranked_gloss(candidates, context):
    ranked = GlossIndex(candidates.values()).search(context, len(candidates))
    return ranked[0]['id'] if ranked else min(candidates)


def observed_key(surface, penn_tag, morph):
    pos = penn_pos(penn_tag)
    if pos is None:
        return None
    surface = surface.replace(' ', '_')
    return (norm(morph(surface, pos) or surface), pos)


def sentence_records(archive, doc):
    with archive.open('semcor/' + doc) as f:
        root = ElementTree.parse(f).getroot()
    for sentence in root.iter('s'):
        words = list(sentence)
        surfaces = [(word.text or '').replace('_', ' ') for word in words]
        context = ' '.join(surfaces)
        annotated = [(position, word) for position, word in enumerate(words)
                     if word.tag == 'wf' and word.get('wnsn') and word.get('lexsn')]
        yield context, surfaces, annotated


def sentences(archive, doc):
    for context, _surfaces, annotated in sentence_records(archive, doc):
        yield context, [word for _position, word in annotated]


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
    index = build_index(nodes.values())
    train_counts = defaultdict(Counter)
    counts = Counter()
    slices = defaultdict(Counter)
    with zipfile.ZipFile(args.nltk_data / 'corpora/semcor.zip') as semcor_archive:
        for subset in ('train', 'dev'):
            for doc in split[subset]:
                for context, annotated in sentences(semcor_archive, doc):
                    for token in annotated:
                        if subset == 'dev':
                            counts['annotated_tokens'] += 1
                        if token.get('rdf'):
                            if subset == 'dev': counts['skipped_named_entity_rdf'] += 1
                            continue
                        key = observed_key(token.text or '', token.get('pos', ''), wordnet.morphy)
                        if key is None:
                            if subset == 'dev': counts['unsupported_surface_pos'] += 1
                            continue
                        if subset == 'dev': counts['eligible_tokens'] += 1
                        candidates = index.get(key, {})
                        # Candidate selection uses only surface text and annotated POS.
                        if subset == 'dev' and candidates:
                            mfs_prediction = ranked_mfs(candidates, train_counts[key])
                            gloss_prediction = ranked_gloss(candidates, context)
                        gold_lemma = token.get('lemma')
                        lexsn = token.get('lexsn')
                        if not gold_lemma or not lexsn or ';' in lexsn:
                            if subset == 'dev': counts['invalid_gold_key'] += 1
                            continue
                        target, issue = mapped_target(gold_lemma + '%' + lexsn, mapping, nodes)
                        if issue:
                            if subset == 'dev': counts[issue] += 1
                            continue
                        if target not in candidates:
                            if subset == 'dev': counts['target_not_in_candidates'] += 1
                            continue
                        if subset == 'train':
                            train_counts[key][target] += 1
                            continue
                        counts['covered'] += 1
                        mfs_correct = mfs_prediction == target
                        gloss_correct = gloss_prediction == target
                        seen = bool(train_counts[key])
                        counts['mfs_correct'] += mfs_correct
                        counts['gloss_correct'] += gloss_correct
                        counts['mfs_unseen_key'] += not seen
                        counts['both_correct'] += mfs_correct and gloss_correct
                        counts['mfs_only_correct'] += mfs_correct and not gloss_correct
                        counts['gloss_only_correct'] += gloss_correct and not mfs_correct
                        counts['neither_correct'] += not mfs_correct and not gloss_correct
                        for group in ('one_candidate' if len(candidates) == 1 else 'multiple_candidates',
                                      'lemma_pos_seen' if seen else 'lemma_pos_unseen'):
                            slices[group]['covered'] += 1
                            slices[group]['mfs_correct'] += mfs_correct
                            slices[group]['gloss_correct'] += gloss_correct
    denominator = counts['eligible_tokens']
    covered = counts['covered']
    result = {'split_seed': 17, 'document_counts': {k: len(v) for k, v in split.items()},
              'counts': dict(counts), 'posthoc_slices': {key: dict(val) for key, val in sorted(slices.items())},
              'accuracy_covered': {k: counts[k + '_correct'] / covered if covered else None for k in ('mfs', 'gloss')},
              'accuracy_all_eligible': {k: counts[k + '_correct'] / denominator if denominator else None for k in ('mfs', 'gloss')},
              'inputs_sha256': {'semcor.zip': digest(args.nltk_data / 'corpora/semcor.zip'),
                                'wordnet.zip': digest(args.nltk_data / 'corpora/wordnet.zip'),
                                'oewn_entries.zip': digest(args.oewn_zip), 'nodes.tsv': digest(args.nodes)},
              'split_ids_sha256': hashlib.sha256(json.dumps(split, sort_keys=True).encode()).hexdigest(),
              'nltk_version': nltk.__version__,
              'limits': 'Exploratory SemCor dev only; targets from observed surface and annotated POS; RDF entities excluded; no held-out test or standard benchmark.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps({'counts': result['counts'], 'accuracy_covered': result['accuracy_covered'],
                      'accuracy_all_eligible': result['accuracy_all_eligible']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
