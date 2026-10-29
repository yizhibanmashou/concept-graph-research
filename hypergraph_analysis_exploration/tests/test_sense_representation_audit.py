import copy
import unittest
from src.analysis.sense_representation_pilot import build
from src.analysis.sense_representation_audit import audit


class SenseAuditTests(unittest.TestCase):
    def test_counts_and_detects_mismatched_information(self):
        item = build('h', 'head', [['x', 'y'], ['y']], {'x': 'one', 'y': 'two'})
        result = audit([item])[0]
        self.assertEqual((result['dependency_count'], result['branch_count']), (2, 2))
        self.assertGreater(result['json_characters']['D'], result['json_characters']['A'])
        for mutate in (
            lambda x: x['C']['dependencies'].pop(),
            lambda x: x['C']['edges'].pop(),
            lambda x: x['D']['branches'].append([]),
            lambda x: x['D']['branches'].__setitem__(0, ['unknown']),
            lambda x: x['B'].__setitem__('gloss', 'different'),
        ):
            changed = copy.deepcopy(item)
            mutate(changed)
            with self.assertRaises(ValueError):
                audit([changed])
