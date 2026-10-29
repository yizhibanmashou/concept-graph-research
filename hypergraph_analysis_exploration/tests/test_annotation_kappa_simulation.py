import unittest

from src.analysis.simulate_annotation_kappa_ci import _joint_probabilities, run_simulation


def small_design_manifest():
    strata = {
        "s1": {"population_count": 30, "sample_count": 4, "design_weight": 7.5},
        "s2": {"population_count": 40, "sample_count": 4, "design_weight": 10.0},
        "s3": {"population_count": 50, "sample_count": 4, "design_weight": 12.5},
    }
    return {
        "eligible_oewn_sense_count": 120,
        "random_panel_count": 12,
        "random_panel_strata": strata,
    }


class AnnotationKappaSimulationTests(unittest.TestCase):
    def test_scenario_joint_probabilities_are_valid(self):
        for scenario in (
            "balanced_three_category", "rare_category", "near_zero_kappa",
            "near_degenerate_margins", "stratum_heterogeneity",
        ):
            for stratum_index in range(24):
                probabilities = _joint_probabilities(scenario, stratum_index)
                self.assertEqual(len(probabilities), 9)
                self.assertTrue(all(value >= 0 for value in probabilities))
                self.assertAlmostEqual(sum(probabilities), 1.0)

    def test_simulation_is_reproducible_for_fixed_design_and_seed(self):
        first = run_simulation(small_design_manifest(), replicates=40, seed=271828)
        second = run_simulation(small_design_manifest(), replicates=40, seed=271828)
        self.assertEqual(first, second)
        by_name = {scenario["scenario"]: scenario for scenario in first["scenarios"]}
        for scenario in first["scenarios"]:
            self.assertEqual(scenario["point_estimates_valid"] + scenario["undefined_point_estimate"], 40)
            self.assertEqual(
                scenario["replicates_valid"] + scenario["taylor_interval_unavailable"]
                + scenario["undefined_point_estimate"], 40,
            )
            self.assertEqual(
                scenario["jackknife_valid"] + scenario["jackknife_interval_unavailable"]
                + scenario["jackknife_undefined_estimate"], 40,
            )
        self.assertLess(by_name["near_degenerate_margins"]["replicates_valid"], 40)


if __name__ == "__main__":
    unittest.main()
