import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.oewn_release_crosscheck import crosscheck_release


class OewnReleaseCrosscheckTests(unittest.TestCase):
    def test_exact_and_normalized_matches_are_reported_without_gloss_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle"
            release = root / "release"
            source = bundle / "sources" / "Synset" / "fixture" / "sense.json"
            source.parent.mkdir(parents=True)
            release.mkdir()
            source.write_text(json.dumps({
                "synset": {"raw_definition": "a  raw gloss"},
                "definition": {"definition": "effective gloss"},
            }), encoding="utf-8")
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            (release / "noun.fixture.json").write_text(json.dumps({
                "00000001-n": {"definition": ["a raw gloss"]},
                "00000002-n": {"definition": ["another gloss"]},
            }), encoding="utf-8")
            frame = root / "frame.jsonl"
            frame.write_text(json.dumps({
                "sense_id": "oewn-00000001-n",
                "panel": "random_stratified",
                "source_records": [{"path": "sources/Synset/fixture/sense.json", "sha256": source_hash}],
            }) + "\n", encoding="utf-8")

            report = crosscheck_release(frame, bundle, release, release_name="test release", release_date="2026-01-01", release_uri="test://release")
            self.assertEqual(report["overall"]["normalized_raw_gloss_match"], 1)
            self.assertEqual(report["overall"]["exact_raw_gloss_match"], 0)
            self.assertEqual(report["overall"]["exact_effective_gloss_match"], 0)
            self.assertEqual(report["overall"]["normalized_effective_gloss_match"], 0)
            self.assertFalse(report["raw_gloss_text_emitted"])
            self.assertEqual(report["release_name"], "test release")
            self.assertNotIn("a  raw gloss", json.dumps(report))
            source_comparison = report["per_sense"][0]["source_record_comparisons"][0]
            self.assertEqual(source_comparison["source_payload_sha256"], source_hash)
            self.assertTrue(source_comparison["raw_gloss_normalized_match"])
            self.assertFalse(source_comparison["effective_gloss_normalized_match"])
            self.assertFalse(source_comparison["raw_equals_effective"])
            self.assertNotIn("effective gloss", json.dumps(report))

    def test_empty_effective_gloss_is_distinguished_from_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle"
            release = root / "release"
            source = bundle / "sources" / "Synset" / "sense.json"
            source.parent.mkdir(parents=True)
            release.mkdir()
            source.write_text(json.dumps({
                "synset": {"raw_definition": "an official definition"},
                "definition": {"definition": ""},
            }), encoding="utf-8")
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            (release / "noun.fixture.json").write_text(json.dumps({
                "00000001-n": {"definition": "an official definition"},
            }), encoding="utf-8")
            frame = root / "frame.jsonl"
            frame.write_text(json.dumps({
                "sense_id": "oewn-00000001-n",
                "source_records": [{"path": "sources/Synset/sense.json", "sha256": source_hash}],
            }) + "\n", encoding="utf-8")

            report = crosscheck_release(frame, bundle, release)

            comparison = report["per_sense"][0]["source_record_comparisons"][0]
            self.assertTrue(comparison["source_effective_gloss_present"])
            self.assertEqual(comparison["source_effective_gloss_length_codepoints"], 0)
            self.assertFalse(comparison["effective_gloss_exact_match"])
            self.assertEqual(report["overall"]["blank_source_effective_gloss"], 1)
            self.assertEqual(report["overall"]["no_source_effective_gloss"], 0)


if __name__ == "__main__":
    unittest.main()
