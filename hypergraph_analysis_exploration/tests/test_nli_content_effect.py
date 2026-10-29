import unittest

from src.logic.nli_content_effect import evaluate_content_effect, validate_content_effect_sidecar


GLOSS = "a" * 64
HYP = "b" * 64
BASE_INPUT = "c" * 64
DISTRACTOR_INPUT = "d" * 64
CONTEXT = "e" * 64


def _row(example_id, *, condition, value, support="supported", relation="entailment",
         plausibility="plausible", contrast=None, split="test", group="lemma-1",
         sense="sense-1", claim="claim-1", gloss=GLOSS, hypothesis=HYP,
         input_hash=BASE_INPUT, context_hash=None, review="adjudicated"):
    return {
        "example_id": example_id,
        "contrast_group_id": contrast,
        "split": split,
        "diagnostic_condition": condition,
        "condition_value": value,
        "source_sense_id": sense,
        "claim_id": claim,
        "gloss_sha256": gloss,
        "hypothesis_sha256": hypothesis,
        "model_premise_sha256": input_hash,
        "context_sha256": context_hash,
        "gold_support_label": support if review == "adjudicated" else None,
        "nli_gold_relation": relation if review == "adjudicated" else None,
        "claim_plausibility": plausibility,
        "review_status": review,
        "group_id": group,
    }


def _prediction(example_id, entailment, neutral, contradiction, split="test"):
    return {"example_id": example_id, "split": split,
            "model_id": "test-nli", "model_revision": "immutable-revision-123",
            "scores": {"entailment": entailment, "neutral": neutral,
                       "contradiction": contradiction}}


class NliContentEffectTests(unittest.TestCase):
    def test_matched_and_context_pairs_are_descriptive_and_route_ineligible(self):
        rows = [
            _row("m-p", condition="matched_plausibility_pair", value="plausible",
                 plausibility="plausible", contrast="matched-1", group="g1"),
            _row("m-i", condition="matched_plausibility_pair", value="implausible",
                 plausibility="implausible", contrast="matched-1", group="g1", sense="sense-2",
                 claim="claim-2", gloss="f" * 64),
            _row("c-b", condition="irrelevant_context_pair", value="source_only",
                 plausibility="plausible", contrast="context-1", group="g2", input_hash=GLOSS),
            _row("c-d", condition="irrelevant_context_pair", value="irrelevant_context",
                 plausibility="plausible", contrast="context-1", group="g2", input_hash=DISTRACTOR_INPUT,
                 context_hash=CONTEXT),
        ]
        predictions = [
            _prediction("m-p", .9, .08, .02),
            _prediction("m-i", .55, .40, .05),
            _prediction("c-b", .8, .15, .05),
            _prediction("c-d", .4, .5, .1),
        ]

        report = evaluate_content_effect(rows, predictions)
        paired = report["splits"]["test"]["paired_diagnostics"]
        match = paired["matched_plausibility_pair"]["supported"]
        context = paired["irrelevant_context_pair"]
        self.assertAlmostEqual(match["mean_entailment_score_delta_right_minus_left"], -.35)
        self.assertEqual(match["prediction_flip_rate"], 0.0)
        self.assertAlmostEqual(context["mean_entailment_score_delta_right_minus_left"], -.4)
        self.assertEqual(context["prediction_flip_rate"], 1.0)
        self.assertTrue(report["diagnostic_only"])
        self.assertFalse(report["threshold_selection_performed"])
        self.assertFalse(report["proof_route_eligible"])
        self.assertFalse(report["inference_performed"])
        # Paired observations are analysed as pairs, not reused as independent strata.
        self.assertEqual(report["splits"]["test"]["plausibility_strata"], {})

    def test_support_bias_gap_is_reported_as_descriptive_difference(self):
        rows = [
            _row("sp", condition="plausibility_stratum", value="plausible", plausibility="plausible"),
            _row("si", condition="plausibility_stratum", value="implausible", plausibility="implausible"),
            _row("up", condition="plausibility_stratum", value="plausible", plausibility="plausible",
                 support="not_supported", relation="neutral", claim="claim-2"),
            _row("ui", condition="plausibility_stratum", value="implausible", plausibility="implausible",
                 support="not_supported", relation="neutral", claim="claim-3"),
        ]
        predictions = [
            _prediction("sp", .8, .15, .05),
            _prediction("si", .2, .75, .05),
            _prediction("up", .6, .35, .05),
            _prediction("ui", .1, .85, .05),
        ]
        result = evaluate_content_effect(rows, predictions)["splits"]["test"]
        gaps = result["descriptive_content_effect_gaps"]
        self.assertEqual(gaps["CE_supported_fnr_implausible_minus_plausible"], 1.0)
        self.assertEqual(gaps["CE_not_supported_fpr_plausible_minus_implausible"], 1.0)

    def test_sidecar_rejects_source_text_and_pair_label_mismatch(self):
        row = _row("a", condition="plausibility_stratum", value="plausible")
        with self.assertRaisesRegex(ValueError, "must not contain source or model-input text"):
            validate_content_effect_sidecar([{**row, "gloss": "raw gloss"}])

        left = _row("p", condition="matched_plausibility_pair", value="plausible",
                    contrast="pair", group="g")
        right = _row("i", condition="matched_plausibility_pair", value="implausible",
                     plausibility="implausible", support="not_supported", relation="neutral",
                     contrast="pair", group="g")
        with self.assertRaisesRegex(ValueError, "mismatched gold_support_label"):
            validate_content_effect_sidecar([left, right])

    def test_sidecar_rejects_cross_split_group_leakage(self):
        left = _row("d", condition="plausibility_stratum", value="plausible", split="dev", group="shared")
        right = _row("t", condition="plausibility_stratum", value="implausible", plausibility="implausible",
                     split="test", group="shared")
        with self.assertRaisesRegex(ValueError, "group_id leakage"):
            validate_content_effect_sidecar([left, right])

    def test_context_pair_requires_same_locked_gloss_and_hypothesis(self):
        left = _row("base", condition="irrelevant_context_pair", value="source_only",
                    contrast="pair", group="g", input_hash=GLOSS)
        right = _row("noise", condition="irrelevant_context_pair", value="irrelevant_context",
                     contrast="pair", group="g", input_hash=DISTRACTOR_INPUT,
                     context_hash=CONTEXT, gloss="9" * 64)
        with self.assertRaisesRegex(ValueError, "mismatched gloss_sha256"):
            validate_content_effect_sidecar([left, right])

    def test_prediction_join_requires_exact_ids_and_matching_splits(self):
        row = _row("a", condition="plausibility_stratum", value="plausible")
        with self.assertRaisesRegex(ValueError, "exactly match"):
            evaluate_content_effect([row], [])
        with self.assertRaisesRegex(ValueError, "split mismatch"):
            evaluate_content_effect([row], [_prediction("a", .8, .1, .1, split="dev")])


if __name__ == "__main__":
    unittest.main()
