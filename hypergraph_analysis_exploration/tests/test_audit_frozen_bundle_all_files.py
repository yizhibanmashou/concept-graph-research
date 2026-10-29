import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.audit_frozen_bundle_all_files import audit


class FrozenBundleAllFilesAuditTests(unittest.TestCase):
    def test_all_manifest_files_and_metadata_match(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp)
            payload = b"frozen data\n"
            manifest_payload = b'{"version":1}'
            (bundle / "graph").mkdir()
            (bundle / "graph" / "nodes.tsv").write_bytes(payload)
            (bundle / "manifest.json").write_bytes(manifest_payload)
            entries = [
                {"path": "graph/nodes.tsv", "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()},
                {"path": "manifest.json", "bytes": len(manifest_payload), "sha256": hashlib.sha256(manifest_payload).hexdigest()},
            ]
            (bundle / "checksums.jsonl").write_text(
                "\n".join(json.dumps(row) for row in entries) + "\n", encoding="utf-8"
            )

            result = audit(bundle)

        self.assertTrue(result["passed"])
        self.assertEqual(result["matched_file_count"], 2)
        self.assertEqual(result["hashed_bytes"], len(payload) + len(manifest_payload))

    def test_detects_missing_mismatched_and_unlisted_files(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp)
            (bundle / "bad.txt").write_text("changed", encoding="utf-8")
            (bundle / "extra.txt").write_text("extra", encoding="utf-8")
            (bundle / "manifest.json").write_text("{}", encoding="utf-8")
            (bundle / "checksums.jsonl").write_text("\n".join([
                json.dumps({"path": "bad.txt", "bytes": 4, "sha256": "0" * 64}),
                json.dumps({"path": "missing.txt", "bytes": 1, "sha256": "1" * 64}),
            ]), encoding="utf-8")

            result = audit(bundle)

        self.assertFalse(result["passed"])
        self.assertEqual(result["size_mismatches"], 1)
        self.assertEqual(result["missing_files"], 1)
        self.assertEqual(result["unlisted_files"], 1)

    def test_rejects_duplicate_and_path_traversal_entries(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp)
            row = {"path": "safe.txt", "bytes": 0, "sha256": "0" * 64}
            (bundle / "checksums.jsonl").write_text("\n".join([
                json.dumps(row), json.dumps(row),
                json.dumps({"path": "../escape", "bytes": 0, "sha256": "0" * 64}),
            ]), encoding="utf-8")

            result = audit(bundle)

        self.assertFalse(result["passed"])
        self.assertEqual(result["duplicate_entries"], 1)
        self.assertEqual(result["unsafe_entries"], 1)

    def test_requires_manifest_itself_to_be_checksum_covered(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp)
            (bundle / "manifest.json").write_text("{}", encoding="utf-8")
            (bundle / "checksums.jsonl").write_text("", encoding="utf-8")

            result = audit(bundle)

        self.assertFalse(result["passed"])
        self.assertEqual(result["manifest_checksum_missing"], 1)


if __name__ == "__main__":
    unittest.main()
