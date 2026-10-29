"""Untrained lexical reverse-dictionary baseline over target glosses.

This is a word-overlap retrieval baseline; it does not understand direction,
negation or graph structure. No candidate is selected using a test answer.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import heapq
import json
import math
from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[2]
TOKEN = re.compile(r"[a-z]+(?:'[a-z]+)?")

def tokenize(text):
    return TOKEN.findall(text.casefold())

class GlossIndex:
    def __init__(self, rows):
        self.rows = {}
        self.postings = defaultdict(list)
        total = 0
        for row in rows:
            identity = row['synset_id']
            if identity in self.rows:
                raise ValueError('duplicate sense ID')
            counts = Counter(tokenize(row['definition']))
            length = sum(counts.values())
            self.rows[identity] = (row, length)
            total += length
            for term, count in counts.items():
                self.postings[term].append((identity, count))
        self.average_length = total / len(self.rows) if self.rows else 0

    def search(self, query, limit=10):
        if limit < 1:
            raise ValueError('limit must be positive')
        scores = defaultdict(float)
        n = len(self.rows)
        for term in set(tokenize(query)):
            postings = self.postings.get(term, ())
            if not postings:
                continue
            idf = math.log(1 + (n - len(postings) + 0.5) / (len(postings) + 0.5))
            for identity, tf in postings:
                length = self.rows[identity][1]
                norm = 1 - 0.75 + 0.75 * length / self.average_length
                scores[identity] += idf * tf * 2.2 / (tf + 1.2 * norm)
        best = heapq.nsmallest(limit, scores, key=lambda x: (-scores[x], x))
        return [{'id': x, 'lemmas': self.rows[x][0]['lemmas'],
                 'gloss': self.rows[x][0]['definition'], 'score': scores[x]} for x in best]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--nodes', type=Path, default=PROJECT.parent / 'OEWN/graph/nodes.tsv')
    p.add_argument('--query', required=True)
    p.add_argument('--limit', type=int, default=10)
    args = p.parse_args()
    with args.nodes.open(encoding='utf-8-sig', newline='') as f:
        index = GlossIndex(csv.DictReader(f, delimiter='\t'))
    print(json.dumps({'query': args.query, 'results': index.search(args.query, args.limit),
                      'notice': 'Lexical baseline only; not a semantic or role-sensitive ranking.'}, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
