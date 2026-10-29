import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.project_paths import configured_bundle_root


class ProjectPathsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "config").mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_config(self, bundle_root):
        config_path = self.root / "config" / "project_config.json"
        config_path.write_text(json.dumps({"data_source": {"root": str(bundle_root)}}), encoding="utf-8")

    def test_resolves_relative_bundle_from_project_root(self):
        self._write_config("../frozen/bundle")
        self.assertEqual(configured_bundle_root(self.root), (self.root / "../frozen/bundle").resolve())

    def test_preserves_absolute_bundle_path(self):
        absolute = (self.root / "external" / "frozen").resolve()
        self._write_config(absolute)
        self.assertEqual(configured_bundle_root(self.root), absolute)

    def test_rejects_missing_or_invalid_root_configuration(self):
        with self.assertRaisesRegex(ValueError, "data_source.root"):
            self._write_config(" ")
            configured_bundle_root(self.root)

        (self.root / "config" / "project_config.json").unlink()
        with self.assertRaisesRegex(ValueError, "configuration is missing"):
            configured_bundle_root(self.root)


if __name__ == "__main__":
    unittest.main()
