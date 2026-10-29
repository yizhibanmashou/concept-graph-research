import tempfile
import unittest
from pathlib import Path
import shutil
import subprocess

from src import ensure_project_structure


class ProjectStructureTests(unittest.TestCase):
    def test_ensures_current_directories_relative_to_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            ensure_project_structure(project_root)

            expected = (
                "src/analysis",
                "src/logic",
                "outputs",
                "reports",
                "config",
                "docs",
                "archive",
                "sources",
                "tests",
                "tmp",
            )
            for relative_path in expected:
                with self.subTest(path=relative_path):
                    self.assertTrue((project_root / relative_path).is_dir())

            self.assertFalse((project_root / "src/src").exists())
            self.assertFalse((project_root / "src/visualization").exists())
            self.assertFalse((project_root / "src/utils").exists())
            self.assertFalse((project_root / "data/cache").exists())

    @unittest.skipUnless(shutil.which("git"), "git is required to verify ignore rules")
    def test_restricted_gloss_and_witness_files_are_git_ignored(self):
        project_root = Path(__file__).resolve().parents[1]
        protected_paths = (
            "outputs/phase7/annotation_batch_2025_plus_blind.jsonl",
            "outputs/phase6/witness_oewn-00520548-n.json",
            "outputs/phase7/oewn_2025_plus_release_crosscheck.json",
            "outputs/phase8/frozen_bundle_replay_exceptions.json",
            "outputs/phase9/gloss_genus_baseline_2025_plus_200.json",
            "outputs/phase16/oewn_hypernym_verification.json",
        )

        for relative_path in protected_paths:
            with self.subTest(path=relative_path):
                result = subprocess.run(
                    ["git", "check-ignore", "--quiet", "--", relative_path],
                    cwd=project_root,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, "restricted artifact must remain ignored")


if __name__ == "__main__":
    unittest.main()
