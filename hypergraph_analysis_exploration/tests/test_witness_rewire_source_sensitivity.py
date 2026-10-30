import unittest
from src.analysis.witness_rewire_source_sensitivity import SOURCES, source_groups


class SourceSensitivityTests(unittest.TestCase):
    def test_grouping_preserves_supplied_root_order(self):
        nodes = [{'synset_id': 'a', 'source_root': SOURCES[0]},
                 {'synset_id': 'b', 'source_root': SOURCES[1]},
                 {'synset_id': 'c', 'source_root': SOURCES[0]}]
        self.assertEqual(source_groups(['c', 'b', 'a'], nodes), {SOURCES[0]: ['c', 'a'], SOURCES[1]: ['b']})

    def test_missing_or_duplicate_nodes_fail(self):
        with self.assertRaises(ValueError):
            source_groups(['a'], [{'synset_id': 'a', 'source_root': SOURCES[0]}] * 2)


if __name__ == '__main__':
    unittest.main()
