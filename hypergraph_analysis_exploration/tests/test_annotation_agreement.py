import copy
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.annotation_agreement import (
    _claim_counter,
    _design_weighted_kappa,
    _design_weighted_prevalence,
    _load_stratified_design,
    compare_annotators,
    main,
)
from tests.test_annotation_validator import toy_record


def make_record(item_id, annotator_id, status="annotated"):
    record = toy_record(f"{item_id}:{annotator_id}", "unassigned")
    record["item_id"] = item_id
    record["sense"]["synset_id"] = f"{item_id}.n.01"
    record["source"]["record_id"] = f"{item_id}.n.01"
    record["annotation"]["annotator_id"] = annotator_id
    if status != "annotated":
        record["analysis"] = {
            "status": status,
            "nodes": [],
            "root_node_ids": [],
            "rule_claims": [],
            "horn_projection": {"status": "unsupported", "rule_ids": [], "omissions": ["not formalized"]},
        }
    return record


class AnnotationAgreementTests(unittest.TestCase):
    def test_claim_agreement_includes_variable_sort_declarations(self):
        a = make_record("item-1", "rater-a")
        b = make_record("item-1", "rater-b")
        for record in (a, b):
            record["schema_version"] = "0.5-draft"
            record["analysis"]["rule_claims"][0]["inference_basis"] = ["lexical_or_paraphrastic"]
        a["analysis"]["rule_claims"][0]["variable_sorts"] = {"?x": "Entity"}
        b["analysis"]["rule_claims"][0]["variable_sorts"] = {"?x": "Person"}
        self.assertNotEqual(
            _claim_counter(a, include_evidence=True),
            _claim_counter(b, include_evidence=True),
        )

    def test_claim_agreement_includes_schema_06_sort_judgment_and_evidence(self):
        a = make_record("item-1", "rater-a")
        b = make_record("item-1", "rater-b")
        for record in (a, b):
            record["schema_version"] = "0.6-draft"
            record["analysis"]["rule_claims"][0]["inference_basis"] = ["lexical_or_paraphrastic"]
        a["analysis"]["rule_claims"][0]["variable_sort_judgments"] = {
            "?x": {
                "status": "assigned", "sort": "Entity", "basis": "gloss_span",
                "evidence_spans": [{"start": 0, "end": 4}], "rationale": "rater-specific rationale A",
            }
        }
        b["analysis"]["rule_claims"][0]["variable_sort_judgments"] = {
            "?x": {
                "status": "assigned", "sort": "Person", "basis": "gloss_span",
                "evidence_spans": [{"start": 0, "end": 4}], "rationale": "rater-specific rationale B",
            }
        }
        self.assertNotEqual(
            _claim_counter(a, include_evidence=True),
            _claim_counter(b, include_evidence=True),
        )
        result = compare_annotators([a], [b])
        self.assertEqual(result["agreement_version"], "wordnet-annotation-agreement/13")
        self.assertEqual(result["variable_sort_judgment_multiset_micro"]["f1"], 0.0)
        # Free-text rationales are retained for adjudication but are not exact-match IAA labels.
        b["analysis"]["rule_claims"][0]["variable_sort_judgments"]["?x"]["sort"] = "Entity"
        self.assertEqual(
            _claim_counter(a, include_evidence=True),
            _claim_counter(b, include_evidence=True),
        )
        result = compare_annotators([a], [b])
        self.assertEqual(result["variable_sort_judgment_multiset_micro"]["f1"], 1.0)

    def test_perfect_design_weighted_agreement_is_exactly_one_with_zero_variance(self):
        manifest = {
            "eligible_oewn_sense_count": 10,
            "random_panel_count": 4,
            "random_panel_strata": {
                "s1": {"population_count": 10, "sample_count": 4, "design_weight": 2.5},
            },
        }
        design = _load_stratified_design(manifest)
        item_ids = ["i1", "i2", "i3", "i4"]
        strata = {item_id: "s1" for item_id in item_ids}
        result = _design_weighted_kappa(
            item_ids,
            ["annotated", "ambiguous", "annotated", "ambiguous"],
            ["annotated", "ambiguous", "annotated", "ambiguous"],
            strata,
            design,
        )
        self.assertEqual(result["weighted_cohens_kappa"], 1.0)
        self.assertEqual(result["standard_error"], 0.0)
        self.assertEqual(result["sample_disagreement_count"], 0)
        self.assertIsNotNone(result["wald_95_ci_warning"])
        self.assertIsNone(result["wald_95_ci"])
        self.assertEqual(result["status"], "point_estimate_only_no_observed_disagreements")

    def test_identical_records_agree_on_every_supported_measure(self):
        a = make_record("item-1", "rater-a")
        b = copy.deepcopy(a)
        b["annotation_id"] = "item-1:rater-b"
        b["annotation"]["annotator_id"] = "rater-b"
        # AST node IDs are arbitrary and should not affect structural agreement.
        b["analysis"]["nodes"] = [dict(node, id=f"b-{node['id']}") for node in b["analysis"]["nodes"]]
        b["analysis"]["nodes"][2]["children"] = ["b-n1", "b-n2"]
        b["analysis"]["root_node_ids"] = ["b-n3"]
        b["analysis"]["rule_claims"][0]["formula_node_id"] = "b-n3"

        result = compare_annotators([a], [b])
        self.assertEqual(result["paired_item_count"], 1)
        self.assertTrue(result["per_item_agreement"][0]["ast_root_structure_multiset_exact"])
        self.assertEqual(result["ast_labeled_span_micro"]["f1"], 1.0)
        self.assertEqual(result["evidence_span_micro"]["f1"], 1.0)
        self.assertEqual(result["complete_rule_claim_multiset_micro"]["f1"], 1.0)
        self.assertEqual(result["semantic_support_presence_by_item"]["supported"]["observed_agreement"], 1.0)
        self.assertIsNone(result["analysis_status"]["cohens_kappa"])
        self.assertEqual(result["analysis_status"]["observed_agreement"], 1.0)

    def test_kappa_reports_raw_agreement_and_expected_agreement(self):
        a = [make_record("i1", "rater-a", "annotated"),
             make_record("i2", "rater-a", "ambiguous"),
             make_record("i3", "rater-a", "unsupported")]
        b = [make_record("i1", "rater-b", "annotated"),
             make_record("i2", "rater-b", "ambiguous"),
             make_record("i3", "rater-b", "ambiguous")]
        result = compare_annotators(a, b)
        repeated = compare_annotators(a, b)
        self.assertAlmostEqual(result["analysis_status"]["observed_agreement"], 2 / 3)
        self.assertAlmostEqual(result["analysis_status"]["cohens_kappa"], 0.5)
        self.assertEqual(result["analysis_status"]["n"], 3)
        interval = result["analysis_status"]["bootstrap_95_ci"]["status_cohens_kappa"]
        self.assertEqual(interval["valid_replicates"] + interval["undefined_replicates"], 1000)
        self.assertLessEqual(interval["lower"], result["analysis_status"]["cohens_kappa"])
        self.assertGreaterEqual(interval["upper"], result["analysis_status"]["cohens_kappa"])
        self.assertEqual(result["paired_item_bootstrap"]["seed"], 20261003)
        self.assertEqual(interval, repeated["analysis_status"]["bootstrap_95_ci"]["status_cohens_kappa"])

    def test_span_and_claim_disagreements_are_separated(self):
        a = make_record("item-1", "rater-a")
        b = make_record("item-1", "rater-b")
        b["analysis"]["nodes"][0]["span"] = {"start": 3, "end": 14}
        # Gap-free cover of the whole subtree but with boundaries different
        # from A's single [0,14] span, so exact evidence-span F1 is 0 while
        # the record still passes validation.
        b["analysis"]["rule_claims"][0]["evidence_spans"] = [
            {"start": 0, "end": 8}, {"start": 8, "end": 14}]
        b["analysis"]["rule_claims"][0]["relation"] = "typical"
        b["analysis"]["rule_claims"][0]["direction"] = "none"
        b["analysis"]["rule_claims"][0]["semantic_support"] = "uncertain"
        b["analysis"]["rule_claims"][0]["support_reasons"] = [
            "lexical_or_sense_ambiguity"]
        result = compare_annotators([a], [b])
        self.assertLess(result["ast_labeled_span_micro"]["f1"], 1.0)
        self.assertEqual(result["evidence_span_micro"]["f1"], 0.0)
        self.assertEqual(result["rule_formula_direction_multiset_micro"]["f1"], 0.0)
        self.assertEqual(result["semantic_support_presence_by_item"]["supported"]["observed_agreement"], 0.0)

    def test_same_annotator_or_different_source_gloss_is_rejected(self):
        a = make_record("item-1", "rater-a")
        same_rater = copy.deepcopy(a)
        self.assertRaises(ValueError, compare_annotators, [a], [same_rater])
        b = make_record("item-1", "rater-b")
        b["sense"]["gloss"] = "a different gloss"
        self.assertRaises(ValueError, compare_annotators, [a], [b])

    def test_unpaired_items_are_counted_and_not_silently_paired(self):
        a = [make_record("shared", "rater-a"), make_record("only-a", "rater-a")]
        b = [make_record("shared", "rater-b"), make_record("only-b", "rater-b")]
        result = compare_annotators(a, b)
        self.assertEqual(result["paired_item_count"], 1)
        self.assertEqual(result["unpaired_item_count"], {"a_only": 1, "b_only": 1})

    def test_design_weighted_kappa_uses_stratum_weights_and_linearized_interval(self):
        strata = ["s1", "s1", "s2", "s2"]
        a_statuses = ["annotated", "annotated", "annotated", "ambiguous"]
        b_statuses = ["annotated", "ambiguous", "ambiguous", "ambiguous"]
        batch_hash = "blind-batch-sha256"
        annotator_a, annotator_b = [], []
        for index, (stratum, status_a, status_b) in enumerate(zip(strata, a_statuses, b_statuses), start=1):
            left = make_record(f"i{index}", "rater-a", status_a)
            right = make_record(f"i{index}", "rater-b", status_b)
            left["provenance"] = {
                "sampling_panel": "random_stratified", "stratum": stratum,
                "blind_batch_sha256": batch_hash,
            }
            right["provenance"] = copy.deepcopy(left["provenance"])
            annotator_a.append(left)
            annotator_b.append(right)
        manifest = {
            "eligible_oewn_sense_count": 10,
            "random_panel_count": 4,
            "frame_sha256": "frame-sha256",
            "random_panel_strata": {
                "s1": {"population_count": 4, "sample_count": 2, "design_weight": 2.0},
                "s2": {"population_count": 6, "sample_count": 2, "design_weight": 3.0},
            },
        }
        batch_manifest = {
            "frame_sha256": "frame-sha256", "batch_sha256": batch_hash, "candidate_count": 4,
        }

        result = compare_annotators(annotator_a, annotator_b, manifest, batch_manifest)
        weighted = result["design_weighted_category_agreement"]["analysis_status"]
        self.assertAlmostEqual(weighted["observed_agreement"], 0.5)
        self.assertAlmostEqual(weighted["expected_agreement"], 0.38)
        self.assertAlmostEqual(weighted["weighted_cohens_kappa"], 0.12 / 0.62)
        self.assertAlmostEqual(weighted["standard_error"], 0.2558437222298491)
        self.assertGreaterEqual(weighted["wald_95_ci"]["upper"], weighted["weighted_cohens_kappa"])
        self.assertLessEqual(weighted["wald_95_ci"]["lower"], weighted["weighted_cohens_kappa"])
        self.assertEqual(result["estimand_scope"], "design_weighted_finite_population_agreement_for_categorical_labels")

        prevalence = result["design_weighted_category_agreement"]["marginal_prevalence_by_annotator"]
        annotated_a = prevalence["annotator_a"]["analysis_status"]["category_estimates"]["annotated"]
        annotated_b = prevalence["annotator_b"]["analysis_status"]["category_estimates"]["annotated"]
        self.assertAlmostEqual(annotated_a["estimated_proportion"], 0.7)
        self.assertAlmostEqual(annotated_a["standard_error"], 0.2449489742783178)
        self.assertEqual(annotated_a["status"], "computed_exploratory_clipped_normal_wald")
        self.assertIn("showed undercoverage", annotated_a["ci_warning"])
        self.assertAlmostEqual(annotated_b["estimated_proportion"], 0.2)
        self.assertAlmostEqual(annotated_b["standard_error"], 0.14142135623730953)
        self.assertIsNone(
            prevalence["annotator_a"]["analysis_status"]["category_estimates"]["underspecified"]["wald_95_ci"]
        )
        self.assertIn("not adjudicated truth", prevalence["annotator_a"]["analysis_status"]["interpretation"])

    def test_design_weighted_prevalence_suppresses_zero_variance_non_census_interval(self):
        manifest = {
            "eligible_oewn_sense_count": 10,
            "random_panel_count": 2,
            "random_panel_strata": {
                "s1": {"population_count": 10, "sample_count": 2, "design_weight": 5.0},
            },
        }
        design = _load_stratified_design(manifest)
        result = _design_weighted_prevalence(
            ["i1", "i2"], ["annotated", "annotated"], {"i1": "s1", "i2": "s1"},
            design, ["annotated", "ambiguous"],
        )
        annotated = result["category_estimates"]["annotated"]
        self.assertEqual(annotated["estimated_proportion"], 1.0)
        self.assertIsNone(annotated["wald_95_ci"])
        self.assertEqual(annotated["status"], "point_estimate_only_zero_estimated_variance")
        self.assertEqual(annotated["strata_with_zero_sample_variance"], 1)

        census_design = _load_stratified_design({
            "eligible_oewn_sense_count": 2,
            "random_panel_count": 2,
            "random_panel_strata": {
                "s1": {"population_count": 2, "sample_count": 2, "design_weight": 1.0},
            },
        })
        census = _design_weighted_prevalence(
            ["i1", "i2"], ["annotated", "ambiguous"], {"i1": "s1", "i2": "s1"},
            census_design, ["annotated", "ambiguous"],
        )
        self.assertEqual(census["category_estimates"]["annotated"]["wald_95_ci"], {"lower": 0.5, "upper": 0.5})
        self.assertEqual(census["category_estimates"]["annotated"]["status"], "exact_census")

    def test_design_weighted_kappa_rejects_incomplete_or_misaligned_panel(self):
        a = [make_record("i1", "rater-a"), make_record("i2", "rater-a")]
        b = [make_record("i1", "rater-b"), make_record("i2", "rater-b")]
        for row in a:
            row["provenance"] = {"sampling_panel": "random_stratified", "stratum": "s1"}
        for row in b:
            row["provenance"] = {"sampling_panel": "random_stratified", "stratum": "s1"}
        manifest = {
            "eligible_oewn_sense_count": 10,
            "random_panel_count": 2,
            "frame_sha256": "frame-sha256",
            "random_panel_strata": {"s1": {"population_count": 10, "sample_count": 2, "design_weight": 5.0}},
        }
        batch_manifest = {
            "frame_sha256": "frame-sha256", "batch_sha256": "blind-batch-sha256", "candidate_count": 2,
        }
        for row in [*a, *b]:
            row["provenance"]["blind_batch_sha256"] = "blind-batch-sha256"
        self.assertRaises(ValueError, compare_annotators, a, b[:1], manifest, batch_manifest)
        b[1]["provenance"]["stratum"] = "wrong-stratum"
        self.assertRaises(ValueError, compare_annotators, a, b, manifest, batch_manifest)

    def test_cli_writes_hashed_reproducible_summary_without_gloss_text(self):
        a = make_record("item-1", "rater-a")
        b = make_record("item-1", "rater-b")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            a_path, b_path, output = root / "a.jsonl", root / "b.jsonl", root / "agreement.json"
            a_path.write_text(json.dumps(a) + "\n", encoding="utf-8")
            b_path.write_text(json.dumps(b) + "\n", encoding="utf-8")
            self.assertEqual(main([str(a_path), str(b_path), "--output", str(output)]), 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["paired_item_count"], 1)
            self.assertIn("annotator_a", report["input_sha256"])
            self.assertNotIn("gloss", json.dumps(report).casefold())


if __name__ == "__main__":
    unittest.main()
