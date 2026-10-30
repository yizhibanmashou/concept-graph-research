"""Audit explicit user-supplied without calls in enumerated want candidates.

This validates syntax and bookkeeping only, not whether formulas are true.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def operators(value):
    if isinstance(value, dict):
        if 'op' in value:
            yield value['op']
        for child in value.values():
            yield from operators(child)
    elif isinstance(value, list):
        for child in value:
            yield from operators(child)


def lexical_uses(value):
    if isinstance(value, dict):
        if value.get('op') == 'use':
            yield value.get('occurrence_id')
        for child in value.values():
            yield from lexical_uses(child)
    elif isinstance(value, list):
        for child in value:
            yield from lexical_uses(child)


def audit(source, candidates):
    occurrences = source['usage']['occurrence_ids']
    if len(occurrences) != 1:
        raise ValueError('expected a single declared occurrence')
    occurrence = occurrences[0]
    ids = set()
    counts = Counter()
    bindings = Counter()
    for row in candidates:
        if row['candidate_id'] in ids:
            raise ValueError('duplicate candidate')
        ids.add(row['candidate_id'])
        if row['formula']['synset_id'] != source['source']['synset_id']:
            raise ValueError('candidate source mismatch')
        lexical = row['binding_plan']['lexical']
        matching = [v for v in lexical if v['occurrence_id'] == occurrence]
        if len(matching) > 1 or any(v['occurrence_id'] != occurrence for v in lexical):
            raise ValueError('unexpected lexical occurrence')
        if set(row['used_occurrence_ids']) != {v['occurrence_id'] for v in lexical}:
            raise ValueError('used occurrence bookkeeping mismatch')
        if Counter(lexical_uses(row['formula']['rhs'])) != Counter(v['occurrence_id'] for v in lexical):
            raise ValueError('formula and binding plan disagree')
        if matching:
            binding = matching[0]['bindings']
            key = tuple(sorted(binding.items()))
            bindings[key] += 1
            counts['same_named_binding' if binding == {'e': 'e', 's': 's', 'h': 'h'} else 'other_binding'] += 1
        else:
            counts['without_not_called'] += 1
            ops = set(operators(row['formula']['rhs']))
            if not ops.intersection({'not', 'neg', 'negation', 'use'}):
                counts['no_call_and_no_explicit_negation_operator'] += 1
    return {'total': len(candidates), 'without_not_called': counts['without_not_called'],
            'same_named_binding': counts['same_named_binding'], 'other_binding': counts['other_binding'],
            'no_call_and_no_explicit_negation_operator': counts['no_call_and_no_explicit_negation_operator'],
            'binding_counts': [{'bindings': dict(key), 'count': count} for key, count in sorted(bindings.items())]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--candidates', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding='utf-8'))
    with args.candidates.open(encoding='utf-8') as f:
        candidates = [json.loads(line) for line in f if line.strip()]
    result = {'protocol': 'want-without-interface-audit/1', 'counts': audit(source, candidates),
              'inputs_sha256': {'input': digest(args.input), 'candidates': digest(args.candidates)},
              'limits': 'Syntactic counts only; no gold, semantic truth, annotation, or new basis member.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
