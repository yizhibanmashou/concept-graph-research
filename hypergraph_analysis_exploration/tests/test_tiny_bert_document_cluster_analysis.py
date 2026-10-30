import unittest
from io import BytesIO
from zipfile import ZipFile

from src.analysis.tiny_bert_document_cluster_analysis import (
    bootstrap_by_document, correctness_by_target, map_sample_documents, stable_hash,
)


class TinyBertDocumentClusterTests(unittest.TestCase):
    def test_sample_hashes_join_to_pseudonymous_document_clusters(self):
        memory = BytesIO()
        with ZipFile(memory, 'w') as archive:
            archive.writestr('semcor/doc.xml',
                             '<corpus><s><wf wnsn="1" lexsn="x">pivot</wf></s></corpus>')
        memory.seek(0)
        sample_id = stable_hash('doc.xml:0:0')
        with ZipFile(memory) as archive:
            clusters = map_sample_documents(archive, ['doc.xml'], [sample_id])
        self.assertEqual(clusters[sample_id], stable_hash('semcor-document:doc.xml'))
        self.assertNotIn('doc.xml', clusters[sample_id])

    def test_seed_predictions_are_averaged_within_target_before_cluster_bootstrap(self):
        rows = [
            {'sample_id': 'a', 'label': 0, 'candidate_ids': ['x', 'y'], 'gold_candidate_id': 'x'},
            {'sample_id': 'b', 'label': 0, 'candidate_ids': ['x', 'y'], 'gold_candidate_id': 'x'},
            {'sample_id': 'c', 'label': -1, 'candidate_ids': ['x'], 'gold_candidate_id': None},
        ]
        runs = []
        for predictions in ([0, 1, 0], [1, 1, 0]):
            runs.append({'dev': {condition: {'predictions': predictions}
                                 for condition in ('A', 'B', 'C', 'D')}})
        scores = correctness_by_target(rows, runs)
        self.assertEqual(scores['A'], {'a': 0.5, 'b': 0.0, 'c': 0.0})
        result = bootstrap_by_document(rows, {'a': 'd1', 'b': 'd1', 'c': 'd2'}, scores,
                                       replicates=50, seed=3)
        self.assertEqual(result['document_clusters'], 2)
        self.assertEqual(result['replicates'], 50)


if __name__ == '__main__':
    unittest.main()
