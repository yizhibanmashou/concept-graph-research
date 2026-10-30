import unittest
from src.analysis.tiny_bert_candidate_coverage_audit import summarize_sizes


class CandidateCoverageTests(unittest.TestCase):
    def test_size_summary_is_deterministic(self):
        self.assertEqual(summarize_sizes([9, 2, 4, 3]), {'min': 2, 'median_lower': 3, 'p90_lower': 4, 'max': 9})
        with self.assertRaises(ValueError):
            summarize_sizes([])


if __name__ == '__main__':
    unittest.main()
