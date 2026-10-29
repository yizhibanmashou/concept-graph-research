import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.logic.nli_gate import (
    evaluate_calibrated_jsonl,
    evaluate_calibrated_splits,
    route_candidate,
    select_entailment_threshold,
)


class NliGateTests(unittest.TestCase):
    def setUp(self):
        self.dev = [
            {"sense_id": "s1", "split": "dev", "gold": "entailment", "scores": {"entailment": .95, "neutral": .03, "contradiction": .02}},
            {"sense_id": "s2", "split": "dev", "gold": "neutral", "scores": {"entailment": .15, "neutral": .80, "contradiction": .05}},
            {"sense_id": "s3", "split": "dev", "gold": "contradiction", "scores": {"entailment": .10, "neutral": .10, "contradiction": .80}},
        ]

    def _entailment_dev(self, count=8, score=.95):
        # A single observed score means no Bonferroni multiplicity penalty
        # across thresholds; eight all-entailing rows yield a Wilson lower
        # bound of roughly 0.68, comfortably above a 0.2 precision floor.
        rest = (1.0 - score) / 2
        return [
            {"sense_id": f"cal-{index}", "split": "dev", "gold": "entailment",
             "scores": {"entailment": score, "neutral": rest, "contradiction": rest}}
            for index in range(count)
        ]

    def test_threshold_selected_on_development_precision_floor(self):
        result = select_entailment_threshold(self._entailment_dev(), minimum_precision=.2)
        self.assertEqual(result["status"], "selected_on_development_data")
        self.assertGreaterEqual(result["precision"], .9)
        self.assertGreaterEqual(result["precision_wilson_lower_bound"], .2)
        self.assertEqual(result["recall"], 1.0)

    def test_small_development_sample_does_not_claim_ninety_percent_precision(self):
        result = select_entailment_threshold(self.dev, minimum_precision=.9)
        self.assertEqual(result["status"], "no_threshold_meets_precision_floor")

    def test_nli_alone_cannot_accept_candidate(self):
        threshold = select_entailment_threshold(self._entailment_dev(), minimum_precision=.2)
        result = route_candidate(self.dev[0]["scores"], threshold, proof_certificate_valid=False,
                                 source_semantics_reviewed=False)
        self.assertEqual(result["route"], "abstain_missing_or_invalid_proof")

    def test_invalid_source_semantics_requires_abstention(self):
        threshold = select_entailment_threshold(self._entailment_dev(), minimum_precision=.2)
        result = route_candidate(self.dev[0]["scores"], threshold, proof_certificate_valid=True,
                                 source_semantics_reviewed=False)
        self.assertEqual(result["route"], "abstain_source_rule_not_semantically_audited")

    def test_test_split_cannot_be_used_to_select_threshold(self):
        test_rows = [dict(row, split="test") for row in self.dev]
        with self.assertRaisesRegex(ValueError, "development rows only"):
            select_entailment_threshold(test_rows, minimum_precision=.9)

    def test_missing_dev_threshold_forces_abstention(self):
        result = route_candidate(self.dev[0]["scores"], {"status": "no_threshold_meets_precision_floor"},
                                 proof_certificate_valid=True, source_semantics_reviewed=True)
        self.assertEqual(result["route"], "abstain_no_calibrated_threshold")

    def test_non_finite_and_boolean_scores_are_rejected(self):
        for invalid_value in (float("nan"), float("inf"), True, 10 ** 1000):
            with self.subTest(value=invalid_value):
                row = dict(self.dev[0], scores={**self.dev[0]["scores"], "entailment": invalid_value})
                with self.assertRaisesRegex(ValueError, "finite numbers"):
                    select_entailment_threshold([row])

    def test_boolean_precision_floor_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "minimum_precision"):
            select_entailment_threshold(self.dev, minimum_precision=True)

    def test_calibrated_pair_checks_group_leakage_and_reports_test_gate(self):
        dev = [
            {"sense_id": f"dev-{i}", "group_id": f"dev-group-{i}", "split": "dev",
             "gold": "entailment",
             "scores": {"entailment": .96, "neutral": .02, "contradiction": .02}}
            for i in range(40)
        ]
        test = [
            {"sense_id": "test-1", "group_id": "test-group-1", "split": "test", "gold": "entailment",
             "scores": {"entailment": .97, "neutral": .02, "contradiction": .01}},
            {"sense_id": "test-2", "group_id": "test-group-2", "split": "test", "gold": "neutral",
             "scores": {"entailment": .96, "neutral": .03, "contradiction": .01}},
            {"sense_id": "test-3", "group_id": "test-group-3", "split": "test", "gold": "contradiction",
             "scores": {"entailment": .10, "neutral": .10, "contradiction": .80}},
        ]
        report = evaluate_calibrated_splits(dev, test, minimum_precision=.9)
        self.assertEqual(report["development"]["threshold_selection"]["status"],
                         "selected_on_development_data")
        gate = report["test"]["entailment_gate"]
        self.assertAlmostEqual(gate["coverage"], 2 / 3)
        self.assertEqual(gate["precision"], .5)
        self.assertEqual(gate["recall"], 1.0)
        self.assertIn("top_label_ece_10_bins", report["test"])

    def test_calibrated_pair_rejects_lemma_group_leakage_and_incomplete_group_ids(self):
        dev = [dict(self.dev[0], sense_id="n-1", group_id="lemma-1")]
        test = [dict(self.dev[0], sense_id="n-2", group_id="lemma-1", split="test")]
        with self.assertRaisesRegex(ValueError, "group leakage"):
            evaluate_calibrated_splits(dev, test, minimum_precision=.2)

        test[0].pop("group_id")
        with self.assertRaisesRegex(ValueError, "group_id is used"):
            evaluate_calibrated_splits(dev, test, minimum_precision=.2)

    def test_calibrated_pair_rejects_example_id_reused_across_splits(self):
        dev = [dict(self.dev[0], sense_id="dev-sense", example_id="same-example")]
        test = [dict(self.dev[1], sense_id="test-sense", split="test", example_id="same-example")]
        with self.assertRaisesRegex(ValueError, "example_id leakage"):
            evaluate_calibrated_splits(dev, test, minimum_precision=.2)

    def test_duplicate_example_id_is_rejected(self):
        rows = [dict(row, example_id="same") for row in self.dev[:2]]
        with self.assertRaisesRegex(ValueError, "duplicate example_id"):
            select_entailment_threshold(rows, minimum_precision=.2)

    def test_jsonl_report_records_prediction_input_hashes(self):
        dev = [
            {"sense_id": f"d-{i}", "split": "dev", "gold": "entailment",
             "scores": {"entailment": .96, "neutral": .02, "contradiction": .02}}
            for i in range(40)
        ]
        test = [dict(self.dev[0], sense_id="t-1", split="test")]
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_path = Path(temp_dir) / "dev.jsonl"
            test_path = Path(temp_dir) / "test.jsonl"
            dev_path.write_text("".join(json.dumps(row) + "\n" for row in dev), encoding="utf-8")
            test_path.write_text("".join(json.dumps(row) + "\n" for row in test), encoding="utf-8")
            report = evaluate_calibrated_jsonl(dev_path, test_path, minimum_precision=.9)
            self.assertEqual(report["input_sha256"]["development_predictions"],
                             hashlib.sha256(dev_path.read_bytes()).hexdigest())
            self.assertEqual(report["input_sha256"]["test_predictions"],
                             hashlib.sha256(test_path.read_bytes()).hexdigest())

    def test_cli_dev_test_mode_writes_versioned_report(self):
        dev = [
            {"sense_id": f"d-{i}", "split": "dev", "gold": "entailment",
             "scores": {"entailment": .96, "neutral": .02, "contradiction": .02}}
            for i in range(40)
        ]
        test = [dict(self.dev[0], sense_id="t-1", split="test")]
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            dev_path, test_path, output_path = temp / "dev.jsonl", temp / "test.jsonl", temp / "report.json"
            dev_path.write_text("".join(json.dumps(row) + "\n" for row in dev), encoding="utf-8")
            test_path.write_text("".join(json.dumps(row) + "\n" for row in test), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-m", "src.logic.nli_gate",
                 "--dev-predictions", str(dev_path), "--test-predictions", str(test_path),
                 "--minimum-precision", "0.9", "--model-id", "synthetic-test-model",
                 "--model-revision", "sha256:test-only", "--output", str(output_path)],
                cwd=project_root, capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(report["evaluation_version"], "nli-dev-calibration-test/3")
            self.assertEqual(report["model"]["revision"], "sha256:test-only")
            self.assertEqual(report["test"]["entailment_gate"]["selected_count"], 0)


if __name__ == "__main__":
    unittest.main()
