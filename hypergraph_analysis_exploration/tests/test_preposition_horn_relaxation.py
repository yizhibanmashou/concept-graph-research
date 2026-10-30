import unittest

from src.analysis.preposition_horn_relaxation import (
    minimum_derivation_depths_allow_unreachable,
    relax_preposition_literals,
    summarize_depths,
)


class PrepositionHornRelaxationTests(unittest.TestCase):
    def test_removes_only_preposition_literals_and_preserves_or_clauses(self):
        clauses = [
            ("target", ("prep", "noun")),
            ("target", ("verb",)),
            ("prep", ("basis",)),
        ]
        relaxed, counts = relax_preposition_literals(
            clauses,
            {"prep": "prep", "noun": "n", "verb": "v", "basis": "n"},
        )
        self.assertEqual(
            relaxed,
            [("target", ("noun",)), ("target", ("verb",)), ("prep", ("basis",))],
        )
        self.assertEqual(counts, {
            "clauses_with_preposition_literals": 1,
            "removed_preposition_literals": 1,
            "newly_empty_clauses": 0,
        })

    def test_preposition_only_clause_becomes_empty_and_is_reported(self):
        relaxed, counts = relax_preposition_literals(
            [("target", ("prep",))],
            {"prep": "prep"},
        )
        self.assertEqual(relaxed, [("target", ())])
        self.assertEqual(counts["newly_empty_clauses"], 1)

    def test_phrase_sensitivity_removes_only_prep_and_prep_phrase(self):
        clauses = [("target", ("prep", "phrase", "noun"))]
        relaxed, counts = relax_preposition_literals(
            clauses,
            {"prep": "prep", "phrase": "prep_phrase", "noun": "n"},
            {"prep", "prep_phrase"},
        )
        self.assertEqual(relaxed, [("target", ("noun",))])
        self.assertEqual(counts["removed_preposition_literals"], 2)

    def test_depth_summary_is_stable_for_empty_and_nonempty_inputs(self):
        self.assertEqual(summarize_depths([]), {
            "count": 0, "min": None, "median": None, "p90": None, "max": None,
        })

    def test_unreachable_variant_does_not_invent_empty_clause_facts(self):
        depths = minimum_derivation_depths_allow_unreachable(
            {"seed", "reachable", "orphan"},
            [("reachable", ("seed",)), ("orphan", ("orphan",))],
            {"seed"},
        )
        self.assertEqual(depths, {"seed": 0, "reachable": 1})
        self.assertEqual(summarize_depths([0, 1, 2, 4]), {
            "count": 4, "min": 0, "median": 1.5, "p90": 2, "max": 4,
        })


if __name__ == "__main__":
    unittest.main()
