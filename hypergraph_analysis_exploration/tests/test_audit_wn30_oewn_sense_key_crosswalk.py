import unittest

from src.analysis.audit_wn30_oewn_sense_key_crosswalk import _synset_alignment


class WordNetOewnSenseKeyCrosswalkTests(unittest.TestCase):
    def test_counts_complete_partial_conflicting_and_unmatched_synsets(self):
        wordnet = {
            "one%1:00:00::": ("n", "00000001"),
            "two%1:00:00::": ("n", "00000001"),
            "three%1:00:00::": ("n", "00000002"),
            "four%1:00:00::": ("n", "00000002"),
            "five%1:00:00::": ("n", "00000003"),
        }
        oewn = {
            "one%1:00:00::": {"oewn-00000001-n"},
            "two%1:00:00::": {"oewn-00000001-n"},
            "three%1:00:00::": {"oewn-00000002-n"},
            "four%1:00:00::": {"oewn-00000003-n"},
        }

        result = _synset_alignment(wordnet, oewn)

        self.assertEqual(result["exact_oewn_sense_key_matches"], 4)
        self.assertEqual(result["synsets_all_keys_map_to_one_oewn_synset"], 1)
        self.assertEqual(result["synsets_with_multiple_oewn_targets"], 1)
        self.assertEqual(result["synsets_with_no_oewn_target"], 1)
        self.assertEqual(result["synsets_partially_mapped_to_one_oewn_synset"], 0)

    def test_one_missing_member_is_partial_mapping(self):
        wordnet = {
            "one%1:00:00::": ("n", "00000001"),
            "two%1:00:00::": ("n", "00000001"),
        }
        result = _synset_alignment(wordnet, {"one%1:00:00::": {"oewn-00000001-n"}})
        self.assertEqual(result["synsets_partially_mapped_to_one_oewn_synset"], 1)

    def test_duplicate_oewn_sense_key_targets_are_conflicting(self):
        wordnet = {"one%1:00:00::": ("n", "00000001")}
        oewn = {"one%1:00:00::": {"oewn-00000001-n", "oewn-00000002-n"}}
        result = _synset_alignment(wordnet, oewn)
        self.assertEqual(result["sense_keys_with_multiple_oewn_targets"], 1)
        self.assertEqual(result["synsets_with_multiple_oewn_targets"], 1)

    def test_alignment_reports_pos_stratified_coverage(self):
        wordnet = {
            "one%1:00:00::": ("n", "00000001"),
            "run%2:00:00::": ("v", "00000002"),
        }
        result = _synset_alignment(wordnet, {"one%1:00:00::": {"oewn-00000001-n"}})
        self.assertEqual(result["by_pos"]["n"]["sense_key_coverage_percent"], 100.0)
        self.assertEqual(result["by_pos"]["v"]["sense_key_coverage_percent"], 0.0)


if __name__ == "__main__":
    unittest.main()
