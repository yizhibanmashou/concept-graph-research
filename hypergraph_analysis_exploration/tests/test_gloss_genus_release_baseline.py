import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from src.analysis.gloss_genus_release_baseline import evaluate_synsets, verify_extracted_inputs


class GlossGenusReleaseBaselineTests(unittest.TestCase):
    def test_release_wide_evaluation_uses_each_definition_and_excludes_roots(self):
        records = [
            {"synset_id": "target-n", "lexname": "animal", "definitions": ["a bird", "a small bird"],
             "members": ["sparrow"], "hypernyms": ["bird-n"]},
            {"synset_id": "root-n", "lexname": "entity", "definitions": ["something that exists"],
             "members": ["entity"], "hypernyms": []},
        ]
        result = evaluate_synsets(records, {"bird": ["bird-n"], "small bird": ["small-bird-n"]})
        self.assertEqual(result["noun_synset_count"], 2)
        self.assertEqual(result["definition_instance_count"], 3)
        self.assertEqual(result["synsets_with_multiple_definition_strings"], 1)
        self.assertEqual(result["definition_instances_without_direct_hypernym"], 1)
        self.assertEqual(result["overall"]["eligible_definition_instances"], 2)
        self.assertEqual(result["overall"]["status_counts"]["candidate_matches_direct_hypernym"], 1)
        self.assertEqual(result["overall"]["status_counts"]["candidate_not_direct_hypernym"], 1)
        self.assertFalse(result["source_gloss_text_emitted"])

    def test_extracted_files_must_match_archive_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release_dir = root / "release"
            release_dir.mkdir()
            contents = {
                "entries-a.json": b"{}",
                "noun.test.json": b"{}",
            }
            for name, data in contents.items():
                (release_dir / name).write_bytes(data)
            archive_path = root / "release.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                for name, data in contents.items():
                    archive.writestr(name, data)
            result = verify_extracted_inputs(release_dir, archive_path)
            self.assertEqual(result["verified_file_count"], 2)
            self.assertEqual(result["entries_file_count"], 1)
            self.assertEqual(result["noun_synset_file_count"], 1)
            (release_dir / "noun.test.json").write_text("{ }", encoding="utf-8")
            self.assertRaises(ValueError, verify_extracted_inputs, release_dir, archive_path)


if __name__ == "__main__":
    unittest.main()
