import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.analysis.audit_output_release_surface import (
    _write_report,
    audit_output_release_surface,
)


class OutputReleaseSurfaceAuditTests(unittest.TestCase):
    def test_flags_gloss_identity_and_ignored_artifacts_without_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "outputs/phase7").mkdir(parents=True)
            (root / "outputs/phase13").mkdir(parents=True)
            (root / ".gitignore").write_text("/outputs/phase7/*_blind.jsonl\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "outputs/phase7/sample_blind.jsonl").write_text(
                json.dumps({"task_id": "private-id", "gloss": "private text"}) + "\n",
                encoding="utf-8",
            )
            (root / "outputs/phase13/aggregate.json").write_text(
                json.dumps({"node_count": 4, "component_count": 2}), encoding="utf-8"
            )

            report = audit_output_release_surface(root)

            self.assertEqual(report["artifact_count"], 2)
            self.assertEqual(report["release_clearance"], "not_cleared_for_public_release")
            by_path = {row["path"]: row for row in report["artifacts"]}
            sensitive = by_path["outputs/phase7/sample_blind.jsonl"]
            self.assertTrue(sensitive["git_ignored"])
            self.assertEqual(sensitive["text_risk_field_names"], ["gloss"])
            self.assertEqual(sensitive["identity_risk_field_names"], ["task_id"])
            self.assertNotIn("private text", json.dumps(report))
            self.assertNotIn("private-id", json.dumps(report))
            self.assertEqual(
                by_path["outputs/phase13/aggregate.json"]["release_decision"],
                "manual_review_required",
            )

    def test_report_writer_refuses_external_path_and_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report = {"example": True}
            with self.assertRaises(ValueError):
                _write_report(report, root.parent / "outside.json", root, force=False)
            destination = root / "outputs/report.json"
            _write_report(report, destination, root, force=False)
            with self.assertRaises(FileExistsError):
                _write_report(report, destination, root, force=False)
            _write_report(report, destination, root, force=True)


if __name__ == "__main__":
    unittest.main()
