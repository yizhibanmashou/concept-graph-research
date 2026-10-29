import unittest

from src.analysis.audit_instance_relation_frame_precision import (
    audit_manifest,
    minimum_n_for_contrast_margin,
    minimum_n_for_worst_case_margin,
)


def synthetic_manifest():
    return {
        "candidate_count": 320,
        "stratum_counts": {
            "direct_edge": 64,
            "lift_one_class_edge": 64,
            "lift_two_plus_class_edges": 64,
            "reverse_direct_challenge": 64,
            "same_pos_nonclosure_challenge": 64,
        },
        "population_counts": {
            "direct_edge": 100,
            "lift_one_class_edge": 200,
            "lift_two_plus_class_edges": 400,
            "reverse_direct_challenge": 100,
            "same_pos_nonclosure_challenge": {
                "eligible_source_synset_count": 200,
                "noun_target_synset_count": 1000,
            },
        },
    }


class InstanceRelationFramePrecisionTests(unittest.TestCase):
    def test_reports_stratum_weighted_and_challenge_design_separately(self):
        report = audit_manifest(synthetic_manifest())
        self.assertAlmostEqual(
            report["per_stratum"]["direct_edge"]["worst_case_95pct_normal_half_width"],
            1.959963984540054 * (0.25 / 64 * (100 - 64) / 99) ** 0.5,
        )
        self.assertAlmostEqual(sum(report["positive_closure_weighted_total"]["stratum_weights"].values()), 1.0)
        self.assertEqual(report["same_pos_challenge"]["source_sample_n"], 64)
        self.assertIn("macro-average", report["same_pos_challenge"]["estimand"])
        self.assertFalse(report["confirmatory_power_calculated"])
        self.assertEqual(report["annotation_workload_at_two_annotators"], 640)

    def test_sample_size_for_worst_case_ten_point_margin(self):
        self.assertEqual(minimum_n_for_worst_case_margin(8599, 0.10), 95)
        self.assertEqual(minimum_n_for_worst_case_margin(50574, 0.10), 96)
        self.assertEqual(minimum_n_for_contrast_margin(8599, 9112, 0.10), 189)
        self.assertEqual(minimum_n_for_contrast_margin(9112, 50574, 0.10), 190)

    def test_rejects_invalid_sample_and_margin_inputs(self):
        manifest = synthetic_manifest()
        manifest["stratum_counts"]["direct_edge"] = 101
        with self.assertRaisesRegex(ValueError, "exceeds population"):
            audit_manifest(manifest)
        with self.assertRaisesRegex(ValueError, "between 0 and 0.5"):
            minimum_n_for_worst_case_margin(100, 0.5)


if __name__ == "__main__":
    unittest.main()
