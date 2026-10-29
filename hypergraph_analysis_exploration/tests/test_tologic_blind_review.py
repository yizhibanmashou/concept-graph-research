import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


path = Path(__file__).resolve().parents[1] / 'research/tologic/blind_review.py'
spec = importlib.util.spec_from_file_location('blind_review', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BlindReviewTests(unittest.TestCase):
    def test_reproducible_and_no_reference_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'input.json'
            candidates = root / 'candidates.jsonl'
            source.write_text(json.dumps({'source': {'definition': 'have', 'lemmas': ['bear']},
                'usage': {'sentence_a': 'A', 'sentence_b': 'B', 'parameters': [],
                          'argumentation': 'REFERENCE_SECRET'}}), encoding='utf-8')
            rows = [{'candidate_id': f'id{i}', 'readable_formula': f'F{i}',
                     'semantic_acceptance': True, 'inventory': {'expected': 'REFERENCE_SECRET'}} for i in range(8)]
            candidates.write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
            public, key = module.prepare(source, candidates, 4, 19)
            self.assertEqual((public, key), module.prepare(source, candidates, 4, 19))
            self.assertEqual(len(public['items']), 4)
            self.assertNotIn('REFERENCE_SECRET', json.dumps(public))
            self.assertNotIn('candidate_id', json.dumps(public))
            self.assertEqual(len({r['candidate_id'] for r in key['mapping']}), 4)
            self.assertNotEqual(key['mapping'], module.prepare(source, candidates, 4, 20)[1]['mapping'])
            with self.assertRaises(ValueError):
                module.prepare(source, candidates, 9, 19)


if __name__ == '__main__':
    unittest.main()
