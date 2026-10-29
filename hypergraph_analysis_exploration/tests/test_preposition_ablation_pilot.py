import csv
import json
import tempfile
import unittest
from pathlib import Path
from src.analysis.preposition_ablation_pilot import run


class PrepositionAblationPilotTests(unittest.TestCase):
    def test_truncation_removes_preposition_and_descendants_but_not_other_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            graph = root / 'bundle' / 'graph'
            graph.mkdir(parents=True)
            exp = root / 'experiment'
            exp.mkdir()
            with (graph / 'nodes.tsv').open('w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=['synset_id', 'pos', 'is_basis'], delimiter='\t')
                w.writeheader()
                w.writerows([
                    {'synset_id': 'root', 'pos': 'n', 'is_basis': 'false'},
                    {'synset_id': 'prep', 'pos': 'prep', 'is_basis': 'false'},
                    {'synset_id': 'a', 'pos': 'n', 'is_basis': 'true'},
                    {'synset_id': 'b', 'pos': 'n', 'is_basis': 'true'},
                ])
            rules = [{'head': 'root', 'witness_clause': ['prep', 'a']},
                     {'head': 'prep', 'witness_clause': ['b']},
                     {'head': 'a', 'witness_clause': []},
                     {'head': 'b', 'witness_clause': []}]
            (graph / 'coverage_witnesses.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in rules), encoding='utf-8')
            (exp / 'evaluation_root_ids.txt').write_text('root\n', encoding='utf-8')
            candidates = root / 'candidates.json'
            candidates.write_text(json.dumps({'top20': [{'pair': [{'id': 'a', 'lemmas': 'A'}, {'id': 'b', 'lemmas': 'B'}]}]}), encoding='utf-8')
            result = run(root / 'bundle', exp, candidates, 2)
            self.assertEqual(result['stats']['roots_with_prep_encountered'], 1)
            self.assertEqual(result['stats']['original_frontier_total'], 2)
            self.assertEqual(result['stats']['cut_frontier_total'], 1)
            self.assertEqual(result['pairs'][0]['original_support'], 1)
            self.assertEqual(result['pairs'][0]['cut_support'], 0)


if __name__ == '__main__':
    unittest.main()
