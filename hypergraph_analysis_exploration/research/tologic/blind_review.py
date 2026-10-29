"""Prepare a seeded, reference-free candidate sample for manual review."""
import argparse
import hashlib
import json
import random
from pathlib import Path


def prepare(input_path, candidates_path, sample_size, seed):
    source_bytes = input_path.read_bytes()
    candidate_bytes = candidates_path.read_bytes()
    source = json.loads(source_bytes)
    candidates = [json.loads(line) for line in candidate_bytes.splitlines() if line.strip()]
    if not 0 < sample_size <= len(candidates):
        raise ValueError("sample size must be between 1 and the number of candidates")
    ids = [row['candidate_id'] for row in candidates]
    if len(ids) != len(set(ids)):
        raise ValueError("candidate IDs must be unique")
    if any(not isinstance(row.get('readable_formula'), str) for row in candidates):
        raise ValueError("every candidate must have a readable formula")
    chosen = random.Random(seed).sample(candidates, sample_size)
    usage = source['usage']
    public = {
        'scope': 'Exploratory single-usage review; candidate sampling is not semantic validation.',
        'definition': source['source']['definition'],
        'lemmas': source['source']['lemmas'],
        'sentence_a': usage['sentence_a'],
        'sentence_b': usage['sentence_b'],
        'parameters': usage['parameters'],
        'items': [{'review_id': f'R{i:04d}', 'formula': c['readable_formula'],
                   'judgment': None, 'reason': ''} for i, c in enumerate(chosen, 1)],
    }
    key = {
        'seed': seed, 'sample_size': sample_size, 'population_size': len(candidates),
        'input_sha256': hashlib.sha256(source_bytes).hexdigest(),
        'candidates_sha256': hashlib.sha256(candidate_bytes).hexdigest(),
        'mapping': [{'review_id': f'R{i:04d}', 'candidate_id': c['candidate_id']}
                    for i, c in enumerate(chosen, 1)],
    }
    return public, key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--candidates', type=Path, required=True)
    parser.add_argument('--size', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True, help='new output directory')
    args = parser.parse_args()
    public, key = prepare(args.input, args.candidates, args.size, args.seed)
    args.out.mkdir(parents=True, exist_ok=False)
    for name, data in [('review.json', public), ('private-key.json', key)]:
        (args.out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Exported {len(public['items'])} candidates; keep private-key.json separate from reviewers.")


if __name__ == '__main__':
    main()
