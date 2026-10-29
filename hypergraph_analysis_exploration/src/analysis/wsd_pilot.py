"""Candidate-limited lexical WSD smoke test over the frozen graph.

Uses original glosses only. This is neither a trained system nor a standard
all-words benchmark, and does not perform OEWN-to-WordNet mapping.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from src.analysis.reverse_dictionary_pilot import GlossIndex, PROJECT


def candidates(rows, lemma, pos):
    lemma = lemma.casefold().strip()
    return [row for row in rows if row['pos'] == pos and lemma in
            {part.strip().casefold() for part in row['lemmas'].split('/')}]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--nodes', type=Path, default=PROJECT.parent / 'OEWN/graph/nodes.tsv')
    p.add_argument('--lemma', required=True)
    p.add_argument('--pos', required=True)
    p.add_argument('--context', required=True)
    p.add_argument('--limit', type=int, default=5)
    args = p.parse_args()
    if args.limit < 1:
        p.error('limit must be positive')
    with args.nodes.open(encoding='utf-8-sig', newline='') as f:
        selected = candidates(csv.DictReader(f, delimiter='\t'), args.lemma, args.pos)
    if not selected:
        raise ValueError('no candidate senses for this lemma and part of speech')
    hits = GlossIndex(selected).search(args.context, len(selected))
    print(json.dumps({'lemma': args.lemma, 'pos': args.pos, 'candidate_count': len(selected),
                      'ranked_overlap_candidates': hits[:args.limit],
                      'unranked_candidates': len(selected)-len(hits),
                      'notice': 'Gloss overlap only. Zero-overlap candidates remain unranked; no gold label or independent benchmark.'}, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
