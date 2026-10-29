import unittest

from src.analysis.build_oewn_instance_manual_audit_frame import build_candidate_rows


class InstanceManualAuditFrameTests(unittest.TestCase):
    def setUp(self):
        noun_ids = ("i1", "c1", "i2", "c2", "middle", "root", "other1", "other2")
        self.nodes = {sid: {"pos": "n", "source_file": "noun.test.json"} for sid in noun_ids}
        self.nodes.update({"v1": {"pos": "v", "source_file": "verb.test.json"},
                           "v2": {"pos": "v", "source_file": "verb.test.json"}})
        self.instance_parents = {sid: () for sid in self.nodes}
        self.instance_parents.update({"i1": ("c1",), "i2": ("c2",)})
        self.class_parents = {sid: () for sid in self.nodes}
        self.class_parents.update({"c1": ("middle",), "c2": ("middle",), "middle": ("root",)})

    def test_text_free_candidates_and_hidden_key_have_deterministic_strata(self):
        candidates, key, counts = build_candidate_rows(
            self.nodes, self.instance_parents, self.class_parents, per_stratum=2
        )
        repeat = build_candidate_rows(self.nodes, self.instance_parents, self.class_parents, per_stratum=2)
        self.assertEqual((candidates, key, counts), repeat)
        self.assertEqual(len(candidates), 10)
        self.assertEqual(len(key), 10)
        self.assertEqual(set(counts.values()), {2})
        self.assertTrue(all(set(row) == {"candidate_id", "instance_synset_id", "class_synset_id"}
                            for row in candidates))
        self.assertTrue(all(not any(stratum in row["candidate_id"] for stratum in counts)
                            for row in candidates))
        self.assertTrue(all(set(row) == {"candidate_id", "stratum", "resource_status", "class_lift_depth",
                                        "within_source_target_population_count"}
                            for row in key))
        by_stratum = {row["stratum"]: row for row in key}
        self.assertEqual(by_stratum["direct_edge"]["resource_status"], "direct_instance_membership")
        self.assertEqual(by_stratum["lift_one_class_edge"]["class_lift_depth"], 1)
        self.assertEqual(by_stratum["lift_two_plus_class_edges"]["class_lift_depth"], 2)

    def test_refuses_impossible_sample_size(self):
        with self.assertRaisesRegex(ValueError, "candidates; need"):
            build_candidate_rows(self.nodes, self.instance_parents, self.class_parents, per_stratum=20)


if __name__ == "__main__":
    unittest.main()
