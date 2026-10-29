"""Evaluate a no-training lexical-coverage baseline on six fixed examples.

The label is read after scores have been computed. Ties are evaluated by their
uniform expected reciprocal rank and expected top-1, avoiding ID/order bias.
"""
import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bundle', type=Path, default=BASE / 'model')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    cases = ['bear', 'life', 'hand_in_hand', 'all_along', 'immobility', 'impermissible']
    rows = []
    for case in cases:
        folder = args.bundle / 'cases' / case
        candidates = [json.loads(line) for line in (folder / 'results/candidates.jsonl').read_text(encoding='utf-8').splitlines()]
        # Only count used input occurrence IDs. No reference, formula text, or training data is used in the score.
        scored = [(c['candidate_id'], len(set(c['used_occurrence_ids']))) for c in candidates]
        reference = json.loads((folder / 'expected/selection.json').read_text(encoding='utf-8'))['candidate_id']
        scores = [s for cid, s in scored if cid == reference]
        if len(scores) != 1: raise ValueError(f'{case}: reference not unique')
        score = scores[0]
        above = sum(s > score for _, s in scored)
        tied = sum(s == score for _, s in scored)
        ranks = range(above + 1, above + tied + 1)
        rows.append({'case': case, 'candidates': len(scored), 'higher': above, 'tied': tied,
                     'expected_reciprocal_rank': sum(1 / r for r in ranks) / tied,
                     'expected_top1': 1 / tied if above == 0 else 0})
    result = {'baseline': 'unique-input-occurrence-coverage', 'cases': rows,
              'mean_expected_reciprocal_rank': sum(r['expected_reciprocal_rank'] for r in rows)/len(rows),
              'mean_expected_top1': sum(r['expected_top1'] for r in rows)/len(rows),
              'scope': 'Descriptive six-example in-sample baseline, not an independent benchmark or semantic validation.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f: json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
