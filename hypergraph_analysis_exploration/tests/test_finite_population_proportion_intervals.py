import unittest

from src.analysis.finite_population_proportion_intervals import (
    hypergeometric_exact_interval,
    hypergeometric_pmf,
    stratified_supported_interval,
)


class FinitePopulationIntervalTests(unittest.TestCase):
    def test_equal_tailed_interval_has_at_least_nominal_coverage_exhaustively(self):
        confidence = 0.90
        for N in range(2, 9):
            for n in range(1, N + 1):
                for true_successes in range(N + 1):
                    coverage = 0.0
                    low_support = max(0, n - (N - true_successes))
                    high_support = min(n, true_successes)
                    for observed in range(low_support, high_support + 1):
                        lower, upper = hypergeometric_exact_interval(
                            N, n, observed, confidence
                        )
                        if lower <= true_successes <= upper:
                            coverage += hypergeometric_pmf(
                                N, true_successes, n, observed
                            )
                    self.assertGreaterEqual(coverage + 1e-12, confidence)

    def test_census_returns_exact_finite_population_proportion(self):
        self.assertEqual(hypergeometric_exact_interval(12, 12, 7), (7, 7))
        self.assertEqual(hypergeometric_exact_interval(10, 4, 0)[0], 0)
        self.assertEqual(hypergeometric_exact_interval(10, 4, 4)[1], 10)

    def test_stratified_bounds_are_bonferroni_weighted_and_bound_missingness(self):
        report = stratified_supported_interval({
            "a": {"population_n": 100, "sample_n": 20, "supported_n": 8},
            "b": {"population_n": 300, "sample_n": 20, "supported_n": 9, "missing_n": 2},
        })
        self.assertAlmostEqual(report["stratum_confidence_level"], 0.975)
        self.assertIsNone(report["population_weighted_supported_prevalence_point_estimate"])
        bounds = report["strata"]["b"]["supported_proportion_bounds"]
        low_only = hypergeometric_exact_interval(300, 20, 9, 0.975)[0] / 300
        high_with_missing = hypergeometric_exact_interval(300, 20, 11, 0.975)[1] / 300
        self.assertAlmostEqual(bounds[0], low_only)
        self.assertAlmostEqual(bounds[1], high_with_missing)
        self.assertLessEqual(report["population_weighted_supported_prevalence_bounds"][0],
                             report["population_weighted_supported_prevalence_bounds"][1])

    def test_complete_strata_return_weighted_point_and_validation_rejects_bad_counts(self):
        report = stratified_supported_interval({
            "a": {"population_n": 100, "sample_n": 20, "supported_n": 8},
            "b": {"population_n": 300, "sample_n": 20, "supported_n": 10},
        })
        self.assertAlmostEqual(report["population_weighted_supported_prevalence_point_estimate"], 0.475)
        self.assertLessEqual(report["population_weighted_supported_prevalence_bounds"][0], 0.475)
        self.assertGreaterEqual(report["population_weighted_supported_prevalence_bounds"][1], 0.475)
        with self.assertRaisesRegex(ValueError, "invalid sample counts"):
            stratified_supported_interval({
                "bad": {"population_n": 10, "sample_n": 5, "supported_n": 4, "missing_n": 2}
            })


if __name__ == "__main__":
    unittest.main()
