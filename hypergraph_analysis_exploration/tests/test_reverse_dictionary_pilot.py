import unittest
import os
import subprocess
import sys
from src.analysis.reverse_dictionary_pilot import GlossIndex


class ReverseDictionaryTests(unittest.TestCase):
    def test_ranks_gloss_terms_without_target_labels(self):
        rows = [dict(synset_id='a', lemmas='cat', definition='small furry animal'),
                dict(synset_id='b', lemmas='table', definition='flat wooden furniture')]
        index = GlossIndex(rows)
        self.assertEqual(index.search('furry animal')[0]['id'], 'a')
        self.assertEqual(index.search('unknown'), [])

    def test_duplicate_id_is_rejected(self):
        row = dict(synset_id='a', lemmas='x', definition='thing')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            GlossIndex([row, row])

    def test_scores_stable_across_python_hash_seeds(self):
        code = """import json
from src.analysis.reverse_dictionary_pilot import GlossIndex
rows = [dict(synset_id='a', lemmas='a', definition='alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon phi chi psi omega'),
        dict(synset_id='b', lemmas='b', definition='alpha alpha gamma delta epsilon eta theta iota lambda nu xi pi rho tau phi psi')]
print(json.dumps(GlossIndex(rows).search('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon phi chi psi omega')))
"""
        outputs = []
        for seed in ('1', '2'):
            env = {**os.environ, 'PYTHONHASHSEED': seed}
            outputs.append(subprocess.check_output([sys.executable, '-c', code], env=env, text=True))
        self.assertEqual(outputs[0], outputs[1])


if __name__ == '__main__': unittest.main()
