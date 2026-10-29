import unittest
from src.analysis.sense_representation_pilot import build


class SenseRepresentationPilotTests(unittest.TestCase):
    def test_matched_dependency_information_and_branch_structure(self):
        result = build('h', 'head', [['x', 'y'], ['y', 'z']], {'x': 'one', 'y': 'two', 'z': 'three'})
        self.assertEqual(result['B']['dependencies'], result['C']['dependencies'])
        self.assertEqual(result['B']['dependencies'], result['D']['dependencies'])
        self.assertEqual(result['D']['branches'], [['x', 'y'], ['y', 'z']])
        self.assertEqual(len(result['C']['edges']), 3)
        self.assertNotIn('dependencies', result['A'])

    def test_missing_dependency_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'missing'):
            build('h', 'head', [['x']], {})


if __name__ == '__main__': unittest.main()
