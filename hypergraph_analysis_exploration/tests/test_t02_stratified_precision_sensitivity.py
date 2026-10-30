import unittest

from src.analysis.t02_stratified_precision_sensitivity import (
    BOTH,
    COLLISION,
    EMPTY,
    OTHER,
    UNAFFECTED,
    allocate_targets,
    scenario,
)


class T02StratifiedPrecisionSensitivityTests(unittest.TestCase):
    def setUp(self):
        self.population = {
            EMPTY: 508,
            COLLISION: 501,
            BOTH: 4,
            OTHER: 88045,
            UNAFFECTED: 21367,
        }
        self.branches = {
            EMPTY: 1102,
            COLLISION: 1599,
            BOTH: 19,
            OTHER: 123823,
            UNAFFECTED: 27663,
        }

    def test_two_hundred_target_allocation(self):
        self.assertEqual(allocate_targets(self.population, 200), {
            BOTH: 4, EMPTY: 50, COLLISION: 50, OTHER: 77, UNAFFECTED: 19,
        })

    def test_precision_and_workload_order_with_sample_size(self):
        small = scenario(self.population, self.branches, 200)
        large = scenario(self.population, self.branches, 500)
        self.assertGreater(small["mean_95_worst_half_width"],
                           large["mean_95_worst_half_width"])
        self.assertGreater(small["three_paired_contrasts_simultaneous_95_worst_half_width"],
                           large["three_paired_contrasts_simultaneous_95_worst_half_width"])
        self.assertGreater(small["expected_branch_condition_reviewer_units"], 0)

    def test_rejects_insufficient_or_overpopulation_sample(self):
        with self.assertRaises(ValueError):
            allocate_targets(self.population, 100)
        with self.assertRaises(ValueError):
            allocate_targets(self.population, sum(self.population.values()) + 1)


if __name__ == "__main__":
    unittest.main()
