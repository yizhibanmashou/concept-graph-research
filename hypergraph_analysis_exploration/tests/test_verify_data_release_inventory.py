"""Synthetic tests for the read-only data release inventory checker."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from src.analysis.verify_data_release_inventory import audit_release_inventory


class VerifyDataReleaseInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "sources").mkdir()
        (self.root / "config").mkdir()
        (self.root / "bundle").mkdir()
        self.archive = self.root / "oewn.zip"
        with zipfile.ZipFile(self.archive, "w") as zipped:
            zipped.writestr("README.txt", "synthetic fixture")
        self.manifest = {
            "head_count": 2,
            "clause_count": 3,
            "source_record_files": 4,
            "graph_sha256": "a" * 64,
            "semantic_fingerprint_sha256": "b" * 64,
            "head_kinds": {"oewn": 2},
        }
        (self.root / "bundle" / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        (self.root / "config" / "project_config.json").write_text(
            json.dumps({"data_source": {"root": "bundle"}}), encoding="utf-8"
        )
        self.inventory_path = self.root / "sources" / "data_release_inventory.json"
        self.inventory = {
            "schema_version": "data-release-inventory/1",
            "project_release_status": "not_cleared_for_public_release",
            "upstream_resources": [{
                "resource_id": "fixture",
                "local_archive": "oewn.zip",
                "local_archive_sha256": hashlib.sha256(self.archive.read_bytes()).hexdigest(),
                "archive_contains_license_or_readme": True,
            }],
            "project_inputs": [{
                "resource_id": "frozen_hypergraph_bundle_154206",
                "local_manifest": "manifest.json",
                **self.manifest,
            }],
            "project_artifacts": [{
                "resource_id": "project_source_code_and_docs",
                "root_license_file_present": False,
            }],
        }
        self._write_inventory()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_inventory(self) -> None:
        self.inventory_path.write_text(json.dumps(self.inventory), encoding="utf-8")

    def test_consistent_inventory_passes_but_never_grants_release_clearance(self) -> None:
        result = audit_release_inventory(self.root)
        self.assertTrue(result["inventory_consistent"], result["checks"])
        self.assertEqual(result["release_clearance"], "not_cleared_for_public_release")

    def test_archive_hash_drift_is_reported(self) -> None:
        self.archive.write_bytes(self.archive.read_bytes() + b"tamper")
        result = audit_release_inventory(self.root)
        self.assertFalse(result["inventory_consistent"])
        self.assertFalse(next(check for check in result["checks"] if check["check"] == "archive_sha256:fixture")["ok"])

    def test_bundle_manifest_drift_is_reported(self) -> None:
        self.manifest["head_count"] = 3
        (self.root / "bundle" / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        result = audit_release_inventory(self.root)
        self.assertFalse(result["inventory_consistent"])
        self.assertFalse(next(check for check in result["checks"] if check["check"] == "bundle:head_count")["ok"])

    def test_license_file_drift_is_reported(self) -> None:
        (self.root / "LICENSE").write_text("unapproved fixture", encoding="utf-8")
        result = audit_release_inventory(self.root)
        self.assertFalse(result["inventory_consistent"])
        self.assertFalse(next(check for check in result["checks"] if check["check"] == "root_license_file")["ok"])

    def test_archive_path_cannot_escape_project_root(self) -> None:
        self.inventory["upstream_resources"][0]["local_archive"] = "../outside.zip"
        self._write_inventory()
        result = audit_release_inventory(self.root)
        self.assertFalse(result["inventory_consistent"])
        self.assertIn("escapes project root", next(check for check in result["checks"] if check["check"] == "archive:fixture")["detail"])


if __name__ == "__main__":
    unittest.main()
