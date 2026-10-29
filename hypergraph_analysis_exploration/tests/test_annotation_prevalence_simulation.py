import unittest

from src.analysis.simulate_annotation_prevalence_ci import (
    SCENARIOS,
    _stratum_probability,
    _transformed_interval,
    run_simulation,
)


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


class AnnotationPrevalenceSimulationTests(unittest.TestCase):
    def test_scenarios_cover_balanced_rare_and_heterogeneous_prevalence(self):
        self.assertEqual(len(SCENARIOS), 5)
        self.assertEqual(_stratum_probability("balanced_prevalence", 0, 24), 0.5)
        self.assertEqual(_stratum_probability("rare_prevalence", 0, 24), 0.01)
        self.assertLess(
            _stratum_probability("stratum_heterogeneity", 0, 24),
            _stratum_probability("stratum_heterogeneity", 23, 24),
        )
        with self.assertRaises(ValueError):
            _stratum_probability("unknown", 0, 24)

    def test_transformed_diagnostic_intervals_stay_bounded_and_report_boundary_limits(self):
        for method in ("logit_delta", "arcsine_delta"):
            interval = _transformed_interval(0.01, 0.005, method)
            self.assertGreaterEqual(interval["lower"], 0.0)
            self.assertLessEqual(interval["upper"], 1.0)
            self.assertIsNone(_transformed_interval(0.0, 0.01, method))
            self.assertIsNone(_transformed_interval(0.5, 0.0, method))

    def test_simulation_is_reproducible_and_reports_availability_denominators(self):
        first = run_simulation(small_design_manifest(), replicates=30, seed=314159, population_replicates=2)
        second = run_simulation(small_design_manifest(), replicates=30, seed=314159, population_replicates=2)
        self.assertEqual(first, second)
        self.assertEqual(first["simulation_version"], "stratified-prevalence-interval-simulation/2")
        for row in first["scenarios"]:
            self.assertEqual(
                row["intervals_reported"] + row["interval_unavailable_zero_estimated_variance"],
                row["replicates_requested"],
            )
            self.assertEqual(row["valid_point_estimates"], row["replicates_requested"])
            self.assertEqual(row["interval_availability_rate"], row["intervals_reported"] / row["replicates_requested"])
            self.assertEqual(row["population_replicates"], 2)
            self.assertEqual(len(row["population_runs"]), 2)
            self.assertEqual(sum(run["covered_intervals"] for run in row["population_runs"]), row["covered_intervals"])
            self.assertIn("logit_delta", row["transformed_interval_diagnostics"])
            self.assertAlmostEqual(
                row["covered_and_reported_rate"],
                (row["conditional_coverage"] or 0.0) * row["interval_availability_rate"],
            )


if __name__ == "__main__":
    unittest.main()
